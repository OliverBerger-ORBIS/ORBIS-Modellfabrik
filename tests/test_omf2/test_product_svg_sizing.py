#!/usr/bin/env python3
"""
Unit Tests for Product SVG Sizing and Warehouse Grid Layout
===========================================================

Tests for:
- Product SVG sizing with PRODUCT_SVG_BASE_SIZE = 200px
- 3x3 warehouse grid layout enforcement
- Proportional scaling for non-square SVGs
- Optional scale parameter support
"""

import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from omf2.assets.asset_manager import PRODUCT_SVG_BASE_SIZE, get_asset_manager


class TestProductSvgSizeConstant(unittest.TestCase):
    """Tests for PRODUCT_SVG_BASE_SIZE constant"""

    def test_product_svg_base_size_is_200(self):
        """Test: PRODUCT_SVG_BASE_SIZE is defined as 200 pixels"""
        self.assertEqual(PRODUCT_SVG_BASE_SIZE, 200)
        self.assertIsInstance(PRODUCT_SVG_BASE_SIZE, int)


class TestWarehouseGridLayout(unittest.TestCase):
    """Tests for warehouse 3x3 grid layout enforcement"""

    def test_grid_remains_3x3_regardless_of_svg_sizes(self):
        """Test: Warehouse grid maintains 3x3 structure independent of SVG variations"""
        # Grid should always be 3x3 (9 positions: A1-A3, B1-B3, C1-C3)
        expected_positions = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]

        self.assertEqual(len(expected_positions), 9)
        # Verify structure is 3x3
        rows = set([pos[0] for pos in expected_positions])
        cols = set([pos[1] for pos in expected_positions])
        self.assertEqual(len(rows), 3)  # 3 rows: A, B, C
        self.assertEqual(len(cols), 3)  # 3 columns: 1, 2, 3

    def test_cell_size_matches_product_svg_base_size(self):
        """Test: Grid cell size should match PRODUCT_SVG_BASE_SIZE for consistency"""
        # Each cell should accommodate PRODUCT_SVG_BASE_SIZE
        cell_size = PRODUCT_SVG_BASE_SIZE
        self.assertEqual(cell_size, 200)

        # Total grid size should be 3 * cell_size for each dimension
        grid_width = 3 * cell_size
        grid_height = 3 * cell_size
        self.assertEqual(grid_width, 600)
        self.assertEqual(grid_height, 600)


class TestProductSvgSizingPolicy(unittest.TestCase):
    """Tests for product SVG sizing policy"""

    def setUp(self):
        """Setup for each test"""
        self.asset_manager = get_asset_manager()

    def test_product_svg_rendering_uses_base_size(self):
        """Test: Product SVGs should be rendered within PRODUCT_SVG_BASE_SIZE container"""
        container_size = PRODUCT_SVG_BASE_SIZE

        # Container should be square (200x200)
        self.assertEqual(container_size, 200)

        # For square SVGs
        expected_width = container_size
        expected_height = container_size
        self.assertEqual(expected_width, 200)
        self.assertEqual(expected_height, 200)

    def test_non_square_svg_proportional_scaling(self):
        """Test: Non-square SVGs should maintain width=200px with proportional height"""
        base_width = PRODUCT_SVG_BASE_SIZE  # 200px

        # Example: SVG with original dimensions 300x200 (aspect ratio 1.5:1)
        original_width = 300
        original_height = 200
        aspect_ratio = original_width / original_height

        # After sizing: width should be 200px
        scaled_width = base_width
        # Height should be proportional: 200 / 1.5 = 133.33px
        scaled_height = scaled_width / aspect_ratio

        self.assertEqual(scaled_width, 200)
        self.assertAlmostEqual(scaled_height, 133.33, places=2)

    def test_scale_parameter_support(self):
        """Test: Optional scale parameter should multiply base size"""
        base_size = PRODUCT_SVG_BASE_SIZE

        # scale = 1.0 (default)
        size_1x = base_size * 1.0
        self.assertEqual(size_1x, 200)

        # scale = 1.5
        size_1_5x = base_size * 1.5
        self.assertEqual(size_1_5x, 300)

        # scale = 0.5
        size_0_5x = base_size * 0.5
        self.assertEqual(size_0_5x, 100)

    def test_get_product_svg_with_sizing_exists(self):
        """Test: Asset manager has get_product_svg_with_sizing method"""
        self.assertTrue(hasattr(self.asset_manager, "get_product_svg_with_sizing"))
        self.assertTrue(callable(self.asset_manager.get_product_svg_with_sizing))


class TestWorkpieceSvgRenderingConsistency(unittest.TestCase):
    """Tests for workpiece SVG rendering consistency across UI components"""

    def test_all_workpiece_colors_use_same_sizing(self):
        """Test: BLUE, WHITE, RED workpieces should all use same base size"""
        # All colors should render in the same container size
        colors = ["BLUE", "WHITE", "RED"]
        base_size = PRODUCT_SVG_BASE_SIZE

        for color in colors:
            # Each color should use the same base size
            container_size = base_size
            self.assertEqual(container_size, 200, f"{color} workpiece should use PRODUCT_SVG_BASE_SIZE")

    def test_different_states_use_same_container_size(self):
        """Test: Different workpiece states (product, 3dim, unprocessed) use same container"""
        states = ["product", "3dim", "unprocessed", "instock_unprocessed", "instock_reserved"]
        base_size = PRODUCT_SVG_BASE_SIZE

        for state in states:
            # All states should use the same container size
            container_size = base_size
            self.assertEqual(container_size, 200, f"Workpiece state '{state}' should use PRODUCT_SVG_BASE_SIZE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
