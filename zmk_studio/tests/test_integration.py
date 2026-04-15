"""
Integration tests for ZMK Studio keymap extractor.

Tests the complete flow from extraction to export with all formats.
"""

import pytest
import json
import yaml
from pathlib import Path
from typing import Dict, Any

from zmk_studio import KeymapExtractor
from zmk_studio.extractor import (
    RPCClient,
    RPCError,
    LOCK_STATE_LOCKED,
    LOCK_STATE_UNLOCKED,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────


@pytest.fixture
def sample_keymap() -> Dict[str, Any]:
    """Sample keymap for testing."""
    return {
        "layers": [
            {
                "id": 0,
                "name": "base",
                "bindings": [
                    {
                        "behavior_id": 3,
                        "param1": 0x04,
                        "param2": 0,
                        "behavior_name": "kp",
                        "param1_desc": "A",
                    },
                    {
                        "behavior_id": 3,
                        "param1": 0x05,
                        "param2": 0,
                        "behavior_name": "kp",
                        "param1_desc": "B",
                    },
                    {
                        "behavior_id": 9,
                        "param1": 0x02,
                        "param2": 0x04,
                        "behavior_name": "mt",
                        "param1_desc": "LCTRL",
                        "param2_desc": "A",
                    },
                ],
            },
            {
                "id": 1,
                "name": "nav",
                "bindings": [
                    {
                        "behavior_id": 7,
                        "param1": 0,
                        "param2": 0,
                        "behavior_name": "mo",
                        "param1_desc": "Layer 0",
                    },
                ],
            },
        ],
        "availableLayers": 2,
        "maxLayerNameLength": 20,
    }


@pytest.fixture
def extractor(tmp_path):
    """Create a KeymapExtractor instance with temp cache."""
    cache_file = tmp_path / "test_cache.json"
    return KeymapExtractor(cache_file=str(cache_file), debug=False)


# ─── Integration Tests ───────────────────────────────────────────────────────


class TestKeymapExtractorIntegration:
    """Integration tests for KeymapExtractor."""

    def test_export_all_formats(self, extractor, sample_keymap, tmp_path):
        """Test exporting keymap to all supported formats."""
        formats = ["json", "yaml", "csv", "devicetree"]

        for fmt in formats:
            output_file = tmp_path / f"keymap.{fmt}"

            # Export to format
            output_str = extractor.export(sample_keymap, fmt, str(output_file))

            # Verify file was created
            assert output_file.exists(), f"Output file not created for {fmt}"

            # Verify file content matches returned string
            with open(output_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            assert file_content == output_str, f"File content mismatch for {fmt}"

            # Verify file is not empty
            assert len(output_str) > 0, f"Empty output for {fmt}"

    def test_export_json_format(self, extractor, sample_keymap, tmp_path):
        """Test JSON export format."""
        output_file = tmp_path / "keymap.json"

        # Export
        extractor.export(sample_keymap, "json", str(output_file))

        # Load and verify
        with open(output_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded == sample_keymap
        assert loaded["layers"][0]["name"] == "base"
        assert loaded["layers"][0]["bindings"][0]["behavior_name"] == "kp"

    def test_export_yaml_format(self, extractor, sample_keymap, tmp_path):
        """Test YAML export format."""
        output_file = tmp_path / "keymap.yaml"

        # Export
        extractor.export(sample_keymap, "yaml", str(output_file))

        # Load and verify
        with open(output_file, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)

        assert loaded == sample_keymap
        assert loaded["layers"][0]["name"] == "base"

    def test_export_csv_format(self, extractor, sample_keymap, tmp_path):
        """Test CSV export format."""
        output_file = tmp_path / "keymap.csv"

        # Export
        extractor.export(sample_keymap, "csv", str(output_file))

        # Load and verify
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify CSV has header
        assert "layer" in content
        assert "key_index" in content

        # Verify data rows
        lines = content.strip().split("\n")
        assert len(lines) >= 3  # Header + at least 2 data rows

    def test_export_devicetree_format(self, extractor, sample_keymap, tmp_path):
        """Test devicetree export format."""
        output_file = tmp_path / "keymap.keymap"

        # Export
        extractor.export(sample_keymap, "devicetree", str(output_file))

        # Load and verify
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify devicetree syntax
        assert "&kp" in content or "&mo" in content
        assert "base" in content or "nav" in content

    def test_export_to_stdout(self, extractor, sample_keymap):
        """Test exporting to stdout (no output file)."""
        # Export without output file
        output_str = extractor.export(sample_keymap, "json", None)

        # Verify output is returned as string
        assert isinstance(output_str, str)
        assert len(output_str) > 0

        # Verify it's valid JSON
        loaded = json.loads(output_str)
        assert loaded == sample_keymap

    def test_verify_matching_keymaps(self, extractor, sample_keymap):
        """Test verification of matching keymaps."""
        # Verify identical keymaps
        result = extractor.verify(sample_keymap, sample_keymap)
        assert result is True

    def test_verify_different_keymaps(self, extractor, sample_keymap):
        """Test verification of different keymaps."""
        # Create modified keymap
        modified = json.loads(json.dumps(sample_keymap))
        modified["layers"][0]["bindings"][0]["behavior_id"] = 999

        # Verify different keymaps
        result = extractor.verify(sample_keymap, modified)
        assert result is False

    def test_verify_different_layer_count(self, extractor, sample_keymap):
        """Test verification with different layer counts."""
        # Create keymap with extra layer
        modified = json.loads(json.dumps(sample_keymap))
        modified["layers"].append({"id": 2, "name": "sym", "bindings": []})

        # Verify different layer counts
        result = extractor.verify(sample_keymap, modified)
        assert result is False

    def test_list_behaviors_cached(self, extractor):
        """Test listing behaviors from cache."""
        # List behaviors (should use cache)
        behaviors = extractor.list_behaviors(refresh=False)

        # Verify we get some behaviors
        assert isinstance(behaviors, dict)
        assert len(behaviors) > 0

        # Verify behavior IDs are integers
        for bid in behaviors.keys():
            assert isinstance(bid, int)

        # Verify behavior names are strings
        for name in behaviors.values():
            assert isinstance(name, str)

    def test_clear_cache(self, extractor, tmp_path):
        """Test clearing behavior cache."""
        cache_file = tmp_path / "test_cache.json"

        # Create cache file
        cache_file.write_text('{"behaviors": {"3": "kp"}}')

        # Clear cache
        extractor.clear_cache()

        # Verify cache is cleared
        if cache_file.exists():
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            assert "behaviors" in cache_data
            assert len(cache_data["behaviors"]) == 0

    def test_resolve_layer_names(self, extractor, sample_keymap):
        """Test layer name resolution."""
        # Keymap already has names, but test the resolution logic
        keymap = extractor._resolve_layer_names(sample_keymap)

        # Verify layer names are preserved
        assert keymap["layers"][0]["name"] == "base"
        assert keymap["layers"][1]["name"] == "nav"

    def test_resolve_layer_names_empty(self, extractor):
        """Test layer name resolution with empty names."""
        # Create keymap with empty layer names
        keymap = {
            "layers": [
                {"id": 0, "name": "", "bindings": []},
                {"id": 1, "name": "", "bindings": []},
            ],
            "availableLayers": 2,
            "maxLayerNameLength": 20,
        }

        # Resolve layer names
        resolved = extractor._resolve_layer_names(keymap)

        # Verify semantic names are generated
        assert resolved["layers"][0]["name"] != ""
        assert resolved["layers"][1]["name"] != ""
        assert resolved["layers"][0]["name"] != resolved["layers"][1]["name"]

    def test_resolve_behaviors(self, extractor, sample_keymap):
        """Test behavior resolution in keymap."""
        # Resolve behaviors
        resolved = extractor._resolve_behaviors(sample_keymap)

        # Verify behavior names are added
        for layer in resolved["layers"]:
            for binding in layer["bindings"]:
                assert "behavior_name" in binding
                assert isinstance(binding["behavior_name"], str)

    def test_resolve_parameters_kp(self, extractor):
        """Test parameter resolution for kp behavior."""
        binding = {
            "behavior_id": 3,
            "param1": 0x04,
            "param2": 0,
            "behavior_name": "kp",
        }

        # Resolve parameters
        resolved = extractor._resolve_parameters(binding)

        # Verify parameter description
        assert "param1_desc" in resolved
        assert resolved["param1_desc"] == "kp A"

    def test_resolve_parameters_mo(self, extractor):
        """Test parameter resolution for mo behavior."""
        binding = {
            "behavior_id": 7,
            "param1": 1,
            "param2": 0,
            "behavior_name": "mo",
        }

        # Resolve parameters
        resolved = extractor._resolve_parameters(binding)

        # Verify parameter description
        assert "param1_desc" in resolved
        assert "Layer 1" in resolved["param1_desc"]

    def test_resolve_parameters_lt(self, extractor):
        """Test parameter resolution for lt behavior."""
        binding = {
            "behavior_id": 8,
            "param1": 1,
            "param2": 0x04,
            "behavior_name": "lt",
        }

        # Resolve parameters
        resolved = extractor._resolve_parameters(binding)

        # Verify parameter descriptions
        assert "param1_desc" in resolved
        assert "param2_desc" in resolved
        assert "Layer 1" in resolved["param1_desc"]
        assert "lt A" in resolved["param2_desc"]

    def test_resolve_parameters_mt(self, extractor):
        """Test parameter resolution for mt behavior."""
        binding = {
            "behavior_id": 9,
            "param1": 0x01,
            "param2": 0x04,
            "behavior_name": "mt",
        }

        # Resolve parameters
        resolved = extractor._resolve_parameters(binding)

        # Verify parameter descriptions
        assert "param1_desc" in resolved
        assert "param2_desc" in resolved
        # param1=0x01 = LCTRL, param2=0x04 = A
        assert "LCTRL" in resolved["param1_desc"]
        assert "mt A" in resolved["param2_desc"]

    def test_get_current_keymap(self, extractor, sample_keymap):
        """Test getting current keymap."""
        # Initially should be None
        assert extractor.get_current_keymap() is None

        # Set current keymap
        extractor._current_keymap = sample_keymap

        # Get current keymap
        current = extractor.get_current_keymap()
        assert current == sample_keymap

    def test_context_manager(self, extractor):
        """Test using extractor as context manager."""
        # This test just verifies the context manager interface exists
        # Actual connection testing would require a real keyboard
        assert hasattr(extractor, "__enter__")
        assert hasattr(extractor, "__exit__")


class TestRPCClientIntegration:
    """Integration tests for RPC client."""

    def test_rpc_client_creation(self):
        """Test creating RPC client."""
        client = RPCClient(port=None, baudrate=12500, debug=False)
        assert client is not None
        assert client.serial is not None

    def test_rpc_error_creation(self):
        """Test creating RPC error."""
        error = RPCError(1, "UNLOCK_REQUIRED")
        assert error.error_code == 1
        assert error.error_name == "UNLOCK_REQUIRED"
        assert "UNLOCK_REQUIRED" in str(error)

    def test_lock_state_constants(self):
        """Test lock state constants."""
        assert LOCK_STATE_LOCKED == 0
        assert LOCK_STATE_UNLOCKED == 1


class TestEndToEndFlow:
    """End-to-end integration tests."""

    def test_complete_flow_json(self, extractor, sample_keymap, tmp_path):
        """Test complete flow: extract -> export JSON."""
        # Simulate extraction
        extractor._current_keymap = sample_keymap

        # Export to JSON
        output_file = tmp_path / "output.json"
        extractor.export(sample_keymap, "json", str(output_file))

        # Verify
        assert output_file.exists()
        with open(output_file, "r") as f:
            loaded = json.load(f)
        assert loaded == sample_keymap

    def test_complete_flow_yaml(self, extractor, sample_keymap, tmp_path):
        """Test complete flow: extract -> export YAML."""
        # Simulate extraction
        extractor._current_keymap = sample_keymap

        # Export to YAML
        output_file = tmp_path / "output.yaml"
        extractor.export(sample_keymap, "yaml", str(output_file))

        # Verify
        assert output_file.exists()
        with open(output_file, "r") as f:
            loaded = yaml.safe_load(f)
        assert loaded == sample_keymap

    def test_complete_flow_csv(self, extractor, sample_keymap, tmp_path):
        """Test complete flow: extract -> export CSV."""
        # Simulate extraction
        extractor._current_keymap = sample_keymap

        # Export to CSV
        output_file = tmp_path / "output.csv"
        extractor.export(sample_keymap, "csv", str(output_file))

        # Verify
        assert output_file.exists()
        with open(output_file, "r") as f:
            content = f.read()
        assert "layer" in content
        assert len(content) > 0

    def test_complete_flow_devicetree(self, extractor, sample_keymap, tmp_path):
        """Test complete flow: extract -> export devicetree."""
        # Simulate extraction
        extractor._current_keymap = sample_keymap

        # Export to devicetree
        output_file = tmp_path / "output.keymap"
        extractor.export(sample_keymap, "devicetree", str(output_file))

        # Verify
        assert output_file.exists()
        with open(output_file, "r") as f:
            content = f.read()
        assert len(content) > 0

    def test_multi_format_export(self, extractor, sample_keymap, tmp_path):
        """Test exporting same keymap to multiple formats."""
        formats = ["json", "yaml", "csv", "devicetree"]

        for fmt in formats:
            output_file = tmp_path / f"keymap.{fmt}"
            extractor.export(sample_keymap, fmt, str(output_file))
            assert output_file.exists()

        # Verify all files exist
        for fmt in formats:
            assert (tmp_path / f"keymap.{fmt}").exists()

    def test_verify_after_export(self, extractor, sample_keymap, tmp_path):
        """Test verifying keymap after export."""
        # Export to JSON
        output_file = tmp_path / "keymap.json"
        extractor.export(sample_keymap, "json", str(output_file))

        # Load exported keymap
        with open(output_file, "r") as f:
            loaded = json.load(f)

        # Verify
        assert extractor.verify(sample_keymap, loaded) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
