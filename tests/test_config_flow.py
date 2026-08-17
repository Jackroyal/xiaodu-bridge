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

from custom_components.xiaodu.const import (
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
            CONF_PUBLIC_URL: "https://ha.example.com:8663",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "confirm"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_REDIRECT_URI] == "https://xiaodu.baidu.com/saiya/auth/test"
    assert result["data"][CONF_PUBLIC_URL] == "https://ha.example.com:8663"


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
            CONF_PUBLIC_URL: "https://ha.example.com:8663",
        },
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {CONF_REDIRECT_URI: "invalid_url"}


async def test_options_flow_saves_patterns(hass) -> None:
    from tests.common import MockConfigEntry

    entry = MockConfigEntry(domain=DOMAIN, data={})
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"entity_include_select": ["light.living_room"]},
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"]["entity_include"] == ["light.living_room"]
