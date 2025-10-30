#!/usr/bin/env python3
"""
Tests for Shopfloor Layout - Streamlit-native Implementation
"""


from omf2.ui.ccu.common.shopfloor_layout import (
    _find_cell_data,
    _get_module_icon_svg,
)


class TestShopfloorLayoutHelpers:
    """Test cases for Shopfloor Layout Helper Functions"""

    def test_find_cell_data_finds_module(self):
        """Test that _find_cell_data can find a module at a position"""
        modules = [
            {"id": "DRILL", "type": "DRILL", "serialNumber": "SVR4H76449", "position": [2, 0]},
            {"id": "MILL", "type": "MILL", "serialNumber": "SVR3QA2098", "position": [0, 1]},
        ]
        fixed_positions = []
        intersections = []

        result = _find_cell_data(2, 0, modules, fixed_positions, intersections)

        assert result is not None
        assert result["type"] == "DRILL"
        assert result["id"] == "DRILL"

    def test_find_cell_data_finds_intersection(self):
        """Test that _find_cell_data can find an intersection"""
        modules = []
        fixed_positions = []
        intersections = [
            {"id": "1", "position": [1, 1]},
            {"id": "2", "position": [1, 2]},
        ]

        result = _find_cell_data(1, 1, modules, fixed_positions, intersections)

        assert result is not None
        assert result["type"] == "intersection"
        assert result["id"] == "1"

    def test_find_cell_data_finds_fixed_position(self):
        """Test that _find_cell_data can find a fixed position"""
        modules = []
        fixed_positions = [
            {
                "id": "COMPANY",
                "type": "company",
                "position": [0, 0],
                "assets": {"rectangle": "ORBIS", "square1": "shelves", "square2": "conveyor_belt"},
            }
        ]
        intersections = []

        result = _find_cell_data(0, 0, modules, fixed_positions, intersections)

        assert result is not None
        assert result["type"] == "fixed"
        assert result["id"] == "COMPANY"

    def test_find_cell_data_returns_none_for_empty(self):
        """Test that _find_cell_data returns None for empty cells"""
        modules = []
        fixed_positions = []
        intersections = []

        result = _find_cell_data(2, 2, modules, fixed_positions, intersections)

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
