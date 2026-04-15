"""
ZMK Studio - Modular ZMK Keymap Extractor.

This package provides a refactored, modular implementation of the ZMK
keymap extractor with the following modules:

- protocol: Serial communication, framing, protobuf encoding/decoding
- mapping: Keycode mapping, modifier decoding, behavior resolution, layer naming
- formatter: Multiple output formats (JSON, YAML, CSV, devicetree)
- extractor: Main extraction and export functionality
- tests: Unit and integration tests

Example usage:
    >>> from zmk_studio import KeymapExtractor
    >>> extractor = KeymapExtractor(port="COM8")
    >>> keymap = extractor.extract()
    >>> json_output = extractor.export(keymap, "json", "output.json")
"""

__version__ = "2.0.0"
__author__ = "ZMK Community"

from .extractor import KeymapExtractor, RPCClient, RPCError
from .extractor.rpc_client import LOCK_STATE_LOCKED, LOCK_STATE_UNLOCKED

__all__ = [
    "KeymapExtractor",
    "RPCClient",
    "RPCError",
    "LOCK_STATE_LOCKED",
    "LOCK_STATE_UNLOCKED",
]
