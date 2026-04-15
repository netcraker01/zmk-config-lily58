"""
CSV Formatter for ZMK Keymaps.

Exports keymaps in flat CSV format, suitable for analysis in spreadsheet
applications like Excel, Google Sheets, or data processing tools.
"""

from typing import Dict, List, Any, Optional
from csv import writer as csv_writer
from io import StringIO

from ..formatter import OutputFormatter


class CSVFormatter(OutputFormatter):
    """
    Formatter for CSV export of keymap data.

    Produces a flat CSV file with one row per binding:
    - Headers: layer_name, key_position, behavior, param1, param2, devicetree_binding
    - Suitable for data analysis, filtering, and visualization
    """

    def __init__(self, include_header: bool = True):
        """
        Initialize the CSV formatter.

        Args:
            include_header: Whether to include column headers in output
        """
        self.include_header = include_header

    def format_binding(
        self, binding: Dict[str, Any], behavior_map: Optional[Dict[int, str]] = None
    ) -> Dict[str, str]:
        """
        Format a single behavior binding into a CSV row dict.

        Args:
            binding: A dict with keys 'behavior_id', 'param1', 'param2'
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            Dict with formatted binding data for CSV
        """
        bid = binding.get("behavior_id", 0)
        p1 = binding.get("param1", 0)
        p2 = binding.get("param2", 0)

        result = {
            "behaviorId": str(bid),
            "param1": str(p1),
            "param2": str(p2),
        }

        # Add behavior name if map is provided
        if behavior_map is not None and bid in behavior_map:
            result["behavior"] = behavior_map[bid]
        else:
            result["behavior"] = f"beh_{bid}"

        return result

    def format_layer(
        self, layer: Dict[str, Any], behavior_map: Optional[Dict[int, str]] = None
    ) -> List[Dict[str, str]]:
        """
        Format a single layer with all its bindings as CSV rows.

        Args:
            layer: A dict with keys 'id', 'name', 'bindings'
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            List of dicts, one per binding, with layer and position info
        """
        layer_id = layer.get("id", 0)
        layer_name = layer.get("name", f"layer_{layer_id}")
        bindings = layer.get("bindings", [])

        rows = []
        for pos, binding in enumerate(bindings):
            row = self.format_binding(binding, behavior_map)
            row["layerName"] = layer_name
            row["layerId"] = str(layer_id)
            row["keyPosition"] = str(pos)
            rows.append(row)

        return rows

    def format_header(self, keymap: Dict[str, Any]) -> str:
        """
        Format the header/metadata section of the CSV output.

        Args:
            keymap: The complete keymap dict with metadata

        Returns:
            CSV header row string (or empty if include_header is False)
        """
        if self.include_header:
            return "layerName,layerId,keyPosition,behavior,behaviorId,param1,param2"
        return ""

    def format_footer(self) -> str:
        """
        Format the footer/closing section of the CSV output.

        Returns:
            Empty string (CSV doesn't have a footer concept)
        """
        return ""

    def format(self, keymap: Dict[str, Any]) -> str:
        """
        Format keymap as CSV (implements OutputFormatter protocol).

        Args:
            keymap: The complete keymap dict

        Returns:
            CSV-formatted string
        """
        return self.format_keymap(keymap)

    def format_keymap(
        self,
        keymap: Dict[str, Any],
        behavior_map: Optional[Dict[int, str]] = None,
        include_metadata: bool = True,
    ) -> str:
        """
        Format the complete keymap as CSV.

        Args:
            keymap: The complete keymap dict
            behavior_map: Optional mapping from behavior IDs to names
            include_metadata: Ignored for CSV (always flat structure)

        Returns:
            CSV-formatted string
        """
        output = StringIO()

        # Write header
        if self.include_header:
            header_row = [
                "layerName",
                "layerId",
                "keyPosition",
                "behavior",
                "behaviorId",
                "param1",
                "param2",
            ]
            writer = csv_writer(output, lineterminator="\n")
            writer.writerow(header_row)

        # Write all bindings
        layers = keymap.get("layers", [])
        writer = csv_writer(output, lineterminator="\n")

        for layer in layers:
            rows = self.format_layer(layer, behavior_map)
            for row in rows:
                writer.writerow(
                    [
                        row["layerName"],
                        row["layerId"],
                        row["keyPosition"],
                        row["behavior"],
                        row["behaviorId"],
                        row["param1"],
                        row["param2"],
                    ]
                )

        return output.getvalue()

    def format_bindings(
        self,
        bindings: List[Dict[str, Any]],
        behavior_map: Optional[Dict[int, str]] = None,
    ) -> List[Dict[str, str]]:
        """
        Format multiple bindings at once.

        Args:
            bindings: List of binding dicts
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            List of formatted binding dicts
        """
        return [self.format_binding(b, behavior_map) for b in bindings]

    def format_layers(
        self,
        layers: List[Dict[str, Any]],
        behavior_map: Optional[Dict[int, str]] = None,
    ) -> List[List[Dict[str, str]]]:
        """
        Format multiple layers at once.

        Args:
            layers: List of layer dicts
            behavior_map: Optional mapping from behavior IDs to names

        Returns:
            List of lists of rows (one list per layer)
        """
        return [self.format_layer(layer, behavior_map) for layer in layers]


__all__ = ["CSVFormatter"]
