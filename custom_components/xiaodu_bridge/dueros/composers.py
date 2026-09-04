"""Reusable CapabilityMapping composers.

A composer is a *declarative* factory: a device profile fills in its entities and
semantic roles, and the composer returns a ready ``CapabilityMapping`` with the
``read`` / ``write`` / ``query`` / ``change_report`` callbacks wired up. This keeps
the protocol layer free of device-type ``if`` branches.

These are pure logic (no Home Assistant runtime imports) so they can be unit
tested with fake ``State`` objects.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from .model import (
    CAP_KIND_CONTROL,
    CAP_KIND_QUERY,
    AttributeValue,
    CapabilityMapping,
    DuerAction,
    DuerAttribute,
    DuerCapability,
    EntityBinding,
    ReadContext,
    ServiceCall,
    WriteContext,
    make_attribute,
)
from .constants import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMPERATURE,
    ATTR_FAN_SPEED,
    ATTR_HUMIDITY,
    ATTR_MODE,
    ATTR_PAUSE_STATE,
    ATTR_PERCENTAGE,
    ATTR_SUCTION,
    ATTR_TARGET_HUMIDITY,
    ATTR_TARGET_TEMPERATURE,
    ATTR_TEMPERATURE,
    ATTR_TURN_ON_STATE,
    ATTR_WARMTH_LEVEL,
    ATTR_COLOR,
    ATTR_VOLUME,
    ATTR_CHANNEL,
    ATTR_MUTE_STATE,
    ATTR_WATER_LEVEL,
    ACTION_CONTINUE,
    ACTION_DECREMENT_FAN_SPEED,
    ACTION_DECREMENT_TEMPERATURE,
    ACTION_INCREMENT_FAN_SPEED,
    ACTION_INCREMENT_TEMPERATURE,
    ACTION_PAUSE,
    ACTION_SET_FAN_SPEED,
    ACTION_SET_GEAR,
    ACTION_SET_HUMIDITY,
    ACTION_SET_MODE,
    ACTION_SET_SUCTION,
    ACTION_SET_TEMPERATURE,
    ACTION_SET_WATER_LEVEL,
    ACTION_SET_BRIGHTNESS,
    ACTION_SET_COLOR,
    ACTION_SET_COLOR_TEMPERATURE,
    ACTION_SET_VOLUME,
    ACTION_SET_VOLUME_MUTE,
    ACTION_SET_TV_CHANNEL,
    ACTION_TURN_OFF,
    ACTION_TURN_ON,
    ACTION_UNSET_MODE,
)


# --- value helpers -----------------------------------------------------------

def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _payload_value(payload: dict[str, Any], key: str) -> Any:
    """Extract a scalar from the DuerOS payload ``{key: {"value": ...}}`` form."""
    node = payload.get(key)
    if isinstance(node, dict):
        return node.get("value")
    return node


def _payload_number(payload: dict[str, Any], *keys: str) -> float | None:
    """Return the first numeric payload value found under any of ``keys``.

    The DuerOS incremental payloads use ``{deltaTemperature: {value: 1.0}}``
    style objects; accepting several aliases keeps the handler robust until the
    exact field name is confirmed by a captured request.
    """
    for key in keys:
        value = _num(_payload_value(payload, key))
        if value is not None:
            return value
    return None


def _temperature_target_unit(hass: Any) -> str:
    """The temperature unit Home Assistant is configured to display.

    Read from ``hass.config.units.temperature_unit`` (the ``UnitSystem``
    HA core exposes); returns ``""`` when unavailable so callers fall back to
    the entity's own unit (e.g. in standalone tests without a HA runtime).
    """
    units = getattr(getattr(hass, "config", None), "units", None)
    return getattr(units, "temperature_unit", "") if units is not None else ""


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a temperature value between °C and °F (no HA runtime import).

    Kept to the degree-symbol forms HA uses (``°C`` / ``°F``); anything else
    (e.g. ``℃``) passes through unchanged — the numeric value already matches
    the token reported by :func:`_sensor_scale` then.
    """
    f = (from_unit or "").lower()
    t = (to_unit or "").lower()
    if not f or not t or f == t:
        return value
    if "f" in f and "c" in t:
        return round((value - 32) * 5 / 9, 1)
    if "c" in f and "f" in t:
        return round(value * 9 / 5 + 32, 1)
    return value


def is_powered_on(state: Any) -> bool:
    """Return True when a HA entity is considered powered-on."""
    if state.domain == "climate":
        # Modern HA exposes the hvac mode as the entity *state* (off / heat /
        # cool / ...), not necessarily as an ``hvac_mode`` attribute. Trust the
        # state first so an off AC is not reported ON just because the
        # attribute is absent (Midea / xiaomi ACs expose no hvac_mode attr).
        mode = str(
            getattr(state, "state", "")
            or (state.attributes or {}).get("hvac_mode")
            or ""
        ).lower()
        return mode not in ("", "off", "unavailable", "unknown")
    if state.domain == "cover":
        return state.state in ("open", "opening")
    return state.state == "on"


def _turn_on_state_attr(value: bool) -> AttributeValue:
    return make_attribute(ATTR_TURN_ON_STATE, "ON" if value else "OFF", legal="(ON, OFF)")


def _connectivity_attr(state: Any) -> AttributeValue:
    reachable = state.state != "unavailable"
    return make_attribute(
        "connectivity",
        "REACHABLE" if reachable else "UNREACHABLE",
        legal="(UNREACHABLE, REACHABLE)",
    )


# --- composers ---------------------------------------------------------------

def power_mapping(
    *,
    domain: str,
    entity_id: str,
    appliance_types: tuple[str, ...],
    on_service: str = "turn_on",
    off_service: str = "turn_off",
    capability_key: str = "power",
    actions: tuple[str, ...] = (ACTION_TURN_ON, ACTION_TURN_OFF),
    power_predicate: Callable[[Any], bool] | None = None,
    action_calls: dict[str, tuple[str, str, dict[str, Any]]] | None = None,
) -> CapabilityMapping:
    """Single on/off entity -> ``power`` (turnOnState)."""
    cap = DuerCapability(
        capability_key,
        "开关",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_TURN_ON_STATE, "string", legal="(ON, OFF)"),
                    DuerAttribute("connectivity", "string", legal="(UNREACHABLE, REACHABLE)")),
        actions=tuple(DuerAction(a, capability_key) for a in actions),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities["power"]
        on = power_predicate(state) if power_predicate is not None else is_powered_on(state)
        return _turn_on_state_attr(on)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name == ACTION_TURN_ON:
            return [ServiceCall(domain, on_service, {}, entity_id)]
        if ctx.action.name == ACTION_TURN_OFF:
            return [ServiceCall(domain, off_service, {}, entity_id)]
        if action_calls and ctx.action.name in action_calls:
            d, s, data = action_calls[ctx.action.name]
            return [ServiceCall(d, s, dict(data), entity_id)]
        return None

    return CapabilityMapping(
        cap, (EntityBinding(entity_id, "power"),), read=read, write=write
    )


def mode_switches_mapping(
    *,
    modes: Iterable[tuple[str, str, str]],
    appliance_types: tuple[str, ...],
    capability_key: str = "mode",
    domain: str = "switch",
    service_on: str = "turn_on",
    service_off: str = "turn_off",
    exclusive: bool = False,
) -> CapabilityMapping:
    """N switch entities synthesize a ``mode`` (1 capability -> N entities).

    ``modes`` is a sequence of ``(mode_value, role, entity_id)``. The current
    mode is whichever bound entity is ``on``; if multiple are on the first wins
    (or ``exclusive`` controls whether setting one turns the others off).
    """
    mode_list = list(modes)
    legal = "(" + ", ".join(m for m, _, _ in mode_list) + ")"
    actions = (
        DuerAction(ACTION_SET_MODE, capability_key, "mode", fanout=exclusive),
        DuerAction(ACTION_UNSET_MODE, capability_key, "mode", fanout=exclusive),
    )
    cap = DuerCapability(
        capability_key,
        "模式",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_MODE, "string", legal=legal),),
        actions=actions,
    )

    def read(ctx: ReadContext) -> AttributeValue:
        for mode_value, role, _entity_id in mode_list:
            state = ctx.entities.get(role)
            if state is not None and state.state == "on":
                return make_attribute(ATTR_MODE, mode_value, legal=legal)
        return make_attribute(ATTR_MODE, "", legal=legal)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        value = str(_payload_value(ctx.payload, "mode") or "")
        target = next((eid for m, role, eid in mode_list if m == value and ctx.entities.get(role) is not None), None)
        if not target:
            return None
        target_domain = target.split(".", 1)[0]
        if ctx.action.name == ACTION_SET_MODE:
            calls = [ServiceCall(target_domain, service_on, {}, target)]
            if exclusive:
                # Turn off every sibling mode so the requested one becomes active.
                for m, role, eid in mode_list:
                    state = ctx.entities.get(role)
                    if eid != target and state is not None and state.state == "on":
                        calls.append(ServiceCall(eid.split(".", 1)[0], service_off, {}, eid))
            return calls
        if ctx.action.name == ACTION_UNSET_MODE:
            return [ServiceCall(target_domain, service_off, {}, target)]
        return None

    bindings = tuple(EntityBinding(eid, role) for _m, role, eid in mode_list)
    return CapabilityMapping(cap, bindings, read=read, write=write)


def select_mapping(
    *,
    entity_id: str,
    attribute_name: str,
    capability_key: str,
    appliance_types: tuple[str, ...],
    select_domain: str = "select",
    set_action: str = "",
    unset_action: str = "",
) -> CapabilityMapping:
    """A ``select`` entity (mode / gear / fan-speed / water-level) mapping.

    Reads the current ``option``; writes via ``select.select_option``. The
    ``set_action`` / ``unset_action`` names tell the protocol which DuerOS
    actions this capability accepts (e.g. setGear for warmthLevel).
    """
    actions = tuple(
        DuerAction(name, capability_key, capability_key)
        for name in (set_action, unset_action)
        if name
    )
    cap = DuerCapability(
        capability_key,
        "档位",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(attribute_name, "string"),),
        actions=actions,
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        option = (state.attributes.get("option") if state else None) or ""
        return make_attribute(attribute_name, option)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name not in (set_action, unset_action):
            return None
        value = _payload_value(ctx.payload, capability_key)
        if value is None:
            value = _payload_value(ctx.payload, "mode")
        if value is None:
            return None
        return [ServiceCall(select_domain, "select_option", {"option": str(value)}, entity_id)]

    return CapabilityMapping(
        cap, (EntityBinding(entity_id, "value"),), read=read, write=write
    )


def target_temperature_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "number",
    set_service: str = "set_value",
    capability_key: str = "targetTemperature",
    attribute_name: str = ATTR_TARGET_TEMPERATURE,
) -> CapabilityMapping:
    """A target-temperature entity (number / climate)."""
    cap = DuerCapability(
        capability_key,
        "目标温度",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(attribute_name, "number", unit="CELSIUS", legal="DOUBLE"),),
        actions=(DuerAction(ACTION_SET_TEMPERATURE, capability_key, "temperature"),),
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        value = _num(state.state if state else None)
        if value is None:
            return None
        return make_attribute(attribute_name, value, scale="CELSIUS", legal="DOUBLE")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_TEMPERATURE:
            return None
        value = _num(_payload_value(ctx.payload, "temperature"))
        if value is None:
            return None
        return [ServiceCall(domain, set_service, {"value": value}, entity_id)]

    return CapabilityMapping(
        cap, (EntityBinding(entity_id, "value"),), read=read, write=write
    )


def percentage_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "cover",
    capability_key: str = "percentage",
) -> CapabilityMapping:
    """A cover's position as a percentage (0..100)."""
    cap = DuerCapability(
        capability_key,
        "位置",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_PERCENTAGE, "number", unit="%", legal="[0, 100]"),),
        actions=(),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        pos = _num(state.attributes.get("current_position") if state else None)
        return make_attribute(ATTR_PERCENTAGE, pos if pos is not None else 0, scale="%", legal="[0, 100]")

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read)


def pause_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "cover",
    capability_key: str = "pause",
    include_continue: bool = True,
) -> CapabilityMapping:
    """A pause/continue capability (cover.stop, vacuum.pause/start,...)."""
    cap = DuerCapability(
        capability_key,
        "暂停",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_PAUSE_STATE, "boolean", legal="BOOLEAN"),),
        actions=(
            (DuerAction(ACTION_PAUSE, capability_key),)
            + ((DuerAction(ACTION_CONTINUE, capability_key),) if include_continue else ())
        ),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        paused = bool(state and state.state == "paused")
        return make_attribute(ATTR_PAUSE_STATE, paused, legal="BOOLEAN")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name == ACTION_PAUSE:
            service = "stop_cover" if domain == "cover" else ("pause" if domain == "vacuum" else "stop")
            return [ServiceCall(domain, service, {}, entity_id)]
        if ctx.action.name == ACTION_CONTINUE and include_continue:
            return [ServiceCall("vacuum", "start", {}, entity_id)]
        return None

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def _query_action_name(query_name: str) -> str:
    """Discovery action advertised for a DuerOS query request.

    ``GetTemperatureReadingRequest`` -> ``getTemperatureReading``,
    ``GetHumidityRequest`` -> ``getHumidity``. A read-only sensor still has to
    advertise its query as an *action* so the platform knows it can answer
    "现在多少度 / 湿度多少" (mirrors havcs).
    """
    name = query_name
    if name.endswith("Request"):
        name = name[: -len("Request")]
    return (name[:1].lower() + name[1:]) if name else name


def sensor_query_mapping(
    *,
    entity_id: str,
    attribute_name: str,
    capability_key: str,
    appliance_types: tuple[str, ...],
    unit: str = "",
    legal: str = "DOUBLE",
    query_names: tuple[str, ...] = (),
    scale: str = "",
) -> CapabilityMapping:
    """A read-only sensor query (temperature / humidity / electricity capacity).

    Each supported query is advertised as an action (``getTemperatureReading``
    etc.) so the appliance is not discoverable with an empty ``actions`` list.
    """
    cap = DuerCapability(
        capability_key,
        "查询",
        kind=CAP_KIND_QUERY,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(attribute_name, "number", unit=unit, legal=legal),),
        actions=tuple(
            DuerAction(_query_action_name(q), capability_key) for q in query_names
        ),
        query_names=query_names,
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        value = _num(state.state if state else None)
        if value is None:
            # unknown / unavailable: omit the attribute instead of fabricating
            # a numeric 0.0 against legalValue.
            return None
        scale_value = scale or unit
        if capability_key == "temperature":
            from_unit = str(state.attributes.get("unit_of_measurement") or "") if state else ""
            target = _temperature_target_unit(ctx.hass)
            if from_unit and target and from_unit.lower() != target.lower():
                value = _convert_temperature(value, from_unit, target)
                t = target.lower()
                scale_value = "CELSIUS" if "c" in t else ("FAHRENHEIT" if "f" in t else scale_value)
        return make_attribute(attribute_name, value, scale=scale_value, legal=legal)

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read)


def composite_power_mapping(
    *,
    primary_entity_id: str,
    domain: str,
    switch_roles: Iterable[tuple[str, str]],
    appliance_types: tuple[str, ...],
    on_services: Iterable[tuple[str, str, dict[str, Any]]] | None = None,
    off_services: Iterable[tuple[str, str, dict[str, Any]]] | None = None,
    capability_key: str = "power",
) -> CapabilityMapping:
    """Composite ``power``: on when any function entity is on; off turns all off.

    ``switch_roles`` is ``(entity_id, role)`` pairs (e.g. a YUBA's heating /
    blow / ventilation / light). ``on_services`` / ``off_services`` optionally
    provide the exact calls to fan out beyond the per-switch turn_on/off.
    """
    on_list = list(on_services) if on_services else []
    off_list = list(off_services) if off_services else []
    cap = DuerCapability(
        capability_key,
        "开关",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_TURN_ON_STATE, "string", legal="(ON, OFF)"),),
        actions=(DuerAction(ACTION_TURN_ON, capability_key, fanout=True),
                 DuerAction(ACTION_TURN_OFF, capability_key, fanout=True)),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        for _eid, role in switch_roles:
            state = ctx.entities.get(role)
            if state is not None and state.state == "on":
                return _turn_on_state_attr(True)
        return _turn_on_state_attr(False)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name == ACTION_TURN_OFF:
            calls = list(off_list)
            for eid, role in switch_roles:
                state = ctx.entities.get(role)
                if state is not None and state.state == "on":
                    calls.append(ServiceCall(eid.split(".", 1)[0], "turn_off", {}, eid))
            return calls or None
        if ctx.action.name == ACTION_TURN_ON:
            calls = list(on_list)
            if not calls:
                # Default: turn on the primary entity using its own domain.
                calls.append(
                    ServiceCall(primary_entity_id.split(".", 1)[0], "turn_on", {}, primary_entity_id)
                )
            return calls
        return None

    bindings = tuple(EntityBinding(eid, role) for eid, role in switch_roles)
    bindings += (EntityBinding(primary_entity_id, "power"),)
    return CapabilityMapping(cap, bindings, read=read, write=write)



# --- simple-device composers (light / media_player / fan / climate / humidifier) ---

def _mireds_to_kelvin(mireds: Any) -> float | None:
    """Convert a mired color-temperature value to Kelvin."""
    value = _num(mireds)
    return round(1_000_000.0 / value) if value else None


def _color_temp_kelvin(state: Any) -> float | None:
    kelvin = state.attributes.get("color_temp_kelvin")
    if kelvin is not None:
        return round(float(kelvin))
    return _mireds_to_kelvin(state.attributes.get("color_temp"))


def _color_temp_bounds(state: Any) -> tuple[float, float]:
    min_kelvin = _num(state.attributes.get("color_temp_min_kelvin"))
    max_kelvin = _num(state.attributes.get("color_temp_max_kelvin"))
    if min_kelvin is None:
        min_kelvin = _mireds_to_kelvin(state.attributes.get("color_temp_max"))
    if max_kelvin is None:
        max_kelvin = _mireds_to_kelvin(state.attributes.get("color_temp_min"))
    return (min_kelvin or 1000.0, max_kelvin or 10000.0)


def brightness_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "light",
) -> CapabilityMapping:
    """Brightness of a light (0..100%), via ``light.turn_on brightness_pct``."""
    cap = DuerCapability(
        "brightness",
        "亮度",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_BRIGHTNESS, "number", unit="%", legal="[0, 100]"),),
        actions=(DuerAction(ACTION_SET_BRIGHTNESS, "brightness", "brightness"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        b = _num(state.attributes.get("brightness") if state else None)
        value = (b / 255 * 100) if b is not None else 0.0
        return make_attribute(ATTR_BRIGHTNESS, round(float(value), 1), scale="%", legal="[0, 100]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_BRIGHTNESS:
            return None
        value = _payload_value(ctx.payload, "brightness")
        if value is None:
            return None
        v = max(0.0, min(100.0, float(value)))
        return [ServiceCall(domain, "turn_on", {"brightness_pct": v}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def color_temperature_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "light",
) -> CapabilityMapping:
    """Color temperature in Kelvin (``setColorTemperature``)."""
    cap = DuerCapability(
        "colorTemperature",
        "色温",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_COLOR_TEMPERATURE, "number", unit="K", legal="DOUBLE"),),
        actions=(DuerAction(ACTION_SET_COLOR_TEMPERATURE, "colorTemperature", "colorTemperature"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        kelvin = _color_temp_kelvin(state) if state is not None else None
        lo, hi = _color_temp_bounds(state) if state is not None else (1000.0, 10000.0)
        return make_attribute(
            ATTR_COLOR_TEMPERATURE,
            kelvin if kelvin is not None else round((lo + hi) / 2),
            scale="K",
            legal=f"[{int(lo)}, {int(hi)}]",
        )

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_COLOR_TEMPERATURE:
            return None
        value = _payload_value(ctx.payload, "colorTemperature")
        if value is None:
            return None
        state = ctx.entities.get("value")
        lo, hi = _color_temp_bounds(state) if state is not None else (1000.0, 10000.0)
        kelvin = max(lo, min(hi, float(value)))
        return [ServiceCall(domain, "turn_on", {"color_temp_kelvin": kelvin}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def color_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "light",
) -> CapabilityMapping:
    """HS color (``setColor``), via ``light.turn_on hs_color``."""
    cap = DuerCapability(
        "color",
        "颜色",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_COLOR, "string"),),
        actions=(DuerAction(ACTION_SET_COLOR, "color", "color"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        hs = (state.attributes.get("hs_color") if state else None) or []
        return make_attribute(ATTR_COLOR, {"hue": hs[0], "saturation": hs[1] / 100} if len(hs) >= 2 else {"hue": 0, "saturation": 0})

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_COLOR:
            return None
        color = ctx.payload.get("color") or {}
        hue = _num(color.get("hue"))
        saturation = _num(color.get("saturation"))
        if hue is None or saturation is None:
            return None
        return [ServiceCall(domain, "turn_on", {"hs_color": [hue, saturation * 100]}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def volume_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """Media-player volume (0..100%)."""
    cap = DuerCapability(
        "volume",
        "音量",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_VOLUME, "number", unit="%", legal="[0, 100]"),),
        actions=(DuerAction(ACTION_SET_VOLUME, "volume", "volume"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        level = _num(state.attributes.get("volume_level") if state else None)
        value = round(float(level) * 100) if level is not None else 0
        return make_attribute(ATTR_VOLUME, value, scale="%", legal="[0, 100]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_VOLUME:
            return None
        value = _payload_value(ctx.payload, "volume")
        if value is None:
            return None
        level = max(0.0, min(100.0, float(value))) / 100
        return [ServiceCall("media_player", "volume_set", {"volume_level": level}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def mute_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """Media-player mute (``setVolumeMute``)."""
    cap = DuerCapability(
        "mute",
        "静音",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_MUTE_STATE, "boolean", legal="(true, false)"),),
        actions=(DuerAction(ACTION_SET_VOLUME_MUTE, "mute", "mute"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        muted = bool(state.attributes.get("is_volume_muted")) if state else False
        return make_attribute(ATTR_MUTE_STATE, muted, legal="(true, false)")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_VOLUME_MUTE:
            return None
        mute = ctx.payload.get("mute", ctx.payload.get("muteState"))
        if not isinstance(mute, bool):
            return None
        return [ServiceCall("media_player", "volume_mute", {"is_volume_muted": mute}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def channel_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """Media-player source/channel (``setTVChannel``)."""
    cap = DuerCapability(
        "channel",
        "频道",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_CHANNEL, "string"),),
        actions=(DuerAction(ACTION_SET_TV_CHANNEL, "channel", "channel"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        source = str(state.attributes.get("source") or "") if state else ""
        return make_attribute(ATTR_CHANNEL, source)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_TV_CHANNEL:
            return None
        channel = (ctx.payload.get("channel") or {}).get("value")
        if channel is None:
            return None
        return [ServiceCall("media_player", "select_source", {"source": str(channel)}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def fan_speed_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "fan",
) -> CapabilityMapping:
    """Fan speed as 0..10 (``setFanSpeed``), via ``fan.set_percentage``."""
    cap = DuerCapability(
        "fanSpeed",
        "风速",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_FAN_SPEED, "number", legal="[0, 10]"),),
        actions=(DuerAction(ACTION_SET_FAN_SPEED, "fanSpeed", "fanSpeed"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        pct = _num(state.attributes.get("percentage") if state else None)
        value = (pct / 10) if pct is not None else 0
        return make_attribute(ATTR_FAN_SPEED, value, legal="[0, 10]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_FAN_SPEED:
            return None
        value = _payload_value(ctx.payload, "fanSpeed")
        if value is None:
            return None
        v = max(0, min(10, round(float(value))))
        return [ServiceCall(domain, "set_percentage", {"percentage": v * 10}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def _climate_fan_levels(state: Any) -> list[str]:
    """Order a climate's ``fan_modes`` from slowest to fastest.

    AC integrations (Midea / xiaomi) model fan speed as discrete
    ``fan_modes`` — percentage strings ("20".."100") plus an "auto" token.
    Numeric modes sort by value; anything non-numeric (e.g. auto) is treated
    as the fastest level.
    """
    modes = list((state.attributes.get("fan_modes") or ()) if state is not None else [])
    numeric: list[str] = []
    labelled: list[str] = []
    for mode in modes:
        if _num(mode) is not None:
            numeric.append(str(mode))
        else:
            labelled.append(str(mode))
    numeric.sort(key=float)
    return numeric + labelled


def _climate_fan_index(state: Any, levels: list[str]) -> int | None:
    """0-based index of the climate's current ``fan_mode`` within ``levels``."""
    if state is None or not levels:
        return None
    current = str(state.attributes.get("fan_mode") or "")
    return levels.index(current) if current in levels else None


def climate_fan_speed_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """AC fan speed (``setFanSpeed`` / ``incrementFanSpeed`` / ``decrementFanSpeed``).

    The climate domain has no ``percentage`` attribute, so DuerOS fan speed
    (0..10) maps onto the climate's discrete ``fan_mode`` levels (0-based index
    into the ordered list) and is written via ``climate.set_fan_mode`` instead
    of the ``fan.set_percentage`` used by standalone fans.
    """
    cap = DuerCapability(
        "fanSpeed",
        "风速",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_FAN_SPEED, "number", legal="[0, 10]"),),
        actions=(
            DuerAction(ACTION_SET_FAN_SPEED, "fanSpeed", "fanSpeed"),
            DuerAction(ACTION_INCREMENT_FAN_SPEED, "fanSpeed", "fanSpeed"),
            DuerAction(ACTION_DECREMENT_FAN_SPEED, "fanSpeed", "fanSpeed"),
        ),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        index = _climate_fan_index(state, _climate_fan_levels(state))
        return make_attribute(ATTR_FAN_SPEED, index if index is not None else 0, legal="[0, 10]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        state = ctx.entities.get("value")
        levels = _climate_fan_levels(state)
        if not levels:
            return None
        action = ctx.action.name
        if action == ACTION_SET_FAN_SPEED:
            value = _num(_payload_value(ctx.payload, "fanSpeed"))
            if value is None:
                return None
            index = max(0, min(len(levels) - 1, round(value)))
        elif action in (ACTION_INCREMENT_FAN_SPEED, ACTION_DECREMENT_FAN_SPEED):
            current = _climate_fan_index(state, levels)
            if current is None:
                return None
            delta = _payload_number(ctx.payload, "deltaFanSpeed", "fanSpeed")
            delta = 1 if delta is None else round(delta)
            step = delta if action == ACTION_INCREMENT_FAN_SPEED else -delta
            index = max(0, min(len(levels) - 1, current + step))
        else:
            return None
        return [ServiceCall("climate", "set_fan_mode", {"fan_mode": levels[index]}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def climate_mode_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """Climate HVAC mode (``setMode``/``unSetMode``)."""
    cap = DuerCapability(
        "mode",
        "模式",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_MODE, "string"),),
        actions=(
            DuerAction(ACTION_SET_MODE, "mode", "mode"),
            DuerAction(ACTION_UNSET_MODE, "mode", "mode"),
        ),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        mode = str(state.attributes.get("hvac_mode") or "").upper() if state else ""
        return make_attribute(ATTR_MODE, mode)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name not in (ACTION_SET_MODE, ACTION_UNSET_MODE):
            return None
        mode = (ctx.payload.get("mode") or {}).get("value")
        if mode is None:
            mode = ctx.payload.get("mode")
        if isinstance(mode, dict):
            mode = mode.get("value")
        if not mode:
            return None
        # unSetMode -> off (turn off the climate).
        if ctx.action.name == ACTION_UNSET_MODE:
            return [ServiceCall("climate", "turn_off", {}, entity_id)]
        return [ServiceCall("climate", "set_hvac_mode", {"hvac_mode": str(mode).lower()}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def climate_temperature_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """Climate target temperature (``setTemperature`` / ``increment`` / ``decrement``).

    The DuerOS app's +/− steppers bind to the incremental actions, so they are
    advertised next to the absolute ``setTemperature`` and implemented by
    applying the delta to the current HA target temperature.
    """
    cap = DuerCapability(
        "targetTemperature",
        "目标温度",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_TARGET_TEMPERATURE, "number", unit="CELSIUS", legal="DOUBLE"),),
        actions=(
            DuerAction(ACTION_SET_TEMPERATURE, "targetTemperature", "temperature"),
            DuerAction(ACTION_INCREMENT_TEMPERATURE, "targetTemperature", "temperature"),
            DuerAction(ACTION_DECREMENT_TEMPERATURE, "targetTemperature", "temperature"),
        ),
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        value = _num(state.attributes.get("temperature") if state else None)
        if value is None:
            return None
        return make_attribute(ATTR_TARGET_TEMPERATURE, value, scale="CELSIUS", legal="DOUBLE")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        state = ctx.entities.get("value")
        action = ctx.action.name
        if action == ACTION_SET_TEMPERATURE:
            value = _num(_payload_value(ctx.payload, "temperature"))
            if value is None:
                return None
            return [ServiceCall("climate", "set_temperature", {"temperature": value}, entity_id)]
        if action in (ACTION_INCREMENT_TEMPERATURE, ACTION_DECREMENT_TEMPERATURE):
            current = _num(state.attributes.get("temperature") if state else None)
            if current is None:
                return None
            step = _num(state.attributes.get("target_temp_step")) if state is not None else None
            delta = _payload_number(ctx.payload, "deltaTemperature", "temperature")
            if delta is None:
                delta = step or 1.0
            value = current + delta if action == ACTION_INCREMENT_TEMPERATURE else current - delta
            if step:
                value = round(round(value / step) * step, 2)
            return [ServiceCall("climate", "set_temperature", {"temperature": value}, entity_id)]
        return None

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def target_humidity_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    domain: str = "humidifier",
) -> CapabilityMapping:
    """Humidifier target humidity (``setHumidity``)."""
    cap = DuerCapability(
        "targetHumidity",
        "目标湿度",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_TARGET_HUMIDITY, "number", unit="%", legal="[0, 100]"),),
        actions=(DuerAction(ACTION_SET_HUMIDITY, "targetHumidity", "humidity"),),
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        value = _num(state.attributes.get("target_humidity") if state else None)
        if value is None:
            # Off / not reported: the entity state string (e.g. "off") is not a
            # numeric humidity. Serializing it would break legalValue [0, 100],
            # so omit the attribute until a numeric target is available.
            return None
        return make_attribute(ATTR_TARGET_HUMIDITY, value, scale="%", legal="[0, 100]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_HUMIDITY:
            return None
        value = _num(_payload_value(ctx.payload, "humidity"))
        if value is None:
            return None
        return [ServiceCall(domain, "set_humidity", {"humidity": int(value)}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def humidifier_mode_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
) -> CapabilityMapping:
    """Humidifier operating mode (``setMode``) via ``humidifier.set_mode``.

    Uses the HA ``humidifier`` domain's own ``mode`` / ``available_modes``
    attributes and the ``humidifier.set_mode`` service (the domain's official
    API), instead of routing through ``select.select_option`` like a generic
    select entity (``humidifier.select_option`` does not exist). ``legalValue``
    is derived from ``available_modes`` so Xiaodu knows the valid mode strings.
    """
    cap = DuerCapability(
        "mode",
        "模式",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(ATTR_MODE, "string"),),
        actions=(DuerAction(ACTION_SET_MODE, "mode", "mode"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        modes = list(state.attributes.get("available_modes") or ()) if state else []
        mode = str(state.attributes.get("mode") or "") if state else ""
        legal = "(" + ", ".join(str(m) for m in modes) + ")" if modes else ""
        return make_attribute(ATTR_MODE, mode, legal=legal)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_MODE:
            return None
        value = _payload_value(ctx.payload, "mode")
        if value is None:
            return None
        return [ServiceCall("humidifier", "set_mode", {"mode": str(value)}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


__all__ = [
    "power_mapping",
    "mode_switches_mapping",
    "select_mapping",
    "target_temperature_mapping",
    "percentage_mapping",
    "pause_mapping",
    "sensor_query_mapping",
    "composite_power_mapping",
    "is_powered_on",
    "_turn_on_state_attr",
    "brightness_mapping",
    "color_temperature_mapping",
    "color_mapping",
    "volume_mapping",
    "mute_mapping",
    "channel_mapping",
    "fan_speed_mapping",
    "climate_fan_speed_mapping",
    "climate_mode_mapping",
    "climate_temperature_mapping",
    "target_humidity_mapping",
    "humidifier_mode_mapping",
]



def attribute_level_mapping(
    *,
    entity_id: str,
    attribute_name: str,
    capability_key: str,
    appliance_types: tuple[str, ...],
    set_action: str,
    service_domain: str,
    service: str,
    data_key: str,
    payload_key: str,
    read_attr: str | None = None,
    read_state: bool = False,
    unit: str = "",
    legal: str = "",
    query_names: tuple[str, ...] = (),
) -> CapabilityMapping:
    """A scalar level (suction / water level / mode) written via a service call.

    Reads from ``state.attributes[read_attr]`` (or ``state.state`` when
    ``read_state``), writes ``set_action`` to ``service_domain.service`` with
    ``{data_key: payload_value}``.
    """
    cap = DuerCapability(
        capability_key,
        "档位",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(attribute_name, "string", unit=unit, legal=legal),),
        actions=(DuerAction(set_action, capability_key, payload_key),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        if read_state:
            value = state.state if state is not None else ""
        else:
            value = (state.attributes.get(read_attr) if state is not None and read_attr else None) or ""
        return make_attribute(attribute_name, value, scale=unit, legal=legal)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != set_action:
            return None
        value = _payload_value(ctx.payload, payload_key)
        if value is None:
            return None
        return [ServiceCall(service_domain, service, {data_key: str(value)}, entity_id)]

    return CapabilityMapping(
        cap, (EntityBinding(entity_id, "value"),), read=read, write=write
    )
