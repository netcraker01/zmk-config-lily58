"""
Keymap Extractor - Main extraction and export functionality.

Integrates protocol, mapping, and formatter modules into a unified API.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from .rpc_client import RPCClient, RPCError, LOCK_STATE_LOCKED, LOCK_STATE_UNLOCKED
from zmk_studio.mapping import BehaviorResolver, LayerNameGenerator
from zmk_studio.formatter import create_formatter

logger = logging.getLogger(__name__)


class KeymapExtractor:
    """
    Main keymap extraction and export class.

    Provides high-level API for:
    - Extracting keymaps from ZMK firmware
    - Resolving behavior names and parameters
    - Exporting to multiple formats (JSON, YAML, CSV, devicetree)
    - Managing behavior cache
    """

    def __init__(
        self,
        port: Optional[str] = None,
        cache_file: str = "behavior_cache.json",
        debug: bool = False,
    ):
        """
        Initialize the keymap extractor.

        Args:
            port: Serial port path (e.g., "COM8" or "/dev/ttyACM0")
            cache_file: Path to behavior cache file
            debug: Enable debug logging
        """
        self.port = port
        self.cache_file = cache_file
        self.debug = debug

        # Initialize RPC client
        self.rpc_client = RPCClient(port=port, debug=debug)

        # Initialize behavior resolver with RPC client for dynamic resolution
        self.behavior_resolver = BehaviorResolver(
            cache_file=cache_file, rpc_client=self.rpc_client
        )

        # Initialize layer name generator
        self.layer_name_generator = LayerNameGenerator()

        # Cache for extracted keymap
        self._current_keymap: Optional[Dict[str, Any]] = None

        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)

    def extract(
        self, port: Optional[str] = None, auto_unlock: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Extract keymap from the keyboard.

        Args:
            port: Override port (uses default if None)
            auto_unlock: Automatically unlock keyboard if locked

        Returns:
            Keymap dictionary, or None on error

        Example:
            >>> extractor = KeymapExtractor()
            >>> keymap = extractor.extract(port="COM8")
            >>> print(keymap["layers"][0]["name"])
            'base'
        """
        if port:
            self.port = port
            # Update RPC client port
            self.rpc_client.serial.port = port

        logger.info("Starting keymap extraction...")

        # Connect to keyboard
        if not self.rpc_client.connect():
            logger.error("Failed to connect to keyboard")
            return None

        try:
            # Check lock state
            lock_state = self.rpc_client.get_lock_state()

            # Unlock if necessary
            if lock_state == LOCK_STATE_LOCKED and auto_unlock:
                logger.info("Keyboard is locked, attempting to unlock...")
                if not self.rpc_client.unlock():
                    logger.error("Failed to unlock keyboard")
                    return None

            # Extract keymap
            keymap = self.rpc_client.get_keymap()
            if keymap is None:
                logger.error("Failed to extract keymap")
                return None

            # Resolve layer names
            keymap = self._resolve_layer_names(keymap)

            # Resolve behavior names in bindings
            keymap = self._resolve_behaviors(keymap)

            # Cache the keymap
            self._current_keymap = keymap

            logger.info(
                f"Successfully extracted keymap with {len(keymap['layers'])} layers"
            )

            return keymap

        except RPCError as e:
            logger.error(f"RPC error during extraction: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {e}")
            return None
        finally:
            self.rpc_client.disconnect()

    def export(
        self, keymap: Dict[str, Any], format: str, output: Optional[str] = None
    ) -> str:
        """
        Export keymap to a specific format.

        Args:
            keymap: Keymap dictionary
            format: Output format ("json", "yaml", "csv", "devicetree", "dt")
            output: Optional output file path (if None, returns string)

        Returns:
            Formatted keymap string

        Example:
            >>> extractor = KeymapExtractor()
            >>> keymap = extractor.extract()
            >>> json_output = extractor.export(keymap, "json")
            >>> print(json_output[:50])
            {
              "layers": [
        """
        logger.info(f"Exporting keymap to {format} format...")

        # Create formatter
        formatter = create_formatter(format)

        # Format keymap
        output_str = formatter.format(keymap)

        # Write to file if output path specified
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                f.write(output_str)
            logger.info(f"Exported to {output}")
        else:
            logger.info("Export complete")

        return output_str

    def list_behaviors(self, refresh: bool = False) -> Dict[int, str]:
        """
        List all available behaviors.

        Args:
            refresh: Force refresh from firmware (uses cache if False)

        Returns:
            Dict mapping behavior_id -> behavior_name

        Example:
            >>> extractor = KeymapExtractor()
            >>> behaviors = extractor.list_behaviors()
            >>> print(behaviors[3])
            'kp'
        """
        logger.info("Listing behaviors...")

        if refresh:
            logger.info("Refreshing behaviors from firmware...")
            if not self.rpc_client.connect():
                logger.error("Failed to connect to keyboard")
                return {}

            try:
                # Get all behavior IDs
                behavior_ids = self.rpc_client.get_behaviors()
                if behavior_ids is None:
                    logger.error("Failed to get behavior list")
                    return {}

                # Resolve all behaviors (this will cache them)
                behaviors = {}
                for bid in behavior_ids:
                    name = self.behavior_resolver.resolve(bid)
                    behaviors[bid] = name

                logger.info(f"Found {len(behaviors)} behaviors")
                return behaviors

            except RPCError as e:
                logger.error(f"RPC error: {e}")
                return {}
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return {}
            finally:
                self.rpc_client.disconnect()
        else:
            # Return cached behaviors
            behaviors = self.behavior_resolver.get_all_cached()
            logger.info(f"Using cached behaviors: {len(behaviors)} behaviors")
            return behaviors

    def verify(self, keymap1: Dict[str, Any], keymap2: Dict[str, Any]) -> bool:
        """
        Verify that two keymaps are equivalent.

        Args:
            keymap1: First keymap dictionary
            keymap2: Second keymap dictionary

        Returns:
            True if keymaps match, False otherwise

        Example:
            >>> extractor = KeymapExtractor()
            >>> keymap1 = extractor.extract()
            >>> keymap2 = extractor.extract()
            >>> extractor.verify(keymap1, keymap2)
            True
        """
        logger.info("Verifying keymaps...")

        # Check number of layers
        layers1 = keymap1.get("layers", [])
        layers2 = keymap2.get("layers", [])

        if len(layers1) != len(layers2):
            logger.error(f"Layer count mismatch: {len(layers1)} vs {len(layers2)}")
            return False

        # Check each layer
        for i, (layer1, layer2) in enumerate(zip(layers1, layers2)):
            if layer1.get("id") != layer2.get("id"):
                logger.error(
                    f"Layer {i} ID mismatch: {layer1.get('id')} vs {layer2.get('id')}"
                )
                return False

            bindings1 = layer1.get("bindings", [])
            bindings2 = layer2.get("bindings", [])

            if len(bindings1) != len(bindings2):
                logger.error(
                    f"Layer {i} binding count mismatch: {len(bindings1)} vs {len(bindings2)}"
                )
                return False

            # Check each binding
            for j, (b1, b2) in enumerate(zip(bindings1, bindings2)):
                if b1 != b2:
                    logger.error(f"Layer {i}, key {j} binding mismatch")
                    return False

        logger.info("Keymaps match!")
        return True

    def clear_cache(self) -> None:
        """Clear the behavior cache."""
        logger.info("Clearing behavior cache...")
        self.behavior_resolver.clear_cache()
        logger.info("Cache cleared")

    def _resolve_layer_names(self, keymap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve layer names using semantic naming.

        Args:
            keymap: Raw keymap dictionary

        Returns:
            Keymap dictionary with resolved layer names
        """
        logger.debug("Resolving layer names...")

        # Collect original layer names
        original_names = {}
        for layer in keymap.get("layers", []):
            layer_id = layer.get("id", 0)
            original_name = layer.get("name", "")
            # Only use original name if it's non-empty
            if original_name:
                original_names[layer_id] = original_name

        # Update layer name generator with original names
        self.layer_name_generator.load_original_names(original_names)

        # Generate layer names
        for layer in keymap.get("layers", []):
            layer_id = layer.get("id", 0)
            original_name = layer.get("name", "")

            # Use original name if available, otherwise generate semantic name
            if original_name:
                layer["name"] = original_name
            else:
                layer["name"] = self.layer_name_generator.generate_name(layer_id)

        return keymap

    def _resolve_behaviors(self, keymap: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve behavior IDs to names in all bindings.

        Args:
            keymap: Raw keymap dictionary

        Returns:
            Keymap dictionary with resolved behavior names
        """
        logger.debug("Resolving behaviors...")

        # Collect all behavior IDs
        behavior_ids = set()
        for layer in keymap.get("layers", []):
            for binding in layer.get("bindings", []):
                behavior_ids.add(binding.get("behavior_id", 0))

        # Resolve all behaviors
        resolved_names = self.behavior_resolver.resolve_many(list(behavior_ids))

        # Add resolved names to bindings
        for layer in keymap.get("layers", []):
            for binding in layer.get("bindings", []):
                behavior_id = binding.get("behavior_id", 0)
                binding["behavior_name"] = resolved_names.get(
                    behavior_id, f"beh_{behavior_id}"
                )

                # Also resolve parameter descriptions
                binding = self._resolve_parameters(binding)

        return keymap

    def _resolve_parameters(self, binding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve binding parameters to human-readable descriptions.

        Args:
            binding: Binding dictionary with behavior_id, param1, param2

        Returns:
            Binding dictionary with parameter descriptions
        """
        behavior_id = binding.get("behavior_id", 0)
        behavior_name = binding.get("behavior_name", "")
        param1 = binding.get("param1", 0)
        param2 = binding.get("param2", 0)

        # Resolve based on behavior type
        if behavior_name == "kp":
            # Key press: param1 is keycode (need to add KEYCODE_BASE offset)
            from zmk_studio.mapping.keycodes import KEYCODE_BASE, keycode_name_only

            binding["param1_desc"] = f"kp {keycode_name_only(param1 + KEYCODE_BASE)}"
        elif behavior_name == "mo":
            # Momentary layer: param1 is layer ID
            binding["param1_desc"] = f"Layer {param1}"
        elif behavior_name == "lt":
            # Layer-tap: param1 is layer ID, param2 is keycode (need to add KEYCODE_BASE offset)
            from zmk_studio.mapping.keycodes import KEYCODE_BASE, keycode_name_only

            binding["param1_desc"] = f"Layer {param1}"
            binding["param2_desc"] = f"lt {keycode_name_only(param2 + KEYCODE_BASE)}"
        elif behavior_name == "mt":
            # Mod-tap: param1 is modifier bitmask, param2 is keycode (need to add KEYCODE_BASE offset)
            from zmk_studio.mapping.modifiers import format_modifiers_from_bitmask
            from zmk_studio.mapping.keycodes import KEYCODE_BASE, keycode_name_only

            binding["param1_desc"] = format_modifiers_from_bitmask(param1)
            binding["param2_desc"] = f"mt {keycode_name_only(param2 + KEYCODE_BASE)}"
        elif behavior_name in ("to", "tog"):
            # To layer / Toggle layer: param1 is layer ID
            binding["param1_desc"] = f"Layer {param1}"

        return binding

    def get_current_keymap(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently extracted keymap.

        Returns:
            Keymap dictionary or None if not yet extracted
        """
        return self._current_keymap

    def __enter__(self):
        """Context manager entry."""
        self.rpc_client.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.rpc_client.disconnect()


__all__ = ["KeymapExtractor"]
