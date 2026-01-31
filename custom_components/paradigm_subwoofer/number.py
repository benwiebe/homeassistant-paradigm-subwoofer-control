"""Number platform for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ParadigmSubwooferCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Paradigm Subwoofer number platform."""
    coordinator: ParadigmSubwooferCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            ParadigmSubwooferVolume(coordinator),
            ParadigmSubwooferTrim(coordinator),
            ParadigmSubwooferLowPassFilter(coordinator),
        ],
    )


class ParadigmSubwooferNumberBase(CoordinatorEntity, NumberEntity):
    """Base class for Paradigm Subwoofer number entities."""

    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: ParadigmSubwooferCoordinator,
        number_type: str,
        name_suffix: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._number_type = number_type
        self._attr_unique_id = f"{coordinator.client._mac_address}_{number_type}"
        self._attr_name = name_suffix
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.client._mac_address)},
            "name": "Paradigm Subwoofer",
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Always available - the device might be on even if we don't have recent data
        # Setting values will trigger a connection attempt
        return True


class ParadigmSubwooferVolume(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer volume control."""

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:volume-high"

    def __init__(self, coordinator: ParadigmSubwooferCoordinator) -> None:
        """Initialize the volume control."""
        super().__init__(coordinator, "volume", "Volume")

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("volume")

    async def async_set_native_value(self, value: float) -> None:
        """Set the volume level."""
        await self.coordinator.async_send_command(
            self.coordinator.client.set_volume, int(value)
        )


class ParadigmSubwooferTrim(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer trim control."""

    _attr_native_min_value = -12
    _attr_native_max_value = 12
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "dB"
    _attr_icon = "mdi:tune"

    def __init__(self, coordinator: ParadigmSubwooferCoordinator) -> None:
        """Initialize the trim control."""
        super().__init__(coordinator, "trim", "Trim")

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("trim")

    async def async_set_native_value(self, value: float) -> None:
        """Set the trim level."""
        await self.coordinator.async_send_command(
            self.coordinator.client.set_trim, int(value)
        )


class ParadigmSubwooferLowPassFilter(ParadigmSubwooferNumberBase):
    """Representation of Paradigm Subwoofer low pass filter control."""

    _attr_native_min_value = 40
    _attr_native_max_value = 200
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "Hz"
    _attr_icon = "mdi:sine-wave"

    def __init__(self, coordinator: ParadigmSubwooferCoordinator) -> None:
        """Initialize the low pass filter control."""
        super().__init__(coordinator, "low_pass_filter", "Low Pass Filter")

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("low_pass_filter")

    async def async_set_native_value(self, value: float) -> None:
        """Set the low pass filter frequency."""
        await self.coordinator.async_send_command(
            self.coordinator.client.set_low_pass_filter, int(value)
        )
