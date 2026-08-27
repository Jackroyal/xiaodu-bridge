"""Pure-logic tests for the capability model primitives (no HA runtime).

Covers the helpers consumed by the DuerOS semantic model (``dueros/defaults.py``
and ``dueros/enhanced.py``): ``derive_capabilities``, ``classify_device``,
``_is_auxiliary``, and the YUBA / socket control-entity filters.
"""

from tests._dueros_loader import load_devices

devices_mod = load_devices()

derive_capabilities = devices_mod.derive_capabilities
CAP_POWER = devices_mod.CAP_POWER
CAP_BRIGHTNESS = devices_mod.CAP_BRIGHTNESS
CAP_COLOR_TEMPERATURE = devices_mod.CAP_COLOR_TEMPERATURE
CAP_COLOR = devices_mod.CAP_COLOR
CAP_VOLUME = devices_mod.CAP_VOLUME
CAP_CHANNEL = devices_mod.CAP_CHANNEL
CAP_MUTE = devices_mod.CAP_MUTE
CAP_FAN_SPEED = devices_mod.CAP_FAN_SPEED
CAP_TARGET_TEMPERATURE = devices_mod.CAP_TARGET_TEMPERATURE
CAP_TARGET_HUMIDITY = devices_mod.CAP_TARGET_HUMIDITY
CAP_MODE = devices_mod.CAP_MODE
CAP_PERCENTAGE = devices_mod.CAP_PERCENTAGE
CAP_SUCTION = devices_mod.CAP_SUCTION
CAP_TEMPERATURE = devices_mod.CAP_TEMPERATURE
CAP_HUMIDITY = devices_mod.CAP_HUMIDITY
CAP_PAUSE = devices_mod.CAP_PAUSE


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _light(entity_id="light.x", attrs=None):
    return FakeState(entity_id, "on", attrs or {})


def _fake_yuba_states():
    return [
        FakeState(
            "light.yuba_light",
            "on",
            {
                "friendly_name": "米家智能浴霸N1 灯",
                "brightness": 128,
                "supported_color_modes": ["brightness"],
            },
        ),
        FakeState("switch.yuba_heating", "off", {"friendly_name": "米家智能浴霸N1 浴霸风暖 暖风"}),
        FakeState("switch.yuba_blow", "off", {"friendly_name": "米家智能浴霸N1 浴霸风暖 吹风"}),
        FakeState("switch.yuba_vent", "off", {"friendly_name": "米家智能浴霸N1 浴霸风暖 换气"}),
        FakeState("switch.yuba_night_light", "off", {"friendly_name": "米家智能浴霸N1 灯 智能夜灯开关"}),
        FakeState("number.yuba_target_temp", "28", {"friendly_name": "米家智能浴霸N1 浴霸风暖 设定温度"}),
        FakeState("sensor.yuba_temp", "26", {"friendly_name": "米家智能浴霸N1 环境参数 温度", "unit_of_measurement": "°C"}),
    ]


# --- derive_capabilities -----------------------------------------------------

def test_derive_capabilities_full_light():
    caps = derive_capabilities(
        _light(attrs={"supported_color_modes": ["brightness", "color_temp", "hs"]})
    )
    assert caps == {CAP_POWER, CAP_BRIGHTNESS, CAP_COLOR_TEMPERATURE, CAP_COLOR}


def test_derive_capabilities_plain_light_only_power():
    assert derive_capabilities(_light()) == {CAP_POWER}


def test_derive_capabilities_switch_only_power():
    assert derive_capabilities(FakeState("switch.plug", "on")) == {CAP_POWER}


def test_derive_capabilities_sensor_readonly_only():
    assert derive_capabilities(
        FakeState("sensor.temp", "23", {"unit_of_measurement": "°C"})
    ) == {CAP_TEMPERATURE}


def test_derive_capabilities_color_temp_via_attributes():
    caps = derive_capabilities(
        _light(attrs={"color_temp_kelvin": 4000, "hs_color": [30, 80]})
    )
    assert {CAP_COLOR_TEMPERATURE, CAP_COLOR} <= caps


def test_derive_capabilities_light_without_explicit_brightness_mode():
    caps = derive_capabilities(
        _light(attrs={"supported_color_modes": ["color_temp", "hs"]})
    )
    assert CAP_BRIGHTNESS in caps
    assert CAP_COLOR_TEMPERATURE in caps
    assert CAP_COLOR in caps


def test_derive_capabilities_media_player():
    caps = derive_capabilities(
        FakeState(
            "media_player.tv",
            "on",
            {"volume_level": 0.3, "is_volume_muted": False, "source_list": ["HDMI1", "HDMI2"]},
        )
    )
    assert caps == {CAP_POWER, CAP_VOLUME, CAP_MUTE, CAP_CHANNEL}


def test_derive_capabilities_fan_speed():
    assert CAP_FAN_SPEED in derive_capabilities(
        FakeState("fan.x", "on", {"percentage": 50})
    )


def test_derive_capabilities_climate():
    caps = derive_capabilities(
        FakeState("climate.ac", "heat", {"temperature": 26, "hvac_modes": ["heat", "cool"]})
    )
    assert caps == {CAP_POWER, CAP_TARGET_TEMPERATURE, CAP_MODE}


def test_derive_capabilities_cover_percentage_reserved():
    assert CAP_PERCENTAGE in derive_capabilities(
        FakeState("cover.curtain", "open", {"current_position": 50})
    )


def test_derive_capabilities_humidifier():
    caps = derive_capabilities(
        FakeState("humidifier.h", "on", {"humidity": 50, "available_modes": ["auto"]})
    )
    assert caps == {CAP_POWER, CAP_TARGET_HUMIDITY, CAP_MODE}


def test_derive_capabilities_vacuum_suction():
    assert CAP_SUCTION in derive_capabilities(
        FakeState("vacuum.v", "cleaning", {"fan_speed_list": ["quiet", "strong"]})
    )


def test_derive_capabilities_sensor_readonly():
    temp = derive_capabilities(
        FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    )
    humidity = derive_capabilities(
        FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    )
    assert temp == {CAP_TEMPERATURE}
    assert humidity == {CAP_HUMIDITY}


def test_derive_capabilities_fahrenheit_sensor_is_temperature():
    caps = derive_capabilities(
        FakeState("sensor.t", "65.66", {"unit_of_measurement": "°F", "device_class": "temperature"})
    )
    assert caps == {CAP_TEMPERATURE}


def test_derive_capabilities_percent_sensor_without_class_not_humidity():
    assert derive_capabilities(
        FakeState("sensor.saturability", "65", {"unit_of_measurement": "%"})
    ) == set()


def test_derive_capabilities_cover_includes_pause():
    caps = derive_capabilities(FakeState("cover.curtain", "closed"))
    assert CAP_PAUSE in caps
    assert CAP_POWER in caps


def test_derive_capabilities_vacuum_includes_continue():
    state = FakeState("vacuum.robot", "docked", {"friendly_name": "扫地机器人", "fan_speed_list": ["安静", "标准", "强力"]})
    caps = derive_capabilities(state)
    assert devices_mod.CAP_CONTINUE in caps
    assert devices_mod.CAP_POWER in caps
    assert devices_mod.CAP_SUCTION in caps


# --- classify_device ---------------------------------------------------------

def test_classify_device_clothes_rack_by_entity_id():
    assert (
        devices_mod.classify_device("dev-1", [FakeState("cover.micoe_airer", "closed")])
        == devices_mod.DEVICE_CLASS_CLOTHES_RACK
    )


def test_classify_device_clothes_rack_by_model_metadata():
    assert (
        devices_mod.classify_device(
            "dev-1",
            [FakeState("cover.c1", "closed")],
            metadata={"manufacturer": "四季沐歌", "model": "micoe.airer.hz001z"},
        )
        == devices_mod.DEVICE_CLASS_CLOTHES_RACK
    )


def test_classify_device_plain_curtain_is_auto():
    assert (
        devices_mod.classify_device(
            "dev-1",
            [FakeState("cover.curtain", "closed")],
            metadata={"manufacturer": "Aqara", "model": "curtain"},
        )
        == devices_mod.DEVICE_CLASS_AUTO
    )


def test_classify_device_yuba_by_model():
    metadata = {"model": "xiaomi.bhf_light.na1"}
    assert (
        devices_mod.classify_device("yuba-dev", _fake_yuba_states(), metadata)
        == devices_mod.DEVICE_CLASS_YUBA
    )


def test_classify_device_socket_by_model():
    metadata = {"model": "chuangmi.plug.212a01"}
    states = [
        FakeState("switch.plug_on", "on", {"friendly_name": "米家智能插座2 蓝牙网关版 开关"}),
        FakeState("switch.plug_task", "off", {"friendly_name": "米家智能插座2 蓝牙网关版 任务开关"}),
    ]
    assert (
        devices_mod.classify_device("plug-dev", states, metadata)
        == devices_mod.DEVICE_CLASS_SOCKET
    )


# --- entity filters (used by dueros/defaults.py) -----------------------------

def test_yuba_control_entity_keeps_master_light_only():
    for state in _fake_yuba_states():
        assert devices_mod._yuba_control_entity(state) == (
            state.domain == "light" and "indicator" not in state.entity_id.lower()
        )


def test_yuba_control_entity_filters_indicator_light():
    assert not devices_mod._yuba_control_entity(
        FakeState("light.yuba_indicator_light", "on")
    )
    assert devices_mod._yuba_control_entity(
        FakeState("light.yuba_light", "on")
    )


def test_socket_control_entity_keeps_main_power_switch():
    assert devices_mod._socket_control_entity(
        FakeState("switch.plug_0_on_p_1", "on")
    )
    assert not devices_mod._socket_control_entity(
        FakeState("switch.plug_task", "off")
    )


def test_is_auxiliary_entity_id_markers():
    assert devices_mod._is_auxiliary(FakeState("switch.fan_child_lock", "off"))
    assert devices_mod._is_auxiliary(FakeState("light.dmaker_indicator_light", "on"))
    assert not devices_mod._is_auxiliary(FakeState("light.bedroom", "on"))


def test_is_auxiliary_friendly_name_keywords():
    assert devices_mod._is_auxiliary(
        FakeState("switch.fan_alarm", "off", {"friendly_name": "风扇 提示音"})
    )
    assert not devices_mod._is_auxiliary(
        FakeState("fan.fan", "on", {"friendly_name": "风扇"})
    )
