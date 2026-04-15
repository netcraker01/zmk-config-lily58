"""
Behavior Resolution Module for ZMK.

This module provides dynamic resolution of ZMK behavior IDs to their names,
with caching support to avoid repeated RPC calls to the firmware.

Behaviors in ZMK are dynamically assigned IDs by the firmware. This module
provides:
- Static fallback mapping for common behaviors
- Dynamic resolution via RPC calls
- Persistent JSON cache for performance
- Behavior details retrieval
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# ─── Constants ─────────────────────────────────────────────────────────────

# Default cache file location
DEFAULT_CACHE_FILE = "behavior_cache.json"

# Common ZMK behaviors and their typical IDs (used as fallback)
STATIC_BEHAVIOR_MAP: Dict[int, str] = {
    1: "bootloader",
    2: "caps_word",
    3: "kp",  # Key Press
    4: "grv_esc",  # Grave/Escape
    5: "key_repeat",
    6: "kt",  # Key Toggle
    7: "mo",  # Momentary Layer
    8: "lt",  # Layer-Tap
    9: "mt",  # Mod-Tap
    10: "none",
    11: "out",  # Output Selection
    12: "sk",  # Sticky Key
    13: "sl",  # Sticky Layer
    14: "studio_unlock",
    15: "sys_reset",
    16: "to",  # To Layer
    17: "tog",  # Toggle Layer
    18: "bt",  # Bluetooth
    19: "enc_key_press",  # Encoder key press
    20: "ext_power",  # External Power
    21: "rgb_ug",  # Underglow (RGB)
    22: "trans",  # Transparent
}

# ─── Behavior Cache ───────────────────────────────────────────────────────


class BehaviorCache:
    """
    Simple persistent cache for behavior mappings.

    Stores behavior ID -> name mappings and behavior details in a JSON file.
    """

    def __init__(self, cache_file: str = DEFAULT_CACHE_FILE):
        """
        Initialize the behavior cache.

        Args:
            cache_file: Path to the cache file
        """
        self.cache_file = Path(cache_file)
        self._cache: Dict[str, Any] = {
            "version": "1.0",
            "last_updated": None,
            "behaviors": {},  # id -> name mapping
            "details": {},  # id -> full details
        }
        self._load()

    def _load(self) -> None:
        """Load cache from file if it exists."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self._cache.update(data)
            except (json.JSONDecodeError, IOError) as e:
                # Corrupt cache, start fresh
                self._cache["behaviors"] = {}
                self._cache["details"] = {}

    def _save(self) -> None:
        """Save cache to file."""
        self._cache["last_updated"] = datetime.now().isoformat()
        with open(self.cache_file, "w") as f:
            json.dump(self._cache, f, indent=2)

    def get_behavior_name(self, behavior_id: int) -> Optional[str]:
        """Get behavior name from cache."""
        return self._cache["behaviors"].get(str(behavior_id))

    def set_behavior_name(self, behavior_id: int, name: str) -> None:
        """Set behavior name in cache."""
        self._cache["behaviors"][str(behavior_id)] = name
        self._save()

    def get_behavior_details(self, behavior_id: int) -> Optional[Dict[str, Any]]:
        """Get full behavior details from cache."""
        return self._cache["details"].get(str(behavior_id))

    def set_behavior_details(self, behavior_id: int, details: Dict[str, Any]) -> None:
        """Set full behavior details in cache."""
        self._cache["details"][str(behavior_id)] = details
        self._cache["behaviors"][str(behavior_id)] = details.get(
            "name", f"beh_{behavior_id}"
        )
        self._save()

    def get_all_behaviors(self) -> Dict[int, str]:
        """Get all cached behavior names."""
        return {int(k): v for k, v in self._cache["behaviors"].items()}

    def clear(self) -> None:
        """Clear all cached behaviors."""
        self._cache["behaviors"] = {}
        self._cache["details"] = {}
        self._save()

    def is_empty(self) -> bool:
        """Check if cache is empty."""
        return len(self._cache["behaviors"]) == 0

    def get_last_updated(self) -> Optional[str]:
        """Get last updated timestamp."""
        return self._cache.get("last_updated")


# ─── Behavior Resolver ────────────────────────────────────────────────────


class BehaviorResolver:
    """
    Resolves ZMK behavior IDs to names with caching support.

    This class provides dynamic resolution of behavior IDs by:
    1. Checking cache first
    2. Querying firmware via RPC (if client provided)
    3. Falling back to static mapping
    4. Caching results for future use
    """

    def __init__(
        self, cache_file: str = DEFAULT_CACHE_FILE, rpc_client: Optional[Any] = None
    ):
        """
        Initialize the behavior resolver.

        Args:
            cache_file: Path to the cache file
            rpc_client: Optional RPC client for querying firmware
        """
        self.cache = BehaviorCache(cache_file)
        self.rpc_client = rpc_client
        self._static_map_loaded = False

    def resolve(self, behavior_id: int) -> str:
        """
        Resolve a behavior ID to its name.

        Resolution order:
        1. Check cache
        2. Query firmware (if RPC client available)
        3. Fall back to static map
        4. Return "beh_{id}" as last resort

        Args:
            behavior_id: The behavior ID to resolve

        Returns:
            The behavior name

        Examples:
            >>> resolver = BehaviorResolver()
            >>> resolver.resolve(3)
            'kp'
            >>> resolver.resolve(999)
            'beh_999'
        """
        # Check cache first
        cached_name = self.cache.get_behavior_name(behavior_id)
        if cached_name:
            return cached_name

        # Try to query firmware
        if self.rpc_client:
            try:
                details = self.get_details(behavior_id)
                if details and "name" in details:
                    return details["name"]
            except Exception:
                # RPC failed, continue to fallback
                pass

        # Load static map if not already loaded
        if not self._static_map_loaded:
            self._load_static_map()

        # Return static name or fallback
        name = STATIC_BEHAVIOR_MAP.get(behavior_id, f"beh_{behavior_id}")

        # Cache the result
        self.cache.set_behavior_name(behavior_id, name)

        return name

    def resolve_many(self, behavior_ids: List[int]) -> Dict[int, str]:
        """
        Resolve multiple behavior IDs efficiently.

        Args:
            behavior_ids: List of behavior IDs to resolve

        Returns:
            Dict mapping behavior_id -> name
        """
        return {bid: self.resolve(bid) for bid in behavior_ids}

    def get_details(self, behavior_id: int) -> Optional[Dict[str, Any]]:
        """
        Get full details for a behavior from the firmware.

        This requires an RPC client to be configured.

        Args:
            behavior_id: The behavior ID to get details for

        Returns:
            Dict with behavior details, or None if not available
        """
        if not self.rpc_client:
            return None

        # Check cache first
        cached = self.cache.get_behavior_details(behavior_id)
        if cached:
            return cached

        # Query firmware
        try:
            # Assuming RPC client has get_behavior_details method
            details = self.rpc_client.get_behavior_details(behavior_id)
            if details:
                self.cache.set_behavior_details(behavior_id, details)
                return details
        except Exception:
            pass

        return None

    def refresh_all(self) -> Dict[int, str]:
        """
        Refresh all behaviors by querying the firmware.

        This clears the cache and queries the firmware for all available behaviors.

        Args:
            None

        Returns:
            Dict of all behavior_id -> name mappings
        """
        if not self.rpc_client:
            # No RPC client, just return cached behaviors
            return self.cache.get_all_behaviors()

        # Clear cache
        self.cache.clear()

        try:
            # Assuming RPC client has get_behaviors_list method
            behavior_ids = self.rpc_client.get_behaviors_list()

            # Resolve all behaviors
            for bid in behavior_ids:
                self.resolve(bid)

            return self.cache.get_all_behaviors()
        except Exception:
            # RPC failed, return cached behaviors
            return self.cache.get_all_behaviors()

    def _load_static_map(self) -> None:
        """Load static behavior map into cache."""
        for bid, name in STATIC_BEHAVIOR_MAP.items():
            if not self.cache.get_behavior_name(bid):
                self.cache.set_behavior_name(bid, name)
        self._static_map_loaded = True

    def get_all_cached(self) -> Dict[int, str]:
        """Get all cached behavior names without querying firmware."""
        # Ensure static map is loaded
        if self.cache.is_empty():
            self._load_static_map()
        return self.cache.get_all_behaviors()

    def clear_cache(self) -> None:
        """Clear the behavior cache."""
        self.cache.clear()
        self._static_map_loaded = False

    def set_rpc_client(self, rpc_client: Any) -> None:
        """Set or update the RPC client for dynamic resolution."""
        self.rpc_client = rpc_client


# ─── Helper Functions ─────────────────────────────────────────────────────


def create_resolver(
    cache_file: str = DEFAULT_CACHE_FILE, rpc_client: Optional[Any] = None
) -> BehaviorResolver:
    """
    Factory function to create a behavior resolver.

    Args:
        cache_file: Path to the cache file
        rpc_client: Optional RPC client for querying firmware

    Returns:
        Configured BehaviorResolver instance
    """
    return BehaviorResolver(cache_file, rpc_client)


def load_static_behaviors() -> Dict[int, str]:
    """Return the static behavior map."""
    return STATIC_BEHAVIOR_MAP.copy()


# ─── Module Info ──────────────────────────────────────────────────────────

__all__ = [
    "DEFAULT_CACHE_FILE",
    "STATIC_BEHAVIOR_MAP",
    "BehaviorCache",
    "BehaviorResolver",
    "create_resolver",
    "load_static_behaviors",
]
