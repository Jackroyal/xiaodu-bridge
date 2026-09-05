"""Load the DuerOS protocol + device model without importing homeassistant.

Importing ``custom_components.xiaodu_bridge`` executes its ``__init__.py``, which
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
_XIAODU = _ROOT / "custom_components" / "xiaodu_bridge"


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
    _load_module("xiaodu.devices", _XIAODU / "devices.py")
    return parent


def load_devices() -> types.ModuleType:
    """Load the device/capability model standalone (no HA runtime)."""
    _load_parent()
    return sys.modules["xiaodu.devices"]


def load_dueros() -> tuple:
    """Return (handle_request, protocol_module)."""
    _load_parent()

    pkg = types.ModuleType("xiaodu.dueros")
    pkg.__path__ = [str(_XIAODU / "dueros")]
    sys.modules["xiaodu.dueros"] = pkg

    for mod in ("constants", "model", "composers", "registry", "profiles", "defaults", "enhanced"):
        _load_module(f"xiaodu.dueros.{mod}", _XIAODU / "dueros" / f"{mod}.py")
    protocol = _load_module("xiaodu.dueros.protocol", _XIAODU / "dueros" / "protocol.py")

    return protocol.handle_request, protocol


def load_semantic_model() -> types.ModuleType:
    """Load the long-term semantic model (model / composers / registry) standalone.

    These modules only import HA under TYPE_CHECKING, so they can be loaded
    without a Home Assistant runtime; reloading a fresh ``xiaodu.dueros``
    package keeps the registry isolated per test.
    """
    _load_parent()

    pkg = types.ModuleType("xiaodu.dueros")
    pkg.__path__ = [str(_XIAODU / "dueros")]
    sys.modules["xiaodu.dueros"] = pkg

    _load_module("xiaodu.dueros.constants", _XIAODU / "dueros" / "constants.py")
    _load_module("xiaodu.dueros.model", _XIAODU / "dueros" / "model.py")
    _load_module("xiaodu.dueros.composers", _XIAODU / "dueros" / "composers.py")
    _load_module("xiaodu.dueros.registry", _XIAODU / "dueros" / "registry.py")
    _load_module("xiaodu.dueros.profiles", _XIAODU / "dueros" / "profiles.py")
    _load_module("xiaodu.dueros.defaults", _XIAODU / "dueros" / "defaults.py")

    return sys.modules["xiaodu.dueros.registry"]


def load_enhanced() -> tuple:
    """Return (protocol_module, enhanced_module) with the semantic stack loaded."""
    _load_parent()
    pkg = types.ModuleType("xiaodu.dueros")
    pkg.__path__ = [str(_XIAODU / "dueros")]
    sys.modules["xiaodu.dueros"] = pkg
    for mod in ("constants", "model", "composers", "registry", "profiles", "defaults", "enhanced"):
        _load_module(f"xiaodu.dueros.{mod}", _XIAODU / "dueros" / f"{mod}.py")
    protocol = _load_module("xiaodu.dueros.protocol", _XIAODU / "dueros" / "protocol.py")
    return protocol, sys.modules["xiaodu.dueros.enhanced"]
