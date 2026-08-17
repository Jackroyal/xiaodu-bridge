"""Xiaodu (DuerOS) integration for Home Assistant.

This is a hub integration without entity platforms: it serves the OAuth2
endpoints and the DuerOS smart-home WebService. The HTTP views are registered
once per setup; all runtime state (OAuth tokens, device map) is resolved
per-request from the config entry. Pending DuerOS timing requests are loaded
from storage at setup and re-armed with HA's event-loop scheduler.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DATA_TIMER_MANAGER, DOMAIN
from .oauth_server import (
    DATA_VIEWS_REGISTERED,
    XiaoduDuerOSServiceView,
    XiaoduDuerOSView,
    XiaoduOAuthAuthorizeView,
    XiaoduOAuthTokenView,
)
from .timers import TimedServiceManager


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaodu from a config entry."""
    data = hass.data.setdefault(DOMAIN, {})
    if not data.get(DATA_VIEWS_REGISTERED):
        hass.http.register_view(XiaoduOAuthAuthorizeView())
        hass.http.register_view(XiaoduOAuthTokenView())
        hass.http.register_view(XiaoduDuerOSView())
        hass.http.register_view(XiaoduDuerOSServiceView())
        data[DATA_VIEWS_REGISTERED] = True

    if DATA_TIMER_MANAGER not in data:
        data[DATA_TIMER_MANAGER] = TimedServiceManager(hass)
    await data[DATA_TIMER_MANAGER].async_load()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry (no entity platforms are loaded)."""
    data = hass.data.get(DOMAIN, {})
    manager = data.get(DATA_TIMER_MANAGER)
    if manager is not None:
        manager.cancel_all()
    data.pop(entry.entry_id, None)
    return True
