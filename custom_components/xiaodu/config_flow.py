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
    CONF_DEVICE,
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

    Interaction: pick devices first, then "click" each selected device to
    choose which units (entities) to sync and their capabilities. The
    default unit of a device keeps the device name; extra units (e.g. the
    light on a 晾衣杆) are separate speaker appliances and default to off.
    Choosing "keep defaults and finish" saves everything with the default
    unit enabled (all its capabilities).
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
    _DONE = "__done__"

    def __init__(self) -> None:
        """Initialize the flow."""
        self._devices: dict[str, Any] = {}
        self._unit_config: dict[str, dict[str, list[str]]] = {}
        self._pending: list[str] = []
        self._pending_units: list[tuple[str, str]] = []
        self._current: str | None = None
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
    def _needs_config(device: Any) -> bool:
        """A device needs a wizard step when it has toggles beyond defaults."""
        return len(device.units) > 1 or any(
            XiaoduOptionsFlow._selectable(unit) for unit in device.units
        )

    @staticmethod
    def _unit_label(device: Any, unit: Any) -> str:
        """Unit option label: default unit keeps the device name."""
        if unit.is_default:
            return f"{device.name}（默认）"
        return unit.name

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
        """Select which devices Xiaodu may discover and control."""
        candidates = self._candidate_devices()
        current = build_device_map(self.hass, self.config_entry.options)
        current_keys = {d.device_key for d in current.devices()}

        options = [
            selector.SelectOptionDict(value=d.device_key, label=self._label(d))
            for d in candidates
        ]

        if not options:
            return self.async_create_entry(
                title="", data={CONF_DEVICES: {}, CONF_SYNC_AREAS: False}
            )

        if user_input is not None:
            selected = set(user_input.get(CONF_DEVICES, []))
            self._sync_areas = bool(user_input.get(CONF_SYNC_AREAS, False))
            self._devices = {
                d.device_key: d for d in candidates if d.device_key in selected
            }
            self._unit_config = {}
            self._pending = [
                key
                for key, device in self._devices.items()
                if self._needs_config(device)
            ]
            if not self._devices:
                return self._save()
            return await self.async_step_device_select()

        return self.async_show_form(
            step_id="init",
            description_placeholders={
                "exposed_summary": summarize_devices(current),
                "candidate_count": str(len(candidates)),
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICES,
                        default=sorted(current_keys),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_SYNC_AREAS,
                        default=bool(
                            self.config_entry.options.get(CONF_SYNC_AREAS, False)
                        ),
                    ): bool,
                }
            ),
        )

    async def async_step_device_select(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick the next device whose capabilities to configure."""
        if not self._pending:
            return self._save()

        if user_input is not None:
            choice = user_input.get(CONF_DEVICE, "")
            if choice in self._devices and choice in self._pending:
                self._current = choice
                return await self.async_step_unit_select()
            return self._save()

        options = [
            selector.SelectOptionDict(
                value=key, label=self._label(self._devices[key])
            )
            for key in self._pending
        ]
        options.append(
            selector.SelectOptionDict(
                value=self._DONE, label="保持默认并完成（跳过剩余设备）"
            )
        )
        return self.async_show_form(
            step_id="device_select",
            description_placeholders={
                "remaining": str(len(self._pending)),
                "power_note": "必选能力（如开关）始终启用，不可取消；未配置的设备将默认启用默认单元的全部能力。",
            },
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=options)
                    )
                }
            ),
        )

    async def async_step_unit_select(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick which units of the current device to sync to Xiaodu."""
        assert self._current is not None
        device = self._devices[self._current]
        current_units = self._current_units(device)

        if user_input is not None:
            chosen = list(user_input.get(CONF_UNITS, []))
            config = self._unit_config.setdefault(self._current, {})
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
            if self._current in self._pending:
                self._pending.remove(self._current)
            self._current = None
            if self._pending_units:
                return await self.async_step_unit_caps()
            if self._pending:
                return await self.async_step_device_select()
            return self._save()

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
            if self._pending:
                return await self.async_step_device_select()
            return self._save()

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
            if self._pending:
                return await self.async_step_device_select()
            return self._save()

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
