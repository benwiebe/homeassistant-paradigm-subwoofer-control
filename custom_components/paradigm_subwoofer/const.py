"""Constants for the Paradigm Subwoofer Control integration."""

DOMAIN = "paradigm_subwoofer"

CONF_MAC_ADDRESS = "mac_address"

DEFAULT_NAME = "Paradigm Subwoofer"

# Bluetooth UUIDs
SERVICE_UUID = "57fbe597-036d-63bb-6748-47e77bb26154"
COMMUNICATION_CHARACTERISTIC_UUID = "e7add780-b042-4876-aae1-112855353cc1"

# Protocol Commands
CMD_VOLUME = "VOL"
CMD_LISTENING_MODE = "LMD"
CMD_TRIM = "TSS"
CMD_POWER = "Z1POW"
CMD_LOW_PASS_FILTER = "LPF"
CMD_PHASE = "PHA"
CMD_POLARITY = "POL"
CMD_DEVICE_NAME = "IDF"
CMD_SERIAL_NUMBER = "IDN"
CMD_FIRMWARE_VERSION = "IDS"

# Profiles (LMD values)
PROFILE_MOVIE = "movie"
PROFILE_MUSIC = "music"
PROFILE_NIGHT = "night"

PROFILES = [PROFILE_MOVIE, PROFILE_MUSIC, PROFILE_NIGHT]

# Profile mapping to LMD command values
# Verified against manufacturer app: LMD0=Music, LMD1=Movie, LMD2=Night
PROFILE_TO_LMD = {
    PROFILE_MUSIC: "0",
    PROFILE_MOVIE: "1",
    PROFILE_NIGHT: "2",
}

LMD_TO_PROFILE = {v: k for k, v in PROFILE_TO_LMD.items()}

# Bluetooth scan interval
SCAN_INTERVAL = 30
