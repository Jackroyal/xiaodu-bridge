"""Xiaodu (DuerOS) integration for Home Assistant.

This is a hub integration without entity platforms: it serves the OAuth2
endpoints and the DuerOS smart-home WebService. The HTTP views are registered
once per setup; all runtime state (OAuth tokens, device map) is resolved
per-request from the config entry. Pending DuerOS timing requests are loaded
from storage at setup and re-armed with HA's event-loop scheduler.
"""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.frontend import (
    DATA_EXTRA_MODULE_URL,
    add_extra_js_url,
)
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_DEVICES,
    DATA_STATE_REPORT_MANAGER,
    DATA_TIMER_MANAGER,
    DOMAIN,
)
from .devices import build_device_map, implied_capabilities
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

# Title shown on the integration page for this hub entry; the 设备与服务 page
# uses it as the row headline (falls back to the domain name when empty).
ENTRY_TITLE = "小度中枢"
DEVICE_MANUFACTURER = "DuerOS"
DEVICE_MODEL = "小度智能中枢"

# 「设备与服务」页设备行菜单的「单元与能力」入口来自前端模块
# ha-xiaodu-device-config.js（注入式，见该文件头部注释）。
# 说明：frontend.add_extra_js_url 是官方注册前端模块的 API（HACS 同样
# 用它注入 iconset），但往核心组件 ha-config-entry-device-row 的菜单里
# 追加自定义项属于非官方用法：HA 大版本升级可能让该入口失效（已做
# 兜底，最坏情况只是菜单项不显示）。官方替代方案为「设备与能力」选项
# 流程或自定义配置面板（config_panel_domain），本集成暂保留注入方案。
FRONTEND_MODULE_URL = "/ha_xiaodu/www/ha-xiaodu-device-config.js"

# Optional capabilities offered in the per-device unit/capability editor.
# Mandatory capabilities (power, cover pause, YUBA modes / target temperature)
# are force-kept by ``implied_capabilities`` and never shown as toggles.
SELECTABLE_CAPS = (
    "brightness",
    "colorTemperature",
    "color",
    "volume",
    "channel",
    "mute",
    "fanSpeed",
    "targetTemperature",
    "targetHumidity",
    "mode",
    "suction",
    "continue",
    "temperature",
    "humidity",
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register frontend assets and the per-device editor API.

    这里的静态路径、WS 命令都是官方机制；唯一带注入性质的是前端模块里
    对设备行菜单的 DOM 追加（见 www/ha-xiaodu-device-config.js 注释）。
    """
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/ha_xiaodu/www",
                hass.config.path("custom_components", DOMAIN, "www"),
                cache_headers=False,
            )
        ]
    )
    _ensure_frontend_module(hass)
    # 配置条目在启动早期就会被设置，而 frontend 组件要到更晚才初始化
    # DATA_EXTRA_MODULE_URL；首次注册往往落在空窗期，所以挂一个
    # EVENT_HOMEASSISTANT_START 兜底，等所有组件就绪后再补注册。
    # 该监听在 async_setup_entry 里也会再调一次 _ensure_frontend_module，
    # 幂等，不会重复添加。
    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_START,
        lambda _event: _ensure_frontend_module(hass),
    )
    websocket_api.async_register_command(hass, ws_device_config)
    websocket_api.async_register_command(hass, ws_set_device_config)
    return True


def _ensure_frontend_module(hass: HomeAssistant) -> None:
    """Register the device-menu module with the frontend (idempotent).

    add_extra_js_url 只是往 frontend 的模块集合里加 URL，页面每次加载时
    都会重新渲染该集合，因此运行期注册即可生效，无需重启。
    """
    try:
        manager = hass.data.get(DATA_EXTRA_MODULE_URL)
        if manager is not None and FRONTEND_MODULE_URL not in manager.urls:
            add_extra_js_url(hass, FRONTEND_MODULE_URL)
            _LOGGER.debug("Registered frontend module %s", FRONTEND_MODULE_URL)
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Failed to register frontend module %s", FRONTEND_MODULE_URL)


def _get_entry(hass: HomeAssistant) -> ConfigEntry | None:
    """Return the single Xiaodu hub entry, if configured."""
    entries = hass.config_entries.async_entries(DOMAIN)
    return entries[0] if entries else None


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_xiaodu/device_config",
        vol.Required("device_key"): str,
    }
)
@websocket_api.async_response
async def ws_device_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Return the unit/capability model of one exposed device."""
    entry = _get_entry(hass)
    if entry is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "No config entry"
        )
        return

    candidates = build_device_map(hass, {})
    device = candidates.device(msg["device_key"])
    if device is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Device not found"
        )
        return

    current = build_device_map(hass, entry.options)
    current_device = current.device(msg["device_key"])
    current_units = (
        {unit.entity_id: unit for unit in current_device.units}
        if current_device is not None
        else {}
    )

    units = []
    for unit in device.units:
        enabled = unit.entity_id in current_units
        required = set(
            implied_capabilities(
                domain=unit.entity_id.split(".", 1)[0],
                device_class=unit.device_class,
                is_default=unit.is_default,
            )
        ) & set(unit.capabilities)
        units.append(
            {
                "entity_id": unit.entity_id,
                "name": unit.name,
                "is_default": unit.is_default,
                "capabilities": sorted(unit.capabilities),
                "selectable": [
                    capability
                    for capability in SELECTABLE_CAPS
                    if capability in unit.capabilities
                ],
                "required": sorted(required),
                "enabled": enabled,
                "enabled_capabilities": (
                    sorted(current_units[unit.entity_id].enabled) if enabled else []
                ),
            }
        )

    connection.send_result(
        msg["id"],
        {
            "device": {
                "name": device.name,
                "area_name": device.area_name,
                "units": units,
            }
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "ha_xiaodu/set_device_config",
        vol.Required("device_key"): str,
        vol.Required("units"): {str: [str]},
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_set_device_config(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Update the units/capabilities exposed for one device."""
    entry = _get_entry(hass)
    if entry is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "No config entry"
        )
        return

    candidates = build_device_map(hass, {})
    device = candidates.device(msg["device_key"])
    if device is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Device not found"
        )
        return

    unit_by_entity = {unit.entity_id: unit for unit in device.units}
    cleaned: dict[str, list[str]] = {}
    for entity_id, capabilities in msg["units"].items():
        unit = unit_by_entity.get(entity_id)
        if unit is None:
            continue
        valid = {c for c in capabilities if c in unit.capabilities}
        valid |= set(
            implied_capabilities(
                domain=entity_id.split(".", 1)[0],
                device_class=unit.device_class,
                is_default=unit.is_default,
            )
        ) & set(unit.capabilities)
        cleaned[entity_id] = sorted(valid)

    options = dict(entry.options)
    devices = dict(options.get(CONF_DEVICES) or {})
    if cleaned:
        devices[msg["device_key"]] = cleaned
    else:
        devices.pop(msg["device_key"], None)
    options[CONF_DEVICES] = devices

    hass.config_entries.async_update_entry(entry, options=options)
    await hass.config_entries.async_reload(entry.entry_id)
    connection.send_result(msg["id"], {})


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
            value
            for domain, value in device_entry.identifiers
            if domain == DOMAIN
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
    # Belt-and-suspenders: the page module must be registered even if the
    # component-level setup ran before the frontend was ready.
    _ensure_frontend_module(hass)
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

    # Active state reporting: push changereports when exposed entities change
    # outside the speaker, so DuerOS keeps its attribute values fresh.
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
            (value for domain, value in device.identifiers if domain == DOMAIN),
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
            )
        updates: dict[str, object] = {}
        if device.name != name:
            updates["name"] = name
        if device.area_id != wanted_areas[device_key]:
            updates["area_id"] = wanted_areas[device_key]
        if device.config_entry_id != entry.entry_id:
            updates["new_config_entry_id"] = entry.entry_id
        if updates:
            registry.async_update_device(device.id, **updates)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Rebuild the state-report index when the entry's options/data change."""
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
