"""Pure-logic tests for the YUBA device profile (build + capability mappings)."""

from tests._dueros_loader import load_semantic_model

registry_mod = load_semantic_model()

from xiaodu.dueros.model import DuerAction, DuerDeviceProfile, DeviceBuildContext, make_device_id
from xiaodu.dueros.registry import MappingRegistry
from xiaodu.dueros.profiles import YUBA_PROFILE, build_yuba, match_role, register_default_profiles


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _yuba_states():
    return [
        FakeState("light.yuba", "on", {"friendly_name": "浴室浴霸"}),
        FakeState("switch.heating", "on", {"friendly_name": "取暖"}),
        FakeState("switch.blow", "off", {"friendly_name": "吹风"}),
        FakeState("switch.ventilation", "off", {"friendly_name": "换气"}),
        FakeState("select.warmth_level", "select", {"friendly_name": "热度档位", "option": "暖风"}),
        FakeState("select.fan_speed", "select", {"friendly_name": "风速", "option": "强劲"}),
        FakeState("number.target_temperature", "30", {"friendly_name": "设定温度"}),
    ]


def _ctx(states=None):
    return DeviceBuildContext(
        hass=None,
        ha_device_id="ha-device-1",
        device_name="浴室浴霸",
        profile_key="YUBA",
        domain="light",
        states=states or _yuba_states(),
    )


def test_build_yuba_creates_one_device_with_capabilities():
    devs = build_yuba(_ctx())
    assert len(devs) == 1
    dev = devs[0]
    assert dev.profile_key == "YUBA"
    assert dev.appliance_types == ("YUBA",)
    # The light is no longer claimed by the YUBA appliance: it surfaces as a
    # separate LIGHT device via the leftover path.
    assert dev.primary_entity_id == "switch.heating"
    keys = {c.key for c in dev.capabilities}
    # power / mode / warmthLevel / fanSpeed / targetTemperature all present.
    assert {"power", "mode", "warmthLevel", "fanSpeed", "targetTemperature"} <= keys
    # Actions aggregated across capabilities.
    actions = set(dev.actions())
    assert {"turnOn", "turnOff", "setMode", "unSetMode", "setGear", "setFanSpeed", "setTemperature"} <= actions


def test_yuba_power_read_on_when_any_function_on():
    dev = build_yuba(_ctx())[0]
    power = next(c for c in dev.capabilities if c.key == "power")
    # heating is on -> power ON
    ctx = _ctx()
    entities = {r: ctx.find_state(e) for r, e in [("heating","switch.heating"),("blow","switch.blow"),("ventilation","switch.ventilation"),("light","light.yuba")]}
    val = power.read(__import__("types").SimpleNamespace(entities=entities))
    assert val.name == "turnOnState" and val.value == "ON"


def test_yuba_mode_read_current_function():
    dev = build_yuba(_ctx())[0]
    mode = next(c for c in dev.capabilities if c.key == "mode")
    ctx = _ctx()
    entities = {"heating": ctx.find_state("switch.heating"), "blow": ctx.find_state("switch.blow"),
                "ventilation": ctx.find_state("switch.ventilation"), "light": ctx.find_state("light.yuba")}
    val = mode.read(__import__("types").SimpleNamespace(entities=entities))
    # heating and light both on; first in mode order wins -> 暖风
    assert val.value == "暖风"


def test_yuba_set_mode_writes_target_function():
    dev = build_yuba(_ctx())[0]
    mode = next(c for c in dev.capabilities if c.key == "mode")
    ctx = _ctx()
    entities = {"heating": ctx.find_state("switch.heating"), "blow": ctx.find_state("switch.blow"),
                "ventilation": ctx.find_state("switch.ventilation"), "light": ctx.find_state("light.yuba")}
    write_ctx = __import__("types").SimpleNamespace(
        action=DuerAction("setMode", "mode", "mode"), payload={"mode": {"value": "吹风"}}, entities=entities)
    calls = mode.write(write_ctx)
    assert [(c.target_entity_id, c.service) for c in calls] == [("switch.blow", "turn_on")]


def test_yuba_set_gear_and_temperature():
    dev = build_yuba(_ctx())[0]
    gear = next(c for c in dev.capabilities if c.key == "warmthLevel")
    ctx = _ctx()
    gear_ctx = __import__("types").SimpleNamespace(
        action=DuerAction("setGear", "warmthLevel", "warmthLevel"),
        payload={"warmthLevel": {"value": "强暖"}}, entities={"value": ctx.find_state("select.warmth_level")})
    gcalls = gear.write(gear_ctx)
    assert gcalls[0].data == {"option": "强暖"}

    temp = next(c for c in dev.capabilities if c.key == "targetTemperature")
    tctx = __import__("types").SimpleNamespace(
        action=DuerAction("setTemperature", "targetTemperature", "temperature"),
        payload={"temperature": {"value": 32}}, entities={"value": ctx.find_state("number.target_temperature")})
    tcalls = temp.write(tctx)
    assert tcalls[0].domain == "number"
    assert tcalls[0].data == {"value": 32}


def test_yuba_off_turns_all_functions_off():
    dev = build_yuba(_ctx())[0]
    power = next(c for c in dev.capabilities if c.key == "power")
    ctx = _ctx()
    entities = {"heating": ctx.find_state("switch.heating"), "blow": ctx.find_state("switch.blow"),
                "ventilation": ctx.find_state("switch.ventilation"), "light": ctx.find_state("light.yuba")}
    off_ctx = __import__("types").SimpleNamespace(
        action=DuerAction("turnOff", "power"), payload={}, entities=entities)
    calls = power.write(off_ctx)
    # heating is on; the light is no longer part of the YUBA power group.
    assert [(c.target_entity_id, c.service) for c in calls] == [
        ("switch.heating", "turn_off")]


def test_match_role_suggestion_only():
    assert match_role(FakeState("switch.heating", "on"), "heating")
    assert match_role(FakeState("number.target_temperature", "30"), "target_temperature")
    assert not match_role(FakeState("sensor.temp", "30"), "target_temperature")


def test_register_default_profiles_and_build_via_registry():
    reg = MappingRegistry()
    register_default_profiles(reg)
    assert reg.get_profile("YUBA") is not None
    dev = reg.build_device(_ctx())
    assert dev is not None and dev.profile_key == "YUBA"
    assert dev.device_id == make_device_id("YUBA", "ha-device-1")


def test_build_yuba_leaves_light_unclaimed():
    dev = build_yuba(_ctx())[0]
    claimed = {
        b.entity_id
        for cap in dev.capabilities
        for b in cap.bindings
    }
    assert "light.yuba" not in claimed
    assert "switch.heating" in claimed
    # YUBA actions no longer carry light-specific vocabulary.
    assert "setBrightnessPercentage" not in set(dev.actions())
