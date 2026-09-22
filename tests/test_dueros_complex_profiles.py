"""Pure-logic tests for the SWEEPING_ROBOT / CLOTHES_RACK / WASHING_MACHINE profiles."""

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


def test_clothes_rack_build_and_mode():
    devs = build_clothes_rack(_ctx(_rack_states()))
    assert len(devs) == 1
    dev = devs[0]
    assert dev.profile_key == "CLOTHES_RACK"
    keys = {c.key for c in dev.capabilities}
    assert {"power", "percentage", "pause", "mode"} <= keys
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
    # percentage read 60
    pct = next(c for c in dev.capabilities if c.key == "percentage")
    p = pct.read(types.SimpleNamespace(entities={"value": FakeState("cover.airer", "open", {"current_position": 60})}))
    assert p.value == 60


def test_clothes_rack_power_open_close():
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
