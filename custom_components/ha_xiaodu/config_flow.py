"""Config flow for the Xiaodu (DuerOS) integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.helpers import selector

from .const import (
    CONF_BOT_ID,
    CONF_CAPABILITIES,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_DEVICES,
    CONF_SYNC_AREAS,
    CONF_PUBLIC_URL,
    CONF_REDIRECT_URI,
    CONF_UNITS,
    DOMAIN,
    DUEROS_SERVICE_PATH,
    OAUTH_AUTHORIZE_PATH,
    OAUTH_TOKEN_PATH,
)
from .devices import (
    CAP_LABELS,
    build_device_map,
    implied_capabilities,
    summarize_devices,
)

_LOGGER = logging.getLogger(__name__)


async def _schedule_device_sync(hass: Any, entry: ConfigEntry) -> None:
    """Notify DuerOS to re-sync devices (safe no-op when not configured)."""
    from .dueros_sync import sync_devices  # noqa: PLC0415
    from .oauth_server import _get_store  # noqa: PLC0415

    store = await _get_store(hass)
    await sync_devices(hass, entry, store)


class XiaoduConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Xiaodu config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._data: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow start."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        errors: dict[str, str] = {}
        if user_input is not None:
            redirect_uri = user_input[CONF_REDIRECT_URI].strip()
            public_url = user_input[CONF_PUBLIC_URL].strip().rstrip("/")
            if not user_input[CONF_CLIENT_ID].strip() or not user_input[
                CONF_CLIENT_SECRET
            ].strip():
                errors["base"] = "invalid_credentials"
            elif not user_input[CONF_BOT_ID].strip():
                errors["base"] = "invalid_bot_id"
            elif not redirect_uri.startswith("https://"):
                errors[CONF_REDIRECT_URI] = "invalid_url"
            elif not public_url.startswith("https://"):
                errors[CONF_PUBLIC_URL] = "invalid_url"
            else:
                self._data = {
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID].strip(),
                    CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET].strip(),
                    CONF_BOT_ID: user_input[CONF_BOT_ID].strip(),
                    CONF_REDIRECT_URI: redirect_uri,
                    CONF_PUBLIC_URL: public_url,
                }
                return await self.async_step_confirm()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                    vol.Required(CONF_BOT_ID): str,
                    vol.Required(CONF_REDIRECT_URI): str,
                    vol.Required(CONF_PUBLIC_URL): str,
                }
            ),
            errors=errors,
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the three URLs to fill in on the Xiaodu console."""
        if user_input is not None:
            return self.async_create_entry(title="Xiaodu", data=self._data)

        base = self._data[CONF_PUBLIC_URL]
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "authorize_url": f"{base}{OAUTH_AUTHORIZE_PATH}",
                "token_url": f"{base}{OAUTH_TOKEN_PATH}",
                "webservice_url": f"{base}{DUEROS_SERVICE_PATH}",
                "callback_url": self._data[CONF_REDIRECT_URI],
            },
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the OAuth credentials and public URLs."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            client_id = user_input[CONF_CLIENT_ID].strip()
            client_secret = user_input[CONF_CLIENT_SECRET].strip()
            bot_id = user_input[CONF_BOT_ID].strip()
            redirect_uri = user_input[CONF_REDIRECT_URI].strip()
            public_url = user_input[CONF_PUBLIC_URL].strip().rstrip("/")
            if not client_id or not client_secret:
                errors["base"] = "invalid_credentials"
            elif not bot_id:
                errors["base"] = "invalid_bot_id"
            elif not redirect_uri.startswith("https://"):
                errors[CONF_REDIRECT_URI] = "invalid_url"
            elif not public_url.startswith("https://"):
                errors[CONF_PUBLIC_URL] = "invalid_url"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={
                        CONF_CLIENT_ID: client_id,
                        CONF_CLIENT_SECRET: client_secret,
                        CONF_BOT_ID: bot_id,
                        CONF_REDIRECT_URI: redirect_uri,
                        CONF_PUBLIC_URL: public_url,
                    },
                )
                # Kick a device sync now that a botId is configured.
                self.hass.async_create_task(
                    _schedule_device_sync(self.hass, entry)
                )
                return self.async_abort(reason="reconfigure_successful")

        base = (entry.data.get(CONF_PUBLIC_URL) or "").rstrip("/")
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CLIENT_ID,
                        default=entry.data.get(CONF_CLIENT_ID, ""),
                    ): str,
                    vol.Required(
                        CONF_CLIENT_SECRET,
                        default=entry.data.get(CONF_CLIENT_SECRET, ""),
                    ): str,
                    vol.Required(
                        CONF_BOT_ID,
                        default=entry.data.get(CONF_BOT_ID, ""),
                    ): str,
                    vol.Required(
                        CONF_REDIRECT_URI,
                        default=entry.data.get(CONF_REDIRECT_URI, ""),
                    ): str,
                    vol.Required(
                        CONF_PUBLIC_URL,
                        default=entry.data.get(CONF_PUBLIC_URL, ""),
                    ): str,
                }
            ),
            description_placeholders={
                "authorize_url": f"{base}{OAUTH_AUTHORIZE_PATH}",
                "token_url": f"{base}{OAUTH_TOKEN_PATH}",
                "webservice_url": f"{base}{DUEROS_SERVICE_PATH}",
            },
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> XiaoduOptionsFlow:
        """Return the options flow for this config entry."""
        return XiaoduOptionsFlow()


class XiaoduOptionsFlow(OptionsFlow):
    """Handle Xiaodu options.

    Collapsible structure (native menus): the first page is the top level —
    a "中枢" section that expands into parallel speaker platforms (小度 now,
    Tmall Genie later); each platform expands into the flat list of selected
    devices; clicking a device opens its units (entities) and capabilities.
    Devices that are not touched keep their saved settings.
    """

    # Optional capabilities the user can toggle. The mandatory ones (power,
    # cover pause, YUBA mode / target temperature) are shown in the wizard as
    # force-checked entries and can never be switched off; ``percentage`` and
    # ``waterLevel`` are reserved model capabilities with no DuerOS action yet,
    # so they are not offered either. Per-unit filtering happens via ``cap in
    # unit.capabilities`` so each device type only shows what it supports.
    _SELECTABLE_CAPS = (
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
    def __init__(self) -> None:
        """Initialize the flow."""
        self._devices: dict[str, Any] = {}
        self._unit_config: dict[str, dict[str, list[str]]] = {}
        self._pending_units: list[tuple[str, str]] = []
        self._current: str | None = None
        self._edited: set[str] = set()
        self._sync_areas = False

    def _candidate_devices(self) -> list[Any]:
        """Return every exposable device (all units, all capabilities)."""
        return build_device_map(self.hass, {}).devices()

    @staticmethod
    def _selectable(unit: Any) -> list[str]:
        return [c for c in XiaoduOptionsFlow._SELECTABLE_CAPS if c in unit.capabilities]

    @staticmethod
    def _required_caps(unit: Any) -> list[str]:
        """Mandatory capabilities of a unit (force-checked, never removable)."""
        domain = unit.entity_id.split(".", 1)[0]
        required = implied_capabilities(
            domain=domain,
            device_class=unit.device_class,
            is_default=unit.is_default,
        )
        return [c for c in required if c in unit.capabilities]

    @staticmethod
    def _label(device: Any) -> str:
        """Short option label: room + device name (entity ids are too long)."""
        if device.area_name:
            return f"{device.area_name} · {device.name}"
        return device.name

    @staticmethod
    def _unit_label(device: Any, unit: Any) -> str:
        """Unit option label: default unit keeps the device name."""
        if unit.is_default:
            return f"{device.name}（默认）"
        return unit.name

    def _device_option_label(self, device: Any) -> str:
        """Row label: room + device name, marked new vs already configured."""
        label = self._label(device)
        saved = self.config_entry.options.get(CONF_DEVICES, {})
        if device.device_key in saved or device.device_key in self._edited:
            return f"{label}（已配置）"
        return f"{label}（新增）"

    def _bind_edit_step(self, step_id: str, device_key: str) -> None:
        """Bind a per-device menu step that opens its unit/capability editor."""

        async def _edit_step(
            user_input: dict[str, Any] | None = None,
        ) -> ConfigFlowResult:
            self._current = device_key
            return await self.async_step_unit_select()

        setattr(self, f"async_step_{step_id}", _edit_step)

    def _bind_group_step(self, step_id: str) -> None:
        """Bind a platform menu step that opens that platform's device list."""

        async def _step(
            user_input: dict[str, Any] | None = None,
        ) -> ConfigFlowResult:
            return await self.async_step_group()

        setattr(self, f"async_step_{step_id}", _step)

    def _platform_entries(self) -> list[tuple[str, str]]:
        """Parallel platform rows shown inside the 中枢 section.

        Each platform gets its own menu step, so a future Tmall Genie / Xiaoai
        platform simply appends a row here, sibling to 小度.
        """
        return [
            ("group_xiaodu", f"小度（{len(self._devices)} 台设备）"),
        ]

    def _current_units(self, device: Any) -> dict[str, Any]:
        """Return {entity_id: unit} of the currently exposed device (if any)."""
        current = build_device_map(self.hass, self.config_entry.options)
        current_device = current.device(device.device_key)
        if current_device is None:
            return {}
        return {u.entity_id: u for u in current_device.units}

    def _save(self) -> ConfigFlowResult:
        """Persist the device/unit/capability configuration."""
        devices_config: dict[str, dict[str, list[str]]] = {}
        for key, device in self._devices.items():
            if key in self._unit_config:
                devices_config[key] = self._unit_config[key]
                continue
            default = device.default_unit
            if default is None:
                continue
            devices_config[key] = {default.entity_id: self._selectable(default)}
        result = self.async_create_entry(
            title="",
            data={CONF_DEVICES: devices_config, CONF_SYNC_AREAS: self._sync_areas},
        )
        self.hass.async_create_task(
            self.hass.config_entries.async_reload(self.config_entry.entry_id)
        )
        # The exposed device set changed: ask DuerOS to re-discover.
        self.hass.async_create_task(
            _schedule_device_sync(self.hass, self.config_entry)
        )
        return result

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Top-level menu: the "中枢" section expands into the platforms."""
        candidates = self._candidate_devices()
        current = build_device_map(self.hass, self.config_entry.options)
        current_keys = {d.device_key for d in current.devices()}
        saved = dict(self.config_entry.options.get(CONF_DEVICES, {}) or {})

        if not self._devices:
            # First visit: mirror the currently exposed devices so the
            # expanded lists show what is already synced.
            self._devices = {
                d.device_key: d for d in candidates if d.device_key in current_keys
            }
            self._sync_areas = bool(
                self.config_entry.options.get(CONF_SYNC_AREAS, False)
            )
            for key, device in self._devices.items():
                if key in saved:
                    self._unit_config[key] = saved[key]
                else:
                    default = device.default_unit
                    if default is not None:
                        self._unit_config[key] = {
                            default.entity_id: self._selectable(default)
                        }

        if not candidates:
            return self._save()

        return self.async_show_menu(
            step_id="init",
            menu_options={
                "platform": f"中枢（{len(self._devices)} 台设备）",
                "manage": "添加 / 移除设备",
                "save": "保存并完成",
            },
            description_placeholders={
                "exposed_summary": summarize_devices(current),
                "candidate_count": str(len(candidates)),
            },
        )

    async def async_step_platform(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Expanded 中枢 section: one row per speaker platform."""
        menu_options: dict[str, str] = {}
        for step_id, label in self._platform_entries():
            self._bind_group_step(step_id)
            menu_options[step_id] = label
        menu_options["init"] = "返回上一级"
        return self.async_show_menu(
            step_id="platform",
            menu_options=menu_options,
            description_placeholders={
                "count": str(len(self._devices)),
            },
        )

    async def async_step_group(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Expanded platform section: the flat list of selected devices."""
        if not self._devices:
            return await self.async_step_platform()

        menu_options: dict[str, str] = {}
        for index, key in enumerate(self._devices):
            step_id = f"edit_{index}"
            self._bind_edit_step(step_id, key)
            menu_options[step_id] = self._device_option_label(self._devices[key])
        menu_options["platform"] = "返回上一级"
        return self.async_show_menu(
            step_id="group",
            menu_options=menu_options,
            description_placeholders={
                "count": str(len(self._devices)),
            },
        )

    async def async_step_manage(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select which devices Xiaodu may discover and control."""
        candidates = self._candidate_devices()
        saved = dict(self.config_entry.options.get(CONF_DEVICES, {}) or {})
        options = [
            selector.SelectOptionDict(value=d.device_key, label=self._label(d))
            for d in candidates
        ]

        if user_input is not None:
            selected = set(user_input.get(CONF_DEVICES, []))
            self._sync_areas = bool(user_input.get(CONF_SYNC_AREAS, False))
            self._devices = {
                d.device_key: d for d in candidates if d.device_key in selected
            }
            # Keep edits made earlier in this wizard; preserve saved configs;
            # brand-new devices default to the default unit with all caps.
            merged: dict[str, Any] = {}
            for key, device in self._devices.items():
                if key in self._unit_config:
                    merged[key] = self._unit_config[key]
                elif key in saved:
                    merged[key] = saved[key]
                else:
                    default = device.default_unit
                    if default is not None:
                        merged[key] = {
                            default.entity_id: self._selectable(default)
                        }
            self._unit_config = merged
            return await self.async_step_init()

        return self.async_show_form(
            step_id="manage",
            description_placeholders={
                "candidate_count": str(len(candidates)),
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICES,
                        default=sorted(self._devices),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_SYNC_AREAS,
                        default=self._sync_areas,
                    ): bool,
                }
            ),
        )

    async def async_step_save(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Save the current configuration and finish."""
        return self._save()

    async def async_step_unit_select(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick which units of the current device to sync to Xiaodu."""
        assert self._current is not None
        device = self._devices[self._current]
        current_units = self._current_units(device)

        if user_input is not None:
            chosen = set(user_input.get(CONF_UNITS, []))
            config = self._unit_config.setdefault(self._current, {})
            for entity_id in list(config):
                if entity_id not in chosen:
                    del config[entity_id]
            pending: list[tuple[str, str]] = []
            for entity_id in chosen:
                unit = next(
                    (u for u in device.units if u.entity_id == entity_id), None
                )
                if unit is None:
                    continue
                if self._selectable(unit):
                    pending.append((self._current, entity_id))
                else:
                    config[entity_id] = []  # nothing to configure beyond power
            self._pending_units = pending
            self._edited.add(self._current)
            self._current = None
            if self._pending_units:
                return await self.async_step_unit_caps()
            return await self.async_step_group()

        options = [
            selector.SelectOptionDict(
                value=unit.entity_id, label=self._unit_label(device, unit)
            )
            for unit in device.units
        ]
        enabled_units = [u.entity_id for u in current_units.values() if u.enabled]
        default_checked = enabled_units or [
            unit.entity_id for unit in device.units if unit.is_default
        ]
        return self.async_show_form(
            step_id="unit_select",
            description_placeholders={
                "device_name": device.name,
                "unit_hint": "每个勾选的单元会作为一个小度设备同步；默认单元保持设备名，其余单元默认关闭。",
            },
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UNITS, default=default_checked
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=options, multiple=True)
                    )
                }
            ),
        )

    async def async_step_unit_caps(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the capabilities for one unit of the current device."""
        if not self._pending_units:
            return await self.async_step_group()

        device_key, unit_entity_id = self._pending_units[0]
        device = self._devices[device_key]
        unit = next(u for u in device.units if u.entity_id == unit_entity_id)
        selectable = self._selectable(unit)
        required = self._required_caps(unit)
        current_unit = self._current_units(device).get(unit_entity_id)

        if user_input is not None:
            chosen = set(user_input.get(CONF_CAPABILITIES, []))
            # Only the optional caps are persisted; the mandatory ones are
            # implied at resolve time and can never be switched off.
            self._unit_config.setdefault(device_key, {})[unit_entity_id] = [
                cap for cap in selectable if cap in chosen
            ]
            self._pending_units.pop(0)
            if self._pending_units:
                return await self.async_step_unit_caps()
            return await self.async_step_group()

        if current_unit is not None:
            checked = {c for c in selectable if c in current_unit.enabled}
        else:
            checked = set(selectable)
        caps_default = [
            *required,
            *(c for c in selectable if c in checked and c not in required),
        ]
        listed = [*required, *(c for c in selectable if c not in required)]
        options = [
            selector.SelectOptionDict(value=cap, label=CAP_LABELS[cap]) for cap in listed
        ]
        return self.async_show_form(
            step_id="unit_caps",
            description_placeholders={
                "device_name": device.name,
                "unit_name": self._unit_label(device, unit),
                "power_note": "必选能力（如开关）始终启用，保存后自动恢复勾选，不可取消。",
            },
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CAPABILITIES, default=caps_default
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=options, multiple=True)
                    )
                }
            ),
        )
