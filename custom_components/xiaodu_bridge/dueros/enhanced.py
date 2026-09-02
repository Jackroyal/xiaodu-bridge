"""Runtime wiring for the DuerOS semantic model (sole/default path).

The device-center semantic model is the only runtime path. Every exposable HA
device is surfaced as one or more ``DuerDevice`` appliances:

1. A device that matches a declared profile (YUBA, CLOTHES_RACK, ...) is built
   by that profile (aggregating several entities into one appliance).
2. Every other device is built by ``build_default_devices`` (per-domain
   composers), so lights, switches, sensors, fans, climate, media players etc.
   all flow through the same semantic model.

``build_enhanced_device_set`` optionally filters by ``options[CONF_DEVICES]``
(device_key -> enabled capability keys), matching the "设备 → 能力" options UI.
"""

from __future__ import annotations

from typing import Any, Callable

from ..const import CONF_DEVICES, CONF_SYNC_AREAS
from .. import devices as device_mod
from .defaults import _device_enabled, build_default_devices
from .model import DeviceBuildContext, DuerDevice, DuerDeviceProfile
from .profiles import register_default_profiles
from .registry import REGISTRY


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


def _filter_device(device: DuerDevice, enabled: Any) -> DuerDevice | None:
    """Drop capabilities not in ``enabled`` (a list of capability keys).

    ``enabled`` of ``None``/empty keeps every capability. A device with no
    enabled control capability left is dropped.
    """
    if enabled is None:
        return device
    if isinstance(enabled, dict):
        # Legacy per-entity dict: profiles expose their default capability set
        # (per-entity narrowing is not applied to an aggregated appliance).
        return device
    selected = set(enabled or ())
    if not selected:
        return device
    caps = tuple(
        cap for cap in device.capabilities if cap.key in selected or cap.key == "power"
    )
    if not caps:
        return None
    return DuerDevice(
        device_id=device.device_id,
        friendly_name=device.friendly_name,
        profile_key=device.profile_key,
        primary_entity_id=device.primary_entity_id,
        capabilities=caps,
        is_reachable=device.is_reachable,
        appliance_types=device.appliance_types,
    )


def _collect(
    built: list[DuerDevice],
    config_entry: Any,
    devices: list[DuerDevice],
    claimed: set[str],
) -> None:
    for dev in built:
        filtered = _filter_device(dev, config_entry)
        if filtered is None:
            continue
        devices.append(filtered)
        for cap in filtered.capabilities:
            for binding in cap.bindings:
                claimed.add(binding.entity_id)


def build_enhanced_device_set(
    states: list[Any],
    options: dict[str, Any],
    *,
    device_of: Callable[[str], str | None],
    name_of: Callable[[str], str | None] | None = None,
    area_of: Callable[[str], str | None] | None = None,
) -> EnhancedDeviceSet:
    """Build the DuerOS device set (the only runtime path).

    ``options[CONF_DEVICES]`` is ``{device_key: enabled_capabilities}``. When it
    is ``None`` every exposable device is enrolled (candidate / fresh view);
    otherwise only the listed devices are enrolled. For each enrolled device a
    profile is preferred; the generic builder handles the rest.
    """
    _ensure_profiles_registered()
    profiles = REGISTRY.all_profiles()
    groups = _group_by_device(states, device_of)
    config = options.get(CONF_DEVICES)
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
        group = groups[device_key]
        config_entry = config.get(device_key) if isinstance(config, dict) else None
        start = len(devices)

        matched = False
        for profile in profiles:
            if profile.matches is not None and profile.matches(group) and profile.build is not None:
                ctx = DeviceBuildContext(
                    hass=None,
                    ha_device_id=device_key,
                    device_name=_display_name(group, name_of, device_key),
                    profile_key=profile.key,
                    domain=getattr(group[0], "domain", ""),
                    states=group,
                    config=config_entry,
                )
                _collect(profile.build(ctx), config_entry, devices, claimed)
                _record_area(start)
                matched = True
                break

        if matched:
            # Entities the profile did not claim (e.g. a clothes-rack / YUBA
            # light) still surface through the generic builder as their own
            # appliance. A legacy per-entity dict whose entries are all default
            # (empty list) means "device enabled, default-all" (the new options
            # UI saves a flat device -> capabilities list), so leftover
            # entities must not be silently dropped just because the legacy
            # dict only lists the profile's own entities.
            leftover = [
                s for s in group
                if getattr(s, "entity_id", "") not in claimed
                and getattr(s, "domain", "") in device_mod.EXPOSABLE_DOMAINS
                and getattr(s, "domain", "") != "sensor"
                and not device_mod._is_auxiliary(s)
            ]
            if leftover:
                leftover_config = config_entry
                if isinstance(config_entry, dict) and _device_enabled(config_entry) is None:
                    leftover_config = None
                first_name = (getattr(leftover[0], "attributes", None) or {}).get("friendly_name")
                leftover_ctx = DeviceBuildContext(
                    hass=None,
                    ha_device_id=device_key,
                    device_name=first_name or _display_name(group, name_of, device_key),
                    profile_key="",
                    domain=getattr(leftover[0], "domain", ""),
                    states=leftover,
                    config=leftover_config,
                )
                _collect(build_default_devices(leftover_ctx), config_entry, devices, claimed)
                _record_area(start)
            continue

        ctx = DeviceBuildContext(
            hass=None,
            ha_device_id=device_key,
            device_name=_display_name(group, name_of, device_key),
            profile_key="",
            domain=getattr(group[0], "domain", ""),
            states=group,
            config=config_entry,
        )
        _collect(build_default_devices(ctx), config_entry, devices, claimed)
        _record_area(start)

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

    def name_of(device_key: str) -> str | None:
        device = device_reg.async_get(device_key)
        return (device.name_by_user or device.name) if device else None

    enhanced = build_enhanced_device_set(
        list(hass.states.async_all()),
        {},
        device_of=device_of,
        name_of=name_of,
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


__all__ = [
    "EnhancedDeviceSet",
    "build_enhanced_device_set",
    "build_enhanced_for_hass",
    "build_candidate_devices",
]
