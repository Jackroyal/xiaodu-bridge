"""xiaodu bridge integration for Home Assistant.

This is a hub integration without entity platforms: it serves the OAuth2
endpoints and the DuerOS smart-home WebService. The HTTP views are registered
once per setup; all runtime state (OAuth tokens, enhanced device set) is
resolved per-request from the config entry. Pending DuerOS timing requests are
loaded from storage at setup and re-armed with HA's event-loop scheduler.

The runtime model is the DuerOS *semantic* model (``dueros`` package): every
exposable device is surfaced as one or more ``DuerDevice`` appliances. The
legacy per-entity (unit) path is no longer used.

Following hub-integration conventions (like HomeKit Bridge), the device
registry holds a single virtual "hub" device; bridged HA devices are not
mirrored into it.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_DEVICES,
    DATA_ENHANCED_DEVICES,
    DATA_STATE_REPORT_MANAGER,
    DATA_TIMER_MANAGER,
    DOMAIN,
)

from .oauth_server import (
    DATA_VIEWS_REGISTERED,
    XiaoduDuerOSServiceView,
    XiaoduDuerOSView,
    XiaoduOAuthAuthorizeView,
    XiaoduOAuthTokenView,
)
from .state_report import StateReportManager
from .timers import TimedServiceManager

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)

# Title shown on the integration page for this hub entry.
ENTRY_TITLE = "xiaodu bridge"
DEVICE_MANUFACTURER = "DuerOS"
DEVICE_MODEL = "小度智能中枢"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the hub (no entity platforms, no device-menu injection).

    The per-device "单元与能力" frontend module and its WebSocket commands are
    obsolete: device → capability configuration is handled by the options flow.
    """
    return True


def _get_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Return the single Xiaodu hub entry, if configured."""
    entries = hass.config_entries.async_entries(DOMAIN)
    return entries[0] if entries else None


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Allow the official "Remove device" action for hub-owned entries.

    桥接型集成只保留一个「小度中枢」虚拟设备（对齐 HomeKit Bridge 惯例）。
    「移除设备」仅清理注册表条目本身，不会改动 ``CONF_DEVICES`` 配置，
    也不影响小度侧已发现的设备；中枢条目会在下次集成加载时自动重建。
    旧版本遗留的每设备镜像条目同样允许手动移除。
    """
    return any(ids[0] == DOMAIN for ids in device_entry.identifiers)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaodu from a config entry."""
    data = hass.data.setdefault(DOMAIN, {})
    # The device-center (semantic) device set is built lazily by the DuerOS
    # WebService on the first request (see dueros.protocol._get_enhanced) and
    # cached in ``hass.data``, so it always reflects devices loaded at that time.
    # Give the hub entry a readable headline on the integrations page.
    if not entry.title or entry.title in ("Xiaodu", "xiaodu"):
        hass.config_entries.async_update_entry(entry, title=ENTRY_TITLE)
    # Ensure the single hub device exists so the integrations page row can
    # fold open (HomeKit-Bridge style: one virtual device per hub entry).
    _sync_device_registry(hass, entry)
    if not data.get(DATA_VIEWS_REGISTERED):
        hass.http.register_view(XiaoduOAuthAuthorizeView())
        hass.http.register_view(XiaoduOAuthTokenView())
        hass.http.register_view(XiaoduDuerOSView())
        hass.http.register_view(XiaoduDuerOSServiceView())
        data[DATA_VIEWS_REGISTERED] = True

    if DATA_TIMER_MANAGER not in data:
        data[DATA_TIMER_MANAGER] = TimedServiceManager(hass)
    await data[DATA_TIMER_MANAGER].async_load()

    manager = StateReportManager(hass, entry)
    data[DATA_STATE_REPORT_MANAGER] = manager
    manager.async_start()
    manager.update_unsub = entry.add_update_listener(_async_update_listener)
    return True



def _sync_device_registry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ensure exactly one hub device exists for this config entry.

    对齐 HA 桥接型集成惯例（如 HomeKit Bridge）：整个集成只在设备注册表
    中保留一个「小度中枢」虚拟条目，作为集成页折叠展开与设备计数的锚点。
    被桥接的 HA 设备不再镜像进注册表——它们在 HA 侧由各自的真实集成展示，
    在小度侧由语义模型（``dueros`` 包）管理，能力配置走集成选项流程。

    v0.9.2 之前创建的每设备镜像条目（identifiers 为 ``(DOMAIN, device_key)``
    且以「集成禁用」标记）在此统一清理，仅当该条目只属于本集成时移除。
    """
    registry = dr.async_get(hass)

    hub = registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    if hub is None:
        hub = registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, entry.entry_id)},
            name=ENTRY_TITLE,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
        )
    updates: dict[str, object] = {}
    if hub.name_by_user is None and hub.name != ENTRY_TITLE:
        updates["name"] = ENTRY_TITLE
    if hub.manufacturer != DEVICE_MANUFACTURER:
        updates["manufacturer"] = DEVICE_MANUFACTURER
    if hub.model != DEVICE_MODEL:
        updates["model"] = DEVICE_MODEL
    if hub.disabled_by is not None:
        # 中枢必须保持启用，才能出现在默认设备列表中。
        updates["disabled_by"] = None
    if entry.entry_id not in hub.config_entries:
        updates["new_config_entry_id"] = entry.entry_id
    if updates:
        registry.async_update_device(hub.id, **updates)

    # 清理旧版每设备镜像条目（含 v0.9.1 的禁用镜像）。
    for device in list(registry.devices.values()):
        if device.id == hub.id:
            continue
        if entry.entry_id not in device.config_entries:
            continue
        if (DOMAIN, entry.entry_id) in device.identifiers:
            continue
        if not any(ids[0] == DOMAIN for ids in device.identifiers):
            continue
        if len(device.config_entries) == 1:
            registry.async_remove_device(device.id)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Rebuild the device set + state-report index on options/data change."""
    from .dueros.enhanced import build_enhanced_for_hass  # noqa: PLC0415

    hass.data.setdefault(DOMAIN, {})[DATA_ENHANCED_DEVICES] = build_enhanced_for_hass(hass, entry)
    _sync_device_registry(hass, entry)
    manager = hass.data.get(DOMAIN, {}).get(DATA_STATE_REPORT_MANAGER)
    if manager is not None:
        manager.async_rebuild()


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry (no entity platforms are loaded)."""
    data = hass.data.get(DOMAIN, {})
    manager = data.get(DATA_TIMER_MANAGER)
    if manager is not None:
        manager.cancel_all()
    report_manager = data.get(DATA_STATE_REPORT_MANAGER)
    if report_manager is not None:
        await report_manager.async_shutdown()
    data.pop(entry.entry_id, None)
    return True
