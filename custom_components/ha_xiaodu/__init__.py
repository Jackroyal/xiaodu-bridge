"""Xiaodu (DuerOS) integration for Home Assistant.

This is a hub integration without entity platforms: it serves the OAuth2
endpoints and the DuerOS smart-home WebService. The HTTP views are registered
once per setup; all runtime state (OAuth tokens, enhanced device set) is
resolved per-request from the config entry. Pending DuerOS timing requests are
loaded from storage at setup and re-armed with HA's event-loop scheduler.

The runtime model is the DuerOS *semantic* model (``dueros`` package): every
exposable device is surfaced as one or more ``DuerDevice`` appliances. The
legacy per-entity (unit) path is no longer used.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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

_LOGGER = logging.getLogger(__name__)

# Title shown on the integration page for this hub entry.
ENTRY_TITLE = "小度中枢"
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
    """Remove one synced device from Xiaodu exposure.

    这是 HA 官方的设备移除钩子：模块级存在该函数即令
    ``config_entry.supports_remove_device`` 为真，核心前端就会在设备行
    三点菜单里渲染「移除设备」项，点击确认后通过
    ``config/device_registry/remove_config_entry`` WS 调用本函数。
    这是核心唯一为设备行菜单提供的官方扩展点（与「单元与能力」入口的
    注入方案不同，本函数零注入、随 HA 升级稳定）。

    核心处理器容忍集成先移除设备（"Integration might have removed the
    config entry already, that is fine"），因此这里直接更新 options 并
    重载，让注册表同步清理设备条目即可。
    """
    device_key = next(
        (
            ids[1]
            for ids in device_entry.identifiers
            if ids[0] == DOMAIN
        ),
        None,
    )
    if device_key is None:
        return False

    options = dict(config_entry.options)
    devices = dict(options.get(CONF_DEVICES) or {})
    if device_key not in devices:
        return False
    devices.pop(device_key)
    options[CONF_DEVICES] = devices

    hass.config_entries.async_update_entry(config_entry, options=options)
    await hass.config_entries.async_reload(config_entry.entry_id)
    return True






async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Xiaodu from a config entry."""
    data = hass.data.setdefault(DOMAIN, {})
    # The device-center (semantic) device set is built lazily by the DuerOS
    # WebService on the first request (see dueros.protocol._get_enhanced) and
    # cached in ``hass.data``, so it always reflects devices loaded at that time.
    # Give the hub entry a readable headline on the integrations page.
    if not entry.title or entry.title == "Xiaodu":
        hass.config_entries.async_update_entry(entry, title=ENTRY_TITLE)
    # Register the synced devices with this config entry so the integrations
    # page row becomes expandable and lists exactly what Xiaodu may control.
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
    """Keep the device registry aligned with the exposed device set.

    The integrations page renders one row per config entry; the expand
    button and the "N 个设备" menu entry only appear when the entry owns
    device-registry entries. Mirroring ``options[CONF_DEVICES]`` into the
    registry makes the row fold open to exactly the devices Xiaodu may
    discover and control.

    这些镜像设备一律带 ``disabled_by=DeviceEntryDisabler.INTEGRATION``：
    HA 2026.8 的设备页默认过滤已禁用设备，因此同一台设备不会在「设置 →
    设备」列表里和 Xiaomi Home 的真实设备重复出现；但设备仍保留在注册表
    中，集成页的折叠展开、设备计数与官方「移除设备」入口照常工作（行会
    按禁用态置灰显示）。需要核对时在设备页勾选「已禁用」筛选即可看到
    这些镜像；单设备能力配置走集成项的「设备与能力」选项流程。
    """
    registry = dr.async_get(hass)
    devices_config = entry.options.get(CONF_DEVICES) or {}

    # Resolve the current friendly name/area from the underlying device.
    wanted: dict[str, str] = {}
    wanted_areas: dict[str, str | None] = {}
    for device_key in devices_config:
        underlying = registry.async_get(device_key)
        if underlying is not None:
            wanted[device_key] = underlying.name_by_user or underlying.name or device_key
            wanted_areas[device_key] = underlying.area_id
        else:
            # The underlying HA device is gone; keep a stable placeholder so
            # the synced count stays truthful until the entry is reconfigured.
            wanted[device_key] = device_key
            wanted_areas[device_key] = None

    # Drop registry devices we own that are no longer exposed.
    for device in list(registry.devices.values()):
        device_key = next(
            (ids[1] for ids in device.identifiers if ids[0] == DOMAIN),
            None,
        )
        if device_key is None or device_key in wanted:
            continue
        if entry.entry_id in device.config_entries and len(device.config_entries) == 1:
            registry.async_remove_device(device.id)

    # Create or update the exposed devices under this config entry.
    for device_key, name in wanted.items():
        device = registry.async_get_device(identifiers={(DOMAIN, device_key)})
        if device is None:
            device = registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, device_key)},
                name=name,
                manufacturer=DEVICE_MANUFACTURER,
                model=DEVICE_MODEL,
                disabled_by=dr.DeviceEntryDisabler.INTEGRATION,
            )
        updates: dict[str, object] = {}
        if device.name != name:
            updates["name"] = name
        if device.area_id != wanted_areas[device_key]:
            updates["area_id"] = wanted_areas[device_key]
        if device.config_entry_id != entry.entry_id:
            updates["new_config_entry_id"] = entry.entry_id
        if device.disabled_by != dr.DeviceEntryDisabler.INTEGRATION:
            # 迁移旧版本创建的无禁用标记镜像，避免它们重新出现在设备列表。
            updates["disabled_by"] = dr.DeviceEntryDisabler.INTEGRATION
        if updates:
            registry.async_update_device(device.id, **updates)


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
