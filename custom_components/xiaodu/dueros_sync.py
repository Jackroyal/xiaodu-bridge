"""Push device-change notifications to DuerOS (device sync).

The Xiaodu smart-home skill can notify DuerOS that a user's device set
changed (e.g. the user added/removed devices or changed which devices are
exposed); DuerOS then re-triggers ``DiscoverAppliancesRequest`` so the new
list is picked up.

Interface (DuerOS "notification" protocol):

    POST https://xiaodu.baidu.com/saiya/smarthome/devicesync
    {"botId": <skill id>, "logId": <uuid>, "openUids": [<user openUid>, ...]}

Only the integration's own ``bot_id`` (filled in by the user next to the
OAuth config) plus the openUids observed during discovery are sent. The HA
imports live inside the function so this module stays importable without a
HA runtime for pure-logic tests.
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .oauth_store import XiaoduOAuthStore

from .const import CONF_BOT_ID, DUEROS_DEVICE_SYNC_URL

_LOGGER = logging.getLogger(__name__)

_SYNC_BATCH_SIZE = 5  # DuerOS accepts at most 5 openUids per request


def build_sync_batches(
    open_uids: list[str], batch_size: int = _SYNC_BATCH_SIZE
) -> list[list[str]]:
    """Split openUids into batches of at most ``batch_size``."""
    return [
        open_uids[i : i + batch_size] for i in range(0, len(open_uids), batch_size)
    ]


def build_sync_payload(bot_id: str, log_id: str, open_uids: list[str]) -> dict[str, Any]:
    """Build the devicesync request body."""
    return {
        "botId": bot_id,
        "logId": log_id,
        "openUids": list(open_uids),
    }


async def sync_devices(
    hass: HomeAssistant,
    entry: Any,
    store: XiaoduOAuthStore,
    session: Any | None = None,
) -> None:
    """Notify DuerOS to re-sync the device list for all bound users.

    Safe to call on every options save: without a configured ``bot_id`` or
    without bound users it is a no-op, and DuerOS treats the sync as an
    idempotent "please re-discover" hint.
    """
    bot_id = str((entry.data or {}).get(CONF_BOT_ID, "") or "").strip()
    open_uids = store.open_uids()
    if not bot_id:
        _LOGGER.info("Xiaodu device sync skipped: botId is not configured")
        return
    if not open_uids:
        _LOGGER.info("Xiaodu device sync skipped: no bound users yet")
        return

    if session is None:
        from homeassistant.helpers.aiohttp_client import (  # noqa: PLC0415
            async_get_clientsession,
        )

        session = async_get_clientsession(hass)

    for batch in build_sync_batches(open_uids):
        payload = build_sync_payload(bot_id, str(uuid.uuid4()), batch)
        try:
            async with session.post(DUEROS_DEVICE_SYNC_URL, json=payload) as response:
                try:
                    body = await response.json(content_type=None)
                except ValueError:
                    body = {}
                _LOGGER.info(
                    "Xiaodu device sync -> HTTP %s, msg=%s, openUids=%s",
                    response.status,
                    body.get("msg") if isinstance(body, dict) else body,
                    batch,
                )
        except Exception:  # noqa: BLE001 - a failed push must not break the flow
            _LOGGER.warning("Xiaodu device sync failed: %s", payload, exc_info=True)
