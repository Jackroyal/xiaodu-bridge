"""Pure-logic tests for the generic (fallback) DuerDevice builder."""

from tests._dueros_loader import load_semantic_model

load_semantic_model()
from xiaodu.dueros.defaults import build_default_devices
from xiaodu.dueros.model import DeviceBuildContext


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _ctx(states, ha_device_id="dev", config=None, name="设备"):
    return DeviceBuildContext(
        hass=None,
        ha_device_id=ha_device_id,
        device_name=name,
        states=list(states),
        config=config,
    )


def test_light_builds_light_appliance_with_caps():
    s = FakeState(
        "light.lamp",
        "on",
        {
            "friendly_name": "客厅灯",
            "brightness": 128,
            "supported_color_modes": ["brightness", "color_temp", "hs"],
            "hs_color": [30, 80],
            "color_temp_kelvin": 4000,
            "color_temp_min_kelvin": 1700,
            "color_temp_max_kelvin": 6500,
        },
    )
    devs = build_default_devices(_ctx([s]))
    assert len(devs) == 1
    d = devs[0]
    assert d.device_id == "light.lamp"
    assert d.profile_key == "light"
    assert d.appliance_types == ("LIGHT",)
    keys = {c.key for c in d.capabilities}
    assert {"power", "brightness", "colorTemperature", "color"} <= keys
    # serialize the actions it advertises
    assert "turnOn" in d.actions()
    assert "setBrightnessPercentage" in d.actions()
    assert "setColorTemperature" in d.actions()


def test_socket_switch_uses_socket_type():
    s = FakeState("switch.plug_on", "on", {"friendly_name": "插座 开关"})
    devs = build_default_devices(_ctx([s], ha_device_id="plug-dev"))
    assert len(devs) == 1
    assert devs[0].appliance_types == ("SOCKET",)
    assert devs[0].device_id == "switch.plug_on"


def test_sensor_pair_aggregates_into_single_sensor():
    t = FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h = FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    devs = build_default_devices(_ctx([t, h], ha_device_id="temp-dev"))
    assert len(devs) == 1
    d = devs[0]
    assert d.profile_key == "SENSOR"
    assert d.appliance_types == ("SENSOR",)
    # Read-only sensor: no *control* actions, but the query capabilities are
    # advertised as query actions so DuerOS can answer 温度/湿度 questions.
    assert set(d.actions()) == {"getHumidity", "getTemperatureReading"}
    assert {c.key for c in d.capabilities} <= {"temperature", "humidity"}
    caps = {c.key for c in d.capabilities}
    assert {"temperature", "humidity"} <= caps


def test_config_list_narrows_capabilities():
    s = FakeState(
        "light.lamp",
        "on",
        {"friendly_name": "灯", "brightness": 100, "supported_color_modes": ["brightness"]},
    )
    devs = build_default_devices(_ctx([s], config=["power", "brightness"]))
    d = devs[0]
    keys = {c.key for c in d.capabilities}
    assert "power" in keys and "brightness" in keys
    assert "colorTemperature" not in keys


def test_config_dict_excludes_unselected_entity():
    cover = FakeState("cover.airer", "closed", {"friendly_name": "晾衣杆"})
    light = FakeState("light.airer_light", "off", {"friendly_name": "晾衣杆 灯"})
    devs = build_default_devices(
        _ctx([cover, light], ha_device_id="rack-dev", config={"cover.airer": []})
    )
    # Only the cover entity is selected; the light is excluded.
    ids = {d.device_id for d in devs}
    assert "cover.airer" in ids
    assert "light.airer_light" not in ids


def test_readonly_empty_config_keeps_all_query_caps():
    t = FakeState("sensor.t", "20", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h = FakeState("sensor.h", "60", {"unit_of_measurement": "%", "device_class": "humidity"})
    devs = build_default_devices(_ctx([t, h], ha_device_id="temp-dev", config=[]))
    d = devs[0]
    keys = {c.key for c in d.capabilities}
    assert {"temperature", "humidity"} <= keys
