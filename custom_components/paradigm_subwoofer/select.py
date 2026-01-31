"""Select platform for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PROFILE_TO_LMD, PROFILES
from .coordinator import ParadigmSubwooferCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Paradigm Subwoofer select platform."""
    coordinator: ParadigmSubwooferCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            ParadigmSubwooferProfile(coordinator),
            ParadigmSubwooferPhase(coordinator),
            ParadigmSubwooferPolarity(coordinator),
        ],
    )


class ParadigmSubwooferSelectBase(CoordinatorEntity, SelectEntity):
    """Base class for Paradigm Subwoofer select entities."""

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Always available - the device might be on even if we don't have recent data
        # Setting values will trigger a connection attempt
        return True


class ParadigmSubwooferProfile(ParadigmSubwooferSelectBase):
    """Representation of Paradigm Subwoofer profile selection."""

    _attr_icon = "mdi:tune-variant"
    _attr_options = PROFILES

    def __init__(self, coordinator: ParadigmSubwooferCoordinator) -> None:
        """Initialize the profile selector."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.client._mac_address}_profile"
        self._attr_name = "Profile"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.client._mac_address)},
            "name": "Paradigm Subwoofer",
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data:
            return self.coordinator.data.get("profile")
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected profile."""
        if option not in PROFILES:
            _LOGGER.error("Invalid profile: %s", option)
            return

        lmd_value = PROFILE_TO_LMD.get(option)
        if lmd_value:
            await self.coordinator.async_send_command(
                self.coordinator.client.set_listening_mode, lmd_value
            )


class ParadigmSubwooferPhase(ParadigmSubwooferSelectBase):
    """Representation of Paradigm Subwoofer phase selection."""

    _attr_icon = "mdi:sine-wave"
    _attr_options = ["0°", "180°"]

    def __init__(self, coordinator: ParadigmSubwooferCoordinator) -> None:
        """Initialize the phase selector."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.client._mac_address}_phase"
        self._attr_name = "Phase"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.client._mac_address)},
            "name": "Paradigm Subwoofer",
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data:
            phase = self.coordinator.data.get("phase")
            if phase is not None:
                return "0°" if phase == 0 else "180°"
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the phase setting."""
        phase_value = 0 if option == "0°" else 180
        await self.coordinator.async_send_command(
            self.coordinator.client.set_phase, phase_value
        )


class ParadigmSubwooferPolarity(ParadigmSubwooferSelectBase):
    """Representation of Paradigm Subwoofer polarity selection."""

    _attr_icon = "mdi:plus-minus"
    _attr_options = ["Normal", "Inverted"]

    def __init__(self, coordinator: ParadigmSubwooferCoordinator) -> None:
        """Initialize the polarity selector."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.client._mac_address}_polarity"
        self._attr_name = "Polarity"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.client._mac_address)},
            "name": "Paradigm Subwoofer",
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        if self.coordinator.data:
            polarity = self.coordinator.data.get("polarity")
            if polarity is not None:
                return "Normal" if polarity == 0 else "Inverted"
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the polarity setting."""
        polarity_value = 0 if option == "Normal" else 1
        await self.coordinator.async_send_command(
            self.coordinator.client.set_polarity, polarity_value
        )
