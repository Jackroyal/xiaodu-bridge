"""Load the DuerOS protocol + device model without importing homeassistant.

Importing ``custom_components.ha_xiaodu`` executes its ``__init__.py``, which
pulls in homeassistant. The protocol/device layers only import HA under
TYPE_CHECKING, so we can load them standalone for pure-logic tests.

The package tree is simulated as ``xiaodu`` -> ``xiaodu.dueros`` so relative
imports (``from ..devices import ...``) resolve correctly.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_XIAODU = _ROOT / "custom_components" / "ha_xiaodu"


def _load_module(modname: str, filename: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(modname, filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module


def _load_parent() -> types.ModuleType:
    """Register the synthetic ``xiaodu`` parent package."""
    parent = types.ModuleType("xiaodu")
    parent.__path__ = [str(_XIAODU)]
    sys.modules["xiaodu"] = parent
    _load_module("xiaodu.const", _XIAODU / "const.py")
    _load_module("xiaodu.entity_filter", _XIAODU / "entity_filter.py")
    _load_module("xiaodu.devices", _XIAODU / "devices.py")
    return parent


def load_devices() -> types.ModuleType:
    """Load the device/capability model standalone (no HA runtime)."""
    _load_parent()
    return sys.modules["xiaodu.devices"]


def load_dueros() -> tuple:
    """Return (handle_request, EntityFilter, protocol_module)."""
    _load_parent()

    pkg = types.ModuleType("xiaodu.dueros")
    pkg.__path__ = [str(_XIAODU / "dueros")]
    sys.modules["xiaodu.dueros"] = pkg

    _load_module("xiaodu.dueros.constants", _XIAODU / "dueros" / "constants.py")
    _load_module("xiaodu.dueros.adapters", _XIAODU / "dueros" / "adapters.py")
    protocol = _load_module("xiaodu.dueros.protocol", _XIAODU / "dueros" / "protocol.py")

    return protocol.handle_request, sys.modules["xiaodu.entity_filter"].EntityFilter, protocol
