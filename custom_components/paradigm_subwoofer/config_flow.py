"""Config flow for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .bluetooth import get_device_name, is_paradigm_subwoofer
from .const import CONF_MAC_ADDRESS, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_MAC_ADDRESS): cv.string,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Paradigm Subwoofer Control."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_device_name: str | None = None
        self._discovered_mac: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the Bluetooth discovery step."""
        _LOGGER.debug("Discovered Paradigm device: %s", discovery_info)

        if not is_paradigm_subwoofer(discovery_info):
            return self.async_abort(reason="not_supported")

        mac_address = discovery_info.address
        await self.async_set_unique_id(mac_address)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self._discovered_device_name = get_device_name(discovery_info)
        self._discovered_mac = mac_address

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm discovery."""
        assert self._discovery_info is not None
        assert self._discovered_device_name is not None
        assert self._discovered_mac is not None

        if user_input is not None:
            return self.async_create_entry(
                title=self._discovered_device_name,
                data={
                    CONF_NAME: self._discovered_device_name,
                    CONF_MAC_ADDRESS: self._discovered_mac,
                },
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={
                "name": self._discovered_device_name,
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step (manual setup)."""
        errors: dict[str, str] = {}

        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS].upper().replace("-", ":")

            await self.async_set_unique_id(mac_address)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_MAC_ADDRESS: mac_address,
                },
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
