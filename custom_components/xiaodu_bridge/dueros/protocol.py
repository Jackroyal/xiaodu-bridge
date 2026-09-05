"""DuerOS Connected Home protocol dispatcher.

This module is deliberately thin: it knows the protocol envelope (header /
payload, namespaces, response/error naming) but not domain specifics. All
domain behavior lives in the semantic model (``model.py`` / ``composers.py`` /
``profiles.py`` / ``defaults.py``); all constants in ``constants.py``. Adding
a device capability means extending the model, not this dispatcher.

The only runtime path is the DuerOS *semantic* model (``enhanced.py``):
Discovery / Query / Control all resolve against an ``EnhancedDeviceSet``.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from ..const import DATA_ENHANCED_DEVICES, DATA_STATE_REPORT_MANAGER, DATA_TIMER_MANAGER, DATA_VERSION, DOMAIN
from .enhanced import EnhancedDeviceSet
from .model import AttributeValue, DuerAction, ReadContext, WriteContext
from .constants import (
    ACTION_TIMING_TURN_OFF,
    ACTION_TIMING_TURN_ON,
    ACTION_TURN_OFF,
    ACTION_TURN_ON,
    ERROR_DEVICE_NOT_FOUND,
    ERROR_OFFLINE,
    ERROR_SERVICE,
    ERROR_UNSUPPORTED,
    NAMESPACE_CONTROL,
    NAMESPACE_DISCOVERY,
    NAMESPACE_QUERY,
)

_LOGGER = logging.getLogger(__name__)


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

def _clean_group_name(name: str) -> str:
    """Sanitize an area name into a DuerOS group name (<=20 chars)."""
    cleaned = re.sub(r"[^\w\u4e00-\u9fff -]", "", name).strip()
    return cleaned[:20]

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
    # Runtime version resolved once at setup via HA's integration loader and
    # stashed in hass.data. "0.0.0" can only appear if setup never injected
    # it (requests cannot be served before setup completes).
    app_version = hass.data.get(DOMAIN, {}).get(DATA_VERSION) or "0.0.0"
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
                "version": app_version,
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

def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def _redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of a DuerOS payload safe to log (credentials scrubbed)."""

    def _scrub(node: Any) -> Any:
        if isinstance(node, dict):
            return {
                key: "<redacted>" if key == "accessToken" else _scrub(value)
                for key, value in node.items()
            }
        if isinstance(node, list):
            return [_scrub(value) for value in node]
        return node

    return _scrub(payload)

def _build_and_cache_enhanced(hass: HomeAssistant) -> EnhancedDeviceSet | None:
    """Build the enhanced device set from the hub entry and cache it.

    Failures are logged and surfaced as ``None``: the request path must never
    500, but a silent empty device list used to make build errors invisible
    (DuerOS just answered "device not found"), so they are now logged loudly.
    """
    try:
        from .enhanced import build_enhanced_for_hass  # noqa: PLC0415

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            return None
        built = build_enhanced_for_hass(hass, entries[0])
        hass.data.setdefault(DOMAIN, {})[DATA_ENHANCED_DEVICES] = built
        return built
    except Exception:  # noqa: BLE001 - never break the request path
        _LOGGER.exception(
            "Building the Xiaodu device set failed; DuerOS requests are "
            "answered as if no devices were exposed"
        )
        return None


def _get_enhanced(hass: HomeAssistant) -> EnhancedDeviceSet | None:
    """Return the enhanced device set, building it on demand if needed.

    The set is the only runtime model. It is cached in ``hass.data`` and the
    cache is invalidated (debounced) whenever the entity/device/area registries
    or the entity set change (see the integration setup), so a lazy rebuild
    here reflects the current HA state. Discovery additionally forces a
    rebuild so a device-list refresh never serves a stale set.
    """
    cached = hass.data.get(DOMAIN, {}).get(DATA_ENHANCED_DEVICES)
    if cached is not None:
        return cached
    return _build_and_cache_enhanced(hass)

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
    _LOGGER.debug(
        "DuerOS payload: namespace=%s name=%s payload=%s",
        namespace,
        header.get("name", ""),
        _redact_payload(payload),
    )

    # Prefer the enhanced set passed by the caller (the runtime path); fall
    # back to the cached set in ``hass.data`` (on-demand build).
    enhanced = devices if isinstance(devices, EnhancedDeviceSet) else _get_enhanced(hass)

    if namespace == NAMESPACE_DISCOVERY:
        # Discovery is the moment Xiaodu refreshes its device list: rebuild
        # from the current HA state so devices added/removed/renamed since the
        # cache was built show up immediately, without waiting for (or relying
        # on) the debounced cache invalidation.
        fresh = _build_and_cache_enhanced(hass)
        if fresh is not None:
            enhanced = fresh

    if not enhanced:
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