"""Capability-model device mapping (platform-agnostic core).

Home Assistant exposes *entities*; Xiaodu and other smart-speaker platforms
talk about *devices* with *capabilities*. This module:

- groups entities back into devices via the entity/device registries,
- exposes *units*: one unit per controllable entity (a device can therefore
  surface multiple speaker appliances, e.g. a 晾衣杆 cover + its light),
- derives a platform-agnostic capability set per unit (power / brightness /
  colorTemperature / color / ...).

The Xiaodu protocol layer translates these capabilities into DuerOS actions;
future platforms (Tmall Genie, Xiaoai, Alexa, ...) add their own translation
layers without changing this module.

The module has no Home Assistant runtime imports so the core logic can be
unit-tested standalone.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICES,
    CONF_ENTITY_EXCLUDE,
    CONF_ENTITY_INCLUDE,
    CONF_SYNC_AREAS,
)
from .entity_filter import EntityFilter

# Platform-agnostic capabilities.
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
CONTROL_CAPS = frozenset(c for c, k in CAP_KINDS.items() if k == CAP_KIND_CONTROL)
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
# stay in sync with the registered adapters in ``dueros/adapters.py``.
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

# Primary-entity selection priority (lower wins). ``switch`` ranks low on
# purpose: Mi Home creates ``*.is_on`` switch entities on the same device as
# TVs / fans / humidifiers / vacuums, and those auxiliary switches must not
# steal the primary role from the real controller.
_PRIMARY_PRIORITY = {
    "light": 0,
    "media_player": 1,
    "climate": 2,
    "fan": 3,
    "humidifier": 4,
    "cover": 5,
    "vacuum": 6,
    "switch": 7,
    "sensor": 8,
}

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


def select_default_unit(entities: Iterable[Any]) -> Any | None:
    """Pick the default unit of a device group.

    The default unit keeps the device name and inherits legacy list-form
    config; every other unit defaults to off. Auxiliary entities are
    excluded; the richest entity wins (a fan over its indicator light), with
    the domain priority as the tiebreaker.
    """
    candidates = [
        e
        for e in entities
        if getattr(e, "domain", "") in EXPOSABLE_DOMAINS and not _is_auxiliary(e)
    ]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda e: (
            -len(derive_capabilities(e)),
            _PRIMARY_PRIORITY.get(e.domain, 99),
            e.entity_id,
        ),
    )


def _selected_or_readonly(
    unit_caps: list[str] | tuple[str, ...],
    available: frozenset[str],
    implied: set[str],
) -> frozenset[str]:
    """Compute the enabled subset for one unit from its stored caps."""
    selected = set(unit_caps or ())
    if not selected and not (available & {CAP_POWER}):
        # Read-only units (sensors): an empty selection means "expose all
        # read-only capabilities" (power is never available on them).
        return available
    return (selected & available) | (implied & available)


def implied_capabilities(
    *,
    domain: str,
    device_class: str = DEVICE_CLASS_AUTO,
    is_default: bool = False,
) -> tuple[str, ...]:
    """Structural capabilities that stay on whenever available.

    Power is mandatory for every controllable appliance; pause is mandatory
    for covers, and a YUBA master additionally keeps its modes and target
    temperature. The options wizard lists these as force-checked entries.
    """
    implied = [CAP_POWER]
    if domain == "cover":
        implied.append(CAP_PAUSE)
    if device_class == DEVICE_CLASS_YUBA and is_default:
        implied.append(CAP_MODE)
        implied.append(CAP_TARGET_TEMPERATURE)
    return tuple(implied)


def _resolve_enabled(
    *,
    available: frozenset[str],
    device_config: Any,
    entity_id: str,
    is_default: bool,
    domain: str,
    device_class: str = DEVICE_CLASS_AUTO,
) -> frozenset[str]:
    """Resolve the enabled capability subset for one unit.

    Structural capabilities (see ``implied_capabilities``) stay on whenever
    available, so a device configured before pause existed keeps working
    after an upgrade and cannot have them switched off.
    """
    implied = set(
        implied_capabilities(
            domain=domain, device_class=device_class, is_default=is_default
        )
    )
    if device_config is None:
        return available  # candidate view: everything on
    if isinstance(device_config, dict):
        unit_caps = device_config.get(entity_id)
        if unit_caps is None:
            return frozenset()  # unit not selected
        return _selected_or_readonly(unit_caps, available, implied)
    if not is_default:
        return frozenset()  # legacy list applies to the default unit only
    if not device_config:
        # Empty legacy list (migration from older versions): default to every
        # available capability instead of only the implied (mandatory) ones.
        return available
    return _selected_or_readonly(device_config, available, implied)


@dataclass(frozen=True, slots=True)
class XiaoduUnit:
    """One exposable entity: one speaker appliance on a device."""

    entity_id: str
    name: str                        # display name (default unit uses the device name)
    capabilities: frozenset[str]     # available capabilities of this unit
    enabled: frozenset[str]          # user-selected subset actually exposed
    is_default: bool = False         # keeps the device name; carries read-only caps
    query_entities: dict[str, str] = field(default_factory=dict)  # query cap -> entity id
    device_class: str = DEVICE_CLASS_AUTO  # overrides the appliance type


@dataclass(frozen=True, slots=True)
class XiaoduDevice:
    """A physical device: a UI grouping of one or more exposed units."""

    device_key: str
    name: str
    units: tuple[XiaoduUnit, ...] = ()
    area_name: str | None = None   # room name (for UI grouping)
    device_class: str = DEVICE_CLASS_AUTO  # classifier result (grouping/badge only)
    controls: dict[str, str] = field(default_factory=dict)  # semantic control -> entity id

    @property
    def default_unit(self) -> XiaoduUnit | None:
        """Return the default unit (keeps the device name), if any."""
        return next((unit for unit in self.units if unit.is_default), None)


def build_devices_from_entities(
    states: Iterable[Any],
    device_of: Callable[[str], str | None],
    name_of: Callable[[str], str | None],
    config: dict[str, list[str] | dict[str, list[str]]] | None,
    area_name_of: Callable[[str], str | None] | None = None,
    metadata_of: Callable[[str], dict[str, str] | None] | None = None,
) -> list[XiaoduDevice]:
    """Group entity states into devices and expose one unit per entity.

    ``config`` is the ``CONF_DEVICES`` mapping in either form:

    - legacy ``device_key -> [capabilities]``: the list applies to the
      device's default unit only; every other unit stays off.
    - current ``device_key -> {entity_id: [capabilities]}``: units present
      in the mapping are on (with those capabilities), the rest are off.

    ``config=None`` (used for the candidate list in the options wizard)
    exposes every unit with all its capabilities.
    """
    groups: dict[str, list[Any]] = {}
    for state in states:
        key = device_of(state.entity_id) or state.entity_id
        groups.setdefault(key, []).append(state)

    devices: list[XiaoduDevice] = []
    new_mode = config is not None
    for key in sorted(groups):
        if new_mode and key not in config:
            continue
        metadata = metadata_of(key) if metadata_of else None
        device_class = classify_device(key, groups[key], metadata)
        entity_list = groups[key]

        # Semantic controls of a classified device (YUBA): mode functions and
        # the target-temperature number live on non-exposable domains (switch /
        # number), so they are resolved here into entity ids for the adapter.
        controls: dict[str, str] = {}
        if device_class == DEVICE_CLASS_YUBA:
            for candidate in entity_list:
                text = _entity_text(candidate)
                domain = getattr(candidate, "domain", "")
                if domain == "light" and not _is_auxiliary(candidate):
                    controls.setdefault("light", candidate.entity_id)
                elif domain == "switch":
                    if "heating" in text or "暖风" in text or "取暖" in text:
                        controls.setdefault("heating", candidate.entity_id)
                    elif "blow" in text or "吹风" in text:
                        controls.setdefault("blow", candidate.entity_id)
                    elif "ventilation" in text or "换气" in text:
                        controls.setdefault("ventilation", candidate.entity_id)
                elif domain == "number" and (
                    "target_temperature" in text or "设定温度" in text
                ):
                    controls.setdefault("target_temperature", candidate.entity_id)

        # Read-only capabilities are aggregated across the whole device and
        # reported by the default unit (e.g. a 温湿度计 exposes temperature
        # and humidity on separate entities but surfaces as one appliance).
        query_entities: dict[str, str] = {}
        for candidate in entity_list:
            for capability in derive_capabilities(candidate):
                if capability in QUERY_CAPS:
                    query_entities.setdefault(capability, candidate.entity_id)

        # Control-capable entities become their own units; auxiliary
        # entities (indicator LEDs, child locks, ...) are never exposed.
        # Classified devices (浴霸 / 插座) further restrict the unit set to
        # their real functions so the speaker surface stays clean.
        control_entities = [
            e
            for e in entity_list
            if getattr(e, "domain", "") in EXPOSABLE_DOMAINS
            and getattr(e, "domain", "") != "sensor"
            and not _is_auxiliary(e)
        ]
        if device_class == DEVICE_CLASS_YUBA:
            control_entities = [e for e in control_entities if _yuba_control_entity(e)]
        elif device_class == DEVICE_CLASS_SOCKET:
            control_entities = [e for e in control_entities if _socket_control_entity(e)]
        default_entity = select_default_unit(control_entities or entity_list)
        if default_entity is None:
            continue

        device_config = config.get(key) if new_mode else None
        units: list[XiaoduUnit] = []
        if control_entities:
            for entity in control_entities:
                is_default = entity.entity_id == default_entity.entity_id
                caps = set(derive_capabilities(entity))
                if is_default:
                    caps |= set(query_entities)
                    if device_class == DEVICE_CLASS_YUBA:
                        # The YUBA master carries the bathroom-heater function
                        # modes (取暖/吹风/换气) and the target temperature.
                        if any(k in controls for k in ("light", "heating", "blow", "ventilation")):
                            caps.add(CAP_MODE)
                        if "target_temperature" in controls:
                            caps.add(CAP_TARGET_TEMPERATURE)
                unit_device_class = device_class if is_default else DEVICE_CLASS_AUTO
                units.append(
                    _build_unit(
                        entity,
                        caps,
                        device_config,
                        is_default,
                        query_entities if is_default else {},
                        unit_device_class,
                    )
                )
        else:
            caps = set(derive_capabilities(default_entity)) | set(query_entities)
            units.append(
                _build_unit(
                    default_entity,
                    caps,
                    device_config,
                    True,
                    query_entities,
                    device_class,
                )
            )

        if not any(unit.capabilities for unit in units):
            continue
        device_name = (
            name_of(key)
            or (default_entity.attributes or {}).get("friendly_name")
            or default_entity.entity_id
        )
        area_name = area_name_of(key) if area_name_of else None
        devices.append(
            XiaoduDevice(
                device_key=key,
                name=str(device_name),
                area_name=area_name,
                device_class=device_class,
                units=tuple(units),
                controls=controls,
            )
        )
    return devices


def _build_unit(
    entity: Any,
    caps: set[str],
    device_config: Any,
    is_default: bool,
    query_entities: dict[str, str],
    device_class: str,
) -> XiaoduUnit:
    """Build one exposed unit from an entity state."""
    return XiaoduUnit(
        entity_id=entity.entity_id,
        name=str(entity.attributes.get("friendly_name") or entity.entity_id),
        capabilities=frozenset(caps),
        enabled=_resolve_enabled(
            available=frozenset(caps),
            device_config=device_config,
            entity_id=entity.entity_id,
            is_default=is_default,
            domain=entity.domain,
            device_class=device_class,
        ),
        is_default=is_default,
        query_entities=query_entities,
        device_class=device_class,
    )


class XiaoduDeviceMap:
    """Resolved device/unit set for one config entry."""

    def __init__(
        self, devices: list[XiaoduDevice], sync_areas: bool = False
    ) -> None:
        self._devices = devices
        self.sync_areas = sync_areas
        self._units_by_entity = {
            unit.entity_id: unit for device in devices for unit in device.units
        }
        self._device_by_entity = {
            unit.entity_id: device for device in devices for unit in device.units
        }
        self._by_key = {d.device_key: d for d in devices}

    def devices(self) -> list[XiaoduDevice]:
        return list(self._devices)

    def get(self, entity_id: str) -> XiaoduUnit | None:
        """Return the exposed unit for an entity id, if any."""
        return self._units_by_entity.get(entity_id)

    def device(self, device_key: str) -> XiaoduDevice | None:
        return self._by_key.get(device_key)

    def device_for_entity(self, entity_id: str) -> XiaoduDevice | None:
        """Return the physical device owning an exposed unit, if any."""
        return self._device_by_entity.get(entity_id)

    def capability_enabled(self, entity_id: str, capability: str) -> bool:
        unit = self.get(entity_id)
        return unit is not None and capability in unit.enabled

    def default_unit(self, device_key: str) -> XiaoduUnit | None:
        """Return the default unit of a device, if any."""
        device = self._by_key.get(device_key)
        return device.default_unit if device else None


def build_device_map(hass: HomeAssistant, options: dict[str, Any]) -> XiaoduDeviceMap:
    """Resolve the exposed device set from entry options.

    New-style options store ``CONF_DEVICES`` (device_key -> enabled caps,
    power implied). Legacy entity include/exclude options are applied as a
    migration: the previously exposed entities become devices with all
    capabilities enabled.
    """
    config = options.get(CONF_DEVICES)
    sync_areas = bool(options.get(CONF_SYNC_AREAS, False))
    states = list(hass.states.async_all())
    # Imported here so the module stays importable without a HA runtime
    # (the pure-logic tests load it standalone).
    from homeassistant.helpers import device_registry as dr  # noqa: PLC0415
    from homeassistant.helpers import entity_registry as er  # noqa: PLC0415
    from homeassistant.helpers import area_registry as ar  # noqa: PLC0415

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    area_registry = ar.async_get(hass)

    def device_of(entity_id: str) -> str | None:
        entry = entity_registry.async_get(entity_id)
        return entry.device_id if entry and entry.device_id else None

    def name_of(device_key: str) -> str | None:
        if device := device_registry.async_get(device_key):
            return device.name_by_user or device.name
        return None

    def area_name_of(device_key: str) -> str | None:
        device = device_registry.async_get(device_key)
        if device is None or not device.area_id:
            return None
        area = area_registry.async_get_area(device.area_id)
        return area.name if area else None

    def metadata_of(device_key: str) -> dict[str, str] | None:
        device = device_registry.async_get(device_key)
        if device is None:
            return None
        return {
            "manufacturer": device.manufacturer or "",
            "model": device.model or "",
        }

    if config is None:
        legacy = EntityFilter.from_lists(
            options.get(CONF_ENTITY_INCLUDE),
            options.get(CONF_ENTITY_EXCLUDE),
        )
        states = [s for s in states if legacy.allowed(s.entity_id)]

    return XiaoduDeviceMap(
        build_devices_from_entities(
            states,
            device_of,
            name_of,
            config,
            area_name_of=area_name_of,
            metadata_of=metadata_of,
        ),
        sync_areas=sync_areas,
    )


def summarize_devices(devices: XiaoduDeviceMap) -> str:
    """Return a short Chinese summary of the exposed devices."""
    items = devices.devices()
    if not items:
        return "0 台设备（当前没有可暴露的设备）"
    parts: list[str] = []
    for device in items:
        for unit in device.units:
            labels = [CAP_LABELS[c] for c in unit.enabled if c in CAP_LABELS]
            if not labels:
                continue
            label = device.name if unit.is_default else unit.name
            parts.append(f"{label}（{'、'.join(labels)}）")
    text = "、".join(parts[:6])
    if len(parts) > 6:
        text += " 等"
    return f"{len(items)} 台设备：{text}"
