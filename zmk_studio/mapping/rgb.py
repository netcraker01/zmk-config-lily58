"""
RGB Underglow Constants Mapping for ZMK.

Maps ZMK rgb_ug behavior parameters to their named constants.
"""

from typing import Dict, Optional

# RGB Underglow commands from dt-bindings/zmk/rgb.h
# Format: command_id -> constant_name
RGB_COMMANDS: Dict[int, str] = {
    0: "RGB_TOG",  # Toggle
    1: "RGB_ON",  # On
    2: "RGB_OFF",  # Off
    3: "RGB_HUI",  # Hue Increase
    4: "RGB_HUD",  # Hue Decrease
    5: "RGB_SAI",  # Saturation Increase
    6: "RGB_SAD",  # Saturation Decrease
    7: "RGB_BRI",  # Brightness Increase
    8: "RGB_BRD",  # Brightness Decrease
    9: "RGB_SPI",  # Speed Increase
    10: "RGB_SPD",  # Speed Decrease
    11: "RGB_EFF",  # Effect Next
    12: "RGB_EFR",  # Effect Previous
}

# RGB Effects (second parameter for some commands)
RGB_EFFECTS: Dict[int, str] = {
    0: "RGB_COLOR",  # Solid color
    1: "RGB_BREATH",  # Breathing
    2: "RGB_CYCLE",  # Color cycle
    3: "RGB_SWIRL",  # Swirl
}


def rgb_command_to_name(command: int, param: int = 0) -> str:
    """
    Convert RGB command ID to ZMK constant name.

    Args:
        command: The RGB command ID (first parameter)
        param: Optional second parameter (not always used)

    Returns:
        RGB constant name or raw format if unknown
    """
    if command in RGB_COMMANDS:
        return RGB_COMMANDS[command]
    return f"{command} {param}"


def format_rgb_binding(command: int, param: int) -> str:
    """
    Format an rgb_ug binding for devicetree.

    Args:
        command: The RGB command ID
        param: The second parameter

    Returns:
        Formatted binding string like "rgb_ug RGB_TOG"
    """
    cmd_name = RGB_COMMANDS.get(command)
    if cmd_name:
        return f"&rgb_ug {cmd_name}"
    return f"&rgb_ug {command} {param}"


__all__ = [
    "RGB_COMMANDS",
    "RGB_EFFECTS",
    "rgb_command_to_name",
    "format_rgb_binding",
]
