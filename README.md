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

2. Make changes to keymap (`config/Lily58.keymap`) or config (`config/lily58.conf`)

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
- ✅ ZMK Studio (live keymap editing)

## Keymap Layers

- **DEFAULT**: Base QWERTY layout with hyper-mod-tap on right pinky
- **NAV** (Hold Space): Navigation, F-keys, Bluetooth controls
- **SYM** (Hold Enter): Symbols, RGB controls
- **ADJUST**: RGB advanced controls

## Special Keys

### Hyper Mod-Tap (Right Pinky)
The rightmost key on the home row acts as:
- **Tap**: `_` (underscore)
- **Hold**: Hyper modifier (LCTRL + LALT + LGUI + RSHIFT)

This is implemented using a custom macro-based hold-tap behavior since ZMK's built-in `&mt` doesn't support multiple modifiers.

## RGB Controls (in SYM layer)

- `RGB_TOG` - Toggle RGB on/off
- `RGB_HUD` - Hue down
- `RGB_HUI` - Hue up
- `RGB_SAD` - Saturation down
- `RGB_SAI` - Saturation up
- `RGB_EFF` - Next effect
- `RGB_BRD` - Brightness down
- `RGB_BRI` - Brightness up

## Bluetooth Controls (in NAV layer)

- `BT_CLR` - Clear all Bluetooth bonds
- `BT_SEL 0-4` - Switch between 5 Bluetooth profiles

## Hardware

- Board: nice!nano V2
- Shield: lily58_left, lily58_right (with nice!oled)
- OLED: SSD1306 128x32 I2C
- RGB: WS2812 (6 LEDs per side)

## ZMK Studio Keymap Extractor

This repository includes a tool to extract keymaps from ZMK keyboards via the ZMK Studio protocol.

### Quick Usage

```bash
# Extract keymap from keyboard
python -m zmk_studio.cli -p COM8 extract --format devicetree --output extracted.keymap

# List available behaviors
python -m zmk_studio.cli list-behaviors
```

See [zmk_studio/README.md](zmk_studio/README.md) for full documentation.

### Why This Tool?

ZMK Studio allows live keymap editing, but the changes are only stored in the keyboard's flash memory. This tool extracts the current keymap configuration so you can:
1. Save it to your repository
2. Build firmware with your exact current configuration
3. Sync changes made via ZMK Studio back to your config files

## Building

Firmware is built automatically via GitHub Actions on every push.
Download the compiled `.uf2` files from the Actions tab.

## Keymap Implementation Notes

### Multi-Modifier Mod-Tap

ZMK's `&mt` behavior only accepts a single modifier. For multi-modifier hold-taps (like a "Hyper" key), use a macro-based approach:

```dts
macros {
    hyper_mod: hyper_mod {
        compatible = "zmk,behavior-macro";
        #binding-cells = <0>;
        bindings
            = <&macro_press &kp LCTRL &kp LALT &kp LGUI &kp RSHFT>
            , <&macro_pause_for_release>
            , <&macro_release &kp RSHFT &kp LGUI &kp LALT &kp LCTRL>
            ;
    };
};

behaviors {
    ht_hyper: ht_hyper {
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;  // Required: must be 2
        flavor = "hold-preferred";
        tapping-term-ms = <200>;
        bindings = <&hyper_mod>, <&kp>;
    };
};

// Usage in keymap: &ht_hyper 0 UNDERSCORE
// First param (0) is dummy, second is the tap keycode
```

## Credits

- [ZMK Firmware](https://github.com/zmkfirmware/zmk)
- [PandaKBLab Module](https://github.com/PandaKBLab/zmk-for-keyboards)
- [Lily58 Keyboard](https://github.com/kata0510/Lily58)