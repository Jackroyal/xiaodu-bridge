"""Per-device object config: normalization + accessors for ``options[CONF_DEVICES]``.

``CONF_DEVICES`` stores one *object* per ``device_key``::

    {
      "caps": [cap_key, ...],        # empty / absent = default-all; power implicit
      "bindings": {role: entity_id}, # explicit role -> entity overrides
      "hidden": [entity_id, ...],    # entities never exposed
      "names": {appliance_key: label},
      "mode": "auto" | "generic" | <profile_key>,   # absent = "auto"
    }

Top-level semantics: a missing ``device_key`` means "not selected"; an absent /
``None`` ``devices`` value is the default-all candidate view (every device
exposed, all capabilities). A non-object value is treated as an unconfigured
default-all device.

This module is the single reader of that shape. Normalization is *read-side and
idempotent* (it never writes back): :func:`_clean_object` keeps only the reserved
keys and lightly coerces each field.
"""

from __future__ import annotations

from typing import Any

# Reserved keys that mark a value as the object shape (entity ids never collide:
# HA entity ids always contain a ``.``).
_OBJECT_KEYS = frozenset({"caps", "bindings", "hidden", "names", "mode"})

DEFAULT_MODE = "auto"


def _iter_caps(value: Any) -> tuple[str, ...]:
    """Return the capability keys of a stored ``caps`` value."""
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(c for c in value if isinstance(c, str))
    if isinstance(value, str):
        return (value,)
    return ()


def _clean_object(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only the reserved object keys, lightly coerced."""
    out: dict[str, Any] = {}
    for key in _OBJECT_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if key == "caps":
            out[key] = list(_iter_caps(value))
        elif key in ("bindings", "names"):
            if isinstance(value, dict):
                out[key] = {
                    str(k): str(v)
                    for k, v in value.items()
                    if str(k) and v not in (None, "")
                }
        elif key == "hidden":
            if isinstance(value, (list, tuple)):
                out[key] = [v for v in value if isinstance(v, str)]
        else:  # "mode"
            out[key] = str(value) if value else DEFAULT_MODE
    return out


def normalize(devices: Any) -> dict[str, Any] | None:
    """Normalize the whole ``options[CONF_DEVICES]`` mapping.

    ``None`` passes through (candidate / default-all view). Otherwise returns a
    ``{device_key: object}`` mapping.
    """
    if devices is None:
        return None
    if not isinstance(devices, dict):
        devices = {}
    return {key: normalize_entry(entry) for key, entry in devices.items()}


def normalize_entry(raw: Any) -> dict[str, Any]:
    """Normalize one per-device CONF_DEVICES value into the object shape.

    Only the object shape is recognised; ``None`` or any unexpected non-dict
    value is treated as an unconfigured (default-all) device.
    """
    if not isinstance(raw, dict):
        return {}
    return _clean_object(raw)


def merge_device_obj(stored: Any, adv: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge a stored per-device object with an advanced-edit overlay.

    ``stored`` is the stored per-device object (or ``None``/missing); it is
    normalised first (see :func:`normalize_entry`). ``adv`` is
    the object-shape overlay the advanced options form submits (only the
    reserved ``_OBJECT_KEYS`` are honoured and whole fields replace, so an
    explicit empty ``bindings``/``hidden``/``names`` or ``mode: "auto"`` clears
    a stored value). The result is what the advanced form renders against and
    what ``_save`` persists.
    """
    if not adv:
        return normalize_entry(stored)
    return _clean_object({**normalize_entry(stored), **adv})


def serialize_caps(full_caps: list[str], selected: list[str]) -> list[str]:
    """Map the user's checked capability set to the stored ``caps`` list.

    Stored ``caps`` is a *narrowing* list: ``[]`` (or absent) means default-all
    — every capability the device exposes, including ones added later, so the
    form keeps that dynamic semantic instead of pinning an explicit full list.
    ``power`` is implicit for control appliances (the runtime keeps it no matter
    what), so it is dropped from stored subsets. Rules:

    - every capability checked  -> ``[]`` (default-all, stays dynamic);
    - a strict subset checked    -> exactly those keys, ``power`` omitted;
    - only ``power`` checked     -> ``["power"]`` as a non-empty *power-only*
      marker (an empty list would otherwise read back as default-all).
    """
    available = [cap for cap in (full_caps or []) if cap != "power"]
    chosen = set(selected or ())
    if available and chosen.issuperset(available):
        return []
    if available and not (chosen & set(available)):
        return ["power"] if "power" in (full_caps or []) else []
    return [cap for cap in available if cap in chosen]


def device_caps(obj: Any) -> list[str] | None:
    """Enabled capability keys of a normalized object (None = default-all)."""
    if not isinstance(obj, dict):
        return None
    caps = obj.get("caps")
    if not caps:
        return None
    return list(_iter_caps(caps))


def bindings_of(obj: Any) -> dict[str, str]:
    """Explicit role -> entity id overrides (empty when none)."""
    if not isinstance(obj, dict):
        return {}
    bindings = obj.get("bindings")
    if not isinstance(bindings, dict):
        return {}
    return {
        str(role): str(entity_id)
        for role, entity_id in bindings.items()
        if str(role) and entity_id not in (None, "")
    }


def hidden_of(obj: Any) -> list[str]:
    """Entity ids that must not be exposed by the device (empty when none)."""
    if not isinstance(obj, dict):
        return []
    hidden = obj.get("hidden")
    if not isinstance(hidden, (list, tuple)):
        return []
    return [eid for eid in hidden if isinstance(eid, str)]


def names_of(obj: Any) -> dict[str, str]:
    """Appliance_key -> display-name overrides (empty when none)."""
    if not isinstance(obj, dict):
        return {}
    names = obj.get("names")
    if not isinstance(names, dict):
        return {}
    return {
        str(key): str(label)
        for key, label in names.items()
        if str(key) and label not in (None, "")
    }


def mode_of(obj: Any) -> str:
    """Build mode of the device: ``auto`` / ``generic`` / a profile key."""
    if not isinstance(obj, dict):
        return DEFAULT_MODE
    mode = obj.get("mode", DEFAULT_MODE)
    return str(mode) if mode else DEFAULT_MODE


__all__ = [
    "DEFAULT_MODE",
    "bindings_of",
    "device_caps",
    "hidden_of",
    "merge_device_obj",
    "mode_of",
    "names_of",
    "normalize",
    "normalize_entry",
    "serialize_caps",
]
