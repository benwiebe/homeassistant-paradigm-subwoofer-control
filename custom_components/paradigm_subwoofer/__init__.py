"""The Paradigm Subwoofer Control integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .client import ParadigmSubwooferClient
from .const import CONF_MAC_ADDRESS, DOMAIN
from .coordinator import ParadigmSubwooferCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.NUMBER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Paradigm Subwoofer Control from a config entry."""
    mac_address = entry.data[CONF_MAC_ADDRESS]

    # Create client
    client = ParadigmSubwooferClient(mac_address)

    # Create coordinator without automatic updates (on-demand only)
    coordinator = ParadigmSubwooferCoordinator(
        hass,
        client,
        update_interval=None,
    )

    # Try to fetch initial data, but don't fail setup if device is unavailable
    # This allows the integration to load even when the subwoofer is powered off
    try:
        await coordinator.async_refresh()
    except Exception as err:
        _LOGGER.info(
            "Could not connect to subwoofer during setup (device may be powered off): %s",
            err,
        )

    # Store coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Shutdown coordinator
    coordinator: ParadigmSubwooferCoordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_shutdown()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
