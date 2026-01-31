"""Bluetooth client for Paradigm Subwoofer communication."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from bleak import BleakClient, BleakError
from bleak_retry_connector import establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import COMMUNICATION_CHARACTERISTIC_UUID

_LOGGER = logging.getLogger(__name__)


class ParadigmSubwooferClient:
    """Client for communicating with Paradigm Subwoofer via Bluetooth."""

    def __init__(self, hass: HomeAssistant, mac_address: str) -> None:
        """Initialize the client."""
        self._hass = hass
        self._mac_address = mac_address
        self._client: BleakClient | None = None
        self._response_data: str = ""
        self._response_event: asyncio.Event = asyncio.Event()

    async def connect(self) -> None:
        """Connect to the subwoofer."""
        if self._client is None or not self._client.is_connected:
            # Get the BLE device from Home Assistant's bluetooth integration
            # This is required for ESPHome bluetooth proxies
            ble_device = bluetooth.async_ble_device_from_address(
                self._hass, self._mac_address, connectable=True
            )
            if not ble_device:
                raise BleakError(
                    f"Device {self._mac_address} not found. "
                    "Make sure it's in range of a Bluetooth adapter or ESPHome proxy."
                )

            self._client = await establish_connection(
                BleakClient,
                ble_device,
                self._mac_address,
            )
            # Subscribe to notifications
            await self._client.start_notify(
                COMMUNICATION_CHARACTERISTIC_UUID, self._notification_handler
            )
            _LOGGER.debug("Connected to Paradigm Subwoofer at %s", self._mac_address)

    async def disconnect(self) -> None:
        """Disconnect from the subwoofer."""
        if self._client and self._client.is_connected:
            try:
                await self._client.stop_notify(COMMUNICATION_CHARACTERISTIC_UUID)
                await self._client.disconnect()
                _LOGGER.debug("Disconnected from Paradigm Subwoofer")
            except Exception as ex:
                _LOGGER.debug("Error disconnecting: %s", ex)
            finally:
                self._client = None

    def _notification_handler(self, sender: int, data: bytearray) -> None:
        """Handle notifications from the subwoofer."""
        try:
            response = data.decode("ascii")
            _LOGGER.debug("Received notification: %s", response)
            self._response_data = response
            self._response_event.set()
        except Exception as ex:
            _LOGGER.error("Error handling notification: %s", ex)

    async def _send_command(self, command: str) -> str:
        """Send a command and wait for response."""
        if not self._client or not self._client.is_connected:
            await self.connect()

        self._response_event.clear()
        self._response_data = ""

        # Send command
        command_bytes = command.encode("ascii")
        await self._client.write_gatt_char(
            COMMUNICATION_CHARACTERISTIC_UUID, command_bytes, response=False
        )
        _LOGGER.debug("Sent command: %s", command)

        # Wait for response with timeout
        try:
            await asyncio.wait_for(self._response_event.wait(), timeout=5.0)
            return self._response_data
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout waiting for response to command: %s", command)
            return ""

    async def query(self, parameter: str) -> str | None:
        """Query a parameter value."""
        command = f"{parameter}?;"
        response = await self._send_command(command)

        if not response:
            return None

        # Parse response: "PARAMETERvalue;" -> "value"
        if response.startswith(parameter) and response.endswith(";"):
            value = response[len(parameter) : -1]
            return value

        _LOGGER.warning("Unexpected response format: %s", response)
        return None

    async def set_value(self, parameter: str, value: str | int) -> bool:
        """Set a parameter value."""
        command = f"{parameter}{value};"
        response = await self._send_command(command)

        # For set commands, we may not get a direct response
        # Query again to verify
        await asyncio.sleep(0.1)  # Small delay
        actual_value = await self.query(parameter)

        return actual_value == str(value)

    async def get_volume(self) -> int | None:
        """Get current volume (0-100)."""
        value = await self.query("VOL")
        return int(value) if value and value.isdigit() else None

    async def set_volume(self, volume: int) -> bool:
        """Set volume (0-100)."""
        return await self.set_value("VOL", volume)

    async def get_trim(self) -> int | None:
        """Get current trim/subwoofer level."""
        value = await self.query("TSS")
        return int(value) if value and value.lstrip("-").isdigit() else None

    async def set_trim(self, trim: int) -> bool:
        """Set trim/subwoofer level."""
        return await self.set_value("TSS", trim)

    async def get_listening_mode(self) -> str | None:
        """Get current listening mode (0=Movie, 1=Music, 2=Night)."""
        return await self.query("LMD")

    async def set_listening_mode(self, mode: str) -> bool:
        """Set listening mode (0=Movie, 1=Music, 2=Night)."""
        return await self.set_value("LMD", mode)

    async def get_low_pass_filter(self) -> int | None:
        """Get low pass filter frequency."""
        value = await self.query("LPF")
        return int(value) if value and value.isdigit() else None

    async def set_low_pass_filter(self, frequency: int) -> bool:
        """Set low pass filter frequency."""
        return await self.set_value("LPF", frequency)

    async def get_phase(self) -> int | None:
        """Get phase setting (0 or 180)."""
        value = await self.query("PHA")
        return int(value) if value and value.isdigit() else None

    async def set_phase(self, phase: int) -> bool:
        """Set phase (0 or 180)."""
        return await self.set_value("PHA", phase)

    async def get_polarity(self) -> int | None:
        """Get polarity setting."""
        value = await self.query("POL")
        return int(value) if value and value.isdigit() else None

    async def set_polarity(self, polarity: int) -> bool:
        """Set polarity."""
        return await self.set_value("POL", polarity)

    async def get_power(self) -> bool | None:
        """Get power state."""
        value = await self.query("Z1POW")
        if value == "1":
            return True
        elif value == "0":
            return False
        return None

    async def set_power(self, power: bool) -> bool:
        """Set power state."""
        return await self.set_value("Z1POW", "1" if power else "0")

    async def get_device_info(self) -> dict[str, str]:
        """Get device information."""
        info = {}

        device_name = await self.query("IDF")
        if device_name:
            info["name"] = device_name

        serial = await self.query("IDN")
        if serial:
            info["serial_number"] = serial

        firmware = await self.query("IDS")
        if firmware:
            info["firmware_version"] = firmware

        return info

    @property
    def is_connected(self) -> bool:
        """Return if the client is connected."""
        return self._client is not None and self._client.is_connected
