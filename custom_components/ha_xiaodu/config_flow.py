"""Config flow for the xiaodu integration."""

from __future__ import annotations

import json
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
    DOMAIN,
    DUEROS_SERVICE_PATH,
    OAUTH_AUTHORIZE_PATH,
    OAUTH_TOKEN_PATH,
)
from .devices import CAP_LABELS

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
            return self.async_create_entry(title="xiaodu", data=self._data)

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
    """Xiaodu options: 设备 → 能力（device → capability）。

    The legacy "unit" (entity-level appliance) concept is removed. Each row is
    an HA physical device; expanding it shows the capabilities the device can
    expose to Xiaodu, and the user picks which to enable. The device-center
    semantic model builds one or more ``DuerDevice`` appliances per device.
    """

    # Capabilities a user may toggle. ``power`` is implied for control
    # appliances and always stays on; read-only query capabilities
    # (temperature / humidity) are selectable like any other.
    _SELECTABLE_CAPS = (
        "power",
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
        "waterLevel",
        "percentage",
        "pause",
        "continue",
        "temperature",
        "humidity",
        "warmthLevel",
        "electricityCapacity",
        "workState",
        "timeLeft",
    )

    def __init__(self) -> None:
        """Initialize the flow."""
        self._candidates: list[dict[str, Any]] = []
        self._selected: dict[str, Any] = {}   # device_key -> candidate
        self._cap_config: dict[str, list[str]] = {}
        self._edited: set[str] = set()
        self._sync_areas = False

    def _build_candidates(self) -> None:
        """Enumerate the exposable HA devices (device -> capabilities)."""
        from .dueros.enhanced import build_candidate_devices  # noqa: PLC0415

        self._candidates = build_candidate_devices(self.hass)

    @staticmethod
    def _cap_label(cap: str) -> str:
        return CAP_LABELS.get(cap, cap)

    def _candidate(self, device_key: str) -> dict[str, Any] | None:
        return next((c for c in self._candidates if c["device_key"] == device_key), None)

    def _device_caps(self, device_key: str) -> list[str]:
        cand = self._candidate(device_key)
        return cand["capabilities"] if cand else []

    def _device_label(self, device_key: str) -> str:
        cand = self._candidate(device_key)
        name = cand["name"] if cand else device_key
        if device_key in self._edited or device_key in self._cap_config:
            return f"{name}（已配置）"
        return f"{name}（新增）"

    def _save(self) -> ConfigFlowResult:
        """Persist the device -> capability configuration."""
        devices_config: dict[str, list[str]] = {}
        for key in self._selected:
            if key in self._cap_config:
                devices_config[key] = self._cap_config[key]
            else:
                devices_config[key] = self._device_caps(key)
        result = self.async_create_entry(
            title="",
            data={
                CONF_DEVICES: devices_config,
                CONF_SYNC_AREAS: self._sync_areas,
            },
        )
        self.hass.async_create_task(
            self.hass.config_entries.async_reload(self.config_entry.entry_id)
        )
        self.hass.async_create_task(
            _schedule_device_sync(self.hass, self.config_entry)
        )
        return result

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Top-level menu for the 中枢 section."""
        self._build_candidates()
        if not self._selected:
            # First visit: mirror the currently configured devices.
            current = self.config_entry.options.get(CONF_DEVICES, {}) or {}
            self._sync_areas = bool(self.config_entry.options.get(CONF_SYNC_AREAS, False))
            self._selected = {
                c["device_key"]: c
                for c in self._candidates
                if c["device_key"] in current
            }
            self._cap_config = {
                k: list(v) for k, v in current.items() if isinstance(v, (list, tuple))
            }
        if not self._candidates:
            return self._save()

        menu = {
            "manage": "添加 / 移除设备",
            "devices": f"已选设备（{len(self._selected)}）",
            "save": "保存并完成",
        }
        return self.async_show_menu(
            step_id="init",
            menu_options=menu,
            description_placeholders={
                "candidate_count": str(len(self._candidates)),
            },
        )

    def _bind_edit_step(self, step_id: str, device_key: str) -> None:
        """Bind a per-device widget that opens its capability editor."""

        async def _edit_step(
            user_input: dict[str, Any] | None = None,
        ) -> ConfigFlowResult:
            self._current = device_key
            return await self.async_step_edit_device()

        setattr(self, f"async_step_{step_id}", _edit_step)

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Expanded list of the selected devices."""
        if not self._selected:
            return await self.async_step_manage()

        menu_options: dict[str, str] = {}
        for index, key in enumerate(self._selected):
            step_id = f"edit_{index}"
            self._bind_edit_step(step_id, key)
            menu_options[step_id] = self._device_label(key)
        menu_options["init"] = "返回上一级"
        return self.async_show_menu(
            step_id="devices",
            menu_options=menu_options,
            description_placeholders={"count": str(len(self._selected))},
        )

    async def async_step_manage(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select which devices Xiaodu may discover and control."""
        options = [
            selector.SelectOptionDict(value=c["device_key"], label=c["name"])
            for c in self._candidates
        ]

        if user_input is not None:
            selected = set(user_input.get(CONF_DEVICES, []))
            self._sync_areas = bool(user_input.get(CONF_SYNC_AREAS, False))
            self._selected = {
                c["device_key"]: c for c in self._candidates if c["device_key"] in selected
            }
            for key in self._selected:
                if key not in self._cap_config:
                    self._cap_config[key] = self._device_caps(key)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="manage",
            description_placeholders={
                "candidate_count": str(len(self._candidates)),
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICES,
                        default=sorted(self._selected),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=options, multiple=True)
                    ),
                    vol.Optional(
                        CONF_SYNC_AREAS,
                        default=self._sync_areas,
                    ): bool,
                }
            ),
        )

    async def async_step_edit_device(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose the capabilities of one selected device."""
        device_key = getattr(self, "_current", None)
        if device_key is None:
            return await self.async_step_devices()
        caps = self._device_caps(device_key)
        current = self._cap_config.get(device_key, caps)
        options = [
            selector.SelectOptionDict(value=cap, label=self._cap_label(cap))
            for cap in caps
        ]

        if user_input is not None:
            chosen = set(user_input.get(CONF_CAPABILITIES, []))
            self._cap_config[device_key] = [cap for cap in caps if cap in chosen or cap == "power"]
            self._edited.add(device_key)
            return await self.async_step_devices()

        return self.async_show_form(
            step_id="edit_device",
            description_placeholders={"device_name": self._device_label(device_key)},
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CAPABILITIES, default=current
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=options, multiple=True)
                    )
                }
            ),
        )

    async def async_step_save(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Save the current configuration and finish."""
        return self._save()


__all__ = ["XiaoduConfigFlow", "XiaoduOptionsFlow"]
