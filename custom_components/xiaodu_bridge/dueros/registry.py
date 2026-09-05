"""Registry for the DuerOS semantic model.

Holds the registered device profiles (YUBA, SWEEPING_ROBOT, CLOTHES_RACK,
WASHING_MACHINE). The runtime resolves appliances by asking each profile
whether it matches a device group and letting it build the ``DuerDevice``
(see ``enhanced.py``); devices without a matching profile fall back to the
generic composers in ``defaults.build_default_devices``.
"""

from __future__ import annotations

from .model import DuerDeviceProfile


class ProfileRegistry:
    """Registry of device profiles keyed by profile key."""

    def __init__(self) -> None:
        self._profiles: dict[str, DuerDeviceProfile] = {}

    def register_profile(self, profile: DuerDeviceProfile) -> None:
        self._profiles[profile.key] = profile

    def get_profile(self, profile_key: str) -> DuerDeviceProfile | None:
        return self._profiles.get(profile_key)

    def all_profiles(self) -> tuple[DuerDeviceProfile, ...]:
        return tuple(self._profiles.values())


REGISTRY = ProfileRegistry()

__all__ = ["ProfileRegistry", "REGISTRY"]
