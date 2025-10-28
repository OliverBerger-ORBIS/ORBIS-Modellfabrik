#!/usr/bin/env python3
"""
Unit tests for sensors_display_utils
Tests normalization functions and IAQ mapping
"""

import pytest

from omf2.ui.ccu.sensors_display_utils import (
    clamp,
    get_iaq_info,
    iaq_color,
    iaq_label,
    iaq_level,
    lux_to_percent,
    normalize_brightness,
    normalize_humidity,
    normalize_pressure,
    normalize_temperature,
    percent_from_range,
)


class TestClamp:
    """Test clamp function"""

    def test_clamp_within_range(self):
        """Test clamping value within range"""
        assert clamp(5.0, 0.0, 10.0) == 5.0
        assert clamp(50.0, 0.0, 100.0) == 50.0

    def test_clamp_below_minimum(self):
        """Test clamping value below minimum"""
        assert clamp(-5.0, 0.0, 10.0) == 0.0
        assert clamp(-100.0, 0.0, 100.0) == 0.0

    def test_clamp_above_maximum(self):
        """Test clamping value above maximum"""
        assert clamp(15.0, 0.0, 10.0) == 10.0
        assert clamp(150.0, 0.0, 100.0) == 100.0

    def test_clamp_at_boundaries(self):
        """Test clamping at exact boundaries"""
        assert clamp(0.0, 0.0, 10.0) == 0.0
        assert clamp(10.0, 0.0, 10.0) == 10.0


class TestPercentFromRange:
    """Test percent_from_range function"""

    def test_percent_from_range_middle(self):
        """Test percentage calculation at middle of range"""
        assert percent_from_range(50.0, 0.0, 100.0) == 50.0
        assert percent_from_range(5.0, 0.0, 10.0) == 50.0

    def test_percent_from_range_boundaries(self):
        """Test percentage calculation at boundaries"""
        assert percent_from_range(0.0, 0.0, 100.0) == 0.0
        assert percent_from_range(100.0, 0.0, 100.0) == 100.0

    def test_percent_from_range_negative_range(self):
        """Test percentage calculation with negative range"""
        assert percent_from_range(0.0, -30.0, 60.0) == pytest.approx(33.33, rel=0.01)
        assert percent_from_range(-30.0, -30.0, 60.0) == 0.0
        assert percent_from_range(60.0, -30.0, 60.0) == 100.0

    def test_percent_from_range_clamping(self):
        """Test that values outside range are clamped"""
        assert percent_from_range(150.0, 0.0, 100.0) == 100.0
        assert percent_from_range(-50.0, 0.0, 100.0) == 0.0

    def test_percent_from_range_invalid_range(self):
        """Test behavior with invalid range (max <= min)"""
        result = percent_from_range(50.0, 100.0, 50.0)
        assert result == 0.0


class TestLuxToPercent:
    """Test lux_to_percent function"""

    def test_lux_to_percent_basic(self):
        """Test basic lux to percent conversion"""
        assert lux_to_percent(0.0, 1000.0) == 0.0
        assert lux_to_percent(500.0, 1000.0) == 50.0
        assert lux_to_percent(1000.0, 1000.0) == 100.0

    def test_lux_to_percent_never_exceeds_100(self):
        """Test that lux never exceeds 100%"""
        assert lux_to_percent(1500.0, 1000.0) == 100.0
        assert lux_to_percent(2000.0, 1000.0) == 100.0
        assert lux_to_percent(10000.0, 1000.0) == 100.0

    def test_lux_to_percent_different_max(self):
        """Test with different max_lux values"""
        assert lux_to_percent(500.0, 500.0) == 100.0
        assert lux_to_percent(1000.0, 2000.0) == 50.0

    def test_lux_to_percent_invalid_max(self):
        """Test behavior with invalid max_lux"""
        # Should use default 1000 when max_lux is invalid
        result = lux_to_percent(500.0, 0.0)
        assert result == 50.0  # Uses default 1000


class TestIAQLevel:
    """Test iaq_level function"""

    def test_iaq_level_good(self):
        """Test IAQ level classification for good air quality"""
        assert iaq_level(0.0) == "good"
        assert iaq_level(25.0) == "good"
        assert iaq_level(50.0) == "good"

    def test_iaq_level_moderate(self):
        """Test IAQ level classification for moderate air quality"""
        assert iaq_level(51.0) == "moderate"
        assert iaq_level(75.0) == "moderate"
        assert iaq_level(100.0) == "moderate"

    def test_iaq_level_unhealthy(self):
        """Test IAQ level classification for unhealthy air quality"""
        assert iaq_level(101.0) == "unhealthy"
        assert iaq_level(125.0) == "unhealthy"
        assert iaq_level(150.0) == "unhealthy"

    def test_iaq_level_hazard(self):
        """Test IAQ level classification for hazardous air quality"""
        assert iaq_level(151.0) == "hazard"
        assert iaq_level(200.0) == "hazard"
        assert iaq_level(500.0) == "hazard"

    def test_iaq_level_custom_config(self):
        """Test IAQ level with custom configuration"""
        custom_config = {"iaq": {"thresholds": {"good": 30, "moderate": 80, "unhealthy": 120}}}
        assert iaq_level(25.0, custom_config) == "good"
        assert iaq_level(50.0, custom_config) == "moderate"
        assert iaq_level(100.0, custom_config) == "unhealthy"
        assert iaq_level(150.0, custom_config) == "hazard"


class TestIAQColor:
    """Test iaq_color function"""

    def test_iaq_color_good(self):
        """Test color for good air quality"""
        assert iaq_color(25.0) == "#28a745"  # Green

    def test_iaq_color_moderate(self):
        """Test color for moderate air quality"""
        assert iaq_color(75.0) == "#ffc107"  # Yellow

    def test_iaq_color_unhealthy(self):
        """Test color for unhealthy air quality"""
        assert iaq_color(125.0) == "#fd7e14"  # Orange

    def test_iaq_color_hazard(self):
        """Test color for hazardous air quality"""
        assert iaq_color(200.0) == "#dc3545"  # Red


class TestIAQLabel:
    """Test iaq_label function"""

    def test_iaq_label_good(self):
        """Test label for good air quality"""
        assert iaq_label(25.0) == "Good"

    def test_iaq_label_moderate(self):
        """Test label for moderate air quality"""
        assert iaq_label(75.0) == "Moderate"

    def test_iaq_label_unhealthy(self):
        """Test label for unhealthy air quality"""
        assert iaq_label(125.0) == "Unhealthy"

    def test_iaq_label_hazard(self):
        """Test label for hazardous air quality"""
        assert iaq_label(200.0) == "Hazardous"


class TestGetIAQInfo:
    """Test get_iaq_info function"""

    def test_get_iaq_info_good(self):
        """Test getting complete IAQ info for good quality"""
        level, color, label = get_iaq_info(25.0)
        assert level == "good"
        assert color == "#28a745"
        assert label == "Good"

    def test_get_iaq_info_moderate(self):
        """Test getting complete IAQ info for moderate quality"""
        level, color, label = get_iaq_info(75.0)
        assert level == "moderate"
        assert color == "#ffc107"
        assert label == "Moderate"

    def test_get_iaq_info_unhealthy(self):
        """Test getting complete IAQ info for unhealthy quality"""
        level, color, label = get_iaq_info(125.0)
        assert level == "unhealthy"
        assert color == "#fd7e14"
        assert label == "Unhealthy"

    def test_get_iaq_info_hazard(self):
        """Test getting complete IAQ info for hazardous quality"""
        level, color, label = get_iaq_info(200.0)
        assert level == "hazard"
        assert color == "#dc3545"
        assert label == "Hazardous"


class TestNormalizeTemperature:
    """Test normalize_temperature function"""

    def test_normalize_temperature_default_range(self):
        """Test temperature normalization with default range (-30 to 60)"""
        assert normalize_temperature(-30.0) == 0.0
        assert normalize_temperature(15.0) == 50.0
        assert normalize_temperature(60.0) == 100.0

    def test_normalize_temperature_clamping(self):
        """Test that temperature normalization clamps values"""
        assert normalize_temperature(-50.0) == 0.0
        assert normalize_temperature(100.0) == 100.0

    def test_normalize_temperature_custom_config(self):
        """Test temperature normalization with custom config"""
        custom_config = {"temperature": {"min": 0.0, "max": 50.0}}
        assert normalize_temperature(0.0, custom_config) == 0.0
        assert normalize_temperature(25.0, custom_config) == 50.0
        assert normalize_temperature(50.0, custom_config) == 100.0


class TestNormalizeHumidity:
    """Test normalize_humidity function"""

    def test_normalize_humidity_valid_range(self):
        """Test humidity normalization for valid range"""
        assert normalize_humidity(0.0) == 0.0
        assert normalize_humidity(50.0) == 50.0
        assert normalize_humidity(100.0) == 100.0

    def test_normalize_humidity_clamping(self):
        """Test humidity normalization clamping"""
        assert normalize_humidity(-10.0) == 0.0
        assert normalize_humidity(110.0) == 100.0
        assert normalize_humidity(200.0) == 100.0


class TestNormalizeBrightness:
    """Test normalize_brightness function"""

    def test_normalize_brightness_default_max(self):
        """Test brightness normalization with default max_lux"""
        assert normalize_brightness(0.0) == 0.0
        assert normalize_brightness(500.0) == 50.0
        assert normalize_brightness(1000.0) == 100.0

    def test_normalize_brightness_never_exceeds_100(self):
        """Test that brightness never exceeds 100%"""
        assert normalize_brightness(1500.0) == 100.0
        assert normalize_brightness(2000.0) == 100.0
        assert normalize_brightness(10000.0) == 100.0

    def test_normalize_brightness_custom_config(self):
        """Test brightness normalization with custom config"""
        custom_config = {"brightness": {"max_lux": 500.0}}
        assert normalize_brightness(0.0, custom_config) == 0.0
        assert normalize_brightness(250.0, custom_config) == 50.0
        assert normalize_brightness(500.0, custom_config) == 100.0
        assert normalize_brightness(1000.0, custom_config) == 100.0


class TestNormalizePressure:
    """Test normalize_pressure function"""

    def test_normalize_pressure_default_range(self):
        """Test pressure normalization with default range (900-1100)"""
        assert normalize_pressure(900.0) == 0.0
        assert normalize_pressure(1000.0) == 50.0
        assert normalize_pressure(1100.0) == 100.0

    def test_normalize_pressure_clamping(self):
        """Test that pressure normalization clamps values"""
        assert normalize_pressure(800.0) == 0.0
        assert normalize_pressure(1200.0) == 100.0

    def test_normalize_pressure_custom_config(self):
        """Test pressure normalization with custom config"""
        custom_config = {"pressure": {"min": 950.0, "max": 1050.0}}
        assert normalize_pressure(950.0, custom_config) == 0.0
        assert normalize_pressure(1000.0, custom_config) == 50.0
        assert normalize_pressure(1050.0, custom_config) == 100.0


class TestIntegration:
    """Integration tests for sensor display utilities"""

    def test_temperature_normalization_realistic_values(self):
        """Test temperature normalization with realistic values"""
        # Room temperature (20°C in -30 to 60 range = 50/90 = 55.56%)
        assert 50.0 < normalize_temperature(20.0) < 60.0
        # Cold weather
        assert 0.0 <= normalize_temperature(-20.0) < 20.0
        # Hot weather
        assert 75.0 < normalize_temperature(40.0) < 85.0

    def test_brightness_never_shows_over_100(self):
        """Test that brightness never shows over 100% for any input"""
        test_values = [0, 100, 500, 1000, 1500, 2000, 5000, 10000]
        for lux in test_values:
            result = normalize_brightness(float(lux))
            assert 0.0 <= result <= 100.0, f"Brightness {result}% exceeds 100% for {lux} lux"

    def test_iaq_traffic_light_transitions(self):
        """Test IAQ transitions between levels"""
        # Test around threshold boundaries
        assert iaq_level(49.0) == "good"
        assert iaq_level(51.0) == "moderate"
        assert iaq_level(99.0) == "moderate"
        assert iaq_level(101.0) == "unhealthy"
        assert iaq_level(149.0) == "unhealthy"
        assert iaq_level(151.0) == "hazard"

    def test_all_normalizations_return_0_to_100(self):
        """Test that all normalization functions return values in 0-100 range"""
        # Test with extreme values
        extreme_values = [-1000, -100, -10, 0, 10, 100, 1000, 10000]

        for val in extreme_values:
            temp_result = normalize_temperature(float(val))
            humidity_result = normalize_humidity(float(val))
            brightness_result = normalize_brightness(float(val))
            pressure_result = normalize_pressure(float(val))

            assert 0.0 <= temp_result <= 100.0
            assert 0.0 <= humidity_result <= 100.0
            assert 0.0 <= brightness_result <= 100.0
            assert 0.0 <= pressure_result <= 100.0
