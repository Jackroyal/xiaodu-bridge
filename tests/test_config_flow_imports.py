"""Static sanity check: every ``CONF_*`` name used by config_flow exists.

``config_flow.py`` imports Home Assistant at module import time, so it cannot
be executed in the standalone test environment. Instead we parse its source
and verify that every ``CONF_*`` name it references is defined in
``xiaodu.const`` (this catches missing-import regressions like the
``CONF_UNITS`` NameError in the options wizard).
"""

import ast
import sys
from importlib import util
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CONFIG_FLOW = _ROOT / "custom_components" / "ha_xiaodu" / "config_flow.py"
_CONST = _ROOT / "custom_components" / "ha_xiaodu" / "const.py"


def _load_const() -> object:
    spec = util.spec_from_file_location("xiaodu_const_check", _CONST)
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_every_conf_name_used_by_config_flow_is_defined() -> None:
    tree = ast.parse(_CONFIG_FLOW.read_text())
    const = _load_const()
    used = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id.startswith("CONF_")
    }
    missing = used - set(dir(const))
    assert not missing, f"config_flow uses const names that are not defined: {missing}"
