"""
ZMK Mapping Module.

This module provides comprehensive mapping utilities for ZMK keymap data:
- keycodes: HID and Consumer keycode mapping
- modifiers: Modifier flag encoding/decoding
- behaviors: Dynamic behavior resolution with caching
- layers: Semantic layer name generation
"""

from .keycodes import (
    KEYCODE_BASE,
    CONSUMER_KEYCODE_BASE,
    HID_KEYCODES,
    CONSUMER_KEYCODES,
    keycode_to_name,
    name_to_keycode,
    is_hid_keycode,
    is_consumer_keycode,
    get_hid_usage,
    get_consumer_usage,
)

from .modifiers import (
    MODIFIER_FLAGS,
    MODIFIER_NAMES,
    decode_modifiers,
    encode_modifiers,
    format_modifiers,
    format_modifiers_from_bitmask,
    parse_modifiers_string,
    has_modifiers,
    is_left_modifier,
    is_right_modifier,
    get_modifier_count,
)

from .behaviors import (
    DEFAULT_CACHE_FILE,
    STATIC_BEHAVIOR_MAP,
    BehaviorCache,
    BehaviorResolver,
    create_resolver,
    load_static_behaviors,
)

from .layers import (
    SEMANTIC_LAYER_NAMES,
    DEFAULT_MAX_LAYERS,
    LayerNameGenerator,
    parse_keymap_layers,
    generate_layer_name,
    generate_layer_names,
    layer_id_from_name,
    is_sequential_layer_name,
)

__all__ = [
    # Keycodes
    "KEYCODE_BASE",
    "CONSUMER_KEYCODE_BASE",
    "HID_KEYCODES",
    "CONSUMER_KEYCODES",
    "keycode_to_name",
    "name_to_keycode",
    "is_hid_keycode",
    "is_consumer_keycode",
    "get_hid_usage",
    "get_consumer_usage",
    # Modifiers
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
    # Behaviors
    "DEFAULT_CACHE_FILE",
    "STATIC_BEHAVIOR_MAP",
    "BehaviorCache",
    "BehaviorResolver",
    "create_resolver",
    "load_static_behaviors",
    # Layers
    "SEMANTIC_LAYER_NAMES",
    "DEFAULT_MAX_LAYERS",
    "LayerNameGenerator",
    "parse_keymap_layers",
    "generate_layer_name",
    "generate_layer_names",
    "layer_id_from_name",
    "is_sequential_layer_name",
]
