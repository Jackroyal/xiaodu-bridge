"""Capability model for the DuerOS semantic model (platform-agnostic core).

This module provides the platform-agnostic capability vocabulary and pure
helpers used by ``dueros/defaults.py`` (generic device builder) and
``dueros/enhanced.py`` (runtime assembly):

- capability constants (``CAP_*``), their UI labels (``CAP_LABELS``) and
  control/query kinds,
- device-class markers and ``EXPOSABLE_DOMAINS`` for classification,
- entity helpers: ``derive_capabilities``, ``classify_device``, ``_is_auxiliary``
  and the YUBA / socket control-entity filters.

The module has no Home Assistant runtime imports so it can be unit-tested
standalone.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


CAP_POWER = "power"
CAP_BRIGHTNESS = "brightness"
CAP_COLOR_TEMPERATURE = "colorTemperature"
CAP_COLOR = "color"
CAP_VOLUME = "volume"
CAP_CHANNEL = "channel"
CAP_MUTE = "mute"
CAP_FAN_SPEED = "fanSpeed"
CAP_TARGET_TEMPERATURE = "targetTemperature"
CAP_TARGET_HUMIDITY = "targetHumidity"
CAP_MODE = "mode"
CAP_PERCENTAGE = "percentage"
CAP_SUCTION = "suction"
CAP_WATER_LEVEL = "waterLevel"
CAP_PAUSE = "pause"
CAP_CONTINUE = "continue"
# Read-only (query) capabilities.
CAP_TEMPERATURE = "temperature"
CAP_HUMIDITY = "humidity"

# Capability kinds: control (writable, maps to actions) vs query (read-only,
# maps to attributes / query actions). Both are first-class capabilities so
# read-only devices (sensors) are selectable in the UI and their exposure can
# be controlled per capability.
CAP_KIND_CONTROL = "control"
CAP_KIND_QUERY = "query"

CAP_KINDS = {
    CAP_POWER: CAP_KIND_CONTROL,
    CAP_BRIGHTNESS: CAP_KIND_CONTROL,
    CAP_COLOR_TEMPERATURE: CAP_KIND_CONTROL,
    CAP_COLOR: CAP_KIND_CONTROL,
    CAP_VOLUME: CAP_KIND_CONTROL,
    CAP_CHANNEL: CAP_KIND_CONTROL,
    CAP_MUTE: CAP_KIND_CONTROL,
    CAP_FAN_SPEED: CAP_KIND_CONTROL,
    CAP_TARGET_TEMPERATURE: CAP_KIND_CONTROL,
    CAP_TARGET_HUMIDITY: CAP_KIND_CONTROL,
    CAP_MODE: CAP_KIND_CONTROL,
    CAP_PERCENTAGE: CAP_KIND_CONTROL,
    CAP_SUCTION: CAP_KIND_CONTROL,
    CAP_WATER_LEVEL: CAP_KIND_CONTROL,
    CAP_PAUSE: CAP_KIND_CONTROL,
    CAP_CONTINUE: CAP_KIND_CONTROL,
    CAP_TEMPERATURE: CAP_KIND_QUERY,
    CAP_HUMIDITY: CAP_KIND_QUERY,
}
QUERY_CAPS = frozenset(c for c, k in CAP_KINDS.items() if k == CAP_KIND_QUERY)

CAP_LABELS = {
    CAP_POWER: "开关",
    CAP_BRIGHTNESS: "亮度",
    CAP_COLOR_TEMPERATURE: "色温",
    CAP_COLOR: "颜色",
    CAP_VOLUME: "音量",
    CAP_CHANNEL: "频道",
    CAP_MUTE: "静音",
    CAP_FAN_SPEED: "风速",
    CAP_TARGET_TEMPERATURE: "目标温度",
    CAP_TARGET_HUMIDITY: "目标湿度",
    CAP_MODE: "模式",
    CAP_PERCENTAGE: "位置",
    CAP_SUCTION: "吸力",
    CAP_WATER_LEVEL: "水量",
    CAP_PAUSE: "暂停",
    CAP_CONTINUE: "继续",
    CAP_TEMPERATURE: "温度",
    CAP_HUMIDITY: "湿度",
    # Device-profile capabilities (device-center semantic model).
    "warmthLevel": "暖风档位",
    "electricityCapacity": "电量",
    "workState": "运行状态",
    "timeLeft": "剩余时间",
    "targetHumidity": "目标湿度",
    "waterLevel": "水位",
    "percentage": "位置",
    "pause": "暂停",
    "continue": "继续",
}

# Device-class classification (platform-agnostic, see ``classify_device``).
# ``auto`` means "derive the appliance type from the primary entity domain";
# a concrete class lets a device override that default (e.g. a 晾衣杆 whose
# HA device is a cover but should surface as a CLOTHES_RACK appliance).
DEVICE_CLASS_AUTO = "auto"
DEVICE_CLASS_CLOTHES_RACK = "clothes_rack"
DEVICE_CLASS_YUBA = "yuba"
DEVICE_CLASS_SOCKET = "socket"

# Entity ids / device model markers that identify a clothes rack. Kept loose
# on purpose: Xiaomi Home names the cover entity ``..._airer`` and the model
# ``micoe.airer.*``; other integrations use ``clothes_rack`` / 晾衣.
_CLOTHES_RACK_MARKERS = ("airer", "clothesrack", "clothes_rack", "晾衣")

# A bathroom heater (浴霸): the Xiaomi Home model is ``xiaomi.bhf_light.*`` and
# the device is usually named 浴霸. Classified as the official YUBA appliance so
# Xiaodu offers 取暖/吹风/换气/照明 modes instead of a pile of raw switches.
_YUBA_MARKERS = ("bhf", "浴霸")

# Plugs / sockets: the Xiaomi Home model is ``chuangmi.plug.*`` and the device
# is named 插座. Classified as SOCKET so Xiaodu uses 插座 semantics.
_SOCKET_MARKERS = ("plug", "插座")

# Domains that can expose control capabilities to a speaker platform. Must
# stay in sync with the per-domain composers in ``dueros/defaults.py``.
EXPOSABLE_DOMAINS = frozenset(
    {
        "light",
        "switch",
        "fan",
        "climate",
        "media_player",
        "cover",
        "sensor",
        "humidifier",
        "vacuum",
    }
)


# Entities whose entity_id contains one of these markers are status/safety
# entities (indicator LEDs, child locks, physical-control locks, buzzer/fault
# flags). They are never exposed to speaker platforms: exposing an indicator
# LED as a controllable light would be wrong, and these would only add noise.
_AUXILIARY_MARKERS = (
    "indicator",
    "child_lock",
    "physical_controls",
    "buzzer",
    "fault",
    "is_on",  # Mi Home generates ``*_is_on`` power-state switches on TVs / heaters
    "night_light",  # 夜灯 config switches are not independent speaker appliances
    "night",
)

# Chinese friendly-name keywords for the same kind of status/safety entities
# (indicator LEDs, beepers, child locks). The entity ids of these switches vary
# between firmware versions, so the names are the stable signal.
_AUXILIARY_NAME_KEYWORDS = ("指示灯", "提示音", "童锁", "物理控制锁", "故障")


def _is_auxiliary(entity: Any) -> bool:
    """Return True for status/safety entities that should not be exposed."""
    entity_id = getattr(entity, "entity_id", "").lower()
    if any(marker in entity_id for marker in _AUXILIARY_MARKERS):
        return True
    name = str((getattr(entity, "attributes", None) or {}).get("friendly_name", ""))
    return any(keyword in name for keyword in _AUXILIARY_NAME_KEYWORDS)


def derive_capabilities(state: Any) -> frozenset[str]:
    """Return the capabilities available for one entity state (pure logic)."""
    caps: set[str] = set()
    domain = getattr(state, "domain", "")
    attributes = getattr(state, "attributes", {}) or {}
    if domain in EXPOSABLE_DOMAINS and domain != "sensor":
        caps.add(CAP_POWER)
    if domain == "light":
        modes = set(attributes.get("supported_color_modes") or ())
        # A color-capable light (color_temp / hs / rgb / xy) always supports
        # brightness even when the integration omits the "brightness" mode.
        color_modes = {"color_temp", "color_temp_kelvin", "hs", "rgb", "xy"}
        if (
            "brightness" in modes
            or bool(modes & color_modes)
            or attributes.get("brightness") is not None
            or attributes.get("brightness_pct") is not None
        ):
            caps.add(CAP_BRIGHTNESS)
        if (
            "color_temp" in modes
            or "color_temp_kelvin" in modes
            or attributes.get("color_temp") is not None
            or attributes.get("color_temp_kelvin") is not None
        ):
            caps.add(CAP_COLOR_TEMPERATURE)
        if (
            bool(modes & {"hs", "rgb", "xy"})
            or attributes.get("hs_color") is not None
            or attributes.get("rgb_color") is not None
        ):
            caps.add(CAP_COLOR)
    elif domain == "media_player":
        if attributes.get("volume_level") is not None:
            caps.add(CAP_VOLUME)
        if attributes.get("is_volume_muted") is not None:
            caps.add(CAP_MUTE)
        if attributes.get("source_list"):
            caps.add(CAP_CHANNEL)
    elif domain == "fan":
        if (
            attributes.get("percentage") is not None
            or attributes.get("preset_mode") is not None
            or attributes.get("preset_modes")
        ):
            caps.add(CAP_FAN_SPEED)
    elif domain == "climate":
        if (
            attributes.get("temperature") is not None
            or attributes.get("target_temp_step") is not None
        ):
            caps.add(CAP_TARGET_TEMPERATURE)
        if attributes.get("hvac_modes"):
            caps.add(CAP_MODE)
        if attributes.get("fan_modes"):
            caps.add(CAP_FAN_SPEED)
    elif domain == "cover":
        # Every cover can be paused (stop) even without position support.
        caps.add(CAP_PAUSE)
        if (
            attributes.get("current_position") is not None
            or attributes.get("current_tilt_position") is not None
        ):
            caps.add(CAP_PERCENTAGE)
    elif domain == "humidifier":
        if attributes.get("humidity") is not None or attributes.get(
            "target_humidity"
        ) is not None:
            caps.add(CAP_TARGET_HUMIDITY)
        if attributes.get("available_modes"):
            caps.add(CAP_MODE)
    elif domain == "vacuum":
        if attributes.get("fan_speed_list"):
            caps.add(CAP_SUCTION)
        if attributes.get("water_level_list"):
            caps.add(CAP_WATER_LEVEL)
        if attributes.get("fan_speed_list"):
            caps.add(CAP_MODE)
        # Every HA vacuum can start again after a stop/pause (vacuum.start),
        # which maps to the official "continue" action (继续扫地).
        caps.add(CAP_CONTINUE)
    elif domain == "sensor":
        unit = str(attributes.get("unit_of_measurement", "")).lower()
        device_class = str(attributes.get("device_class", "")).lower()
        if (
            device_class == "temperature"
            or "°c" in unit
            or "℃" in unit
            or unit == "c"
            or "°f" in unit
            or "temperature" in unit
        ):
            caps.add(CAP_TEMPERATURE)
        elif device_class == "humidity" or "humidity" in unit:
            caps.add(CAP_HUMIDITY)
    return frozenset(caps)


def classify_device(
    device_key: str,
    entities: Iterable[Any],
    metadata: dict[str, str] | None = None,
) -> str:
    """Classify a device group into a platform-agnostic device class.

    Returns ``DEVICE_CLASS_AUTO`` when no classifier matches; the primary
    entity then decides the appliance type as before.
    """
    haystack = [device_key]
    if metadata:
        haystack.append(metadata.get("manufacturer", ""))
        haystack.append(metadata.get("model", ""))
    for state in entities:
        haystack.append(state.entity_id)
        haystack.append(str(state.attributes.get("friendly_name", "")))
    text = " ".join(haystack).lower()
    if any(marker in text for marker in _YUBA_MARKERS):
        return DEVICE_CLASS_YUBA
    if any(marker in text for marker in _SOCKET_MARKERS):
        return DEVICE_CLASS_SOCKET
    if any(marker in text for marker in _CLOTHES_RACK_MARKERS):
        return DEVICE_CLASS_CLOTHES_RACK
    return DEVICE_CLASS_AUTO


def _entity_text(entity: Any) -> str:
    """Lowercased entity id + friendly name used for capability matching."""
    name = str((getattr(entity, "attributes", None) or {}).get("friendly_name", ""))
    return f"{getattr(entity, 'entity_id', '')} {name}".lower()


def _yuba_control_entity(entity: Any) -> bool:
    """Keep only the YUBA master (the bathroom light) as an exposed unit.

    Xiaodu models a bathroom heater as ONE ``YUBA`` appliance: 取暖/吹风/换气
    are ``mode`` values of that appliance (setMode / unSetMode), not separate
    devices. Exposing the function switches as standalone SWITCH units would
    duplicate the controls and make the skill's NLU ambiguous ("打开浴霸取暖"
    could match both the master's setMode and the raw 暖风 switch). The
    function switches stay available through the device's ``controls`` map so
    setMode can target them, but they are never units. Everything else
    (夜灯开关/延时/杀菌/提示音 config switches) is filtered out as before.
    """
    text = _entity_text(entity)
    if "indicator" in text:
        return False
    return getattr(entity, "domain", "") == "light"


def _socket_control_entity(entity: Any) -> bool:
    """Keep only the main power switch of a plug (``*_on_p_*``).

    The companion switches (通电状态/翻转开关/任务开关/倒计时) are auxiliary
    configuration and would only add noise as separate speaker appliances.
    """
    return "_on_p_" in getattr(entity, "entity_id", "").lower()