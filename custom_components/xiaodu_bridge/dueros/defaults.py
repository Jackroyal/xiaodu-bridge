"""Generic (fallback) builder for simple devices.

Every HA physical device that does not match a declared device profile (YUBA,
CLOTHES_RACK, WASHING_MACHINE, SWEEPING_ROBOT, ...) is surfaced through this
builder. It maps the device's entities into one or more ``DuerDevice``
appliances using the per-domain capability composers, so the protocol layer
sees the same semantic model as the profile path.

A device with several independent control entities (e.g. a light and a plug on
the same physical device) yields one ``DuerDevice`` per appliance; read-only
sensor capabilities (temperature / humidity) are aggregated onto the device's
default appliance.

This builder is config-agnostic: it exposes every entity of the device with all
its capabilities. Per-device capability narrowing / hidden-entity filtering /
name overrides are applied by ``dueros.enhanced`` (``_filter_device`` and the
per-device object from ``dueros.device_config``), never here.
"""

from __future__ import annotations

from typing import Any

from .. import devices as device_mod
from .composers import (
    brightness_mapping,
    channel_mapping,
    climate_fan_speed_mapping,
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
from .model import DeviceBuildContext, DuerDevice, make_device_id

# Master control domains that own a whole physical unit: when present they
# collapse the device to the master entity and hide the settings/toggle
# siblings those integrations expose (see build_default_devices).
_MASTER_CONTROL_DOMAINS = ("climate", "humidifier")

# Appliance type for a known device class, overriding the domain default.
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
    return _DOMAIN_APPLIANCE.get(domain, APPLIANCE_SWITCH)


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


def _entity_appliance_id(
    ctx: DeviceBuildContext, kind: str, entity_id: str
) -> str:
    """Stable appliance id for a generic per-entity appliance.

    A real HA device (grouped under a device-registry id) yields a hashed id
    keyed on the device id plus the entity's rename-stable sub-identity, so
    renaming the entity does not recreate the DuerOS appliance. A lone
    *ungrouped* entity has no device-registry base (its group key is its own
    entity id), so there is nothing stable to anchor on — its id stays the
    entity id, and renaming it recreates the appliance.
    """
    if ctx.ha_device_id == entity_id:
        return entity_id
    return make_device_id(kind, ctx.ha_device_id, ctx.stable_sub(entity_id))


def _sensor_device(
    ctx: DeviceBuildContext,
    query_entities: dict[str, str],
) -> DuerDevice | None:
    """Build a read-only SENSOR appliance from aggregated query capabilities.

    The aggregate's device id is anchored on its *primary* member — the member
    with the smallest rename-stable sub-identity — so the id only guarantees
    stability across **renames of existing members** (renaming a member keeps
    its unique_id, hence its sub-identity). Adding or removing members is a
    different story: deleting the current primary, or adding a member whose
    sub-identity sorts before it, displaces the primary and therefore yields a
    new aggregate id. That is expected semantics, not a stability bug.
    """
    mappings = []
    entity_ids: set[str] = set()
    for capability, entity_id in query_entities.items():
        state = ctx.find_state(entity_id)
        if state is None:
            continue
        # Every query capability whose entity exists is aggregated; per-device
        # capability narrowing happens later in enhanced._filter_device.
        mappings.append(_sensor_mapping(entity_id, capability, state, (APPLIANCE_SENSOR,)))
        entity_ids.add(entity_id)
    if not mappings:
        return None
    # Deterministic aggregation order uses the *stable* member identities, so
    # renaming a member sensor does not reshuffle / re-identify the aggregate;
    # the entity_id tie-break keeps members with equal stable_sub fully ordered
    # across restarts (Python hash-randomises set iteration, not the sort key).
    members = sorted(entity_ids, key=lambda eid: (ctx.stable_sub(eid), eid))
    primary = members[0] if members else ""
    return DuerDevice(
        device_id=_entity_appliance_id(ctx, "SENSOR", primary),
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
            out.append(climate_fan_speed_mapping(entity_id=entity_id, appliance_types=appliance_types))
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
    if device_class == device_mod.DEVICE_CLASS_SOCKET:
        filtered = [s for s in control_entities if device_mod._socket_control_entity(s)]
        # Fall back to all non-auxiliary control entities when the main-power
        # switch marker is absent (e.g. a generic plug named ``switch.plug``).
        control_entities = filtered or control_entities
    elif any(
        getattr(s, "domain", "") in _MASTER_CONTROL_DOMAINS for s in control_entities
    ):
        # A device whose master is climate / humidifier (AC, fridge zone,
        # humidifier) is *one* appliance. Those integrations (Midea AC,
        # Mi Home humidifier, ...) split one physical unit into a master entity
        # plus many settings switches/fans (屏幕显示、电辅热、干燥、自清洁、新风、
        # 自动熄灯、调试 …) — exposing those as standalone SWITCH/FAN appliances
        # clutters DuerOS. Keep only the master-domain entity(ies).
        control_entities = [
            s
            for s in control_entities
            if getattr(s, "domain", "") in _MASTER_CONTROL_DOMAINS
        ]

    query_entities = _query_capabilities(states)
    devices: list[DuerDevice] = []

    for entity in control_entities:
        entity_id = getattr(entity, "entity_id", "")
        caps = device_mod.derive_capabilities(entity)
        appliance_types = (_appliance_type(entity, device_class),)
        mappings = _control_mappings(entity, caps, appliance_types)
        if not mappings:
            continue
        # Capability narrowing is centralized in enhanced._filter_device: every
        # control entity of an exposable device is built here with all its
        # capabilities, and the per-device ``caps`` object is applied afterwards.
        kind = getattr(entity, "domain", "")
        friendly = (getattr(entity, "attributes", None) or {}).get("friendly_name")
        # A single control entity keeps the device-registry name (e.g. 床头灯);
        # several control entities (e.g. a two-gang switch 筒灯/餐厅灯) surface
        # each under its own entity name instead of one shared device name.
        name = (
            ctx.device_name
            if len(control_entities) == 1
            else (friendly or ctx.device_name)
        )
        devices.append(
            DuerDevice(
                device_id=_entity_appliance_id(ctx, kind, entity_id),
                friendly_name=name,
                profile_key=kind,
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
            for capability, entity_id in query_entities.items():
                state = ctx.find_state(entity_id)
                if state is None:
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
