"""Legacy entity include/exclude filter for the Xiaodu integration.

The device/capability model (``CONF_DEVICES``) replaced the include/exclude
pattern lists. They are still read here purely as a migration path: options
written by old versions are applied as a filter over the entity states before
they are grouped into devices.
"""

from __future__ import annotations

import fnmatch
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(slots=True)
class EntityFilter:
    """Include/exclude entity filter based on fnmatch patterns.

    - An empty ``include`` set means every entity is a candidate.
    - ``exclude`` always wins over ``include``.
    - Patterns match the full ``entity_id``, e.g. ``light.*`` or
      ``switch.bedroom_*``.
    """

    include: set[str] = field(default_factory=set)
    exclude: set[str] = field(default_factory=set)

    @classmethod
    def from_lists(
        cls,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> EntityFilter:
        """Build a filter from optional pattern lists."""
        return cls(include=set(include or ()), exclude=set(exclude or ()))

    def allowed(self, entity_id: str) -> bool:
        """Return True when the entity should be exposed to Xiaodu."""
        if any(fnmatch.fnmatch(entity_id, pattern) for pattern in self.exclude):
            return False
        if not self.include:
            return True
        return any(fnmatch.fnmatch(entity_id, pattern) for pattern in self.include)
