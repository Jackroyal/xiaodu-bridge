"""Pure-logic tests for the long-term semantic model (no HA runtime).

Covers ``dueros.model`` (DuerDevice / CapabilityMapping / AttributeValue),
``dueros.composers`` (power / mode_switches / select / target_temperature /
percentage / sensor_query / composite_power).
"""

from tests._dueros_loader import load_semantic_model

load_semantic_model()
from xiaodu.dueros.model import (
    AttributeValue,
    CapabilityMapping,
    DuerAction,
    DuerAttribute,
    DuerCapability,
    DuerDevice,
    EntityBinding,
    ServiceCall,
    make_attribute,
    make_device_id,
)
from xiaodu.dueros.composers import (
    composite_power_mapping,
    enum_value_mapping,
    mode_switches_mapping,
    pause_mapping,
    percentage_mapping,
    power_mapping,
    select_mapping,
    sensor_enum_mapping,
    sensor_query_mapping,
    target_temperature_mapping,
    time_left_mapping,
)
from xiaodu.dueros.constants import (
    ATTR_FAN_SPEED,
    ATTR_MODE,
    ATTR_SUCTION,
    ATTR_TARGET_TEMPERATURE,
    ATTR_TURN_ON_STATE,
    ATTR_WARMTH_LEVEL,
    ATTR_WATER_LEVEL,
    ATTR_WORK_STATE,
    ATTR_PERCENTAGE,
    SUCTION_VALUES,
    WARMTH_LEVEL_VALUES,
    WASHING_MODE_VALUES,
    WATER_LEVEL_VALUES,
    WORK_STATE_VALUES,
    GEAR_VALUES,
)
from xiaodu.dueros.profiles import (
    SUCTION_ALIASES,
    WARMTH_LEVEL_ALIASES,
    WORK_STATE_ALIASES,
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


# --- select_mapping (generic select: option label is the DuerOS value) ---

def test_select_mapping_read_write():
    m = select_mapping(
        entity_id="select.fan_speed",
        attribute_name=ATTR_FAN_SPEED,
        capability_key="fanSpeed",
        appliance_types=("FAN",),
        set_action="setFanSpeed",
    )
    ctxr = __import__("types").SimpleNamespace(
        entities={"value": FakeState("select.fan_speed", "select", {"option": "低档"})}
    )
    val = m.read(ctxr)
    assert val.name == ATTR_FAN_SPEED and val.value == "低档"
    ctxw = __import__("types").SimpleNamespace(
        action=DuerAction("setFanSpeed", "fanSpeed", "fanSpeed"),
        payload={"fanSpeed": {"value": "低档"}},
    )
    calls = m.write(ctxw)
    assert calls[0].domain == "select"
    assert calls[0].data == {"option": "低档"}


# --- enum_value_mapping (contract enum <-> device vocabulary) ---

def test_enum_value_mapping_gear_resolves_position_and_reads_enum():
    m = enum_value_mapping(
        entity_id="select.warmth_level",
        attribute_name=ATTR_WARMTH_LEVEL,
        capability_key="warmthLevel",
        appliance_types=("YUBA",),
        tokens=WARMTH_LEVEL_VALUES,
        write_tokens=GEAR_VALUES,
        set_action="setGear",
        payload_key="gear",
        ordered=True,
        aliases=WARMTH_LEVEL_ALIASES,
    )
    state = FakeState(
        "select.warmth_level", "select",
        {"option": "强暖", "options": ["弱暖", "强暖", "恒温"]},
    )

    def write(payload):
        return m.write(__import__("types").SimpleNamespace(
            action=DuerAction("setGear", "warmthLevel", "gear"),
            payload=payload,
            entities={"value": state},
        ))

    assert write({"gear": {"value": "HIGH", "scale": "挡"}})[0].data == {"option": "强暖"}
    assert write({"gear": {"value": "LOW", "scale": "挡"}})[0].data == {"option": "弱暖"}
    assert write({"gear": {"value": "MIDDLE", "scale": "挡"}})[0].data == {"option": "恒温"}
    assert write({"warmthLevel": {"value": "HIGH"}}) is None
    assert m.read(__import__("types").SimpleNamespace(
        entities={"value": state})).value == "HIGH"
    # An unknown label is omitted rather than reported outside legalValue.
    assert m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState(
            "select.warmth_level", "select", {"option": "舒适", "options": ["舒适"]})}
    )) is None


def test_enum_value_mapping_suction_matches_contract_tokens():
    m = enum_value_mapping(
        entity_id="vacuum.robot",
        attribute_name=ATTR_SUCTION,
        capability_key="suction",
        appliance_types=("SWEEPING_ROBOT",),
        tokens=SUCTION_VALUES,
        set_action="setSuction",
        domain="vacuum",
        service="set_fan_speed",
        data_key="fan_speed",
        options_attr="fan_speed_list",
        read_attr="fan_speed",
        ordered=True,
        aliases=SUCTION_ALIASES,
    )
    attributes = {
        "fan_speed": "Quiet",
        "fan_speed_list": ["Quiet", "Balanced", "Turbo", "Max"],
    }
    state = FakeState("vacuum.robot", "cleaning", attributes)
    assert m.read(__import__("types").SimpleNamespace(entities={"value": state})).value == "STANDARD"
    calls = m.write(__import__("types").SimpleNamespace(
        action=DuerAction("setSuction", "suction", "suction"),
        payload={"suction": {"value": "STRONG"}},
        entities={"value": state},
    ))
    assert calls[0].data == {"fan_speed": "Max"}


def test_sensor_enum_mapping_maps_states_and_omits_unknown():
    m = sensor_enum_mapping(
        entity_id="sensor.run_state",
        attribute_name=ATTR_WORK_STATE,
        capability_key="workState",
        appliance_types=("WASHING_MACHINE",),
        tokens=WORK_STATE_VALUES,
        aliases=WORK_STATE_ALIASES,
    )

    def read(state_value):
        return m.read(__import__("types").SimpleNamespace(
            entities={"value": FakeState("sensor.run_state", state_value)}))

    assert read("运行中").value == "WORKING"
    assert read("done").value == "DONE"
    assert read("神秘状态") is None


def test_enum_value_mapping_ordered_fallback_uses_positions():
    # No alias matches a device that names its levels 一档..四档; an ordered
    # vocabulary still resolves the token's position onto those steps.
    m = enum_value_mapping(
        entity_id="select.level",
        attribute_name=ATTR_WATER_LEVEL,
        capability_key="waterLevel",
        appliance_types=("WASHING_MACHINE",),
        tokens=WATER_LEVEL_VALUES,
        set_action="setWaterLevel",
        ordered=True,
    )
    options = ["一档", "二档", "三档", "四档"]
    state = FakeState("select.level", "select", {"option": "三档", "options": options})

    def write(token):
        return m.write(__import__("types").SimpleNamespace(
            action=DuerAction("setWaterLevel", "waterLevel", "waterLevel"),
            payload={"waterLevel": {"value": token}},
            entities={"value": state},
        ))

    assert write("LOW")[0].data == {"option": "一档"}
    assert write("HIGH")[0].data == {"option": "四档"}
    assert write("MEDIUM")[0].data == {"option": "三档"}
    # ...and positions map back to the enum.
    for option, token in (("一档", "LOW"), ("三档", "MEDIUM"), ("四档", "HIGH")):
        value = m.read(__import__("types").SimpleNamespace(
            entities={"value": FakeState(
                "select.level", "select", {"option": option, "options": options})}
        ))
        assert value.value == token


def test_enum_value_mapping_exact_contract_token_passes_through():
    # An integration whose own values already are the contract tokens is driven
    # verbatim — no alias or position guessing involved.
    m = enum_value_mapping(
        entity_id="vacuum.robot",
        attribute_name=ATTR_SUCTION,
        capability_key="suction",
        appliance_types=("SWEEPING_ROBOT",),
        tokens=SUCTION_VALUES,
        set_action="setSuction",
        domain="vacuum",
        service="set_fan_speed",
        data_key="fan_speed",
        options_attr="fan_speed_list",
        read_attr="fan_speed",
    )
    state = FakeState("vacuum.robot", "cleaning", {
        "fan_speed": "STRONG", "fan_speed_list": ["STANDARD", "STRONG"],
    })
    assert m.read(__import__("types").SimpleNamespace(entities={"value": state})).value == "STRONG"
    calls = m.write(__import__("types").SimpleNamespace(
        action=DuerAction("setSuction", "suction", "suction"),
        payload={"suction": {"value": "standard"}},  # case-insensitive match
        entities={"value": state},
    ))
    assert calls[0].data == {"fan_speed": "STANDARD"}


def test_enum_value_mapping_allow_custom_reports_vendor_modes():
    # attributes.md's mode allows a vendor ``customName``: a listed value the
    # alias table cannot name is still reported (with the entity's own
    # legalValue) and accepted verbatim on the way in.
    m = enum_value_mapping(
        entity_id="select.wash_mode",
        attribute_name=ATTR_MODE,
        capability_key="mode",
        appliance_types=("WASHING_MACHINE",),
        tokens=WASHING_MODE_VALUES,
        set_action="setMode",
        allow_custom=True,
        aliases={"FAST_WASH": ("快速",)},
    )
    options = ["快速洗", "单脱水"]
    value = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState(
            "select.wash_mode", "select", {"option": "快速洗", "options": options})}
    ))
    assert (value.value, value.legal) == ("FAST_WASH", "(STANDARD, DRY, WASH_DRY, FAST_WASH, DOWN_JACKET)")
    custom = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState(
            "select.wash_mode", "select", {"option": "单脱水", "options": options})}
    ))
    assert (custom.value, custom.legal) == ("单脱水", "(快速洗, 单脱水)")
    calls = m.write(__import__("types").SimpleNamespace(
        action=DuerAction("setMode", "mode", "mode"),
        payload={"mode": {"value": "单脱水"}},
        entities={"value": FakeState(
            "select.wash_mode", "select", {"option": "快速洗", "options": options})},
    ))
    assert calls[0].data == {"option": "单脱水"}


def test_sensor_enum_mapping_prefers_the_most_specific_alias():
    m = sensor_enum_mapping(
        entity_id="sensor.run_state",
        attribute_name=ATTR_WORK_STATE,
        capability_key="workState",
        appliance_types=("WASHING_MACHINE",),
        tokens=WORK_STATE_VALUES,
        aliases=WORK_STATE_ALIASES,
    )
    # "烘干" (WORKING) is a substring of "烘干完成" — the longer, more specific
    # alias (DONE) must win.
    value = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState("sensor.run_state", "烘干完成")}
    ))
    assert value.value == "DONE"


def test_select_reads_the_current_value_from_the_entity_state():
    # A real HA ``select`` exposes its current option as the entity *state* —
    # the ``option`` attribute does not exist on it, and reading only that
    # attribute made every select-backed capability report an empty value.
    m = enum_value_mapping(
        entity_id="select.warmth_level",
        attribute_name=ATTR_WARMTH_LEVEL,
        capability_key="warmthLevel",
        appliance_types=("YUBA",),
        tokens=WARMTH_LEVEL_VALUES,
        write_tokens=GEAR_VALUES,
        set_action="setGear",
        payload_key="gear",
        ordered=True,
        aliases=WARMTH_LEVEL_ALIASES,
    )
    options = ["弱暖(低热、暖风)", "强暖(高热、热风)", "恒温"]

    def read(option):
        # No ``option`` attribute: exactly what the Mi Home select looks like.
        return m.read(__import__("types").SimpleNamespace(
            entities={"value": FakeState("select.warmth_level", option, {"options": options})}
        ))

    assert read("恒温").value == "MIDDLE"
    assert read("弱暖(低热、暖风)").value == "LOW"
    assert read("强暖(高热、热风)").value == "HIGH"
    # An unavailable select must not be reported as a level at all.
    assert read("unavailable") is None

    fan = select_mapping(
        entity_id="select.fan_speed",
        attribute_name=ATTR_FAN_SPEED,
        capability_key="fanSpeed",
        appliance_types=("YUBA",),
        set_action="setFanSpeed",
        ordered_options=True,
    )
    value = fan.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState(
            "select.fan_speed", "高档", {"options": ["低档", "高档"]})}
    ))
    assert value.value == 10


def test_time_left_mapping_converts_to_seconds():
    m = time_left_mapping(entity_id="sensor.time_left", appliance_types=("WASHING_MACHINE",))
    attr = m.read(__import__("types").SimpleNamespace(
        entities={"value": FakeState(
            "sensor.time_left", "45", {"unit_of_measurement": "min"})}
    ))
    assert (attr.name, attr.value) == ("timeLeftInSeconds", 2700)
    assert m.capability.query_names == ("GetTimeLeftRequest",)


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
