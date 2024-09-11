"""RinnaiFireplace API Client."""

from __future__ import annotations

import re
import socket
from enum import Enum
from typing import Any

from attr import dataclass

from .const import LOGGER


class RinnaiFireplaceApiClientError(Exception):
    """Exception to indicate a general API error."""


class RinnaiFireplaceApiClientProtocolError(
    RinnaiFireplaceApiClientError,
):
    """Exception to indicate a protocol error."""


class RinnaiFireplaceApiClientCommunicationError(
    RinnaiFireplaceApiClientError,
):
    """Exception to indicate a communication error."""


class Eco(Enum):
    """Economy setting of the device."""

    OFF = "00"
    ON = "01"


def parse_eco(mode: int) -> Eco:
    """Parse the Eco."""
    try:
        return Eco(f"{mode:0>2X}")
    except ValueError as ve:
        msg = f"Unknown Eco value: {mode}"
        raise RinnaiFireplaceApiClientCommunicationError(msg) from ve


class OperationalState(Enum):
    """OperationalState of the device."""

    STANDBY = "00"
    ON = "01"


def parse_operational_state(state: int) -> OperationalState:
    """Parse the OperationalState."""
    try:
        return OperationalState(f"{state:0>2X}")
    except ValueError as ve:
        msg = f"Unknown OperationalState value: {state}"
        raise RinnaiFireplaceApiClientCommunicationError(msg) from ve


class OperationalMode(Enum):
    """OperationalMode of the device."""

    STANDBY = "00"
    FLAME = "01"
    """Fixed flame level mode."""
    TEMP = "02"
    """Target temperature mode."""


def parse_operational_mode(mode: int) -> OperationalMode:
    """Parse the OperationalMode."""
    try:
        return OperationalMode(f"{mode:0>2X}")
    except ValueError as ve:
        msg = f"Unknown OperationalMode value: {mode}"
        raise RinnaiFireplaceApiClientCommunicationError(msg) from ve


@dataclass
class RinnaiFireplaceStatus:
    """The status of the device."""

    main_power_switch: int
    operation_state: OperationalState
    error_code: int
    operation_mode: OperationalMode
    burning_state: int
    flame_level: int
    """Flame level, values are between 1 and 5 inclusive"""
    economy: Eco
    lighting: int
    room_temp: int
    set_temp: int
    burn_speed_info: int
    lighting_info: int
    timer_active: int
    wifi_strength: int


class RinnaiFireplaceApiClient:
    """RinnaiFireplace Api Client."""

    PORT = 3000

    def __init__(
        self,
        host: str,
    ) -> None:
        """Initialize API Client."""
        self._host = host

    async def async_get_name(self) -> str:
        """Get data from the API."""
        data = self._api_wrapper(self._host, "RINNAI_27,E")
        pattern = r"RINNAI_27,([^,]*)"
        result = re.search(pattern, data)
        if result is None:
            msg = f"Cannot parse name from payload: {data}"
            raise RinnaiFireplaceApiClientError(msg)
        return result.group(1)

    async def async_get_version(self) -> str:
        """Get version from the API."""
        data = self._api_wrapper(self._host, "RINNAI_10,E")
        pattern = r"RINNAI_10,([^,]*)"
        result = re.search(pattern, data)
        if result is None:
            msg = f"Cannot parse version from payload: {data}"
            raise RinnaiFireplaceApiClientError(msg)
        return result.group(1)

    async def async_set_eco(self, eco: Eco) -> None:
        """Set economy mode."""
        self._api_wrapper(self._host, f"RINNAI_35,{eco.value},E")

    async def async_set_op_state(self, state: OperationalState) -> None:
        """Set operational state."""
        self._api_wrapper(self._host, f"RINNAI_34,{state.value},E")

    async def async_set_target_temp(self, temp: int) -> None:
        """Set target temperature."""
        self._api_wrapper(self._host, f"RINNAI_33,{temp:0>2X},E")

    async def async_set_flame_level(self, flame_level: int) -> None:
        """Set flame level."""
        self._api_wrapper(self._host, f"RINNAI_32,{flame_level:0>2X},E")

    async def async_get_status(self) -> RinnaiFireplaceStatus | None:
        """Get data from the API."""
        data = self._api_wrapper(self._host, "RINNAI_22,E")
        pattern = r"RINNAI_22,(.*),E"
        result = re.search(pattern, data)
        if result is None:
            # Sometimes we get empty payloads :(
            return None
        data = result.group(1).split(",")
        main_power_switch = int(data[0], 16)
        operation_state = parse_operational_state(int(data[1], 16))
        error_code = int(f"{data[2]}{data[3]}", 16)
        operation_mode = parse_operational_mode(int(data[4], 16))
        burning_state = int(data[5], 16)
        flame_level = int(data[6], 16)
        economy = parse_eco(int(data[7], 16))
        lighting = int(data[8], 16)
        room_temp = int(data[9], 16)
        set_temp = int(data[10], 16)
        burn_speed_info = int(data[11], 16)
        lighting_info = int(data[12], 16)
        timer_active = int(data[13], 16)
        wifi_strength = int(data[14], 16)
        return RinnaiFireplaceStatus(
            main_power_switch=main_power_switch,
            operation_state=operation_state,
            error_code=error_code,
            operation_mode=operation_mode,
            burning_state=burning_state,
            flame_level=flame_level,
            economy=economy,
            lighting=lighting,
            room_temp=room_temp,
            set_temp=set_temp,
            burn_speed_info=burn_speed_info,
            lighting_info=lighting_info,
            timer_active=timer_active,
            wifi_strength=wifi_strength,
        )

    def _api_wrapper(
        self,
        host: str,
        payload: str,
    ) -> Any:
        """Send request to the Deivce."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((host, self.PORT))
                LOGGER.debug("Sending: %s", payload.encode("ascii"))
                s.sendall(payload.encode("ascii"))
                data = s.recv(1024)
                LOGGER.debug("Received: %s", repr(data))
                return data.decode()
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Error calling api - {exception}"
            raise RinnaiFireplaceApiClientError(
                msg,
            ) from exception
