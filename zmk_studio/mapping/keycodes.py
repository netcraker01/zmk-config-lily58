"""
HID Keycode Mapping Module for ZMK.

This module provides a comprehensive mapping of HID Usage Page 0x07 (Keyboard/Keypad)
and Consumer Page 0x0C keycodes to their ZMK mnemonic names.

Based on:
- USB HID Usage Tables v1.12 (HUT) - Usage Page 0x07 (Keyboard/Keypad)
- USB HID Usage Tables v1.12 (HUT) - Usage Page 0x0C (Consumer)
- ZMK keycode definitions from include/zmk/hid_usage.h
"""

from typing import Dict, Optional

# ─── Constants ─────────────────────────────────────────────────────────────

KEYCODE_BASE = 0x70000  # ZMK adds this offset to HID usage codes
CONSUMER_KEYCODE_BASE = 0x00C00  # Approximate offset for consumer keys

# ─── HID Usage Page 0x07 (Keyboard/Keypad) ─────────────────────────────────

# Standard letter keys (0x04-0x1D)
HID_KEYCODES: Dict[int, str] = {
    0x04: "A",
    0x05: "B",
    0x06: "C",
    0x07: "D",
    0x08: "E",
    0x09: "F",
    0x0A: "G",
    0x0B: "H",
    0x0C: "I",
    0x0D: "J",
    0x0E: "K",
    0x0F: "L",
    0x10: "M",
    0x11: "N",
    0x12: "O",
    0x13: "P",
    0x14: "Q",
    0x15: "R",
    0x16: "S",
    0x17: "T",
    0x18: "U",
    0x19: "V",
    0x1A: "W",
    0x1B: "X",
    0x1C: "Y",
    0x1D: "Z",
    # Digit keys (0x1E-0x27)
    0x1E: "N1",
    0x1F: "N2",
    0x20: "N3",
    0x21: "N4",
    0x22: "N5",
    0x23: "N6",
    0x24: "N7",
    0x25: "N8",
    0x26: "N9",
    0x27: "N0",
    # Control keys (0x28-0x39)
    0x28: "ENTER",
    0x29: "ESC",
    0x2A: "BACKSPACE",
    0x2B: "TAB",
    0x2C: "SPACE",
    0x2D: "MINUS",
    0x2E: "EQUAL",
    0x2F: "LBKT",
    0x30: "RBKT",
    0x31: "BSLH",
    0x32: "NON_US_HASH",  # Non-US # and ~
    0x33: "SEMI",
    0x34: "SQT",
    0x35: "GRAVE",
    0x36: "COMMA",
    0x37: "DOT",
    0x38: "SLASH",
    0x39: "CAPS",
    # Function keys (0x3A-0x45)
    0x3A: "F1",
    0x3B: "F2",
    0x3C: "F3",
    0x3D: "F4",
    0x3E: "F5",
    0x3F: "F6",
    0x40: "F7",
    0x41: "F8",
    0x42: "F9",
    0x43: "F10",
    0x44: "F11",
    0x45: "F12",
    # Additional keys (0x46-0x52)
    0x46: "PSCRN",
    0x47: "SLCK",
    0x48: "PAUSE_BREAK",
    0x49: "INS",
    0x4A: "HOME",
    0x4B: "PG_UP",
    0x4C: "DEL",
    0x4D: "END",
    0x4E: "PG_DN",
    0x4F: "RIGHT",
    0x50: "LEFT",
    0x51: "DOWN",
    0x52: "UP",
    # Num Lock and Numpad (0x53-0x63)
    0x53: "NUM_LOCK",
    0x54: "KP_DIV",
    0x55: "KP_MULT",
    0x56: "KP_MINUS",
    0x57: "KP_PLUS",
    0x58: "KP_ENTER",
    0x59: "KP_N1",
    0x5A: "KP_N2",
    0x5B: "KP_N3",
    0x5C: "KP_N4",
    0x5D: "KP_N5",
    0x5E: "KP_N6",
    0x5F: "KP_N7",
    0x60: "KP_N8",
    0x61: "KP_N9",
    0x62: "KP_N0",
    0x63: "KP_DOT",
    # Additional keys (0x64-0x67)
    0x64: "NON_US_BACKSLASH",
    0x65: "APPLICATION",
    0x66: "POWER",
    0x67: "KP_EQUAL",
    # Modifier keys (0xE0-0xE7)
    0xE0: "LCTRL",
    0xE1: "LSHFT",
    0xE2: "LALT",
    0xE3: "LGUI",
    0xE4: "RCTRL",
    0xE5: "RSHFT",
    0xE6: "RALT",
    0xE7: "RGUI",
}

# ─── Consumer Page 0x0C (Consumer) ──────────────────────────────────────────

# Media and consumer control keys
CONSUMER_KEYCODES: Dict[int, str] = {
    # Audio controls (0xE2, 0xE9-0xEA, 0xCD)
    0xE2: "C_MUTE",
    0xE9: "C_VOL_UP",
    0xEA: "C_VOL_DN",
    0xCD: "C_PLAY_PAUSE",
    # Transport controls (0xB2-0xB7)
    0xB2: "C_REWIND",
    0xB3: "C_FAST_FWD",
    0xB4: "C_PLAY",
    0xB5: "C_SCAN_NEXT",
    0xB6: "C_SCAN_PREV",
    0xB7: "C_STOP",
    # Navigation (0x82-0x83)
    0x82: "C_PREV",
    0x83: "C_NEXT",
    # Power controls (0x30)
    0x30: "C_POWER",
    # Browser controls (0x182-0x196)
    0x182: "C_WWW_BACK",
    0x183: "C_WWW_FORWARD",
    0x184: "C_WWW_STOP",
    0x185: "C_WWW_REFRESH",
    0x186: "C_WWW_HOME",
    0x196: "C_WWW_FAVORITES",
    # Additional consumer keys
    0x8A: "C_MAIL",
    0x8C: "C_CALC",
    0x8F: "C_MY_COMPUTER",
    0x94: "C_SEARCH",
    0x21A: "C_BRIGHTNESS_UP",
    0x21B: "C_BRIGHTNESS_DN",
    0x6F: "C_BASS_UP",
    0x70: "C_BASS_DN",
    0x72: "C_TREBLE_UP",
    0x73: "C_TREBLE_DN",
    0x7D: "C_MEDIA",
}

# ─── Helper Functions ─────────────────────────────────────────────────────


def keycode_to_name(param: int, behavior: str = "kp") -> str:
    """
    Convert a ZMK keycode parameter to a human-readable name.

    Args:
        param: The keycode parameter (e.g., 0x70004 for A, 0x20001E for EXCL)
        behavior: The behavior name (default "kp" for key press)

    Returns:
        A human-readable name (e.g., "A", "kp C_MUTE", "EXCL")

    Examples:
        >>> keycode_to_name(0x70004)
        'A'
        >>> keycode_to_name(0x20001E)  # SHIFT + N1
        'EXCL'
        >>> keycode_to_name(0x500E2)  # Consumer MUTE
        'C_MUTE'
    """
    # First check for modified keycodes (usage_page in bits 20-23)
    modified_name = keycode_with_modifiers_name(param)
    if modified_name:
        return modified_name

    # HID Keyboard Usage Page: param - 0x70000 = HID usage
    if param >= KEYCODE_BASE:
        hid = param - KEYCODE_BASE
        name = HID_KEYCODES.get(hid, f"C(0x{hid:02X})")
        if behavior == "kp":
            return name
        return f"{behavior} {name}"

    # Consumer keys (media keys) - usage page 0x0C
    # Consumer keycodes are in the range 0x00C00-0x00FFF
    if param >= CONSUMER_KEYCODE_BASE and param < 0x01000:
        consumer = param - CONSUMER_KEYCODE_BASE
        name = CONSUMER_KEYCODES.get(consumer, f"C(0x{param:04X})")
        return f"cp {name}"

    # Unknown keycodes - return hex representation
    return f"C(0x{param:04X})"


def keycode_name_only(param: int) -> str:
    """
    Convert a ZMK keycode parameter to a human-readable name WITHOUT behavior prefix.

    This is used for behaviors like &lt and &mt where the keycode is part of the behavior,
    not a separate &kp binding.

    Args:
        param: The keycode parameter (e.g., 0x70004 for A, 0x0CE2 for C_MUTE)

    Returns:
        A human-readable name (e.g., "A", "C_MUTE")

    Examples:
        >>> keycode_name_only(0x70004)
        'A'
        >>> keycode_name_only(0x0CE2)
        'C_MUTE'
    """
    # HID Keyboard Usage Page: param - 0x70000 = HID usage
    if param >= KEYCODE_BASE:
        hid = param - KEYCODE_BASE
        return HID_KEYCODES.get(hid, f"C(0x{hid:02X})")

    # Consumer keys (media keys) - usage page 0x0C
    if param >= CONSUMER_KEYCODE_BASE and param < 0x01000:
        consumer = param - CONSUMER_KEYCODE_BASE
        return CONSUMER_KEYCODES.get(consumer, f"C(0x{param:04X})")

    # Unknown keycodes - return hex representation
    return f"C(0x{param:04X})"


def name_to_keycode(name: str) -> Optional[int]:
    """
    Convert a ZMK keycode name to its parameter value.

    Args:
        name: The keycode name (e.g., "A", "N1", "C_MUTE", "F1")

    Returns:
        The parameter value, or None if not found

    Examples:
        >>> name_to_keycode("A")
        458756  # 0x70004
        >>> name_to_keycode("C_MUTE")
        3618  # 0x00E2
    """
    # Remove "kp " prefix if present
    if name.startswith("kp "):
        name = name[3:]

    # Check HID keycodes
    reverse_hid = {v: k for k, v in HID_KEYCODES.items()}
    if name in reverse_hid:
        return KEYCODE_BASE + reverse_hid[name]

    # Check consumer keycodes
    reverse_consumer = {v: k for k, v in CONSUMER_KEYCODES.items()}
    if name in reverse_consumer:
        return CONSUMER_KEYCODE_BASE + reverse_consumer[name]

    return None


def is_hid_keycode(param: int) -> bool:
    """Check if a parameter is a HID keyboard keycode."""
    return param >= KEYCODE_BASE


def is_consumer_keycode(param: int) -> bool:
    """Check if a parameter is a consumer keycode."""
    return param >= CONSUMER_KEYCODE_BASE and param < 0x01000


def get_hid_usage(param: int) -> Optional[int]:
    """Extract the HID usage from a keycode parameter."""
    if is_hid_keycode(param):
        return param - KEYCODE_BASE
    return None


def get_consumer_usage(param: int) -> Optional[int]:
    """Extract the consumer usage from a keycode parameter.

    Args:
        param: The keycode parameter (e.g., 0x0CE2 for C_MUTE)

    Returns:
        The consumer usage code (e.g., 0xE2 for C_MUTE), or None

    Note:
        Consumer keycodes are in the range 0x00C00-0x00FFF.
        The usage is extracted by subtracting the base offset (0x00C00).
        For example, C_MUTE is 0x00C00 + 0xE2 = 0x0CE2, so the usage is 0xE2.
    """
    if is_consumer_keycode(param):
        return param - CONSUMER_KEYCODE_BASE
    return None


def decode_modified_keycode(param: int) -> tuple[int, int]:
    """
    Decode a keycode that may have modifiers applied.

    ZMK encodes modified keycodes by placing modifier flags in the upper bits.
    Format: (modifiers << 24) | keycode

    Common modifier flags:
    - 0x02: SHIFT (LSHFT)
    - 0x04: ALT (LALT)
    - 0x08: GUI (LGUI)
    - 0x01: CTRL (LCTRL)

    For example:
    - 0x20001E = SHIFT + N1 = EXCL (!)
    - 0x200033 = SHIFT + SEMI = COLON (:)

    Args:
        param: The keycode parameter (may include modifiers)

    Returns:
        Tuple of (base_keycode, modifier_flags)
        base_keycode is the raw keycode (e.g., 0x1E for N1)
        modifier_flags is the modifier bitmask (e.g., 0x02 for SHIFT)
    """
    modifier_flags = (param >> 24) & 0xFF
    base_keycode = param & 0xFFFFFF

    # Check if this is a modified keycode (modifier byte > 0)
    if modifier_flags == 0:
        # No modifiers, might still be a modified key if high bits are set
        # Check for pattern where usage page != 0x07
        usage_page = (param >> 16) & 0xFF
        if usage_page == 0x07:
            # Normal HID keycode
            return base_keycode, 0
        else:
            # Different encoding - return as-is
            return param, 0

    return base_keycode, modifier_flags


def keycode_with_modifiers_name(param: int) -> Optional[str]:
    """
    Convert a keycode with modifiers or usage page to a human-readable name.

    This handles:
    - Modified keycodes like SHIFT+N1 = EXCL
    - Consumer keycodes with usage page prefix

    ZMK encoding format:
    - Bits 24-31: Modifier flags (e.g., 0x02 = SHIFT)
    - Bits 16-23: Usage page (e.g., 0x07 = HID Keyboard, 0x05 = Consumer)
    - Bits 0-15: Usage code

    Common values:
    - 0x0207001E: SHIFT + HID_KEYBOARD + N1 = EXCL
    - 0x00070004: HID_KEYBOARD + A = A
    - 0x000500E2: Consumer + MUTE = C_MUTE

    Args:
        param: The keycode parameter (may include usage page)

    Returns:
        Human-readable name (e.g., "EXCL", "AT", "C_MUTE")
        or None if not a recognized modified keycode

    Examples:
        >>> keycode_with_modifiers_name(0x0207001E)  # SHIFT + N1
        'EXCL'
        >>> keycode_with_modifiers_name(0x000500E2)  # Consumer MUTE
        'C_MUTE'
    """
    # Extract components
    modifier = (param >> 24) & 0xFF
    usage_page = (param >> 16) & 0xFF
    usage_code = param & 0xFFFF

    # SHIFT + key mappings (modifier 0x02)
    # These produce shifted symbols: SHIFT + N1 = !
    shift_mappings = {
        0x1E: "EXCL",  # SHIFT + N1 = !
        0x1F: "AT",  # SHIFT + N2 = @
        0x20: "HASH",  # SHIFT + N3 = #
        0x21: "DOLLAR",  # SHIFT + N4 = $
        0x22: "PRCNT",  # SHIFT + N5 = %
        0x23: "CARET",  # SHIFT + N6 = ^
        0x24: "AMPS",  # SHIFT + N7 = &
        0x25: "ASTRK",  # SHIFT + N8 = *
        0x26: "LPAR",  # SHIFT + N9 = (
        0x27: "RPAR",  # SHIFT + N0 = )
        0x2D: "UNDERSCORE",  # SHIFT + MINUS = _
        0x2E: "PLUS",  # SHIFT + EQUAL = +
        0x2F: "LCURLEY",  # SHIFT + LBKT = {
        0x30: "RCURLEY",  # SHIFT + RBKT = }
        0x31: "PIPE",  # SHIFT + BSLH = |
        0x33: "COLON",  # SHIFT + SEMI = :
        0x34: "DQT",  # SHIFT + SQT = "
        0x35: "TILDE",  # SHIFT + GRAVE = ~
        0x36: "LT",  # SHIFT + COMMA = <
        0x37: "GT",  # SHIFT + DOT = >
        0x38: "QM",  # SHIFT + SLASH = ?
    }

    # Check for SHIFT modifier (modifier byte 0x02)
    if modifier == 0x02 and usage_page == 0x07:
        return shift_mappings.get(usage_code)

    # Check for Consumer page (usage_page 0x05 or 0x0C)
    if usage_page in (0x05, 0x0C):
        return CONSUMER_KEYCODES.get(usage_code, f"C(0x{usage_code:03X})")

    return None

    # SHIFT + key mappings (common shifted symbols)
    shift_mappings = {
        0x1E: "EXCL",  # SHIFT + N1 = !
        0x1F: "AT",  # SHIFT + N2 = @
        0x20: "HASH",  # SHIFT + N3 = #
        0x21: "DOLLAR",  # SHIFT + N4 = $
        0x22: "PRCNT",  # SHIFT + N5 = %
        0x23: "CARET",  # SHIFT + N6 = ^
        0x24: "AMPS",  # SHIFT + N7 = &
        0x25: "ASTRK",  # SHIFT + N8 = *
        0x26: "LPAR",  # SHIFT + N9 = (
        0x27: "RPAR",  # SHIFT + N0 = )
        0x2D: "UNDERSCORE",  # SHIFT + MINUS = _
        0x2E: "PLUS",  # SHIFT + EQUAL = +
        0x2F: "LCURLEY",  # SHIFT + LBKT = {
        0x30: "RCURLEY",  # SHIFT + RBKT = }
        0x31: "PIPE",  # SHIFT + BSLH = |
        0x33: "COLON",  # SHIFT + SEMI = :
        0x34: "DQT",  # SHIFT + SQT = "
        0x35: "TILDE",  # SHIFT + GRAVE = ~
        0x36: "LT",  # SHIFT + COMMA = <
        0x37: "GT",  # SHIFT + DOT = >
        0x38: "QM",  # SHIFT + SLASH = ?
    }

    # ALT + key mappings (common alt symbols)
    alt_mappings = {
        # These would depend on the keyboard layout
    }

    if modifiers & 0x02:  # SHIFT
        return shift_mappings.get(base_keycode)
    elif modifiers & 0x04:  # ALT
        return alt_mappings.get(base_keycode)

    return None


# ─── Module Info ──────────────────────────────────────────────────────────

__all__ = [
    "KEYCODE_BASE",
    "CONSUMER_KEYCODE_BASE",
    "HID_KEYCODES",
    "CONSUMER_KEYCODES",
    "keycode_to_name",
    "keycode_name_only",
    "name_to_keycode",
    "is_hid_keycode",
    "is_consumer_keycode",
    "get_hid_usage",
    "get_consumer_usage",
    "decode_modified_keycode",
    "keycode_with_modifiers_name",
]
