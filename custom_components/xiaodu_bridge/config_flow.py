"""Config flow for the xiaodu bridge integration."""

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
from homeassistant.data_entry_flow import section
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

# Section keys of the per-device advanced options form (HA ``section``). Each
# groups a set of form fields under a translatable header
# (``options.step.device_advanced.sections.<key>.name``); on submit the fields
# arrive nested under the section key (``user_input[<key>]`` is a dict).
ADV_SECTION_CAPABILITIES = "capabilities"
ADV_SECTION_HIDDEN = "hidden_entities"
ADV_SECTION_MODE = "build_mode"
ADV_SECTION_ROLES = "role_bindings"
ADV_SECTION_NAMES = "device_names"


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
            return self.async_create_entry(title="xiaodu bridge", data=self._data)

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

    Each row is an HA physical device; expanding it shows the capabilities the
    device can expose to Xiaodu, and the user picks which to enable. The
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
        # Simple per-device capability choice (``caps`` editing).
        self._cap_config: dict[str, list[str]] = {}
        # The *normalized* per-device objects mirrored from the stored options
        # (advanced fields such as mode / bindings / hidden / names live here).
        self._objects: dict[str, dict[str, Any]] = {}
        # Advanced edits made during this options session, merged over the
        # mirrored objects at save time.
        self._adv_config: dict[str, dict[str, Any]] = {}
        # Render-time readable-key -> ("role", role) | ("name", appliance_key)
        # forward table for the advanced form of the currently edited device,
        # plus its ``role_to_display`` / ``appliance_to_display`` reverse tables
        # (an :class:`dueros.enhanced.AdvFieldMap`, rebuilt on every render).
        # The role / rename fields are keyed by *Chinese display labels* so the
        # HA front end shows 取暖 / 浴霸 instead of raw ``role:heating`` keys;
        # this map restores the canonical bindings / names keys on submit.
        self._adv_field_map: dict[str, tuple[str, str]] = {}
        self._edited: set[str] = set()
        self._sync_areas = False

    def _build_candidates(self) -> None:
        """Enumerate the exposable HA devices (device -> capabilities)."""
        from .dueros.enhanced import build_candidate_devices  # noqa: PLC0415

        self._candidates = build_candidate_devices(self.hass)

    @staticmethod
    def _cap_label(cap: str) -> str:
        return CAP_LABELS.get(cap, cap)

    @staticmethod
    def _show_caps(candidate: list[str], stored: list[str]) -> list[str]:
        """Checkboxes to show for a capability picker.

        An empty ``stored`` caps means default-all -> every candidate checked.
        Otherwise the stored subset is shown; ``power`` is always enforced so it
        is shown checked whenever the device offers it.
        """
        if not stored:
            return list(candidate)
        shown = [c for c in candidate if c in stored]
        if "power" in candidate and "power" not in shown:
            shown.insert(0, "power")
        return shown

    def _candidate(self, device_key: str) -> dict[str, Any] | None:
        return next((c for c in self._candidates if c["device_key"] == device_key), None)

    def _device_caps(self, device_key: str) -> list[str]:
        cand = self._candidate(device_key)
        return cand["capabilities"] if cand else []

    def _device_label(self, device_key: str) -> str:
        cand = self._candidate(device_key)
        name = cand["name"] if cand else device_key
        if device_key in self._adv_config:
            return f"{name}（高级已配置）"
        if device_key in self._edited or device_key in self._cap_config:
            return f"{name}（已配置）"
        return f"{name}（新增）"

    def _save(self) -> ConfigFlowResult:
        """Persist the device -> capability configuration (object schema)."""
        from .dueros.device_config import merge_device_obj

        devices_config: dict[str, Any] = {}
        for key in self._selected:
            # The stored base merged with this session's advanced overlay
            # (same merge the advanced form renders against).
            obj = merge_device_obj(self._objects.get(key), self._adv_config.get(key))
            if key in self._cap_config:
                obj["caps"] = list(self._cap_config[key])
            # Minimal serialization: drop empty optional containers so an
            # untouched simple device stays ``{"caps": [...]}``, a narrowed
            # device keeps its subset, and a default-all device stores
            # ``caps: []`` (dynamic) instead of a pinned explicit full list.
            for opt in ("bindings", "hidden", "names"):
                if not obj.get(opt):
                    obj.pop(opt, None)
            if not obj.get("mode") or obj["mode"] == "auto":
                obj.pop("mode", None)
            devices_config[key] = obj
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
        from .dueros.device_config import normalize

        self._build_candidates()
        if not self._selected:
            # First visit: mirror the currently configured devices onto the
            # object schema so the simple and advanced sub-flows agree on one
            # shape.
            current = normalize(self.config_entry.options.get(CONF_DEVICES)) or {}
            self._sync_areas = bool(self.config_entry.options.get(CONF_SYNC_AREAS, False))
            self._objects = {key: dict(entry or {}) for key, entry in current.items()}
            self._cap_config = {
                key: list((entry or {}).get("caps") or [])
                for key, entry in current.items()
            }
            self._selected = {
                c["device_key"]: c
                for c in self._candidates
                if c["device_key"] in current
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

    def _bind_device_step(self, step_id: str, device_key: str) -> None:
        """Bind a per-device row that opens that device's sub-menu."""

        async def _device_step(
            user_input: dict[str, Any] | None = None,
        ) -> ConfigFlowResult:
            self._current = device_key
            return await self.async_step_device_menu()

        setattr(self, f"async_step_{step_id}", _device_step)

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """List of the selected devices — one row per device."""
        if not self._selected:
            return await self.async_step_manage()

        menu_options: dict[str, str] = {}
        for index, key in enumerate(self._selected):
            step_id = f"dev_{index}"
            self._bind_device_step(step_id, key)
            menu_options[step_id] = self._device_label(key)
        menu_options["init"] = "返回上一级"
        return self.async_show_menu(
            step_id="devices",
            menu_options=menu_options,
            description_placeholders={"count": str(len(self._selected))},
        )

    async def async_step_device_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Per-device menu: 普通能力设置 vs 高级设置 (kept out of the list row)."""
        if getattr(self, "_current", None) is None:
            return await self.async_step_devices()
        return self.async_show_menu(
            step_id="device_menu",
            menu_options={
                "edit_device": "能力设置",
                "device_advanced": "高级设置",
                "devices": "返回设备列表",
            },
            description_placeholders={
                "device_name": self._device_label(getattr(self, "_current", "")),
            },
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
                    # Freshly added device: default-all (dynamic) until the user
                    # narrows it in a sub-editor.
                    self._cap_config[key] = []
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
                        selector.SelectSelectorConfig(mode="dropdown", options=options, multiple=True)
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
        from .dueros.device_config import serialize_caps  # noqa: PLC0415

        device_key = getattr(self, "_current", None)
        if device_key is None:
            return await self.async_step_devices()
        caps = self._device_caps(device_key)
        stored = self._cap_config.get(device_key)
        current = self._show_caps(caps, stored or [])
        options = [
            selector.SelectOptionDict(value=cap, label=self._cap_label(cap))
            for cap in caps
        ]

        if user_input is not None:
            if user_input.get("action") == "back":
                # Leave this page without applying anything (nothing is persisted
                # to the config entry until the top-level 保存并完成).
                return await self.async_step_device_menu()
            chosen = set(user_input.get(CONF_CAPABILITIES, []))
            # All selected normalizes back to [] (default-all) so the device
            # keeps following capabilities added later; ``power`` is implicit.
            self._cap_config[device_key] = serialize_caps(caps, chosen)
            self._edited.add(device_key)
            return await self.async_step_device_menu()

        return self.async_show_form(
            step_id="edit_device",
            description_placeholders={"device_name": self._device_label(device_key)},
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CAPABILITIES, default=current
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(mode="dropdown", options=options, multiple=True)
                    ),
                    vol.Optional("action", default="save"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            mode="dropdown",
                            options=[
                                selector.SelectOptionDict(value="save", label="完成（返回设备列表）"),
                                selector.SelectOptionDict(value="back", label="返回上一页（不保存本页改动）"),
                            ],
                            translation_key="xiaodu_options_action",
                        )
                    ),
                }
            ),
        )

    # --- per-device advanced overrides --------------------------------------

    _MODE_LABELS = {
        "auto": "自动识别",
        "generic": "拆分为单个设备",
    }
    _PROFILE_NAMES = {
        "YUBA": "浴霸",
        "SWEEPING_ROBOT": "扫地机器人",
        "CLOTHES_RACK": "晾衣架",
        "WASHING_MACHINE": "洗衣机",
    }
    _AUTO_ROLE = "__auto__"

    async def async_step_device_advanced(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """One combined form: caps / hidden / mode / role bindings / names."""
        from .dueros.device_config import (  # noqa: PLC0415
            merge_device_obj,
            serialize_caps,
        )
        from .dueros.enhanced import (  # noqa: PLC0415
            advanced_shape_key,
            adv_field_map,
            build_device_detail,
            restore_bindings_and_names,
            role_binding_specs,
        )
        from .dueros.profiles import register_default_profiles  # noqa: PLC0415
        from .dueros.registry import REGISTRY  # noqa: PLC0415

        device_key = getattr(self, "_current", None)
        if device_key is None:
            return await self.async_step_devices()

        register_default_profiles(REGISTRY)

        # The view is rendered against the *merged* object (stored base + this
        # session's advanced edits): the stored / just-picked ``mode`` therefore
        # re-shapes the detail, so switching a device to a forced profile shows
        # that profile's role selects and aggregate rename box even when auto
        # detection never matched it.
        merged = merge_device_obj(
            self._objects.get(device_key), self._adv_config.get(device_key)
        )
        detail = build_device_detail(self.hass, device_key, merged)
        caps_list = detail["caps_union"]
        # ``entities`` are the exposable-domain rows (hidden / capability picks);
        # role candidates and forced-profile plausibility draw from the *whole*
        # HA group (``all_entities``) so a role may bind a ``select`` / ``fan`` /
        # ``number`` / ``climate`` entity that is never exposed standalone.
        entities = detail["entities"]
        all_entities = detail["all_entities"]
        cur_mode = merged.get("mode", "auto") or "auto"
        shape = advanced_shape_key(cur_mode, detail["matched_profile"])
        profile = REGISTRY.get_profile(shape or "") if shape else None
        roles = profile.roles if profile else {}

        cur_bindings = dict(merged.get("bindings") or {})
        cur_hidden = list(merged.get("hidden") or [])
        cur_names = dict(merged.get("names") or {})

        if user_input is not None:
            if user_input.get("action") == "back":
                # Leave without applying anything (persist only at 保存并完成).
                return await self.async_step_device_menu()
            # Fields arrive nested under their form sections
            # (``user_input[<section>]`` is a dict keyed by that section's field
            # keys). A section the front end did not send means the user kept its
            # rendered defaults, so fall back to the shown values rather than
            # clearing the field.
            caps_sec = user_input.get(ADV_SECTION_CAPABILITIES)
            if isinstance(caps_sec, dict):
                chosen = set(caps_sec.get(CONF_CAPABILITIES) or [])
            else:
                chosen = set(
                    self._show_caps(
                        caps_list, self._cap_config.get(device_key) or []
                    )
                )
            # Capabilities: all selected normalizes to [] (default-all, dynamic);
            # a strict subset is stored without the always-implicit power.
            self._cap_config[device_key] = serialize_caps(caps_list, chosen)
            self._edited.add(device_key)

            # The advanced overlay is captured whole (not as a diff) so merging
            # it over the stored base also *clears* fields the user emptied.
            adv: dict[str, Any] = {}
            entity_ids = {e["id"] for e in entities}

            hidden_sec = user_input.get(ADV_SECTION_HIDDEN)
            if isinstance(hidden_sec, dict):
                raw_hidden = hidden_sec.get("hidden", cur_hidden)
            else:
                raw_hidden = cur_hidden
            adv["hidden"] = [e for e in raw_hidden if e in entity_ids]

            mode_sec = user_input.get(ADV_SECTION_MODE)
            if isinstance(mode_sec, dict):
                adv["mode"] = mode_sec.get("mode", cur_mode) or "auto"
            else:
                adv["mode"] = cur_mode or "auto"

            # Each rendered role/rename field is keyed by a Chinese display label
            # (see ``_adv_field_map``, rebuilt on every render) and lives inside
            # its 角色绑定 / 设备改名 section;
            # :func:`restore_bindings_and_names` walks the map to translate the
            # submitted values back onto the stored ``bindings`` (role) /
            # ``names`` (appliance_key) keys. Those two dicts *replace* the whole
            # stored field when merged, so a role left on 自动识别 (no candidate
            # entity, or the user reset it) or a cleared rename simply drops out
            # and is naturally removed on save — the "clear by empty replace"
            # semantics.
            default_label = {
                a["appliance_key"]: a["label"] for a in detail["appliances"]
            }
            bindings, names = restore_bindings_and_names(
                user_input,
                self._adv_field_map,
                default_labels=default_label,
                roles_section=ADV_SECTION_ROLES,
                names_section=ADV_SECTION_NAMES,
            )
            adv["bindings"] = bindings
            adv["names"] = names

            self._adv_config[device_key] = adv
            if adv["mode"] != cur_mode:
                # The build shape changed: re-render this step under the merged
                # object so the just-forced profile's role/rename widgets appear
                # (that is how an auto-unmatched device gets bound / renamed).
                return await self.async_step_device_advanced()
            return await self.async_step_device_menu()

        # ----- build the form (submit path already returned above) -----
        stored_caps = self._cap_config.get(device_key)
        cur_caps = self._show_caps(caps_list, stored_caps or [])
        caps_options = [
            selector.SelectOptionDict(value=cap, label=self._cap_label(cap))
            for cap in caps_list
        ]
        hidden_options = [
            selector.SelectOptionDict(value=e["id"], label=e["label"])
            for e in entities
        ]
        mode_options = [
            selector.SelectOptionDict(value="auto", label=self._MODE_LABELS["auto"]),
            selector.SelectOptionDict(value="generic", label=self._MODE_LABELS["generic"]),
        ]
        # Forced-shape choices follow auto-detection. A device auto already
        # classified (浴霸 -> YUBA, 晾衣杆 -> CLOTHES_RACK) only needs auto /
        # generic / its own shape — offering 扫地机/洗衣机 there was pure noise.
        # A device auto did *not* classify offers the registered shapes whose
        # roles can actually bind to this device's entities (e.g. a cover-only
        # airer missed by auto can still be forced onto 晾衣架). A plain light /
        # switch has no profile-role domain on it, so no forced shape is offered
        # at all — such a device is correctly a generic appliance, not a
        # detection failure waiting to be corrected. A previously-forced mode
        # stays selectable either way.
        matched_profile = detail["matched_profile"]
        if matched_profile and REGISTRY.get_profile(matched_profile):
            shape_profiles = [REGISTRY.get_profile(matched_profile)]
        else:
            shape_profiles = [
                p for p in REGISTRY.all_profiles()
                if any(role_binding_specs(p, all_entities).values())
            ]
        if profile is not None and all(
            p.key != profile.key for p in shape_profiles
        ):
            shape_profiles.append(profile)
        for p in shape_profiles:
            mode_options.append(
                selector.SelectOptionDict(
                    value=p.key, label=self._PROFILE_NAMES.get(p.key, p.key)
                )
            )

        # Each group of fields is wrapped in an HA ``section`` so the page shows
        # titled, expandable blocks (能力 / 隐藏实体 / 构建形态 / 角色绑定 / 设备改名).
        # Section fields submit *nested* under their section key; the per-device
        # footer ``action`` select stays at form level, outside any section.
        # Sections that end up with no fields (no role / rename widgets for this
        # build shape) are not emitted at all.
        schema: dict[Any, Any] = {
            vol.Optional(ADV_SECTION_CAPABILITIES): section(
                vol.Schema(
                    {
                        vol.Optional(
                            CONF_CAPABILITIES, default=list(cur_caps) or []
                        ): selector.SelectSelector(
                            selector.SelectSelectorConfig(mode="dropdown", options=caps_options, multiple=True)
                        ),
                    }
                ),
                {"collapsed": False},
            ),
            vol.Optional(ADV_SECTION_HIDDEN): section(
                vol.Schema(
                    {
                        vol.Optional("hidden", default=cur_hidden): selector.SelectSelector(
                            selector.SelectSelectorConfig(mode="dropdown", options=hidden_options, multiple=True)
                        ),
                    }
                ),
                {"collapsed": False},
            ),
            vol.Optional(ADV_SECTION_MODE): section(
                vol.Schema(
                    {
                        vol.Optional("mode", default=cur_mode): selector.SelectSelector(
                            selector.SelectSelectorConfig(mode="dropdown", options=mode_options)
                        ),
                    }
                ),
                {"collapsed": False},
            ),
        }

        # Role-binding and rename widgets use *Chinese display labels* as schema
        # keys (a profile role label like 取暖, an appliance label like 浴霸) so
        # the HA front end does not show raw ``role:heating`` keys. The matching
        # ``_adv_field_map`` table (readable key -> stored role / appliance_key)
        # is kept on the flow so the submit path can translate the input back; it
        # carries pre-built ``role_to_display`` / ``appliance_to_display``
        # reverse tables so the renderer never re-derives them by hand.
        specs = role_binding_specs(profile, all_entities) if profile else {}
        field_map = adv_field_map(
            {role: roles[role] for role in specs}, detail["appliances"]
        )
        self._adv_field_map = field_map

        # Every declared role gets a picker, even when this device has no
        # in-domain candidate entity: the field stays visible with only the
        # 自动识别 option (a real 浴霸 must keep 暖风档位 / 风速档位 / 设定温度 visible;
        # hiding roles that had no candidate was the previous regression).
        role_fields: dict[Any, Any] = {}
        for role in specs:
            candidates = specs[role]
            current_binding = cur_bindings.get(role)
            option_values = {e["id"] for e in candidates}
            if current_binding not in option_values:
                current_binding = self._AUTO_ROLE
            role_options = [
                selector.SelectOptionDict(
                    value=self._AUTO_ROLE, label="自动识别"
                )
            ]
            role_options.extend(
                selector.SelectOptionDict(value=e["id"], label=e["label"])
                for e in candidates
            )
            role_fields[
                vol.Optional(
                    field_map.role_to_display[role], default=current_binding
                )
            ] = selector.SelectSelector(
                selector.SelectSelectorConfig(mode="dropdown", options=role_options)
            )
        if role_fields:
            schema[vol.Optional(ADV_SECTION_ROLES)] = section(
                vol.Schema(role_fields),
                {"collapsed": False},
            )

        name_fields: dict[Any, Any] = {}
        for appliance in detail["appliances"]:
            key = appliance["appliance_key"]
            name_fields[
                vol.Optional(
                    field_map.appliance_to_display[key],
                    default=cur_names.get(key, appliance["label"]),
                )
            ] = str
        if name_fields:
            schema[vol.Optional(ADV_SECTION_NAMES)] = section(
                vol.Schema(name_fields),
                {"collapsed": False},
            )

        schema[
            vol.Optional("action", default="save")
        ] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                mode="dropdown",
                options=[
                    selector.SelectOptionDict(value="save", label="完成（返回设备列表）"),
                    selector.SelectOptionDict(value="back", label="返回上一页（不保存本页改动）"),
                ],
                translation_key="xiaodu_options_action",
            )
        )
        return self.async_show_form(
            step_id="device_advanced",
            description_placeholders={
                "device_name": self._device_label(device_key),
            },
            data_schema=vol.Schema(schema),
        )

    async def async_step_save(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Save the current configuration and finish."""
        return self._save()


__all__ = ["XiaoduConfigFlow", "XiaoduOptionsFlow"]
