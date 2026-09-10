"""Runtime wiring for the DuerOS semantic model (sole/default path).

The device-center semantic model is the only runtime path. Every exposable HA
device is surfaced as one or more ``DuerDevice`` appliances:

1. A device that matches a declared profile (YUBA, CLOTHES_RACK, ...) is built
   by that profile (aggregating several entities into one appliance).
2. Every other device is built by ``build_default_devices`` (per-domain
   composers), so lights, switches, sensors, fans, climate, media players etc.
   all flow through the same semantic model.

``build_enhanced_device_set`` optionally filters by ``options[CONF_DEVICES]``
(device_key -> a per-device object from ``dueros.device_config`` with optional
caps / bindings / hidden / names / mode), matching the "设备 → 能力" options UI
and its per-device override sub-flow.
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Mapping
from typing import Any, Callable

from .. import devices as device_mod
from ..const import CONF_DEVICES, CONF_SYNC_AREAS
from .defaults import build_default_devices
from .device_config import (
    bindings_of,
    device_caps,
    hidden_of,
    mode_of,
    names_of,
    normalize,
    normalize_entry,
)
from .model import DeviceBuildContext, DuerDevice
from .profiles import register_default_profiles
from .registry import REGISTRY

# Profile keys whose build surfaces one *aggregate* appliance. Their stable
# ``appliance_key`` (the ``names`` map key) is the profile key itself, distinct
# from per-entity generic/leftover appliances that key on domain + stable id.
PROFILE_AGGREGATE_KEYS = frozenset(
    {"YUBA", "SWEEPING_ROBOT", "CLOTHES_RACK", "WASHING_MACHINE"}
)
_SENSOR_KEY = "SENSOR"

_LOGGER = logging.getLogger(__name__)


class EnhancedDeviceSet:
    """Holds the enrolled DuerOS devices plus the entity ids they claim."""

    def __init__(
        self,
        devices: list[DuerDevice] | None = None,
        claimed_entity_ids: set[str] | None = None,
        *,
        enabled: bool = True,
        sync_areas: bool = False,
        areas: dict[str, str] | None = None,
    ) -> None:
        self._devices = list(devices or [])
        self._claimed = set(claimed_entity_ids or ())
        self.enabled = enabled
        self.sync_areas = sync_areas
        self._areas = dict(areas or {})
        self._by_id = {d.device_id: d for d in self._devices}

    def all(self) -> list[DuerDevice]:
        return list(self._devices)

    def resolve(self, appliance_id: str) -> DuerDevice | None:
        return self._by_id.get(appliance_id)

    def area(self, appliance_id: str) -> str | None:
        """Return the HA room (area) name of an appliance, if known."""
        return self._areas.get(appliance_id)

    @property
    def claimed_entity_ids(self) -> frozenset[str]:
        return frozenset(self._claimed)

    def __bool__(self) -> bool:
        return self.enabled and bool(self._devices)


def _group_by_device(
    states: list[Any], device_of: Callable[[str], str | None]
) -> dict[str, list[Any]]:
    groups: dict[str, list[Any]] = {}
    for state in states:
        key = device_of(getattr(state, "entity_id", "")) or getattr(state, "entity_id", "")
        groups.setdefault(key, []).append(state)
    return groups


def _display_name(
    states: list[Any], name_of: Callable[[str], str | None] | None, key: str
) -> str:
    if name_of and (name := name_of(key)):
        return name
    for state in states:
        friendly = (getattr(state, "attributes", None) or {}).get("friendly_name")
        if friendly:
            return str(friendly)
    return key


def _filter_device(device: DuerDevice, caps: list[str] | None) -> DuerDevice | None:
    """Drop capabilities not in ``caps`` (a list of capability keys).

    ``caps`` of ``None``/empty keeps every capability (default-all). ``power``
    is always kept for control appliances. A device left with no capability is
    dropped. This is the *only* capability-narrowing point: it is applied
    uniformly to profile aggregates, generic devices, leftover appliances and
    sensor aggregates.
    """
    if not caps:
        return device
    selected = set(caps)
    kept = tuple(
        cap for cap in device.capabilities if cap.key in selected or cap.key == "power"
    )
    if not kept:
        return None
    return DuerDevice(
        device_id=device.device_id,
        friendly_name=device.friendly_name,
        profile_key=device.profile_key,
        primary_entity_id=device.primary_entity_id,
        capabilities=kept,
        is_reachable=device.is_reachable,
        appliance_types=device.appliance_types,
    )


def role_candidate_entities(
    entities: list[dict[str, Any]], allowed_domains: tuple[str, ...]
) -> list[dict[str, Any]]:
    """Filter a device's entities to those a semantic role may be bound to.

    Roles drive capabilities whose composers assume specific HA domains (e.g. a
    YUBA ``heating`` composite_power hardcodes domain "switch"); binding a role
    to an entity outside its allowed domains would produce a broken mapping, so
    the options flow only offers in-domain, non-auxiliary entities. Entities are
    ``{id, label, domain, is_aux}`` dicts (see :func:`build_device_detail`).
    """
    allowed = set(allowed_domains or ())
    return [e for e in entities if e["domain"] in allowed and not e["is_aux"]]


def role_binding_specs(
    profile: Any, group_entities: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    """Per-role binding candidates of a profile for one device group.

    The advanced form renders a role-binding picker for *every* declared role —
    a role with no in-domain entity simply offers only 自动识别 rather than
    disappearing (hiding 暖风档位 / 风速档位 / 设定温度 on real 浴霸 devices was a
    regression) — so every ``profile.roles`` key is present here. Its value is
    the (possibly empty) list of candidate entities on this device (domain ∈
    ``role_domains[role]``, non-aux — the same rule as
    :func:`role_candidate_entities`).
    """
    specs: dict[str, list[dict[str, Any]]] = {}
    for role in profile.roles:
        specs[role] = role_candidate_entities(
            group_entities, profile.role_domains.get(role) or ()
        )
    return specs


class AdvFieldMap(dict[str, tuple[str, str]]):
    """Forward ``{display: (kind, key)}`` field map plus reverse lookups.

    The advanced form's role-binding / rename widgets are keyed by *display*
    labels (取暖 / 浴霸); iterating this dict yields those
    ``{display: (kind, key)}`` rows so the submit path can restore the submitted
    values onto the canonical ``bindings`` (role) / ``names`` (appliance_key)
    keys. The reverse tables turn a canonical ``role`` / ``appliance_key`` back
    into its display label — provided ready-built because the flow re-deriving
    them from the forward rows was the source of a past variable-shadowing bug.
    """

    def __init__(
        self,
        mapping: dict[str, tuple[str, str]],
        *,
        role_to_display: dict[str, str],
        appliance_to_display: dict[str, str],
    ) -> None:
        super().__init__(mapping)
        # role -> its rendered display label (the readable schema key).
        self.role_to_display: dict[str, str] = role_to_display
        # appliance_key -> its rendered display label (the readable schema key).
        self.appliance_to_display: dict[str, str] = appliance_to_display


def adv_field_map(
    profile_roles: dict[str, str],
    appliances: list[dict[str, Any]],
) -> AdvFieldMap:
    """Map readable Chinese schema keys to their stored ``(kind, key)`` field.

    The advanced form's role-binding and appliance-rename fields are labelled by
    *display* text (a profile role label such as 取暖, or an appliance label such
    as 浴霸  灯). The HA front end renders an untranslated schema key verbatim,
    so keying those fields by ``role:<role>`` / ``name:<appliance_key>`` leaked
    raw keys (``role:heating``, ``name:light:xiaomi_home...``). The returned
    :class:`AdvFieldMap` is that ``{readable_key: ("role", role) | ("name",
    appliance_key)}`` forward table the submit path uses to restore submitted
    values onto the stored ``bindings`` / ``names`` keys, and also carries the
    pre-built reverse tables ``role_to_display`` / ``appliance_to_display`` for
    the render path (role names / appliance keys are the reverse keys).

    ``profile_roles`` maps the *rendered* role keys to their Chinese labels;
    ``appliances`` are the ``{appliance_key, label, ...}`` rows from
    ``build_device_detail``. Readable keys are unique across the whole form: a
    duplicate label gets a ``label（2）``-style suffix. Role labels are allocated
    first, so a rename appliance whose label collides with a role label falls
    back to the suffixed key.
    """
    used: set[str] = set()
    mapping: dict[str, tuple[str, str]] = {}
    role_to_display: dict[str, str] = {}
    appliance_to_display: dict[str, str] = {}

    def _unique(label: str) -> str:
        if label not in used:
            used.add(label)
            return label
        index = 2
        while f"{label}（{index}）" in used:
            index += 1
        key = f"{label}（{index}）"
        used.add(key)
        return key

    for role, label in profile_roles.items():
        display = _unique(label)
        mapping[display] = ("role", role)
        role_to_display[role] = display
    for appliance in appliances:
        key = appliance["appliance_key"]
        label = str(appliance["label"])
        display = _unique(label)
        mapping[display] = ("name", key)
        appliance_to_display[key] = display
    return AdvFieldMap(
        mapping,
        role_to_display=role_to_display,
        appliance_to_display=appliance_to_display,
    )


def restore_bindings_and_names(
    user_input: Mapping[str, Any],
    field_map: AdvFieldMap,
    *,
    default_labels: Mapping[str, str] | None = None,
    auto_value: str = "__auto__",
    roles_section: str = "role_bindings",
    names_section: str = "device_names",
) -> tuple[dict[str, str], dict[str, str]]:
    """Restore submitted role/rename fields onto canonical stored keys.

    ``user_input`` is the validated payload of the advanced options step, whose
    role-binding and appliance-rename widgets live *inside* their form sections:
    ``user_input[roles_section]`` / ``user_input[names_section]`` are the nested
    dicts keyed by the readable (Chinese) display labels. Walking ``field_map``
    (see :class:`AdvFieldMap`) translates those display keys back onto the
    stored ``bindings`` (role) / ``names`` (appliance_key) keys.

    The returned ``bindings`` / ``names`` *replace* the whole stored field on
    merge, so the "clear by empty replace" semantics hold: a role left on 自动识别
    (``auto_value``) or without a submitted value drops out, and a rename left
    blank (or equal to its appliance default label) drops out too.
    """
    defaults = dict(default_labels or {})
    roles_in = user_input.get(roles_section) if isinstance(user_input, Mapping) else None
    names_in = user_input.get(names_section) if isinstance(user_input, Mapping) else None
    roles_in = roles_in if isinstance(roles_in, Mapping) else {}
    names_in = names_in if isinstance(names_in, Mapping) else {}

    bindings: dict[str, str] = {}
    for display_key, (kind, key) in field_map.items():
        if kind != "role":
            continue
        value = roles_in.get(display_key)
        if value and value != auto_value:
            bindings[key] = value

    names: dict[str, str] = {}
    for display_key, (kind, key) in field_map.items():
        if kind != "name":
            continue
        label = str((names_in.get(display_key) or defaults.get(key, "")).strip())
        if label and label != defaults.get(key):
            names[key] = label
    return bindings, names


def _appliance_key(ctx: DeviceBuildContext, device: DuerDevice) -> str:
    """Stable ``appliance_key`` of a built appliance (the ``names`` map key).

    Profile aggregates key on the profile key; SENSOR aggregates on "SENSOR";
    generic / leftover control entities key on ``domain:stable_sub(primary)``
    so the same light gets one key under auto (leftover) and forced generic.
    """
    pk = device.profile_key
    if pk in PROFILE_AGGREGATE_KEYS or pk == _SENSOR_KEY:
        return pk
    domain = pk or (device.primary_entity_id or "").split(".", 1)[0]
    return f"{domain}:{ctx.stable_sub(device.primary_entity_id)}"


def _standalone_appliance_key(device: DuerDevice, stable_id_of: Any) -> str:
    """Like :func:`_appliance_key`, for callers without a build context."""
    pk = device.profile_key
    if pk in PROFILE_AGGREGATE_KEYS or pk == _SENSOR_KEY:
        return pk
    domain = pk or (device.primary_entity_id or "").split(".", 1)[0]
    sub = device.primary_entity_id
    if stable_id_of is not None:
        stable = stable_id_of(device.primary_entity_id)
        if stable:
            sub = stable
    return f"{domain}:{sub}"


def _collect(
    ctx: DeviceBuildContext,
    built: list[DuerDevice],
    caps: list[str] | None,
    names: dict[str, str],
    devices: list[DuerDevice],
    claimed: set[str],
) -> None:
    """Narrow, rename and append every built appliance (and claim its entities).

    Capability narrowing via :func:`_filter_device` happens first; then the
    per-device ``names`` override replaces ``friendly_name`` (via
    ``dataclasses.replace``; ``device_id`` is never rewritten so a rename does
    not recreate the DuerOS appliance). Finally the appliance's bound entities
    are marked claimed so leftover resolution sees them.
    """
    for dev in built:
        filtered = _filter_device(dev, caps)
        if filtered is None:
            continue
        label = names.get(_appliance_key(ctx, filtered))
        if label:
            filtered = dataclasses.replace(filtered, friendly_name=label)
        devices.append(filtered)
        for cap in filtered.capabilities:
            for binding in cap.bindings:
                claimed.add(binding.entity_id)


def _clean_bindings_for_group(
    bindings: dict[str, str],
    *,
    hidden: set[str],
    group: list[Any],
    device_key: str,
) -> dict[str, str]:
    """Drop role bindings whose target is hidden or gone from this device.

    ``group`` is the device's entity list *after* ``hidden`` removal, so a
    binding to a hidden entity and a binding to an entity that is no longer on
    the device (renamed / deleted) both fail to resolve against ``ctx.states``.
    Keeping such a binding makes the profile build its mapping on a ghost entity
    whose ``is_reachable`` never turns true — the appliance shows up in
    discovery but is permanently offline. Each dropped binding logs a warning
    (role, target, reason) instead of failing silently.
    """
    present = {getattr(s, "entity_id", "") for s in group}
    cleaned: dict[str, str] = {}
    for role, entity_id in bindings.items():
        if entity_id in hidden:
            _LOGGER.warning(
                "xiaodu_bridge 设备 %s：角色 %s 的绑定实体 %s 已被隐藏，丢弃该绑定",
                device_key,
                role,
                entity_id,
            )
            continue
        if entity_id not in present:
            _LOGGER.warning(
                "xiaodu_bridge 设备 %s：角色 %s 的绑定实体 %s 不在该设备当前实体中"
                "（可能已改名或删除），丢弃该绑定",
                device_key,
                role,
                entity_id,
            )
            continue
        cleaned[role] = entity_id
    return cleaned


def build_enhanced_device_set(
    states: list[Any],
    options: dict[str, Any],
    *,
    device_of: Callable[[str], str | None],
    name_of: Callable[[str], str | None] | None = None,
    area_of: Callable[[str], str | None] | None = None,
    stable_id_of: Callable[[str], str | None] | None = None,
) -> EnhancedDeviceSet:
    """Build the DuerOS device set (the only runtime path).

    ``options[CONF_DEVICES]`` is ``{device_key: <normalized object>}``. When it
    is ``None`` every exposable device is enrolled (candidate / fresh view,
    all capabilities); otherwise only the listed devices are enrolled. Per
    device the object may narrow capabilities (``caps``), hide entities
    (``hidden``), force a role->entity binding (``bindings``), override
    appliance names (``names``) or force the build shape (``mode``).

    ``stable_id_of(entity_id)`` resolves an entity to a rename-stable identity
    (the HA entity-registry ``unique_id``) so generic / leftover appliances keep
    the same DuerOS appliance id when the entity is renamed.
    """
    _ensure_profiles_registered()
    profiles = REGISTRY.all_profiles()
    groups = _group_by_device(states, device_of)
    config = normalize(options.get(CONF_DEVICES))
    sync_areas = bool(options.get(CONF_SYNC_AREAS, False))
    devices: list[DuerDevice] = []
    claimed: set[str] = set()
    device_areas: dict[str, str] = {}

    def _record_area(start: int) -> None:
        if area_of is None:
            return
        area = area_of(device_key)
        for dev in devices[start:]:
            if area:
                device_areas.setdefault(dev.device_id, area)

    for device_key in sorted(groups):
        if config is not None and device_key not in config:
            continue
        obj = config.get(device_key) if config is not None else None
        caps = device_caps(obj)
        names = names_of(obj)
        bindings = bindings_of(obj)
        hidden = set(hidden_of(obj))
        mode = mode_of(obj)

        # Hidden entities are removed before profile matching so hiding touches
        # profile.matches, leftover / generic building, sensor aggregation and
        # reachability alike.
        group = [
            s for s in groups[device_key]
            if getattr(s, "entity_id", "") not in hidden
        ]
        if not group:
            continue
        start = len(devices)

        def _make_ctx(
            states_sub: list[Any],
            *,
            profile_key: str = "",
            ctx_bindings: dict[str, str] | None = None,
            name: str | None = None,
        ) -> DeviceBuildContext:
            return DeviceBuildContext(
                hass=None,
                ha_device_id=device_key,
                device_name=name
                or _display_name(states_sub, name_of, device_key),
                profile_key=profile_key,
                domain=getattr(states_sub[0], "domain", "") if states_sub else "",
                states=states_sub,
                config=obj,
                bindings=dict(ctx_bindings or {}),
                stable_id_of=stable_id_of,
            )

        def _emit_generic(
            states_sub: list[Any], *, name: str | None = None
        ) -> None:
            """Build ``states_sub`` through the generic builder and collect it."""
            ctx = _make_ctx(states_sub, name=name)
            _collect(ctx, build_default_devices(ctx), caps, names, devices, claimed)
            _record_area(start)

        def _emit_leftover(profile: Any) -> None:
            """Surface unclaimed control entities after a matched profile.

            The matched profile may restrict which domains may surface
            (``leftover_domains``) — e.g. a bath heater exposes only its light,
            not its config switches.
            """
            allow = getattr(profile, "leftover_domains", None)
            leftover = [
                s for s in group
                if getattr(s, "entity_id", "") not in claimed
                and getattr(s, "domain", "") in device_mod.EXPOSABLE_DOMAINS
                and getattr(s, "domain", "") != "sensor"
                and not device_mod._is_auxiliary(s)
                and (allow is None or getattr(s, "domain", "") in allow)
            ]
            if not leftover:
                return
            first_name = (getattr(leftover[0], "attributes", None) or {}).get(
                "friendly_name"
            )
            _emit_generic(
                leftover, name=first_name or _display_name(group, name_of, device_key)
            )

        forced: Any = None
        if mode not in ("auto", "generic"):
            forced = REGISTRY.get_profile(mode)
            if forced is None:
                _LOGGER.warning(
                    "xiaodu_bridge 设备 %s：形态 %r 未注册，回退到自动识别",
                    device_key,
                    mode,
                )
                mode = "auto"

        if mode == "generic":
            # Skip the profile loop entirely: the whole group is built as
            # per-entity generic appliances; no leftover pass.
            _emit_generic(group, name=_display_name(group, name_of, device_key))
            continue

        # Profile builds aggregate several entities and resolve reachability
        # against ``group`` (hidden already removed): a role binding to a hidden
        # entity or to one that no longer exists on the device would build on a
        # ghost entity and stay forever unreachable, so drop it up front (with a
        # warning) instead of letting each profile's ``_suggest_role`` use it.
        bindings = _clean_bindings_for_group(
            bindings, hidden=hidden, group=group, device_key=device_key
        )

        matched = False
        matched_profile: Any = None
        for profile in (forced,) if forced is not None else profiles:
            if profile.build is None:
                continue
            if forced is None and (
                profile.matches is None or not profile.matches(group)
            ):
                continue
            ctx = _make_ctx(group, profile_key=profile.key, ctx_bindings=bindings)
            built = profile.build(ctx)
            if forced is not None and not built:
                # A forced shape that builds nothing falls back to generic
                # whether or not bindings were present; bindings only shape the
                # log hint (they may have been set for a role the build never
                # reached).
                _LOGGER.warning(
                    "xiaodu_bridge 设备 %s：强制形态 %s 构建为空%s，回退到 generic",
                    device_key,
                    mode,
                    "" if bindings else "（且无角色绑定）",
                )
                break  # matched stays False -> outer generic fallback
            _collect(ctx, built, caps, names, devices, claimed)
            _record_area(start)
            matched = True
            matched_profile = profile
            break

        if not matched:
            _emit_generic(group, name=_display_name(group, name_of, device_key))
            continue
        # A profile (auto-detected or forced) was built: its unclaimed control
        # entities (e.g. a YUBA / clothes-rack light) still surface through the
        # generic builder as their own appliance, subject to the profile's
        # ``leftover_domains`` restriction.
        _emit_leftover(matched_profile)

    return EnhancedDeviceSet(devices, claimed, enabled=True, sync_areas=sync_areas, areas=device_areas)


def build_enhanced_for_hass(hass: Any, entry: Any) -> EnhancedDeviceSet:
    """Build the enhanced device set for a config entry (registry-aware glue)."""
    from homeassistant.helpers import area_registry as ar  # noqa: PLC0415
    from homeassistant.helpers import device_registry as dr  # noqa: PLC0415
    from homeassistant.helpers import entity_registry as er  # noqa: PLC0415

    ent_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)
    area_reg = ar.async_get(hass)

    def device_of(entity_id: str) -> str | None:
        row = ent_reg.async_get(entity_id)
        return row.device_id if row and row.device_id else None

    def stable_id_of(entity_id: str) -> str | None:
        row = ent_reg.async_get(entity_id)
        return row.unique_id if row and row.unique_id else None

    def name_of(device_key: str) -> str | None:
        device = device_reg.async_get(device_key)
        return (device.name_by_user or device.name) if device else None

    def area_of(device_key: str) -> str | None:
        device = device_reg.async_get(device_key)
        if device is None or not device.area_id:
            return None
        area = area_reg.async_get_area(device.area_id)
        return area.name if area else None

    return build_enhanced_device_set(
        list(hass.states.async_all()),
        dict(entry.options),
        device_of=device_of,
        name_of=name_of,
        area_of=area_of,
        stable_id_of=stable_id_of,
    )


_registered = False


def _ensure_profiles_registered() -> None:
    global _registered
    if not _registered:
        register_default_profiles(REGISTRY)
        _registered = True




def build_candidate_devices(hass: Any) -> list[dict[str, Any]]:
    """Enumerate the exposable HA devices for the options UI.

    Returns ``[{device_key, name, capabilities, appliances}]``. Capabilities
    are the union of every capability the device's appliances expose, so the
    UI can let the user pick a "设备 → 能力" set.
    """
    from homeassistant.helpers import device_registry as dr  # noqa: PLC0415
    from homeassistant.helpers import entity_registry as er  # noqa: PLC0415

    ent_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)

    def device_of(entity_id: str) -> str | None:
        row = ent_reg.async_get(entity_id)
        return row.device_id if row and row.device_id else None

    def stable_id_of(entity_id: str) -> str | None:
        row = ent_reg.async_get(entity_id)
        return row.unique_id if row and row.unique_id else None

    def name_of(device_key: str) -> str | None:
        device = device_reg.async_get(device_key)
        return (device.name_by_user or device.name) if device else None

    enhanced = build_enhanced_device_set(
        list(hass.states.async_all()),
        {},
        device_of=device_of,
        name_of=name_of,
        stable_id_of=stable_id_of,
    )
    grouped: dict[str, list[DuerDevice]] = {}
    for dev in enhanced.all():
        key = device_of(dev.primary_entity_id) or dev.primary_entity_id
        grouped.setdefault(key, []).append(dev)

    out: list[dict[str, Any]] = []
    for key in sorted(grouped):
        devs = grouped[key]
        caps = sorted({c.key for d in devs for c in d.capabilities})
        out.append(
            {
                "device_key": key,
                "name": name_of(key) or devs[0].friendly_name,
                "capabilities": caps,
                "appliances": len(devs),
            }
        )
    return out


def build_device_detail(hass: Any, device_key: str, obj: Any = None) -> dict[str, Any]:
    """Describe one device for the advanced per-device options UI (HA glue).

    Resolves the entity/device registry closures and the current state list from
    ``hass``, then delegates the whole description to
    :func:`build_device_detail_parts` (kept pure so the form logic can be unit
    tested without a Home Assistant runtime).
    """
    from homeassistant.helpers import device_registry as dr  # noqa: PLC0415
    from homeassistant.helpers import entity_registry as er  # noqa: PLC0415

    ent_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)

    def device_of(entity_id: str) -> str | None:
        row = ent_reg.async_get(entity_id)
        return row.device_id if row and row.device_id else None

    def stable_id_of(entity_id: str) -> str | None:
        row = ent_reg.async_get(entity_id)
        return row.unique_id if row and row.unique_id else None

    def name_of(key: str) -> str | None:
        device = device_reg.async_get(key)
        return (device.name_by_user or device.name) if device else None

    return build_device_detail_parts(
        list(hass.states.async_all()),
        device_key,
        obj,
        device_of=device_of,
        name_of=name_of,
        stable_id_of=stable_id_of,
    )


def build_device_detail_parts(
    states: list[Any],
    device_key: str,
    obj: Any = None,
    *,
    device_of: Callable[[str], str | None],
    name_of: Callable[[str], str | None] | None,
    stable_id_of: Callable[[str], str | None] | None,
) -> dict[str, Any]:
    """Describe one device for the advanced per-device options UI (HA-free core).

    Builds the device's full (default-all) appliance set and returns what the
    UI needs to offer caps / role bindings / hidden entities / per-appliance
    name overrides:

    - ``appliances``: ``[{appliance_key, label, profile_key, caps}]``
      (``appliance_key`` is the stable ``names`` key — the profile key for an
      aggregate, ``domain:stable_sub`` for generic/leftover appliances);
    - ``caps_union``: every capability the device could expose;
    - ``entities``: ``[{id, label, domain, is_aux}]`` restricted to the
      exposable domains, for the hidden-entity multiselect / capability picks;
    - ``all_entities``: the *whole* HA device group (every domain the device
      registry groups under ``device_key``, not just
      ``EXPOSABLE_DOMAINS``) in the same shape, for role-binding candidates.
      Roles like a YUBA ``warmth_level`` / ``fan_speed`` (``select``/``fan``) or
      ``target_temperature`` (``climate``/``number``) must be able to bind
      entities that are never exposed to DuerOS as standalone devices (a ``number``
      setting, a ``select`` gear); restricting role candidates to ``entities``
      left those roles with no picker at all.
    - ``matched_profile``: the profile key of the aggregate that the build
      actually produced under ``obj`` (or ``None``, e.g. an empty forced build
      that fell back to generic).

    ``obj`` is an optional existing per-device object; its ``mode`` / ``hidden``
    / ``names`` are honoured so the description matches what would actually be
    built (a forced profile therefore re-shapes the view). ``caps`` is
    overridden to ``None`` so the option list stays stable regardless of any
    current capability narrowing.
    """
    entry = normalize_entry(obj) or {}
    entry["caps"] = None  # stable options: never narrow for the picker
    enhanced = build_enhanced_device_set(
        states,
        {CONF_DEVICES: {device_key: entry}},
        device_of=device_of,
        name_of=name_of,
        stable_id_of=stable_id_of,
    )
    devs = enhanced.all()
    name = name_of(device_key) or (devs[0].friendly_name if devs else device_key)

    all_group = []
    group = []
    for state in states:
        entity_id = getattr(state, "entity_id", "")
        key = device_of(entity_id) or entity_id
        if key != device_key:
            continue
        all_group.append(state)
        if getattr(state, "domain", "") in device_mod.EXPOSABLE_DOMAINS:
            group.append(state)

    def _as_entity(state: Any) -> dict[str, Any]:
        return {
            "id": getattr(state, "entity_id", ""),
            "label": str(
                (getattr(state, "attributes", None) or {}).get("friendly_name")
                or getattr(state, "entity_id", "")
            ),
            "domain": getattr(state, "domain", ""),
            "is_aux": device_mod._is_auxiliary(state),
        }

    appliances = []
    matched_profile: str | None = None
    for dev in devs:
        if matched_profile is None and dev.profile_key in PROFILE_AGGREGATE_KEYS:
            matched_profile = dev.profile_key
        appliances.append(
            {
                "appliance_key": _standalone_appliance_key(dev, stable_id_of),
                "label": dev.friendly_name,
                "profile_key": dev.profile_key,
                "caps": sorted({c.key for c in dev.capabilities}),
            }
        )

    return {
        "device_key": device_key,
        "name": name,
        "appliances": appliances,
        "caps_union": sorted({c.key for d in devs for c in d.capabilities}),
        "entities": [_as_entity(s) for s in group],
        "all_entities": [_as_entity(s) for s in all_group],
        "matched_profile": matched_profile,
    }


def advanced_shape_key(mode: str, matched_profile: str | None) -> str | None:
    """Return the profile key whose metadata shapes the advanced binding UI.

    An explicit forced ``mode`` (a registered profile key) wins over whatever
    the build matched, so a device that auto-detects nothing can still be
    forced onto a profile and immediately offer that profile's role-binding /
    aggregate-rename widgets (the very step that makes the forced build succeed
    via a role binding). Under ``auto`` the build's aggregate wins; ``generic``
    and unknown keys shape nothing.
    """
    if mode not in ("", "auto", "generic"):
        return mode
    if mode == "generic":
        return None
    if matched_profile in PROFILE_AGGREGATE_KEYS:
        return matched_profile
    return None


__all__ = [
    "AdvFieldMap",
    "EnhancedDeviceSet",
    "PROFILE_AGGREGATE_KEYS",
    "adv_field_map",
    "advanced_shape_key",
    "build_candidate_devices",
    "build_device_detail",
    "build_device_detail_parts",
    "build_enhanced_device_set",
    "build_enhanced_for_hass",
    "role_binding_specs",
]
