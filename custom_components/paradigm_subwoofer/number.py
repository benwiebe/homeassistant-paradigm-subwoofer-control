"""Number platform for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging
from typing import Any

from bleak import BleakClient, BleakError

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MAC_ADDRESS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Paradigm Subwoofer number platform."""
    name = config_entry.data[CONF_NAME]
    mac_address = config_entry.data[CONF_MAC_ADDRESS]

    async_add_entities(
        [
            ParadigmSubwooferVolume(name, mac_address, config_entry.entry_id),
            ParadigmSubwooferTrim(name, mac_address, config_entry.entry_id),
        ],
        True,
    )


class ParadigmSubwooferNumberBase(NumberEntity):
    """Base class for Paradigm Subwoofer number entities."""

    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, name: str, mac_address: str, entry_id: str, number_type: str
    ) -> None:
        """Initialize the number entity."""
        self._base_name = name
        self._mac_address = mac_address
        self._number_type = number_type
        self._attr_unique_id = f"{mac_address}_{number_type}"
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


class ParadigmSubwooferVolume(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer volume control."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:volume-high"

    def __init__(self, name: str, mac_address: str, entry_id: str) -> None:
        """Initialize the volume control."""
        super().__init__(name, mac_address, entry_id, "volume")
        self._attr_name = f"{name} Volume"
        self._attr_native_value = 50

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume level."""
        try:
            client = await self._get_client()
            # TODO: Send volume command via Bluetooth
            # Example: await client.write_gatt_char(VOLUME_CHARACTERISTIC_UUID, bytes([int(value)]))
            self._attr_native_value = value
            _LOGGER.debug("Set volume to %s%%", value)
        except (BleakError, Exception) as ex:
            _LOGGER.error("Error setting volume: %s", ex)
            await self._disconnect_client()
            raise

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            client = await self._get_client()
            # TODO: Read current volume from Bluetooth
            # Example: data = await client.read_gatt_char(VOLUME_CHARACTERISTIC_UUID)
            # self._attr_native_value = int(data[0])
            pass
        except (BleakError, Exception) as ex:
            _LOGGER.debug("Error updating volume: %s", ex)
            await self._disconnect_client()


class ParadigmSubwooferTrim(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer trim control."""

    _attr_native_min_value = -12
    _attr_native_max_value = 12
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "dB"
    _attr_icon = "mdi:tune"

    def __init__(self, name: str, mac_address: str, entry_id: str) -> None:
        """Initialize the trim control."""
        super().__init__(name, mac_address, entry_id, "trim")
        self._attr_name = f"{name} Trim"
        self._attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Set the trim level."""
        try:
            client = await self._get_client()
            # TODO: Send trim command via Bluetooth
            # Example: await client.write_gatt_char(TRIM_CHARACTERISTIC_UUID, struct.pack('f', value))
            self._attr_native_value = value
            _LOGGER.debug("Set trim to %s dB", value)
        except (BleakError, Exception) as ex:
            _LOGGER.error("Error setting trim: %s", ex)
            await self._disconnect_client()
            raise

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            client = await self._get_client()
            # TODO: Read current trim from Bluetooth
            # Example: data = await client.read_gatt_char(TRIM_CHARACTERISTIC_UUID)
            # self._attr_native_value = struct.unpack('f', data)[0]
            pass
        except (BleakError, Exception) as ex:
            _LOGGER.debug("Error updating trim: %s", ex)
            await self._disconnect_client()
