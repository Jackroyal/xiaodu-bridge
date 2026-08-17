"""Pure-logic tests for the DuerOS protocol dispatcher (no HA runtime)."""

import asyncio
import time

from tests._dueros_loader import load_devices, load_dueros

handle_request, EntityFilter, protocol = load_dueros()
devices_mod = load_devices()
NAMESPACE_CONTROL = protocol.NAMESPACE_CONTROL
NAMESPACE_DISCOVERY = protocol.NAMESPACE_DISCOVERY
NAMESPACE_QUERY = protocol.NAMESPACE_QUERY


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


class FakeStates:
    def __init__(self, states):
        self._states = {s.entity_id: s for s in states}

    def async_all(self):
        return list(self._states.values())

    def get(self, entity_id):
        return self._states.get(entity_id)


class FakeServices:
    def __init__(self, hass):
        self._hass = hass

    async def async_call(self, domain, service, data, blocking=True):
        self._hass.service_calls.append((domain, service, data))


class FakeHass:
    def __init__(self, states):
        self.states = FakeStates(states)
        self.service_calls = []
        self.services = FakeServices(self)
        self.data = {}


class FakeTimedManager:
    """Minimal stand-in for ``timers.TimedServiceManager`` (HA-free)."""

    def __init__(self):
        self.scheduled = []

    async def schedule(self, domain, service, data, fire_at):
        self.scheduled.append((domain, service, data, fire_at))


def _header(namespace, name):
    return {
        "namespace": namespace,
        "name": name,
        "messageId": "msg-1",
        "payloadVersion": "1",
    }


def _request(namespace, name, payload):
    return {"header": _header(namespace, name), "payload": payload}


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def _device_map(hass, entity_ids=None, caps=None, name_of=None):
    """Build a XiaoduDeviceMap for the fake states.

    ``entity_ids`` restricts exposure (device keys == entity ids when no
    device grouping is simulated); ``caps`` limits the enabled capabilities;
    ``name_of`` provides device names (device registry lookup).
    """
    all_caps = [c for c in devices_mod.CAP_LABELS if c != devices_mod.CAP_POWER]
    config = None
    if entity_ids is not None:
        selected = list(all_caps if caps is None else caps)
        config = {eid: {eid: selected} for eid in entity_ids}
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: None,
        name_of=name_of or (lambda key: None),
        config=config,
    )
    return devices_mod.XiaoduDeviceMap(device_list)


def _hass():
    return FakeHass(
        [
            FakeState(
                "light.living",
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
            ),
            FakeState("light.bedroom", "off"),
            FakeState("switch.plug", "on"),
            FakeState("cover.curtain", "closed"),
            FakeState("sensor.temp", "23.5", {"unit_of_measurement": "°C"}),
            FakeState("sensor.power", "12.3", {"unit_of_measurement": "W"}),
            FakeState("person.me", "home"),
        ]
    )


def test_discovery_returns_filtered_appliances():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass(), ["light.bedroom", "light.living", "switch.plug"]),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    assert result["header"]["name"] == "DiscoverAppliancesResponse"
    ids = [a["applianceId"] for a in result["payload"]["discoveredAppliances"]]
    assert ids == ["light.bedroom", "light.living", "switch.plug"]
    living = next(a for a in result["payload"]["discoveredAppliances"] if a["applianceId"] == "light.living")
    assert living["applianceTypes"] == ["LIGHT"]
    assert "setColor" in living["actions"]
    assert "setColorTemperature" in living["actions"]
    assert any(a["name"] == "brightness" for a in living["attributes"])


def test_discovery_skips_unsupported_domains_and_sensors():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass()),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {}),
        )
    )
    ids = [a["applianceId"] for a in result["payload"]["discoveredAppliances"]]
    # person.* is unsupported; sensor.power is not temperature/humidity
    assert "person.me" not in ids
    assert "sensor.power" not in ids
    assert "sensor.temp" in ids


def test_control_turn_on_calls_service_and_confirms():
    hass = _hass()
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.bedroom", "light.living"]),
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "light.living"}},
            ),
        )
    )
    assert result["header"]["name"] == "TurnOnConfirmation"
    assert hass.service_calls == [("light", "turn_on", {"entity_id": "light.living"})]
    assert any(a["name"] == "turnOnState" for a in result["payload"]["attributes"])


def test_control_cover_maps_open_close():
    hass = _hass()
    run(
        handle_request(
            hass,
            _device_map(hass, ["cover.curtain"]),
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "cover.curtain"}},
            ),
        )
    )
    assert hass.service_calls == [("cover", "open_cover", {"entity_id": "cover.curtain"})]


def test_control_brightness_is_clamped():
    hass = _hass()
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.bedroom", "light.living"]),
            _request(
                NAMESPACE_CONTROL,
                "SetBrightnessPercentageRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.living"},
                    "brightness": {"value": 250},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetBrightnessPercentageConfirmation"
    assert hass.service_calls == [("light", "turn_on", {"entity_id": "light.living", "brightness_pct": 100.0})]


def test_control_set_color_maps_hs():
    hass = _hass()
    run(
        handle_request(
            hass,
            _device_map(hass, ["light.bedroom", "light.living"]),
            _request(
                NAMESPACE_CONTROL,
                "SetColorRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.living"},
                    "color": {"hue": 120, "saturation": 0.5},
                },
            ),
        )
    )
    assert hass.service_calls == [("light", "turn_on", {"entity_id": "light.living", "hs_color": [120.0, 50.0]})]


def test_control_rejects_filtered_entity():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass(), ["switch.plug"]),
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "light.living"}},
            ),
        )
    )
    assert result["header"]["name"] == "DriverInternalError"
    assert result["payload"] == {}


def test_control_offline_entity():
    hass = FakeHass([FakeState("light.offline", "unavailable")])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.offline"]),
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "light.offline"}},
            ),
        )
    )
    assert result["header"]["name"] == "TargetOfflineError"


def test_control_unsupported_action():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass(), ["switch.plug"]),
            _request(
                NAMESPACE_CONTROL,
                "SetColorRequest",
                {"accessToken": "t", "appliance": {"applianceId": "switch.plug"}},
            ),
        )
    )
    assert result["header"]["name"] == "NotSupportedInCurrentModeError"


def test_query_temperature():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass(), ["sensor.power", "sensor.temp"]),
            _request(
                NAMESPACE_QUERY,
                "GetTemperatureReadingRequest",
                {"accessToken": "t", "appliance": {"applianceId": "sensor.temp"}},
            ),
        )
    )
    assert result["header"]["name"] == "GetTemperatureReadingResponse"
    assert result["payload"]["temperatureReading"]["value"] == 23.5
    assert result["payload"]["temperatureReading"]["scale"] == "CELSIUS"


def test_query_generic_returns_attributes():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass(), ["light.living"]),
            _request(
                NAMESPACE_QUERY,
                "QueryRequest",
                {"accessToken": "t", "appliance": {"applianceId": "light.living"}},
            ),
        )
    )
    assert result["header"]["name"] == "QueryResponse"
    assert any(a["name"] == "turnOnState" for a in result["payload"]["attributes"])


def test_unknown_namespace():
    result = run(
        handle_request(
            _hass(),
            _device_map(_hass()),
            _request("DuerOS.Unknown", "WhateverRequest", {}),
        )
    )
    assert result["header"]["name"] == "NotSupportedInCurrentModeError"


def _ct_light_state(entity_id="light.ct"):
    return FakeState(
        entity_id,
        "on",
        {
            "friendly_name": "色温灯",
            "supported_color_modes": ["color_temp"],
            "color_temp_kelvin": 4000,
            "color_temp_min_kelvin": 1700,
            "color_temp_max_kelvin": 6500,
        },
    )


def test_control_color_temperature_maps_to_kelvin():
    hass = FakeHass([_ct_light_state()])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.ct"]),
            _request(
                NAMESPACE_CONTROL,
                "SetColorTemperatureRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.ct"},
                    "colorTemperature": {"value": 3000},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetColorTemperatureConfirmation"
    assert hass.service_calls == [
        ("light", "turn_on", {"entity_id": "light.ct", "color_temp_kelvin": 3000})
    ]


def test_control_color_temperature_clamped_to_device_range():
    hass = FakeHass([_ct_light_state()])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.ct"]),
            _request(
                NAMESPACE_CONTROL,
                "SetColorTemperatureRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.ct"},
                    "colorTemperature": {"value": 9000},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetColorTemperatureConfirmation"
    assert hass.service_calls == [
        ("light", "turn_on", {"entity_id": "light.ct", "color_temp_kelvin": 6500})
    ]


def test_discovery_advertises_color_temperature_capability():
    hass = FakeHass([_ct_light_state()])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.ct"]),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    light = result["payload"]["discoveredAppliances"][0]
    assert "setColorTemperature" in light["actions"]
    ct = next(
        (a for a in light["attributes"] if a["name"] == "colorTemperatureInKelvin"),
        None,
    )
    assert ct is not None
    assert ct["value"] == 4000
    assert ct["scale"] == "K"
    assert ct["legalValue"] == "[1700, 6500]"


def test_discovery_omits_color_temperature_for_plain_light():
    hass = FakeHass([FakeState("light.plain", "on", {"friendly_name": "普通灯"})])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.plain"]),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    light = result["payload"]["discoveredAppliances"][0]
    assert "setColorTemperature" not in light["actions"]
    assert not any(
        a["name"] == "colorTemperatureInKelvin" for a in light["attributes"]
    )


def test_control_rejects_disabled_capability():
    hass = FakeHass([_ct_light_state()])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.ct"], caps=["colorTemperature"]),
            _request(
                NAMESPACE_CONTROL,
                "SetBrightnessPercentageRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.ct"},
                    "brightness": {"value": 50},
                },
            ),
        )
    )
    assert result["header"]["name"] == "NotSupportedInCurrentModeError"
    assert hass.service_calls == []


def test_discovery_advertises_only_enabled_capabilities():
    hass = FakeHass([_ct_light_state()])
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.ct"], caps=["colorTemperature"]),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    light = result["payload"]["discoveredAppliances"][0]
    assert "setColorTemperature" in light["actions"]
    assert "turnOn" in light["actions"]  # power is mandatory
    assert "setBrightnessPercentage" not in light["actions"]
    names = {a["name"] for a in light["attributes"]}
    assert "colorTemperatureInKelvin" in names
    assert "brightness" not in names


def test_discovery_uses_device_registry_name():
    hass = _hass()
    devices = _device_map(
        hass,
        ["light.living"],
        name_of=lambda key: {"light.living": "床头灯"}.get(key),
    )
    result = run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    light = next(
        a for a in result["payload"]["discoveredAppliances"]
        if a["applianceId"] == "light.living"
    )
    assert light["friendlyName"] == "床头灯"
    assert light["friendlyDescription"] == "床头灯"


def test_discovery_falls_back_to_entity_name_without_device():
    hass = _hass()
    devices = _device_map(hass, ["light.living"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    light = next(
        a for a in result["payload"]["discoveredAppliances"]
        if a["applianceId"] == "light.living"
    )
    assert light["friendlyName"] == "客厅灯"


def _discovery_with_groups(hass, devices):
    return run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )


def test_discovery_groups_sync_areas_generates_area_groups():
    hass = _hass()
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: None,
        name_of=lambda key: None,
        config={"light.living": ["brightness"], "switch.plug": []},
        area_name_of=lambda key: {"light.living": "卧室", "switch.plug": "卧室"}.get(key),
    )
    devices = devices_mod.XiaoduDeviceMap(device_list, sync_areas=True)
    result = _discovery_with_groups(hass, devices)
    groups = result["payload"]["discoveredGroups"]
    assert groups == [
        {
            "groupName": "卧室",
            "applianceIds": ["light.living", "switch.plug"],
        }
    ]


def test_discovery_groups_sanitizes_area_names():
    hass = _hass()
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: None,
        name_of=lambda key: None,
        config={"light.living": []},
        area_name_of=lambda key: "卧室！·（1）",
    )
    devices = devices_mod.XiaoduDeviceMap(device_list, sync_areas=True)
    result = _discovery_with_groups(hass, devices)
    groups = result["payload"]["discoveredGroups"]
    assert groups == [{"groupName": "卧室1", "applianceIds": ["light.living"]}]


def test_discovery_groups_empty_when_sync_areas_off():
    hass = _hass()
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: None,
        name_of=lambda key: None,
        config={"light.living": []},
        area_name_of=lambda key: "卧室",
    )
    devices = devices_mod.XiaoduDeviceMap(device_list)
    result = _discovery_with_groups(hass, devices)
    assert result["payload"]["discoveredGroups"] == []


def _tv_state():
    return FakeState(
        "media_player.tv",
        "on",
        {
            "friendly_name": "电视",
            "volume_level": 0.3,
            "is_volume_muted": False,
            "source_list": ["HDMI1", "HDMI2"],
            "source": "HDMI1",
        },
    )


def test_control_media_player_volume():
    hass = FakeHass([_tv_state()])
    devices = _device_map(hass, ["media_player.tv"], caps=["volume"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_CONTROL,
                "SetVolumeRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "media_player.tv"},
                    "volume": {"value": 50},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetVolumeConfirmation"
    assert hass.service_calls == [
        ("media_player", "volume_set", {"entity_id": "media_player.tv", "volume_level": 0.5})
    ]


def test_control_media_player_mute():
    hass = FakeHass([_tv_state()])
    devices = _device_map(hass, ["media_player.tv"], caps=["mute"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_CONTROL,
                "SetVolumeMuteRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "media_player.tv"},
                    "mute": True,
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetVolumeMuteConfirmation"
    assert hass.service_calls == [
        ("media_player", "volume_mute", {"entity_id": "media_player.tv", "is_volume_muted": True})
    ]


def test_control_media_player_channel():
    hass = FakeHass([_tv_state()])
    devices = _device_map(hass, ["media_player.tv"], caps=["channel"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_CONTROL,
                "SetTVChannelRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "media_player.tv"},
                    "channel": {"value": "HDMI2"},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetTVChannelConfirmation"
    assert hass.service_calls == [
        ("media_player", "select_source", {"entity_id": "media_player.tv", "source": "HDMI2"})
    ]


def test_control_fan_speed():
    hass = FakeHass([FakeState("fan.f1", "on", {"friendly_name": "风扇", "percentage": 30})])
    devices = _device_map(hass, ["fan.f1"], caps=["fanSpeed"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_CONTROL,
                "SetFanSpeedRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "fan.f1"},
                    "fanSpeed": {"value": 5},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetFanSpeedConfirmation"
    assert hass.service_calls == [
        ("fan", "set_percentage", {"entity_id": "fan.f1", "percentage": 50})
    ]


def test_control_humidifier_humidity():
    hass = FakeHass([FakeState("humidifier.h", "on", {"friendly_name": "加湿器", "humidity": 50})])
    devices = _device_map(hass, ["humidifier.h"], caps=["targetHumidity"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_CONTROL,
                "SetHumidityRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "humidifier.h"},
                    "humidity": {"value": 60},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetHumidityConfirmation"
    assert hass.service_calls == [
        ("humidifier", "set_humidity", {"entity_id": "humidifier.h", "humidity": 60})
    ]


def test_control_vacuum_start():
    hass = FakeHass([FakeState("vacuum.v", "idle", {"friendly_name": "扫地机"})])
    devices = _device_map(hass, ["vacuum.v"], caps=[])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "vacuum.v"}},
            ),
        )
    )
    assert result["header"]["name"] == "TurnOnConfirmation"
    assert hass.service_calls == [
        ("vacuum", "start", {"entity_id": "vacuum.v"})
    ]


def test_discovery_tv_actions_and_attributes():
    hass = FakeHass([_tv_state()])
    devices = _device_map(hass, ["media_player.tv"], caps=["volume", "mute", "channel"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    tv = next(
        a for a in result["payload"]["discoveredAppliances"]
        if a["applianceId"] == "media_player.tv"
    )
    assert {"turnOn", "turnOff", "setVolume", "setVolumeMute", "setTVChannel"} <= set(tv["actions"])
    names = {a["name"] for a in tv["attributes"]}
    assert {"volume", "muteState", "channel"} <= names


def _sensor_device_map(hass, config):
    """Group a temperature + humidity pair into one 温湿度计 device."""
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "sensor-dev" if eid in ("sensor.t", "sensor.h") else eid,
        name_of=lambda key: {"sensor-dev": "温湿度计"}.get(key),
        config=config,
    )
    return devices_mod.XiaoduDeviceMap(device_list)


def _temp_humidity_hass():
    return FakeHass(
        [
            FakeState(
                "sensor.t",
                "23.5",
                {"friendly_name": "温度", "unit_of_measurement": "°C", "device_class": "temperature"},
            ),
            FakeState(
                "sensor.h",
                "50",
                {"friendly_name": "湿度", "unit_of_measurement": "%", "device_class": "humidity"},
            ),
        ]
    )


def test_discovery_thermohygrometer_unions_readonly_attributes():
    # Empty legacy selection on a read-only device exposes all read-only caps.
    hass = _temp_humidity_hass()
    devices = _sensor_device_map(hass, {"sensor-dev": []})
    result = run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    sensor = next(a for a in result["payload"]["discoveredAppliances"])
    names = {a["name"] for a in sensor["attributes"]}
    assert {"temperature", "humidity"} <= names


def test_discovery_readonly_capability_selectable():
    hass = _temp_humidity_hass()
    devices = _sensor_device_map(hass, {"sensor-dev": ["humidity"]})
    result = run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    sensor = next(a for a in result["payload"]["discoveredAppliances"])
    names = {a["name"] for a in sensor["attributes"]}
    assert "humidity" in names
    assert "temperature" not in names


def test_query_routes_to_sibling_entity():
    hass = _temp_humidity_hass()
    devices = _sensor_device_map(hass, {"sensor-dev": ["temperature", "humidity"]})
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_QUERY,
                "GetHumidityRequest",
                {"accessToken": "t", "appliance": {"applianceId": "sensor.h"}},
            ),
        )
    )
    assert result["header"]["name"] == "GetHumidityResponse"
    humidity = result["payload"]["attributes"][0]
    assert humidity["name"] == "humidity"
    assert humidity["value"] == 50


def test_query_temperature_requires_enabled_capability():
    hass = _temp_humidity_hass()
    devices = _sensor_device_map(hass, {"sensor-dev": ["humidity"]})
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_QUERY,
                "GetTemperatureReadingRequest",
                {"accessToken": "t", "appliance": {"applianceId": "sensor.h"}},
            ),
        )
    )
    assert result["header"]["name"] == "NotSupportedInCurrentModeError"

    devices = _sensor_device_map(hass, {"sensor-dev": ["temperature", "humidity"]})
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_QUERY,
                "GetTemperatureReadingRequest",
                {"accessToken": "t", "appliance": {"applianceId": "sensor.h"}},
            ),
        )
    )
    assert result["header"]["name"] == "GetTemperatureReadingResponse"


def test_sensor_fahrenheit_reports_scale():
    hass = FakeHass(
        [
            FakeState(
                "sensor.tf",
                "65.66",
                {"friendly_name": "温度", "unit_of_measurement": "°F", "device_class": "temperature"},
            )
        ]
    )
    devices = _device_map(hass, ["sensor.tf"], caps=["temperature"])
    result = run(
        handle_request(
            hass,
            devices,
            _request(
                NAMESPACE_QUERY,
                "GetTemperatureReadingRequest",
                {"accessToken": "t", "appliance": {"applianceId": "sensor.tf"}},
            ),
        )
    )
    reading = result["payload"]["temperatureReading"]
    assert reading["value"] == 65.66
    assert reading["scale"] == "FAHRENHEIT"


def test_light_device_does_not_aggregate_percent_sibling_as_humidity():
    # Regression: the 床头灯's "饱和度" sensor (unit "%", no device_class)
    # must not be derived/aggregated as a humidity capability.
    hass = FakeHass(
        [
            FakeState("light.lamp", "on", {"friendly_name": "床头灯"}),
            FakeState("sensor.saturability", "65", {"friendly_name": "饱和度", "unit_of_measurement": "%"}),
        ]
    )
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "lamp-dev" if eid in ("light.lamp", "sensor.saturability") else eid,
        name_of=lambda key: {"lamp-dev": "床头灯"}.get(key),
        config={"lamp-dev": []},
    )
    devices = devices_mod.XiaoduDeviceMap(device_list)
    result = run(
        handle_request(
            hass,
            devices,
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    lamp = next(a for a in result["payload"]["discoveredAppliances"])
    assert not any(a["name"] == "humidity" for a in lamp["attributes"])


def _clothes_rack_hass():
    return FakeHass(
        [
            FakeState(
                "cover.rack",
                "closed",
                {"friendly_name": "晾衣杆", "supported_features": 11},
            ),
            FakeState("light.rack_light", "off", {"friendly_name": "晾衣杆 灯"}),
        ]
    )


def _clothes_rack_map(hass, caps=None):
    """Group the 晾衣杆 cover + light into one clothes-rack device."""
    all_caps = [c for c in devices_mod.CAP_LABELS if c != devices_mod.CAP_POWER]
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={
            "rack-dev": {
                "cover.rack": list(all_caps if caps is None else caps),
            }
        },
        metadata_of=lambda key: {
            "manufacturer": "四季沐歌",
            "model": "micoe.airer.hz001z",
        },
    )
    return devices_mod.XiaoduDeviceMap(device_list)


def test_discovery_clothes_rack_advertises_clothes_rack():
    hass = _clothes_rack_hass()
    result = run(
        handle_request(
            hass,
            _clothes_rack_map(hass),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    appliances = result["payload"]["discoveredAppliances"]
    ids = [a["applianceId"] for a in appliances]
    # The cover is the primary entity; the rack light is not a separate device.
    assert ids == ["cover.rack"]
    rack = appliances[0]
    assert rack["applianceTypes"] == ["CLOTHES_RACK"]
    assert {"turnOn", "turnOff", "pause"} <= set(rack["actions"])
    assert rack["friendlyName"] == "晾衣杆"


def test_control_clothes_rack_up_down_pause_maps_cover_services():
    hass = _clothes_rack_hass()
    devices = _clothes_rack_map(hass)
    for name in ("TurnOnRequest", "TurnOffRequest", "PauseRequest"):
        result = run(
            handle_request(
                hass,
                devices,
                _request(
                    NAMESPACE_CONTROL,
                    name,
                    {"accessToken": "t", "appliance": {"applianceId": "cover.rack"}},
                ),
            )
        )
        assert result["header"]["name"] == name.replace("Request", "Confirmation")
    assert hass.service_calls == [
        ("cover", "open_cover", {"entity_id": "cover.rack"}),
        ("cover", "close_cover", {"entity_id": "cover.rack"}),
        ("cover", "stop_cover", {"entity_id": "cover.rack"}),
    ]


def test_control_clothes_rack_pause_implied_for_legacy_empty_config():
    # A clothes rack configured before "pause" existed (stored []) must still
    # expose pause after upgrade: cover pause is implied like power.
    hass = _clothes_rack_hass()
    result = run(
        handle_request(
            hass,
            _clothes_rack_map(hass, caps=[]),
            _request(
                NAMESPACE_CONTROL,
                "PauseRequest",
                {"accessToken": "t", "appliance": {"applianceId": "cover.rack"}},
            ),
        )
    )
    assert result["header"]["name"] == "PauseConfirmation"
    assert hass.service_calls == [("cover", "stop_cover", {"entity_id": "cover.rack"})]


def test_control_curtain_pause_maps_stop_cover():
    hass = _hass()
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["cover.curtain"]),
            _request(
                NAMESPACE_CONTROL,
                "PauseRequest",
                {"accessToken": "t", "appliance": {"applianceId": "cover.curtain"}},
            ),
        )
    )
    assert result["header"]["name"] == "PauseConfirmation"
    assert hass.service_calls == [("cover", "stop_cover", {"entity_id": "cover.curtain"})]


def test_control_unknown_state_is_not_offline():
    # Xiaomi airer covers stay "unknown" until first move; control must still
    # be allowed (only "unavailable" counts as offline).
    hass = FakeHass(
        [
            FakeState(
                "cover.rack",
                "unknown",
                {"friendly_name": "晾衣杆", "supported_features": 11},
            )
        ]
    )
    result = run(
        handle_request(
            hass,
            _clothes_rack_map(hass),
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "cover.rack"}},
            ),
        )
    )
    assert result["header"]["name"] == "TurnOnConfirmation"
    assert hass.service_calls == [("cover", "open_cover", {"entity_id": "cover.rack"})]


def test_discovery_multi_unit_device_exposes_two_appliances():
    # Both the 晾衣杆 cover and its light are selected -> two appliances with
    # their own types, names and actions.
    hass = _clothes_rack_hass()
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={
            "rack-dev": {
                "cover.rack": [],
                "light.rack_light": [],
            }
        },
        metadata_of=lambda key: {"model": "micoe.airer.hz001z"},
    )
    result = run(
        handle_request(
            hass,
            devices_mod.XiaoduDeviceMap(device_list),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    appliances = {a["applianceId"]: a for a in result["payload"]["discoveredAppliances"]}
    assert set(appliances) == {"cover.rack", "light.rack_light"}
    rack = appliances["cover.rack"]
    assert rack["applianceTypes"] == ["CLOTHES_RACK"]
    assert {"turnOn", "turnOff", "pause"} <= set(rack["actions"])
    assert rack["friendlyName"] == "晾衣杆"
    light = appliances["light.rack_light"]
    assert light["applianceTypes"] == ["LIGHT"]
    assert {"turnOn", "turnOff", "timingTurnOn", "timingTurnOff"} <= set(light["actions"])
    assert light["friendlyName"] == "晾衣杆 灯"


def test_discovery_disabled_unit_is_not_exposed():
    # A unit absent from the config must not appear in discovery.
    hass = _clothes_rack_hass()
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={"rack-dev": {"cover.rack": []}},
        metadata_of=lambda key: {"model": "micoe.airer.hz001z"},
    )
    result = run(
        handle_request(
            hass,
            devices_mod.XiaoduDeviceMap(device_list),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    ids = [a["applianceId"] for a in result["payload"]["discoveredAppliances"]]
    assert ids == ["cover.rack"]


def test_control_multi_unit_light_routes_to_light_entity():
    hass = _clothes_rack_hass()
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "rack-dev",
        name_of=lambda key: "晾衣杆",
        config={
            "rack-dev": {
                "cover.rack": [],
                "light.rack_light": [],
            }
        },
        metadata_of=lambda key: {"model": "micoe.airer.hz001z"},
    )
    result = run(
        handle_request(
            hass,
            devices_mod.XiaoduDeviceMap(device_list),
            _request(
                NAMESPACE_CONTROL,
                "TurnOnRequest",
                {"accessToken": "t", "appliance": {"applianceId": "light.rack_light"}},
            ),
        )
    )
    assert result["header"]["name"] == "TurnOnConfirmation"
    assert hass.service_calls == [
        ("light", "turn_on", {"entity_id": "light.rack_light"})
    ]


# --- v0.7.0: YUBA / SOCKET / timing / vacuum continue -----------------------


def _yuba_hass():
    return FakeHass(
        [
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
    )


def _yuba_map(hass):
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "yuba-dev",
        name_of=lambda key: "米家智能浴霸N1",
        config={"yuba-dev": {"light.yuba_light": ["brightness", "temperature"]}},
        metadata_of=lambda key: {"manufacturer": "小米", "model": "xiaomi.bhf_light.na1"},
    )
    return devices_mod.XiaoduDeviceMap(device_list)


def test_discovery_yuba_advertises_single_yuba_appliance():
    hass = _yuba_hass()
    result = run(
        handle_request(
            hass,
            _yuba_map(hass),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    appliances = result["payload"]["discoveredAppliances"]
    # Only the YUBA master is exposed (function switches stay off by default
    # and the auxiliary config switches are filtered out entirely).
    assert [a["applianceId"] for a in appliances] == ["light.yuba_light"]
    master = appliances[0]
    assert master["applianceTypes"] == ["YUBA"]
    assert master["friendlyName"] == "米家智能浴霸N1"
    actions = set(master["actions"])
    assert {
        "turnOn",
        "turnOff",
        "timingTurnOn",
        "timingTurnOff",
        "setBrightnessPercentage",
        "setMode",
        "unSetMode",
        "setTemperature",
    } <= actions
    attr_names = {a["name"] for a in master["attributes"]}
    assert {"turnOnState", "brightness", "mode", "targetTemperature", "temperature"} <= attr_names
    mode = next(a for a in master["attributes"] if a["name"] == "mode")
    assert mode["value"] == "照明"  # light is on, functions are off
    assert mode["legalValue"] == "(照明, 暖风, 吹风, 换气)"


def test_control_yuba_set_mode_routes_to_function_switch():
    hass = _yuba_hass()
    result = run(
        handle_request(
            hass,
            _yuba_map(hass),
            _request(
                NAMESPACE_CONTROL,
                "SetModeRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.yuba_light"},
                    "mode": {"value": "暖风"},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetModeConfirmation"
    assert hass.service_calls == [
        ("switch", "turn_on", {"entity_id": "switch.yuba_heating"})
    ]


def test_control_yuba_unset_mode_turns_function_off():
    hass = _yuba_hass()
    result = run(
        handle_request(
            hass,
            _yuba_map(hass),
            _request(
                NAMESPACE_CONTROL,
                "UnSetModeRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.yuba_light"},
                    "mode": {"value": "吹风"},
                },
            ),
        )
    )
    assert result["header"]["name"] == "UnSetModeConfirmation"
    assert hass.service_calls == [
        ("switch", "turn_off", {"entity_id": "switch.yuba_blow"})
    ]


def test_control_yuba_turn_off_shuts_all_functions():
    hass = _yuba_hass()
    result = run(
        handle_request(
            hass,
            _yuba_map(hass),
            _request(
                NAMESPACE_CONTROL,
                "TurnOffRequest",
                {"accessToken": "t", "appliance": {"applianceId": "light.yuba_light"}},
            ),
        )
    )
    assert result["header"]["name"] == "TurnOffConfirmation"
    expected = [
        ("light", "turn_off", {"entity_id": "light.yuba_light"}),
        ("switch", "turn_off", {"entity_id": "switch.yuba_heating"}),
        ("switch", "turn_off", {"entity_id": "switch.yuba_blow"}),
        ("switch", "turn_off", {"entity_id": "switch.yuba_vent"}),
    ]
    assert len(hass.service_calls) == len(expected)
    for call in expected:
        assert call in hass.service_calls


def test_control_yuba_set_temperature_maps_to_number():
    hass = _yuba_hass()
    result = run(
        handle_request(
            hass,
            _yuba_map(hass),
            _request(
                NAMESPACE_CONTROL,
                "SetTemperatureRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.yuba_light"},
                    "temperature": {"value": 30},
                },
            ),
        )
    )
    assert result["header"]["name"] == "SetTemperatureConfirmation"
    assert hass.service_calls == [
        ("number", "set_value", {"entity_id": "number.yuba_target_temp", "value": 30})
    ]


def test_control_timing_turn_off_schedules_persisted_call():
    hass = _hass()
    manager = FakeTimedManager()
    hass.data["xiaodu"] = {"timed_services": manager}
    now = time.time()
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.living"]),
            _request(
                NAMESPACE_CONTROL,
                "TimingTurnOffRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.living"},
                    "timestamp": {"value": now + 60},
                },
            ),
        )
    )
    assert result["header"]["name"] == "TimingTurnOffConfirmation"
    assert len(manager.scheduled) == 1
    domain, service, data, fire_at = manager.scheduled[0]
    assert (domain, service, data) == ("light", "turn_off", {"entity_id": "light.living"})
    assert abs(fire_at - (now + 60)) < 1


def test_control_timing_turn_on_schedules_persisted_call():
    hass = _hass()
    manager = FakeTimedManager()
    hass.data["xiaodu"] = {"timed_services": manager}
    now = time.time()
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["switch.plug"]),
            _request(
                NAMESPACE_CONTROL,
                "TimingTurnOnRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "switch.plug"},
                    "timestamp": {"value": now + 120},
                },
            ),
        )
    )
    assert result["header"]["name"] == "TimingTurnOnConfirmation"
    domain, service, data, fire_at = manager.scheduled[0]
    assert (domain, service, data) == ("switch", "turn_on", {"entity_id": "switch.plug"})
    assert abs(fire_at - (now + 120)) < 1


def test_control_timing_rejects_invalid_timestamp():
    hass = _hass()
    manager = FakeTimedManager()
    hass.data["xiaodu"] = {"timed_services": manager}
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["light.living"]),
            _request(
                NAMESPACE_CONTROL,
                "TimingTurnOffRequest",
                {
                    "accessToken": "t",
                    "appliance": {"applianceId": "light.living"},
                    "timestamp": {"value": "not-a-number"},
                },
            ),
        )
    )
    assert result["header"]["name"] == "NotSupportedInCurrentModeError"
    assert manager.scheduled == []


def test_discovery_socket_advertises_socket_type():
    hass = FakeHass(
        [
            FakeState("switch.plug_on", "on", {"friendly_name": "米家智能插座2 蓝牙网关版 开关"}),
            FakeState("switch.plug_task", "off", {"friendly_name": "米家智能插座2 蓝牙网关版 任务开关"}),
            FakeState("light.plug_indicator", "on", {"friendly_name": "米家智能插座2 蓝牙网关版 指示灯"}),
        ]
    )
    device_list = devices_mod.build_devices_from_entities(
        hass.states.async_all(),
        device_of=lambda eid: "plug-dev",
        name_of=lambda key: "米家智能插座2 蓝牙网关版",
        config={"plug-dev": {"switch.plug_on": []}},
        metadata_of=lambda key: {"manufacturer": "小白", "model": "chuangmi.plug.212a01"},
    )
    result = run(
        handle_request(
            hass,
            devices_mod.XiaoduDeviceMap(device_list),
            _request(NAMESPACE_DISCOVERY, "DiscoverAppliancesRequest", {"accessToken": "t"}),
        )
    )
    appliances = result["payload"]["discoveredAppliances"]
    assert [a["applianceId"] for a in appliances] == ["switch.plug_on"]
    assert appliances[0]["applianceTypes"] == ["SOCKET"]
    assert {"turnOn", "turnOff", "timingTurnOn", "timingTurnOff"} <= set(appliances[0]["actions"])


def test_control_vacuum_continue_starts():
    hass = FakeHass(
        [
            FakeState(
                "vacuum.robot",
                "paused",
                {"friendly_name": "扫地机器人", "fan_speed_list": ["安静", "标准", "强力"]},
            )
        ]
    )
    result = run(
        handle_request(
            hass,
            _device_map(hass, ["vacuum.robot"]),
            _request(
                NAMESPACE_CONTROL,
                "ContinueRequest",
                {"accessToken": "t", "appliance": {"applianceId": "vacuum.robot"}},
            ),
        )
    )
    assert result["header"]["name"] == "ContinueConfirmation"
    assert hass.service_calls == [("vacuum", "start", {"entity_id": "vacuum.robot"})]
