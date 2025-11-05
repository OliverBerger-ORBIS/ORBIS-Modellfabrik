#!/usr/bin/env python3
"""
Tests for Shopfloor Layout - SVG Rendering Implementation

Note: Legacy helper functions (_find_cell_data, _get_module_icon_svg) have been removed.
These tests are updated to use the new _get_entity_at_position function.
"""


from omf2.ui.ccu.common.shopfloor_layout import (
    _get_entity_at_position,
)


class TestShopfloorLayoutHelpers:
    """Test cases for Shopfloor Layout Helper Functions"""

    def test_get_entity_at_position_finds_module(self):
        """Test that _get_entity_at_position can find a module at a position"""
        layout = {
            "modules": [
                {"id": "DRILL", "type": "DRILL", "serialNumber": "SVR4H76449", "position": [2, 0]},
                {"id": "MILL", "type": "MILL", "serialNumber": "SVR3QA2098", "position": [0, 1]},
            ],
            "fixed_positions": [],
            "intersections": [],
        }

        result = _get_entity_at_position(layout, 2, 0)

        assert result is not None
        assert result["type"] == "module"
        assert result["data"]["type"] == "DRILL"
        assert result["data"]["id"] == "DRILL"

    def test_get_entity_at_position_finds_intersection(self):
        """Test that _get_entity_at_position can find an intersection"""
        layout = {
            "modules": [],
            "fixed_positions": [],
            "intersections": [
                {"id": "1", "type": "INTERSECTION-1", "position": [1, 1]},
                {"id": "2", "type": "INTERSECTION-2", "position": [1, 2]},
            ],
        }

        result = _get_entity_at_position(layout, 1, 1)

        assert result is not None
        assert result["type"] == "intersection"
        assert result["data"]["id"] == "1"

    def test_get_entity_at_position_finds_fixed_position(self):
        """Test that _get_entity_at_position can find a fixed position"""
        layout = {
            "modules": [],
            "fixed_positions": [
                {
                    "id": "COMPANY",
                    "type": "ORBIS",
                    "position": [0, 0],
                }
            ],
            "intersections": [],
        }

        result = _get_entity_at_position(layout, 0, 0)

        assert result is not None
        assert result["type"] == "fixed_position"
        assert result["data"]["id"] == "COMPANY"

    def test_get_entity_at_position_returns_none_for_empty(self):
        """Test that _get_entity_at_position returns None for empty cells"""
        layout = {
            "modules": [],
            "fixed_positions": [],
            "intersections": [],
        }

        result = _get_entity_at_position(layout, 2, 2)

        assert result is None
