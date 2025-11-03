#!/usr/bin/env python3
"""
Tests for AQ (Air Quality Score) Display Functionality
Tests the three-block system and Ampel logic
"""


import pytest

from omf2.ui.ccu.sensors_display_utils import (
    aq_color,
    aq_label,
    aq_level,
    get_aq_info,
    normalize_aq,
)


class TestAQDisplay:
    """Test AQ display functionality"""

    def test_aq_level_classification(self):
        """Test AQ level classification"""
        # Gut (0-1)
        assert aq_level(0.0) == "sehr_gut"
        assert aq_level(0.5) == "sehr_gut"
        assert aq_level(1.0) == "sehr_gut"

        # Mittel (1.1-3.0)
        assert aq_level(1.1) == "gut"
        assert aq_level(2.0) == "gut"
        assert aq_level(2.5) == "maessig"
        assert aq_level(3.0) == "maessig"

        # Schlecht (3.1-5.0)
        assert aq_level(3.1) == "schlecht"
        assert aq_level(4.0) == "schlecht"
        assert aq_level(4.5) == "sehr_schlecht"
        assert aq_level(5.0) == "sehr_schlecht"

    def test_aq_color_assignment(self):
        """Test AQ color assignment"""
        # Gut (0-1) - Green variations
        assert aq_color(0.5) == "#28a745"  # sehr_gut
        assert aq_color(1.0) == "#90EE90"  # sehr_gut (hellgrün)

        # Mittel (1.1-3.0) - Yellow/Orange variations
        assert aq_color(1.5) == "#90EE90"  # gut (hellgrün)
        assert aq_color(2.5) == "#ffc107"  # maessig (gelb)
        assert aq_color(3.0) == "#fd7e14"  # maessig (orange)

        # Schlecht (3.1-5.0) - Orange/Red
        assert aq_color(3.5) == "#fd7e14"  # schlecht (orange)
        assert aq_color(4.5) == "#dc3545"  # sehr_schlecht (rot)

    def test_aq_label_assignment(self):
        """Test AQ label assignment - returns i18n keys"""
        # Excellent range [0, 1) - upper bound exclusive
        assert aq_label(0.5) == "ccu_overview.sensor_data.aq.label_excellent"
        assert aq_label(0.9) == "ccu_overview.sensor_data.aq.label_excellent"
        
        # Good range [1, 2) - 1.0 belongs to this range
        assert aq_label(1.0) == "ccu_overview.sensor_data.aq.label_good"
        assert aq_label(1.1) == "ccu_overview.sensor_data.aq.label_good"

        # Mittel
        assert aq_label(1.5) == "ccu_overview.sensor_data.aq.label_good"
        assert aq_label(2.5) == "ccu_overview.sensor_data.aq.label_moderate"
        assert aq_label(2.9) == "ccu_overview.sensor_data.aq.label_moderate"  # [2, 3)

        # Schlecht - 3.0 belongs to [3, 4) range
        assert aq_label(3.0) == "ccu_overview.sensor_data.aq.label_poor"
        assert aq_label(3.5) == "ccu_overview.sensor_data.aq.label_poor"
        assert aq_label(4.5) == "ccu_overview.sensor_data.aq.label_very_poor"

    def test_aq_normalization(self):
        """Test AQ normalization to percentage"""
        # Test edge cases
        assert normalize_aq(0.0) == 0.0
        assert normalize_aq(5.0) == 100.0

        # Test middle values
        assert normalize_aq(2.5) == 50.0
        assert normalize_aq(1.0) == 20.0
        assert normalize_aq(4.0) == 80.0

    def test_get_aq_info_complete(self):
        """Test complete AQ info retrieval - returns i18n keys"""
        # Test gut
        level, color, label = get_aq_info(0.5)
        assert level == "sehr_gut"
        assert color == "#28a745"
        assert label == "ccu_overview.sensor_data.aq.label_excellent"

        # Test mittel
        level, color, label = get_aq_info(2.5)
        assert level == "maessig"
        assert color == "#ffc107"
        assert label == "ccu_overview.sensor_data.aq.label_moderate"

        # Test schlecht
        level, color, label = get_aq_info(4.5)
        assert level == "sehr_schlecht"
        assert color == "#dc3545"
        assert label == "ccu_overview.sensor_data.aq.label_very_poor"

    def test_aq_ampel_logic(self):
        """Test Ampel logic for three-block system"""

        def get_ampel_state(aq_value):
            """Determine which block should be active"""
            if aq_value <= 1.0:
                return "bottom_active"  # Unterer Block
            elif aq_value <= 3.0:
                return "middle_active"  # Mittlerer Block
            else:
                return "top_active"  # Oberer Block

        # Test Ampel states
        assert get_ampel_state(0.5) == "bottom_active"
        assert get_ampel_state(1.0) == "bottom_active"
        assert get_ampel_state(1.5) == "middle_active"
        assert get_ampel_state(2.5) == "middle_active"
        assert get_ampel_state(3.0) == "middle_active"
        assert get_ampel_state(3.5) == "top_active"
        assert get_ampel_state(4.5) == "top_active"

    def test_aq_edge_cases(self):
        """Test AQ edge cases"""
        # Negative values
        assert normalize_aq(-1.0) == 0.0
        assert aq_level(-1.0) == "sehr_gut"

        # Values above 5
        assert normalize_aq(10.0) == 100.0
        assert aq_level(10.0) == "sehr_schlecht"

        # Exact boundary values
        assert aq_level(1.0) == "sehr_gut"
        assert aq_level(1.1) == "gut"
        assert aq_level(3.0) == "maessig"
        assert aq_level(3.1) == "schlecht"

    def test_aq_with_custom_config(self):
        """Test AQ functions with custom configuration - uses fallback when no i18n keys"""
        custom_config = {
            "aq": {
                "min": 0.0,
                "max": 5.0,
                "bar_chart": {
                    "color_ranges": [
                        [0, 1, "#00ff00"],  # Custom green (no i18n key - uses fallback)
                        [1, 2, "#ffff00"],  # Custom yellow
                        [2, 3, "#ff8000"],  # Custom orange
                        [3, 4, "#ff4000"],  # Custom red-orange
                        [4, 5, "#ff0000"],  # Custom red
                    ],
                },
            }
        }

        # Test with custom config - falls back to level-based labels
        level, color, label = get_aq_info(0.5, custom_config)
        assert color == "#00ff00"
        assert label == "Excellent"  # Fallback from level_map

        level, color, label = get_aq_info(2.5, custom_config)
        assert color == "#ff8000"
        assert label == "Moderate"  # Fallback from level_map (maessig -> Moderate)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
