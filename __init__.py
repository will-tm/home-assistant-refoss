"""Refoss devices platform loader - HTTP only, no UDP discovery."""

from __future__ import annotations

from typing import Final

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_CHANNELS,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_MAC,
    CONF_PORT,
    CONF_UUID,
    COORDINATORS,
    DEFAULT_CHANNELS,
    DEFAULT_DEVICE_NAME,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_MAC,
    DEFAULT_PORT,
    DOMAIN,
    _LOGGER,
)
from .coordinator import RefossDataUpdateCoordinator
from .refoss_ha.device import DeviceInfo
from .refoss_ha.device_manager import async_build_base_device

PLATFORMS: Final = [
    Platform.SENSOR,
    Platform.SWITCH,
]

# Schema for a single device in YAML configuration
DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_UUID): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_DEVICE_TYPE, default=DEFAULT_DEVICE_TYPE): cv.string,
        vol.Optional(CONF_DEVICE_NAME, default=DEFAULT_DEVICE_NAME): cv.string,
        vol.Optional(CONF_MAC, default=DEFAULT_MAC): cv.string,
        vol.Optional(CONF_CHANNELS, default=DEFAULT_CHANNELS): cv.string,
    }
)

# Schema for YAML configuration - supports list of devices
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(cv.ensure_list, [DEVICE_SCHEMA]),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Refoss from YAML configuration."""
    if DOMAIN not in config:
        return True

    for device_config in config[DOMAIN]:
        # Check if this device is already configured
        existing_entries = [
            entry
            for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.data.get(CONF_UUID) == device_config[CONF_UUID]
        ]

        if existing_entries:
            _LOGGER.debug(
                "Device with UUID %s already configured, skipping YAML import",
                device_config[CONF_UUID],
            )
            continue

        _LOGGER.info(
            "Importing Refoss device from YAML: %s at %s",
            device_config.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME),
            device_config[CONF_HOST],
        )

        # Create a config entry from YAML configuration
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=device_config,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Refoss from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(COORDINATORS, {})

    # Migration: Handle old config entries with empty data
    # Fall back to original hardcoded values for backwards compatibility
    if CONF_HOST not in entry.data or not entry.data.get(CONF_HOST):
        _LOGGER.warning(
            "Config entry has no host configured (legacy entry). "
            "Please delete and reconfigure the integration, or add YAML configuration."
        )
        # Return False to mark entry as failed - user needs to reconfigure
        return False

    # Read configuration from entry data
    host = entry.data[CONF_HOST]
    uuid = entry.data[CONF_UUID]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    device_type = entry.data.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE)
    device_name = entry.data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)
    mac = entry.data.get(CONF_MAC, DEFAULT_MAC)
    channels = entry.data.get(CONF_CHANNELS, DEFAULT_CHANNELS)

    _LOGGER.info(
        "Initializing Refoss %s device at %s (HTTP only, no UDP discovery)",
        device_name,
        host,
    )

    # Create DeviceInfo from config entry data
    device_info = DeviceInfo(
        uuid=uuid,
        dev_name=device_name,
        device_type=device_type,
        dev_soft_ware="1.0.0",
        dev_hard_ware="1.0.0",
        ip=host,
        port=str(port),
        mac=mac,
        sub_type="us",
        channels=channels,
    )

    _LOGGER.debug(
        "Created DeviceInfo: uuid=%s, type=%s, ip=%s",
        device_info.uuid,
        device_info.device_type,
        device_info.inner_ip,
    )

    # Build the device using config info (queries device abilities via HTTP)
    device = await async_build_base_device(device_info)
    if device is None:
        _LOGGER.warning(
            "Failed to communicate with device at %s via HTTP - will retry",
            host,
        )
        raise ConfigEntryNotReady(f"Device at {host} not responding to HTTP")

    coordinator = RefossDataUpdateCoordinator(hass, entry, device)
    hass.data[DOMAIN][COORDINATORS][entry.entry_id] = coordinator
    await coordinator.async_refresh()

    _LOGGER.info(
        "Device initialized successfully via HTTP: %s at %s",
        device_info.dev_name,
        device_info.inner_ip,
    )

    # Set up platforms AFTER device and coordinator are ready
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN][COORDINATORS].pop(entry.entry_id, None)

    return unload_ok
