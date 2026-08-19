"""Tests for Xiaodu setup/unload."""

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from custom_components.ha_xiaodu import (
    async_remove_config_entry_device,
    _sync_device_registry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.ha_xiaodu.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_DEVICES,
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
            CONF_PUBLIC_URL: "https://ha.example.com:8123",
        },
    )
    entry.add_to_hass(hass)

    assert await async_setup_entry(hass, entry)
    assert hass.data[DOMAIN]  # OAuth/HTTP state is registered

    assert await async_unload_entry(hass, entry)
    assert entry.entry_id not in hass.data[DOMAIN]


async def test_sync_device_registry(hass: HomeAssistant) -> None:
    """Exposed devices are mirrored into the device registry."""
    device_registry = dr.async_get(hass)
    underlying_entry = MockConfigEntry(domain="test", data={}, title="测试")
    underlying_entry.add_to_hass(hass)
    underlying = device_registry.async_get_or_create(
        config_entry_id=underlying_entry.entry_id,
        identifiers={("test", "ciwo_lamp")},
        name="次卧灯",
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="小度中枢",
        data={
            CONF_CLIENT_ID: "dueros_test",
            CONF_CLIENT_SECRET: "secret",
            CONF_REDIRECT_URI: "https://xiaodu.baidu.com/saiya/auth/test",
            CONF_PUBLIC_URL: "https://ha.example.com:8123",
        },
        options={CONF_DEVICES: {underlying.id: {"light.ciwo": ["power"]}}},
    )
    entry.add_to_hass(hass)

    _sync_device_registry(hass, entry)

    synced = device_registry.async_get_device(identifiers={(DOMAIN, underlying.id)})
    assert synced is not None
    assert synced.name == "次卧灯"
    assert entry.entry_id in synced.config_entries

    # Deselecting the device removes it from the registry again.
    hass.config_entries.async_update_entry(entry, options={CONF_DEVICES: {}})
    _sync_device_registry(hass, entry)
    assert device_registry.async_get_device(identifiers={(DOMAIN, underlying.id)}) is None


async def test_remove_config_entry_device(hass: HomeAssistant) -> None:
    """The official remove-device hook deselects one synced device."""
    device_registry = dr.async_get(hass)
    underlying_entry = MockConfigEntry(domain="test", data={}, title="测试")
    underlying_entry.add_to_hass(hass)
    underlying = device_registry.async_get_or_create(
        config_entry_id=underlying_entry.entry_id,
        identifiers={("test", "ciwo_lamp")},
        name="次卧灯",
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="小度中枢",
        data={
            CONF_CLIENT_ID: "dueros_test",
            CONF_CLIENT_SECRET: "secret",
            CONF_REDIRECT_URI: "https://xiaodu.baidu.com/saiya/auth/test",
            CONF_PUBLIC_URL: "https://ha.example.com:8123",
        },
        options={CONF_DEVICES: {underlying.id: {"light.ciwo": ["power"]}}},
    )
    entry.add_to_hass(hass)
    await async_setup_entry(hass, entry)

    synced = device_registry.async_get_device(identifiers={(DOMAIN, underlying.id)})
    assert synced is not None
    assert await async_remove_config_entry_device(hass, entry, synced)
    assert entry.options.get(CONF_DEVICES) == {}
    assert (
        device_registry.async_get_device(identifiers={(DOMAIN, underlying.id)})
        is None
    )
