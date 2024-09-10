"""Constants for rinnai_fireplace."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "rinnai_fireplace"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
CORE_DEVICE_NAME = "Rinnai Fireplace: {name}"
