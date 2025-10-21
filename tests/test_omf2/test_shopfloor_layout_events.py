#!/usr/bin/env python3
"""
Tests for Shopfloor Layout - Streamlit-native Implementation
"""

import pytest

from omf2.ui.ccu.common.shopfloor_layout import (
    _find_cell_data,
    _get_module_icon_svg,
    show_shopfloor_layout,
)


class TestShopfloorLayoutHelpers:
    """Test cases for Shopfloor Layout Helper Functions"""

    def test_find_cell_data_finds_module(self):
        """Test that _find_cell_data can find a module at a position"""
        modules = [
            {"id": "DRILL", "type": "DRILL", "serialNumber": "SVR4H76449", "position": [2, 0]},
            {"id": "MILL", "type": "MILL", "serialNumber": "SVR3QA2098", "position": [0, 1]},
        ]
        empty_positions = []
        intersections = []

        result = _find_cell_data(2, 0, modules, empty_positions, intersections)
        
        assert result is not None
        assert result["type"] == "DRILL"
        assert result["id"] == "DRILL"

    def test_find_cell_data_finds_intersection(self):
        """Test that _find_cell_data can find an intersection"""
        modules = []
        empty_positions = []
        intersections = [
            {"id": "1", "position": [1, 1]},
            {"id": "2", "position": [1, 2]},
        ]

        result = _find_cell_data(1, 1, modules, empty_positions, intersections)
        
        assert result is not None
        assert result["type"] == "intersection"
        assert result["id"] == "1"

    def test_find_cell_data_returns_none_for_empty(self):
        """Test that _find_cell_data returns None for empty cells"""
        modules = []
        empty_positions = []
        intersections = []

        result = _find_cell_data(0, 0, modules, empty_positions, intersections)
        
        assert result is None

    def test_get_module_icon_svg_handles_missing_icon(self):
        """Test that _get_module_icon_svg handles missing icons gracefully"""
        
        class MockAssetManager:
            def get_module_icon_path(self, module_type):
                return None

        asset_manager = MockAssetManager()
        
        result = _get_module_icon_svg(asset_manager, "NONEXISTENT", 100, 100, None)
        
        # Should return fallback text element
        assert "text" in result
        assert "NONEXISTENT" in result


class TestShopfloorLayoutDeprecatedFunctions:
    """Test cases for deprecated functions to ensure they don't break"""

    def test_deprecated_svg_grid_with_roads(self):
        """Test that deprecated _generate_omf2_svg_grid_with_roads returns empty string"""
        from omf2.ui.ccu.common.shopfloor_layout import _generate_omf2_svg_grid_with_roads
        
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

        # Should return empty string and log warning
        html = _generate_omf2_svg_grid_with_roads(
            layout_config=layout_config,
            asset_manager=asset_manager,
            active_module_id=None,
            active_intersections=None,
            mode="ccu_configuration",
        )

        assert html == ""

    def test_deprecated_process_grid_events(self):
        """Test that deprecated _process_grid_events doesn't crash"""
        from omf2.ui.ccu.common.shopfloor_layout import _process_grid_events
        
        # Should not crash, just log warning
        _process_grid_events("test_key")

    def test_deprecated_handle_grid_event(self):
        """Test that deprecated _handle_grid_event doesn't crash"""
        from omf2.ui.ccu.common.shopfloor_layout import _handle_grid_event
        
        event_data = {
            "type": "module-click",
            "id": "DRILL",
            "moduleType": "DRILL"
        }
        
        # Should not crash, just log warning
        _handle_grid_event(event_data)
