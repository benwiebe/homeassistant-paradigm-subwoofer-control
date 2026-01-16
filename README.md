# Paradigm Subwoofer Control for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration for controlling Paradigm subwoofers via Bluetooth.

## Features

- **Volume Control**: Adjust subwoofer volume (0-100%)
- **Trim Control**: Fine-tune subwoofer level (-12dB to +12dB)
- **Profile Selection**: Switch between Movie, Music, and Night modes
- **Phase & Polarity**: Fine-tune integration with your speakers (0°/180°, Normal/Inverted)
- **Crossover**: Adjust Low Pass Filter frequency (40Hz-200Hz)
- **Automatic Discovery**: Devices are automatically detected by Home Assistant

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/bwiebe/homeassistant-paradigm-subwoofer-control`
6. Select category "Integration"
7. Click "Add"
8. Search for "Paradigm Subwoofer Control" and install

### Manual Installation

1. Copy the `custom_components/paradigm_subwoofer` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. If your subwoofer is powered on, Home Assistant should automatically show a **Discovered** card for it.
3. Click **Configure** on the discovered device.
4. If it's not discovered automatically:
   - Click **+ Add Integration**
   - Search for **Paradigm Subwoofer Control**
   - The integration will scan for nearby subwoofers for you to select.

## Usage

After configuration, you'll have access to the following entities:

- **Number**: `Volume` - Control output volume (0-100%)
- **Number**: `Trim` - Adjust subwoofer trim (-12 to +12 dB)
- **Number**: `Low Pass Filter` - Set crossover frequency (40-200 Hz)
- **Select**: `Profile` - Choose between Movie, Music, or Night modes
- **Select**: `Phase` - Toggle 0° or 180°
- **Select**: `Polarity` - Normal or Inverted

These can be controlled via:
- Home Assistant UI
- Automations
- Scripts
- Voice assistants (Alexa, Google Assistant, etc.)

## Development Status

This integration is based on reverse-engineered Bluetooth protocol captures from Paradigm Defiance series subwoofers. It uses ASCII-based commands over BLE.

### TODO

- [x] Initial Bluetooth protocol reverse engineering
- [x] Implementation of core Number and Select entities
- [x] Automatic Bluetooth discovery
- [ ] Implement Switch entity for Power control (`Z1POW` command)
- [ ] Add Binary Sensor for connectivity status
- [ ] Robust error handling for intermittent Bluetooth connections
- [ ] Add unit tests with BLE mocking
- [ ] Submit to HACS default repository

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/bwiebe/homeassistant-paradigm-subwoofer-control/issues) on GitHub.
