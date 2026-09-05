"""Persisted timed service calls (Xiaodu timingTurnOn / timingTurnOff).

Xiaodu can ask the skill to turn a device on/off at an absolute time
(``timingTurnOnRequest`` / ``timingTurnOffRequest``). Instead of a plain
in-process ``asyncio.sleep`` task (which a core restart cancels), pending
timers are:

- persisted in HA storage (``xiaodu.timed_services``),
- armed with ``homeassistant.helpers.event.async_track_point_in_utc_time`` —
  the same event-loop scheduler HA automations use for their time triggers,
- re-armed from storage at setup, so a core restart does not lose them.

Stale records (fire time already passed while HA was down) are dropped on
load: like a HA automation time trigger, a timer only fires while HA is
running.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.storage import Store
from homeassistant.util.dt import utc_from_timestamp


_LOGGER = logging.getLogger(__name__)

STORAGE_KEY = "xiaodu.timed_services"
STORAGE_VERSION = 1


def _key(record: dict[str, Any]) -> tuple[str, str, str]:
    """Return the dedup key: one pending timer per (service, entity)."""
    return (
        str(record.get("domain", "")),
        str(record.get("service", "")),
        str((record.get("data") or {}).get("entity_id", "")),
    )


class TimedServiceManager:
    """Schedule persisted HA service calls at an absolute UTC time."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._store = Store[dict[str, Any]](hass, STORAGE_VERSION, STORAGE_KEY)
        self._records: list[dict[str, Any]] = []
        self._unsubs: dict[tuple[str, str, str], Any] = {}
        self._lock = asyncio.Lock()
        self._loaded = False

    async def async_load(self) -> None:
        """Load persisted timers and re-arm those still in the future."""
        if self._loaded:
            return
        self._loaded = True
        data = await self._store.async_load() or {}
        now = time.time()
        self._records = []
        for record in data.get("timers") or []:
            if not isinstance(record, dict):
                continue
            try:
                fire_at = float(record.get("fire_at") or 0)
            except (TypeError, ValueError):
                continue
            record["fire_at"] = fire_at
            if fire_at > now:
                self._records.append(record)
                self._arm(record)
            else:
                _LOGGER.info(
                    "Xiaodu dropped stale timer %s (fire time already passed)",
                    _key(record),
                )
        if self._records:
            await self._persist()

    async def schedule(
        self, domain: str, service: str, data: dict[str, Any], fire_at: float
    ) -> None:
        """Schedule a service call, replacing an existing one for the same key.

        A timestamp in the past (clock skew / live request) runs immediately.
        """
        record = {
            "domain": domain,
            "service": service,
            "data": dict(data),
            "fire_at": float(fire_at),
        }
        key = _key(record)
        self._cancel(key)
        self._records = [r for r in self._records if _key(r) != key]
        if fire_at <= time.time():
            await self._fire(record, persist=False)
            return
        self._records.append(record)
        await self._persist()
        self._arm(record)
        _LOGGER.info(
            "Xiaodu scheduled %s.%s for entity %s at %.0f",
            domain,
            service,
            data.get("entity_id", ""),
            fire_at,
        )

    def cancel_all(self) -> None:
        """Cancel all armed timers (records stay persisted for next setup)."""
        for unsub in self._unsubs.values():
            unsub()
        self._unsubs.clear()

    # ------------------------------------------------------------------

    def _arm(self, record: dict[str, Any]) -> None:
        def _on_time(_now: Any) -> None:
            self._hass.async_create_task(self._fire(record))

        self._unsubs[_key(record)] = async_track_point_in_utc_time(
            self._hass, _on_time, utc_from_timestamp(record["fire_at"])
        )

    def _cancel(self, key: tuple[str, str, str]) -> None:
        unsub = self._unsubs.pop(key, None)
        if unsub:
            unsub()

    async def _fire(self, record: dict[str, Any], *, persist: bool = True) -> None:
        self._cancel(_key(record))
        if persist:
            self._records = [r for r in self._records if _key(r) != _key(record)]
            await self._persist()
        domain = record.get("domain", "")
        service = record.get("service", "")
        data = record.get("data") or {}
        _LOGGER.info(
            "Xiaodu timed %s.%s firing for entity %s",
            domain,
            service,
            data.get("entity_id", ""),
        )
        try:
            await self._hass.services.async_call(domain, service, data, blocking=True)
        except Exception:  # noqa: BLE001 - a failed timed call must not crash
            _LOGGER.exception("Xiaodu timed %s.%s failed", domain, service)

    async def _persist(self) -> None:
        async with self._lock:
            await self._store.async_save({"timers": list(self._records)})
