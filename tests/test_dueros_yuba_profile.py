"""Pure-logic tests for the YUBA device profile (build + capability mappings)."""

from tests._dueros_loader import load_semantic_model

registry_mod = load_semantic_model()

from xiaodu.dueros.composers import select_mapping
from xiaodu.dueros.model import DuerAction, DuerDeviceProfile, DeviceBuildContext, make_device_id
from xiaodu.dueros.registry import ProfileRegistry
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
        FakeState("select.warmth_level", "select", {"friendly_name": "热度档位", "option": "强暖", "options": ["弱暖", "强暖", "恒温"]}),
        FakeState("select.fan_speed", "select", {"friendly_name": "风速", "option": "高档", "options": ["低档", "高档"]}),
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
    # heating and light both on; first in mode order wins -> HEAT
    assert val.value == "HEAT"


def test_yuba_set_mode_writes_target_function():
    dev = build_yuba(_ctx())[0]
    mode = next(c for c in dev.capabilities if c.key == "mode")
    ctx = _ctx()
    entities = {"heating": ctx.find_state("switch.heating"), "blow": ctx.find_state("switch.blow"),
                "ventilation": ctx.find_state("switch.ventilation"), "light": ctx.find_state("light.yuba")}
    write_ctx = __import__("types").SimpleNamespace(
        action=DuerAction("setMode", "mode", "mode"), payload={"mode": {"value": "FAN"}}, entities=entities)
    calls = mode.write(write_ctx)
    assert [(c.target_entity_id, c.service) for c in calls] == [("switch.blow", "turn_on")]


def test_yuba_set_gear_and_temperature():
    dev = build_yuba(_ctx())[0]
    gear = next(c for c in dev.capabilities if c.key == "warmthLevel")
    ctx = _ctx()
    state = ctx.find_state("select.warmth_level")

    def calls(payload):
        return gear.write(
            __import__("types").SimpleNamespace(
                action=DuerAction("setGear", "warmthLevel", "gear"),
                payload=payload,
                entities={"value": state},
            )
        )

    # SetGearRequest carries the value under ``gear`` (control-message.md):
    # HIGH -> 强暖, MIDDLE -> 恒温 (the vendor's middle option), MIN/LOW -> 弱暖.
    assert calls({"gear": {"value": "HIGH", "scale": "挡"}})[0].data == {"option": "强暖"}
    assert calls({"gear": {"value": "MIDDLE", "scale": "挡"}})[0].data == {"option": "恒温"}
    assert calls({"gear": {"value": "MIN", "scale": "挡"}})[0].data == {"option": "弱暖"}
    # Every position on the gear scale has a landing spot, so the mapping stays
    # monotone instead of mixing alias and positional rules.
    assert calls({"gear": {"value": "LOW", "scale": "挡"}})[0].data == {"option": "弱暖"}
    assert calls({"gear": {"value": "MIDDLE_LOW", "scale": "挡"}})[0].data == {"option": "弱暖"}
    assert calls({"gear": {"value": "MIDDLE_HIGH", "scale": "挡"}})[0].data == {"option": "强暖"}
    assert calls({"gear": {"value": "MAX", "scale": "挡"}})[0].data == {"option": "强暖"}
    # AUTO / RANDOM are not positions on the gear scale, and the payload this
    # used to read (``warmthLevel``) does not exist in the protocol at all.
    assert calls({"gear": {"value": "AUTO", "scale": "挡"}}) is None
    assert calls({"gear": {"value": "RANDOM", "scale": "挡"}}) is None
    assert calls({"warmthLevel": {"value": "强暖"}}) is None

    # The reported attribute is the contract enum, not the vendor's label.
    for option, token in (("弱暖", "LOW"), ("强暖", "HIGH"), ("恒温", "MIDDLE")):
        val = gear.read(__import__("types").SimpleNamespace(
            entities={"value": FakeState(
                "select.warmth_level", "select",
                {"option": option, "options": ["弱暖", "强暖", "恒温"]})}
        ))
        assert (val.name, val.value) == ("warmthLevel", token)

    temp = next(c for c in dev.capabilities if c.key == "targetTemperature")
    tctx = __import__("types").SimpleNamespace(
        hass=None,
        action=DuerAction("setTemperature", "targetTemperature", "temperature"),
        payload={"targetTemperature": {"value": 32, "scale": "CELSIUS"}},
        entities={"value": ctx.find_state("number.target_temperature")})
    tcalls = temp.write(tctx)
    assert tcalls[0].domain == "number"
    assert tcalls[0].data == {"value": 32}


def test_yuba_set_fan_speed_maps_level_onto_option_order():
    # DuerOS names a position ("max", or fanSpeed 1..10); the select's labels
    # come from the integration (低档 / 高档), so the raw token is never a valid
    # option — it has to be resolved against the entity's own option order.
    dev = build_yuba(_ctx())[0]
    fan = next(c for c in dev.capabilities if c.key == "fanSpeed")
    ctx = _ctx()
    state = ctx.find_state("select.fan_speed")

    def calls(payload):
        return fan.write(
            __import__("types").SimpleNamespace(
                hass=None,
                action=DuerAction("setFanSpeed", "fanSpeed", "fanSpeed"),
                payload=payload,
                entities={"value": state},
            )
        )

    assert calls({"fanSpeed": {"level": "max"}})[0].data == {"option": "高档"}
    assert calls({"fanSpeed": {"level": "min"}})[0].data == {"option": "低档"}
    assert calls({"fanSpeed": {"value": 10}})[0].data == {"option": "高档"}
    assert calls({"fanSpeed": {"value": 1}})[0].data == {"option": "低档"}
    # No automatic option on this entity.
    assert calls({"fanSpeed": {"level": "auto"}}) is None

    # The reading is the position on the contract's 1..10 scale — the same
    # scale the write path resolves against — not the option label (which is
    # not a fanSpeed value) and not the raw option index.
    def read(option):
        return fan.read(__import__("types").SimpleNamespace(
            entities={"value": FakeState(
                "select.fan_speed", "select",
                {"option": option, "options": ["低档", "高档"]})}
        ))

    assert read("高档").value == 10
    assert read("低档").value == 1
    assert fan.capability.attributes[0].legal == "[0, 10]"

    wide = select_mapping(
        entity_id="select.fan_speed", attribute_name="fanSpeed", capability_key="fanSpeed",
        appliance_types=("FAN",), set_action="setFanSpeed", ordered_options=True,
    )
    four = wide.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState(
            "select.fan_speed", "select",
            {"option": "中档", "options": ["低档", "中档", "高档", "超强"]})}
    ))
    # 4 steps: index 1 -> 1 + 1/3*9 = 4.0 on the 1..10 scale.
    assert four.value == 4.0


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
    reg = ProfileRegistry()
    register_default_profiles(reg)
    profile = reg.get_profile("YUBA")
    assert profile is not None
    built = profile.build(_ctx())
    assert built and built[0].profile_key == "YUBA"
    assert built[0].device_id == make_device_id("YUBA", "ha-device-1")


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
