# Paradigm Subwoofer Control for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration for controlling Paradigm subwoofers via Bluetooth.

## Features

- **Volume Control**: Adjust subwoofer volume (0-100%)
- **Trim Control**: Fine-tune subwoofer level (-12dB to +12dB)
- **Profile Selection**: Switch between Movie, Music, and Night modes
- **Bluetooth Connectivity**: Direct BLE connection to your Paradigm subwoofer

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
2. Click **+ Add Integration**
3. Search for **Paradigm Subwoofer Control**
4. Enter your subwoofer's Bluetooth MAC address
   - You can find this in your Bluetooth settings or using a BLE scanner app
5. Give your subwoofer a name (optional)

## Usage

After configuration, you'll have access to the following entities:

- **Number Entity**: `[Name] Volume` - Control output volume (0-100%)
- **Number Entity**: `[Name] Trim` - Adjust subwoofer trim (-12 to +12 dB)
- **Select Entity**: `[Name] Profile` - Choose between Movie, Music, or Night modes

These can be controlled via:
- Home Assistant UI
- Automations
- Scripts
- Voice assistants (Alexa, Google Assistant, etc.)

## Development Status

⚠️ **Note**: This integration is currently in development. The Bluetooth communication protocol needs to be implemented based on your specific Paradigm subwoofer model.

### TODO

- [ ] Implement actual Bluetooth GATT characteristics/services
- [ ] Add connection state monitoring
- [ ] Add error handling and retry logic
- [ ] Test with actual Paradigm subwoofer hardware
- [ ] Add support for additional settings (phase, crossover, etc.)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/bwiebe/homeassistant-paradigm-subwoofer-control/issues) on GitHub.
