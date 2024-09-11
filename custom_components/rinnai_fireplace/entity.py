"""RinnaiFireplaceEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import MANUFACTURER
from .coordinator import RinnaiFireplaceDataUpdateCoordinator


class RinnaiFireplaceEntity(CoordinatorEntity[RinnaiFireplaceDataUpdateCoordinator]):
    """RinnaiFireplaceEntity class."""

    coordinator: RinnaiFireplaceDataUpdateCoordinator

    def __init__(self, coordinator: RinnaiFireplaceDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self.coordinator = coordinator
        print(self._attr_device_info)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={
                (
                    self.coordinator.config_entry.domain,
                    self.coordinator.device_name
                    or self.coordinator.config_entry.entry_id,
                ),
            },
            manufacturer=MANUFACTURER,
            name=self.coordinator.device_name,
            sw_version=self.coordinator.sw_version,
        )
