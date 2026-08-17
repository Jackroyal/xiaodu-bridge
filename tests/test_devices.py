"""Pure-logic tests for the capability-model device mapping (no HA runtime)."""

from tests._dueros_loader import load_devices

devices_mod = load_devices()

derive_capabilities = devices_mod.derive_capabilities
select_default_unit = devices_mod.select_default_unit
build_devices_from_entities = devices_mod.build_devices_from_entities
XiaoduDeviceMap = devices_mod.XiaoduDeviceMap
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
    # Sensors carry read-only capabilities (no power / control).
    assert derive_capabilities(
        FakeState("sensor.temp", "23", {"unit_of_measurement": "°C"})
    ) == {CAP_TEMPERATURE}


def test_derive_capabilities_color_temp_via_attributes():
    caps = derive_capabilities(
        _light(attrs={"color_temp_kelvin": 4000, "hs_color": [30, 80]})
    )
    assert {CAP_COLOR_TEMPERATURE, CAP_COLOR} <= caps


def test_select_default_unit_prefers_light_over_switch():
    primary = select_default_unit(
        [
            FakeState("switch.night", "off"),
            FakeState("light.main", "on"),
        ]
    )
    assert primary.entity_id == "light.main"


def test_select_default_unit_skips_unsupported_domain():
    assert select_default_unit([FakeState("person.me", "home")]) is None


def test_build_devices_groups_and_enables_all_caps_by_default():
    devices = build_devices_from_entities(
        [
            FakeState("light.a", "on", {"brightness": 100}),
            FakeState("switch.a", "off"),
        ],
        device_of=lambda eid: "device-1" if eid.startswith("light.") else "device-2",
        name_of=lambda key: {"device-1": "床头灯", "device-2": "插座"}.get(key),
        config=None,
    )
    assert len(devices) == 2
    by_key = {d.device_key: d for d in devices}
    assert by_key["device-1"].default_unit.entity_id == "light.a"
    assert by_key["device-1"].name == "床头灯"
    assert CAP_BRIGHTNESS in by_key["device-1"].default_unit.enabled
    assert by_key["device-2"].default_unit.entity_id == "switch.a"


def test_build_devices_config_gates_capabilities_and_power_is_implied():
    devices = build_devices_from_entities(
        [_light("light.a", {"color_temp_kelvin": 3000})],
        device_of=lambda eid: None,
        name_of=lambda key: None,
        config={"light.a": [CAP_COLOR_TEMPERATURE]},
    )
    assert len(devices) == 1
    device = devices[0]
    assert device.default_unit.enabled == {CAP_POWER, CAP_COLOR_TEMPERATURE}
    assert CAP_BRIGHTNESS not in device.default_unit.enabled


def test_build_devices_config_hides_unlisted_devices():
    devices = build_devices_from_entities(
        [_light("light.a"), _light("light.b")],
        device_of=lambda eid: None,
        name_of=lambda key: None,
        config={"light.a": []},
    )
    assert [d.default_unit.entity_id for d in devices] == ["light.a"]


def test_device_map_lookup_and_capability_check():
    devices = build_devices_from_entities(
        [_light("light.a", {"brightness": 50})],
        device_of=lambda eid: None,
        name_of=lambda key: None,
        config={"light.a": [CAP_BRIGHTNESS]},
    )
    device_map = XiaoduDeviceMap(devices)
    assert device_map.get("light.a") is not None
    assert device_map.get("light.missing") is None
    assert device_map.capability_enabled("light.a", CAP_POWER)
    assert device_map.capability_enabled("light.a", CAP_BRIGHTNESS)
    assert not device_map.capability_enabled("light.a", CAP_COLOR)


def test_derive_capabilities_light_without_explicit_brightness_mode():
    # Mi Home lights often list only ["color_temp", "hs"]; brightness is implied.
    caps = derive_capabilities(
        _light(attrs={"supported_color_modes": ["color_temp", "hs"]})
    )
    assert CAP_BRIGHTNESS in caps
    assert CAP_COLOR_TEMPERATURE in caps
    assert CAP_COLOR in caps


def test_area_name_populated_from_area_resolver():
    devices = build_devices_from_entities(
        [_light("light.x"), FakeState("switch.night", "off")],
        device_of=lambda eid: "dev-1",
        name_of=lambda key: None,
        config=None,
        area_name_of=lambda key: "卧室" if key == "dev-1" else None,
    )
    assert devices[0].area_name == "卧室"


def test_area_name_none_when_no_resolver():
    devices = build_devices_from_entities(
        [_light("light.x")],
        device_of=lambda eid: "dev-1",
        name_of=lambda key: None,
        config=None,
    )
    assert devices[0].area_name is None


def test_device_map_sync_areas_flag():
    devices = build_devices_from_entities(
        [_light("light.x")],
        device_of=lambda eid: "dev-1",
        name_of=lambda key: None,
        config=None,
    )
    assert XiaoduDeviceMap(devices, sync_areas=True).sync_areas is True
    assert XiaoduDeviceMap(devices).sync_areas is False


def test_derive_capabilities_media_player():
    caps = derive_capabilities(
        FakeState(
            "media_player.tv",
            "on",
            {
                "volume_level": 0.3,
                "is_volume_muted": False,
                "source_list": ["HDMI1", "HDMI2"],
            },
        )
    )
    assert caps == {CAP_POWER, CAP_VOLUME, CAP_MUTE, CAP_CHANNEL}


def test_derive_capabilities_fan_speed():
    assert CAP_FAN_SPEED in derive_capabilities(
        FakeState("fan.x", "on", {"percentage": 50})
    )


def test_derive_capabilities_climate():
    caps = derive_capabilities(
        FakeState(
            "climate.ac", "heat", {"temperature": 26, "hvac_modes": ["heat", "cool"]}
        )
    )
    assert caps == {CAP_POWER, CAP_TARGET_TEMPERATURE, CAP_MODE}


def test_derive_capabilities_cover_percentage_reserved():
    assert CAP_PERCENTAGE in derive_capabilities(
        FakeState("cover.curtain", "open", {"current_position": 50})
    )


def test_derive_capabilities_humidifier():
    caps = derive_capabilities(
        FakeState(
            "humidifier.h", "on", {"humidity": 50, "available_modes": ["auto"]}
        )
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


def test_empty_selection_readonly_device_exposes_all():
    devices = build_devices_from_entities(
        [
            FakeState(
                "sensor.t",
                "23.5",
                {"unit_of_measurement": "°C", "device_class": "temperature"},
            )
        ],
        device_of=lambda eid: "s1",
        name_of=lambda key: None,
        config={"s1": []},
    )
    assert devices[0].default_unit.enabled == {CAP_TEMPERATURE}


def test_empty_selection_controllable_exposes_all_capabilities():
    devices = build_devices_from_entities(
        [_light("light.x", {"brightness": 128})],
        device_of=lambda eid: "d1",
        name_of=lambda key: None,
        config={"d1": []},
    )
    assert devices[0].default_unit.enabled == {CAP_POWER, CAP_BRIGHTNESS}


def test_dict_config_empty_selection_keeps_implied_only():
    # A dict-form entry explicitly stores what the user picked; an empty list
    # means "no optional capability", so only the implied ones stay on.
    devices = build_devices_from_entities(
        [_light("light.x", {"brightness": 128})],
        device_of=lambda eid: "d1",
        name_of=lambda key: None,
        config={"d1": {"light.x": []}},
    )
    assert devices[0].default_unit.enabled == {CAP_POWER}


def test_implied_capabilities_structural_rules():
    assert devices_mod.implied_capabilities(domain="light") == (CAP_POWER,)
    assert devices_mod.implied_capabilities(domain="cover") == (CAP_POWER, CAP_PAUSE)
    yuba = devices_mod.implied_capabilities(
        domain="light",
        device_class=devices_mod.DEVICE_CLASS_YUBA,
        is_default=True,
    )
    assert yuba == (CAP_POWER, CAP_MODE, CAP_TARGET_TEMPERATURE)
    # Non-default units of a YUBA only keep power.
    assert devices_mod.implied_capabilities(
        domain="light",
        device_class=devices_mod.DEVICE_CLASS_YUBA,
        is_default=False,
    ) == (CAP_POWER,)


def test_select_default_unit_tv_prefers_media_player_over_is_on_switch():
    primary = select_default_unit(
        [
            FakeState("switch.tv_is_on", "on"),
            FakeState(
                "media_player.tv",
                "on",
                {"volume_level": 0.3, "source_list": ["HDMI1"]},
            ),
        ]
    )
    assert primary.entity_id == "media_player.tv"


def test_select_default_unit_fan_prefers_fan_over_is_on_switch():
    primary = select_default_unit(
        [
            FakeState("switch.fan_is_on", "on"),
            FakeState("fan.f1", "on", {"percentage": 50}),
        ]
    )
    assert primary.entity_id == "fan.f1"


def test_derive_capabilities_fahrenheit_sensor_is_temperature():
    caps = derive_capabilities(
        FakeState("sensor.t", "65.66", {"unit_of_measurement": "°F", "device_class": "temperature"})
    )
    assert caps == {CAP_TEMPERATURE}


def test_derive_capabilities_percent_sensor_without_class_not_humidity():
    # e.g. a "饱和度" sensor reports unit "%" but is not humidity.
    assert derive_capabilities(
        FakeState("sensor.saturability", "65", {"unit_of_measurement": "%"})
    ) == set()


def test_derive_capabilities_cover_includes_pause():
    caps = derive_capabilities(FakeState("cover.curtain", "closed"))
    assert CAP_PAUSE in caps
    assert CAP_POWER in caps


def test_classify_device_clothes_rack_by_entity_id():
    assert (
        devices_mod.classify_device(
            "dev-1",
            [FakeState("cover.micoe_airer", "closed")],
        )
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


def test_select_default_unit_prefers_richer_entity():
    # The cover (power + pause) wins over the plain light (power only).
    primary = select_default_unit(
        [
            FakeState("light.rack_light", "off"),
            FakeState("cover.rack", "closed"),
        ]
    )
    assert primary.entity_id == "cover.rack"


def test_build_devices_clothes_rack_prefers_cover_and_classifies():
    devices = build_devices_from_entities(
        [
            FakeState("light.rack_light", "off"),
            FakeState("cover.rack", "closed"),
            FakeState("sensor.rack_fault", "0"),
        ],
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config=None,
        metadata_of=lambda key: {
            "manufacturer": "四季沐歌",
            "model": "micoe.airer.hz001z",
        },
    )
    assert len(devices) == 1
    device = devices[0]
    assert device.device_class == devices_mod.DEVICE_CLASS_CLOTHES_RACK
    assert device.default_unit.entity_id == "cover.rack"
    assert CAP_PAUSE in device.default_unit.capabilities
    assert device.default_unit.enabled == {CAP_POWER, CAP_PAUSE}


def test_build_devices_clothes_rack_pause_selectable_in_config():
    devices = build_devices_from_entities(
        [
            FakeState("cover.rack", "closed"),
            FakeState("light.rack_light", "off"),
        ],
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={"rack-dev": [CAP_PAUSE]},
        metadata_of=lambda key: {"model": "micoe.airer.hz001z"},
    )
    assert devices[0].default_unit.enabled == {CAP_POWER, CAP_PAUSE}


def test_auxiliary_indicator_and_locked_switches_not_units():
    # The 星月风扇 device: the indicator LED and child-lock switch must never
    # be exposed. The fan is the default unit; the alarm switch stays a
    # selectable (but off-by-default) unit.
    devices = build_devices_from_entities(
        [
            FakeState("fan.dmaker_p9_s_2_fan", "on", {"percentage": 50}),
            FakeState("light.dmaker_p9_s_5_indicator_light", "off"),
            FakeState("switch.dmaker_p9_child_lock_p_3_1", "off"),
            FakeState("switch.dmaker_p9_alarm_p_2_7", "off"),
        ],
        device_of=lambda eid: "fan-dev",
        name_of=lambda key: "风扇",
        config=None,
    )
    assert len(devices) == 1
    device = devices[0]
    assert [u.entity_id for u in device.units] == [
        "fan.dmaker_p9_s_2_fan",
        "switch.dmaker_p9_alarm_p_2_7",
    ]
    assert device.default_unit.entity_id == "fan.dmaker_p9_s_2_fan"


def test_multi_unit_airer_legacy_list_enables_default_cover_only():
    devices = build_devices_from_entities(
        [
            FakeState("cover.rack", "closed", {"friendly_name": "晾衣杆  晾衣架"}),
            FakeState("light.rack_light", "off", {"friendly_name": "晾衣杆  灯"}),
        ],
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={"rack-dev": []},  # legacy list form
        metadata_of=lambda key: {"model": "micoe.airer.hz001z"},
    )
    assert len(devices) == 1
    device = devices[0]
    units = {u.entity_id: u for u in device.units}
    assert set(units) == {"cover.rack", "light.rack_light"}
    assert device.default_unit.entity_id == "cover.rack"
    assert units["cover.rack"].enabled == {CAP_POWER, CAP_PAUSE}
    assert units["light.rack_light"].enabled == frozenset()


def test_multi_unit_airer_dict_config_enables_selected_units():
    devices = build_devices_from_entities(
        [
            FakeState("cover.rack", "closed", {"friendly_name": "晾衣杆  晾衣架"}),
            FakeState("light.rack_light", "off", {"friendly_name": "晾衣杆  灯"}),
        ],
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={
            "rack-dev": {
                "cover.rack": [CAP_PAUSE],
                "light.rack_light": [],
            }
        },
        metadata_of=lambda key: {"model": "micoe.airer.hz001z"},
    )
    device = devices[0]
    units = {u.entity_id: u for u in device.units}
    assert units["cover.rack"].enabled == {CAP_POWER, CAP_PAUSE}
    assert units["light.rack_light"].enabled == {CAP_POWER}
    # light unit is a plain light: LIGHT type via domain, not clothes rack.
    assert units["light.rack_light"].device_class == devices_mod.DEVICE_CLASS_AUTO


def test_map_get_returns_unit_and_default_unit():
    devices = build_devices_from_entities(
        [
            FakeState("cover.rack", "closed"),
            FakeState("light.rack_light", "off"),
        ],
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config=None,
    )
    device_map = devices_mod.XiaoduDeviceMap(devices)
    unit = device_map.get("light.rack_light")
    assert unit is not None and unit.entity_id == "light.rack_light"
    assert device_map.get("missing.entity") is None
    assert device_map.default_unit("rack-dev").entity_id == "cover.rack"
    assert device_map.capability_enabled("cover.rack", CAP_PAUSE)


def test_multi_unit_readonly_aggregation_stays_single_unit():
    # A pure read-only device (温湿度计) still aggregates into one unit.
    devices = build_devices_from_entities(
        [
            FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"}),
            FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"}),
        ],
        device_of=lambda eid: "sensor-dev",
        name_of=lambda key: "温湿度计",
        config=None,
    )
    assert len(devices) == 1
    device = devices[0]
    assert len(device.units) == 1
    unit = device.units[0]
    assert unit.is_default
    assert unit.query_entities == {
        CAP_TEMPERATURE: "sensor.t",
        CAP_HUMIDITY: "sensor.h",
    }
    assert {CAP_TEMPERATURE, CAP_HUMIDITY} <= unit.capabilities


# --- v0.7.0: YUBA / SOCKET classification + auxiliary filtering -------------


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


def _yuba_config(config=None):
    return build_devices_from_entities(
        _fake_yuba_states(),
        device_of=lambda eid: "yuba-dev",
        name_of=lambda key: "米家智能浴霸N1",
        config=config
        or {"yuba-dev": {"light.yuba_light": ["brightness", "temperature"]}},
        metadata_of=lambda key: {"manufacturer": "小米", "model": "xiaomi.bhf_light.na1"},
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


def test_build_devices_yuba_single_master_with_controls():
    devices = _yuba_config()
    assert len(devices) == 1
    device = devices[0]
    assert device.device_class == devices_mod.DEVICE_CLASS_YUBA
    # A YUBA is ONE Xiaodu appliance: only the master light is a unit. The
    # function switches (取暖/吹风/换气) are modes, not separate devices.
    assert [u.entity_id for u in device.units] == ["light.yuba_light"]
    master = device.default_unit
    assert master is not None
    assert master.is_default
    assert master.device_class == devices_mod.DEVICE_CLASS_YUBA
    # Structural caps are enabled even when not stored in the config.
    assert devices_mod.CAP_POWER in master.enabled
    assert devices_mod.CAP_MODE in master.enabled
    assert devices_mod.CAP_TARGET_TEMPERATURE in master.enabled
    assert devices_mod.CAP_BRIGHTNESS in master.enabled
    assert devices_mod.CAP_TEMPERATURE in master.enabled
    # The YUBA master resolves every function to an entity.
    assert device.controls == {
        "light": "light.yuba_light",
        "heating": "switch.yuba_heating",
        "blow": "switch.yuba_blow",
        "ventilation": "switch.yuba_vent",
        "target_temperature": "number.yuba_target_temp",
    }


def test_build_devices_socket_keeps_only_main_switch():
    states = [
        FakeState("switch.plug_on", "on", {"friendly_name": "米家智能插座2 蓝牙网关版 开关"}),
        FakeState("switch.plug_power_enable", "off", {"friendly_name": "米家智能插座2 蓝牙网关版 通电状态"}),
        FakeState("switch.plug_task", "off", {"friendly_name": "米家智能插座2 蓝牙网关版 任务开关"}),
        FakeState("switch.plug_toggle", "off", {"friendly_name": "米家智能插座2 蓝牙网关版 翻转开关"}),
        FakeState("light.plug_indicator", "on", {"friendly_name": "米家智能插座2 蓝牙网关版 指示灯"}),
    ]
    device_list = build_devices_from_entities(
        states,
        device_of=lambda eid: "plug-dev",
        name_of=lambda key: "米家智能插座2 蓝牙网关版",
        config={"plug-dev": {"switch.plug_on": []}},
        metadata_of=lambda key: {"manufacturer": "小白", "model": "chuangmi.plug.212a01"},
    )
    assert len(device_list) == 1
    device = device_list[0]
    assert device.device_class == devices_mod.DEVICE_CLASS_SOCKET
    assert [u.entity_id for u in device.units] == ["switch.plug_on"]
    assert device.default_unit.device_class == devices_mod.DEVICE_CLASS_SOCKET


def test_is_on_auxiliary_switch_not_a_unit():
    # Mi Home creates a ``*_is_on`` switch next to TVs / heaters; it must not
    # become a separate selectable unit.
    states = [
        FakeState("media_player.tv", "idle", {"friendly_name": "电视"}),
        FakeState("switch.tv_is_on", "off", {"friendly_name": "电视 开/关机"}),
    ]
    device_list = build_devices_from_entities(
        states,
        device_of=lambda eid: "tv-dev",
        name_of=lambda key: "电视",
        config={"tv-dev": {"media_player.tv": ["volume", "mute", "channel"]}},
    )
    assert [u.entity_id for u in device_list[0].units] == ["media_player.tv"]


def test_friendly_name_auxiliary_keywords_not_units():
    states = [
        FakeState("fan.fan", "on", {"friendly_name": "风扇 风扇", "percentage": 50}),
        FakeState("switch.fan_alarm", "off", {"friendly_name": "风扇 风扇 提示音"}),
        FakeState("switch.fan_indicator", "off", {"friendly_name": "风扇 风扇 指示灯"}),
    ]
    device_list = build_devices_from_entities(
        states,
        device_of=lambda eid: "fan-dev",
        name_of=lambda key: "风扇",
        config={"fan-dev": {"fan.fan": []}},
    )
    assert [u.entity_id for u in device_list[0].units] == ["fan.fan"]


def test_derive_capabilities_vacuum_includes_continue():
    state = FakeState(
        "vacuum.robot",
        "docked",
        {"friendly_name": "扫地机器人", "fan_speed_list": ["安静", "标准", "强力"]},
    )
    caps = derive_capabilities(state)
    assert devices_mod.CAP_CONTINUE in caps
    assert devices_mod.CAP_POWER in caps
    assert devices_mod.CAP_SUCTION in caps
