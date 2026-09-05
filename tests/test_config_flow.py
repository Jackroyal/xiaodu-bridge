"""Tests for the Xiaodu config flow.

These need Home Assistant plus ``pytest-homeassistant-custom-component``:

    pip install -e ".[test]"
    pytest tests/test_config_flow.py

Without the plugin they are skipped automatically.
"""

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.xiaodu_bridge.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_PUBLIC_URL,
    CONF_REDIRECT_URI,
    DOMAIN,
)


async def test_flow_creates_entry(hass) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CLIENT_ID: "dueros_test",
            CONF_CLIENT_SECRET: "secret",
            CONF_REDIRECT_URI: "https://xiaodu.baidu.com/saiya/auth/test",
            CONF_PUBLIC_URL: "https://ha.example.com:8123",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "confirm"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_REDIRECT_URI] == "https://xiaodu.baidu.com/saiya/auth/test"
    assert result["data"][CONF_PUBLIC_URL] == "https://ha.example.com:8123"


async def test_flow_rejects_invalid_url(hass) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_CLIENT_ID: "dueros_test",
            CONF_CLIENT_SECRET: "secret",
            CONF_REDIRECT_URI: "not-a-url",
            CONF_PUBLIC_URL: "https://ha.example.com:8123",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_REDIRECT_URI: "invalid_url"}


async def test_options_flow_hub_menu(hass) -> None:
    """中枢菜单版选项流：首层菜单 → 添加/移除设备表单 → 取消。"""
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er

    from custom_components.xiaodu_bridge.const import CONF_DEVICES, CONF_SYNC_AREAS
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={CONF_DEVICES: {}, CONF_SYNC_AREAS: False},
    )
    entry.add_to_hass(hass)

    # 提供一台可暴露设备，使首层进入菜单而不是直接保存空配置。
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={("test", "living_lamp")},
        name="客厅灯",
    )
    er.async_get(hass).async_get_or_create(
        "switch", "living_lamp", device_id=device.id
    )
    hass.states.async_set("switch.living_lamp", "off")

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.MENU
    assert {"platform", "manage", "save"} <= set(result["menu_options"])

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "manage"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "manage"

    await hass.config_entries.options.async_abort(result["flow_id"])
