"""RinnaiFireplaceEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_IP, MANUFACTURER
from .coordinator import RinnaiFireplaceDataUpdateCoordinator


class RinnaiFireplaceEntity(CoordinatorEntity[RinnaiFireplaceDataUpdateCoordinator]):
    """RinnaiFireplaceEntity class."""

    coordinator: RinnaiFireplaceDataUpdateCoordinator

    def __init__(self, coordinator: RinnaiFireplaceDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self.coordinator = coordinator

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (
                    self.coordinator.config_entry.domain,
                    self.coordinator.config_entry.entry_id,
                ),
            },
            configuration_url=f"http://{self.coordinator.config_entry.data[CONF_IP]}:3000",
            manufacturer=MANUFACTURER,
            name=self.coordinator.device_name,
            sw_version=self.coordinator.sw_version,
        )
