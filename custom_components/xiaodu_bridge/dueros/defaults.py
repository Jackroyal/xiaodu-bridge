"""Generic (fallback) builder for simple devices.

Every HA physical device that does not match a declared device profile (YUBA,
CLOTHES_RACK, WASHING_MACHINE, SWEEPING_ROBOT, ...) is surfaced through this
builder. It maps the device's entities into one or more ``DuerDevice``
appliances using the per-domain capability composers, so the protocol layer
sees the same semantic model as the profile path (no legacy per-entity
handling).

A device with several independent control entities (e.g. a light and a plug on
the same physical device) yields one ``DuerDevice`` per appliance; read-only
sensor capabilities (temperature / humidity) are aggregated onto the device's
default appliance.
"""

from __future__ import annotations

from typing import Any

from .. import devices as device_mod
from .composers import (
    brightness_mapping,
    channel_mapping,
    climate_mode_mapping,
    climate_temperature_mapping,
    color_mapping,
    color_temperature_mapping,
    fan_speed_mapping,
    humidifier_mode_mapping,
    mute_mapping,
    pause_mapping,
    percentage_mapping,
    power_mapping,
    sensor_query_mapping,
    target_humidity_mapping,
    volume_mapping,
)
from .constants import (
    APPLIANCE_AIR_CONDITION,
    APPLIANCE_CURTAIN,
    APPLIANCE_FAN,
    APPLIANCE_HUMIDIFIER,
    APPLIANCE_LIGHT,
    APPLIANCE_SENSOR,
    APPLIANCE_SOCKET,
    APPLIANCE_SWITCH,
    APPLIANCE_TV_SET,
)
from .model import DeviceBuildContext, DuerDevice

# Appliance type for a known device class, overriding the domain default.
_CLASS_APPLIANCE = {
    device_mod.DEVICE_CLASS_SOCKET: APPLIANCE_SOCKET,
    device_mod.DEVICE_CLASS_CLOTHES_RACK: APPLIANCE_CURTAIN,
    device_mod.DEVICE_CLASS_YUBA: APPLIANCE_LIGHT,
}

_DOMAIN_APPLIANCE = {
    "light": APPLIANCE_LIGHT,
    "switch": APPLIANCE_SWITCH,
    "fan": APPLIANCE_FAN,
    "climate": APPLIANCE_AIR_CONDITION,
    "media_player": APPLIANCE_TV_SET,
    "cover": APPLIANCE_CURTAIN,
    "humidifier": APPLIANCE_HUMIDIFIER,
}


def _appliance_type(entity: Any, device_class: str) -> str:
    domain = getattr(entity, "domain", "")
    # A light is always a LIGHT appliance, even when the physical device is
    # otherwise classified (e.g. a 晾衣杆's light must not become a CURTAIN).
    if domain == "light":
        return APPLIANCE_LIGHT
    if domain == "switch" and device_class == device_mod.DEVICE_CLASS_SOCKET:
        return APPLIANCE_SOCKET
    if device_class in _CLASS_APPLIANCE and domain not in _DOMAIN_APPLIANCE:
        return _CLASS_APPLIANCE[device_class]
    return _DOMAIN_APPLIANCE.get(domain, APPLIANCE_SWITCH)


def _enabled(config: Any, caps: frozenset[str]) -> frozenset[str]:
    """Resolve the enabled capability subset for one entity.

    ``None`` or an empty list (candidate / default view) keeps every capability
    the entity has; a non-empty list filters to it (power always implied for
    control entities).
    """
    if config is None:
        return frozenset(caps)
    selected = set(config or ())
    if not selected:
        return frozenset(caps)
    out = selected & set(caps)
    if "power" in caps:
        out.add("power")
    return frozenset(out)


def _device_enabled(config: Any) -> frozenset[str] | None:
    """Device-level enabled capability set from a per-device CONF_DEVICES entry.

    The legacy/migration per-entity dict shape may list a capability under any
    of the device's entities (e.g. ``temperature`` ticked on the humidity
    sibling). Capability aggregation (sensors) must therefore honor the device
    union, not drop a capability because its *owning* entity is not the one the
    user selected it under. ``None``/empty entry keeps every capability
    (candidate / default view), mirroring :func:`_enabled`.
    """
    if config is None:
        return None
    if isinstance(config, dict):
        if not config:
            return None
        selected: set[str] = set()
        for caps in config.values():
            sel = set(caps or ())
            if not sel:
                return None  # any default-all entity -> device default-all
            selected |= sel
        return frozenset(selected)
    return None if not config else frozenset(config)


def _includes(config: Any, entity_id: str) -> tuple[bool, Any]:
    """Decide whether an entity is exposed and report its per-entity config.

    - ``config is None``: candidate view -> expose every entity, all caps.
    - ``config`` is a list: device-level selection -> expose every entity,
      filtered by the list.
    - ``config`` is a dict: per-entity selection (legacy/migration) -> expose
      only entities present in the dict, filtered by their list.
    """
    if config is None:
        return True, None
    if isinstance(config, dict):
        if entity_id in config:
            return True, config[entity_id]
        return False, None
    return True, config


def _entity_config(device_config: Any, entity_id: str) -> list[str] | None:
    """Return the per-entity capability list from a CONF_DEVICES entry (or None)."""
    if device_config is None:
        return None
    if isinstance(device_config, dict):
        val = device_config.get(entity_id)
        return list(val) if val is not None else None
    return list(device_config)


def _query_capabilities(states: list[Any]) -> dict[str, str]:
    """Aggregate read-only query capabilities (temperature/humidity) per entity."""
    out: dict[str, str] = {}
    for state in states:
        for cap in device_mod.derive_capabilities(state):
            if cap in device_mod.QUERY_CAPS:
                out.setdefault(cap, getattr(state, "entity_id", ""))
    return out


def _sensor_scale(state: Any) -> tuple[str, str, str]:
    """Return (scale/unit, legal, attribute_name) for a sensor query."""
    unit = str((state.attributes or {}).get("unit_of_measurement", "")).lower()
    device_class = str((state.attributes or {}).get("device_class", "")).lower()
    if "°f" in unit:
        return "FAHRENHEIT", "DOUBLE", "temperature"
    if device_class == "temperature" or "°c" in unit or "℃" in unit or unit == "c" or "temperature" in unit:
        return "CELSIUS", "DOUBLE", "temperature"
    if device_class == "humidity" or "humidity" in unit:
        return "%", "[0, 100]", "humidity"
    return "", "DOUBLE", ""


def _sensor_mapping(
    entity_id: str,
    capability: str,
    state: Any | None,
    appliance_types: tuple[str, ...],
) -> Any:
    unit_src, legal, attr_name = (
        _sensor_scale(state) if state is not None else ("", "DOUBLE", capability)
    )
    query_names = (
        ("GetTemperatureReadingRequest",) if capability == "temperature"
        else ("GetHumidityRequest",) if capability == "humidity"
        else ()
    )
    return sensor_query_mapping(
        entity_id=entity_id,
        attribute_name=attr_name or capability,
        capability_key=capability,
        appliance_types=appliance_types,
        unit=unit_src,
        legal=legal,
        query_names=query_names,
        scale=unit_src,
    )


def _reachable(ctx: DeviceBuildContext, entity_ids: set[str]) -> bool:
    for eid in entity_ids:
        state = ctx.find_state(eid)
        if state is not None and getattr(state, "state", "") != "unavailable":
            return True
    return False


def _sensor_device(
    ctx: DeviceBuildContext,
    query_entities: dict[str, str],
) -> DuerDevice | None:
    """Build a read-only SENSOR appliance from aggregated query capabilities."""
    device_enabled = _device_enabled(ctx.config)
    mappings = []
    entity_ids: set[str] = set()
    for capability, entity_id in query_entities.items():
        state = ctx.find_state(entity_id)
        if state is None:
            continue
        # query_entities already derives each capability from its owning
        # entity; only the device-level enablement gates aggregation.
        if device_enabled is not None and capability not in device_enabled:
            continue
        mappings.append(_sensor_mapping(entity_id, capability, state, (APPLIANCE_SENSOR,)))
        entity_ids.add(entity_id)
    if not mappings:
        return None
    primary = min(entity_ids) if entity_ids else ""
    return DuerDevice(
        device_id=primary,
        friendly_name=ctx.device_name,
        profile_key="SENSOR",
        primary_entity_id=primary,
        capabilities=tuple(mappings),
        is_reachable=_reachable(ctx, entity_ids),
        appliance_types=(APPLIANCE_SENSOR,),
    )


def _control_mappings(
    entity: Any,
    caps: frozenset[str],
    appliance_types: tuple[str, ...],
) -> list[Any]:
    domain = getattr(entity, "domain", "")
    entity_id = getattr(entity, "entity_id", "")
    out: list[Any] = []
    if "power" in caps:
        if domain == "cover":
            out.append(
                power_mapping(
                    domain="cover", entity_id=entity_id, appliance_types=appliance_types,
                    on_service="open_cover", off_service="close_cover",
                )
            )
        else:
            out.append(
                power_mapping(domain=domain, entity_id=entity_id, appliance_types=appliance_types)
            )
    if domain == "light":
        if "brightness" in caps:
            out.append(brightness_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "colorTemperature" in caps:
            out.append(color_temperature_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "color" in caps:
            out.append(color_mapping(entity_id=entity_id, appliance_types=appliance_types))
    elif domain == "fan" and "fanSpeed" in caps:
        out.append(fan_speed_mapping(entity_id=entity_id, appliance_types=appliance_types))
    elif domain == "climate":
        if "mode" in caps:
            out.append(climate_mode_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "targetTemperature" in caps:
            out.append(climate_temperature_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "fanSpeed" in caps:
            out.append(fan_speed_mapping(entity_id=entity_id, appliance_types=appliance_types, domain="climate"))
    elif domain == "media_player":
        if "volume" in caps:
            out.append(volume_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "mute" in caps:
            out.append(mute_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "channel" in caps:
            out.append(channel_mapping(entity_id=entity_id, appliance_types=appliance_types))
    elif domain == "cover":
        if "percentage" in caps:
            out.append(percentage_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "pause" in caps:
            out.append(pause_mapping(entity_id=entity_id, appliance_types=appliance_types, domain="cover"))
    elif domain == "humidifier":
        if "targetHumidity" in caps:
            out.append(target_humidity_mapping(entity_id=entity_id, appliance_types=appliance_types))
        if "mode" in caps:
            out.append(humidifier_mode_mapping(entity_id=entity_id, appliance_types=appliance_types))
    return out


def build_default_devices(ctx: DeviceBuildContext) -> list[DuerDevice]:
    """Build one or more DuerDevices for a device with no matching profile."""
    states = list(ctx.states or [])
    if not states:
        return []

    device_class = device_mod.classify_device(ctx.ha_device_id, states, None)
    control_entities = [
        s
        for s in states
        if getattr(s, "domain", "") in device_mod.EXPOSABLE_DOMAINS
        and getattr(s, "domain", "") != "sensor"
        and not device_mod._is_auxiliary(s)
    ]
    if device_class == device_mod.DEVICE_CLASS_YUBA:
        control_entities = [s for s in control_entities if device_mod._yuba_control_entity(s)]
    elif device_class == device_mod.DEVICE_CLASS_SOCKET:
        filtered = [s for s in control_entities if device_mod._socket_control_entity(s)]
        # Fall back to all non-auxiliary control entities when the main-power
        # switch marker is absent (e.g. a generic plug named ``switch.plug``).
        control_entities = filtered or control_entities

    query_entities = _query_capabilities(states)
    devices: list[DuerDevice] = []

    for entity in control_entities:
        entity_id = getattr(entity, "entity_id", "")
        include, per_entity = _includes(ctx.config, entity_id)
        if not include:
            continue
        caps = device_mod.derive_capabilities(entity)
        appliance_types = (_appliance_type(entity, device_class),)
        mappings = _control_mappings(entity, caps, appliance_types)
        if not mappings:
            continue
        enabled = _enabled(per_entity, caps)
        mappings = [m for m in mappings if m.key in enabled]
        if not mappings:
            continue
        devices.append(
            DuerDevice(
                device_id=entity_id,
                friendly_name=ctx.device_name,
                profile_key=getattr(entity, "domain", ""),
                primary_entity_id=entity_id,
                capabilities=tuple(mappings),
                is_reachable=_reachable(ctx, {entity_id}),
                appliance_types=appliance_types,
            )
        )

    if control_entities:
        # Attach read-only query caps onto the first (default) control appliance
        # so a control device with a sensor sibling stays on one appliance.
        if devices and query_entities:
            first = devices[0]
            added = []
            device_enabled = _device_enabled(ctx.config)
            for capability, entity_id in query_entities.items():
                state = ctx.find_state(entity_id)
                if state is None:
                    continue
                if device_enabled is not None and capability not in device_enabled:
                    continue
                added.append(_sensor_mapping(entity_id, capability, state, first.appliance_types))
            if added:
                devices[0] = DuerDevice(
                    device_id=first.device_id,
                    friendly_name=first.friendly_name,
                    profile_key=first.profile_key,
                    primary_entity_id=first.primary_entity_id,
                    capabilities=tuple(list(first.capabilities) + added),
                    is_reachable=first.is_reachable,
                    appliance_types=first.appliance_types,
                )
    else:
        sensor = _sensor_device(ctx, query_entities)
        if sensor is not None:
            devices.append(sensor)

    return devices


__all__ = ["build_default_devices"]
