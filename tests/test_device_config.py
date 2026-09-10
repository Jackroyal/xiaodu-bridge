"""Pure-logic tests for the per-device object config normalization/accessors.

Stage B stores ``options[CONF_DEVICES]`` as ``{device_key: {caps, bindings,
hidden, names, mode}}``. Normalization is read-side: it migrates the legacy
flat list and per-entity dict shapes on the fly without writing back, and never
infers ``hidden`` from the per-entity shape.
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
    assert normalize({"dev": []}) == {"dev": {"caps": []}}


def test_normalize_flat_list():
    assert normalize_entry(["power", "brightness"]) == {
        "caps": ["power", "brightness"]
    }
    assert normalize_entry([]) == {"caps": []}
    assert normalize_entry(()) == {"caps": []}


def test_normalize_per_entity_dict_unions_caps():
    # Legacy per-entity dict: union of every entity's capability list, deduped.
    raw = {
        "switch.a": ["power", "brightness"],
        "switch.b": ["power"],
        "switch.c": ["colorTemperature"],
    }
    assert normalize_entry(raw) == {
        "caps": ["power", "brightness", "colorTemperature"]
    }


def test_normalize_per_entity_empty_is_default_all():
    assert normalize_entry({"switch.a": [], "switch.b": []}) == {"caps": []}
    assert normalize_entry({}) == {"caps": []}


def test_normalize_object_is_kept():
    raw = {
        "caps": ["power"],
        "bindings": {"heating": "switch.h"},
        "hidden": ["light.x"],
        "names": {"YUBA": "浴霸"},
        "mode": "generic",
    }
    assert normalize_entry(raw) == raw


def test_normalize_migrates_top_level_mix():
    assert normalize(
        {
            "a": ["power"],
            "b": {"switch.x": ["temperature"]},
            "c": {"caps": [], "mode": "YUBA"},
            "d": None,
        }
    ) == {
        "a": {"caps": ["power"]},
        "b": {"caps": ["temperature"]},
        "c": {"caps": [], "mode": "YUBA"},
        "d": {},
    }


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
