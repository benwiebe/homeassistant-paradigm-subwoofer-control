"""Bluetooth client for Paradigm Subwoofer communication."""
from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient, BleakError
from bleak_retry_connector import establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import COMMUNICATION_CHARACTERISTIC_UUID

_LOGGER = logging.getLogger(__name__)

# Timeout waiting for an indication after writing a command (seconds).
_INDICATION_TIMEOUT = 5.0

# How many times to retry a failed connect attempt before giving up.
_CONNECT_RETRIES = 3


class ParadigmSubwooferClient:
    """Client for communicating with Paradigm Subwoofer via Bluetooth."""

    def __init__(self, hass: HomeAssistant, mac_address: str) -> None:
        """Initialize the client."""
        self._hass = hass
        self._mac_address = mac_address.upper()
        self._client: BleakClient | None = None
        self._disconnect_timer: asyncio.TimerHandle | None = None
        # Set by the indication handler; waited on by _send_command.
        self._indication_event: asyncio.Event = asyncio.Event()
        self._indication_data: str = ""

    async def connect(self) -> None:
        """Connect to the subwoofer."""
        self._cancel_disconnect_timer()
        if self._client is not None and self._client.is_connected:
            return

        # Always fetch a fresh BLEDevice so that the correct transport
        # (native adapter or ESPHome proxy) is used.  The object encodes
        # *which* proxy/adapter to use, so we must not reuse a stale one.
        ble_device = bluetooth.async_ble_device_from_address(
            self._hass, self._mac_address, connectable=True
        )
        if not ble_device:
            # Fall back to non-connectable advertisement in case the proxy
            # has only seen a passive scan result so far.
            ble_device = bluetooth.async_ble_device_from_address(
                self._hass, self._mac_address, connectable=False
            )

        if not ble_device:
            all_devices = bluetooth.async_discovered_service_info(self._hass)
            _LOGGER.debug(
                "Device %s not in HA BLE cache. Known devices: %s",
                self._mac_address,
                [d.address for d in all_devices],
            )
            raise BleakError(
                f"Device {self._mac_address} not found. "
                "Make sure it is in range of a Bluetooth adapter or ESPHome proxy."
            )

        _LOGGER.debug(
            "Connecting to %s via %s",
            self._mac_address,
            getattr(ble_device, "details", ble_device),
        )

        # establish_connection (from bleak-retry-connector) handles:
        #   - ESPHome proxy transport (BLEDevice must be passed, not a MAC string)
        #   - Automatic retries with backoff on transient failures
        #   - Selecting the best proxy when multiple are available
        # The disconnected_callback keeps self._client in sync if the
        # peripheral drops the connection unexpectedly.
        try:
            self._client = await establish_connection(
                BleakClient,
                ble_device,
                self._mac_address,
                disconnected_callback=self._on_disconnect,
                max_attempts=_CONNECT_RETRIES,
            )
        except Exception:
            self._client = None
            raise

        # Subscribe to indications.  Bleak's start_notify handles both
        # notifications (CCCD 0x0001) and indications (CCCD 0x0002) through
        # the same callback interface and automatically sends the ATT
        # Confirmation required for indications.
        await self._client.start_notify(
            COMMUNICATION_CHARACTERISTIC_UUID, self._indication_handler
        )
        _LOGGER.info("Connected to Paradigm Subwoofer at %s", self._mac_address)

    def _indication_handler(self, sender: int, data: bytearray) -> None:
        """Handle indication from the subwoofer."""
        try:
            self._indication_data = data.decode("ascii")
            _LOGGER.debug("Indication received: %s", self._indication_data)
            self._indication_event.set()
        except Exception as ex:
            _LOGGER.error("Error decoding indication: %s", ex)

    def _on_disconnect(self, client: BleakClient) -> None:
        """Called by Bleak when the peripheral drops the connection."""
        _LOGGER.debug("Paradigm Subwoofer %s disconnected", self._mac_address)
        self._client = None
        self._cancel_disconnect_timer()

    async def disconnect(self) -> None:
        """Disconnect from the subwoofer."""
        self._cancel_disconnect_timer()
        client = self._client
        self._client = None
        if client and client.is_connected:
            try:
                await client.stop_notify(COMMUNICATION_CHARACTERISTIC_UUID)
            except Exception:
                pass
            try:
                await client.disconnect()
                _LOGGER.debug("Disconnected from Paradigm Subwoofer")
            except Exception as ex:
                _LOGGER.debug("Error disconnecting: %s", ex)

    def _schedule_disconnect(self) -> None:
        """Schedule a disconnect after a short idle period."""
        self._cancel_disconnect_timer()
        self._disconnect_timer = self._hass.loop.call_later(
            10,
            lambda: self._hass.async_create_task(self.disconnect()),
        )

    def _cancel_disconnect_timer(self) -> None:
        """Cancel any pending idle-disconnect timer."""
        if self._disconnect_timer:
            self._disconnect_timer.cancel()
            self._disconnect_timer = None

    async def _send_command(self, command: str) -> str:
        """Write *command* and wait for the device's indication response.

        Packet-capture analysis confirms the protocol is:
          1. ATT Write Request (write-with-response) the ASCII command
          2. Device replies with an ATT Handle Value Indication carrying the
             ASCII response (e.g. ``VOL?;`` → indication ``VOL50;``)
          3. Bleak automatically sends the ATT Confirmation for the indication

        Bleak's start_notify/stop_notify handles indications (CCCD 0x0002)
        transparently through the same callback as notifications.
        """
        if not self._client or not self._client.is_connected:
            await self.connect()

        command_bytes = command.encode("ascii")
        _LOGGER.debug("Sending command: %s", command)

        self._indication_event.clear()
        self._indication_data = ""

        # Write with response: ATT Write Request / Write Response handshake
        # ensures the peripheral has received the command before we wait.
        await self._client.write_gatt_char(
            COMMUNICATION_CHARACTERISTIC_UUID, command_bytes, response=True
        )

        try:
            async with asyncio.timeout(_INDICATION_TIMEOUT):
                await self._indication_event.wait()
            response = self._indication_data.strip()
            _LOGGER.debug("Response to %s: %s", command, response)
            self._schedule_disconnect()
            return response
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout reading response for command %s", command)
            self._schedule_disconnect()
            return ""
        except Exception as ex:
            _LOGGER.warning("Failed to read response for command %s: %s", command, ex)
            await self.disconnect()
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
        """Get current volume (0-100).

        The device reports values 1-101 internally; subtract 1 to map to 0-100.
        """
        value = await self.query("VOL")
        return int(value) - 1 if value and value.isdigit() else None

    async def set_volume(self, volume: int) -> bool:
        """Set volume (0-100).

        The device uses 1-101 internally; add 1 to convert from 0-100.
        """
        return await self.set_value("VOL", volume + 1)

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
