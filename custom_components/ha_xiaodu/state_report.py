"""Active device-state reporting to DuerOS (changereport).

DuerOS only learns a device's state when the skill tells it: discovery
responses and control confirmations carry attributes. When the user changes
the state *outside* the speaker (physical button, another app, an HA
automation), DuerOS keeps the old values until the skill actively reports the
change. The official mechanism is a two-step handshake:

1. The skill POSTs a ``ChangeReportRequest`` to
   ``/saiya/smarthome/changereport`` naming the appliance and the one
   attribute that changed.
2. DuerOS answers with ``ReportStateRequest``; the skill's WebService returns
   a ``ReportStateResponse`` with the current attribute values (the generic
   query path in ``protocol.py`` already implements step 2).

This module owns step 1: the HTTP push, plus the HA state listener that
decides when to push. State changes are debounced so a burst (e.g. dragging a
brightness slider) coalesces into a single report, and changes caused by
voice control itself are suppressed because the confirmation message already
carried the fresh attributes back to DuerOS.
"""

from __future__ import annotations

import logging
import time
import uuid
from functools import partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import Event, HomeAssistant

    from .oauth_store import XiaoduOAuthStore

from .const import (
    CONF_BOT_ID,
    DUEROS_CHANGE_REPORT_URL,
)
from .devices import CONTROL_CAPS
from .dueros.adapters import extra_attributes, get_adapter
from .dueros.protocol import filtered_attributes

_LOGGER = logging.getLogger(__name__)

# How long to wait after the first state change before pushing, so a burst of
# changes (slider drags, color wheels) coalesces into one report per entity.
STATE_REPORT_DEBOUNCE_SECONDS = 2.0

# After a Xiaodu control confirmation, skip pushing the resulting state change
# for this long: the confirmation already carried the new attributes to DuerOS,
# so a changereport would only trigger a redundant ReportState round trip.
CONTROL_SUPPRESS_SECONDS = 3.0

# DuerOS only accepts one changereport per attribute per 60 seconds
# ("One attribute can only sync 1 times during 60"). Keep a small margin so
# server-side clock differences do not cause a rejection.
ATTR_SYNC_COOLDOWN_SECONDS = 62.0


def build_change_report(
    bot_id: str,
    open_uid: str,
    entity_id: str,
    attribute_name: str,
    message_id: str | None = None,
) -> dict[str, Any]:
    """Build one ``ChangeReportRequest`` envelope (one attribute per request)."""
    return {
        "header": {
            "namespace": "DuerOS.ConnectedHome.Control",
            "name": "ChangeReportRequest",
            "messageId": message_id or str(uuid.uuid4()),
            "payloadVersion": "1",
        },
        "payload": {
            "botId": bot_id,
            "openUid": open_uid,
            "appliance": {
                "applianceId": entity_id,
                "attributeName": attribute_name,
            },
        },
    }


def changed_attribute_names(
    old_attributes: dict[str, Any] | None,
    new_attributes: dict[str, Any],
) -> set[str]:
    """Return the attribute names whose values changed between two snapshots."""
    if not old_attributes:
        return set()
    return {
        name
        for name, value in new_attributes.items()
        if name not in old_attributes or old_attributes[name] != value
    }


def unit_has_control_capabilities(unit: Any) -> bool:
    """Return True when the unit exposes at least one control capability.

    DuerOS rejects changereport for appliances without control actions
    (pure sensor devices: ``actions: []``) with "Appliance specificed not
    exist", even though the same appliance appears in discovery and works for
    live queries. Only push state reports for units DuerOS actually accepts.
    """
    return bool(set(getattr(unit, "enabled", ())) & CONTROL_CAPS)


async def report_changed_attribute(
    hass: HomeAssistant,
    entry: Any,
    store: XiaoduOAuthStore,
    entity_id: str,
    attribute_name: str,
    session: Any | None = None,
) -> bool:
    """Push one changed attribute to every bound openUid.

    Safe to call from anywhere: without a configured ``bot_id`` or bound users
    it is a no-op. Returns True when DuerOS accepted the push (so the caller
    can record the per-attribute 60s cooldown), False otherwise.
    """
    bot_id = str((entry.data or {}).get(CONF_BOT_ID, "") or "").strip()
    open_uids = store.open_uids()
    if not bot_id or not open_uids or not entity_id or not attribute_name:
        _LOGGER.debug(
            "State report skipped: botId=%s openUids=%d entity=%s attr=%s",
            bot_id or "<missing>",
            len(open_uids),
            entity_id,
            attribute_name,
        )
        return False

    if session is None:
        from homeassistant.helpers.aiohttp_client import (  # noqa: PLC0415
            async_get_clientsession,
        )

        session = async_get_clientsession(hass)

    accepted = False
    for open_uid in open_uids:
        payload = build_change_report(bot_id, open_uid, entity_id, attribute_name)
        try:
            async with session.post(
                DUEROS_CHANGE_REPORT_URL, json=payload
            ) as response:
                try:
                    body = await response.json(content_type=None)
                except ValueError:
                    body = {}
                msg = body.get("msg") if isinstance(body, dict) else ""
                _LOGGER.info(
                    "Xiaodu state report -> HTTP %s, msg=%s, "
                    "appliance=%s attr=%s openUid=%s",
                    response.status,
                    msg,
                    entity_id,
                    attribute_name,
                    open_uid,
                )
                if response.status == 200 and "can only sync" not in str(msg):
                    accepted = True
        except Exception:  # noqa: BLE001 - a failed push must not break the flow
            _LOGGER.warning("Xiaodu state report failed: %s", payload, exc_info=True)
    return accepted


class StateReportManager:
    """Listen for exposed-entity state changes and push changereports.

    One instance per config entry. It keeps a snapshot of the
    DuerOS-visible attributes per exposed unit; when an event touches any
    entity feeding that unit (the unit itself, a sibling query entity such as
    humidity, or a YUBA control switch), it diffs the snapshot and schedules a
    debounced report.
    """

    def __init__(self, hass: HomeAssistant, entry: Any) -> None:
        self.hass = hass
        self.entry = entry
        self.update_unsub: Any | None = None
        self._unsub: Any | None = None
        self._startup_unsub: Any | None = None
        self._stopped = False
        # entity_id -> unit ids that must refresh when this entity changes
        self._index: dict[str, list[str]] = {}
        self._units: dict[str, Any] = {}
        self._devices: dict[str, Any] = {}
        # unit id -> last reported attribute snapshot ({name: value})
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._pending: dict[str, set[str]] = {}
        self._handles: dict[str, Any] = {}
        self._confirmed: dict[str, float] = {}
        # (unit id, attribute name) -> monotonic time of the last accepted push
        self._last_sync: dict[tuple[str, str], float] = {}

    def async_start(self) -> None:
        """Register the state-change listener (idempotent)."""
        if self._unsub is not None:
            return
        from homeassistant.const import (  # noqa: PLC0415
            EVENT_HOMEASSISTANT_STARTED,
            EVENT_STATE_CHANGED,
        )
        from homeassistant.core import CoreState  # noqa: PLC0415

        self.async_rebuild()
        self._unsub = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._async_on_state_changed
        )
        if self.hass.state != CoreState.running:
            # During initial startup the exposed entities may not exist yet,
            # so the first index can be empty. Rebuild once startup finished
            # and all platforms have created their entities.
            self._startup_unsub = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self._async_on_startup
            )
        _LOGGER.debug(
            "State report listener registered, %d units indexed",
            len(self._units),
        )

    async def _async_on_startup(self, _event: Event) -> None:
        """Rebuild the index once HA finished startup (entities now exist)."""
        self._startup_unsub = None
        self.async_rebuild()
        _LOGGER.debug(
            "State report index rebuilt after startup: %d units",
            len(self._units),
        )

    def async_rebuild(self) -> None:
        """Rebuild the entity index and snapshots from entry options.

        Called at setup and whenever the config entry changes (options save /
        reconfigure), so newly exposed/hidden entities take effect immediately.
        """
        for handle in self._handles.values():
            handle.cancel()
        self._handles.clear()
        self._pending.clear()
        self._confirmed.clear()
        self._last_sync.clear()

        from .devices import DEVICE_CLASS_YUBA, build_device_map  # noqa: PLC0415

        devices = build_device_map(self.hass, self.entry.options)
        index: dict[str, set[str]] = {}
        units: dict[str, Any] = {}
        devices_by_unit: dict[str, Any] = {}
        for device in devices.devices():
            for unit in device.units:
                if not unit.enabled:
                    continue
                unit_id = unit.entity_id
                units[unit_id] = unit
                devices_by_unit[unit_id] = device
                index.setdefault(unit_id, set()).add(unit_id)
                for sibling_id in unit.query_entities.values():
                    if sibling_id != unit_id:
                        index.setdefault(sibling_id, set()).add(unit_id)
                if unit.device_class == DEVICE_CLASS_YUBA:
                    for control_id in (device.controls or {}).values():
                        index.setdefault(control_id, set()).add(unit_id)

        self._index = {entity_id: sorted(ids) for entity_id, ids in index.items()}
        self._units = units
        self._devices = devices_by_unit
        # Snapshot current values without pushing anything at setup/rebuild.
        self._snapshots = {
            unit_id: self._unit_attributes(unit_id) for unit_id in units
        }
        _LOGGER.debug(
            "State report index rebuilt: %d units, %d event mappings",
            len(self._units),
            len(self._index),
        )

    def mark_confirmed(self, unit_id: str) -> None:
        """Record that a Xiaodu control just confirmed this unit's state."""
        self._confirmed[unit_id] = time.monotonic()

    async def async_shutdown(self) -> None:
        """Stop listening and cancel any pending reports."""
        self._stopped = True
        if self._unsub is not None:
            self._unsub()
            self._unsub = None
        if self._startup_unsub is not None:
            self._startup_unsub()
            self._startup_unsub = None
        if self.update_unsub is not None:
            self.update_unsub()
            self.update_unsub = None
        for handle in self._handles.values():
            handle.cancel()
        self._handles.clear()
        self._pending.clear()
        self._confirmed.clear()
        self._last_sync.clear()
        self._index.clear()
        self._units.clear()
        self._devices.clear()
        self._snapshots.clear()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    async def _async_on_state_changed(self, event: Event) -> None:
        if self._stopped:
            return
        from homeassistant.core import CoreState  # noqa: PLC0415

        entity_id = str(event.data.get("entity_id", ""))
        if not self._units and self.hass.state == CoreState.running:
            # Self-heal: if the index was built before entities existed (or an
            # integration loaded late), rebuild once on the next event after
            # startup. During startup the HOMEASSISTANT_STARTED rebuild covers
            # the final state, so we do not rebuild on every early event.
            self.async_rebuild()
        unit_ids = self._index.get(entity_id)
        if not unit_ids:
            return
        _LOGGER.debug(
            "State change event for %s feeds units %s",
            entity_id,
            unit_ids,
        )
        for unit_id in unit_ids:
            if self._suppressed(unit_id):
                _LOGGER.debug(
                    "Skip state report for %s: control confirmation in progress",
                    unit_id,
                )
                continue
            old = self._snapshots.get(unit_id)
            new = self._unit_attributes(unit_id)
            changed = changed_attribute_names(old, new)
            self._snapshots[unit_id] = new
            if changed:
                if not unit_has_control_capabilities(self._units[unit_id]):
                    _LOGGER.debug(
                        "Skip state report for %s: query-only unit "
                        "(DuerOS rejects changereport for pure sensors)",
                        unit_id,
                    )
                    continue
                _LOGGER.debug(
                    "State changed for %s: %s",
                    unit_id,
                    sorted(changed),
                )
                self._schedule_report(unit_id, changed)

    def _suppressed(self, unit_id: str) -> bool:
        confirmed_at = self._confirmed.get(unit_id)
        return (
            confirmed_at is not None
            and time.monotonic() - confirmed_at < CONTROL_SUPPRESS_SECONDS
        )

    def _schedule_report(self, unit_id: str, names: set[str]) -> None:
        pending = self._pending.setdefault(unit_id, set())
        pending |= names
        if unit_id in self._handles:
            _LOGGER.debug(
                "Report for %s already pending, merging %s",
                unit_id,
                sorted(names),
            )
            return
        from homeassistant.helpers.event import async_call_later  # noqa: PLC0415

        _LOGGER.debug(
            "Scheduling state report for %s in %.1fs: %s",
            unit_id,
            STATE_REPORT_DEBOUNCE_SECONDS,
            sorted(pending),
        )
        self._handles[unit_id] = async_call_later(
            self.hass,
            STATE_REPORT_DEBOUNCE_SECONDS,
            partial(self._async_flush, unit_id),
        )

    async def _async_flush(self, unit_id: str, _now: Any) -> None:
        self._handles.pop(unit_id, None)
        names = self._pending.pop(unit_id, set())
        if not names:
            return

        from .oauth_server import _get_store  # noqa: PLC0415
        from homeassistant.helpers.event import async_call_later  # noqa: PLC0415

        store = await _get_store(self.hass)
        bot_id = str((self.entry.data or {}).get(CONF_BOT_ID, "") or "").strip()
        _LOGGER.debug(
            "Flushing state report for %s: attrs=%s botId=%s openUids=%s",
            unit_id,
            sorted(names),
            bot_id or "<missing>",
            len(store.open_uids()),
        )

        now = time.monotonic()
        ready: list[str] = []
        held: list[tuple[str, float]] = []
        for attribute_name in sorted(names):
            last_sync = self._last_sync.get((unit_id, attribute_name), 0.0)
            remaining = last_sync + ATTR_SYNC_COOLDOWN_SECONDS - now
            if remaining <= 0:
                ready.append(attribute_name)
            else:
                held.append((attribute_name, remaining))

        if held:
            # DuerOS only accepts one changereport per attribute per 60s; hold
            # the pending change and retry when the cooldown expires. Because
            # ReportStateRequest reads the live state, one retry is enough to
            # bring DuerOS up to date.
            self._pending[unit_id] = {name for name, _ in held}
            min_remaining = min(remaining for _, remaining in held)
            _LOGGER.debug(
                "Holding attrs for %s until DuerOS cooldown expires: %s "
                "(retry in %.1fs)",
                unit_id,
                sorted(name for name, _ in held),
                min_remaining,
            )
            self._handles[unit_id] = async_call_later(
                self.hass,
                min_remaining,
                partial(self._async_flush, unit_id),
            )

        for attribute_name in ready:
            accepted = await report_changed_attribute(
                self.hass, self.entry, store, unit_id, attribute_name
            )
            if accepted:
                self._last_sync[(unit_id, attribute_name)] = time.monotonic()

    def _unit_attributes(self, unit_id: str) -> dict[str, Any]:
        """Snapshot the DuerOS-visible attributes of one exposed unit."""
        unit = self._units[unit_id]
        device = self._devices[unit_id]
        attrs: dict[str, Any] = {}

        state = self.hass.states.get(unit.entity_id)
        if state is not None:
            adapter = get_adapter(state.domain, unit.device_class)
            if adapter is not None:
                for attribute in filtered_attributes(unit, adapter, state):
                    attrs[attribute["name"]] = attribute["value"]

        for capability, entity_id in unit.query_entities.items():
            if capability not in unit.enabled or entity_id == unit.entity_id:
                continue
            sibling = self.hass.states.get(entity_id)
            if sibling is None:
                continue
            sibling_adapter = get_adapter(sibling.domain)
            if sibling_adapter is None:
                continue
            for attribute in filtered_attributes(unit, sibling_adapter, sibling):
                attrs[attribute["name"]] = attribute["value"]

        for attribute in extra_attributes(self.hass, unit, device):
            attrs[attribute["name"]] = attribute["value"]
        return attrs
