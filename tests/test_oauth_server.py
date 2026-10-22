"""Tests for the authorize view's login bookkeeping.

HACS review item 1: the login flow's ``create_entry`` only proves the *password*
was correct. The authorize page must also refuse (a) a credential that resolves
to no user and (b) users who are deactivated or marked "local network only"
when the request comes from outside the local network — exactly like Home
Assistant's own login view does.

HACS review item 2: the page returns HTTP 200 for a wrong password, so HA's
``@log_invalid_auth`` decorator never fires and this view must report failed and
successful logins to HA itself — otherwise the built-in IP ban never sees them,
and a user who eventually logs in keeps a stale failure count.
"""

from __future__ import annotations

import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.xiaodu_bridge import oauth_server
from custom_components.xiaodu_bridge.const import (
    CONF_CLIENT_ID,
    CONF_REDIRECT_URI,
    DATA_ENHANCED_DEVICES,
    DOMAIN,
)
from custom_components.xiaodu_bridge.oauth_server import (
    DATA_OAUTH_STORE,
    MAX_SESSIONS,
    SESSION_COOKIE,
    XiaoduOAuthAuthorizeView,
    _failures,
    _new_session,
    _record_failure,
    _sessions,
)
from custom_components.xiaodu_bridge.oauth_store import XiaoduOAuthStore

CLIENT_ID = "test-client"
REDIRECT_URI = "https://xiaodu.baidu.com/saiya/auth/callback"
STATE = "state-1"
NONCE = "nonce-1"
PUBLIC_IP = "203.0.113.10"  # TEST-NET-3, never a local address


class _Enhanced:
    """Stand-in for the enhanced device set, with a tell-tale device name."""

    def __init__(self, names: list[str]) -> None:
        self._devices = [
            SimpleNamespace(friendly_name=name, capabilities=[]) for name in names
        ]

    def all(self) -> list:
        return self._devices


class _Request:
    """Minimal aiohttp request stand-in for the view under test."""

    def __init__(self, hass: HomeAssistant, *, nonce: str = "") -> None:
        self.app = {"hass": hass}
        self.query = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "state": STATE,
        }
        self.remote = PUBLIC_IP
        self.cookies = {SESSION_COOKIE: nonce} if nonce else {}
        self.headers: dict[str, str] = {}
        self.rel_url = "/auth/xiaodu"
        self._form = {"username": "someone", "password": "secret"}

    async def post(self) -> dict[str, str]:
        return self._form


@pytest.fixture
def entry(hass: HomeAssistant) -> MockConfigEntry:
    """Register the single Xiaodu config entry plus the in-memory state."""
    item = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_CLIENT_ID: CLIENT_ID, CONF_REDIRECT_URI: REDIRECT_URI},
        unique_id=DOMAIN,
    )
    item.add_to_hass(hass)
    data = hass.data.setdefault(DOMAIN, {})
    data[DATA_OAUTH_STORE] = XiaoduOAuthStore()
    return item


def _start_session(hass: HomeAssistant) -> None:
    """Seed the pending authorize session the POST reads from its cookie."""
    _sessions(hass)[NONCE] = {"flow_id": "flow-1", "expires_at": time.time() + 300}


def _finish_login(
    monkeypatch: pytest.MonkeyPatch, hass: HomeAssistant, user: object
) -> None:
    """Make the HA login flow report success and resolve to ``user``."""

    async def _progress(hass_, request, redirect_uri, session, params):
        return {"type": "create_entry", "result": SimpleNamespace(id="cred-1")}

    monkeypatch.setattr(
        XiaoduOAuthAuthorizeView, "_progress_flow", staticmethod(_progress)
    )
    monkeypatch.setattr(
        hass.auth, "async_get_user_by_credentials", AsyncMock(return_value=user)
    )


def _finish_form(
    monkeypatch: pytest.MonkeyPatch, errors: dict[str, str] | None
) -> None:
    """Make the HA login flow come back with a form (normally an error)."""

    async def _progress(hass_, request, redirect_uri, session, params):
        return {"type": "form", "errors": errors, "data_schema": None}

    monkeypatch.setattr(
        XiaoduOAuthAuthorizeView, "_progress_flow", staticmethod(_progress)
    )


def _spy_login_hooks(monkeypatch: pytest.MonkeyPatch) -> tuple[AsyncMock, Mock]:
    """Replace HA's login bookkeeping with spies.

    ``process_wrong_login`` is a coroutine (it does a reverse DNS lookup),
    ``process_success_login`` is a plain ``@callback`` function.
    """
    wrong = AsyncMock()
    success = Mock()
    monkeypatch.setattr(oauth_server, "process_wrong_login", wrong)
    monkeypatch.setattr(oauth_server, "process_success_login", success)
    return wrong, success


async def test_active_user_is_redirected_with_code(
    hass: HomeAssistant, entry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ordinary path still issues a code and redirects to Xiaodu."""
    _finish_login(
        monkeypatch, hass, SimpleNamespace(id="user-1", is_active=True, local_only=False)
    )
    _start_session(hass)

    response = await XiaoduOAuthAuthorizeView().post(_Request(hass, nonce=NONCE))

    assert response.status == 302
    assert "code=" in response.headers["Location"]
    assert NONCE not in _sessions(hass)


@pytest.mark.parametrize(
    ("user", "expected_error"),
    [
        # Credential resolved to no user: fail closed instead of binding "".
        (None, "登录未完成"),
        # Deactivated account.
        (
            SimpleNamespace(id="u", is_active=False, local_only=False),
            "该账号不允许授权",
        ),
        # "Local network only" account, request coming from a public IP.
        (
            SimpleNamespace(id="u", is_active=True, local_only=True),
            "该账号不允许授权",
        ),
    ],
)
async def test_login_that_must_not_be_authorized(
    hass: HomeAssistant,
    entry,
    monkeypatch: pytest.MonkeyPatch,
    user: object,
    expected_error: str,
) -> None:
    """No code is issued, the session is dropped, the throttle stays clean."""
    _finish_login(monkeypatch, hass, user)
    _start_session(hass)

    response = await XiaoduOAuthAuthorizeView().post(_Request(hass, nonce=NONCE))

    assert "Location" not in response.headers  # never redirected to Xiaodu
    assert expected_error in response.text
    assert NONCE not in _sessions(hass)
    # A refused authorization is not a wrong password: the throttle must not
    # record a failure. (The per-IP key may exist with an empty list, because
    # _login_throttled rewrites it on every pass.)
    assert not any(_failures(hass).values())


# ---------------------------------------------------------------------------
# HACS review item 2: feed HA's own login bookkeeping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("base", ["invalid_auth", "invalid_code"])
async def test_wrong_password_is_reported_to_ha(
    hass: HomeAssistant, entry, monkeypatch: pytest.MonkeyPatch, base: str
) -> None:
    """A bad password or MFA code must reach HA, which owns the IP ban."""
    wrong, success = _spy_login_hooks(monkeypatch)
    _finish_form(monkeypatch, {"base": base})
    _start_session(hass)

    response = await XiaoduOAuthAuthorizeView().post(_Request(hass, nonce=NONCE))

    wrong.assert_awaited_once()
    success.assert_not_called()
    assert response.status == 200  # stays on our page, never redirects
    assert len(_failures(hass)[PUBLIC_IP]) == 1  # our own throttle also counts


@pytest.mark.parametrize(
    "errors",
    [
        None,  # form without any error
        {"base": "unknown"},  # some other flow error
        {"password": "invalid_auth"},  # field-level, not the flow's base error
    ],
)
async def test_other_form_outcomes_are_not_wrong_logins(
    hass: HomeAssistant, entry, monkeypatch: pytest.MonkeyPatch, errors
) -> None:
    """Only ``base`` errors invalid_auth/invalid_code count as a bad login."""
    wrong, success = _spy_login_hooks(monkeypatch)
    _finish_form(monkeypatch, errors)
    _start_session(hass)

    await XiaoduOAuthAuthorizeView().post(_Request(hass, nonce=NONCE))

    wrong.assert_not_called()
    success.assert_not_called()


async def test_successful_login_resets_ha_attempts(
    hass: HomeAssistant, entry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A later good login must clear the counter HA uses to ban the IP."""
    wrong, success = _spy_login_hooks(monkeypatch)
    _finish_login(
        monkeypatch, hass, SimpleNamespace(id="user-1", is_active=True, local_only=False)
    )
    _start_session(hass)
    _record_failure(hass, PUBLIC_IP)  # an earlier typo

    response = await XiaoduOAuthAuthorizeView().post(_Request(hass, nonce=NONCE))

    success.assert_called_once()
    wrong.assert_not_called()
    assert response.status == 302
    assert PUBLIC_IP not in _failures(hass)


@pytest.mark.parametrize(
    "user",
    [
        None,
        SimpleNamespace(id="u", is_active=False, local_only=False),
        SimpleNamespace(id="u", is_active=True, local_only=True),
    ],
)
async def test_refused_login_leaves_ha_counters_alone(
    hass: HomeAssistant, entry, monkeypatch: pytest.MonkeyPatch, user: object
) -> None:
    """Neither success nor failure: the earlier typo must stay on record."""
    wrong, success = _spy_login_hooks(monkeypatch)
    _finish_login(monkeypatch, hass, user)
    _start_session(hass)
    _record_failure(hass, PUBLIC_IP)

    await XiaoduOAuthAuthorizeView().post(_Request(hass, nonce=NONCE))

    wrong.assert_not_called()
    success.assert_not_called()
    assert PUBLIC_IP in _failures(hass)


# ---------------------------------------------------------------------------
# HACS review item 3: no device info before login, bounded session table
# ---------------------------------------------------------------------------


async def test_login_page_does_not_reveal_devices(
    hass: HomeAssistant, entry
) -> None:
    """An unauthenticated GET must not disclose what is exposed to Xiaodu."""
    hass.data[DOMAIN][DATA_ENHANCED_DEVICES] = _Enhanced(
        ["SECRET-ROOM-LAMP", "SECRET-ROOM-LOCK"]
    )

    response = await XiaoduOAuthAuthorizeView().get(_Request(hass))

    assert response.status == 200
    assert "SECRET-ROOM-LAMP" not in response.text
    assert "SECRET-ROOM-LOCK" not in response.text
    assert "授权小度访问以下设备" not in response.text
    assert "__ENTITY_SUMMARY__" not in response.text


def test_expired_sessions_are_purged_on_create(hass: HomeAssistant) -> None:
    """A session abandoned without its cookie must not linger forever."""
    sessions = _sessions(hass)
    sessions["stale"] = {"flow_id": None, "expires_at": time.time() - 1}
    sessions["live"] = {"flow_id": None, "expires_at": time.time() + 300}

    _new_session(hass)

    assert "stale" not in sessions
    assert "live" in sessions  # only expired entries are swept


def test_session_table_is_capped(hass: HomeAssistant) -> None:
    """A flood of authorize GETs must not grow the table without limit."""
    sessions = _sessions(hass)
    core = time.time()
    for index in range(MAX_SESSIONS):
        sessions[f"s{index:03d}"] = {
            "flow_id": None,
            "expires_at": core + 10 + index,  # all still live
        }

    _new_session(hass)

    assert len(sessions) == MAX_SESSIONS
    assert "s000" not in sessions  # oldest evicted to make room
    assert f"s{MAX_SESSIONS - 1:03d}" in sessions