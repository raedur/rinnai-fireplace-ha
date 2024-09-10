"""Constants for rinnai_fireplace."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "rinnai_fireplace"
CORE_DEVICE_NAME = "Rinnai Fireplace: {name}"
CONF_IP = "ip"
CONF_ID = "id"
CONF_DEVICE_NAME = "device_name"
ATTR_DEVICE_NAME = "device_name"
ATTR_DEVICE_ID = "device_id"
ATTR_DEVICE_IP = "device_ip"
MANUFACTURER = "Rinnai"
