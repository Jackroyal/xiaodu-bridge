"""DuerOS semantic model (platform-neutral core).

The DuerOS wire protocol does not have a first-class ``capability`` node: an
appliance is just ``applianceTypes + actions + attributes``. This module is the
*semantic* layer we introduce to bind those to Home Assistant:

- ``DuerCapability``: a cohesive unit of DuerOS actions (write) + attributes
  (read/write) + the appliance semantics they belong to (e.g. ``power``,
  ``mode``, ``warmthLevel``, ``fanSpeed``).
- ``CapabilityMapping``: binds a ``DuerCapability`` to 1..N HA entities via
  ``EntityBinding`` roles, and provides ``read`` / ``write`` / ``query`` /
  ``change_report`` so the protocol layer never branches on device types.
- ``DuerDevice``: the appliance exposed to DuerOS; it aggregates one or more
  ``CapabilityMapping`` and has a stable, entity-independent ``device_id``.

The module has no Home Assistant runtime imports so the core can be unit-tested
standalone (same rule as ``devices.py``).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, State

# Capability kinds.
CAP_KIND_CONTROL = "control"
CAP_KIND_QUERY = "query"


@dataclass(frozen=True, slots=True)
class DuerAttribute:
    """The *schema* of one DuerOS attribute (name / value kind / unit / legal)."""

    name: str
    kind: str = "string"          # "boolean" | "number" | "string" | "object"
    unit: str = ""                # scale: "%" / "CELSIUS" / "K" / ""
    legal: str = ""               # legalValue: "(ON, OFF)" / "[0, 100]" / "BOOLEAN"


@dataclass(frozen=True, slots=True)
class AttributeValue:
    """A *runtime* DuerOS attribute value, ready to be serialized."""

    name: str
    value: Any
    scale: str = ""
    legal: str = ""
    timestamp_of_sample: int = field(default_factory=lambda: int(time.time()))
    uncertainty: int = 1000

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "value": self.value,
            "scale": self.scale,
            "timestampOfSample": self.timestamp_of_sample,
            "uncertaintyInMilliseconds": self.uncertainty,
        }
        if self.legal:
            payload["legalValue"] = self.legal
        return payload


@dataclass(frozen=True, slots=True)
class DuerAction:
    """One DuerOS action (write operation) and the capability it controls."""

    name: str                     # "turnOn" / "setMode" / "setGear"
    capability_key: str           # owning capability
    payload_key: str = ""         # payload field: "brightness" / "temperature" / "gear"
    fanout: bool = False          # may fan out to multiple HA entities


@dataclass(frozen=True, slots=True)
class DuerCapability:
    """A cohesive capability = actions (write) + attributes (read/write)."""

    key: str
    name_zh: str
    kind: str = CAP_KIND_CONTROL
    appliance_types: tuple[str, ...] = ()
    attributes: tuple[DuerAttribute, ...] = ()
    actions: tuple[DuerAction, ...] = ()
    query_names: tuple[str, ...] = ()   # GetTemperatureReadingRequest / GetState ...


@dataclass(frozen=True, slots=True)
class EntityBinding:
    """An HA entity that contributes to a capability under a semantic role."""

    entity_id: str
    role: str                     # "power" / "mode_heat" / "target" / "state"


@dataclass(frozen=True, slots=True)
class ServiceCall:
    """One HA service call; may target an explicit sibling entity."""

    domain: str
    service: str
    data: dict[str, Any] = field(default_factory=dict)
    target_entity_id: str = ""


@dataclass
class ReadContext:
    """Everything a ``read`` / ``query`` callback needs."""

    hass: HomeAssistant
    device: DuerDevice
    entities: dict[str, State]    # role -> state (bindings resolved)


@dataclass
class WriteContext:
    """Everything a ``write`` callback needs."""

    hass: HomeAssistant
    device: DuerDevice
    entities: dict[str, State]
    action: DuerAction
    payload: dict[str, Any]


class CapabilityMapping:
    """Binds a ``DuerCapability`` to 1..N HA entities with read/write/query/report.

    This is the single place that knows how a DuerOS capability is realised by
    Home Assistant. It is deliberately declarative: profiles instantiate a
    mapping (optionally via a composer in ``dueros.composers``) instead of
    adding device-type branches in the protocol layer.
    """

    def __init__(
        self,
        capability: DuerCapability,
        bindings: tuple[EntityBinding, ...],
        *,
        read: Callable[[ReadContext], AttributeValue | None],
        write: Callable[[WriteContext], list[ServiceCall] | None] | None = None,
        query: Callable[[ReadContext, str], AttributeValue | list[AttributeValue] | None] | None = None,
        change_report: Callable[[CapabilityMapping, str], str | None] | None = None,
    ) -> None:
        self.capability = capability
        self.bindings = bindings
        self._read = read
        self._write = write
        self._query = query
        self._change_report = change_report

    @property
    def key(self) -> str:
        return self.capability.key

    @property
    def attribute_names(self) -> tuple[str, ...]:
        return tuple(a.name for a in self.capability.attributes)

    def read(self, ctx: ReadContext) -> AttributeValue | None:
        """Current value of the capability's primary attribute."""
        return self._read(ctx)

    def write(self, ctx: WriteContext) -> list[ServiceCall] | None:
        """Translate one action into 0..N HA service calls."""
        if self._write is None:
            return None
        return self._write(ctx)

    def query(self, ctx: ReadContext, query_name: str) -> AttributeValue | list[AttributeValue] | None:
        """Answer a DuerOS query message (falls back to ``read``)."""
        if self._query is not None:
            return self._query(ctx, query_name)
        return self._read(ctx)

    def change_report(self, changed_entity_id: str) -> str | None:
        """Return the attribute name to report for a HA state change, or None."""
        if self._change_report is not None:
            return self._change_report(self, changed_entity_id)
        # Default: if the changed entity is one of our bindings, report the
        # capability's primary attribute.
        if any(b.entity_id == changed_entity_id for b in self.bindings):
            return self.attribute_names[0] if self.attribute_names else None
        return None


@dataclass(frozen=True, slots=True)
class DuerDevice:
    """The appliance exposed to DuerOS (one or many HA entities).

    ``device_id`` is stable and independent of any single entity id so a device
    that aggregates several entities does not "become new" when an entity is
    renamed or removed. ``primary_entity_id`` is used for reachability and for
    being the default service-call target.
    """

    device_id: str
    friendly_name: str
    profile_key: str
    primary_entity_id: str
    capabilities: tuple[CapabilityMapping, ...] = ()
    is_reachable: bool = True
    appliance_types: tuple[str, ...] = ()

    def actions(self) -> list[str]:
        """Deduplicate the actions across all enabled capabilities, in order."""
        seen: set[str] = set()
        out: list[str] = []
        for cap in self.capabilities:
            for action in cap.capability.actions:
                if action.name not in seen:
                    seen.add(action.name)
                    out.append(action.name)
        return out

    def find_capability(self, action_name: str) -> CapabilityMapping | None:
        """Return the capability whose action list contains ``action_name``."""
        for cap in self.capabilities:
            if any(a.name == action_name for a in cap.capability.actions):
                return cap
        return None

    def find_action(self, action_name: str) -> tuple[CapabilityMapping, DuerAction] | None:
        """Return (capability mapping, action) for a DuerOS action name."""
        for cap in self.capabilities:
            for action in cap.capability.actions:
                if action.name == action_name:
                    return cap, action
        return None

    def find_query_capability(self, query_name: str) -> CapabilityMapping | None:
        """Return the capability that can answer a query message name."""
        for cap in self.capabilities:
            if query_name in cap.capability.query_names:
                return cap
        return None


def make_attribute(
    name: str,
    value: Any,
    scale: str = "",
    legal: str = "",
    *,
    timestamp: int | None = None,
    uncertainty: int = 1000,
) -> AttributeValue:
    """Convenience factory for an ``AttributeValue``."""
    return AttributeValue(
        name=name,
        value=value,
        scale=scale,
        legal=legal,
        timestamp_of_sample=timestamp if timestamp is not None else int(time.time()),
        uncertainty=uncertainty,
    )


def make_device_id(profile_key: str, ha_device_id: str, sub_key: str = "") -> str:
    """Build a stable, entity-independent DuerOS appliance id.

    Uses the HA device-registry device id (stable) plus the profile/sub-key so
    a single HA device may surface several DuerOS appliances without the id
    drifting when an entity is renamed.
    """
    import hashlib

    raw = f"{profile_key}:{ha_device_id}:{sub_key}"
    return f"dueros-{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:24]}"




@dataclass
class DeviceBuildContext:
    """Everything a ``DuerDeviceProfile.build`` or domain builder needs.

    Carries the HA device group being resolved, the user's per-device config,
    and any explicit role->entity bindings. Profiles resolve semantic roles
    through ``entity_of`` (explicit binding) with optional heuristic fallback.
    """

    hass: Any
    ha_device_id: str
    device_name: str
    profile_key: str = ""
    domain: str = ""
    area_name: str | None = None
    device_meta: dict[str, str] = field(default_factory=dict)
    states: list[Any] = field(default_factory=list)
    bindings: dict[str, str] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    is_reachable: bool = True

    def entity_of(self, role: str) -> str | None:
        """Return the entity id bound to a semantic role, if any."""
        return self.bindings.get(role)

    def find_state(self, entity_id: str) -> Any | None:
        return next((s for s in self.states if getattr(s, "entity_id", "") == entity_id), None)

@dataclass(frozen=True, slots=True)
class DuerDeviceProfile:
    """Describes one DuerOS device type: how to build it and what it defaults to.

    This is a *declarative* profile. Concrete profiles (YUBA, WASHING_MACHINE,
    CLOTHES_RACK, ...) are instantiated in ``dueros.profiles``; they register
    their ``CapabilityMapping`` objects via ``dueros.registry``.

    ``suggest_bindings`` is purely a UI hint (whether a HA device *looks* like
    this profile) and must never be the source of truth — the user may override.
    """

    key: str
    appliance_types: tuple[str, ...] = ()
    default_capabilities: tuple[str, ...] = ()
    suggest_bindings: Callable[[Any, dict[str, Any]], bool] | None = None
    build: Callable[["DeviceBuildContext"], list["DuerDevice"]] | None = None
    matches: Callable[[Any], bool] | None = None
