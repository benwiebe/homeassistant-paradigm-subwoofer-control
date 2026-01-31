"""Data coordinator for Paradigm Subwoofer Control integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from bleak import BleakError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import ParadigmSubwooferClient
from .const import DOMAIN, LMD_TO_PROFILE

_LOGGER = logging.getLogger(__name__)


class ParadigmSubwooferCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Paradigm Subwoofer data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ParadigmSubwooferClient,
        update_interval: timedelta | None,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client
        self._consecutive_failures = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the subwoofer."""
        try:
            _LOGGER.debug("Starting data update")

            # Ensure we're connected
            if not self.client.is_connected:
                _LOGGER.debug("Connecting to subwoofer")
                await self.client.connect()

            # Query all values
            data = {}

            volume = await self.client.get_volume()
            if volume is not None:
                data["volume"] = volume
                _LOGGER.debug("Volume: %s", volume)

            trim = await self.client.get_trim()
            if trim is not None:
                data["trim"] = trim
                _LOGGER.debug("Trim: %s", trim)

            lpf = await self.client.get_low_pass_filter()
            if lpf is not None:
                data["low_pass_filter"] = lpf
                _LOGGER.debug("Low pass filter: %s", lpf)

            lmd = await self.client.get_listening_mode()
            if lmd and lmd in LMD_TO_PROFILE:
                data["profile"] = LMD_TO_PROFILE[lmd]
                _LOGGER.debug("Profile: %s", data["profile"])

            phase = await self.client.get_phase()
            if phase is not None:
                data["phase"] = phase
                _LOGGER.debug("Phase: %s", phase)

            polarity = await self.client.get_polarity()
            if polarity is not None:
                data["polarity"] = polarity
                _LOGGER.debug("Polarity: %s", polarity)

            # Disconnect immediately after fetching data
            _LOGGER.debug("Disconnecting from subwoofer")
            await self.client.disconnect()

            # Reset failure counter on success
            self._consecutive_failures = 0

            _LOGGER.debug("Data update complete: %s", data)
            return data

        except BleakError as err:
            # Bluetooth errors - likely device is off or out of range
            await self.client.disconnect()
            self._consecutive_failures += 1

            # Only log as warning for first few failures, then debug to avoid spam
            if self._consecutive_failures <= 3:
                _LOGGER.warning(
                    "Cannot connect to subwoofer (device may be powered off): %s", err
                )
            else:
                _LOGGER.debug(
                    "Cannot connect to subwoofer (attempt %d): %s",
                    self._consecutive_failures,
                    err,
                )
            raise UpdateFailed(
                f"Device unavailable (likely powered off)"
            ) from err

        except Exception as err:
            # Other unexpected errors
            await self.client.disconnect()
            self._consecutive_failures += 1
            _LOGGER.error("Unexpected error communicating with subwoofer: %s", err)
            raise UpdateFailed(f"Error communicating with subwoofer: {err}") from err

    async def async_send_command(
        self, command_func, *args, **kwargs
    ) -> Any:
        """Send a command to the subwoofer and handle connection management."""
        try:
            _LOGGER.debug("Sending command: %s with args=%s, kwargs=%s",
                         command_func.__name__, args, kwargs)

            # Ensure we're connected
            if not self.client.is_connected:
                _LOGGER.debug("Connecting to send command")
                await self.client.connect()

            # Execute the command
            result = await command_func(*args, **kwargs)
            _LOGGER.debug("Command %s executed successfully, result: %s",
                         command_func.__name__, result)

            # Reset failure counter on successful command
            self._consecutive_failures = 0

            # Refresh data after command
            _LOGGER.debug("Refreshing data after command")
            await self.async_request_refresh()

            return result

        except BleakError as err:
            _LOGGER.warning("Cannot send command (device may be powered off): %s", err)
            await self.client.disconnect()
            raise

        except Exception as err:
            _LOGGER.error("Error sending command: %s", err)
            await self.client.disconnect()
            raise

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and disconnect."""
        if self.client.is_connected:
            await self.client.disconnect()
