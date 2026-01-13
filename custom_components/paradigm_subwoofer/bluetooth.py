"""Bluetooth discovery and parsing for Paradigm Subwoofer."""
from __future__ import annotations

import logging

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

_LOGGER = logging.getLogger(__name__)

# Paradigm subwoofer device name patterns
PARADIGM_DEVICE_NAMES = ["Defiance", "Paradigm"]


def is_paradigm_subwoofer(discovery_info: BluetoothServiceInfoBleak) -> bool:
    """Check if the discovered device is a Paradigm subwoofer."""
    device_name = discovery_info.name

    if not device_name:
        return False

    # Check if device name contains any of the known Paradigm patterns
    return any(pattern in device_name for pattern in PARADIGM_DEVICE_NAMES)


def get_device_name(discovery_info: BluetoothServiceInfoBleak) -> str:
    """Get the device name from discovery info."""
    return discovery_info.name or "Paradigm Subwoofer"
