"""Custom types for rinnai_fireplace."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import RinnaiFireplaceApiClient
    from .coordinator import RinnaiFireplaceDataUpdateCoordinator


type RinnaiFireplaceConfigEntry = ConfigEntry[RinnaiFireplaceData]


@dataclass
class RinnaiFireplaceData:
    """Data for the RinnaiFireplace integration."""

    client: RinnaiFireplaceApiClient
    coordinator: RinnaiFireplaceDataUpdateCoordinator
    integration: Integration
