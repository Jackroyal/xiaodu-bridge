"""Pure-logic tests for the DuerOS device-sync helper (no HA runtime)."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_XIAODU = ROOT / "custom_components" / "ha_xiaodu"

import types  # noqa: E402

pkg = types.ModuleType("xiaodu")
pkg.__path__ = [str(_XIAODU)]
sys.modules["xiaodu"] = pkg


def _load(name: str, filename: Path):
    spec = importlib.util.spec_from_file_location(name, filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_load("xiaodu.const", _XIAODU / "const.py")
_sync = _load("xiaodu.dueros_sync", _XIAODU / "dueros_sync.py")

build_sync_batches = _sync.build_sync_batches
build_sync_payload = _sync.build_sync_payload
sync_devices = _sync.sync_devices

import asyncio  # noqa: E402


class _FakeResponse:
    status = 200

    async def json(self, **kwargs):
        return {"status": 0, "msg": "ok"}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


class _FakeSession:
    def __init__(self):
        self.posts = []

    def post(self, url, json=None):
        self.posts.append((url, json))
        return _FakeResponse()


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def test_build_sync_batches_splits_at_five():
    uids = [f"open-{i}" for i in range(12)]
    batches = build_sync_batches(uids)
    assert [len(b) for b in batches] == [5, 5, 2]
    assert build_sync_batches([]) == []


def test_build_sync_payload_shape():
    payload = build_sync_payload("bot-1", "log-1", ["a", "b"])
    assert payload == {"botId": "bot-1", "logId": "log-1", "openUids": ["a", "b"]}


def test_sync_devices_skips_without_bot_id():
    class _Entry:
        data = {"client_id": "x"}

    class _Store:
        def open_uids(self):
            return ["open-1"]

    session = _FakeSession()
    _run(sync_devices(None, _Entry(), _Store(), session=session))
    assert session.posts == []


def test_sync_devices_skips_without_users():
    class _Entry:
        data = {"bot_id": "bot-1"}

    class _Store:
        def open_uids(self):
            return []

    session = _FakeSession()
    _run(sync_devices(None, _Entry(), _Store(), session=session))
    assert session.posts == []


def test_sync_devices_posts_batches():
    class _Entry:
        data = {"bot_id": "bot-1"}

    class _Store:
        def open_uids(self):
            return [f"open-{i}" for i in range(6)]

    session = _FakeSession()
    _run(sync_devices(None, _Entry(), _Store(), session=session))
    assert len(session.posts) == 2
    for _, payload in session.posts:
        assert payload["botId"] == "bot-1"
        assert len(payload["openUids"]) <= 5
        assert payload["logId"]
    assert [len(p["openUids"]) for _, p in session.posts] == [5, 1]
