#!/usr/bin/env python3
"""
ZMK Studio CLI - Command-line interface for keymap extraction.

Provides subcommands for:
- extract: Extract keymap from keyboard
- export: Export keymap to various formats
- list-behaviors: List available behaviors
- verify: Verify keymap integrity
- cache-clear: Clear behavior cache
"""

import sys
import logging
from pathlib import Path
from typing import Optional
import click

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import from zmk_studio package
try:
    from zmk_studio import KeymapExtractor, RPCError
except ImportError:
    # Fallback for development
    sys.path.insert(0, str(Path(__file__).parent))
    from zmk_studio.extractor import KeymapExtractor, RPCError


@click.group()
@click.version_option(version="2.0.0")
@click.option(
    "--port",
    "-p",
    default=None,
    help="Serial port (e.g., COM8 or /dev/ttyACM0). Auto-detect if not specified.",
)
@click.option(
    "--cache-file",
    "-c",
    default="behavior_cache.json",
    help="Path to behavior cache file (default: behavior_cache.json).",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose/debug logging.",
)
@click.pass_context
def cli(ctx: click.Context, port: Optional[str], cache_file: str, verbose: bool):
    """
    ZMK Studio CLI - Extract and export keymaps from ZMK keyboards.

    This tool connects to ZMK keyboards via the ZMK Studio serial protocol
    and extracts keymap data, which can be exported to multiple formats.

    Example usage:
        zmk-studio extract --port COM8 --format json --output keymap.json
        zmk-studio list-behaviors --refresh
        zmk-studio export keymap.json --format yaml --output keymap.yaml
    """
    ctx.ensure_object(dict)
    ctx.obj["port"] = port
    ctx.obj["cache_file"] = cache_file

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")


@cli.command()
@click.option(
    "--format",
    "-f",
    default="json",
    type=click.Choice(
        ["json", "yaml", "csv", "devicetree", "dt"], case_sensitive=False
    ),
    help="Output format (default: json).",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path. If not specified, prints to stdout.",
)
@click.option(
    "--no-unlock",
    is_flag=True,
    help="Do not automatically unlock keyboard if locked.",
)
@click.pass_context
def extract(ctx: click.Context, format: str, output: Optional[str], no_unlock: bool):
    """
    Extract keymap from the keyboard.

    Connects to the keyboard, extracts the keymap, and exports it to the
    specified format.

    Example:
        zmk-studio extract --port COM8 --format json --output keymap.json
    """
    port = ctx.obj["port"]
    cache_file = ctx.obj["cache_file"]

    logger.info(f"Extracting keymap from {port or 'auto-detect'}...")

    # Create extractor
    extractor = KeymapExtractor(
        port=port, cache_file=cache_file, debug=logger.level == logging.DEBUG
    )

    # Extract keymap
    keymap = extractor.extract(auto_unlock=not no_unlock)

    if keymap is None:
        logger.error("Failed to extract keymap")
        sys.exit(1)

    # Export to format
    try:
        output_str = extractor.export(keymap, format, output)

        if output is None:
            # Print to stdout
            click.echo(output_str)
        else:
            logger.info(f"Successfully exported to {output}")

    except Exception as e:
        logger.error(f"Failed to export keymap: {e}")
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    default="json",
    type=click.Choice(
        ["json", "yaml", "csv", "devicetree", "dt"], case_sensitive=False
    ),
    help="Output format (default: json).",
)
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path. If not specified, prints to stdout.",
)
@click.pass_context
def export(ctx: click.Context, input_file: str, format: str, output: Optional[str]):
    """
    Export keymap to a different format.

    Reads a keymap file and exports it to a different format.

    Example:
        zmk-studio export keymap.json --format yaml --output keymap.yaml
    """
    import json
    import yaml

    input_path = Path(input_file)

    # Read input file
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            if input_path.suffix == ".json":
                keymap = json.load(f)
            elif input_path.suffix in (".yaml", ".yml"):
                keymap = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported input format: {input_path.suffix}")
                sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        sys.exit(1)

    # Create extractor (no port needed for export)
    extractor = KeymapExtractor(cache_file=ctx.obj["cache_file"])

    # Export to format
    try:
        output_str = extractor.export(keymap, format, output)

        if output is None:
            # Print to stdout
            click.echo(output_str)
        else:
            logger.info(f"Successfully exported to {output}")

    except Exception as e:
        logger.error(f"Failed to export keymap: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--refresh",
    "-r",
    is_flag=True,
    help="Refresh behaviors from firmware (uses cache if False).",
)
@click.pass_context
def list_behaviors(ctx: click.Context, refresh: bool):
    """
    List all available behaviors.

    Shows behavior IDs and their names. Use --refresh to query the firmware
    directly instead of using the cache.

    Example:
        zmk-studio list-behaviors --refresh
    """
    port = ctx.obj["port"]
    cache_file = ctx.obj["cache_file"]

    logger.info("Listing behaviors...")

    # Create extractor
    extractor = KeymapExtractor(
        port=port, cache_file=cache_file, debug=logger.level == logging.DEBUG
    )

    # List behaviors
    behaviors = extractor.list_behaviors(refresh=refresh)

    if not behaviors:
        logger.warning("No behaviors found")
        sys.exit(1)

    # Print behaviors
    click.echo(f"Found {len(behaviors)} behaviors:")
    click.echo()
    for behavior_id in sorted(behaviors.keys()):
        name = behaviors[behavior_id]
        click.echo(f"  {behavior_id:3d}: {name}")


@cli.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
def verify(file1: str, file2: str):
    """
    Verify that two keymap files are equivalent.

    Compares two keymap files and reports whether they match.

    Example:
        zmk-studio verify keymap1.json keymap2.json
    """
    import json
    import yaml

    def read_keymap(path: str):
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            if p.suffix == ".json":
                return json.load(f)
            elif p.suffix in (".yaml", ".yml"):
                return yaml.safe_load(f)
            else:
                logger.error(f"Unsupported format: {p.suffix}")
                sys.exit(1)

    logger.info(f"Verifying {file1} vs {file2}...")

    # Read keymaps
    keymap1 = read_keymap(file1)
    keymap2 = read_keymap(file2)

    # Create extractor
    extractor = KeymapExtractor()

    # Verify
    if extractor.verify(keymap1, keymap2):
        click.echo("✓ Keymaps match!")
        sys.exit(0)
    else:
        click.echo("✗ Keymaps do not match")
        sys.exit(1)


@cli.command()
@click.pass_context
def cache_clear(ctx: click.Context):
    """
    Clear the behavior cache.

    Deletes the cached behavior mappings, forcing a refresh from the
    firmware on the next extraction.

    Example:
        zmk-studio cache-clear
    """
    cache_file = ctx.obj["cache_file"]

    logger.info(f"Clearing cache: {cache_file}")

    # Create extractor
    extractor = KeymapExtractor(cache_file=cache_file)

    # Clear cache
    extractor.clear_cache()

    click.echo(f"✓ Cache cleared: {cache_file}")


if __name__ == "__main__":
    cli()
