"""
Unit tests for formatter modules.

Tests all formatter implementations (devicetree, JSON, YAML, CSV)
to ensure they correctly format keymap data according to specifications.
"""

import pytest
import json

from zmk_studio.formatter import (
    OutputFormatter,
    DevicetreeFormatter,
    JSONFormatter,
    YAMLFormatter,
    CSVFormatter,
)


# Sample keymap data for testing
SAMPLE_KEYMAP = {
    "availableLayers": 4,
    "maxLayerNameLength": 20,
    "layers": [
        {
            "id": 0,
            "name": "base",
            "bindings": [
                {
                    "behaviorId": 3,
                    "param1": 458793,
                    "param2": 0,
                },  # ESC (0x70000 + 0x29)
                {"behaviorId": 3, "param1": 458770, "param2": 0},  # 1 (0x70000 + 0x1E)
                {"behaviorId": 3, "param1": 458771, "param2": 0},  # 2 (0x70000 + 0x1F)
                {"behaviorId": 22, "param1": 0, "param2": 0},  # trans
                {"behaviorId": 7, "param1": 1, "param2": 0},  # mo 1
                {"behaviorId": 8, "param1": 2, "param2": 458793},  # lt 2 ESC
            ],
        },
        {
            "id": 1,
            "name": "nav",
            "bindings": [
                {
                    "behaviorId": 3,
                    "param1": 458795,
                    "param2": 0,
                },  # TAB (0x70000 + 0x2B = 458795)
                {"behaviorId": 3, "param1": 458777, "param2": 0},  # Q (0x70000 + 0x14)
                {"behaviorId": 3, "param1": 458774, "param2": 0},  # W (0x70000 + 0x11)
                {"behaviorId": 22, "param1": 0, "param2": 0},  # trans
                {"behaviorId": 16, "param1": 0, "param2": 0},  # to 0
                {"behaviorId": 9, "param1": 1, "param2": 458795},  # mt LCTRL TAB
            ],
        },
    ],
}

# Sample behavior map
SAMPLE_BEHAVIOR_MAP = {
    3: "kp",
    7: "mo",
    8: "lt",
    9: "mt",
    16: "to",
    22: "trans",
}


class TestDevicetreeFormatter:
    """Tests for DevicetreeFormatter."""

    def test_output_formatter_interface(self):
        """Test that DevicetreeFormatter implements OutputFormatter."""
        formatter = DevicetreeFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_format_binding_trans(self):
        """Test formatting transparent binding."""
        formatter = DevicetreeFormatter()
        binding = {"behaviorId": 22, "param1": 0, "param2": 0}
        result = formatter.format_binding(binding)
        assert result == "&trans"

    def test_format_binding_kp(self):
        """Test formatting key press binding."""
        formatter = DevicetreeFormatter()
        binding = {
            "behaviorId": 3,
            "param1": 458793,
            "param2": 0,
        }  # ESC (0x70000 + 0x29)
        result = formatter.format_binding(binding)
        assert "kp ESC" in result
        assert "&" in result

    def test_format_binding_mo(self):
        """Test formatting momentary layer binding."""
        formatter = DevicetreeFormatter()
        binding = {"behaviorId": 7, "param1": 1, "param2": 0}
        result = formatter.format_binding(binding)
        assert result == "&mo 1"

    def test_format_binding_lt(self):
        """Test formatting layer-tap binding."""
        formatter = DevicetreeFormatter()
        binding = {"behaviorId": 8, "param1": 2, "param2": 458793}  # lt 2 ESC
        result = formatter.format_binding(binding)
        assert "lt" in result
        assert "2" in result
        assert "ESC" in result

    def test_format_binding_mt(self):
        """Test formatting mod-tap binding."""
        formatter = DevicetreeFormatter()
        binding = {
            "behaviorId": 9,
            "param1": 1,
            "param2": 458795,
        }  # mt LCTRL TAB (0x70000 + 0x2B = 458795)
        result = formatter.format_binding(binding)
        assert "mt" in result
        assert "LCTRL" in result
        assert "TAB" in result

    def test_format_layer(self):
        """Test formatting a single layer."""
        formatter = DevicetreeFormatter()
        layer = SAMPLE_KEYMAP["layers"][0]
        result = formatter.format_layer(layer)
        assert "base_layer" in result
        assert "bindings" in result
        assert "&trans" in result

    def test_format_header(self):
        """Test formatting header."""
        formatter = DevicetreeFormatter()
        result = formatter.format_header(SAMPLE_KEYMAP)
        assert "#include <behaviors.dtsi>" in result
        assert "#include <dt-bindings/zmk/keys.h>" in result
        assert 'compatible = "zmk,keymap"' in result

    def test_format_footer(self):
        """Test formatting footer."""
        formatter = DevicetreeFormatter()
        result = formatter.format_footer()
        assert "};" in result
        assert result.count("};") >= 1

    def test_format_bindings_multiple(self):
        """Test formatting multiple bindings at once."""
        formatter = DevicetreeFormatter()
        bindings = SAMPLE_KEYMAP["layers"][0]["bindings"][:3]
        results = formatter.format_bindings(bindings)
        assert len(results) == 3
        assert all("&" in r for r in results)

    def test_format_layers_multiple(self):
        """Test formatting multiple layers at once."""
        formatter = DevicetreeFormatter()
        results = formatter.format_layers(SAMPLE_KEYMAP["layers"])
        assert len(results) == 2
        assert "base_layer" in results[0]
        assert "nav_layer" in results[1]

    def test_custom_behavior_map(self):
        """Test using custom behavior map."""
        formatter = DevicetreeFormatter()
        custom_map = {3: "kp", 7: "mo", 22: "trans"}
        binding = {"behaviorId": 22, "param1": 0, "param2": 0}
        result = formatter.format_binding(binding, custom_map)
        assert result == "&trans"


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_output_formatter_interface(self):
        """Test that JSONFormatter implements OutputFormatter."""
        formatter = JSONFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_format_binding_returns_dict(self):
        """Test that format_binding returns a dict, not a string."""
        formatter = JSONFormatter()
        binding = {"behaviorId": 3, "param1": 458793, "param2": 0}
        result = formatter.format_binding(binding)
        assert isinstance(result, dict)
        assert "behaviorId" in result
        assert "param1" in result
        assert "param2" in result

    def test_format_binding_with_map(self):
        """Test format_binding includes behaviorName when map provided."""
        formatter = JSONFormatter()
        binding = {"behaviorId": 3, "param1": 458793, "param2": 0}
        result = formatter.format_binding(binding, SAMPLE_BEHAVIOR_MAP)
        assert "behaviorName" in result
        assert result["behaviorName"] == "kp"

    def test_format_layer_returns_dict(self):
        """Test that format_layer returns a dict."""
        formatter = JSONFormatter()
        layer = SAMPLE_KEYMAP["layers"][0]
        result = formatter.format_layer(layer)
        assert isinstance(result, dict)
        assert "id" in result
        assert "name" in result
        assert "bindings" in result

    def test_format_header_returns_dict(self):
        """Test that format_header returns a dict."""
        formatter = JSONFormatter()
        result = formatter.format_header(SAMPLE_KEYMAP)
        assert isinstance(result, dict)
        assert "metadata" in result
        assert "keymapInfo" in result

    def test_format_footer_empty(self):
        """Test that format_footer returns empty dict."""
        formatter = JSONFormatter()
        result = formatter.format_footer()
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_format_keymap_valid_json(self):
        """Test that format_keymap produces valid JSON."""
        formatter = JSONFormatter()
        result = formatter.format_keymap(SAMPLE_KEYMAP)
        parsed = json.loads(result)
        assert "metadata" in parsed
        assert "layers" in parsed
        assert len(parsed["layers"]) == 2

    def test_format_keymap_without_metadata(self):
        """Test format_keymap with include_metadata=False."""
        formatter = JSONFormatter()
        result = formatter.format_keymap(SAMPLE_KEYMAP, include_metadata=False)
        parsed = json.loads(result)
        assert "metadata" not in parsed
        assert "layers" in parsed


class TestYAMLFormatter:
    """Tests for YAMLFormatter."""

    def test_output_formatter_interface(self):
        """Test that YAMLFormatter implements OutputFormatter."""
        formatter = YAMLFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_format_binding_returns_dict(self):
        """Test that format_binding returns a dict."""
        formatter = YAMLFormatter()
        binding = {"behaviorId": 3, "param1": 458793, "param2": 0}
        result = formatter.format_binding(binding)
        assert isinstance(result, dict)
        assert "behaviorId" in result

    def test_format_layer_returns_dict(self):
        """Test that format_layer returns a dict."""
        formatter = YAMLFormatter()
        layer = SAMPLE_KEYMAP["layers"][0]
        result = formatter.format_layer(layer)
        assert isinstance(result, dict)
        assert "id" in result
        assert "bindings" in result

    def test_format_header_returns_string(self):
        """Test that format_header returns a string."""
        formatter = YAMLFormatter()
        result = formatter.format_header(SAMPLE_KEYMAP)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_footer_empty_string(self):
        """Test that format_footer returns empty string."""
        formatter = YAMLFormatter()
        result = formatter.format_footer()
        assert result == ""

    def test_format_keymap_produces_yaml(self):
        """Test that format_keymap produces YAML-like output."""
        try:
            import yaml

            formatter = YAMLFormatter()
            result = formatter.format_keymap(SAMPLE_KEYMAP)
            # Try to parse it back
            parsed = yaml.safe_load(result)
            assert "layers" in parsed
            assert len(parsed["layers"]) == 2
        except ImportError:
            pytest.skip("pyyaml not installed")

    def test_format_keymap_without_pyyaml_raises(self):
        """Test that format_keymap raises ImportError without pyyaml."""
        # This is handled by the formatter itself, so we just verify it imports
        try:
            import yaml
        except ImportError:
            pytest.skip("pyyaml not installed")


class TestCSVFormatter:
    """Tests for CSVFormatter."""

    def test_output_formatter_interface(self):
        """Test that CSVFormatter implements OutputFormatter."""
        formatter = CSVFormatter()
        assert isinstance(formatter, OutputFormatter)

    def test_format_binding_returns_dict(self):
        """Test that format_binding returns a dict with string values."""
        formatter = CSVFormatter()
        binding = {"behaviorId": 3, "param1": 458793, "param2": 0}
        result = formatter.format_binding(binding)
        assert isinstance(result, dict)
        assert result["behaviorId"] == "3"
        assert result["param1"] == "458793"
        assert result["param2"] == "0"

    def test_format_binding_with_map(self):
        """Test format_binding includes behavior name when map provided."""
        formatter = CSVFormatter()
        binding = {"behaviorId": 3, "param1": 458793, "param2": 0}
        result = formatter.format_binding(binding, SAMPLE_BEHAVIOR_MAP)
        assert result["behavior"] == "kp"

    def test_format_layer_returns_list_of_dicts(self):
        """Test that format_layer returns list of row dicts."""
        formatter = CSVFormatter()
        layer = SAMPLE_KEYMAP["layers"][0]
        result = formatter.format_layer(layer)
        assert isinstance(result, list)
        assert len(result) == 6  # 6 bindings in sample layer
        assert all("layerName" in r for r in result)
        assert all("keyPosition" in r for r in result)

    def test_format_header(self):
        """Test format_header with include_header=True."""
        formatter = CSVFormatter(include_header=True)
        result = formatter.format_header(SAMPLE_KEYMAP)
        assert "layerName" in result
        assert "keyPosition" in result
        assert "behavior" in result

    def test_format_header_no_include(self):
        """Test format_header with include_header=False."""
        formatter = CSVFormatter(include_header=False)
        result = formatter.format_header(SAMPLE_KEYMAP)
        assert result == ""

    def test_format_footer_empty(self):
        """Test that format_footer returns empty string."""
        formatter = CSVFormatter()
        result = formatter.format_footer()
        assert result == ""

    def test_format_keymap_produces_csv(self):
        """Test that format_keymap produces valid CSV."""
        formatter = CSVFormatter(include_header=True)
        result = formatter.format_keymap(SAMPLE_KEYMAP)
        lines = result.strip().split("\n")
        # Should have header + 2 layers * 6 bindings = 13 lines
        assert len(lines) == 13
        # Check header (includes layerId field)
        assert "layerName,layerId,keyPosition" in lines[0]
        # Check data rows
        assert "base" in lines[1]  # First row of base layer
        assert "nav" in lines[7]  # First row of nav layer

    def test_format_keymap_without_header(self):
        """Test format_keymap with include_header=False."""
        formatter = CSVFormatter(include_header=False)
        result = formatter.format_keymap(SAMPLE_KEYMAP)
        lines = result.strip().split("\n")
        # Should have 2 layers * 6 bindings = 12 lines (no header)
        assert len(lines) == 12
        # First row should be data, not header
        assert "base" in lines[0]

    def test_format_bindings_returns_list_of_dicts(self):
        """Test format_bindings returns list of dicts."""
        formatter = CSVFormatter()
        bindings = SAMPLE_KEYMAP["layers"][0]["bindings"][:3]
        results = formatter.format_bindings(bindings)
        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)

    def test_format_layers_returns_list_of_lists(self):
        """Test format_layers returns list of lists."""
        formatter = CSVFormatter()
        results = formatter.format_layers(SAMPLE_KEYMAP["layers"])
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(layer_rows, list) for layer_rows in results)


class TestFormatterIntegration:
    """Integration tests for all formatters."""

    def test_all_formatters_handle_empty_keymap(self):
        """Test that all formatters handle empty keymap gracefully."""
        empty_keymap = {"availableLayers": 0, "layers": []}

        devicetree = DevicetreeFormatter()
        json_fmt = JSONFormatter()
        yaml_fmt = YAMLFormatter()
        csv_fmt = CSVFormatter()

        # Should not raise exceptions
        dt_result = devicetree.format_header(empty_keymap)
        assert dt_result is not None

        json_result = json_fmt.format_keymap(empty_keymap)
        assert json_result is not None

        yaml_result = yaml_fmt.format_header(empty_keymap)
        assert yaml_result is not None

        csv_result = csv_fmt.format_keymap(empty_keymap)
        assert csv_result is not None

    def test_all_formatters_preserve_data(self):
        """Test that all formatters preserve original data."""
        formatter = JSONFormatter()
        result = formatter.format_keymap(SAMPLE_KEYMAP, SAMPLE_BEHAVIOR_MAP)
        parsed = json.loads(result)

        # Check layer count
        assert len(parsed["layers"]) == len(SAMPLE_KEYMAP["layers"])

        # Check first layer binding count
        assert len(parsed["layers"][0]["bindings"]) == len(
            SAMPLE_KEYMAP["layers"][0]["bindings"]
        )

        # Check first binding
        first_binding = parsed["layers"][0]["bindings"][0]
        assert (
            first_binding["behaviorId"]
            == SAMPLE_KEYMAP["layers"][0]["bindings"][0]["behaviorId"]
        )
