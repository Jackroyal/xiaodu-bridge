"""Domain adapters: map Home Assistant entities to Xiaodu appliances.

One adapter describes one HA domain: which Xiaodu appliance type it becomes,
which actions it accepts, how to describe itself at discovery, how to read
its current attributes, and how to translate a whitelisted action into an HA
service call.

Adding support for a new domain is a single file-local change: subclass
``XiaoduAdapter``, set ``domain`` / ``appliance_type`` / ``actions``, override
``query_attributes`` and/or ``service_call``, and decorate it with
``@register``. The protocol dispatcher (``protocol.py``) never branches on
domain names itself, so capability growth stays additive instead of turning
into one long if/else chain.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import State

from ..devices import DEVICE_CLASS_AUTO, DEVICE_CLASS_YUBA
from .constants import (
    ACTION_CONTINUE,
    ACTION_SET_FAN_SPEED,
    ACTION_SET_BRIGHTNESS,
    ACTION_SET_COLOR,
    ACTION_SET_COLOR_TEMPERATURE,
    ACTION_SET_HUMIDITY,
    ACTION_SET_MODE,
    ACTION_PAUSE,
    ACTION_SET_SUCTION,
    ACTION_SET_TEMPERATURE,
    ACTION_SET_TV_CHANNEL,
    ACTION_SET_VOLUME,
    ACTION_SET_VOLUME_MUTE,
    ACTION_TURN_OFF,
    ACTION_TURN_ON,
    ACTION_UNSET_MODE,
    APPLIANCE_AIR_CONDITION,
    APPLIANCE_CURTAIN,
    APPLIANCE_FAN,
    APPLIANCE_HUMIDIFIER,
    APPLIANCE_LIGHT,
    APPLIANCE_SENSOR,
    APPLIANCE_SWEEPING_ROBOT,
    APPLIANCE_SWITCH,
    APPLIANCE_TV_SET,
    APPLIANCE_YUBA,
    APP_VERSION,
)

def _now() -> int:
    return int(time.time())


def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _attr(
    name: str, value: Any, scale: str = "", legal: str = ""
) -> dict[str, Any]:
    """Build a Xiaodu attribute object."""
    attr: dict[str, Any] = {
        "name": name,
        "value": value,
        "scale": scale,
        "timestampOfSample": _now(),
        "uncertaintyInMilliseconds": 1000,
    }
    if legal:
        attr["legalValue"] = legal
    return attr


def _reachable(state: State) -> bool:
    # Only "unavailable" means the device is offline. "unknown" just means the
    # state has not been reported yet (e.g. a Xiaomi airer before first move);
    # such devices are connected and can still accept commands.
    return state.state != "unavailable"


def _connectivity_attr(state: State) -> dict[str, Any]:
    return _attr(
        "connectivity",
        "REACHABLE" if _reachable(state) else "UNREACHABLE",
        legal="(UNREACHABLE, REACHABLE)",
    )


def _power_state(state: State) -> str:
    """Return ON/OFF for the entity, mapping cover open/closed onto on/off."""
    if state.domain == "cover":
        return "ON" if state.state in ("open", "opening") else "OFF"
    return "ON" if state.state == "on" else "OFF"


def _mireds_to_kelvin(mireds: Any) -> float | None:
    """Convert a mired color-temperature value to Kelvin."""
    value = _num(mireds)
    return round(1_000_000.0 / value) if value else None


def _color_temp_kelvin(state: State) -> float | None:
    """Return the current color temperature in Kelvin, if known."""
    kelvin = state.attributes.get("color_temp_kelvin")
    if kelvin is not None:
        return round(float(kelvin))
    return _mireds_to_kelvin(state.attributes.get("color_temp"))


def _color_temp_bounds(state: State) -> tuple[float, float]:
    """Return (min_kelvin, max_kelvin) supported by the device."""
    min_kelvin = _num(state.attributes.get("color_temp_min_kelvin"))
    max_kelvin = _num(state.attributes.get("color_temp_max_kelvin"))
    if min_kelvin is None:
        # mireds: color_temp_min is the *smallest* mired value (= hottest).
        min_kelvin = _mireds_to_kelvin(state.attributes.get("color_temp_max"))
    if max_kelvin is None:
        max_kelvin = _mireds_to_kelvin(state.attributes.get("color_temp_min"))
    return (min_kelvin or 1000.0, max_kelvin or 10000.0)


def _supports_color_temp(state: State) -> bool:
    """Return True when the entity can be controlled by color temperature."""
    modes = state.attributes.get("supported_color_modes") or ()
    if "color_temp" in modes or "color_temp_kelvin" in modes:
        return True
    return (
        state.attributes.get("color_temp") is not None
        or state.attributes.get("color_temp_kelvin") is not None
        or state.attributes.get("color_temp_min") is not None
        or state.attributes.get("color_temp_min_kelvin") is not None
    )


class XiaoduAdapter:
    """Base adapter for one HA domain."""

    domain: str = ""
    appliance_type: str = ""
    actions: tuple[str, ...] = ()

    def build_appliance(
        self,
        state: State,
        *,
        unit: Any = None,
        device: Any = None,
    ) -> dict[str, Any] | None:
        """Build the Xiaodu appliance object (None when unsupported)."""
        if not self.appliance_type:
            return None
        name = state.attributes.get("friendly_name") or state.entity_id
        return {
            "applianceId": state.entity_id,
            "friendlyName": name,
            "friendlyDescription": name,
            "additionalApplianceDetails": {},
            "applianceTypes": [self.appliance_type],
            "isReachable": _reachable(state),
            "manufacturerName": "Home Assistant",
            "modelName": "Xiaodu",
            "version": APP_VERSION,
            "actions": self.actions_for(state),
            "attributes": self.query_attributes(state, unit=unit, device=device),
        }

    def actions_for(self, state: State) -> list[str]:
        """Return the actions available for a specific device state."""
        return list(self.actions)

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        """Return the current attribute values for a query response."""
        return []

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | list[tuple[str, str, dict[str, Any]]] | None:
        """Map a whitelisted action to an HA service call (or calls), or None.

        Most adapters return a single ``(domain, service, data)`` tuple; an
        adapter may return a list when one speaker action fans out to several
        entities (e.g. turning a YUBA off shuts down light + functions). The
        ``data`` dict may carry an explicit ``entity_id`` to target a sibling
        entity instead of the appliance's own entity.
        """
        return None


class _PowerDeviceAdapter(XiaoduAdapter):
    """Shared implementation for on/off devices (switch, fan, climate, ...)."""

    actions = (ACTION_TURN_ON, ACTION_TURN_OFF)

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        return [
            _attr("turnOnState", _power_state(state), legal="(ON, OFF)"),
            _connectivity_attr(state),
        ]

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_TURN_ON:
            return (self.domain, "turn_on", {})
        if action == ACTION_TURN_OFF:
            return (self.domain, "turn_off", {})
        return None


class _Registry:
    """Adapters keyed by (HA domain, device class).

    The default device class (``DEVICE_CLASS_AUTO``) holds the per-domain
    adapter; classified devices (e.g. a bathroom heater whose light is the
    YUBA master) override it with a dedicated adapter.
    """

    def __init__(self) -> None:
        self._adapters: dict[tuple[str, str], XiaoduAdapter] = {}

    def register(
        self,
        adapter_cls: type[XiaoduAdapter],
        device_class: str = DEVICE_CLASS_AUTO,
    ) -> type[XiaoduAdapter]:
        instance = adapter_cls()
        self._adapters[(instance.domain, device_class)] = instance
        return adapter_cls

    def get(
        self, domain: str, device_class: str = DEVICE_CLASS_AUTO
    ) -> XiaoduAdapter | None:
        return self._adapters.get(
            (domain, device_class)
        ) or self._adapters.get((domain, DEVICE_CLASS_AUTO))


REGISTRY = _Registry()


def register(
    adapter_cls: type[XiaoduAdapter] | None = None,
    *,
    device_class: str = DEVICE_CLASS_AUTO,
) -> Any:
    """Decorator: ``@register`` or ``@register(device_class=...)``."""

    def wrap(cls: type[XiaoduAdapter]) -> type[XiaoduAdapter]:
        REGISTRY.register(cls, device_class=device_class)
        return cls

    if adapter_cls is None:
        return wrap
    return wrap(adapter_cls)


def get_adapter(domain: str, device_class: str = DEVICE_CLASS_AUTO) -> XiaoduAdapter | None:
    """Return the adapter registered for an HA domain (+ device class), if any."""
    return REGISTRY.get(domain, device_class)


@register
class LightAdapter(_PowerDeviceAdapter):
    domain = "light"
    appliance_type = APPLIANCE_LIGHT
    actions = (
        ACTION_TURN_ON,
        ACTION_TURN_OFF,
        ACTION_SET_BRIGHTNESS,
        ACTION_SET_COLOR,
    )

    def actions_for(self, state: State) -> list[str]:
        """Advertise color-temperature control only when the device supports it."""
        actions = super().actions_for(state)
        if _supports_color_temp(state):
            actions.append(ACTION_SET_COLOR_TEMPERATURE)
        return actions

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        attrs = super().query_attributes(state, unit=unit, device=device)
        if (brightness := state.attributes.get("brightness")) is not None:
            attrs.append(
                _attr("brightness", f"{brightness / 255 * 100:.1f}", legal="[0, 100]")
            )
        kelvin = _color_temp_kelvin(state)
        if kelvin is not None:
            lo, hi = _color_temp_bounds(state)
            attrs.append(
                _attr(
                    "colorTemperatureInKelvin",
                    kelvin,
                    scale="K",
                    legal=f"[{int(lo)}, {int(hi)}]",
                )
            )
        return attrs

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_SET_BRIGHTNESS:
            value = _num((payload.get("brightness") or {}).get("value"))
            if value is None:
                return None
            return (
                "light",
                "turn_on",
                {"brightness_pct": max(0.0, min(100.0, value))},
            )
        if action == ACTION_SET_COLOR:
            color = payload.get("color") or {}
            hue = _num(color.get("hue"))
            saturation = _num(color.get("saturation"))
            if hue is None or saturation is None:
                return None
            return ("light", "turn_on", {"hs_color": [hue, saturation * 100]})
        if action == ACTION_SET_COLOR_TEMPERATURE:
            kelvin = _num((payload.get("colorTemperature") or {}).get("value"))
            if kelvin is None:
                return None
            lo, hi = _color_temp_bounds(state)
            return (
                "light",
                "turn_on",
                {"color_temp_kelvin": max(lo, min(hi, kelvin))},
            )
        return super().service_call(state, action, payload, unit=unit, device=device)


@register
class SwitchAdapter(_PowerDeviceAdapter):
    domain = "switch"
    appliance_type = APPLIANCE_SWITCH


@register
class FanAdapter(_PowerDeviceAdapter):
    domain = "fan"
    appliance_type = APPLIANCE_FAN
    actions = (ACTION_TURN_ON, ACTION_TURN_OFF, ACTION_SET_FAN_SPEED)

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        attrs = super().query_attributes(state, unit=unit, device=device)
        if (pct := state.attributes.get("percentage")) is not None:
            attrs.append(_attr("fanSpeed", round(float(pct) / 10), legal="[0, 10]"))
        return attrs

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_SET_FAN_SPEED:
            value = _num((payload.get("fanSpeed") or {}).get("value"))
            if value is None:
                return None
            return (
                "fan",
                "set_percentage",
                {"percentage": max(0, min(10, round(value))) * 10},
            )
        return super().service_call(state, action, payload, unit=unit, device=device)


@register
class ClimateAdapter(_PowerDeviceAdapter):
    domain = "climate"
    appliance_type = APPLIANCE_AIR_CONDITION
    actions = (
        ACTION_TURN_ON,
        ACTION_TURN_OFF,
        ACTION_SET_TEMPERATURE,
        ACTION_SET_MODE,
    )

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        attrs = super().query_attributes(state, unit=unit, device=device)
        if (temp := state.attributes.get("temperature")) is not None:
            attrs.append(
                _attr("targetTemperature", temp, scale="CELSIUS", legal="DOUBLE")
            )
        if (mode := state.attributes.get("hvac_mode")) is not None:
            attrs.append(_attr("mode", str(mode).upper()))
        return attrs

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_SET_TEMPERATURE:
            value = _num((payload.get("temperature") or {}).get("value"))
            if value is None:
                return None
            return ("climate", "set_temperature", {"temperature": value})
        if action == ACTION_SET_MODE:
            mode = (payload.get("mode") or {}).get("value")
            if not mode:
                return None
            return ("climate", "set_hvac_mode", {"hvac_mode": str(mode).lower()})
        return super().service_call(state, action, payload, unit=unit, device=device)


@register
class MediaPlayerAdapter(_PowerDeviceAdapter):
    domain = "media_player"
    appliance_type = APPLIANCE_TV_SET
    actions = (
        ACTION_TURN_ON,
        ACTION_TURN_OFF,
        ACTION_SET_VOLUME,
        ACTION_SET_VOLUME_MUTE,
        ACTION_SET_TV_CHANNEL,
    )

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        attrs = super().query_attributes(state, unit=unit, device=device)
        if (level := state.attributes.get("volume_level")) is not None:
            attrs.append(_attr("volume", round(float(level) * 100), legal="[0, 100]"))
        if (muted := state.attributes.get("is_volume_muted")) is not None:
            attrs.append(_attr("muteState", bool(muted), legal="(true, false)"))
        if (source := state.attributes.get("source")) is not None:
            attrs.append(_attr("channel", str(source)))
        return attrs

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_SET_VOLUME:
            value = _num((payload.get("volume") or {}).get("value"))
            if value is None:
                return None
            return (
                "media_player",
                "volume_set",
                {"volume_level": max(0.0, min(100.0, value)) / 100},
            )
        if action == ACTION_SET_VOLUME_MUTE:
            mute = payload.get("mute", payload.get("muteState"))
            if not isinstance(mute, bool):
                return None
            return ("media_player", "volume_mute", {"is_volume_muted": mute})
        if action == ACTION_SET_TV_CHANNEL:
            channel = (payload.get("channel") or {}).get("value")
            if channel is None:
                return None
            return ("media_player", "select_source", {"source": str(channel)})
        return super().service_call(state, action, payload, unit=unit, device=device)


@register
class CoverAdapter(_PowerDeviceAdapter):
    domain = "cover"
    appliance_type = APPLIANCE_CURTAIN
    actions = (ACTION_TURN_ON, ACTION_TURN_OFF, ACTION_PAUSE)

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_TURN_ON:
            return ("cover", "open_cover", {})
        if action == ACTION_TURN_OFF:
            return ("cover", "close_cover", {})
        if action == ACTION_PAUSE:
            return ("cover", "stop_cover", {})
        return None


@register
class SensorAdapter(XiaoduAdapter):
    """Read-only temperature/humidity sensors."""

    domain = "sensor"
    appliance_type = APPLIANCE_SENSOR
    actions = ()

    def build_appliance(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> dict[str, Any] | None:
        if not self.query_attributes(state, unit=unit, device=device):
            return None
        return super().build_appliance(state, unit=unit, device=device)

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        unit = str(state.attributes.get("unit_of_measurement", "")).lower()
        device_class = str(state.attributes.get("device_class", "")).lower()
        value = _num(state.state)
        if value is None:
            return []
        # Fahrenheit must be checked before the generic temperature branch
        # (a °F sensor usually also sets device_class=temperature).
        if "°f" in unit:
            return [_attr("temperature", value, scale="FAHRENHEIT", legal="DOUBLE")]
        if device_class == "temperature" or "°c" in unit or "℃" in unit or unit == "c" or "temperature" in unit:
            return [_attr("temperature", value, scale="CELSIUS", legal="DOUBLE")]
        if device_class == "humidity" or "humidity" in unit:
            return [_attr("humidity", value, scale="%", legal="[0, 100]")]
        return []


@register
class HumidifierAdapter(_PowerDeviceAdapter):
    domain = "humidifier"
    appliance_type = APPLIANCE_HUMIDIFIER
    actions = (
        ACTION_TURN_ON,
        ACTION_TURN_OFF,
        ACTION_SET_HUMIDITY,
        ACTION_SET_MODE,
    )

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        attrs = super().query_attributes(state, unit=unit, device=device)
        if (hum := state.attributes.get("humidity")) is not None:
            attrs.append(_attr("targetHumidity", hum, scale="%", legal="[0, 100]"))
        if (mode := state.attributes.get("mode")) is not None:
            attrs.append(_attr("mode", str(mode).upper()))
        return attrs

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_SET_HUMIDITY:
            value = _num((payload.get("humidity") or {}).get("value"))
            if value is None:
                return None
            return (
                "humidifier",
                "set_humidity",
                {"humidity": max(0, min(100, round(value)))},
            )
        if action == ACTION_SET_MODE:
            mode = (payload.get("mode") or {}).get("value")
            if not mode:
                return None
            return ("humidifier", "set_mode", {"mode": str(mode).lower()})
        return super().service_call(state, action, payload, unit=unit, device=device)


@register
class VacuumAdapter(_PowerDeviceAdapter):
    domain = "vacuum"
    appliance_type = APPLIANCE_SWEEPING_ROBOT
    actions = (ACTION_TURN_ON, ACTION_TURN_OFF, ACTION_SET_SUCTION, ACTION_CONTINUE)

    def query_attributes(
        self, state: State, *, unit: Any = None, device: Any = None
    ) -> list[dict[str, Any]]:
        attrs = super().query_attributes(state, unit=unit, device=device)
        if (speed := state.attributes.get("fan_speed")) is not None:
            attrs.append(_attr("suction", str(speed)))
        return attrs

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | None:
        if action == ACTION_TURN_ON:
            return ("vacuum", "start", {})
        if action == ACTION_TURN_OFF:
            return ("vacuum", "stop", {})
        if action == ACTION_CONTINUE:
            return ("vacuum", "start", {})
        if action == ACTION_SET_SUCTION:
            value = (payload.get("suction") or {}).get("value")
            if value is None:
                return None
            return ("vacuum", "set_fan_speed", {"fan_speed": str(value)})
        if action == ACTION_SET_MODE:
            # Xiaodu mode (清扫模式: 安静/标准/强力) maps to the fan-speed level.
            mode = (payload.get("mode") or {}).get("value")
            if not mode:
                return None
            return ("vacuum", "set_fan_speed", {"fan_speed": str(mode)})
        return None


# --- YUBA (浴霸) ------------------------------------------------------------

# Mode value (reported in the ``mode`` attribute legalValue) -> semantic
# control name on the device (see ``XiaoduDevice.controls``).
_YUBA_MODES: tuple[tuple[str, str], ...] = (
    ("暖风", "heating"),
    ("吹风", "blow"),
    ("换气", "ventilation"),
    ("照明", "light"),
)


def _yuba_mode_controls(device: Any) -> list[tuple[str, str | None]]:
    """Return (mode value, entity id) pairs for a YUBA device's functions."""
    controls = getattr(device, "controls", {}) or {}
    return [(mode, controls.get(control)) for mode, control in _YUBA_MODES]


def _mode_value(payload: dict[str, Any]) -> str:
    return str((payload.get("mode") or {}).get("value") or "")


@register(device_class=DEVICE_CLASS_YUBA)
class YubaAdapter(LightAdapter):
    """YUBA (浴霸) master: the bathroom heater exposed as one appliance.

    The default unit of a YUBA-classified device is its light; the adapter
    treats the appliance as the whole heater:

    - turnOn  -> 照明 (light on)
    - turnOff -> everything off (light + 取暖/吹风/换气)
    - setMode 暖风/吹风/换气/照明 -> switch that function on
    - unSetMode <mode> -> switch that function off (no mode: everything off)
    - setTemperature -> the 设定温度 number entity on the device

    Brightness / color / color temperature pass through to the light like a
    normal LIGHT appliance.
    """

    domain = "light"
    appliance_type = APPLIANCE_YUBA
    actions = (
        ACTION_TURN_ON,
        ACTION_TURN_OFF,
        ACTION_SET_BRIGHTNESS,
        ACTION_SET_COLOR,
        ACTION_SET_COLOR_TEMPERATURE,
        ACTION_SET_MODE,
        ACTION_UNSET_MODE,
        ACTION_SET_TEMPERATURE,
    )

    def service_call(
        self,
        state: State,
        action: str,
        payload: dict[str, Any],
        *,
        unit: Any = None,
        device: Any = None,
    ) -> tuple[str, str, dict[str, Any]] | list[tuple[str, str, dict[str, Any]]] | None:
        if action == ACTION_SET_MODE:
            return self._function_call(payload, "turn_on", device)
        if action == ACTION_UNSET_MODE:
            if _mode_value(payload):
                return self._function_call(payload, "turn_off", device)
            return self._all_function_calls("turn_off", device)
        if action == ACTION_SET_TEMPERATURE:
            value = _num((payload.get("temperature") or {}).get("value"))
            controls = getattr(device, "controls", {}) or {}
            target = controls.get("target_temperature")
            if value is None or not target:
                return None
            return ("number", "set_value", {"entity_id": target, "value": value})
        if action == ACTION_TURN_OFF:
            return self._all_function_calls("turn_off", device)
        return super().service_call(state, action, payload, unit=unit, device=device)

    def _function_call(
        self,
        payload: dict[str, Any],
        service: str,
        device: Any,
    ) -> tuple[str, str, dict[str, Any]] | None:
        mode = _mode_value(payload)
        target = dict(_yuba_mode_controls(device)).get(mode)
        if not target:
            return None
        return (
            "light" if target.startswith("light.") else "switch",
            service,
            {"entity_id": target},
        )

    def _all_function_calls(
        self, service: str, device: Any
    ) -> list[tuple[str, str, dict[str, Any]]]:
        calls: list[tuple[str, str, dict[str, Any]]] = []
        for _mode, target in _yuba_mode_controls(device):
            if not target:
                continue
            calls.append(
                (
                    "light" if target.startswith("light.") else "switch",
                    service,
                    {"entity_id": target},
                )
            )
        return calls


def extra_attributes(
    hass: Any, unit: Any, device: Any
) -> list[dict[str, Any]]:
    """Return device-level structural attributes for a classified appliance.

    Currently YUBA only: the current ``mode`` and the ``targetTemperature``
    of the 设定温度 number entity. Both are reported unconditionally (they map
    to capabilities that are implied-enabled on the YUBA master).
    """
    if getattr(unit, "device_class", "") != DEVICE_CLASS_YUBA:
        return []
    attrs: list[dict[str, Any]] = []
    current = ""
    for mode, target in _yuba_mode_controls(device):
        if not target:
            continue
        state = hass.states.get(target)
        if state is not None and state.state == "on":
            current = mode
            break
    attrs.append(
        _attr(
            "mode",
            current,
            legal="(照明, 暖风, 吹风, 换气)",
        )
    )
    controls = getattr(device, "controls", {}) or {}
    target = controls.get("target_temperature")
    if target:
        state = hass.states.get(target)
        if state is not None and state.state not in ("unknown", "unavailable"):
            value = _num(state.state)
            if value is not None:
                attrs.append(
                    _attr("targetTemperature", value, scale="CELSIUS", legal="DOUBLE")
                )
    return attrs
