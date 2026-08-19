"""Tests for the standalone OAuth store (no Home Assistant needed).

``oauth_store.py`` only uses the Python standard library, so this module
loads it (and its ``const`` dependency) directly via importlib.
"""

import sys
import time
from importlib import util
from pathlib import Path

_BASE = Path(__file__).resolve().parents[1] / "custom_components" / "ha_xiaodu"


def _load(name: str, filename: str):
    spec = util.spec_from_file_location(name, _BASE / filename)
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_const = _load("xiaodu_pkg.const", "const.py")
_store = _load("xiaodu_pkg.oauth_store", "oauth_store.py")
XiaoduOAuthStore = _store.XiaoduOAuthStore


def test_code_issue_and_single_use() -> None:
    store = XiaoduOAuthStore()
    code = store.issue_code(
        "dueros_test", "https://xiaodu.baidu.com/saiya/auth/x", "user-1"
    )
    record = store.consume_code(code)
    assert record is not None
    assert record["client_id"] == "dueros_test"
    assert record["user_id"] == "user-1"
    assert store.consume_code(code) is None


def test_expired_code_rejected() -> None:
    store = XiaoduOAuthStore()
    code = store.issue_code("c", "r")
    store._codes[code]["expires_at"] = time.time() - 1
    assert store.consume_code(code) is None


def test_token_issue_validate_rotate() -> None:
    store = XiaoduOAuthStore()
    access, refresh = store.issue_token("dueros_test", "user-1")
    assert store.validate_token(access)
    assert not store.validate_token("bogus")

    access2, refresh2 = store.rotate_token(refresh)
    assert not store.validate_token(access)  # old access token is gone
    assert store.validate_token(access2)
    assert store.rotate_token(refresh) is None  # old refresh token is gone
    assert store.rotate_token(refresh2) is not None


def test_user_id_survives_rotation() -> None:
    store = XiaoduOAuthStore()
    access, refresh = store.issue_token("dueros_test", "user-1")
    access2, refresh2 = store.rotate_token(refresh)
    record = store._tokens[access2]
    assert record["user_id"] == "user-1"


def test_access_expiry_keeps_refresh_valid() -> None:
    store = XiaoduOAuthStore()
    access, refresh = store.issue_token("dueros_test")
    store._tokens[access]["access_expires_at"] = time.time() - 1

    assert not store.validate_token(access)  # access expired
    assert store.rotate_token(refresh) is not None  # refresh still usable


def test_refresh_expiry_invalidates_pair() -> None:
    store = XiaoduOAuthStore()
    access, refresh = store.issue_token("dueros_test")
    store._tokens[access]["refresh_expires_at"] = time.time() - 1

    assert store.rotate_token(refresh) is None
    store._purge()
    assert not store.validate_token(access)


def test_persistence_roundtrip() -> None:
    store = XiaoduOAuthStore()
    access, refresh = store.issue_token("dueros_test", "user-1")
    data = store.to_dict()

    restored = XiaoduOAuthStore()
    restored.load_dict(data)
    assert restored.validate_token(access)
    restored._tokens[access]["user_id"] == "user-1"
    assert restored.rotate_token(refresh) is not None


def test_record_open_uid_associates_user() -> None:
    store = XiaoduOAuthStore()
    access, _ = store.issue_token("dueros_test", "user-1")
    assert store.user_id_for_token(access) == "user-1"
    assert store.user_id_for_token("bogus") is None

    assert store.record_open_uid("user-1", "open-1") is True
    assert store.record_open_uid("user-1", "open-1") is False  # unchanged
    assert store.record_open_uid("user-2", "open-2") is True
    assert store.open_uids() == ["open-1", "open-2"]

    restored = XiaoduOAuthStore()
    restored.load_dict(store.to_dict())
    assert restored.open_uids() == ["open-1", "open-2"]


def test_remove_open_uid_for_user() -> None:
    store = XiaoduOAuthStore()
    store.record_open_uid("user-1", "open-1")
    store.record_open_uid("user-2", "open-2")
    assert store.remove_open_uid("user-1") is True
    assert store.open_uids() == ["open-2"]
    assert store.remove_open_uid("user-1") is False


def test_revoke_removes_access_and_refresh() -> None:
    store = XiaoduOAuthStore()
    access, refresh = store.issue_token("dueros_test", "user-1")
    assert store.validate_token(access)

    store.revoke(access)
    assert not store.validate_token(access)
    assert store.rotate_token(refresh) is None  # refresh link is gone too
