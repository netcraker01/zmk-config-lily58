"""
JSON Formatter for ZMK Keymaps.

Exports keymaps in structured JSON format with metadata, suitable for
data processing, API responses, or persistence.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..formatter import OutputFormatter


class JSONFormatter(OutputFormatter):
    """
    Formatter for JSON export of keymap data.

    Produces a structured JSON object containing:
    - Metadata: timestamp, version, etc.
    - Raw behaviors: behavior ID list
    - Layers: extracted layers with bindings
    - Statistics: counts and summaries
    """

    def __init__(self, include_raw_behaviors: bool = True):
        """
        Initialize the JSON formatter.

        Args:
            include_raw_behaviors: Whether to include raw behavior IDs in output
        """
        self.include_raw_behaviors = include_raw_behaviors

    def format_binding(
        self, binding: Dict[str, Any], behavior_map: Optional[Dict[int, str]] = None
    ) -> Dict[str, Any]:
        """
        Format a single behavior binding into a JSON-serializable dict.

        Args:
            binding: A dict with keys 'behavior_id', 'param1', 'param2'
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            Dict with binding data (not a string, for JSON structure)
        """
        bid = binding.get("behavior_id", 0)
        p1 = binding.get("param1", 0)
        p2 = binding.get("param2", 0)

        result = {
            "behavior_id": bid,
            "param1": p1,
            "param2": p2,
        }

        # Add behavior name if map is provided
        if behavior_map is not None and bid in behavior_map:
            result["behavior_name"] = behavior_map[bid]

        # Also copy existing behavior_name if present
        if "behavior_name" in binding:
            result["behavior_name"] = binding["behavior_name"]

        return result

    def format_bindings(
        self,
        bindings: List[Dict[str, Any]],
        behavior_map: Optional[Dict[int, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Format multiple bindings at once.

        Args:
            bindings: List of binding dicts
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            List of formatted binding dicts
        """
        return [self.format_binding(b, behavior_map) for b in bindings]

    def format_layer(
        self, layer: Dict[str, Any], behavior_map: Optional[Dict[int, str]] = None
    ) -> Dict[str, Any]:
        """
        Format a single layer with all its bindings.

        Args:
            layer: A dict with keys 'id', 'name', 'bindings'
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            Dict with layer data and formatted bindings
        """
        layer_id = layer.get("id", 0)
        layer_name = layer.get("name", "")
        bindings = layer.get("bindings", [])

        result = {
            "id": layer_id,
            "name": layer_name,
            "bindings": self.format_bindings(bindings, behavior_map),
        }

        return result

    def format_layers(
        self,
        layers: List[Dict[str, Any]],
        behavior_map: Optional[Dict[int, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Format multiple layers at once.

        Args:
            layers: List of layer dicts
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            List of formatted layer dicts
        """
        return [self.format_layer(layer, behavior_map) for layer in layers]

    def format_header(self, keymap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the header/metadata section of the JSON output.

        Args:
            keymap: The complete keymap dict with metadata

        Returns:
            Dict with metadata fields
        """
        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "format": "zmk-keymap-json",
                "version": "1.0",
            },
            "keymapInfo": {
                "availableLayers": keymap.get("availableLayers", 0),
                "maxLayerNameLength": keymap.get("maxLayerNameLength", 0),
                "totalLayers": len(keymap.get("layers", [])),
            },
        }

    def format_footer(self) -> Dict[str, Any]:
        """
        Format the footer/closing section of the JSON output.

        Returns:
            Empty dict (JSON doesn't have a footer concept)
        """
        return {}

    def format(self, keymap: Dict[str, Any]) -> str:
        """
        Format keymap as JSON (implements OutputFormatter protocol).

        Args:
            keymap: The complete keymap dict

        Returns:
            JSON-formatted string
        """
        return self.format_keymap(keymap)

    def format_keymap(
        self,
        keymap: Dict[str, Any],
        behavior_map: Optional[Dict[int, str]] = None,
        include_metadata: bool = True,
    ) -> str:
        """
        Format the complete keymap as JSON.

        Args:
            keymap: The complete keymap dict
            behavior_map: Optional mapping from behavior IDs to names
            include_metadata: Whether to include metadata section

        Returns:
            JSON-formatted string
        """
        output = {}

        if include_metadata:
            header = self.format_header(keymap)
            output.update(header)

        # Format layers
        layers = keymap.get("layers", [])
        output["layers"] = self.format_layers(layers, behavior_map)

        # Add raw behaviors if requested and available
        if self.include_raw_behaviors and "behaviors" in keymap:
            output["rawBehaviors"] = keymap["behaviors"]

        return json.dumps(output, indent=2, ensure_ascii=False)


__all__ = ["JSONFormatter"]
