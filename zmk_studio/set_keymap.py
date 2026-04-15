"""
Set Keymap Command

Sets a keymap configuration to the keyboard via ZMK Studio protocol.
"""

import argparse
import logging
from pathlib import Path

from zmk_studio.extractor.keymap_extractor import KeymapExtractor

logger = logging.getLogger(__name__)


def set_keymap_from_file(
    input_file: str,
    port: str = "auto",
    debug: bool = False,
):
    """
    Load a keymap file and set it to the keyboard.

    Args:
        input_file: Path to keymap file (JSON format from extraction)
        port: Serial port (auto to detect)
        debug: Enable debug logging
    """
    # Load input keymap
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        return False

    import json

    with open(input_file, "r") as f:
        input_keymap = json.load(f)

    logger.info(f"Loaded keymap from {input_file}")
    logger.info(f"  Layers: {len(input_keymap.get('layers', []))}")

    # Create extractor
    extractor = KeymapExtractor(port=port, debug=debug)

    # Connect to keyboard
    if not extractor.rpc_client.connect():
        logger.error("Failed to connect to keyboard")
        return False

    try:
        # Get current keymap from keyboard (in correct binary format)
        logger.info("Getting current keymap from keyboard...")
        current_keymap = extractor.rpc_client.get_keymap()

        if current_keymap is None:
            logger.error("Failed to get current keymap")
            return False

        # TODO: Modify current_keymap with input_keymap
        # For now, just show what would be sent
        logger.info("Current keymap structure:")
        logger.info(f"  Layers: {len(current_keymap.get('layers', []))}")

        # Check if input matches current
        current_layers = len(current_keymap.get("layers", []))
        input_layers = len(input_keymap.get("layers", []))

        if current_layers != input_layers:
            logger.warning(
                f"Layer count mismatch: current={current_layers}, input={input_layers}"
            )

        logger.warning("Keymap modification not yet implemented - extraction only")
        logger.warning("The protocol supports set_keymap with save_changes=True")
        logger.warning("But parsing devicetree to binary format is complex")
        logger.warning("For now, you can:")
        logger.warning("  1. Extract current keymap")
        logger.warning("  2. Edit the JSON")
        logger.warning("  3. Use ZMK Studio app to upload")

        return True

    except Exception as e:
        logger.error(f"Error setting keymap: {e}")
        return False
    finally:
        extractor.rpc_client.disconnect()


def main():
    """CLI entry point for set_keymap command."""
    parser = argparse.ArgumentParser(
        description="Set ZMK keymap to keyboard via serial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="auto",
        help="Serial port (default: auto-detect)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Keymap JSON file to upload",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    success = set_keymap_from_file(
        input_file=args.input_file,
        port=args.port,
        debug=args.verbose,
    )

    if success:
        logger.info("Keymap set complete")
    else:
        logger.error("Keymap set failed")


if __name__ == "__main__":
    main()
