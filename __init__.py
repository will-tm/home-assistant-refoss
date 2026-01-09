"""Refoss devices platform loader - Hardcoded device configuration (HTTP only, no UDP)."""

from __future__ import annotations

from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import _LOGGER, COORDINATORS, DOMAIN
from .coordinator import RefossDataUpdateCoordinator

# Import from local vendored refoss_ha library (no UDP discovery)
from .refoss_ha.device import DeviceInfo
from .refoss_ha.device_manager import async_build_base_device

PLATFORMS: Final = [
    Platform.SENSOR,
    Platform.SWITCH,
]

# Hardcoded EM16 device configuration (from discovery response)
DEVICE_UUID = "25091775826352740701c4e7ae21055a"
DEVICE_NAME = "em16"
DEVICE_TYPE = "em16"
DEVICE_FIRMWARE = "3.1.11"
DEVICE_HARDWARE = "3.0.0"
DEVICE_IP = "10.0.101.60"
DEVICE_PORT = "80"
DEVICE_MAC = "c4:e7:ae:21:05:5a"
DEVICE_SUBTYPE = "us"
DEVICE_CHANNELS = "[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Refoss from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(COORDINATORS, [])

    _LOGGER.info(
        "Initializing Refoss EM16 device at %s (HTTP only, no UDP discovery)",
        DEVICE_IP,
    )

    # Create DeviceInfo directly with hardcoded values (no UDP discovery needed)
    device_info = DeviceInfo(
        uuid=DEVICE_UUID,
        dev_name=DEVICE_NAME,
        device_type=DEVICE_TYPE,
        dev_soft_ware=DEVICE_FIRMWARE,
        dev_hard_ware=DEVICE_HARDWARE,
        ip=DEVICE_IP,
        port=DEVICE_PORT,
        mac=DEVICE_MAC,
        sub_type=DEVICE_SUBTYPE,
        channels=DEVICE_CHANNELS,
    )

    _LOGGER.debug(
        "Created DeviceInfo: uuid=%s, type=%s, ip=%s",
        device_info.uuid,
        device_info.device_type,
        device_info.inner_ip,
    )

    # Build the device using hardcoded info (queries device abilities via HTTP)
    device = await async_build_base_device(device_info)
    if device is None:
        _LOGGER.warning(
            "Failed to communicate with device at %s via HTTP - will retry",
            DEVICE_IP,
        )
        raise ConfigEntryNotReady(f"Device at {DEVICE_IP} not responding to HTTP")

    coordinator = RefossDataUpdateCoordinator(hass, entry, device)
    hass.data[DOMAIN][COORDINATORS].append(coordinator)
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
        hass.data[DOMAIN].pop(COORDINATORS, None)

    return unload_ok
