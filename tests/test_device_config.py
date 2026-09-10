"""Pure-logic tests for the per-device object config normalization/accessors.

``options[CONF_DEVICES]`` stores one object per ``device_key``
(``{caps, bindings, hidden, names, mode}``). Normalization is read-side and
keeps only the reserved object keys; a non-object value reads as unconfigured.
"""

from tests._dueros_loader import load_semantic_model

load_semantic_model()
from xiaodu.dueros.device_config import (
    bindings_of,
    device_caps,
    hidden_of,
    mode_of,
    names_of,
    normalize,
    normalize_entry,
)


# --- normalize / normalize_entry -------------------------------------------

def test_normalize_none_and_empty():
    assert normalize(None) is None
    assert normalize({}) == {}
    # A non-object value reads as an unconfigured (default-all) device.
    assert normalize({"dev": []}) == {"dev": {}}
    assert normalize({"dev": None}) == {"dev": {}}


def test_normalize_non_object_is_unconfigured():
    assert normalize_entry(None) == {}
    assert normalize_entry([]) == {}
    assert normalize_entry(()) == {}
    assert normalize_entry("power") == {}
    # A dict with no reserved keys (e.g. a stale entity-keyed table) is empty.
    assert normalize_entry({"switch.a": ["power"]}) == {}


def test_normalize_object_is_kept():
    raw = {
        "caps": ["power"],
        "bindings": {"heating": "switch.h"},
        "hidden": ["light.x"],
        "names": {"YUBA": "浴霸"},
        "mode": "generic",
    }
    assert normalize_entry(raw) == raw


def test_normalize_object_drops_unknown_keys():
    assert normalize_entry({"caps": "power", "stale": 1}) == {"caps": ["power"]}


# --- accessors ---------------------------------------------------------------

def test_accessors_empty_object():
    obj = {}
    assert device_caps(obj) is None
    assert bindings_of(obj) == {}
    assert hidden_of(obj) == []
    assert names_of(obj) == {}
    assert mode_of(obj) == "auto"
    assert device_caps(None) is None


def test_accessors_full_object():
    obj = {
        "caps": ["power", "mode"],
        "bindings": {"heating": "switch.h", "blow": ""},
        "hidden": ["light.x"],
        "names": {"YUBA": "浴霸"},
        "mode": "generic",
    }
    assert device_caps(obj) == ["power", "mode"]
    assert device_caps({"caps": []}) is None
    assert device_caps({"caps": None}) is None
    assert bindings_of(obj) == {"heating": "switch.h"}
    assert hidden_of(obj) == ["light.x"]
    assert names_of(obj) == {"YUBA": "浴霸"}
    assert mode_of(obj) == "generic"
    assert mode_of({"mode": ""}) == "auto"
