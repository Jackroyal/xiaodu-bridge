"""DuerOS Connected Home protocol dispatcher.

This module is deliberately thin: it knows the protocol envelope (header /
payload, namespaces, response/error naming) but not domain specifics. All
domain behavior lives in ``adapters.py``; all constants in ``constants.py``.
Adding a device capability means extending an adapter, not this dispatcher.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from ..devices import XiaoduDeviceMap, XiaoduUnit

from ..const import DATA_ENHANCED_DEVICES, DATA_STATE_REPORT_MANAGER, DATA_TIMER_MANAGER, DOMAIN
from ..devices import (
    CAP_BRIGHTNESS,
    CAP_CHANNEL,
    CAP_COLOR,
    CAP_COLOR_TEMPERATURE,
    CAP_CONTINUE,
    CAP_FAN_SPEED,
    CAP_HUMIDITY,
    CAP_MODE,
    CAP_PAUSE,
    CAP_MUTE,
    CAP_POWER,
    CAP_SUCTION,
    CAP_TEMPERATURE,
    CAP_TARGET_HUMIDITY,
    CAP_TARGET_TEMPERATURE,
    CAP_VOLUME,
    DEVICE_CLASS_CLOTHES_RACK,
    DEVICE_CLASS_SOCKET,
    DEVICE_CLASS_YUBA,
)
from .adapters import extra_attributes, get_adapter
from .enhanced import EnhancedDeviceSet
from .model import AttributeValue, DuerAction, ReadContext, WriteContext
from .constants import (
    APP_VERSION,
    ACTION_TIMING_TURN_OFF,
    ACTION_TIMING_TURN_ON,
    ACTION_TURN_OFF,
    ACTION_TURN_ON,
    APPLIANCE_CLOTHES_RACK,
    APPLIANCE_SOCKET,
    APPLIANCE_YUBA,
    ERROR_DEVICE_NOT_FOUND,
    ERROR_OFFLINE,
    ERROR_SERVICE,
    ERROR_UNSUPPORTED,
    NAMESPACE_CONTROL,
    NAMESPACE_DISCOVERY,
    NAMESPACE_QUERY,
)

_LOGGER = logging.getLogger(__name__)

# DuerOS action name -> platform-agnostic capability. Only capabilities that
# DuerOS can actually express live here; reserved model capabilities (e.g.
# CAP_PERCENTAGE) have no entry and are therefore never advertised.
ACTION_CAPABILITIES = {
    "turnOn": CAP_POWER,
    "turnOff": CAP_POWER,
    "timingTurnOn": CAP_POWER,
    "timingTurnOff": CAP_POWER,
    "setBrightnessPercentage": CAP_BRIGHTNESS,
    "setColorTemperature": CAP_COLOR_TEMPERATURE,
    "setColor": CAP_COLOR,
    "setVolume": CAP_VOLUME,
    "setVolumeMute": CAP_MUTE,
    "setTVChannel": CAP_CHANNEL,
    "setFanSpeed": CAP_FAN_SPEED,
    "setTemperature": CAP_TARGET_TEMPERATURE,
    "setMode": CAP_MODE,
    "unSetMode": CAP_MODE,
    "setSuction": CAP_SUCTION,
    "setHumidity": CAP_TARGET_HUMIDITY,
    "pause": CAP_PAUSE,
    "continue": CAP_CONTINUE,
}

# DuerOS query action name -> read-only capability.
QUERY_CAPABILITIES = {
    "GetTemperatureReadingRequest": CAP_TEMPERATURE,
    "GetHumidityRequest": CAP_HUMIDITY,
}

# Attribute name -> capability it belongs to (used to filter query/discovery
# attributes down to the enabled capability set). Attributes without an entry
# (e.g. connectivity) are structural and always reported.
_ATTRIBUTE_CAPABILITIES = {
    "turnOnState": CAP_POWER,
    "brightness": CAP_BRIGHTNESS,
    "colorTemperatureInKelvin": CAP_COLOR_TEMPERATURE,
    "color": CAP_COLOR,
    "volume": CAP_VOLUME,
    "muteState": CAP_MUTE,
    "channel": CAP_CHANNEL,
    "fanSpeed": CAP_FAN_SPEED,
    "temperature": CAP_TEMPERATURE,
    "humidity": CAP_HUMIDITY,
    "targetTemperature": CAP_TARGET_TEMPERATURE,
    "targetHumidity": CAP_TARGET_HUMIDITY,
    "mode": CAP_MODE,
    "suction": CAP_SUCTION,
}


def _respond(header: dict[str, Any], name: str, payload: dict[str, Any]) -> dict[str, Any]:
    response_header = dict(header)
    response_header["name"] = name
    return {"header": response_header, "payload": payload}


def _error_response(header: dict[str, Any], error_name: str) -> dict[str, Any]:
    response_header = dict(header)
    response_header["name"] = error_name
    return {"header": response_header, "payload": {}}


def _strip_request(name: str) -> str:
    """Turn ``TurnOnRequest`` into ``TurnOn`` (or return the name unchanged)."""
    if name.endswith("Request"):
        return name[: -len("Request")]
    return name


def _response_name(name: str) -> str:
    """Turn a query/control name into its response name."""
    if name.endswith("Request"):
        return name[: -len("Request")] + "Response"
    if name.endswith("Confirmation"):
        return name
    return f"{name}Response"


def _action_name(name: str) -> str:
    """Turn ``TurnOnRequest`` into the adapter action name ``turnOn``."""
    stripped = _strip_request(name)
    if not stripped:
        return ""
    return stripped[0].lower() + stripped[1:]


def _confirmation_name(name: str) -> str:
    """Turn ``TurnOnRequest`` into the control confirmation name."""
    if name.endswith("Request"):
        return name[: -len("Request")] + "Confirmation"
    return name


def _dueros_actions(unit: XiaoduUnit) -> list[str]:
    """Translate a unit's enabled capabilities into DuerOS action names."""
    return [
        action
        for action, capability in ACTION_CAPABILITIES.items()
        if capability in unit.enabled
    ]


def filtered_attributes(
    unit: XiaoduUnit, adapter: Any, state: Any
) -> list[dict[str, Any]]:
    """Return the attributes belonging to the unit's enabled capabilities.

    Structural attributes (e.g. connectivity) are always reported; capability
    attributes are filtered down to the enabled capability set. Read-only
    capabilities (temperature / humidity) are selectable like any other.
    """
    return _filter_attribute_list(unit, adapter.query_attributes(state))


def _filter_attribute_list(
    unit: XiaoduUnit, attributes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Filter pre-built attribute objects down to the enabled capability set."""
    filtered = []
    for attribute in attributes:
        capability = _ATTRIBUTE_CAPABILITIES.get(attribute.get("name"))
        if capability is None or capability in unit.enabled:
            filtered.append(attribute)
    return filtered


def _clean_group_name(name: str) -> str:
    """Sanitize an area name into a DuerOS group name (<=20 chars)."""
    cleaned = re.sub(r"[^\w\u4e00-\u9fff -]", "", name).strip()
    return cleaned[:20]


def _discovery_groups(
    devices: XiaoduDeviceMap, emitted_ids: set[str]
) -> list[dict[str, Any]]:
    """Build ``discoveredGroups`` from HA areas (experimental sync_areas).

    Only devices that actually appear in ``discoveredAppliances`` are added to
    a group; the DuerOS protocol requires every ``applianceId`` in a group to
    be a discovered appliance id.
    """
    if not devices.sync_areas:
        return []
    by_area: dict[str, list[str]] = {}
    for device in devices.devices():
        if not device.area_name:
            continue
        unit_ids = [u.entity_id for u in device.units if u.entity_id in emitted_ids]
        if unit_ids:
            by_area.setdefault(device.area_name, []).extend(unit_ids)
    groups: list[dict[str, Any]] = []
    for area_name in sorted(by_area):
        group_name = _clean_group_name(area_name)
        if not group_name:
            continue
        groups.append(
            {
                "groupName": group_name,
                "applianceIds": by_area[area_name][:50],
            }
        )
        if len(groups) >= 10:
            break
    return groups




# --- enhanced (device-center) semantic model dispatch -------------------------

def _enhanced_read_ctx(hass: Any, device: Any, mapping: Any) -> ReadContext:
    """Resolve a capability mapping's bindings into role -> state."""
    entities: dict[str, Any] = {}
    for binding in mapping.bindings:
        state = hass.states.get(binding.entity_id)
        if state is not None:
            entities[binding.role] = state
    return ReadContext(hass=hass, device=device, entities=entities)


def _enhanced_attribute_values(hass: Any, device: Any, only_mapping: Any = None) -> list[dict[str, Any]]:
    """Current attributes (serialized) for a DuerDevice, optionally one mapping."""
    values: list[dict[str, Any]] = []
    for mapping in device.capabilities:
        if only_mapping is not None and mapping is not only_mapping:
            continue
        attr = mapping.read(_enhanced_read_ctx(hass, device, mapping))
        if attr is not None:
            values.append(attr.to_dict())
    return values


def _enhanced_groups(enhanced: Any) -> list[dict[str, Any]]:
    """Build ``discoveredGroups`` from HA areas when sync_areas is enabled."""
    if not getattr(enhanced, "sync_areas", False):
        return []
    by_area: dict[str, list[str]] = {}
    for device in enhanced.all():
        area = enhanced.area(device.device_id)
        if area:
            by_area.setdefault(area, []).append(device.device_id)
    groups: list[dict[str, Any]] = []
    for area_name in sorted(by_area):
        group_name = _clean_group_name(area_name)
        if not group_name:
            continue
        groups.append({"groupName": group_name, "applianceIds": by_area[area_name][:50]})
        if len(groups) >= 10:
            break
    return groups


def _enhanced_discovery(hass: Any, enhanced: Any) -> list[dict[str, Any]]:
    """Build the ``discoveredAppliances`` entries for enhanced devices."""
    appliances: list[dict[str, Any]] = []
    for device in enhanced.all():
        attrs = _enhanced_attribute_values(hass, device)[:10]
        appliances.append(
            {
                "applianceId": device.device_id,
                "friendlyName": device.friendly_name,
                "friendlyDescription": device.friendly_name,
                "additionalApplianceDetails": {},
                "applianceTypes": list(device.appliance_types or ()),
                "isReachable": device.is_reachable,
                "manufacturerName": "Home Assistant",
                "modelName": device.profile_key,
                "version": APP_VERSION,
                "actions": device.actions(),
                "attributes": attrs,
            }
        )
    return appliances


async def _enhanced_control(
    hass: Any, enhanced: Any, header: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    appliance = payload.get("appliance") or {}
    device = enhanced.resolve(str(appliance.get("applianceId", "")))
    if device is None:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)

    action = _action_name(str(header.get("name", "")))
    found = device.find_action(action)
    if found is None:
        return _error_response(header, ERROR_UNSUPPORTED)
    mapping, dueros_action = found

    state = hass.states.get(device.primary_entity_id)
    if state is not None and state.state == "unavailable":
        return _error_response(header, ERROR_OFFLINE)

    write_ctx = WriteContext(
        hass=hass,
        device=device,
        entities=_enhanced_read_ctx(hass, device, mapping).entities,
        action=dueros_action,
        payload=payload,
    )
    calls = mapping.write(write_ctx)
    if calls is None:
        return _error_response(header, ERROR_UNSUPPORTED)

    for call in calls:
        target = call.target_entity_id or device.primary_entity_id
        service_data = {**call.data, "entity_id": target}
        try:
            await hass.services.async_call(call.domain, call.service, service_data, blocking=True)
        except Exception as err:  # noqa: BLE001 - report as driver error
            _LOGGER.error("Xiaodu enhanced control failed for %s: %s", device.device_id, err)
            return _error_response(header, ERROR_SERVICE)

    # The confirmation message below already carries the fresh attributes back
    # to DuerOS; suppress the redundant changereport for this appliance.
    report_manager = hass.data.get(DOMAIN, {}).get(DATA_STATE_REPORT_MANAGER)
    if report_manager is not None:
        report_manager.mark_confirmed(device.device_id)

    return _respond(
        header,
        _confirmation_name(str(header.get("name", ""))),
        {"attributes": _enhanced_attribute_values(hass, device)},
    )


def _enhanced_query(
    hass: Any, enhanced: Any, header: dict[str, Any], payload: dict[str, Any]
) -> dict[str, Any]:
    appliance = payload.get("appliance") or {}
    device = enhanced.resolve(str(appliance.get("applianceId", "")))
    if device is None:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)

    query_name = str(header.get("name", ""))
    mapping = device.find_query_capability(query_name)
    if mapping is None:
        # A query for a specific reading (temperature / humidity) that the
        # device does not support is an error, not a generic attribute dump.
        if query_name in ("GetTemperatureReadingRequest", "GetHumidityRequest"):
            return _error_response(header, ERROR_UNSUPPORTED)
        # Generic query: answer with the full attribute set, like discovery.
        return _respond(
            header, _response_name(query_name), {"attributes": _enhanced_attribute_values(hass, device)}
        )

    ctx = _enhanced_read_ctx(hass, device, mapping)
    result = mapping.query(ctx, query_name)
    if result is None:
        return _error_response(header, ERROR_UNSUPPORTED)

    if query_name == "GetTemperatureReadingRequest":
        temp = result if isinstance(result, AttributeValue) else next(
            (a for a in result if getattr(a, "name", "") == "temperature"), None
        )
        if temp is None:
            return _error_response(header, ERROR_UNSUPPORTED)
        return _respond(
            header,
            _response_name(query_name),
            {
                "temperatureReading": {"value": temp.value, "scale": temp.scale},
                "applianceResponseTimestamp": "",
            },
        )

    if isinstance(result, AttributeValue):
        attributes = [result.to_dict()]
    else:
        attributes = [a.to_dict() for a in (result or ())]
    return _respond(header, _response_name(query_name), {"attributes": attributes})


def _discovery(
    hass: HomeAssistant,
    devices: XiaoduDeviceMap,
    header: dict[str, Any],
    claimed_entity_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    appliances: list[dict[str, Any]] = []
    for device in devices.devices():
        for unit in device.units:
            if unit.entity_id in claimed_entity_ids:
                continue  # handled by the enhanced semantic model instead
            if not unit.enabled:
                continue  # unit not selected in the options
            state = hass.states.get(unit.entity_id)
            if state is None:
                continue
            adapter = get_adapter(state.domain, unit.device_class)
            if adapter is None:
                continue
            appliance = adapter.build_appliance(state, unit=unit, device=device)
            if appliance is None:
                continue
            # The default unit keeps the device registry name (authoritative,
            # survives renames); extra units use their entity name.
            name = device.name if unit.is_default else unit.name
            appliance["friendlyName"] = name
            appliance["friendlyDescription"] = name
            appliance["actions"] = _dueros_actions(unit)
            # Classified devices override the domain's default appliance type
            # (晾衣杆 -> CLOTHES_RACK, 浴霸 -> YUBA, 插座 -> SOCKET).
            if unit.device_class == DEVICE_CLASS_CLOTHES_RACK:
                appliance["applianceTypes"] = [APPLIANCE_CLOTHES_RACK]
            elif unit.device_class == DEVICE_CLASS_YUBA:
                appliance["applianceTypes"] = [APPLIANCE_YUBA]
            elif unit.device_class == DEVICE_CLASS_SOCKET:
                appliance["applianceTypes"] = [APPLIANCE_SOCKET]
            attributes = filtered_attributes(unit, adapter, state)
            # Aggregate read-only attributes from sibling entities onto the
            # default unit (e.g. the humidity entity of a 温湿度计 whose
            # default unit is temperature).
            for capability, entity_id in unit.query_entities.items():
                if capability not in unit.enabled or entity_id == unit.entity_id:
                    continue
                sibling_state = hass.states.get(entity_id)
                if sibling_state is None:
                    continue
                sibling_adapter = get_adapter(sibling_state.domain)
                if sibling_adapter is None:
                    continue
                attributes.extend(
                    filtered_attributes(unit, sibling_adapter, sibling_state)
                )
            # Device-level structural attributes (YUBA mode / target temp).
            attributes.extend(_filter_attribute_list(unit, extra_attributes(hass, unit, device)))
            appliance["attributes"] = attributes
            appliances.append(appliance)
    emitted_ids = {a["applianceId"] for a in appliances}
    return _respond(
        header,
        "DiscoverAppliancesResponse",
        {
            "discoveredAppliances": appliances,
            "discoveredGroups": _discovery_groups(devices, emitted_ids),
        },
    )


async def _control(
    hass: HomeAssistant,
    devices: XiaoduDeviceMap,
    header: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    appliance = payload.get("appliance") or {}
    entity_id = appliance.get("applianceId", "")
    action = _action_name(str(header.get("name", "")))

    unit = devices.get(entity_id)
    if not entity_id or unit is None:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)

    capability = ACTION_CAPABILITIES.get(action)
    if capability is None or capability not in unit.enabled:
        return _error_response(header, ERROR_UNSUPPORTED)

    state = hass.states.get(entity_id)
    if state is None:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)
    if state.state == "unavailable":
        return _error_response(header, ERROR_OFFLINE)

    adapter = get_adapter(state.domain, unit.device_class)
    if adapter is None:
        return _error_response(header, ERROR_UNSUPPORTED)

    if action in (ACTION_TIMING_TURN_ON, ACTION_TIMING_TURN_OFF):
        return await _timing_control(
            hass, state, adapter, header, action, payload, entity_id
        )

    device = devices.device_for_entity(entity_id)
    call = adapter.service_call(state, action, payload, unit=unit, device=device)
    if call is None:
        return _error_response(header, ERROR_UNSUPPORTED)

    # The confirmation below already carries the fresh attributes back to
    # DuerOS; suppress the redundant changereport for this unit so a voice
    # command does not trigger an extra ReportState round trip.
    report_manager = hass.data.get(DOMAIN, {}).get(DATA_STATE_REPORT_MANAGER)
    if report_manager is not None:
        report_manager.mark_confirmed(entity_id)

    calls = call if isinstance(call, list) else [call]
    for domain, service, data in calls:
        # ``data`` may carry an explicit entity_id to target a sibling entity
        # (e.g. a YUBA mode targets the heating switch, not the master light).
        service_data = {**data, "entity_id": data.get("entity_id", entity_id)}
        try:
            await hass.services.async_call(domain, service, service_data, blocking=True)
        except Exception as err:  # noqa: BLE001 - report as driver error
            _LOGGER.error("Xiaodu control failed for %s: %s", entity_id, err)
            return _error_response(header, ERROR_SERVICE)

    updated = hass.states.get(entity_id)
    attributes = filtered_attributes(unit, adapter, updated) if updated else []
    attributes.extend(_filter_attribute_list(unit, extra_attributes(hass, unit, device)))
    return _respond(
        header,
        _confirmation_name(str(header.get("name", ""))),
        {"attributes": attributes},
    )


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


async def _timing_control(
    hass: HomeAssistant,
    state: Any,
    adapter: Any,
    header: dict[str, Any],
    action: str,
    payload: dict[str, Any],
    entity_id: str,
) -> dict[str, Any]:
    """Handle timingTurnOn / timingTurnOff via HA's persisted timer manager.

    The timestamp is an absolute epoch in seconds (per the Xiaodu protocol).
    The call is scheduled with HA's own ``async_track_point_in_utc_time`` and
    persisted in HA storage, so a core restart re-arms pending timers instead
    of cancelling them.
    """
    timestamp = _to_float((payload.get("timestamp") or {}).get("value"))
    if timestamp is None or timestamp <= 0:
        return _error_response(header, ERROR_UNSUPPORTED)
    base_action = ACTION_TURN_ON if action == ACTION_TIMING_TURN_ON else ACTION_TURN_OFF
    call = adapter.service_call(state, base_action, {})
    if call is None:
        return _error_response(header, ERROR_UNSUPPORTED)
    domain, service, data = call

    # Imported lazily so the pure-logic protocol tests (which inject a fake
    # manager into ``hass.data``) do not need a Home Assistant runtime.
    data_by_domain = hass.data.setdefault(DOMAIN, {})
    manager = data_by_domain.get(DATA_TIMER_MANAGER)
    if manager is None:
        from ..timers import TimedServiceManager  # noqa: PLC0415

        manager = TimedServiceManager(hass)
        data_by_domain[DATA_TIMER_MANAGER] = manager
        await manager.async_load()
    await manager.schedule(domain, service, {**data, "entity_id": entity_id}, timestamp)
    return _respond(
        header,
        _confirmation_name(str(header.get("name", ""))),
        {"attributes": []},
    )


def _query(
    hass: HomeAssistant,
    devices: XiaoduDeviceMap,
    header: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    appliance = payload.get("appliance") or {}
    entity_id = appliance.get("applianceId", "")
    action = str(header.get("name", ""))

    unit = devices.get(entity_id)
    if not entity_id or unit is None:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)

    capability = QUERY_CAPABILITIES.get(action)
    if capability is not None and capability not in unit.enabled:
        return _error_response(header, ERROR_UNSUPPORTED)

    # Read-only capabilities may live on a sibling entity of the default unit
    # (e.g. humidity on a 温湿度计 whose default unit is temperature).
    target_entity = entity_id
    if capability and capability in unit.query_entities:
        target_entity = unit.query_entities[capability]
    state = hass.states.get(target_entity)
    if state is None:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)

    adapter = get_adapter(state.domain, unit.device_class)
    if adapter is None:
        return _error_response(header, ERROR_UNSUPPORTED)

    attributes = filtered_attributes(unit, adapter, state)
    # Aggregate read-only attributes from sibling entities onto the requested
    # unit (e.g. the humidity entity of a 温湿度计 whose default unit is
    # temperature) so ReportStateRequest / generic queries answer with the
    # full attribute set, exactly like discovery does.
    seen_entities = {target_entity}
    for capability, sibling_entity in unit.query_entities.items():
        if capability not in unit.enabled or sibling_entity in seen_entities:
            continue
        seen_entities.add(sibling_entity)
        sibling_state = hass.states.get(sibling_entity)
        if sibling_state is None:
            continue
        sibling_adapter = get_adapter(sibling_state.domain)
        if sibling_adapter is None:
            continue
        attributes.extend(filtered_attributes(unit, sibling_adapter, sibling_state))
    device = devices.device_for_entity(entity_id)
    attributes.extend(_filter_attribute_list(unit, extra_attributes(hass, unit, device)))

    if action == "GetTemperatureReadingRequest":
        temperature = next((a for a in attributes if a["name"] == "temperature"), None)
        if temperature is None:
            return _error_response(header, ERROR_UNSUPPORTED)
        return _respond(
            header,
            _response_name(action),
            {
                "temperatureReading": {
                    "value": temperature["value"],
                    "scale": temperature["scale"],
                },
                "applianceResponseTimestamp": "",
            },
        )

    if action == "GetHumidityRequest":
        humidity = next((a for a in attributes if a["name"] == "humidity"), None)
        if humidity is None:
            return _error_response(header, ERROR_UNSUPPORTED)
        return _respond(header, _response_name(action), {"attributes": [humidity]})

    # Generic query: report the current attribute values.
    return _respond(header, _response_name(action), {"attributes": attributes})




def _get_enhanced(hass: HomeAssistant) -> EnhancedDeviceSet | None:
    """Return the enhanced device set, building it on demand if needed.

    The set is the only runtime model; it is built on demand from the current
    HA state / device profiles so the device-center path is always consulted.
    """
    try:
        cached = hass.data.get(DOMAIN, {}).get(DATA_ENHANCED_DEVICES)
        if cached is not None:
            return cached
        from .enhanced import build_enhanced_for_hass  # noqa: PLC0415

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return None
        built = build_enhanced_for_hass(hass, entries[0])
        hass.data.setdefault(DOMAIN, {})[DATA_ENHANCED_DEVICES] = built
        return built
    except Exception:  # noqa: BLE001 - never break the request path
        return None


async def _enhanced_timing_control(
    hass: HomeAssistant,
    device: Any,
    header: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Schedule a timingTurnOn / timingTurnOff via HA's persisted timer manager."""
    timestamp = _to_float((payload.get("timestamp") or {}).get("value"))
    if timestamp is None or timestamp <= 0:
        return _error_response(header, ERROR_UNSUPPORTED)
    action = _action_name(str(header.get("name", "")))
    base_action = ACTION_TURN_ON if action == ACTION_TIMING_TURN_ON else ACTION_TURN_OFF
    found = device.find_action(base_action)
    if found is None:
        return _error_response(header, ERROR_UNSUPPORTED)
    mapping, dueros_action = found
    write_ctx = WriteContext(
        hass=hass,
        device=device,
        entities=_enhanced_read_ctx(hass, device, mapping).entities,
        action=DuerAction(base_action, mapping.key),
        payload={},
    )
    calls = mapping.write(write_ctx)
    if not calls:
        return _error_response(header, ERROR_UNSUPPORTED)
    call = calls[0]
    target = call.target_entity_id or device.primary_entity_id

    data_by_domain = hass.data.setdefault(DOMAIN, {})
    manager = data_by_domain.get(DATA_TIMER_MANAGER)
    if manager is None:
        from ..timers import TimedServiceManager  # noqa: PLC0415

        manager = TimedServiceManager(hass)
        data_by_domain[DATA_TIMER_MANAGER] = manager
        await manager.async_load()
    await manager.schedule(
        call.domain, call.service, {**call.data, "entity_id": target}, timestamp
    )
    return _respond(
        header,
        _confirmation_name(str(header.get("name", ""))),
        {"attributes": []},
    )


async def handle_request(
    hass: HomeAssistant, devices: Any, data: dict[str, Any]
) -> dict[str, Any]:
    """Dispatch a DuerOS smart-home request through the DuerOS semantic model.

    ``devices`` is kept for signature compatibility (it may be an
    ``EnhancedDeviceSet``); the authoritative source is the enhanced set cached
    in ``hass.data`` (or built on demand by ``_get_enhanced``). The legacy
    per-entity path is no longer used by the dispatcher.
    """
    header = data.get("header") or {}
    payload = data.get("payload") or {}
    namespace = header.get("namespace", "")
    message_id = header.get("messageId", "")

    _LOGGER.debug(
        "DuerOS request: namespace=%s name=%s messageId=%s",
        namespace,
        header.get("name", ""),
        message_id,
    )

    # Prefer the enhanced set passed by the caller (the runtime path); fall
    # back to the cached set in ``hass.data`` (on-demand build).
    enhanced = devices if isinstance(devices, EnhancedDeviceSet) else _get_enhanced(hass)
    has_enhanced = bool(enhanced)
    if not has_enhanced:
        return _error_response(header, ERROR_DEVICE_NOT_FOUND)

    appliance_id = str(payload.get("appliance", {}).get("applianceId", ""))

    if namespace == NAMESPACE_DISCOVERY:
        return _respond(
            header,
            "DiscoverAppliancesResponse",
            {
                "discoveredAppliances": _enhanced_discovery(hass, enhanced),
                "discoveredGroups": _enhanced_groups(enhanced),
            },
        )
    if namespace == NAMESPACE_CONTROL:
        device = enhanced.resolve(appliance_id)
        if device is None:
            return _error_response(header, ERROR_DEVICE_NOT_FOUND)
        action = _action_name(str(header.get("name", "")))
        if action in (ACTION_TIMING_TURN_ON, ACTION_TIMING_TURN_OFF):
            return await _enhanced_timing_control(hass, device, header, payload)
        return await _enhanced_control(hass, enhanced, header, payload)
    if namespace == NAMESPACE_QUERY:
        device = enhanced.resolve(appliance_id)
        if device is None:
            return _error_response(header, ERROR_DEVICE_NOT_FOUND)
        return _enhanced_query(hass, enhanced, header, payload)
    return _error_response(header, ERROR_UNSUPPORTED)
