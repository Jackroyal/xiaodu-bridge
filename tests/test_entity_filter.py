"""Tests for the standalone legacy entity filter (no Home Assistant needed).

``entity_filter.py`` only uses the Python standard library, so this module
loads it directly instead of importing the integration package (which would
require a Home Assistant environment).
"""

import sys
from importlib import util
from pathlib import Path

_ENTITY_FILTER_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "xiaodu"
    / "entity_filter.py"
)

_spec = util.spec_from_file_location("xiaodu_entity_filter", _ENTITY_FILTER_PATH)
assert _spec is not None and _spec.loader is not None
_module = util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)
EntityFilter = _module.EntityFilter


def test_empty_filter_allows_everything() -> None:
    filt = EntityFilter()
    assert filt.allowed("light.living_room")
    assert filt.allowed("switch.any")


def test_exclude_wins_over_include() -> None:
    filt = EntityFilter(include={"light.*"}, exclude={"light.bathroom"})
    assert filt.allowed("light.living_room")
    assert not filt.allowed("light.bathroom")
    assert not filt.allowed("switch.kitchen")


def test_include_narrows_default() -> None:
    filt = EntityFilter(include={"light.*", "switch.kitchen"})
    assert filt.allowed("light.living_room")
    assert filt.allowed("switch.kitchen")
    assert not filt.allowed("media_player.tv")


def test_from_lists_handles_none() -> None:
    filt = EntityFilter.from_lists(None, ["switch.*"])
    assert not filt.allowed("switch.tv")
    assert filt.allowed("light.tv")
