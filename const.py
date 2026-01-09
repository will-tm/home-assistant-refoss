"""const."""

from __future__ import annotations

from logging import Logger, getLogger

_LOGGER: Logger = getLogger(__package__)

COORDINATORS = "coordinators"
DISPATCH_DEVICE_DISCOVERED = "refoss_device_discovered"

DOMAIN = "refoss"

MAX_ERRORS = 2

# Configuration keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_UUID = "uuid"
CONF_DEVICE_NAME = "device_name"
CONF_DEVICE_TYPE = "device_type"
CONF_MAC = "mac"
CONF_CHANNELS = "channels"

# Default values
DEFAULT_PORT = 80
DEFAULT_DEVICE_TYPE = "em16"
DEFAULT_DEVICE_NAME = "em16"
DEFAULT_MAC = "00:00:00:00:00:00"
DEFAULT_CHANNELS = "[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]"

# Energy monitoring
SENSOR_EM = "em"

CHANNEL_DISPLAY_NAME: dict[str, dict[int, str]] = {
    "em06": {
        1: "A1",
        2: "B1",
        3: "C1",
        4: "A2",
        5: "B2",
        6: "C2",
    },
    "em16": {
        1: "A1",
        2: "A2",
        3: "A3",
        4: "A4",
        5: "A5",
        6: "A6",
        7: "B1",
        8: "B2",
        9: "B3",
        10: "B4",
        11: "B5",
        12: "B6",
        13: "C1",
        14: "C2",
        15: "C3",
        16: "C4",
        17: "C5",
        18: "C6",
    },
}
