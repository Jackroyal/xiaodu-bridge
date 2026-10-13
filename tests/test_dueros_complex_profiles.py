"""Pure-logic tests for the SWEEPING_ROBOT / CLOTHES_RACK / WASHING_MACHINE profiles."""

import logging
import types

from tests._dueros_loader import load_semantic_model

registry_mod = load_semantic_model()

from xiaodu.dueros.model import DuerAction, DeviceBuildContext
from xiaodu.dueros.profiles import (
    build_clothes_rack,
    build_sweeping_robot,
    build_washing_machine,
)


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _ctx(states):
    return DeviceBuildContext(
        hass=None, ha_device_id="ha-device-1", device_name="测试设备",
        profile_key="", domain="", states=states,
    )


# --- SWEEPING_ROBOT ---

def _robot_states():
    return [
        FakeState(
            "vacuum.robot",
            "cleaning",
            {"friendly_name": "扫地机器人", "fan_speed": "Standard",
             "fan_speed_list": ["Silent", "Standard", "Strong", "Turbo"]},
        ),
        FakeState("sensor.battery", "85", {"friendly_name": "电量", "device_class": "battery"}),
    ]


def test_sweeping_robot_build_and_read():
    devs = build_sweeping_robot(_ctx(_robot_states()))
    assert len(devs) == 1
    dev = devs[0]
    assert dev.profile_key == "SWEEPING_ROBOT"
    keys = {c.key for c in dev.capabilities}
    assert {"power", "pause", "suction", "electricityCapacity"} <= keys
    # power read: state cleaning -> ON
    power = next(c for c in dev.capabilities if c.key == "power")
    val = power.read(types.SimpleNamespace(entities={"power": FakeState("vacuum.robot", "cleaning")}))
    assert val.value == "ON"
    # suction read: the contract's vocabulary (STANDARD/STRONG), not the
    # integration's own fan_speed token.
    suction = next(c for c in dev.capabilities if c.key == "suction")
    entities = {"value": FakeState(
        "vacuum.robot", "cleaning",
        {"fan_speed": "Turbo", "fan_speed_list": ["Silent", "Standard", "Strong", "Turbo"]})}
    assert suction.read(types.SimpleNamespace(entities=entities)).value == "STRONG"
    assert suction.capability.attributes[0].legal == "(STANDARD, STRONG)"


def test_sweeping_robot_write():
    dev = build_sweeping_robot(_ctx(_robot_states()))[0]
    power = next(c for c in dev.capabilities if c.key == "power")
    on = power.write(types.SimpleNamespace(
        action=DuerAction("turnOn", "power"), payload={}))
    assert on[0].service == "start"
    off = power.write(types.SimpleNamespace(
        action=DuerAction("turnOff", "power"), payload={}))
    assert off[0].service == "stop"
    suction = next(c for c in dev.capabilities if c.key == "suction")
    ctx = _ctx(_robot_states())
    entities = {"value": ctx.find_state("vacuum.robot")}

    def calls(payload):
        return suction.write(types.SimpleNamespace(
            action=DuerAction("setSuction", "suction", "suction"),
            payload=payload,
            entities=entities,
        ))

    # SetSuctionRequest sends STANDARD / STRONG (control-message.md); the raw
    # token is not a fan_speed value of the vacuum.
    assert calls({"suction": {"value": "STRONG"}})[0].data == {"fan_speed": "Strong"}
    assert calls({"suction": {"value": "STANDARD"}})[0].data == {"fan_speed": "Standard"}
    # A value outside the contract enum is answered as unsupported.
    assert calls({"suction": {"value": "3"}}) is None


# --- CLOTHES_RACK ---

def _rack_states():
    return [
        FakeState("cover.airer", "open", {"friendly_name": "阳台晾衣架", "current_position": 60}),
        FakeState("switch.dry", "off", {"friendly_name": "烘干"}),
        FakeState("switch.uv", "on", {"friendly_name": "杀菌"}),
    ]


def _rack_light_states():
    """A rack with a light entity and no dry/uv switches (minimal action set)."""
    return [
        FakeState("cover.airer", "closed", {"friendly_name": "阳台晾衣架"}),
        FakeState("light.airer_light", "off", {"friendly_name": "晾衣架 灯"}),
    ]


def test_clothes_rack_build_and_mode():
    devs = build_clothes_rack(_ctx(_rack_states()))
    assert len(devs) == 1
    dev = devs[0]
    assert dev.profile_key == "CLOTHES_RACK"
    keys = {c.key for c in dev.capabilities}
    assert {"power", "height", "pause", "mode"} <= keys
    # The old position capability is gone (the airer has no position attribute).
    assert "percentage" not in keys
    # mode read: uv on -> DISINFECT (DuerOS CLOTHES_RACK mode codes are
    # English, not the Chinese friendly-name labels).
    mode = next(c for c in dev.capabilities if c.key == "mode")
    entities = {"dry": FakeState("switch.dry", "off"), "uv": FakeState("switch.uv", "on")}
    val = mode.read(types.SimpleNamespace(entities=entities))
    assert val.value == "DISINFECT"
    # dry on -> DRYING (and the legalValue only covers present switches).
    entities = {"dry": FakeState("switch.dry", "on"), "uv": FakeState("switch.uv", "off")}
    val = mode.read(types.SimpleNamespace(entities=entities))
    assert val.value == "DRYING"


def test_clothes_rack_light_actions_and_services():
    dev = build_clothes_rack(_ctx(_rack_light_states()))[0]
    # power (灯) first, then the height actions, then pause.
    assert dev.actions() == [
        "turnOn", "turnOff", "incrementHeight", "decrementHeight", "pause",
    ]
    power = next(c for c in dev.capabilities if c.key == "power")
    assert ("light.airer_light", "power") in {
        (b.entity_id, b.role) for b in power.bindings
    }
    # turnOn / turnOff drive the light, not the cover.
    assert power.write(types.SimpleNamespace(
        action=DuerAction("turnOn", "power"), payload={}
    ))[0].target_entity_id == "light.airer_light"
    assert power.write(types.SimpleNamespace(
        action=DuerAction("turnOn", "power"), payload={}
    ))[0].service == "turn_on"
    assert power.write(types.SimpleNamespace(
        action=DuerAction("turnOff", "power"), payload={}
    ))[0].service == "turn_off"
    # Height raises/lowers the cover (open = 上升).
    height = next(c for c in dev.capabilities if c.key == "height")
    up = height.write(types.SimpleNamespace(
        action=DuerAction("incrementHeight", "height"), payload={}
    ))
    assert (up[0].domain, up[0].service) == ("cover", "open_cover")
    down = height.write(types.SimpleNamespace(
        action=DuerAction("decrementHeight", "height"), payload={}
    ))
    assert (down[0].domain, down[0].service) == ("cover", "close_cover")
    pause = next(c for c in dev.capabilities if c.key == "pause")
    stop = pause.write(types.SimpleNamespace(
        action=DuerAction("pause", "pause"), payload={}
    ))
    assert (stop[0].domain, stop[0].service) == ("cover", "stop_cover")


def test_clothes_rack_power_function_dispatch(caplog):
    dev = build_clothes_rack(_ctx(_rack_light_states()))[0]
    power = next(c for c in dev.capabilities if c.key == "power")

    def target(payload):
        return power.write(types.SimpleNamespace(
            action=DuerAction("turnOn", "power"), payload=payload
        ))[0].target_entity_id

    # No function field -> the mapping's default (the light).
    assert target({}) == "light.airer_light"
    # App channel: the undocumented ``function: "light"`` -> the light target.
    assert target({"function": "light"}) == "light.airer_light"
    # Unknown function value -> warn but still fall back to the light.
    with caplog.at_level(logging.WARNING, logger="xiaodu.dueros.composers"):
        assert target({"function": "bogus"}) == "light.airer_light"
    assert any("function" in r.message for r in caplog.records)


def test_clothes_rack_height_delta_degrades_to_full_travel(caplog):
    dev = build_clothes_rack(_ctx(_rack_light_states()))[0]
    height = next(c for c in dev.capabilities if c.key == "height")
    with caplog.at_level(logging.WARNING, logger="xiaodu.dueros.composers"):
        call = height.write(types.SimpleNamespace(
            action=DuerAction("incrementHeight", "height"),
            payload={"deltaValue": {"value": 0.5, "scale": "METER"}},
        ))
    # No position/travel attribute: the delta is ignored, a full raise is issued
    # (never answered as unsupported).
    assert (call[0].domain, call[0].service) == ("cover", "open_cover")
    assert any("deltaValue" in r.message for r in caplog.records)


def test_clothes_rack_power_open_close_without_light():
    # A rack without a light entity keeps the legacy cover open/close on power.
    dev = build_clothes_rack(_ctx(_rack_states()))[0]
    power = next(c for c in dev.capabilities if c.key == "power")
    assert power.write(types.SimpleNamespace(action=DuerAction("turnOn", "power"), payload={}))[0].service == "open_cover"
    assert power.write(types.SimpleNamespace(action=DuerAction("turnOff", "power"), payload={}))[0].service == "close_cover"


# --- WASHING_MACHINE ---

def _washer_states():
    return [
        FakeState("switch.power", "on", {"friendly_name": "洗衣机电源"}),
        FakeState("select.wash_mode", "select", {
            "friendly_name": "洗涤程序", "option": "快速洗",
            "options": ["标准洗", "快速洗", "洗烘", "羽绒服", "单脱水"],
        }),
        FakeState("select.water_level", "select", {
            "friendly_name": "水位", "option": "高", "options": ["低", "中", "高"],
        }),
        FakeState("number.target_temperature", "40", {"friendly_name": "设定温度"}),
        FakeState("sensor.run_state", "运行中", {"friendly_name": "运行状态"}),
        FakeState("sensor.time_left", "30", {
            "friendly_name": "剩余时间", "unit_of_measurement": "min",
        }),
    ]


def test_washing_machine_build():
    devs = build_washing_machine(_ctx(_washer_states()))
    assert len(devs) == 1
    dev = devs[0]
    assert dev.profile_key == "WASHING_MACHINE"
    keys = {c.key for c in dev.capabilities}
    assert {"power", "mode", "waterLevel", "targetTemperature", "workState", "timeLeft"} <= keys
    # workState / timeLeft report the contract's vocabulary and unit.
    state = _ctx(_washer_states())
    work = next(c for c in dev.capabilities if c.key == "workState")
    assert work.read(types.SimpleNamespace(
        entities={"value": state.find_state("sensor.run_state")})).value == "WORKING"
    left = next(c for c in dev.capabilities if c.key == "timeLeft")
    attr = left.read(types.SimpleNamespace(entities={"value": state.find_state("sensor.time_left")}))
    # GetTimeLeftResponse counts seconds, not the sensor's own minutes.
    assert (attr.name, attr.value) == ("timeLeftInSeconds", 1800)


def test_washing_machine_write():
    dev = build_washing_machine(_ctx(_washer_states()))[0]
    ctx = _ctx(_washer_states())
    power = next(c for c in dev.capabilities if c.key == "power")
    # startUp action -> switch.turn_on
    up = power.write(types.SimpleNamespace(action=DuerAction("startUp", "power"), payload={}))
    assert (up[0].domain, up[0].service) == ("switch", "turn_on")
    # mode: the contract names wash programs (模式表 WASHING_MACHINE); the
    # select's own labels are the integration's Chinese program names.
    mode = next(c for c in dev.capabilities if c.key == "mode")
    m = mode.write(types.SimpleNamespace(
        action=DuerAction("setMode", "mode", "mode"),
        payload={"mode": {"value": "FAST_WASH"}},
        entities={"value": ctx.find_state("select.wash_mode")},
    ))
    assert m[0].data == {"option": "快速洗"}
    # waterLevel: LOW / MEDIUM / HIGH against the select's ordered levels.
    wl = next(c for c in dev.capabilities if c.key == "waterLevel")
    w = wl.write(types.SimpleNamespace(
        action=DuerAction("setWaterLevel", "waterLevel", "waterLevel"),
        payload={"waterLevel": {"value": "LOW"}},
        entities={"value": ctx.find_state("select.water_level")},
    ))
    assert w[0].data == {"option": "低"}


# --- negative / guard ---

def test_profile_guards_return_empty():
    assert build_sweeping_robot(_ctx([FakeState("sensor.temp", "20")])) == []
    assert build_clothes_rack(_ctx([FakeState("switch.power", "on")])) == []
    assert build_washing_machine(_ctx([])) == []
