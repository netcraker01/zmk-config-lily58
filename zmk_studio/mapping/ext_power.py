"""
External Power Constants Mapping for ZMK.

Maps ZMK ext_power behavior parameters to their named constants.
"""

from typing import Dict, Optional


# External Power commands from dt-bindings/zmk/ext_power.h
EXT_POWER_COMMANDS: Dict[int, str] = {
    0: "EP_OFF",  # Power off
    1: "EP_ON",  # Power on
    2: "EP_TOG",  # Toggle
}


def format_ext_power_binding(command: int, param: int) -> str:
    """
    Format an ext_power binding for devicetree.

    Args:
        command: The ext_power command ID
        param: The second parameter (usually 0)

    Returns:
        Formatted binding string like "ext_power EP_ON"
    """
    cmd_name = EXT_POWER_COMMANDS.get(command)
    if cmd_name:
        return f"&ext_power {cmd_name}"
    return f"&ext_power {command} {param}"


__all__ = [
    "EXT_POWER_COMMANDS",
    "format_ext_power_binding",
]
