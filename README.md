# ZMK Configuration for Lily58 RGB

Custom ZMK firmware configuration for Lily58 RGB split keyboard with:
- nice!nano V2 controller
- OLED Display (SSD1306 128x32)
- RGB Underglow (6 LEDs per side, WS2812)
- Bluetooth connectivity

## Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/netcraker01/zmk-config-lily58.git
   cd zmk-config-lily58
   ```

2. Make changes to keymap (`config/lily58.keymap`) or config (`config/lily58.conf`)

3. Commit and push:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```

4. Download compiled firmware from GitHub Actions

## Features Enabled

- ✅ OLED Display with status screen
- ✅ RGB Underglow (Swirl effect, auto-off in idle)
- ✅ Bluetooth (5 profiles)
- ✅ Battery reporting
- ✅ Deep sleep support
- ✅ Encoders support
- ✅ ZMK Studio

## Keymap Layers

- **DEFAULT**: Base QWERTY layout
- **LOWER** (Fn + Space): Numbers, F-keys, Bluetooth controls
- **RAISE** (Fn + Enter): RGB controls, media keys
- **ADJUST**: RGB advanced controls

## RGB Controls (in RAISE layer)

- `RGB_TOG` - Toggle RGB on/off
- `RGB_HUD` - Hue down
- `RGB_HUI` - Hue up
- `RGB_SAD` - Saturation down
- `RGB_SAI` - Saturation up
- `RGB_EFF` - Next effect
- `RGB_BRD` - Brightness down
- `RGB_BRI` - Brightness up

## Bluetooth Controls (in LOWER layer)

- `BT_CLR` - Clear all Bluetooth bonds
- `BT_SEL 0-4` - Switch between 5 Bluetooth profiles

## Hardware

- Board: nice!nano V2
- Shield: lily58_left, lily58_right
- OLED: SSD1306 128x32 I2C
- RGB: WS2812 (6 LEDs per side)

## Building

Firmware is built automatically via GitHub Actions on every push.
Download the compiled `.uf2` files from the Actions tab.

## Credits

- [ZMK Firmware](https://github.com/zmkfirmware/zmk)
- [PandaKBLab Module](https://github.com/PandaKBLab/zmk-for-keyboards)
- [Lily58 Keyboard](https://github.com/kata0510/Lily58)