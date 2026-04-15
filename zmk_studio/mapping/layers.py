"""
Layer Naming Module for ZMK.

This module provides semantic layer name generation for ZMK keymaps.

Since ZMK Studio doesn't persist layer names in the firmware, this module
provides:
- Semantic naming conventions (BASE, NAV, SYM, ADJUST, etc.)
- Fallback to sequential naming (LAYER_0, LAYER_1, etc.)
- Support for reading original layer names from keymap files
- Layer ID to name mapping
"""

from typing import Dict, List, Optional, Union
from pathlib import Path
import re

# ─── Constants ─────────────────────────────────────────────────────────────

# Semantic layer name conventions
# These are common layer names used in the ZMK community
SEMANTIC_LAYER_NAMES = [
    "BASE",  # Primary typing layer
    "NAV",  # Navigation layer (arrows, home/end, etc.)
    "SYM",  # Symbols layer (symbols, punctuation)
    "ADJUST",  # Adjustment/FN layer (function keys, system controls)
]

# Default number of layers for sequential fallback
DEFAULT_MAX_LAYERS = 32


# ─── Layer Name Generator ───────────────────────────────────────────────────


class LayerNameGenerator:
    """
    Generates layer names with semantic fallback.

    This class provides flexible layer name generation with:
    1. Semantic names from a predefined list
    2. Sequential names (LAYER_0, LAYER_1, etc.)
    3. Custom mappings for specific layer IDs
    4. Original names from keymap files
    """

    def __init__(
        self,
        semantic_names: Optional[List[str]] = None,
        custom_mapping: Optional[Dict[int, str]] = None,
        original_names: Optional[Dict[int, str]] = None,
    ):
        """
        Initialize the layer name generator.

        Args:
            semantic_names: List of semantic names to use (default: SEMANTIC_LAYER_NAMES)
            custom_mapping: Custom layer ID -> name mapping
            original_names: Original layer names from keymap file
        """
        self.semantic_names = semantic_names or SEMANTIC_LAYER_NAMES.copy()
        self.custom_mapping = custom_mapping or {}
        self.original_names = original_names or {}

    def generate_name(self, layer_id: int) -> str:
        """
        Generate a semantic name for a layer ID.

        Priority order:
        1. Custom mapping
        2. Original name from keymap (if non-empty)
        3. Semantic name from list
        4. Sequential fallback (LAYER_0, LAYER_1, etc.)

        Args:
            layer_id: The layer ID to generate a name for

        Returns:
            A layer name

        Examples:
            >>> gen = LayerNameGenerator()
            >>> gen.generate_name(0)
            'BASE'
            >>> gen.generate_name(1)
            'NAV'
            >>> gen.generate_name(4)
            'LAYER_4'
        """
        # Check custom mapping first
        if layer_id in self.custom_mapping:
            return self.custom_mapping[layer_id]

        # Check original name from keymap (if provided and non-empty)
        if layer_id in self.original_names and self.original_names[layer_id]:
            return self.original_names[layer_id]

        # Use semantic name if available
        if layer_id < len(self.semantic_names):
            return self.semantic_names[layer_id]

        # Fallback to sequential naming
        return f"LAYER_{layer_id}"

    def generate_names(self, layer_ids: List[int]) -> Dict[int, str]:
        """
        Generate names for multiple layer IDs.

        Args:
            layer_ids: List of layer IDs

        Returns:
            Dict mapping layer_id -> name
        """
        return {lid: self.generate_name(lid) for lid in layer_ids}

    def get_semantic_name(self, layer_id: int) -> Optional[str]:
        """
        Get the semantic name for a layer ID (without fallback).

        Returns None if layer_id is out of semantic name range.

        Args:
            layer_id: The layer ID

        Returns:
            Semantic name or None
        """
        if layer_id < len(self.semantic_names):
            return self.semantic_names[layer_id]
        return None

    def set_custom_mapping(self, layer_id: int, name: str) -> None:
        """
        Set a custom name for a specific layer ID.

        Args:
            layer_id: The layer ID
            name: The custom name
        """
        self.custom_mapping[layer_id] = name

    def load_original_names(self, names: Dict[int, str]) -> None:
        """
        Load original layer names from a keymap file.

        Args:
            names: Dict mapping layer_id -> name
        """
        self.original_names.update(names)

    def clear_original_names(self) -> None:
        """Clear all original layer names."""
        self.original_names.clear()


# ─── Layer Name Parser ─────────────────────────────────────────────────────


def parse_keymap_layers(keymap_path: Union[str, Path]) -> Dict[int, str]:
    """
    Parse layer names from a ZMK keymap devicetree file.

    Args:
        keymap_path: Path to the .keymap file

    Returns:
        Dict mapping layer_id -> layer_name (empty string if name not found)

    Examples:
        >>> parse_keymap_layers("config/lily58.keymap")
        {0: 'base', 1: 'nav', 2: 'sym', 3: 'adjust'}
    """
    keymap_path = Path(keymap_path)
    if not keymap_path.exists():
        return {}

    layer_names = {}

    try:
        with open(keymap_path, "r") as f:
            content = f.read()

        # Find layer definitions like:
        # / { label = "base"; ...
        # / { label = "nav"; ...
        pattern = r'/\s*\{\s*label\s*=\s*"([^"]+)"\s*;'
        matches = re.finditer(pattern, content)

        for idx, match in enumerate(matches):
            layer_names[idx] = match.group(1)

    except (IOError, UnicodeDecodeError):
        pass

    return layer_names


def generate_layer_name(layer_id: int, layer_names: Optional[List[str]] = None) -> str:
    """
    Generate a semantic name for a layer ID.

    Simple wrapper around LayerNameGenerator for convenience.

    Args:
        layer_id: The layer ID
        layer_names: Optional list of custom layer names

    Returns:
        A layer name

    Examples:
        >>> generate_layer_name(0)
        'BASE'
        >>> generate_layer_name(3)
        'ADJUST'
        >>> generate_layer_name(4)
        'LAYER_4'
    """
    if layer_names and layer_id < len(layer_names) and layer_names[layer_id]:
        return layer_names[layer_id]

    if layer_id < len(SEMANTIC_LAYER_NAMES):
        return SEMANTIC_LAYER_NAMES[layer_id]

    return f"LAYER_{layer_id}"


def generate_layer_names(
    count: int, custom_names: Optional[List[str]] = None
) -> List[str]:
    """
    Generate names for multiple layers.

    Args:
        count: Number of layer names to generate
        custom_names: Optional list of custom names (index = layer_id)

    Returns:
        List of layer names

    Examples:
        >>> generate_layer_names(4)
        ['BASE', 'NAV', 'SYM', 'ADJUST']
        >>> generate_layer_names(6)
        ['BASE', 'NAV', 'SYM', 'ADJUST', 'LAYER_4', 'LAYER_5']
    """
    names = []
    for i in range(count):
        if custom_names and i < len(custom_names) and custom_names[i]:
            names.append(custom_names[i])
        elif i < len(SEMANTIC_LAYER_NAMES):
            names.append(SEMANTIC_LAYER_NAMES[i])
        else:
            names.append(f"LAYER_{i}")
    return names


def layer_id_from_name(name: str) -> Optional[int]:
    """
    Try to extract a layer ID from a layer name.

    Handles formats like:
    - "LAYER_0" -> 0
    - "LAYER_5" -> 5
    - "BASE" -> 0 (if in semantic list)
    - "NAV" -> 1 (if in semantic list)

    Args:
        name: The layer name

    Returns:
        Layer ID or None if not found

    Examples:
        >>> layer_id_from_name("LAYER_0")
        0
        >>> layer_id_from_name("BASE")
        0
        >>> layer_id_from_name("NAV")
        1
        >>> layer_id_from_name("UNKNOWN")
        None
    """
    # Check for LAYER_N format
    match = re.match(r"^LAYER_(\d+)$", name)
    if match:
        return int(match.group(1))

    # Check semantic names
    if name in SEMANTIC_LAYER_NAMES:
        return SEMANTIC_LAYER_NAMES.index(name)

    return None


def is_sequential_layer_name(name: str) -> bool:
    """
    Check if a layer name is a sequential fallback (e.g., "LAYER_0").

    Args:
        name: The layer name to check

    Returns:
        True if the name is sequential, False otherwise
    """
    return bool(re.match(r"^LAYER_\d+$", name))


# ─── Module Info ──────────────────────────────────────────────────────────

__all__ = [
    "SEMANTIC_LAYER_NAMES",
    "DEFAULT_MAX_LAYERS",
    "LayerNameGenerator",
    "parse_keymap_layers",
    "generate_layer_name",
    "generate_layer_names",
    "layer_id_from_name",
    "is_sequential_layer_name",
]
