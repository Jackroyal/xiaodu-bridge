"""Reusable CapabilityMapping composers.

A composer is a *declarative* factory: a device profile fills in its entities and
semantic roles, and the composer returns a ready ``CapabilityMapping`` with the
``read`` / ``write`` / ``query`` / ``change_report`` callbacks wired up. This keeps
the protocol layer free of device-type ``if`` branches.

These are pure logic (no Home Assistant runtime imports) so they can be unit
tested with fake ``State`` objects.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

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
    ATTR_MODE,
    ATTR_PAUSE_STATE,
    ATTR_PERCENTAGE,
    ATTR_TARGET_HUMIDITY,
    ATTR_TARGET_TEMPERATURE,
    ATTR_TIME_LEFT_IN_SECONDS,
    ATTR_TURN_ON_STATE,
    ATTR_COLOR,
    ATTR_VOLUME,
    ATTR_CHANNEL,
    ATTR_MUTE_STATE,
    ACTION_CONTINUE,
    ACTION_DECREMENT_FAN_SPEED,
    ACTION_DECREMENT_TEMPERATURE,
    ACTION_INCREMENT_FAN_SPEED,
    ACTION_INCREMENT_TEMPERATURE,
    ACTION_PAUSE,
    ACTION_SET_FAN_SPEED,
    ACTION_SET_HUMIDITY,
    ACTION_SET_MODE,
    ACTION_SET_TEMPERATURE,
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


def _payload_temperature(payload: dict[str, Any]) -> tuple[float | None, str]:
    """Extract (value, scale) from a SetTemperature payload.

    Xiaodu sends the absolute target under ``targetTemperature`` (mirroring the
    attribute name); other clients may use ``temperature``. Accept both so a
    captured payload never falls through to ``NotSupportedInCurrentModeError``.
    """
    for key in ("temperature", "targetTemperature"):
        node = payload.get(key)
        if isinstance(node, dict):
            value = _num(node.get("value"))
            if value is not None:
                return value, str(node.get("scale") or "")
        else:
            value = _num(node)
            if value is not None:
                return value, ""
    return None, ""


def _payload_delta_temperature(payload: dict[str, Any]) -> tuple[float | None, str]:
    """Extract (delta, scale) from an Increment/DecrementTemperature payload.

    The contract carries the step under ``deltaValue`` — the ``deltaTemperature``
    / ``temperature`` keys this used to look for do not exist in the protocol.
    """
    node = payload.get("deltaValue")
    if not isinstance(node, dict):
        value = _num(node)
        return (value, "") if value is not None else (None, "")
    value = _num(node.get("value"))
    if value is None:
        return None, ""
    return value, str(node.get("scale") or "")


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


def _convert_temperature_delta(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a temperature *difference* between °C and °F.

    A delta has no zero-point offset, so this scales only — using
    :func:`_convert_temperature` on an increment would subtract 32 first and
    produce a nonsensical step.
    """
    f = (from_unit or "").lower()
    t = (to_unit or "").lower()
    if not f or not t or f == t:
        return value
    if "f" in f and "c" in t:
        return round(value * 5 / 9, 2)
    if "c" in f and "f" in t:
        return round(value * 9 / 5, 2)
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
        attributes=(DuerAttribute(ATTR_TURN_ON_STATE, "string", legal="(ON, OFF)"),),
        actions=tuple(DuerAction(a, capability_key) for a in actions),
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        # The bound entity may already be gone (removed while a report is
        # being computed): omit the attribute instead of raising KeyError.
        state = ctx.entities.get("power")
        if state is None:
            return None
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
    ordered_options: bool = False,
) -> CapabilityMapping:
    """A ``select`` entity (mode / gear / fan-speed / water-level) mapping.

    Reads the current ``option``; writes via ``select.select_option``. The
    ``set_action`` / ``unset_action`` names tell the protocol which DuerOS
    actions this capability accepts (e.g. setGear for warmthLevel).

    ``ordered_options`` marks a capability whose options are an ordered speed
    scale (fan speed): DuerOS then names a *position* (``fanSpeed.value`` 1..10
    or a ``fanSpeed.level`` word) that is resolved against the option order,
    instead of the payload value being used verbatim as an option label.
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
        attributes=(
            DuerAttribute(
                attribute_name,
                "number" if ordered_options else "string",
                legal="[0, 10]" if ordered_options else "",
            ),
        ),
        actions=actions,
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        option = str(_current_value(state, None) or "")
        if ordered_options:
            # Ordered options are a speed scale: report the same 1..10 position
            # the write path resolves a requested speed to (an option label is
            # not a fanSpeed value, and an index would mean a different speed
            # per device).
            options = _entity_values(state, "options")
            index = options.index(option) if option in options else -1
            value = _fan_step_scale(index, len(options)) if index >= 0 else 0
            return make_attribute(attribute_name, value, legal="[0, 10]")
        return make_attribute(attribute_name, option)

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name not in (set_action, unset_action):
            return None
        if ordered_options:
            option = _select_level_option(ctx, capability_key)
            if option is None:
                return None
            return [ServiceCall(select_domain, "select_option", {"option": option}, entity_id)]
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
        # Accept both payload keys: the contract's ``targetTemperature`` and the
        # ``temperature`` some clients use, so a captured payload never falls
        # through to NotSupportedInCurrentModeError.
        value, scale = _payload_temperature(ctx.payload)
        if value is None:
            return None
        target = _temperature_target_unit(ctx.hass)
        if scale and target and scale.lower() != target.lower():
            value = _convert_temperature(value, scale, target)
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
        value = _payload_value(ctx.payload, "colorTemperatureInKelvin")
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
        # attributes.md color：hue 0~360、saturation/brightness 0~1 的对象
        attributes=(DuerAttribute(ATTR_COLOR, "object", legal="OBJECT"),),
        actions=(DuerAction(ACTION_SET_COLOR, "color", "color"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        hs = (state.attributes.get("hs_color") if state else None) or []
        brightness = _num(state.attributes.get("brightness") if state else None)
        has_hs = len(hs) >= 2
        value = {
            "hue": hs[0] if has_hs else 0,
            "saturation": hs[1] / 100 if has_hs else 0,
            "brightness": round(brightness / 255, 4) if brightness is not None else 0,
        }
        return make_attribute(ATTR_COLOR, value, legal="OBJECT")

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
        # attributes.md volume: 0..100, 无单位（scale 为空串）
        attributes=(DuerAttribute(ATTR_VOLUME, "number", legal="[0, 100]"),),
        actions=(DuerAction(ACTION_SET_VOLUME, "volume", "volume"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        level = _num(state.attributes.get("volume_level") if state else None)
        value = round(float(level) * 100) if level is not None else 0
        return make_attribute(ATTR_VOLUME, value, legal="[0, 100]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_VOLUME:
            return None
        # The contract carries the target volume under ``deltaValue`` despite
        # the name (``SetVolumeRequest``: "音量范围0-100").
        value = _num(_payload_value(ctx.payload, "deltaValue"))
        if value is None:
            return None
        level = max(0.0, min(100.0, value)) / 100
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
        # attributes.md muteState: boolean value, legalValue "BOOLEAN".
        attributes=(DuerAttribute(ATTR_MUTE_STATE, "boolean", legal="BOOLEAN"),),
        actions=(DuerAction(ACTION_SET_VOLUME_MUTE, "mute", "mute"),),
    )

    def read(ctx: ReadContext) -> AttributeValue:
        state = ctx.entities.get("value")
        muted = bool(state.attributes.get("is_volume_muted")) if state else False
        return make_attribute(ATTR_MUTE_STATE, muted, legal="BOOLEAN")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if ctx.action.name != ACTION_SET_VOLUME_MUTE:
            return None
        # The contract sends the mute state as the enum "on" / "off" under
        # ``deltaValue.value`` (not a boolean, and not a ``mute`` key).
        mute = _payload_value(ctx.payload, "deltaValue")
        if not isinstance(mute, str):
            return None
        token = mute.strip().lower()
        if token not in ("on", "off"):
            return None
        return [
            ServiceCall(
                "media_player", "volume_mute", {"is_volume_muted": token == "on"}, entity_id
            )
        ]

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
        # The contract carries the channel under ``deltaValue.value`` (int for a
        # numeric channel, string for a channel name) — there is no ``channel``
        # payload key.
        channel = _payload_value(ctx.payload, "deltaValue")
        if channel is None:
            return None
        return [ServiceCall("media_player", "select_source", {"source": str(channel)}, entity_id)]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


# DuerOS named fan levels (``SetFanSpeedRequest.fanSpeed.level``), placed evenly
# on the protocol's 1..10 fanSpeed scale so a level word and a concrete
# ``fanSpeed.value`` are converted by the same code path. "auto" is not a
# position on that scale — it selects the device's automatic fan mode instead.
_FAN_LEVEL_POSITIONS = {"min": 0.0, "low": 0.25, "middle": 0.5, "high": 0.75, "max": 1.0}

# Tokens fan_/climate integrations use for their automatic fan mode. "auto" is
# the Home Assistant convention; "102" is Midea's encoding on its 20..100
# wind-speed scale, surfaced as a plain numeric ``fan_mode`` rather than "auto".
_AUTO_FAN_MODES = frozenset({"auto", "automatic", "102"})


def _is_auto_fan_mode(mode: str) -> bool:
    return mode.strip().lower() in _AUTO_FAN_MODES


def _fan_speed_level(payload: dict[str, Any]) -> str:
    """``fanSpeed.level`` when the user phrased a level word, else ``""``.

    DuerOS sends ``fanSpeed`` as *either* ``{"value": 1..10}`` (a concrete
    speed) or ``{"level": "min"|"low"|"middle"|"high"|"max"|"auto"}`` (a named
    level), depending on how the user phrased it — never both.
    """
    node = payload.get("fanSpeed")
    if not isinstance(node, dict):
        return ""
    level = node.get("level")
    return str(level).strip().lower() if level is not None else ""


def _fan_level_scale(level: str) -> float | None:
    """A DuerOS level word as a position on the 1..10 fanSpeed scale."""
    fraction = _FAN_LEVEL_POSITIONS.get(level)
    return None if fraction is None else 1 + fraction * 9


def _fan_scale_to_step(value: float, count: int) -> int:
    """Spread a 1..10 fanSpeed value over ``count`` discrete device steps."""
    if count <= 1:
        return 0
    return round((min(10.0, max(1.0, value)) - 1) / 9 * (count - 1))


def _fan_step_scale(index: int, count: int) -> int:
    """A device step's position on the DuerOS 1..10 fanSpeed scale.

    The inverse of :func:`_fan_scale_to_step`, so a fan speed read back reports
    the same position DuerOS would have named on the way in (an index is
    device-relative and would mean a different speed per device). attributes.md
    declares fanSpeed as an integer, so the position is rounded (half up) onto
    the scale instead of reported as a fraction.
    """
    if count <= 1:
        return 1
    step = max(0, min(count - 1, index))
    return 1 + (step * 9 + (count - 1) // 2) // (count - 1)


def _fan_level_step(level: str, count: int) -> int | None:
    """A DuerOS level word as an index into ``count`` ordered speed steps."""
    scale = _fan_level_scale(level)
    return None if scale is None else _fan_scale_to_step(scale, count)


def _select_level_option(ctx: WriteContext, payload_key: str) -> str | None:
    """Resolve a DuerOS fan-speed payload to one of a select's own options.

    ``fanSpeed.value`` (1..10) and ``fanSpeed.level`` name a *position* on the
    entity's option order (slowest → fastest); the option labels come from the
    integration (e.g. 低档 / 高档), so the raw DuerOS token is never itself a
    valid option.
    """
    state = ctx.entities.get("value")
    options = _entity_values(state, "options")
    if not options:
        return None
    level = _fan_speed_level(ctx.payload)
    if _is_auto_fan_mode(level):
        return None
    value = _num(_payload_value(ctx.payload, payload_key))
    if value is None:
        value = _fan_level_scale(level)
    if value is None:
        return None
    return options[_fan_scale_to_step(value, len(options))]


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
        value = _num(_payload_value(ctx.payload, "fanSpeed"))
        if value is None:
            # A level word ("min" .. "max"). "auto" has no percentage
            # equivalent, so it stays unsupported for a plain fan.
            value = _fan_level_scale(_fan_speed_level(ctx.payload))
        if value is None:
            return None
        return [
            ServiceCall(
                domain,
                "set_percentage",
                {"percentage": max(0, min(100, round(value * 10)))},
                entity_id,
            )
        ]

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read, write=write)


def _climate_fan_modes(state: Any) -> list[str]:
    modes = (state.attributes.get("fan_modes") or ()) if state is not None else ()
    return [str(mode) for mode in modes]


def _climate_auto_fan_mode(state: Any) -> str | None:
    """The climate's automatic fan mode token, if it exposes one."""
    return next((mode for mode in _climate_fan_modes(state) if _is_auto_fan_mode(mode)), None)


def _climate_fan_levels(state: Any) -> list[str]:
    """Order a climate's ``fan_modes`` from slowest to fastest.

    AC integrations (Midea / xiaomi) model fan speed as discrete
    ``fan_modes`` — percentage strings ("20".."100") plus a separate automatic
    mode. Numeric modes sort by value; anything non-numeric is kept after them.
    The automatic mode is not a speed step, so it is excluded here instead of
    sorting as the fastest level; it is reached via ``fanSpeed.level == "auto"``.
    """
    numeric: list[str] = []
    labelled: list[str] = []
    for mode in _climate_fan_modes(state):
        if _is_auto_fan_mode(mode):
            continue
        if _num(mode) is not None:
            numeric.append(mode)
        else:
            labelled.append(mode)
    numeric.sort(key=float)
    return numeric + labelled


def _climate_fan_steps(state: Any) -> list[str]:
    """Fan modes in DuerOS order: speed steps ascending, then ``auto``.

    Increment / decrement walk this list, so ``auto`` sits above the fastest
    numbered step and stepping down out of auto lands on that step.
    """
    auto = _climate_auto_fan_mode(state)
    levels = _climate_fan_levels(state)
    return [*levels, auto] if auto is not None else levels


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
    maps onto the climate's discrete ``fan_mode`` levels and is written via
    ``climate.set_fan_mode`` instead of the ``fan.set_percentage`` used by
    standalone fans. ``fanSpeed.value`` (1..10) spreads over the numbered
    steps while ``fanSpeed.level`` names one of them (or ``auto``).
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
        levels = _climate_fan_levels(state)
        index = _climate_fan_index(state, levels)
        # Read back on the same 1..10 scale the write path spreads over the
        # climate's own steps (an index would mean a different speed per
        # device). 0 is off that scale, which is what an automatic fan mode is.
        value = _fan_step_scale(index, len(levels)) if index is not None else 0
        return make_attribute(ATTR_FAN_SPEED, value, legal="[0, 10]")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        state = ctx.entities.get("value")
        action = ctx.action.name

        if action == ACTION_SET_FAN_SPEED:
            level = _fan_speed_level(ctx.payload)
            if _is_auto_fan_mode(level):
                auto = _climate_auto_fan_mode(state)
                if auto is None:
                    return None
                return [ServiceCall("climate", "set_fan_mode", {"fan_mode": auto}, entity_id)]
            value = _num(_payload_value(ctx.payload, "fanSpeed"))
            if value is None:
                value = _fan_level_scale(level)
            levels = _climate_fan_levels(state)
            if value is None or not levels:
                return None
            index = _fan_scale_to_step(value, len(levels))
            return [ServiceCall("climate", "set_fan_mode", {"fan_mode": levels[index]}, entity_id)]

        if action in (ACTION_INCREMENT_FAN_SPEED, ACTION_DECREMENT_FAN_SPEED):
            steps = _climate_fan_steps(state)
            current = _climate_fan_index(state, steps)
            if current is None:
                return None
            delta = _payload_number(ctx.payload, "deltaValue")
            delta = 1 if delta is None else round(delta)
            step = delta if action == ACTION_INCREMENT_FAN_SPEED else -delta
            index = max(0, min(len(steps) - 1, current + step))
            return [ServiceCall("climate", "set_fan_mode", {"fan_mode": steps[index]}, entity_id)]

        return None

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
        if state is None:
            return make_attribute(ATTR_MODE, "")
        # Modern HA exposes the HVAC mode as the entity *state* (off / cool /
        # ...); Midea / xiaomi AC integrations omit the ``hvac_mode`` attribute
        # entirely. Prefer the state, then fall back to the attribute.
        mode = str(
            getattr(state, "state", "") or state.attributes.get("hvac_mode") or ""
        ).upper()
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
            value, scale = _payload_temperature(ctx.payload)
            if value is None:
                return None
            # The payload scale may be FAHRENHEIT while HA stores the climate
            # target temperature in its configured unit; normalise when known.
            target = _temperature_target_unit(ctx.hass)
            if scale and target and scale.lower() != target.lower():
                value = _convert_temperature(value, scale, target)
            return [ServiceCall("climate", "set_temperature", {"temperature": value}, entity_id)]
        if action in (ACTION_INCREMENT_TEMPERATURE, ACTION_DECREMENT_TEMPERATURE):
            current = _num(state.attributes.get("temperature") if state else None)
            if current is None:
                return None
            step = _num(state.attributes.get("target_temp_step")) if state is not None else None
            delta, scale = _payload_delta_temperature(ctx.payload)
            if delta is None:
                delta = step or 1.0
            else:
                target = _temperature_target_unit(ctx.hass)
                if scale and target and scale.lower() != target.lower():
                    delta = _convert_temperature_delta(delta, scale, target)
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
        # The contract carries the target humidity under ``deltaValue`` (0-100,
        # scale %), not ``humidity``.
        value = _num(_payload_value(ctx.payload, "deltaValue"))
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


# --- contract enum <-> device vocabulary -------------------------------------
#
# Several capabilities are named by a *contract enum* while the entity behind
# them speaks the integration's own vocabulary: SetGearRequest sends
# MIN..MAX/AUTO for a 暖风档位 select labelled 弱暖/强暖/恒温, SetSuctionRequest
# sends STANDARD/STRONG for a vacuum whose fan_speed_list is
# Silent/Standard/Strong/Turbo, and attributes.md fixes the values the reported
# attribute may carry. The helpers below translate both ways and return
# ``None`` when nothing matches, so an unmappable request is answered with
# NotSupportedInCurrentModeError instead of pushing an invalid option into HA
# (and an unmappable reading is omitted instead of reported out of enum).

def _entity_values(state: Any, attr: str) -> list[str]:
    """A list-valued entity attribute as strings (``options`` / ``fan_speed_list``)."""
    if state is None:
        return []
    raw = state.attributes.get(attr)
    if raw is None:
        return []
    if isinstance(raw, (str, bytes)) or not isinstance(raw, Iterable):
        return [str(raw)]
    return [str(value) for value in raw]


def _current_value(state: Any, attr: str | None) -> Any:
    """The current value of a capability's entity.

    ``attr`` names an attribute (a vacuum's ``fan_speed``). Without one the
    value comes from a ``select``, whose current option Home Assistant exposes
    as the entity *state* — the ``option`` attribute is not part of a real
    select entity, so reading only the attribute yields an empty value on every
    device (it is still honoured first for states that carry it).
    """
    if state is None:
        return None
    if attr:
        return state.attributes.get(attr)
    if "option" in state.attributes:
        return state.attributes.get("option")
    return getattr(state, "state", "")


def _contract_token(value: Any, tokens: tuple[str, ...]) -> str | None:
    """``value`` as one of ``tokens`` (case-insensitive), else ``None``."""
    folded = str(value or "").strip().casefold()
    if not folded:
        return None
    return next((token for token in tokens if token.casefold() == folded), None)


def _alias_hit(token: str, candidates: list[str], aliases: Mapping[str, tuple[str, ...]]) -> str | None:
    """The candidate whose label contains one of the token's aliases."""
    wanted = next(
        (values for key, values in aliases.items() if key.casefold() == token.casefold()),
        (),
    )
    for alias in wanted:
        folded = alias.casefold()
        hit = next((c for c in candidates if folded in c.casefold()), None)
        if hit is not None:
            return hit
    return None


def _value_token(value: Any, tokens: tuple[str, ...], aliases: Mapping[str, tuple[str, ...]]) -> str | None:
    """A device value as its contract token (exact token, then aliases).

    The *longest* matching alias wins: aliases are generic words (WORKING owns
    "烘干"), so a more specific one ("烘干完成" under DONE) must not be shadowed
    by whichever token happens to sit earlier in the table. Equal-length
    keywords fall back to table order.
    """
    token = _contract_token(value, tokens)
    if token is not None:
        return token
    folded = str(value or "").strip().casefold()
    if not folded:
        return None
    best: tuple[int, int, str] | None = None
    for order, (key, wanted) in enumerate(aliases.items()):
        canonical = _contract_token(key, tokens)
        if canonical is None:
            # A write-only key (a gear position, say) is not a reportable token.
            continue
        for alias in wanted:
            hit = alias.casefold()
            if hit and hit in folded and (best is None or (len(hit), -order) > best[:2]):
                best = (len(hit), -order, canonical)
    return best[2] if best is not None else None


def _scaled_index(token: str, tokens: tuple[str, ...], count: int) -> int | None:
    """``token``'s index over ``count`` candidates, via its position in ``tokens``.

    Used for the ordered vocabularies (a 档位 / 水位 scale): the token names a
    *position* on the contract's scale, which is spread over the entity's own
    ordered values — the same rule the fan-speed path uses.
    """
    index = next(
        (i for i, t in enumerate(tokens) if t.casefold() == str(token).strip().casefold()),
        None,
    )
    if index is None or count <= 0 or len(tokens) < 2:
        return None
    return round(index / (len(tokens) - 1) * (count - 1))


def enum_value_mapping(
    *,
    entity_id: str,
    attribute_name: str,
    capability_key: str,
    appliance_types: tuple[str, ...],
    tokens: tuple[str, ...],
    write_tokens: tuple[str, ...] | None = None,
    set_action: str = "",
    payload_key: str = "",
    domain: str = "select",
    service: str = "select_option",
    data_key: str = "option",
    options_attr: str = "options",
    read_attr: str | None = None,
    ordered: bool = False,
    allow_custom: bool = False,
    aliases: Mapping[str, tuple[str, ...]] | None = None,
) -> CapabilityMapping:
    """A capability whose values are a contract enum, written as a service value.

    ``tokens`` is the *attribute* vocabulary (what DuerOS sees in
    ``legalValue``); ``write_tokens`` the optional *request* vocabulary when the
    action names values differently (``setGear`` sends the MIN..MAX gear scale
    while the attribute is LOW/MIDDLE/HIGH). ``options_attr`` / ``read_attr``
    point at the candidate list and the current value on the entity (a select's
    ``options`` / ``option`` by default, a vacuum's ``fan_speed_list`` /
    ``fan_speed``). ``ordered`` marks a scale vocabulary, where a token that
    matches no alias is resolved by position; ``aliases`` maps a contract token
    to the device labels it may appear as.

    ``allow_custom`` opens the enum up in both directions for a vocabulary the
    contract itself leaves device-defined (``mode``'s ``customName``): a value
    that matches one of the entity's own candidates is reported (and accepted)
    verbatim, with the entity's candidates as ``legalValue``, instead of being
    dropped as out-of-enum.
    """
    alias_map: Mapping[str, tuple[str, ...]] = aliases or {}
    request_tokens = write_tokens or tokens
    payload_key = payload_key or capability_key
    cap = DuerCapability(
        capability_key,
        "档位",
        kind=CAP_KIND_CONTROL,
        appliance_types=appliance_types,
        attributes=(
            DuerAttribute(
                attribute_name,
                "string",
                legal="(" + ", ".join(tokens) + ")",
            ),
        ),
        actions=(DuerAction(set_action, capability_key, payload_key),) if set_action else (),
    )
    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        value = _current_value(state, read_attr)
        candidates = _entity_values(state, options_attr)
        token = _value_token(value, tokens, alias_map)
        if token is None and ordered:
            text = str(value or "")
            index = candidates.index(text) if text in candidates else None
            # A scale needs at least two steps to have a position at all.
            if index is not None and len(candidates) >= 2:
                token = tokens[round(index / (len(candidates) - 1) * (len(tokens) - 1))]
        if token is None:
            # A custom mode name the contract leaves to the vendor (mode 属性的
            # customName) is reported verbatim; anything else unmappable is
            # omitted rather than reported outside legalValue.
            text = str(value or "").strip()
            if not (allow_custom and text and text in candidates):
                return None
            return make_attribute(
                attribute_name,
                text,
                legal="(" + ", ".join(candidates) + ")" if candidates else "",
            )
        return make_attribute(attribute_name, token, legal="(" + ", ".join(tokens) + ")")

    def write(ctx: WriteContext) -> list[ServiceCall] | None:
        if not set_action or ctx.action.name != set_action:
            return None
        raw = _payload_value(ctx.payload, payload_key)
        text = str(raw).strip() if raw is not None else ""
        if not text:
            return None
        candidates = _entity_values(ctx.entities.get("value"), options_attr)
        # A value the entity itself lists is honored as-is (a custom mode name
        # DuerOS echoes back); everything else has to be a contract token, so a
        # missing payload or a token outside the request vocabulary (the gear
        # scale's AUTO/RANDOM, say) is answered as unsupported instead of being
        # pushed into the entity as if it were a valid label.
        value = _contract_token(text, candidates) if allow_custom else None
        token = _contract_token(text, request_tokens)
        if value is None and token is not None:
            value = _contract_token(token, candidates) or _alias_hit(token, candidates, alias_map)
            if value is None and ordered and len(candidates) >= 2:
                index = _scaled_index(token, request_tokens, len(candidates))
                if index is not None:
                    value = candidates[max(0, min(len(candidates) - 1, index))]
        if value is None:
            return None
        return [ServiceCall(domain, service, {data_key: value}, entity_id)]

    return CapabilityMapping(
        cap, (EntityBinding(entity_id, "value"),), read=read, write=write
    )


def sensor_enum_mapping(
    *,
    entity_id: str,
    attribute_name: str,
    capability_key: str,
    appliance_types: tuple[str, ...],
    tokens: tuple[str, ...],
    aliases: Mapping[str, tuple[str, ...]] | None = None,
    query_names: tuple[str, ...] = (),
) -> CapabilityMapping:
    """A read-only attribute whose value is a contract enum (``workState``).

    ``sensor_query_mapping`` is numeric-only (it drops a non-numeric state), so
    a string-valued enum reading needs its own path; an unmappable value is
    omitted rather than reported outside ``legalValue``.
    """
    alias_map: Mapping[str, tuple[str, ...]] = aliases or {}
    legal = "(" + ", ".join(tokens) + ")"
    cap = DuerCapability(
        capability_key,
        "查询",
        kind=CAP_KIND_QUERY,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(attribute_name, "string", legal=legal),),
        actions=tuple(DuerAction(_query_action_name(q), capability_key) for q in query_names),
        query_names=query_names,
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        token = _value_token(state.state if state is not None else None, tokens, alias_map)
        if token is None:
            return None
        return make_attribute(attribute_name, token, legal=legal)

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read)


# A remaining-time entity reports whatever unit the integration chose; the
# contract's GetTimeLeftResponse is seconds.
_TIME_UNIT_SECONDS = {
    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "hour": 3600,
    "hours": 3600,
    "min": 60,
    "mins": 60,
    "m": 60,
    "minute": 60,
    "minutes": 60,
    "s": 1,
    "sec": 1,
    "secs": 1,
    "second": 1,
    "seconds": 1,
}


def time_left_mapping(
    *,
    entity_id: str,
    appliance_types: tuple[str, ...],
    attribute_name: str = ATTR_TIME_LEFT_IN_SECONDS,
    query_names: tuple[str, ...] = ("GetTimeLeftRequest",),
) -> CapabilityMapping:
    """Remaining run time as ``timeLeftInSeconds`` (``getTimeLeft``).

    The attribute name and the unit both come from the contract
    (``GetTimeLeftResponse.timeLeftInSeconds``, int, seconds) — there is no
    ``timeLeft`` attribute in attributes.md.
    """
    cap = DuerCapability(
        "timeLeft",
        "剩余时间",
        kind=CAP_KIND_QUERY,
        appliance_types=appliance_types,
        attributes=(DuerAttribute(attribute_name, "number", legal="DOUBLE"),),
        actions=tuple(DuerAction(_query_action_name(q), "timeLeft") for q in query_names),
        query_names=query_names,
    )

    def read(ctx: ReadContext) -> AttributeValue | None:
        state = ctx.entities.get("value")
        value = _num(state.state if state is not None else None)
        if value is None:
            return None
        unit = str((state.attributes or {}).get("unit_of_measurement", "")).strip().lower()
        return make_attribute(
            attribute_name, round(value * _TIME_UNIT_SECONDS.get(unit, 1)), legal="DOUBLE"
        )

    return CapabilityMapping(cap, (EntityBinding(entity_id, "value"),), read=read)


__all__ = [
    "power_mapping",
    "mode_switches_mapping",
    "select_mapping",
    "enum_value_mapping",
    "sensor_enum_mapping",
    "time_left_mapping",
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
