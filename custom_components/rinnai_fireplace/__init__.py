"""Custom integration to integrate rinnai_fireplace with Home Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import RinnaiFireplaceApiClient
from .const import CONF_IP
from .coordinator import RinnaiFireplaceDataUpdateCoordinator
from .data import RinnaiFireplaceData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import RinnaiFireplaceConfigEntry

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: RinnaiFireplaceConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = RinnaiFireplaceDataUpdateCoordinator(hass=hass, config_entry=entry)
    entry.runtime_data = RinnaiFireplaceData(
        client=RinnaiFireplaceApiClient(entry.data[CONF_IP]),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: RinnaiFireplaceConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: RinnaiFireplaceConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
