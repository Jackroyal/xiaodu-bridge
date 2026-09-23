"""Pure-logic tests for the DuerOS state-report helper (no HA runtime)."""

import asyncio
import importlib.util
import sys
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace

from tests._dueros_loader import load_dueros

ROOT = Path(__file__).resolve().parents[1]
_XIAODU = ROOT / "custom_components" / "xiaodu_bridge"

# Load the protocol stack first (registers the synthetic ``xiaodu`` package),
# then load state_report.py standalone.
load_dueros()

_spec = importlib.util.spec_from_file_location(
    "xiaodu.state_report", _XIAODU / "state_report.py"
)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
sys.modules["xiaodu.state_report"] = _module
_spec.loader.exec_module(_module)

build_change_report = _module.build_change_report
changed_attribute_names = _module.changed_attribute_names
report_changed_attribute = _module.report_changed_attribute
DUEROS_CHANGE_REPORT_URL = _module.DUEROS_CHANGE_REPORT_URL

class _FakeResponse:
    status = 200

    def __init__(self, msg="update 1 attributes", data=None):
        self._msg = msg
        self._data = data if data is not None else {}

    async def json(self, **kwargs):
        return {"status": 0, "msg": self._msg, "data": self._data}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

class _FakeSession:
    def __init__(self, msg="update 1 attributes", data=None):
        self.posts = []
        self._msg = msg
        self._data = data

    def post(self, url, json=None):
        self.posts.append((url, json))
        return _FakeResponse(self._msg, self._data)

class _Entry:
    data = {"bot_id": "bot-1"}

class _Store:
    def __init__(self, open_uids=("open-1", "open-2")):
        self._open_uids = list(open_uids)

    def open_uids(self):
        return list(self._open_uids)

def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)

def test_build_change_report_shape():
    report = build_change_report(
        "bot-1", "open-1", "light.bedroom", "brightness", message_id="msg-1"
    )
    assert report["header"] == {
        "namespace": "DuerOS.ConnectedHome.Control",
        "name": "ChangeReportRequest",
        "messageId": "msg-1",
        "payloadVersion": "1",
    }
    assert report["payload"] == {
        "botId": "bot-1",
        "openUid": "open-1",
        "appliance": {
            "applianceId": "light.bedroom",
            "attributeName": "brightness",
        },
    }

def test_build_change_report_generates_message_id():
    report = build_change_report("bot-1", "open-1", "light.bedroom", "turnOnState")
    assert report["header"]["messageId"]
    assert report["payload"]["appliance"]["attributeName"] == "turnOnState"

def test_changed_attribute_names_diffs_values_and_new_names():
    old = {"turnOnState": "ON", "brightness": "50.0"}
    new = {"turnOnState": "ON", "brightness": "80.0", "connectivity": "REACHABLE"}
    assert changed_attribute_names(old, new) == {"brightness", "connectivity"}

def test_changed_attribute_names_ignores_identical_values():
    snapshot = {"turnOnState": "ON", "brightness": "50.0"}
    assert changed_attribute_names(snapshot, dict(snapshot)) == set()

def test_changed_attribute_names_no_previous_snapshot():
    assert changed_attribute_names(None, {"brightness": "10.0"}) == set()

def test_report_pushes_one_request_per_open_uid():
    session = _FakeSession()
    accepted = _run(
        report_changed_attribute(
            None, _Entry(), _Store(), "light.bedroom", "brightness", session=session
        )
    )
    assert len(session.posts) == 2
    assert accepted is True
    for url, payload in session.posts:
        assert url == DUEROS_CHANGE_REPORT_URL
        assert payload["payload"]["botId"] == "bot-1"
        assert payload["payload"]["appliance"]["attributeName"] == "brightness"
    assert {p[1]["payload"]["openUid"] for p in session.posts} == {"open-1", "open-2"}

def test_report_skips_without_bot_id():
    session = _FakeSession()
    entry = _Entry()
    entry.data = {"client_id": "x"}
    _run(
        report_changed_attribute(
            None, entry, _Store(), "light.bedroom", "brightness", session=session
        )
    )
    assert session.posts == []

def test_report_skips_without_bound_users():
    session = _FakeSession()
    accepted = _run(
        report_changed_attribute(
            None, _Entry(), _Store([]), "light.bedroom", "brightness", session=session
        )
    )
    assert session.posts == []
    assert accepted is False


def test_report_logs_the_whole_body_when_the_cloud_does_not_acknowledge(caplog):
    # DuerOS can answer a ChangeReport with a refusal whose reason only exists
    # in the body ("Cloud response name is not ReportStateResponse, stop
    # sync", status 21096, updated_attribute_num 0): keep the full body so the
    # cause is diagnosable from the log, and do not count the push as synced.
    session = _FakeSession(
        msg="Cloud response name is not ReportStateResponse, stop sync",
        data={"updated_attribute_num": 0},
    )
    with caplog.at_level("WARNING"):
        accepted = _run(
            report_changed_attribute(
                None, _Entry(), _Store(("open-1",)), "light.bedroom", "brightness",
                session=session,
            )
        )
    assert accepted is False
    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    assert "云端未确认同步" in warnings[0].getMessage()
    assert "Cloud response name is not ReportStateResponse" in warnings[0].getMessage()


def test_report_treats_zero_updated_attributes_as_not_synced():
    # The count DuerOS reports is authoritative: an "update" wording with
    # updated_attribute_num 0 did not land, so the attribute must stay out of
    # the per-attribute cooldown and be re-sent on its next change.
    session = _FakeSession(msg="update 0 attributes", data={"updated_attribute_num": 0})
    accepted = _run(
        report_changed_attribute(
            None, _Entry(), _Store(("open-1",)), "light.bedroom", "brightness",
            session=session,
        )
    )
    assert accepted is False


def test_report_treats_the_documented_rate_limit_as_not_synced():
    session = _FakeSession(msg="One attribute can only sync 1 times during 60")
    accepted = _run(
        report_changed_attribute(
            None, _Entry(), _Store(("open-1",)), "light.bedroom", "brightness",
            session=session,
        )
    )
    assert accepted is False


def test_report_stays_quiet_on_the_usual_acknowledgement(caplog):
    session = _FakeSession(msg="update 7 attributes", data={"updated_attribute_num": 7})
    with caplog.at_level("WARNING"):
        accepted = _run(
            report_changed_attribute(
                None, _Entry(), _Store(("open-1",)), "light.bedroom", "brightness",
                session=session,
            )
        )
    assert accepted is True
    assert [r for r in caplog.records if r.levelname == "WARNING"] == []

def test_refused_push_retries_once_per_state_change(monkeypatch):
    # 被拒的推送补发一次：一次拒绝只补一次（云端持续拒绝时不至于变成重试循环），
    # 而该属性下次真实变化会重新获得一次补发机会。
    delays = []

    def _fake_call_later(hass, delay, action):
        delays.append(delay)
        return lambda: None

    monkeypatch.setattr("homeassistant.helpers.event.async_call_later", _fake_call_later)
    manager = _module.StateReportManager(SimpleNamespace(), _Entry())

    assert manager._take_retry("dev", "brightness") is True
    assert manager._take_retry("dev", "brightness") is False  # 补发再被拒 → 不再补

    manager._schedule_report("dev", {"brightness"})  # 新的状态变化 → 重新授权
    assert delays == [_module.STATE_REPORT_DEBOUNCE_SECONDS]
    assert manager._take_retry("dev", "brightness") is True
    assert manager._take_retry("dev", "turnOnState") is True  # 属性之间互不影响
    assert manager._take_retry("dev", "brightness") is False


def test_flush_reschedules_a_refused_attribute_once(monkeypatch):
    # 端到端：被拒的属性回到 pending 并在 REFUSAL_RETRY_SECONDS 后被重报；
    # 已同步的属性记冷却（不重报）。
    async def _refused(hass, entry, store, device_id, attribute_name):
        return False

    async def _accepted(hass, entry, store, device_id, attribute_name):
        return True

    async def _store(hass):
        return _Store(("open-1",))

    # 只桩掉 _get_store（真 oauth_server 会拉整套 HA web 依赖，与本用例无关）
    fake_oauth = ModuleType("xiaodu.oauth_server")
    fake_oauth._get_store = _store
    monkeypatch.setitem(sys.modules, "xiaodu.oauth_server", fake_oauth)

    delays = []

    def _fake_call_later(hass, delay, action):
        delays.append(delay)
        return lambda: None

    monkeypatch.setattr("homeassistant.helpers.event.async_call_later", _fake_call_later)
    monkeypatch.setattr(_module, "report_changed_attribute", _refused)

    manager = _module.StateReportManager(SimpleNamespace(), _Entry())
    manager._pending["dev"] = {"brightness"}
    _run(manager._async_flush("dev", None))

    assert manager._pending["dev"] == {"brightness"}
    assert delays == [_module.REFUSAL_RETRY_SECONDS]
    assert ("dev", "brightness") not in manager._last_sync  # 没同步 → 不记冷却

    monkeypatch.setattr(_module, "report_changed_attribute", _accepted)
    delays.clear()
    _run(manager._async_flush("dev", None))
    assert manager._pending.get("dev") in (None, set())
    assert delays == []  # 同步成功 → 不再排补发
    assert ("dev", "brightness") in manager._last_sync


def test_rebuild_keeps_in_flight_reports(monkeypatch):
    # 重建（开机 / 选项保存）只作废冷却与确认状态，不能丢掉「还没同步」的上报
    # 定时器：开机那一波正是云端最容易拒绝的时候，丢掉定时器＝这次补发机会没了。
    delays = []

    def _fake_call_later(hass, delay, action):
        delays.append(delay)
        return lambda: None

    monkeypatch.setattr("homeassistant.helpers.event.async_call_later", _fake_call_later)
    manager = _module.StateReportManager(SimpleNamespace(), _Entry())
    manager._devices = {"dev": SimpleNamespace(capabilities=())}
    manager._pending["dev"] = {"brightness"}
    manager._handles["dev"] = lambda: None
    manager._last_sync[("dev", "brightness")] = time.monotonic()
    manager._retry_used.add(("dev", "brightness"))

    manager._rebuild_index(reset_cooldowns=True)

    assert manager._pending == {"dev": {"brightness"}}
    assert "dev" in manager._handles
    assert "dev" not in delays  # 定时器不重排、也不取消
    assert manager._last_sync == {}
    assert manager._retry_used == set()


def _fake_binding(role, entity_id):
    return SimpleNamespace(role=role, entity_id=entity_id)


def _fake_cap(key, bindings, appliance_types=("LIGHT",)):
    return SimpleNamespace(
        key=key,
        bindings=[_fake_binding(r, e) for r, e in bindings],
        read=lambda ctx: None,
    )


def _fake_device(device_id, caps, appliance_types=("LIGHT",)):
    return SimpleNamespace(
        device_id=device_id, appliance_types=appliance_types, capabilities=caps
    )


def test_structure_signature_is_stable_and_change_sensitive():
    sig = _module.StateReportManager._structure_signature
    power_a = lambda: _fake_cap("power", [("power", "light.a")])
    dev = _fake_device("d1", [power_a()])
    same = _fake_device("d1", [power_a()])
    assert sig([dev]) == sig([same])            # equal structure -> equal signature
    assert sig([dev, same]) == sig([same, dev])  # order-insensitive
    # binding moved to another entity
    assert sig([dev]) != sig([_fake_device("d1", [_fake_cap("power", [("power", "light.b")])])])
    # capability added
    assert sig([dev]) != sig([_fake_device("d1", [power_a(), _fake_cap("brightness", [("target", "light.a")])])])
    # device id changed
    assert sig([dev]) != sig([_fake_device("d2", [power_a()])])
    # appliance type changed
    assert sig([dev]) != sig([_fake_device("d1", [power_a()], appliance_types=("SWITCH",))])
    assert sig([]) == ()


def test_async_refresh_if_changed_only_rebuilds_on_structure_change(monkeypatch):
    class _States:
        def get(self, entity_id):
            return None

    class _Hass:
        states = _States()

    current = [_fake_device("d1", [_fake_cap("power", [("power", "light.a")])])]

    class _Set:
        def all(self):
            return list(current)

    enhanced_mod = sys.modules["xiaodu.dueros.enhanced"]
    monkeypatch.setattr(
        enhanced_mod, "build_enhanced_for_hass", lambda hass, entry: _Set()
    )

    mgr = _module.StateReportManager(_Hass(), object())
    mgr.async_rebuild()
    assert "light.a" in mgr._index

    # No structure change -> no rebuild, signature stable.
    assert mgr.async_refresh_if_changed() is False

    # Structure change -> rebuild, but per-attribute cooldowns are kept.
    mgr._last_sync[("d1", "power")] = 123.0
    current.clear()
    current.append(_fake_device("d1", [_fake_cap("power", [("power", "light.b")])]))
    assert mgr.async_refresh_if_changed() is True
    assert "light.b" in mgr._index and "light.a" not in mgr._index
    assert mgr._last_sync[("d1", "power")] == 123.0

    # After shutdown the refresh is a no-op.
    mgr._stopped = True
    assert mgr.async_refresh_if_changed() is False


def test_report_returns_false_when_rate_limited():
    session = _FakeSession(msg="One attribute can only sync 1 times during 60")
    accepted = _run(
        report_changed_attribute(
            None, _Entry(), _Store(), "light.bedroom", "brightness", session=session
        )
    )
    assert session.posts
    assert accepted is False
