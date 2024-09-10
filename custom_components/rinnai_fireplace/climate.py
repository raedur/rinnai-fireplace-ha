"""Climate platform for rinnai_fireplace."""

from __future__ import annotations

import asyncio
from enum import Enum
from typing import TYPE_CHECKING, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
)
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.exceptions import IntegrationError

from .api import Eco, OperationalMode, OperationalState
from .entity import RinnaiFireplaceEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import RinnaiFireplaceDataUpdateCoordinator
    from .data import RinnaiFireplaceConfigEntry

ENTITY_DESCRIPTIONS = (
    ClimateEntityDescription(
        key="rinnai_fireplace",
        name="Rinnai Fireplace Climate",
        icon="mdi:fire-circle",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: RinnaiFireplaceConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    async_add_entities(
        RinnaiFireplaceClimate(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class Presets(Enum):
    """The supported presets."""

    ECO = "Economy"
    NORMAL = "Normal"


class RinnaiFireplaceClimate(RinnaiFireplaceEntity, ClimateEntity):
    """rinnai_fireplace climate class."""

    def __init__(
        self,
        coordinator: RinnaiFireplaceDataUpdateCoordinator,
        entity_description: ClimateEntityDescription,
    ) -> None:
        """Initialize the climate class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._enable_turn_on_off_backwards_compatibility = False
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF, HVACMode.FAN_ONLY]
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_preset_modes = Presets._member_names_
        self._attr_target_temperature_step = 1
        self._attr_fan_modes = [
            f"{i}" for i in range(self.MIN_FAN_MODE, self.MAX_FAN_MODE + 1)
        ]

    MIN_FAN_MODE = 0
    MAX_FAN_MODE = 5

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.room_temp

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        return self.coordinator.data.set_temp

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        match self.coordinator.data.operation_mode:
            case OperationalMode.FLAME:
                return HVACMode.FAN_ONLY
            case OperationalMode.TEMP:
                return HVACMode.HEAT

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode, e.g., home, away, temp."""
        match self.coordinator.data.economy:
            case Eco.ON:
                return "ECO"
            case Eco.OFF:
                return "NORMAL"

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        return str(self.coordinator.data.flame_level)

    async def async_turn_off(self) -> None:
        """Turn off device."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_turn_on(self) -> None:
        """Turn on device."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        mode = None
        match hvac_mode:
            case HVACMode.OFF:
                mode = OperationalState.STANDBY
            case HVACMode.HEAT:
                mode = OperationalState.ON
            case _:
                msg = f"Unsupported HVACMode: {hvac_mode}"
                raise IntegrationError(msg)

        await self.coordinator.config_entry.runtime_data.client.async_set_op_state(
            state=mode
        )
        # sleep for one second as otherwise we get empty packets
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        try:
            fan_mode_int = int(fan_mode)
        except ValueError as ve:
            msg = f"Unsupported fan_mode: {fan_mode}"
            raise IntegrationError(msg) from ve
        if fan_mode_int < self.MIN_FAN_MODE or fan_mode_int > self.MAX_FAN_MODE:
            msg = f"Unsupported fan_mode: {fan_mode}"
            raise IntegrationError(msg)

        await self.coordinator.config_entry.runtime_data.client.async_set_flame_level(
            flame_level=fan_mode_int
        )
        # sleep for one second as otherwise we get empty packets
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: dict[str, Any]) -> None:
        """Set new target temperature."""
        if temperature := kwargs.get(ATTR_TEMPERATURE) is None:
            msg = "Temperature arg missing"
            raise IntegrationError(msg)
        if temperature is not int:
            msg = f"Temperature not int, got: {temperature}"
            raise IntegrationError(msg)
        await self.coordinator.config_entry.runtime_data.client.async_set_target_temp(
            temp=int(temperature)
        )
        # sleep for one second as otherwise we get empty packets
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        try:
            preset = Presets[preset_mode]
        except ValueError as ve:
            msg = f"Unsupported preset: {preset_mode}"
            raise IntegrationError(msg) from ve

        match preset:
            case Presets.ECO:
                eco = Eco.ON
            case Presets.NORMAL:
                eco = Eco.OFF

        await self.coordinator.config_entry.runtime_data.client.async_set_eco(eco=eco)
        # sleep for one second as otherwise we get empty packets
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()
