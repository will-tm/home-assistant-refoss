"""Config Flow for Refoss integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_CHANNELS,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_MAC,
    CONF_PORT,
    CONF_UUID,
    DEFAULT_CHANNELS,
    DEFAULT_DEVICE_NAME,
    DEFAULT_DEVICE_TYPE,
    DEFAULT_MAC,
    DEFAULT_PORT,
    DOMAIN,
    _LOGGER,
)
from .refoss_ha.device import DeviceInfo
from .refoss_ha.device_manager import async_build_base_device


class RefossConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Refoss."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            uuid = user_input[CONF_UUID]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
            device_type = user_input.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE)
            device_name = user_input.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)

            # Use UUID as unique ID to allow multiple devices
            await self.async_set_unique_id(uuid)
            self._abort_if_unique_id_configured()

            # Test connection to the device
            device_info = DeviceInfo(
                uuid=uuid,
                dev_name=device_name,
                device_type=device_type,
                dev_soft_ware="1.0.0",
                dev_hard_ware="1.0.0",
                ip=host,
                port=str(port),
                mac=DEFAULT_MAC,
                sub_type="us",
                channels=DEFAULT_CHANNELS,
            )

            try:
                device = await async_build_base_device(device_info)
                if device is None:
                    errors["base"] = "cannot_connect"
                else:
                    _LOGGER.info(
                        "Successfully connected to Refoss device at %s", host
                    )
                    return self.async_create_entry(
                        title=f"Refoss {device_name} ({host})",
                        data={
                            CONF_HOST: host,
                            CONF_UUID: uuid,
                            CONF_PORT: port,
                            CONF_DEVICE_TYPE: device_type,
                            CONF_DEVICE_NAME: device_name,
                            CONF_MAC: DEFAULT_MAC,
                            CONF_CHANNELS: DEFAULT_CHANNELS,
                        },
                    )
            except Exception as ex:
                _LOGGER.exception("Error connecting to device: %s", ex)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_UUID): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(
                    CONF_DEVICE_TYPE, default=DEFAULT_DEVICE_TYPE
                ): cv.string,
                vol.Optional(
                    CONF_DEVICE_NAME, default=DEFAULT_DEVICE_NAME
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(
        self, import_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle import from YAML configuration."""
        uuid = import_data[CONF_UUID]
        host = import_data[CONF_HOST]
        device_name = import_data.get(CONF_DEVICE_NAME, DEFAULT_DEVICE_NAME)

        # Use UUID as unique ID
        await self.async_set_unique_id(uuid)
        self._abort_if_unique_id_configured()

        _LOGGER.info(
            "Importing Refoss device from YAML: %s at %s", device_name, host
        )

        return self.async_create_entry(
            title=f"Refoss {device_name} ({host})",
            data={
                CONF_HOST: host,
                CONF_UUID: uuid,
                CONF_PORT: import_data.get(CONF_PORT, DEFAULT_PORT),
                CONF_DEVICE_TYPE: import_data.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE),
                CONF_DEVICE_NAME: device_name,
                CONF_MAC: import_data.get(CONF_MAC, DEFAULT_MAC),
                CONF_CHANNELS: import_data.get(CONF_CHANNELS, DEFAULT_CHANNELS),
            },
        )
