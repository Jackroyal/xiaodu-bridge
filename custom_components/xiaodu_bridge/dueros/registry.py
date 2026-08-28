"""Registry for the long-term semantic model.

Two kinds of mappings are registered:

- ``register_profile`` + ``register_mapping``: device-profile capabilities for
  complex devices (YUBA, WASHING_MACHINE, CLOTHES_RACK, ...). The protocol layer
  prefers a ``DuerDevice`` built from these.
- ``register_domain_default``: per-HA-domain fallback mappings for simple
  devices (light, switch, fan, climate, ...), used when no profile applies.

The protocol dispatcher never branches on device type: it resolves a request to
a ``DuerDevice`` and then to one of its ``CapabilityMapping`` objects.
"""

from __future__ import annotations

from typing import Any

from .model import CapabilityMapping, DuerDevice, DuerDeviceProfile


class MappingRegistry:
    def __init__(self) -> None:
        self._profiles: dict[str, DuerDeviceProfile] = {}
        self._profile_mappings: dict[str, list[CapabilityMapping]] = {}
        self._domain_defaults: dict[str, list[CapabilityMapping]] = {}
        self._domain_builders: dict[str, Any] = {}

    # --- registration --------------------------------------------------

    def register_profile(self, profile: DuerDeviceProfile) -> None:
        self._profiles[profile.key] = profile

    def register_mapping(self, profile_key: str, mapping: CapabilityMapping) -> None:
        self._profile_mappings.setdefault(profile_key, []).append(mapping)

    def register_domain_default(self, domain: str, mapping: CapabilityMapping) -> None:
        self._domain_defaults.setdefault(domain, []).append(mapping)

    # --- lookup --------------------------------------------------------

    def get_profile(self, profile_key: str) -> DuerDeviceProfile | None:
        return self._profiles.get(profile_key)

    def profile_capabilities(self, profile_key: str) -> tuple[CapabilityMapping, ...]:
        return tuple(self._profile_mappings.get(profile_key, ()))

    def domain_defaults(self, domain: str) -> tuple[CapabilityMapping, ...]:
        return tuple(self._domain_defaults.get(domain, ()))

    def register_domain_builder(self, domain: str, builder: Any) -> None:
        """Register a per-device builder for a HA domain (simple devices).

        ``builder`` is ``Callable[[DeviceBuildContext], DuerDevice | None]`` and
        fills in concrete entity ids at build time.
        """
        self._domain_builders[domain] = builder

    def domain_builder(self, domain: str) -> Any | None:
        return self._domain_builders.get(domain)

    def build_device(self, ctx: Any) -> DuerDevice | None:
        """Build a DuerDevice from a DeviceBuildContext.

        Prefers an explicit device profile (complex devices); falls back to the
        per-domain builder (simple devices); returns None when neither applies.
        """
        profile_key = getattr(ctx, "profile_key", "") or ""
        domain = getattr(ctx, "domain", "") or ""
        if profile_key:
            profile = self.get_profile(profile_key)
            if profile is not None and profile.build is not None:
                built = profile.build(ctx)
                return built[0] if built else None
            mappings = self.profile_capabilities(profile_key)
            if mappings and getattr(ctx, "primary_entity_id", ""):
                return self._assemble(ctx, mappings)
        builder = self.domain_builder(domain)
        if builder is not None:
            return builder(ctx)
        return None

    def _assemble(self, ctx: Any, mappings: tuple[CapabilityMapping, ...]) -> DuerDevice | None:
        from .model import DuerDevice
        return DuerDevice(
            device_id=getattr(ctx, "device_id", ""),
            friendly_name=getattr(ctx, "device_name", ""),
            primary_entity_id=getattr(ctx, "primary_entity_id", ""),
            profile_key=getattr(ctx, "profile_key", ""),
            capabilities=tuple(mappings),
            is_reachable=getattr(ctx, "is_reachable", True),
            appliance_types=getattr(ctx, "appliance_types", ()),
        )

    def all_profiles(self) -> tuple[DuerDeviceProfile, ...]:
        return tuple(self._profiles.values())

    def has_profile(self, profile_key: str) -> bool:
        return profile_key in self._profiles

    def resolve_capabilities(
        self, profile_key: str, domain: str
    ) -> tuple[CapabilityMapping, ...]:
        """Return the capability mappings for a device: profile first, then domain default."""
        if profile_key and self.has_profile(profile_key):
            return self.profile_capabilities(profile_key)
        return self.domain_defaults(domain)

    # --- device construction helper (used by devices.py later) ---------

    def build_dueros_device(
        self,
        *,
        device_id: str,
        friendly_name: str,
        profile_key: str,
        primary_entity_id: str,
        domain: str,
        is_reachable: bool = True,
        enabled_capability_keys: tuple[str, ...] = (),
    ) -> DuerDevice | None:
        """Assemble a ``DuerDevice`` from registered capability mappings.

        Only mappings whose capability key is in ``enabled_capability_keys`` are
        kept; an empty tuple means "keep all" (used for discovery candidates).
        """
        mappings = self.resolve_capabilities(profile_key, domain)
        if not mappings:
            return None
        chosen = [
            m for m in mappings
            if not enabled_capability_keys or m.key in enabled_capability_keys
        ]
        if not chosen:
            return None
        profile = self.get_profile(profile_key)
        appliance_types = (
            tuple(profile.appliance_types)
            if profile is not None and profile.appliance_types
            else ()
        )
        return DuerDevice(
            device_id=device_id,
            friendly_name=friendly_name,
            profile_key=profile_key,
            primary_entity_id=primary_entity_id,
            capabilities=tuple(chosen),
            is_reachable=is_reachable,
            appliance_types=appliance_types,
        )


REGISTRY = MappingRegistry()

__all__ = ["MappingRegistry", "REGISTRY"]
