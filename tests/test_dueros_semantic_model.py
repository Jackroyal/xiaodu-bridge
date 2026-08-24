"""Pure-logic tests for the long-term semantic model (no HA runtime).

Covers ``dueros.model`` (DuerDevice / CapabilityMapping / AttributeValue),
``dueros.composers`` (power / mode_switches / select / target_temperature /
percentage / sensor_query / composite_power) and ``dueros.registry``.
"""

from tests._dueros_loader import load_semantic_model

registry_mod = load_semantic_model()

REGISTRY = registry_mod.REGISTRY
MappingRegistry = registry_mod.MappingRegistry
from xiaodu.dueros.model import (
    AttributeValue,
    CapabilityMapping,
    DuerAction,
    DuerAttribute,
    DuerCapability,
    DuerDevice,
    DuerDeviceProfile,
    EntityBinding,
    ServiceCall,
    make_attribute,
    make_device_id,
)
from xiaodu.dueros.composers import (
    composite_power_mapping,
    mode_switches_mapping,
    pause_mapping,
    percentage_mapping,
    power_mapping,
    select_mapping,
    sensor_query_mapping,
    target_temperature_mapping,
)
from xiaodu.dueros.constants import (
    ATTR_MODE,
    ATTR_TARGET_TEMPERATURE,
    ATTR_TURN_ON_STATE,
    ATTR_WARMTH_LEVEL,
    ATTR_PERCENTAGE,
)


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _device(caps):
    return DuerDevice(
        device_id="dueros-test",
        friendly_name="测试",
        profile_key="TEST",
        primary_entity_id="switch.x",
        capabilities=tuple(caps),
    )


# --- model ---

def test_attribute_value_to_dict():
    a = make_attribute(ATTR_TURN_ON_STATE, "ON", legal="(ON, OFF)")
    d = a.to_dict()
    assert d["name"] == "turnOnState"
    assert d["value"] == "ON"
    assert d["legalValue"] == "(ON, OFF)"
    assert "timestampOfSample" in d and "uncertaintyInMilliseconds" in d


def test_make_device_id_stable_and_independent_of_entity():
    a = make_device_id("YUBA", "ha-device-1")
    b = make_device_id("YUBA", "ha-device-1")
    assert a == b
    assert len(a) <= 40
    # Same physical device, different sub-device (e.g. 浴霸灯) -> different id.
    assert make_device_id("YUBA", "ha-device-1", "lamp") != a


def test_duer_device_actions_dedupe_and_find():
    cap1 = DuerCapability(
        "power", "开关", actions=(DuerAction("turnOn", "power"), DuerAction("turnOff", "power")),
    )
    cap2 = DuerCapability(
        "mode", "模式", actions=(DuerAction("setMode", "mode"), DuerAction("turnOn", "mode")),
    )
    dev = _device((
        CapabilityMapping(cap1, (), read=lambda ctx: None),
        CapabilityMapping(cap2, (), read=lambda ctx: None),
    ))
    assert dev.actions() == ["turnOn", "turnOff", "setMode"]  # turnOn deduped
    assert dev.find_capability("setMode").key == "mode"
    assert dev.find_capability("nope") is None


# --- power_mapping ---

def test_power_mapping_read_on_off():
    m = power_mapping(domain="switch", entity_id="switch.x", appliance_types=("SWITCH",))
    on = m.read(__import__("types").SimpleNamespace(entities={"power": FakeState("switch.x", "on")}))
    assert (on.name, on.value) == ("turnOnState", "ON")
    off = m.read(__import__("types").SimpleNamespace(entities={"power": FakeState("switch.x", "off")}))
    assert off.value == "OFF"


def test_power_mapping_write():
    m = power_mapping(domain="switch", entity_id="switch.x", appliance_types=("SWITCH",))
    ctx = __import__("types").SimpleNamespace(
        action=DuerAction("turnOn", "power"), payload={},
    )
    calls = m.write(ctx)
    assert calls == [ServiceCall("switch", "turn_on", {}, "switch.x")]


# --- mode_switches_mapping (1 capability -> N entities) ---

def test_mode_switches_read_which_is_on():
    m = mode_switches_mapping(
        modes=(("暖风", "heating", "switch.heating"),
               ("吹风", "blow", "switch.blow"),
               ("换气", "ventilation", "switch.ventilation")),
        appliance_types=("YUBA",),
    )
    entities = {
        "heating": FakeState("switch.heating", "off"),
        "blow": FakeState("switch.blow", "on"),
        "ventilation": FakeState("switch.ventilation", "off"),
    }
    val = m.read(__import__("types").SimpleNamespace(entities=entities))
    assert val.name == "mode" and val.value == "吹风"
    # none on -> empty mode
    entities2 = {k: FakeState(e, "off") for k, e in [("heating","switch.heating"),("blow","switch.blow"),("ventilation","switch.ventilation")]}
    assert m.read(__import__("types").SimpleNamespace(entities=entities2)).value == ""


def test_mode_switches_write_fanout():
    m = mode_switches_mapping(
        modes=(("暖风", "heating", "switch.heating"),
               ("吹风", "blow", "switch.blow"),
               ("换气", "ventilation", "switch.ventilation")),
        appliance_types=("YUBA",),
        exclusive=True,
    )
    entities = {
        "heating": FakeState("switch.heating", "off"),
        "blow": FakeState("switch.blow", "on"),
        "ventilation": FakeState("switch.ventilation", "off"),
    }
    ctx = __import__("types").SimpleNamespace(
        action=DuerAction("setMode", "mode", "mode"),
        payload={"mode": {"value": "暖风"}},
        entities=entities,
    )
    calls = m.write(ctx)
    # set 暖风 -> turn_on heating, and turn_off the now-inactive blow (exclusive)
    assert [(c.target_entity_id, c.service) for c in calls] == [
        ("switch.heating", "turn_on"), ("switch.blow", "turn_off"),
    ]


# --- select_mapping (warmthLevel via setGear) ---

def test_select_mapping_read_write():
    m = select_mapping(
        entity_id="select.warmth_level",
        attribute_name=ATTR_WARMTH_LEVEL,
        capability_key="warmthLevel",
        appliance_types=("YUBA",),
        set_action="setGear",
    )
    ctxr = __import__("types").SimpleNamespace(
        entities={"value": FakeState("select.warmth_level", "select", {"option": "暖风"})}
    )
    val = m.read(ctxr)
    assert val.name == ATTR_WARMTH_LEVEL and val.value == "暖风"
    ctxw = __import__("types").SimpleNamespace(
        action=DuerAction("setGear", "warmthLevel", "warmthLevel"),
        payload={"warmthLevel": {"value": "强暖"}},
    )
    calls = m.write(ctxw)
    assert calls[0].domain == "select"
    assert calls[0].data == {"option": "强暖"}


# --- target_temperature / percentage / sensor_query ---

def test_target_temperature_read():
    m = target_temperature_mapping(entity_id="number.temp", appliance_types=("YUBA",))
    val = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState("number.temp", "30", {})}))
    assert val.name == ATTR_TARGET_TEMPERATURE
    assert val.value == 30.0


def test_percentage_read():
    m = percentage_mapping(entity_id="cover.c", appliance_types=("CURTAIN",))
    val = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState("cover.c", "open", {"current_position": 60})}))
    assert val.name == ATTR_PERCENTAGE and val.value == 60


def test_sensor_query_read():
    m = sensor_query_mapping(
        entity_id="sensor.hum", attribute_name="humidity", capability_key="humidity",
        appliance_types=("SENSOR",), unit="%",
    )
    val = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState("sensor.hum", "55.5", {})}))
    assert val.value == 55.5


# --- composite_power_mapping (浴霸关 = 全功能关) ---

def test_composite_power_read_and_turn_off():
    m = composite_power_mapping(
        primary_entity_id="light.yuba",
        domain="switch",
        switch_roles=(("switch.heating", "heating"),
                      ("switch.blow", "blow"),
                      ("switch.ventilation", "ventilation"),
                      ("light.yuba", "light")),
        appliance_types=("YUBA",),
    )
    entities = {
        "heating": FakeState("switch.heating", "on"),
        "blow": FakeState("switch.blow", "off"),
        "ventilation": FakeState("switch.ventilation", "off"),
        "light": FakeState("light.yuba", "off"),
    }
    val = m.read(__import__("types").SimpleNamespace(entities=entities))
    assert val.value == "ON"
    ctx = __import__("types").SimpleNamespace(
        action=DuerAction("turnOff", "power"), payload={}, entities=entities,
    )
    calls = m.write(ctx)
    # All currently-on function entities get turn_off (only heating).
    assert [(c.target_entity_id, c.service) for c in calls] == [("switch.heating", "turn_off")]


# --- registry ---

def test_registry_resolve_profile_then_domain_default():
    reg = MappingRegistry()
    reg.register_domain_default("light", power_mapping(domain="light", entity_id="light.x", appliance_types=("LIGHT",)))
    reg.register_profile(DuerDeviceProfile(key="YUBA", appliance_types=("YUBA",)))
    reg.register_mapping("YUBA", mode_switches_mapping(
        modes=(("暖风", "h", "switch.h"),), appliance_types=("YUBA",)))
    assert len(reg.resolve_capabilities("YUBA", "light")) == 1   # profile first
    assert len(reg.resolve_capabilities("", "light")) == 1       # domain default


def test_registry_build_dueros_device():
    reg = MappingRegistry()
    reg.register_domain_default("light", power_mapping(domain="light", entity_id="light.x", appliance_types=("LIGHT",)))
    dev = reg.build_dueros_device(
        device_id="dueros-light", friendly_name="灯", profile_key="", primary_entity_id="light.x",
        domain="light", enabled_capability_keys=("power",),
    )
    assert dev is not None
    assert dev.device_id == "dueros-light"
    assert dev.actions() == ["turnOn", "turnOff"]
    # Unknown/profile-less device with no default mapping -> None.
    assert reg.build_dueros_device(
        device_id="x", friendly_name="x", profile_key="", primary_entity_id="sensor.y",
        domain="sensor", enabled_capability_keys=(),) is None
