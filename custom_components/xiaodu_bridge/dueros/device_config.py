"""Per-device object config: normalization + accessors for ``options[CONF_DEVICES]``.

``CONF_DEVICES`` has historically stored two shapes per ``device_key``::

    {device_key: [cap_key, ...]}            # flat device-level capability list
    {device_key: {entity_id: [cap_key]}}    # legacy per-entity dict

Stage B evolves each value into an *object* with optional fields::

    {
      "caps": [cap_key, ...],        # empty / absent = default-all; power implicit
      "bindings": {role: entity_id}, # explicit role -> entity overrides
      "hidden": [entity_id, ...],    # entities never exposed
      "names": {appliance_key: label},
      "mode": "auto" | "generic" | <profile_key>,   # absent = "auto"
    }

Top-level semantics are preserved: a missing ``device_key`` means "not
selected"; an absent / ``None`` ``devices`` value is the default-all candidate
view (every device exposed, all capabilities).

This module is the single reader of that shape. Normalization is *read-side and
idempotent* (it never writes back) and therefore migrates old list / per-entity
configs on the fly for both runtime building and the options UI. Per-entity
dicts migrate by *unioning* every entity's capability list into ``caps`` (an
all-empty table / empty list -> empty ``caps`` = default-all). Hidden entities
are **never** inferred from the per-entity shape.

Legacy *mixed* per-entity dicts such as ``{A: ["power"], B: []}``: the old
reader treated B's empty table as "default-all for B", while the union rule
below deliberately converges to the non-empty union (``["power"]``) — an empty
entity contributes nothing and only a device whose *every* entity table is
empty becomes default-all. This is an intentional behaviour tightening on
migration, not a bug.
"""

from __future__ import annotations

from typing import Any

# Reserved keys that mark a value as the object shape (entity ids never collide:
# HA entity ids always contain a ``.``).
_OBJECT_KEYS = frozenset({"caps", "bindings", "hidden", "names", "mode"})

DEFAULT_MODE = "auto"


def _iter_caps(value: Any) -> tuple[str, ...]:
    """Return the capability keys of one per-entity / list element."""
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        return tuple(c for c in value if isinstance(c, str))
    if isinstance(value, str):
        return (value,)
    return ()


def _union_caps(mapping: dict[str, Any]) -> list[str]:
    """Union every per-entity capability list into one device-level list."""
    seen: list[str] = []
    for value in mapping.values():
        for cap in _iter_caps(value):
            if cap not in seen:
                seen.append(cap)
    return seen


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
    ``{device_key: object}`` mapping, migrating every legacy entry.
    """
    if devices is None:
        return None
    if not isinstance(devices, dict):
        devices = {}
    return {key: normalize_entry(entry) for key, entry in devices.items()}


def normalize_entry(raw: Any) -> dict[str, Any]:
    """Normalize one per-device CONF_DEVICES value into the object shape."""
    if raw is None:
        return {}
    if isinstance(raw, (list, tuple)):
        # Flat device-level capability list (current simple-UI shape).
        return {"caps": list(_iter_caps(raw))}
    if not isinstance(raw, dict):
        # Unexpected scalar: treat as an unconfigured (default-all) device.
        return {}
    if _OBJECT_KEYS & raw.keys():
        # Already the object shape; keep it (lightly cleaned).
        return _clean_object(raw)
    # Legacy per-entity dict: union each entity's capability list into ``caps``.
    return {"caps": _union_caps(raw)}


def merge_device_obj(stored: Any, adv: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge a stored per-device object with an advanced-edit overlay.

    ``stored`` may be any legacy shape (flat list / per-entity dict / object /
    ``None``); it is normalised first (see :func:`normalize_entry`). ``adv`` is
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
