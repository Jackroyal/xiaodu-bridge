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

import json
import logging
import time
import uuid
from collections.abc import Iterable
from functools import partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import Event, HomeAssistant

    from .oauth_store import XiaoduOAuthStore

from .const import (
    CONF_BOT_ID,
    DUEROS_CHANGE_REPORT_URL,
)
from .dueros.model import CAP_KIND_CONTROL

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

# A push DuerOS refused (rate limit / "stop sync") is retried once after this
# delay: long enough to clear the documented 60-second per-attribute window,
# close enough that a refusal caused by a post-restart burst is not missed.
REFUSAL_RETRY_SECONDS = 65.0

def build_change_report(
    bot_id: str,
    open_uid: str,
    appliance_id: str,
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
                "applianceId": appliance_id,
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

async def report_changed_attribute(
    hass: HomeAssistant,
    entry: Any,
    store: XiaoduOAuthStore,
    appliance_id: str,
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
    if not bot_id or not open_uids or not appliance_id or not attribute_name:
        _LOGGER.debug(
            "State report skipped: botId=%s openUids=%d appliance=%s attr=%s",
            bot_id or "<missing>",
            len(open_uids),
            appliance_id,
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
        payload = build_change_report(bot_id, open_uid, appliance_id, attribute_name)
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
                    appliance_id,
                    attribute_name,
                    open_uid,
                )
                if not _is_acknowledged(msg):
                    # DuerOS sometimes answers a ChangeReport with something
                    # other than its "update N attributes" acknowledgement —
                    # e.g. "Cloud response name is not ReportStateResponse,
                    # stop sync" (status 21096, updated_attribute_num 0), where
                    # the sync was refused. Only the full body says why, so
                    # keep it.
                    _LOGGER.warning(
                        "Xiaodu state report -> 云端未确认同步 appliance=%s attr=%s "
                        "status=%s body=%s",
                        appliance_id,
                        attribute_name,
                        response.status,
                        _format_body(body),
                    )
                if _sync_applied(response.status, body):
                    accepted = True
        except Exception:  # noqa: BLE001 - a failed push must not break the flow
            _LOGGER.warning("Xiaodu state report failed: %s", payload, exc_info=True)
    return accepted


def _sync_applied(status: Any, body: Any) -> bool:
    """Did DuerOS actually apply this ChangeReport?

    HTTP 200 alone does not mean the sync happened — DuerOS also answers 200
    when it refuses: the documented per-attribute rate limit ("... can only
    sync ...") and the restart-burst refusal (status 21096, "Cloud response
    name is not ReportStateResponse, stop sync", whose body reports
    ``data.updated_attribute_num == 0``). Only a reply that reports an update
    counts, because the caller records a 62-second per-attribute cooldown for
    accepted pushes only: a refused attribute stays out of that cooldown and is
    re-sent on its next change instead of waiting out a sync that never landed.
    """
    if status != 200 or not isinstance(body, dict):
        return False
    text = str(body.get("msg") or "").strip()
    if "can only sync" in text:
        return False
    data = body.get("data")
    updated = data.get("updated_attribute_num") if isinstance(data, dict) else None
    if isinstance(updated, int):
        return updated > 0
    return text.startswith("update")


def _is_acknowledged(msg: Any) -> bool:
    """Is this the cloud's usual ChangeReport acknowledgement?

    Known-good replies are the per-attribute update count ("update N
    attributes"), an empty body (older responses), and the documented
    per-attribute rate limit ("... can only sync ..."), which the caller
    handles by not counting the push as accepted.
    """
    text = str(msg or "").strip()
    return not text or text.startswith("update") or "can only sync" in text


def _format_body(body: Any) -> str:
    """One-line, length-capped rendering of a cloud response body for logs."""
    try:
        text = json.dumps(body, ensure_ascii=False)
    except (TypeError, ValueError):
        text = str(body)
    return text[:600]

class StateReportManager:
    """Listen for exposed-device state changes and push changereports.

    One instance per config entry. It keeps a snapshot of the DuerOS-visible
    attributes per ``DuerDevice`` appliance (built from the semantic model).
    When an event touches any entity that feeds a device (the device itself, a
    sibling query entity such as humidity, or a YUBA control switch), it diffs
    the snapshot and schedules a debounced report that pushes the changed
    attribute names back to DuerOS (using the stable ``applianceId``).

    Pure read-only appliances (no control capability, e.g. temperature /
    humidity sensors) are skipped: DuerOS rejects ChangeReportRequest for
    appliances without control actions. They still advertise *query* actions
    (``getTemperatureReading`` / ``getHumidity``) so voice queries work.
    """

    def __init__(self, hass: HomeAssistant, entry: Any) -> None:
        self.hass = hass
        self.entry = entry
        self.update_unsub: Any | None = None
        self._unsub: Any | None = None
        self._startup_unsub: Any | None = None
        self._stopped = False
        # entity_id -> appliance (device) ids that must refresh on change
        self._index: dict[str, list[str]] = {}
        # appliance id -> DuerDevice
        self._devices: dict[str, Any] = {}
        # structural fingerprint of ``_devices`` (ids / capabilities / bindings)
        self._signature: tuple = ()
        # appliance id -> last reported attribute snapshot ({name: value})
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._pending: dict[str, set[str]] = {}
        self._handles: dict[str, Any] = {}
        self._confirmed: dict[str, float] = {}
        # (appliance id, attribute name) -> monotonic time of the last accepted push
        self._last_sync: dict[tuple[str, str], float] = {}
        # (appliance id, attribute) -> its one delayed retry was already used
        self._retry_used: set[tuple[str, str]] = set()

    def _build_devices(self) -> None:
        """Rebuild the semantic device set from the current entry options."""
        from .dueros.enhanced import build_enhanced_for_hass  # noqa: PLC0415

        enhanced = build_enhanced_for_hass(self.hass, self.entry)
        self._devices = {d.device_id: d for d in enhanced.all()}
        self._signature = self._structure_signature(self._devices.values())

    @staticmethod
    def _structure_signature(devices: Iterable[Any]) -> tuple:
        """Structural fingerprint of a device set (ids, types, caps, bindings).

        Two sets with the same signature expose exactly the same appliances
        with the same capabilities bound to the same entities, so a rebuild
        (and the cooldown reset it implies) can be skipped.
        """
        return tuple(
            sorted(
                (
                    dev.device_id,
                    tuple(dev.appliance_types),
                    tuple(
                        sorted(
                            (
                                cap.key,
                                tuple(
                                    sorted(
                                        (b.role, b.entity_id) for b in cap.bindings
                                    )
                                ),
                            )
                            for cap in dev.capabilities
                        )
                    ),
                )
                for dev in devices
            )
        )

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
            # Entities may not exist yet during startup; rebuild once ready.
            self._startup_unsub = self.hass.bus.async_listen_once(
                EVENT_HOMEASSISTANT_STARTED, self._async_on_startup
            )
        _LOGGER.debug(
            "State report listener registered, %d devices indexed",
            len(self._devices),
        )

    async def _async_on_startup(self, _event: Event) -> None:
        """Rebuild the index once HA finished startup (entities now exist)."""
        self._startup_unsub = None
        self.async_rebuild()
        _LOGGER.debug(
            "State report index rebuilt after startup: %d devices",
            len(self._devices),
        )

    def async_rebuild(self) -> None:
        """Rebuild the entity index and snapshots from the semantic model.

        Called at setup and whenever the config entry changes (options save /
        reconfigure), so newly exposed/hidden devices take effect immediately.
        """
        self._build_devices()
        self._rebuild_index(reset_cooldowns=True)

    def async_refresh_if_changed(self) -> bool:
        """Rebuild the index only when the device structure actually changed.

        Called (debounced) after entity/device/area registry changes and after
        entities are added or removed. Registry "update" events fire for many
        trivial changes, so the signature check keeps them from rebuilding the
        index and from resetting the DuerOS per-attribute cooldowns. Returns
        True when the structure changed and the index was rebuilt.
        """
        if self._stopped:
            return False
        from .dueros.enhanced import build_enhanced_for_hass  # noqa: PLC0415

        enhanced = build_enhanced_for_hass(self.hass, self.entry)
        devices = {d.device_id: d for d in enhanced.all()}
        signature = self._structure_signature(devices.values())
        if signature == self._signature:
            return False
        self._devices = devices
        self._signature = signature
        # Keep the report cooldowns: unchanged devices must not re-report
        # attributes that DuerOS still considers freshly synced.
        self._rebuild_index(reset_cooldowns=False)
        _LOGGER.debug(
            "State report index refreshed after structure change: %d devices",
            len(self._devices),
        )
        return True

    def _rebuild_index(self, *, reset_cooldowns: bool) -> None:
        """Rebuild the entity index and attribute snapshots."""
        if reset_cooldowns:
            # A rebuild (startup, options update) invalidates the cooldown and
            # confirmation state, but *not* the in-flight reports: a pending
            # report is an unsynced change, and the post-startup burst is
            # exactly where the cloud refuses pushes. Dropping the timers here
            # (and with them a scheduled retry) would leave those attributes
            # unsynced until they change again, so the handles and the pending
            # set are left alone — a flush for an appliance that no longer
            # exists is refused by the cloud and then dropped.
            self._confirmed.clear()
            self._last_sync.clear()
            self._retry_used.clear()

        index: dict[str, set[str]] = {}
        for dev_id, dev in self._devices.items():
            for mapping in dev.capabilities:
                for binding in mapping.bindings:
                    index.setdefault(binding.entity_id, set()).add(dev_id)

        self._index = {entity_id: sorted(ids) for entity_id, ids in index.items()}
        self._snapshots = {
            dev_id: self._device_attributes(dev_id) for dev_id in self._devices
        }
        _LOGGER.debug(
            "State report index rebuilt: %d devices, %d event mappings",
            len(self._devices),
            len(self._index),
        )

    def _entities_for(self, device: Any, mapping: Any) -> dict[str, Any]:
        """Resolve a capability mapping's bindings into role -> live state."""
        return {
            binding.role: state
            for binding in mapping.bindings
            if (state := self.hass.states.get(binding.entity_id)) is not None
        }

    def _device_attributes(self, device_id: str) -> dict[str, Any]:
        """Snapshot the DuerOS-visible attributes of one DuerDevice appliance."""
        device = self._devices.get(device_id)
        if device is None:
            return {}
        from .dueros.model import ReadContext  # noqa: PLC0415

        attrs: dict[str, Any] = {}
        for mapping in device.capabilities:
            ctx = ReadContext(
                hass=self.hass,
                device=device,
                entities=self._entities_for(device, mapping),
            )
            attr = mapping.read(ctx)
            if attr is not None:
                attrs[attr.name] = attr.value
        return attrs

    def mark_confirmed(self, device_id: str) -> None:
        """Record that a Xiaodu control just confirmed this appliance's state."""
        self._confirmed[device_id] = time.monotonic()

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
            handle()  # async_call_later returns a callable cancel handle
        self._handles.clear()
        self._pending.clear()
        self._confirmed.clear()
        self._last_sync.clear()
        self._retry_used.clear()
        self._index.clear()
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
        if not self._devices and self.hass.state == CoreState.running:
            # Self-heal if the index was built before entities existed.
            self.async_rebuild()
        device_ids = self._index.get(entity_id)
        if not device_ids:
            return
        _LOGGER.debug(
            "State change event for %s feeds devices %s",
            entity_id,
            device_ids,
        )
        for device_id in device_ids:
            if self._suppressed(device_id):
                _LOGGER.debug(
                    "Skip state report for %s: control confirmation in progress",
                    device_id,
                )
                continue
            device = self._devices.get(device_id)
            if device is None:
                continue
            # DuerOS rejects changereport for pure read-only appliances. They
            # do advertise query actions (getTemperatureReading / getHumidity),
            # so detect "query-only" by capability kind, not by actions == [].
            if not any(
                m.capability.kind == CAP_KIND_CONTROL for m in device.capabilities
            ):
                _LOGGER.debug(
                    "Skip state report for %s: query-only device "
                    "(DuerOS rejects changereport for pure sensors)",
                    device_id,
                )
                continue
            old = self._snapshots.get(device_id)
            new = self._device_attributes(device_id)
            changed = changed_attribute_names(old, new)
            self._snapshots[device_id] = new
            if changed:
                _LOGGER.debug(
                    "State changed for %s: %s",
                    device_id,
                    sorted(changed),
                )
                self._schedule_report(device_id, changed)

    def _suppressed(self, device_id: str) -> bool:
        confirmed_at = self._confirmed.get(device_id)
        return (
            confirmed_at is not None
            and time.monotonic() - confirmed_at < CONTROL_SUPPRESS_SECONDS
        )

    def _schedule_report(self, device_id: str, names: set[str]) -> None:
        # A real state change of an attribute grants it a fresh delayed retry
        # budget (see _take_retry): the refusal that consumed the previous
        # retry may well be stale by now.
        for name in names:
            self._retry_used.discard((device_id, name))
        pending = self._pending.setdefault(device_id, set())
        pending |= names
        if device_id in self._handles:
            _LOGGER.debug(
                "Report for %s already pending, merging %s",
                device_id,
                sorted(names),
            )
            return
        from homeassistant.helpers.event import async_call_later  # noqa: PLC0415

        _LOGGER.debug(
            "Scheduling state report for %s in %.1fs: %s",
            device_id,
            STATE_REPORT_DEBOUNCE_SECONDS,
            sorted(pending),
        )
        self._handles[device_id] = async_call_later(
            self.hass,
            STATE_REPORT_DEBOUNCE_SECONDS,
            partial(self._async_flush, device_id),
        )

    async def _async_flush(self, device_id: str, _now: Any) -> None:
        self._handles.pop(device_id, None)
        names = self._pending.pop(device_id, set())
        if not names:
            return

        from .oauth_server import _get_store  # noqa: PLC0415

        store = await _get_store(self.hass)
        bot_id = str((self.entry.data or {}).get(CONF_BOT_ID, "") or "").strip()
        _LOGGER.debug(
            "Flushing state report for %s: attrs=%s botId=%s openUids=%s",
            device_id,
            sorted(names),
            bot_id or "<missing>",
            len(store.open_uids()),
        )

        now = time.monotonic()
        ready: list[str] = []
        held: list[tuple[str, float]] = []
        for attribute_name in sorted(names):
            last_sync = self._last_sync.get((device_id, attribute_name), 0.0)
            remaining = last_sync + ATTR_SYNC_COOLDOWN_SECONDS - now
            if remaining <= 0:
                ready.append(attribute_name)
            else:
                held.append((attribute_name, remaining))

        if held:
            self._pending[device_id] = {name for name, _ in held}
            _LOGGER.debug(
                "Holding attrs for %s until DuerOS cooldown expires: %s "
                "(retry in %.1fs)",
                device_id,
                sorted(name for name, _ in held),
                min(remaining for _, remaining in held),
            )

        # A refused push (rate limit / "stop sync") gets one delayed retry: the
        # documented per-attribute window is 60 seconds, and a refusal caused by
        # the post-restart burst is usually gone by the time it elapses. Both
        # reasons to flush again are folded into a single timer so the device
        # never ends up with two competing handles.
        next_flush: float | None = min((remaining for _, remaining in held), default=None)
        refused: list[str] = []
        for attribute_name in ready:
            accepted = await report_changed_attribute(
                self.hass, self.entry, store, device_id, attribute_name
            )
            if accepted:
                self._last_sync[(device_id, attribute_name)] = time.monotonic()
                self._retry_used.discard((device_id, attribute_name))
                continue
            if not self._take_retry(device_id, attribute_name):
                continue
            refused.append(attribute_name)
            self._pending.setdefault(device_id, set()).add(attribute_name)
            next_flush = (
                REFUSAL_RETRY_SECONDS
                if next_flush is None
                else min(next_flush, REFUSAL_RETRY_SECONDS)
            )

        if refused:
            _LOGGER.debug(
                "Retrying refused attrs for %s in %.1fs: %s",
                device_id,
                REFUSAL_RETRY_SECONDS,
                sorted(refused),
            )
        if next_flush is not None and self._pending.get(device_id):
            from homeassistant.helpers.event import async_call_later  # noqa: PLC0415

            self._handles[device_id] = async_call_later(
                self.hass, next_flush, partial(self._async_flush, device_id)
            )

    def _take_retry(self, device_id: str, attribute_name: str) -> bool:
        """Claim the one delayed retry allowed per refused push.

        Every real state change re-grants it (see ``_schedule_report``), so a
        cloud that keeps refusing cannot turn this into a retry loop: after its
        single retry the attribute simply waits for its next change.
        """
        key = (device_id, attribute_name)
        if key in self._retry_used:
            return False
        self._retry_used.add(key)
        return True

