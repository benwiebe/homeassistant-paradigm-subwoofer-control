"""Select platform for Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import ParadigmSubwooferClient
from .const import CONF_MAC_ADDRESS, DOMAIN, LMD_TO_PROFILE, PROFILE_TO_LMD, PROFILES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Paradigm Subwoofer select platform."""
    name = config_entry.data[CONF_NAME]
    mac_address = config_entry.data[CONF_MAC_ADDRESS]

    client = ParadigmSubwooferClient(mac_address)

    async_add_entities(
        [
            ParadigmSubwooferProfile(name, mac_address, config_entry.entry_id, client),
            ParadigmSubwooferPhase(name, mac_address, config_entry.entry_id, client),
            ParadigmSubwooferPolarity(name, mac_address, config_entry.entry_id, client),
        ],
        True,
    )


class ParadigmSubwooferProfile(SelectEntity):
    """Representation of Paradigm Subwoofer profile selection."""

    _attr_icon = "mdi:tune-variant"

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        client: ParadigmSubwooferClient,
    ) -> None:
        """Initialize the profile selector."""
        self._base_name = name
        self._mac_address = mac_address
        self._attr_name = f"{name} Profile"
        self._attr_unique_id = f"{mac_address}_profile"
        self._attr_options = PROFILES
        self._attr_device_info = {
            "identifiers": {(DOMAIN, mac_address)},
            "name": name,
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }
        self._client = client

    async def async_select_option(self, option: str) -> None:
        """Change the selected profile."""
        if option not in PROFILES:
            _LOGGER.error("Invalid profile: %s", option)
            return

        try:
            lmd_value = PROFILE_TO_LMD.get(option)
            if lmd_value:
                success = await self._client.set_listening_mode(lmd_value)
                if success:
                    self._attr_current_option = option
                else:
                    _LOGGER.warning("Failed to set profile to %s", option)
        except Exception as ex:
            _LOGGER.error("Error setting profile: %s", ex)
            raise

    async def async_update(self) -> None:
        """Update the current profile."""
        try:
            lmd_value = await self._client.get_listening_mode()
            if lmd_value and lmd_value in LMD_TO_PROFILE:
                self._attr_current_option = LMD_TO_PROFILE[lmd_value]
        except Exception as ex:
            _LOGGER.debug("Error updating profile: %s", ex)


class ParadigmSubwooferPhase(SelectEntity):
    """Representation of Paradigm Subwoofer phase selection."""

    _attr_icon = "mdi:sine-wave"
    _attr_options = ["0°", "180°"]

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        client: ParadigmSubwooferClient,
    ) -> None:
        """Initialize the phase selector."""
        self._base_name = name
        self._mac_address = mac_address
        self._attr_name = f"{name} Phase"
        self._attr_unique_id = f"{mac_address}_phase"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, mac_address)},
            "name": name,
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }
        self._client = client

    async def async_select_option(self, option: str) -> None:
        """Change the phase setting."""
        try:
            phase_value = 0 if option == "0°" else 180
            success = await self._client.set_phase(phase_value)
            if success:
                self._attr_current_option = option
            else:
                _LOGGER.warning("Failed to set phase to %s", option)
        except Exception as ex:
            _LOGGER.error("Error setting phase: %s", ex)
            raise

    async def async_update(self) -> None:
        """Update the current phase."""
        try:
            phase = await self._client.get_phase()
            if phase is not None:
                self._attr_current_option = "0°" if phase == 0 else "180°"
        except Exception as ex:
            _LOGGER.debug("Error updating phase: %s", ex)


class ParadigmSubwooferPolarity(SelectEntity):
    """Representation of Paradigm Subwoofer polarity selection."""

    _attr_icon = "mdi:plus-minus"
    _attr_options = ["Normal", "Inverted"]

    def __init__(
        self,
        name: str,
        mac_address: str,
        entry_id: str,
        client: ParadigmSubwooferClient,
    ) -> None:
        """Initialize the polarity selector."""
        self._base_name = name
        self._mac_address = mac_address
        self._attr_name = f"{name} Polarity"
        self._attr_unique_id = f"{mac_address}_polarity"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, mac_address)},
            "name": name,
            "manufacturer": "Paradigm",
            "model": "Bluetooth Subwoofer",
        }
        self._client = client

    async def async_select_option(self, option: str) -> None:
        """Change the polarity setting."""
        try:
            polarity_value = 0 if option == "Normal" else 1
            success = await self._client.set_polarity(polarity_value)
            if success:
                self._attr_current_option = option
            else:
                _LOGGER.warning("Failed to set polarity to %s", option)
        except Exception as ex:
            _LOGGER.error("Error setting polarity: %s", ex)
            raise

    async def async_update(self) -> None:
        """Update the current polarity."""
        try:
            polarity = await self._client.get_polarity()
            if polarity is not None:
                self._attr_current_option = "Normal" if polarity == 0 else "Inverted"
        except Exception as ex:
            _LOGGER.debug("Error updating polarity: %s", ex)
