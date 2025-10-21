#!/usr/bin/env python3
"""
Tests for Shopfloor Layout Event Handling
"""

import pytest

from omf2.ui.ccu.common.shopfloor_layout import _generate_omf2_svg_grid_with_roads


class TestShopfloorLayoutEvents:
    """Test cases for Shopfloor Layout Event Handling"""

    def test_event_forwarder_in_html(self):
        """Test that the event forwarder JavaScript is embedded in the HTML"""
        # Mock layout config
        layout_config = {
            "grid": {"rows": 3, "columns": 4},
            "modules": [
                {"id": "DRILL", "type": "DRILL", "serialNumber": "SVR4H76449", "position": [2, 0]},
                {"id": "MILL", "type": "MILL", "serialNumber": "SVR3QA2098", "position": [0, 1]},
            ],
            "empty_positions": [],
            "intersections": [],
            "roads": [],
        }

        # Mock asset manager
        class MockAssetManager:
            def get_module_icon_path(self, module_type):
                return None

        asset_manager = MockAssetManager()

        # Generate HTML
        html = _generate_omf2_svg_grid_with_roads(
            layout_config=layout_config,
            asset_manager=asset_manager,
            active_module_id=None,
            active_intersections=None,
            mode="ccu_configuration",
        )

        # Verify event forwarder is present in HTML
        assert "FACTORY_GRID_EVENT" in html, "FACTORY_GRID_EVENT listener not found in HTML"
        assert "GET_FACTORY_EVENT" in html, "GET_FACTORY_EVENT dispatch not found in HTML"
        assert "document.addEventListener('FACTORY_GRID_EVENT'" in html, "Event listener not properly set up"
        assert "document.dispatchEvent(streamlitEvent)" in html, "Event dispatch not found"

        # Verify debug logging is present
        assert "Factory Grid Event received" in html, "Debug logging not found"
        assert "Event forwarded as GET_FACTORY_EVENT" in html, "Event forwarding log not found"

    def test_double_click_handler_in_html(self):
        """Test that the double-click handler is present in the HTML"""
        layout_config = {
            "grid": {"rows": 3, "columns": 4},
            "modules": [{"id": "DRILL", "type": "DRILL", "serialNumber": "SVR4H76449", "position": [2, 0]}],
            "empty_positions": [],
            "intersections": [],
            "roads": [],
        }

        class MockAssetManager:
            def get_module_icon_path(self, module_type):
                return None

        asset_manager = MockAssetManager()

        html = _generate_omf2_svg_grid_with_roads(
            layout_config=layout_config,
            asset_manager=asset_manager,
            active_module_id=None,
            active_intersections=None,
            mode="ccu_configuration",
        )

        # Verify double-click handler is present
        assert "handleModuleDoubleClick" in html, "Double-click handler not found"
        assert "module-dblclick" in html, "Double-click event type not found"
        assert "dblclick" in html, "dblclick event listener not found"

    def test_mode_classes_in_html(self):
        """Test that mode-specific CSS classes are present"""
        layout_config = {
            "grid": {"rows": 3, "columns": 4},
            "modules": [],
            "empty_positions": [],
            "intersections": [],
            "roads": [],
        }

        class MockAssetManager:
            def get_module_icon_path(self, module_type):
                return None

        asset_manager = MockAssetManager()

        # Test ccu_configuration mode
        html = _generate_omf2_svg_grid_with_roads(
            layout_config=layout_config,
            asset_manager=asset_manager,
            active_module_id=None,
            active_intersections=None,
            mode="ccu_configuration",
        )

        assert 'class="mode-ccu_configuration"' in html or 'class="mode-ccu-configuration"' in html, (
            "CCU configuration mode class not found"
        )
        assert ".mode-ccu-configuration" in html or ".mode-ccu_configuration" in html, (
            "CCU configuration CSS not found"
        )

    def test_module_data_attributes(self):
        """Test that module cells have proper data attributes for event handling"""
        layout_config = {
            "grid": {"rows": 3, "columns": 4},
            "modules": [
                {"id": "DRILL", "type": "DRILL", "serialNumber": "SVR4H76449", "position": [2, 0]},
            ],
            "empty_positions": [],
            "intersections": [],
            "roads": [],
        }

        class MockAssetManager:
            def get_module_icon_path(self, module_type):
                return None

        asset_manager = MockAssetManager()

        html = _generate_omf2_svg_grid_with_roads(
            layout_config=layout_config,
            asset_manager=asset_manager,
            active_module_id=None,
            active_intersections=None,
            mode="ccu_configuration",
        )

        # Verify module data attributes
        assert 'data-module-id="DRILL"' in html, "Module ID attribute not found"
        assert 'data-module-type="DRILL"' in html, "Module type attribute not found"
        assert 'data-position="[2,0]"' in html, "Module position attribute not found"
