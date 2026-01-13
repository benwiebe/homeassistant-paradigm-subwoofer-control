"""Number platform for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import ParadigmSubwooferClient
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

    client = ParadigmSubwooferClient(mac_address)

    async_add_entities(
        [
            ParadigmSubwooferVolume(name, mac_address, config_entry.entry_id, client),
            ParadigmSubwooferTrim(name, mac_address, config_entry.entry_id, client),
            ParadigmSubwooferLowPassFilter(name, mac_address, config_entry.entry_id, client),
        ],
        True,
    )


class ParadigmSubwooferNumberBase(NumberEntity):
    """Base class for Paradigm Subwoofer number entities."""

    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        number_type: str,
        client: ParadigmSubwooferClient,
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
        self._client = client


class ParadigmSubwooferVolume(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer volume control."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:volume-high"

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        client: ParadigmSubwooferClient,
    ) -> None:
        """Initialize the volume control."""
        super().__init__(name, mac_address, entry_id, "volume", client)
        self._attr_name = f"{name} Volume"

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume level."""
        try:
            success = await self._client.set_volume(int(value))
            if success:
                self._attr_native_value = value
            else:
                _LOGGER.warning("Failed to set volume to %s", value)
        except Exception as ex:
            _LOGGER.error("Error setting volume: %s", ex)
            raise

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            volume = await self._client.get_volume()
            if volume is not None:
                self._attr_native_value = volume
        except Exception as ex:
            _LOGGER.debug("Error updating volume: %s", ex)


class ParadigmSubwooferTrim(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer trim control."""

    _attr_native_min_value = -12
    _attr_native_max_value = 12
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "dB"
    _attr_icon = "mdi:tune"

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        client: ParadigmSubwooferClient,
    ) -> None:
        """Initialize the trim control."""
        super().__init__(name, mac_address, entry_id, "trim", client)
        self._attr_name = f"{name} Trim"

    async def async_set_native_value(self, value: float) -> None:
        """Set the trim level."""
        try:
            success = await self._client.set_trim(int(value))
            if success:
                self._attr_native_value = value
            else:
                _LOGGER.warning("Failed to set trim to %s", value)
        except Exception as ex:
            _LOGGER.error("Error setting trim: %s", ex)
            raise

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            trim = await self._client.get_trim()
            if trim is not None:
                self._attr_native_value = trim
        except Exception as ex:
            _LOGGER.debug("Error updating trim: %s", ex)


class ParadigmSubwooferLowPassFilter(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer low pass filter control."""

    _attr_native_min_value = 40
    _attr_native_max_value = 200
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "Hz"
    _attr_icon = "mdi:sine-wave"

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        client: ParadigmSubwooferClient,
    ) -> None:
        """Initialize the low pass filter control."""
        super().__init__(name, mac_address, entry_id, "low_pass_filter", client)
        self._attr_name = f"{name} Low Pass Filter"

    async def async_set_native_value(self, value: float) -> None:
        """Set the low pass filter frequency."""
        try:
            success = await self._client.set_low_pass_filter(int(value))
            if success:
                self._attr_native_value = value
            else:
                _LOGGER.warning("Failed to set low pass filter to %s Hz", value)
        except Exception as ex:
            _LOGGER.error("Error setting low pass filter: %s", ex)
            raise

    async def async_update(self) -> None:
        """Update the current value."""
        try:
            lpf = await self._client.get_low_pass_filter()
            if lpf is not None:
                self._attr_native_value = lpf
        except Exception as ex:
            _LOGGER.debug("Error updating low pass filter: %s", ex)
