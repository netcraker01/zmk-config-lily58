"""
Modifier Flag Decoding Module for ZMK.

This module provides encoding and decoding of ZMK modifier flags used in
behaviors like &mt (mod-tap), &sl (sticky layer), and others.

Modifiers are represented as bitmasks where each bit corresponds to a specific
modifier key (left/right ctrl, shift, alt, gui).
"""

from typing import List, Union

# ─── Constants ─────────────────────────────────────────────────────────────

# ZMK modifier flags bitmask
# Each modifier occupies one bit in the byte
MODIFIER_FLAGS: Dict[int, str] = {
    0x01: "LCTRL",
    0x02: "LSHFT",
    0x04: "LALT",
    0x08: "LGUI",  # Windows/Command key
    0x10: "RCTRL",
    0x20: "RSHFT",
    0x40: "RALT",  # AltGr
    0x80: "RGUI",  # Windows/Command key
}

# Reverse mapping for encoding
MODIFIER_NAMES: Dict[str, int] = {v: k for k, v in MODIFIER_FLAGS.items()}

# ─── Core Functions ───────────────────────────────────────────────────────


def decode_modifiers(value: int) -> List[str]:
    """
    Decode a modifier bitmask into a list of modifier names.

    Args:
        value: The modifier bitmask (0-255)

    Returns:
        A list of modifier names sorted by bit position

    Examples:
        >>> decode_modifiers(0x03)
        ['LCTRL', 'LSHFT']
        >>> decode_modifiers(0x81)
        ['LCTRL', 'RGUI']
        >>> decode_modifiers(0xFF)
        ['LCTRL', 'LSHFT', 'LALT', 'LGUI', 'RCTRL', 'RSHFT', 'RALT', 'RGUI']
    """
    modifiers = []
    for bit, name in sorted(MODIFIER_FLAGS.items()):
        if value & bit:
            modifiers.append(name)
    return modifiers


def encode_modifiers(modifiers: Union[List[str], str]) -> int:
    """
    Encode a list or string of modifier names into a bitmask.

    Args:
        modifiers: Either a list of modifier names or a comma-separated string

    Returns:
        The combined bitmask

    Examples:
        >>> encode_modifiers(['LCTRL', 'LSHFT'])
        3
        >>> encode_modifiers('LCTRL,LSHFT')
        3
        >>> encode_modifiers(['LGUI', 'RGUI'])
        136
    """
    if isinstance(modifiers, str):
        # Parse comma-separated string
        modifiers = [m.strip() for m in modifiers.split(",") if m.strip()]

    value = 0
    for mod in modifiers:
        if mod in MODIFIER_NAMES:
            value |= MODIFIER_NAMES[mod]
    return value


def format_modifiers(modifiers: List[str], nested: bool = False) -> str:
    """
    Format a list of modifier names into ZMK syntax.

    Args:
        modifiers: List of modifier names
        nested: If True, use nested parentheses; if False, use linear format

    Returns:
        Formatted string

    Examples:
        >>> format_modifiers(['LCTRL', 'LSHFT'])
        'LCTRL(LSHFT)'
        >>> format_modifiers(['LCTRL'], nested=False)
        'LCTRL'
        >>> format_modifiers(['LCTRL', 'LSHFT', 'LALT'], nested=False)
        'LCTRL(LSHFT(LALT))'
    """
    if not modifiers:
        return ""

    if len(modifiers) == 1:
        return modifiers[0]

    if nested:
        # Linear nested format: LCTRL(LSHFT(LALT(...)))
        return "(".join(modifiers) + ")" * (len(modifiers) - 1)
    else:
        # Parenthesized format: (LCTRL LSHFT LALT)
        return "(" + " ".join(modifiers) + ")"


def format_modifiers_from_bitmask(value: int) -> str:
    """
    Decode a modifier bitmask and format it into ZMK syntax.

    Args:
        value: The modifier bitmask

    Returns:
        Formatted string in ZMK modifier syntax

    Examples:
        >>> format_modifiers_from_bitmask(0x03)
        'LCTRL(LSHFT)'
        >>> format_modifiers_from_bitmask(0x01)
        'LCTRL'
        >>> format_modifiers_from_bitmask(0x00)
        ''
    """
    modifiers = decode_modifiers(value)
    return format_modifiers(modifiers, nested=True)


def parse_modifiers_string(modifier_str: str) -> int:
    """
    Parse a ZMK modifier string and return the bitmask.

    Handles formats like:
    - "LCTRL"
    - "LCTRL(LSHFT)"
    - "LCTRL(LSHFT(LALT))"

    Args:
        modifier_str: The modifier string to parse

    Returns:
        The combined bitmask

    Examples:
        >>> parse_modifiers_string('LCTRL')
        1
        >>> parse_modifiers_string('LCTRL(LSHFT)')
        3
        >>> parse_modifiers_string('LCTRL(LSHFT(LALT))')
        7
    """
    # Simple parsing: extract all modifier names
    modifiers = []
    for name in MODIFIER_NAMES.keys():
        if name in modifier_str:
            modifiers.append(name)
    return encode_modifiers(modifiers)


def has_modifiers(value: int, modifiers: Union[List[str], str]) -> bool:
    """
    Check if a bitmask contains all specified modifiers.

    Args:
        value: The modifier bitmask to check
        modifiers: List of modifier names to check for

    Returns:
        True if all specified modifiers are present

    Examples:
        >>> has_modifiers(0x03, ['LCTRL', 'LSHFT'])
        True
        >>> has_modifiers(0x03, ['LCTRL', 'RGUI'])
        False
        >>> has_modifiers(0x01, ['LCTRL'])
        True
    """
    if isinstance(modifiers, str):
        modifiers = [modifiers]

    required_mask = encode_modifiers(modifiers)
    return (value & required_mask) == required_mask


def is_left_modifier(value: int, mod_name: str) -> bool:
    """Check if the modifier is the left-hand version."""
    return has_modifiers(value, f"L{mod_name[1:]}")


def is_right_modifier(value: int, mod_name: str) -> bool:
    """Check if the modifier is the right-hand version."""
    return has_modifiers(value, f"R{mod_name[1:]}")


def get_modifier_count(value: int) -> int:
    """
    Count the number of active modifiers in a bitmask.

    Args:
        value: The modifier bitmask

    Returns:
        Count of active modifiers

    Examples:
        >>> get_modifier_count(0x00)
        0
        >>> get_modifier_count(0x03)
        2
        >>> get_modifier_count(0xFF)
        8
    """
    return bin(value).count("1")


# ─── Module Info ──────────────────────────────────────────────────────────

from typing import Dict

__all__ = [
    "MODIFIER_FLAGS",
    "MODIFIER_NAMES",
    "decode_modifiers",
    "encode_modifiers",
    "format_modifiers",
    "format_modifiers_from_bitmask",
    "parse_modifiers_string",
    "has_modifiers",
    "is_left_modifier",
    "is_right_modifier",
    "get_modifier_count",
]
