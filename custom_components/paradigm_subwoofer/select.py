"""Select platform for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging
from typing import Any

from bleak import BleakClient, BleakError

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MAC_ADDRESS, DOMAIN, PROFILES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Paradigm Subwoofer select platform."""
    name = config_entry.data[CONF_NAME]
    mac_address = config_entry.data[CONF_MAC_ADDRESS]

    async_add_entities(
        [ParadigmSubwooferProfile(name, mac_address, config_entry.entry_id)],
        True,
    )


class ParadigmSubwooferProfile(SelectEntity):
    """Representation of Paradigm Subwoofer profile selection."""

    _attr_icon = "mdi:tune-variant"

    def __init__(self, name: str, mac_address: str, entry_id: str) -> None:
        """Initialize the profile selector."""
        self._base_name = name
        self._mac_address = mac_address
        self._attr_name = f"{name} Profile"
        self._attr_unique_id = f"{mac_address}_profile"
        self._attr_options = PROFILES
        self._attr_current_option = PROFILES[0]  # Default to movie
        self._attr_device_info = {
            "identifiers": {(DOMAIN, mac_address)},
            "name": name,
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }
        self._client: BleakClient | None = None

    async def _get_client(self) -> BleakClient:
        """Get or create a connected BLE client."""
        if self._client is None or not self._client.is_connected:
            self._client = BleakClient(self._mac_address)
            await self._client.connect()
        return self._client

    async def _disconnect_client(self) -> None:
        """Disconnect the BLE client."""
        if self._client and self._client.is_connected:
            try:
                await self._client.disconnect()
            except Exception as ex:
                _LOGGER.debug("Error disconnecting: %s", ex)
            self._client = None

    async def async_select_option(self, option: str) -> None:
        """Change the selected profile."""
        if option not in PROFILES:
            _LOGGER.error("Invalid profile: %s", option)
            return

        try:
            client = await self._get_client()
            # TODO: Send profile selection command via Bluetooth
            # Example:
            # profile_map = {"movie": 0, "music": 1, "night": 2}
            # await client.write_gatt_char(PROFILE_CHARACTERISTIC_UUID, bytes([profile_map[option]]))
            self._attr_current_option = option
            _LOGGER.debug("Set profile to %s", option)
        except (BleakError, Exception) as ex:
            _LOGGER.error("Error setting profile: %s", ex)
            await self._disconnect_client()
            raise

    async def async_update(self) -> None:
        """Update the current profile."""
        try:
            client = await self._get_client()
            # TODO: Read current profile from Bluetooth
            # Example:
            # data = await client.read_gatt_char(PROFILE_CHARACTERISTIC_UUID)
            # profile_map = {0: "movie", 1: "music", 2: "night"}
            # self._attr_current_option = profile_map.get(int(data[0]), "movie")
            pass
        except (BleakError, Exception) as ex:
            _LOGGER.debug("Error updating profile: %s", ex)
            await self._disconnect_client()
