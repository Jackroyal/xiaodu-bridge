"""Tests for Xiaodu setup/unload."""

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.xiaodu_bridge import (
    async_remove_config_entry_device,
    _sync_device_registry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.xiaodu_bridge.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_DEVICES,
    CONF_PUBLIC_URL,
    CONF_REDIRECT_URI,
    DATA_ENHANCED_DEVICES,
    DATA_STRUCTURE_REFRESH_HANDLE,
    DATA_STRUCTURE_UNSUBS,
    DOMAIN,
)
from tests.common import MockConfigEntry, async_fire_time_changed


def _entry_data() -> dict:
    return {
        CONF_CLIENT_ID: "dueros_test",
        CONF_CLIENT_SECRET: "secret",
        CONF_REDIRECT_URI: "https://xiaodu.baidu.com/saiya/auth/test",
        CONF_PUBLIC_URL: "https://ha.example.com:8123",
    }


async def test_setup_and_unload(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, data=_entry_data())
    entry.add_to_hass(hass)

    assert await async_setup_entry(hass, entry)
    assert hass.data[DOMAIN]  # OAuth/HTTP state is registered

    assert await async_unload_entry(hass, entry)
    assert entry.entry_id not in hass.data[DOMAIN]


async def test_sync_device_registry_creates_single_hub(
    hass: HomeAssistant,
) -> None:
    """Only one hub device is registered, regardless of exposed devices."""
    device_registry = dr.async_get(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="小度中枢",
        data=_entry_data(),
        options={CONF_DEVICES: {"some-device-key": {"light.ciwo": ["power"]}}},
    )
    entry.add_to_hass(hass)

    _sync_device_registry(hass, entry)

    owned = [
        device
        for device in device_registry.devices.values()
        if entry.entry_id in device.config_entries
    ]
    assert len(owned) == 1
    hub = owned[0]
    assert hub.identifiers == {(DOMAIN, entry.entry_id)}
    assert hub.name == "小度中枢"
    assert hub.manufacturer == "DuerOS"
    assert hub.model == "小度智能中枢"
    assert hub.disabled_by is None

    # Re-running the sync is idempotent and keeps user renames.
    device_registry.async_update_device(hub.id, name_by_user="我的中枢")
    _sync_device_registry(hass, entry)
    hub = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert hub.name_by_user == "我的中枢"


async def test_sync_device_registry_cleans_up_legacy_mirrors(
    hass: HomeAssistant,
) -> None:
    """v0.9.1-style per-device mirror entries are removed on sync."""
    device_registry = dr.async_get(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="小度中枢",
        data=_entry_data(),
        options={CONF_DEVICES: {"legacy-key": {"light.ciwo": ["power"]}}},
    )
    entry.add_to_hass(hass)

    legacy = device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "legacy-key")},
        name="旧镜像设备",
        disabled_by=dr.DeviceEntryDisabler.INTEGRATION,
    )
    assert entry.entry_id in legacy.config_entries

    _sync_device_registry(hass, entry)

    assert (
        device_registry.async_get_device(identifiers={(DOMAIN, "legacy-key")})
        is None
    )
    hub = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert hub is not None


async def test_remove_config_entry_device(hass: HomeAssistant) -> None:
    """Hub-owned entries may be removed; foreign devices are rejected."""
    device_registry = dr.async_get(hass)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="小度中枢",
        data=_entry_data(),
        options={CONF_DEVICES: {"some-device-key": {"light.ciwo": ["power"]}}},
    )
    entry.add_to_hass(hass)
    await async_setup_entry(hass, entry)

    hub = device_registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    assert hub is not None

    # Removing the hub only clears the registry entry; config stays intact.
    assert await async_remove_config_entry_device(hass, entry, hub)
    assert entry.options.get(CONF_DEVICES) == {
        "some-device-key": {"light.ciwo": ["power"]}
    }

    # A device owned by another integration must not be removable here.
    underlying_entry = MockConfigEntry(domain="test", data={}, title="测试")
    underlying_entry.add_to_hass(hass)
    foreign = device_registry.async_get_or_create(
        config_entry_id=underlying_entry.entry_id,
        identifiers={("test", "ciwo_lamp")},
        name="次卧灯",
    )
    assert not await async_remove_config_entry_device(hass, entry, foreign)


async def _advance_past_debounce(hass: HomeAssistant) -> None:
    """Fire the debounced device-set refresh (2s) and let callbacks run."""
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=3))
    await hass.async_block_till_done()


async def test_entity_add_invalidates_device_cache_but_update_does_not(
    hass: HomeAssistant,
) -> None:
    """A new entity invalidates the cached device set; a state update does not."""
    entry = MockConfigEntry(domain=DOMAIN, data=_entry_data())
    entry.add_to_hass(hass)
    assert await async_setup_entry(hass, entry)

    sentinel = object()
    hass.data[DOMAIN][DATA_ENHANCED_DEVICES] = sentinel

    # Adding an entity (old_state None) schedules the debounced invalidation.
    hass.states.async_set("light.new_device", "on")
    await _advance_past_debounce(hass)
    assert DATA_ENHANCED_DEVICES not in hass.data[DOMAIN]

    # A pure state update must leave the cache untouched.
    hass.data[DOMAIN][DATA_ENHANCED_DEVICES] = sentinel
    hass.states.async_set("light.new_device", "off")
    await _advance_past_debounce(hass)
    assert hass.data[DOMAIN][DATA_ENHANCED_DEVICES] is sentinel

    # Removing an entity (new_state None) invalidates again.
    hass.states.async_remove("light.new_device")
    await _advance_past_debounce(hass)
    assert DATA_ENHANCED_DEVICES not in hass.data[DOMAIN]

    assert await async_unload_entry(hass, entry)


async def test_registry_change_invalidates_device_cache(
    hass: HomeAssistant,
) -> None:
    """Entity/device/area registry changes invalidate the cached device set."""
    entry = MockConfigEntry(domain=DOMAIN, data=_entry_data())
    entry.add_to_hass(hass)
    assert await async_setup_entry(hass, entry)

    hass.data[DOMAIN][DATA_ENHANCED_DEVICES] = object()

    ent_reg = er.async_get(hass)
    ent_reg.async_get_or_create(
        "light", "test_platform", "unique_1", config_entry=entry
    )
    await _advance_past_debounce(hass)
    assert DATA_ENHANCED_DEVICES not in hass.data[DOMAIN]

    assert await async_unload_entry(hass, entry)


async def test_unload_clears_cache_and_listeners(hass: HomeAssistant) -> None:
    """Unload drops the cache, unsubscribes listeners and cancels the debounce."""
    entry = MockConfigEntry(domain=DOMAIN, data=_entry_data())
    entry.add_to_hass(hass)
    assert await async_setup_entry(hass, entry)
    hass.data[DOMAIN][DATA_ENHANCED_DEVICES] = object()
    assert DATA_STRUCTURE_UNSUBS in hass.data[DOMAIN]

    assert await async_unload_entry(hass, entry)
    assert DATA_ENHANCED_DEVICES not in hass.data[DOMAIN]
    assert DATA_STRUCTURE_UNSUBS not in hass.data[DOMAIN]

    # After unload, entity changes no longer schedule a refresh.
    hass.states.async_set("light.after_unload", "on")
    await _advance_past_debounce(hass)
    assert DATA_STRUCTURE_REFRESH_HANDLE not in hass.data.get(DOMAIN, {})
