"""DataUpdateCoordinator for rinnai_fireplace."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    RinnaiFireplaceApiClientError,
    RinnaiFireplaceStatus,
)
from .const import DOMAIN, LOGGER, CONF_DEVICE_NAME

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import RinnaiFireplaceConfigEntry


class RinnaiFireplaceDataUpdateCoordinator(
    DataUpdateCoordinator[RinnaiFireplaceStatus]
):
    """Class to manage fetching data from the device."""

    config_entry: RinnaiFireplaceConfigEntry
    device_name: str | None
    sw_version: str | None

    def __init__(
        self, hass: HomeAssistant, config_entry: RinnaiFireplaceConfigEntry
    ) -> None:
        """Initialize."""
        self.config_entry = config_entry
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=15),
        )
        self.device_name = None
        self.sw_version = None

    async def _async_setup(self) -> None:
        """Do initialization logic."""
        self.device_name = await self.config_entry.runtime_data.client.async_get_name()
        self.sw_version = (
            await self.config_entry.runtime_data.client.async_get_version()
        )

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_status()
        except RinnaiFireplaceApiClientError as exception:
            raise UpdateFailed(exception) from exception
