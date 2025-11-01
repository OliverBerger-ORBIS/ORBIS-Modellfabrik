#!/usr/bin/env python3
"""
Tests for improved brightness normalization with logarithmic scale
Tests the new lux-to-percent conversion for LDR/BME680 sensors
"""

import math

import pytest

from omf2.ui.ccu.sensors_display_utils import lux_to_percent, normalize_brightness


class TestBrightnessNormalization:
    """Test brightness normalization with logarithmic scale"""

    def test_lux_to_percent_basic_ranges(self):
        """Test basic lux to percent conversion with new logarithmic scale"""
        # Test key ranges with 65000 max_lux (from sensors_display.yml)
        # Note: Logarithmic scale gives different percentages than linear ranges
        test_cases = [
            # (lux_value, expected_percent_range_min, expected_percent_range_max, description)
            (0, 0, 0, "Zero lux"),
            (25, 0, 35, "Dunkel, Nacht (0-50 lx) - logarithmic scale"),
            (50, 0, 40, "Dunkel, Nacht (0-50 lx) - logarithmic scale"),
            (250, 20, 50, "Innenraum, gedämpft (50-500 lx) - logarithmic scale"),
            (500, 30, 60, "Innenraum, gedämpft (50-500 lx) - logarithmic scale"),
            (1000, 40, 70, "Normale Raumbeleuchtung (500-2000 lx) - logarithmic scale"),
            (2000, 50, 80, "Normale Raumbeleuchtung (500-2000 lx) - logarithmic scale"),
            (5000, 60, 90, "Helles Zimmer (2000-10000 lx) - logarithmic scale"),
            (10000, 70, 95, "Helles Zimmer (2000-10000 lx) - logarithmic scale"),
            (20000, 80, 100, "Draußen, bewölkt (10000-30000 lx) - logarithmic scale"),
            (30000, 85, 100, "Draußen, bewölkt (10000-30000 lx) - logarithmic scale"),
            (50000, 90, 100, "Sonnig, pralle Sonne (30000-100000 lx) - logarithmic scale"),
            (65000, 95, 100, "Sonnig, pralle Sonne (30000-100000 lx) - logarithmic scale"),
        ]

        for lux, min_percent, max_percent, description in test_cases:
            percent = lux_to_percent(lux, 65000.0)
            assert (
                min_percent <= percent <= max_percent
            ), f"{description}: {lux} lux -> {percent}% (expected {min_percent}-{max_percent}%)"

    def test_lux_to_percent_logarithmic_scale(self):
        """Test that the logarithmic scale provides better distribution"""
        # Test that logarithmic scale gives more realistic distribution
        # compared to linear scale

        # Linear scale would give: 1000/65000 * 100 = 1.54%
        # Logarithmic scale should give higher percentage for low values
        percent_1000 = lux_to_percent(1000, 65000.0)
        assert percent_1000 > 5, f"1000 lux should be > 5% with logarithmic scale, got {percent_1000}%"

        # Test that very high values don't immediately hit 100%
        percent_30000 = lux_to_percent(30000, 65000.0)
        assert percent_30000 < 100, f"30000 lux should be < 100% with logarithmic scale, got {percent_30000}%"

        # Test that 65000 lux gives exactly 100%
        percent_65000 = lux_to_percent(65000, 65000.0)
        assert abs(percent_65000 - 100.0) < 0.1, f"65000 lux should be ~100%, got {percent_65000}%"

    def test_lux_to_percent_edge_cases(self):
        """Test edge cases for lux to percent conversion"""
        # Zero lux
        assert lux_to_percent(0, 65000.0) == 0.0

        # Negative lux (should be clamped to 0)
        assert lux_to_percent(-100, 65000.0) == 0.0

        # Very large lux (should be clamped to 100)
        assert lux_to_percent(100000, 65000.0) == 100.0

        # Invalid max_lux (should use default)
        percent = lux_to_percent(1000, 0)
        assert percent > 0, "Should use default max_lux when invalid value provided"

    def test_lux_to_percent_mathematical_correctness(self):
        """Test mathematical correctness of logarithmic formula"""
        # Test the formula: log(1 + lux) / log(1 + max_lux) * 100
        lux = 1000
        max_lux = 65000

        expected_percent = (math.log(1 + lux) / math.log(1 + max_lux)) * 100.0
        actual_percent = lux_to_percent(lux, max_lux)

        assert (
            abs(expected_percent - actual_percent) < 0.001
        ), f"Mathematical formula mismatch: expected {expected_percent}, got {actual_percent}"

    def test_normalize_brightness_with_config(self):
        """Test normalize_brightness function with configuration"""
        # Test with custom config
        config = {"brightness": {"max_lux": 65000.0, "unit": "lux"}}

        percent = normalize_brightness(1000, config)
        assert 0 <= percent <= 100, f"Normalized brightness should be 0-100%, got {percent}%"

        # Test with default config (should use 65000)
        percent_default = normalize_brightness(1000, None)
        assert 0 <= percent_default <= 100, f"Default config brightness should be 0-100%, got {percent_default}%"

    def test_brightness_percentage_ranges(self):
        """Test that brightness percentages match the specified ranges"""
        # Test the specific percentage ranges from the specification
        ranges = [
            (0, 5, "Dunkel, Nacht"),
            (5, 15, "Innenraum, gedämpft"),
            (15, 30, "Normale Raumbeleuchtung"),
            (30, 60, "Helles Zimmer"),
            (60, 80, "Draußen, bewölkt"),
            (80, 100, "Sonnig, pralle Sonne"),
        ]

        for min_percent, max_percent, description in ranges:
            # Find a lux value that should fall in this range
            # We'll test the middle of each range
            middle_percent = (min_percent + max_percent) / 2

            # Reverse calculate lux from percentage for testing
            # percent = log(1 + lux) / log(1 + 65000) * 100
            # lux = (1 + 65000)^(percent/100) - 1
            lux = (1 + 65000) ** (middle_percent / 100) - 1

            # Test that this lux value gives the expected percentage
            calculated_percent = lux_to_percent(lux, 65000.0)
            assert (
                min_percent <= calculated_percent <= max_percent
            ), f"{description}: {lux} lux -> {calculated_percent}% (expected {min_percent}-{max_percent}%)"

    def test_brightness_consistency(self):
        """Test that brightness normalization is consistent"""
        # Test that same input gives same output
        lux = 5000
        percent1 = lux_to_percent(lux, 65000.0)
        percent2 = lux_to_percent(lux, 65000.0)
        assert percent1 == percent2, "Same input should give same output"

        # Test that higher lux gives higher percentage
        percent_low = lux_to_percent(1000, 65000.0)
        percent_high = lux_to_percent(10000, 65000.0)
        assert percent_low < percent_high, "Higher lux should give higher percentage"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
