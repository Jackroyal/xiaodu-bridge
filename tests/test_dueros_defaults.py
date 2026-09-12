"""Pure-logic tests for the generic (fallback) DuerDevice builder."""

from tests._dueros_loader import load_semantic_model

load_semantic_model()
from xiaodu.dueros.defaults import _clean_entity_name, _dedup_tokens, _strip_device_prefix, build_default_devices
from xiaodu.dueros.model import DeviceBuildContext, make_device_id


class FakeState:
    def __init__(self, entity_id, state, attributes=None):
        self.entity_id = entity_id
        self.state = state
        self.domain = entity_id.split(".", 1)[0]
        self.attributes = attributes or {}


def _ctx(states, ha_device_id="dev", config=None, name="设备", stable_of=None):
    """Build a context; ``stable_of`` maps entity_id -> registry unique_id."""
    stable_id_of = None
    if stable_of is not None:
        def stable_id_of(entity_id):
            return stable_of.get(entity_id)

    return DeviceBuildContext(
        hass=None,
        ha_device_id=ha_device_id,
        device_name=name,
        states=list(states),
        config=config,
        stable_id_of=stable_id_of,
    )


def test_clean_entity_name_strips_device_prefix_and_key():
    assert _clean_entity_name("灯  筒灯 左键", "灯") == "筒灯"
    assert _clean_entity_name("灯  餐厅灯 右键", "灯") == "餐厅灯"


def test_clean_entity_name_strips_type_suffix():
    assert _clean_entity_name("厨房  吸顶灯 开关", "厨房") == "吸顶灯"


def test_clean_entity_name_keeps_prefix_when_result_is_generic():
    assert _clean_entity_name("厨房  灯 开关", "厨房") == "厨房 灯"


def test_clean_entity_name_keeps_device_when_it_contains_sub():
    assert _clean_entity_name("左窗帘  窗帘", "左窗帘") == "左窗帘"
    assert _clean_entity_name("窗帘  窗帘", "窗帘") == "窗帘"


def test_clean_entity_name_leaves_plain_names_untouched():
    # No device-prefix and no noise suffix: return the name as-is.
    assert _clean_entity_name("床头灯", "床头灯") == "床头灯"
    # A key at the front with a hyphen is not a trailing suffix; only the
    # trailing "开关" type suffix is stripped.
    assert _clean_entity_name("厨房  左键-厨房 开关", "厨房") == "左键-厨房"


def test_clean_entity_name_none():
    assert _clean_entity_name(None, "设备") == ""


def test_strip_device_prefix():
    assert _strip_device_prefix("窗帘  窗帘", "窗帘") == "窗帘"
    assert _strip_device_prefix("床头灯", "床头灯") == "床头灯"
    assert _strip_device_prefix(None, "设备") == ""


def test_dedup_tokens():
    assert _dedup_tokens("移动侦测 移动侦测") == "移动侦测"
    assert _dedup_tokens("窗帘 唤醒模式") == "窗帘 唤醒模式"
    assert _dedup_tokens("灯 灯光") == "灯光"
    assert _dedup_tokens("温控器(冷冻)") == "温控器(冷冻)"


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
    devs = build_default_devices(_ctx([s], stable_of={"light.lamp": "lamp-uid-1"}))
    assert len(devs) == 1
    d = devs[0]
    assert d.device_id == make_device_id("light", "dev", "lamp-uid-1")
    assert d.device_id != "light.lamp"
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
    devs = build_default_devices(_ctx([s], ha_device_id="plug-dev", stable_of={"switch.plug_on": "plug-uid"}))
    assert len(devs) == 1
    assert devs[0].appliance_types == ("SOCKET",)
    assert devs[0].device_id == make_device_id("switch", "plug-dev", "plug-uid")


def test_sensor_pair_aggregates_into_single_sensor():
    t = FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h = FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    devs = build_default_devices(
        _ctx(
            [t, h],
            ha_device_id="temp-dev",
            stable_of={"sensor.t": "temp-uid-t", "sensor.h": "hum-uid-h"},
        )
    )
    assert len(devs) == 1
    d = devs[0]
    assert d.profile_key == "SENSOR"
    assert d.appliance_types == ("SENSOR",)
    # Deterministic aggregate id: device id + the *stable* identities, ordered
    # by stable sub (hum-uid-h < temp-uid-t), independent of entity ids.
    assert d.device_id == make_device_id("SENSOR", "temp-dev", "hum-uid-h")
    assert d.primary_entity_id == "sensor.h"
    # Read-only sensor: no *control* actions, but the query capabilities are
    # advertised as query actions so DuerOS can answer 温度/湿度 questions.
    assert set(d.actions()) == {"getHumidity", "getTemperatureReading"}
    assert {c.key for c in d.capabilities} <= {"temperature", "humidity"}
    caps = {c.key for c in d.capabilities}
    assert {"temperature", "humidity"} <= caps


def test_builder_ignores_config_narrowing():
    """Capability narrowing moved to enhanced._filter_device.

    The generic builder no longer reads ``ctx.config``: every control entity is
    built with all its capabilities, and per-device capability selection is
    applied afterwards (uniformly, profiles included).
    """
    s = FakeState(
        "light.lamp",
        "on",
        {"friendly_name": "灯", "brightness": 100, "supported_color_modes": ["brightness", "color_temp"], "color_temp_kelvin": 4000},
    )
    devs = build_default_devices(_ctx([s], config=["power", "brightness"]))
    d = devs[0]
    keys = {c.key for c in d.capabilities}
    # Even though the config only selected power+brightness, the builder keeps
    # colorTemperature; the narrowing is done by enhanced._filter_device.
    assert "power" in keys and "brightness" in keys
    assert "colorTemperature" in keys


def test_builder_exposes_every_control_entity_ignoring_per_entity_dict():
    """Legacy per-entity dicts no longer gate entity exposure here.

    The builder exposes every control entity of the device; hiding an entity is
    an explicit ``hidden`` override in the per-device object (enhanced layer).
    """
    cover = FakeState("cover.airer", "closed", {"friendly_name": "晾衣杆"})
    light = FakeState("light.airer_light", "off", {"friendly_name": "晾衣杆 灯"})
    devs = build_default_devices(
        _ctx(
            [cover, light],
            ha_device_id="rack-dev",
            config={"cover.airer": []},
            stable_of={"cover.airer": "rack-cover-uid", "light.airer_light": "rack-light-uid"},
        )
    )
    ids = {d.device_id for d in devs}
    assert make_device_id("cover", "rack-dev", "rack-cover-uid") in ids
    assert make_device_id("light", "rack-dev", "rack-light-uid") in ids


def test_sensor_builder_keeps_all_query_caps_regardless_of_config():
    """Sensor aggregation ignores ``ctx.config``; narrowing is centralized."""
    t = FakeState("sensor.t", "20", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h = FakeState("sensor.h", "60", {"unit_of_measurement": "%", "device_class": "humidity"})
    devs = build_default_devices(
        _ctx([t, h], ha_device_id="temp-dev", config=["temperature"])
    )
    d = devs[0]
    keys = {c.key for c in d.capabilities}
    assert {"temperature", "humidity"} <= keys


def test_generic_control_device_id_stable_across_entity_rename():
    """A grouped control entity keeps its appliance id after a HA entity rename."""
    s1 = FakeState(
        "light.lamp",
        "on",
        {"friendly_name": "客厅灯", "brightness": 200, "supported_color_modes": ["brightness"]},
    )
    dev1 = build_default_devices(_ctx([s1], ha_device_id="dev", stable_of={"light.lamp": "lamp-uid-1"}))[0]
    # The user renames the entity in HA: new entity_id, SAME registry unique_id.
    s2 = FakeState(
        "light.lamp_renamed",
        "on",
        {"friendly_name": "客厅灯", "brightness": 200, "supported_color_modes": ["brightness"]},
    )
    dev2 = build_default_devices(
        _ctx([s2], ha_device_id="dev", stable_of={"light.lamp_renamed": "lamp-uid-1"})
    )[0]
    assert dev1.device_id == dev2.device_id
    assert dev1.device_id == make_device_id("light", "dev", "lamp-uid-1")
    # ... but a genuinely different entity identity gets a different id.
    s3 = FakeState("light.lamp", "on", {"friendly_name": "客厅灯"})
    dev3 = build_default_devices(_ctx([s3], ha_device_id="dev", stable_of={"light.lamp": "lamp-uid-2"}))[0]
    assert dev3.device_id != dev1.device_id


def test_sensor_aggregate_id_stable_across_member_rename():
    """Aggregating the same two sensor identities yields the same SENSOR id."""
    t1 = FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h1 = FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    dev1 = build_default_devices(
        _ctx([t1, h1], ha_device_id="temp-dev", stable_of={"sensor.t": "temp-uid", "sensor.h": "hum-uid"})
    )[0]
    # Members renamed (different entity ids) but same identities -> same id.
    t2 = FakeState("sensor.temperature_2", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h2 = FakeState("sensor.humidity_2", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    dev2 = build_default_devices(
        _ctx([t2, h2], ha_device_id="temp-dev", stable_of={"sensor.temperature_2": "temp-uid", "sensor.humidity_2": "hum-uid"})
    )[0]
    assert dev1.device_id == dev2.device_id
    assert dev1.device_id == make_device_id("SENSOR", "temp-dev", "hum-uid")


def test_sensor_aggregate_non_primary_rename_keeps_id_and_primary():
    """Renaming a *non-primary* sensor member changes neither id nor primary."""
    t1 = FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h1 = FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    dev1 = build_default_devices(
        _ctx(
            [t1, h1],
            ha_device_id="temp-dev",
            stable_of={"sensor.t": "a-temp-uid", "sensor.h": "b-hum-uid"},
        )
    )[0]
    # Primary is the member with the smallest stable sub (a-temp-uid < b-hum-uid).
    assert dev1.primary_entity_id == "sensor.t"
    assert dev1.device_id == make_device_id("SENSOR", "temp-dev", "a-temp-uid")
    # Rename ONLY the non-primary humidity member (same unique_id -> new entity_id).
    h2 = FakeState("sensor.humidity_renamed", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    dev2 = build_default_devices(
        _ctx(
            [t1, h2],
            ha_device_id="temp-dev",
            stable_of={"sensor.t": "a-temp-uid", "sensor.humidity_renamed": "b-hum-uid"},
        )
    )[0]
    assert dev2.device_id == dev1.device_id
    assert dev2.primary_entity_id == "sensor.t"


def test_sensor_aggregate_primary_rename_keeps_id_switches_primary():
    """Renaming the *primary* sensor member keeps the id but the primary entity
    id follows the member to its new entity_id."""
    t1 = FakeState("sensor.t", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    h1 = FakeState("sensor.h", "50", {"unit_of_measurement": "%", "device_class": "humidity"})
    dev1 = build_default_devices(
        _ctx(
            [t1, h1],
            ha_device_id="temp-dev",
            stable_of={"sensor.t": "a-temp-uid", "sensor.h": "b-hum-uid"},
        )
    )[0]
    assert dev1.primary_entity_id == "sensor.t"
    assert dev1.device_id == make_device_id("SENSOR", "temp-dev", "a-temp-uid")
    # Rename the primary (sensor.t -> sensor.temperature_renamed, same unique_id).
    t2 = FakeState("sensor.temperature_renamed", "23.5", {"unit_of_measurement": "°C", "device_class": "temperature"})
    dev2 = build_default_devices(
        _ctx(
            [t2, h1],
            ha_device_id="temp-dev",
            stable_of={"sensor.temperature_renamed": "a-temp-uid", "sensor.h": "b-hum-uid"},
        )
    )[0]
    assert dev2.device_id == dev1.device_id
    assert dev2.primary_entity_id == "sensor.temperature_renamed"


def test_multiple_generic_entities_on_same_device_get_distinct_ids():
    """Two control entities on one HA device yield two distinct appliances."""
    a = FakeState("light.lamp_a", "on", {"friendly_name": "灯A"})
    b = FakeState("light.lamp_b", "on", {"friendly_name": "灯B"})
    devs = build_default_devices(
        _ctx([a, b], ha_device_id="multi-dev", stable_of={"light.lamp_a": "uid-a", "light.lamp_b": "uid-b"})
    )
    ids = {d.device_id for d in devs}
    assert ids == {
        make_device_id("light", "multi-dev", "uid-a"),
        make_device_id("light", "multi-dev", "uid-b"),
    }
    assert len(ids) == 2


def test_ungrouped_lone_entity_keeps_entity_id_appliance_id():
    """Without a device-registry base there is nothing stable to hash on."""
    s = FakeState("light.lamp", "on", {"friendly_name": "灯"})
    devs = build_default_devices(
        _ctx([s], ha_device_id="light.lamp", stable_of={"light.lamp": "lamp-uid-1"})
    )
    assert devs[0].device_id == "light.lamp"


def test_humidifier_master_control_hides_settings_switches():
    """A humidifier device collapses to its master entity — settings toggles
    (自动熄灯 / 调试…) are not surfaced as standalone switch appliances."""
    h = FakeState(
        "humidifier.air",
        "on",
        {
            "friendly_name": "米家纯净式智能加湿器",
            "humidity": 50,
            "target_humidity": 60,
            "mode": "humidity",
            "available_modes": ["humidity", "auto"],
        },
    )
    s = FakeState("switch.air_display", "on", {"friendly_name": "自动熄灯"})
    devs = build_default_devices(_ctx([h, s], ha_device_id="air-dev"))
    assert all(d.primary_entity_id != "switch.air_display" for d in devs)
    assert len(devs) <= 1
