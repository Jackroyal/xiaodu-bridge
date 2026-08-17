"""Tests for Xiaodu setup/unload."""

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.core import HomeAssistant

from custom_components.xiaodu import async_setup_entry, async_unload_entry
from custom_components.xiaodu.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_PUBLIC_URL,
    CONF_REDIRECT_URI,
    DOMAIN,
)
from tests.common import MockConfigEntry


async def test_setup_and_unload(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_CLIENT_ID: "dueros_test",
            CONF_CLIENT_SECRET: "secret",
            CONF_REDIRECT_URI: "https://xiaodu.baidu.com/saiya/auth/test",
            CONF_PUBLIC_URL: "https://ha.example.com:8663",
        },
    )
    entry.add_to_hass(hass)

    assert await async_setup_entry(hass, entry)
    assert hass.data[DOMAIN]  # OAuth/HTTP state is registered

    assert await async_unload_entry(hass, entry)
    assert entry.entry_id not in hass.data[DOMAIN]
