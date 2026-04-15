"""
Output formatter interface for ZMK keymap data.
"""

from typing import Dict, List, Any, Protocol


class OutputFormatter(Protocol):
    """
    Protocol for keymap output formatters.

    All formatters must implement this interface to ensure
    consistent behavior across different output formats.
    """

    def format(self, keymap: Dict[str, Any]) -> str:
        """
        Format a keymap dictionary into a string representation.

        Args:
            keymap: Keymap dictionary with layers and bindings

        Returns:
            Formatted string representation

        Example:
            >>> formatter = JSONFormatter()
            >>> output = formatter.format(keymap)
            >>> print(output)
            '{"layers": [...]}'
        """
        ...

    def get_extension(self) -> str:
        """
        Get the file extension for this format.

        Returns:
            File extension (e.g., ".json", ".yaml", ".csv", ".keymap")

        Example:
            >>> formatter = JSONFormatter()
            >>> formatter.get_extension()
            '.json'
        """
        ...


def create_formatter(format_name: str) -> OutputFormatter:
    """
    Factory function to create formatters by name.

    Args:
        format_name: Format name ("json", "yaml", "csv", "devicetree", "dt")

    Returns:
        Formatter instance

    Raises:
        ValueError: If format name is unknown

    Example:
        >>> formatter = create_formatter("json")
        >>> isinstance(formatter, JSONFormatter)
        True
    """
    format_name = format_name.lower()

    if format_name in ("json",):
        from .json_formatter import JSONFormatter

        return JSONFormatter()
    elif format_name in ("yaml", "yml"):
        from .yaml_formatter import YAMLFormatter

        return YAMLFormatter()
    elif format_name in ("csv",):
        from .csv_formatter import CSVFormatter

        return CSVFormatter()
    elif format_name in ("devicetree", "dt", "keymap"):
        from .devicetree import DevicetreeFormatter

        return DevicetreeFormatter()
    else:
        raise ValueError(f"Unknown format: {format_name}")


# Import formatter classes for direct access
from .json_formatter import JSONFormatter
from .yaml_formatter import YAMLFormatter
from .csv_formatter import CSVFormatter
from .devicetree import DevicetreeFormatter


__all__ = [
    "OutputFormatter",
    "create_formatter",
    "JSONFormatter",
    "YAMLFormatter",
    "CSVFormatter",
    "DevicetreeFormatter",
]
