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
        FakeState("vacuum.robot", "cleaning", {"friendly_name": "扫地机器人", "fan_speed": "2"}),
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
    # suction read
    suction = next(c for c in dev.capabilities if c.key == "suction")
    s = suction.read(types.SimpleNamespace(entities={"value": FakeState("vacuum.robot", "cleaning", {"fan_speed": "2"})}))
    assert s.value == "2"


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
    s = suction.write(types.SimpleNamespace(
        action=DuerAction("setSuction", "suction", "suction"),
        payload={"suction": {"value": "3"}}))
    assert (s[0].domain, s[0].service, s[0].data) == ("vacuum", "set_fan_speed", {"fan_speed": "3"})


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
    # mode read: uv on -> 杀菌
    mode = next(c for c in dev.capabilities if c.key == "mode")
    entities = {"dry": FakeState("switch.dry", "off"), "uv": FakeState("switch.uv", "on")}
    val = mode.read(types.SimpleNamespace(entities=entities))
    assert val.value == "杀菌"
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
        FakeState("select.wash_mode", "select", {"friendly_name": "洗涤程序", "option": "混合洗"}),
        FakeState("select.water_level", "select", {"friendly_name": "水位", "option": "高"}),
        FakeState("number.target_temperature", "40", {"friendly_name": "设定温度"}),
        FakeState("sensor.run_state", "运行中", {"friendly_name": "运行状态"}),
        FakeState("sensor.time_left", "30", {"friendly_name": "剩余时间"}),
    ]


def test_washing_machine_build():
    devs = build_washing_machine(_ctx(_washer_states()))
    assert len(devs) == 1
    dev = devs[0]
    assert dev.profile_key == "WASHING_MACHINE"
    keys = {c.key for c in dev.capabilities}
    assert {"power", "mode", "waterLevel", "targetTemperature", "workState", "timeLeft"} <= keys


def test_washing_machine_write():
    dev = build_washing_machine(_ctx(_washer_states()))[0]
    power = next(c for c in dev.capabilities if c.key == "power")
    # startUp action -> switch.turn_on
    up = power.write(types.SimpleNamespace(action=DuerAction("startUp", "power"), payload={}))
    assert (up[0].domain, up[0].service) == ("switch", "turn_on")
    # mode -> select_option
    mode = next(c for c in dev.capabilities if c.key == "mode")
    m = mode.write(types.SimpleNamespace(
        action=DuerAction("setMode", "mode", "mode"), payload={"mode": {"value": "快洗"}}))
    assert m[0].data == {"option": "快洗"}
    # waterLevel -> select_option
    wl = next(c for c in dev.capabilities if c.key == "waterLevel")
    w = wl.write(types.SimpleNamespace(
        action=DuerAction("setWaterLevel", "waterLevel", "waterLevel"),
        payload={"waterLevel": {"value": "低"}}))
    assert w[0].data == {"option": "低"}


# --- negative / guard ---

def test_profile_guards_return_empty():
    assert build_sweeping_robot(_ctx([FakeState("sensor.temp", "20")])) == []
    assert build_clothes_rack(_ctx([FakeState("switch.power", "on")])) == []
    assert build_washing_machine(_ctx([])) == []
