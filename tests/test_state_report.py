"""Pure-logic tests for the DuerOS state-report helper (no HA runtime)."""

import asyncio
import importlib.util
import sys
from pathlib import Path

from tests._dueros_loader import load_dueros

ROOT = Path(__file__).resolve().parents[1]
_XIAODU = ROOT / "custom_components" / "ha_xiaodu"

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

    def __init__(self, msg="update 1 attributes"):
        self._msg = msg

    async def json(self, **kwargs):
        return {"status": 0, "msg": self._msg, "data": {}}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

class _FakeSession:
    def __init__(self, msg="update 1 attributes"):
        self.posts = []
        self._msg = msg

    def post(self, url, json=None):
        self.posts.append((url, json))
        return _FakeResponse(self._msg)

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

def test_report_returns_false_when_rate_limited():
    session = _FakeSession(msg="One attribute can only sync 1 times during 60")
    accepted = _run(
        report_changed_attribute(
            None, _Entry(), _Store(), "light.bedroom", "brightness", session=session
        )
    )
    assert session.posts
    assert accepted is False
