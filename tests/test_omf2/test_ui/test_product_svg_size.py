#!/usr/bin/env python3
"""
Tests for Product SVG Size Standardization

Tests that verify:
1. Size calculations are correct for different scale factors
2. HTML/CSS structure contains proper container dimensions
3. Warehouse grid enforces 3x3 layout
"""

import pytest
from omf2.ui.common.ui_constants import PRODUCT_SVG_BASE_SIZE, WAREHOUSE_CELL_SIZE, WAREHOUSE_GRID_COLUMNS
from omf2.ui.common.product_rendering import (
    render_product_svg_container,
    render_warehouse_cell,
    render_product_card
)


class TestProductSVGConstants:
    """Test UI constants are defined correctly"""
    
    def test_product_svg_base_size(self):
        """Test that PRODUCT_SVG_BASE_SIZE is 200px"""
        assert PRODUCT_SVG_BASE_SIZE == 200
    
    def test_warehouse_cell_size(self):
        """Test that WAREHOUSE_CELL_SIZE matches PRODUCT_SVG_BASE_SIZE"""
        assert WAREHOUSE_CELL_SIZE == 200
        assert WAREHOUSE_CELL_SIZE == PRODUCT_SVG_BASE_SIZE
    
    def test_warehouse_grid_columns(self):
        """Test that warehouse grid is 3 columns"""
        assert WAREHOUSE_GRID_COLUMNS == 3


class TestSizeCalculations:
    """Test size calculations with different scale factors"""
    
    def test_scale_default(self):
        """Test default scale (1.0) produces 200px"""
        scale = 1.0
        expected_size = int(PRODUCT_SVG_BASE_SIZE * scale)
        assert expected_size == 200
    
    def test_scale_150_percent(self):
        """Test scale=1.5 produces 300px"""
        scale = 1.5
        expected_size = int(PRODUCT_SVG_BASE_SIZE * scale)
        assert expected_size == 300
    
    def test_scale_50_percent(self):
        """Test scale=0.5 produces 100px"""
        scale = 0.5
        expected_size = int(PRODUCT_SVG_BASE_SIZE * scale)
        assert expected_size == 100
    
    def test_scale_200_percent(self):
        """Test scale=2.0 produces 400px"""
        scale = 2.0
        expected_size = int(PRODUCT_SVG_BASE_SIZE * scale)
        assert expected_size == 400


class TestProductSVGContainerRendering:
    """Test HTML structure of product SVG containers"""
    
    def test_container_default_size(self):
        """Test container has default 200x200 dimensions"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_product_svg_container(svg_content, scale=1.0)
        
        # Check that HTML contains 200px dimensions
        assert "200px" in html
        assert svg_content in html
    
    def test_container_scaled_size(self):
        """Test container scales correctly with scale=1.5"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_product_svg_container(svg_content, scale=1.5)
        
        # Check that HTML contains 300px dimensions
        assert "300px" in html
        assert svg_content in html
    
    def test_container_has_border(self):
        """Test container includes border styling"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_product_svg_container(svg_content)
        
        assert "border:" in html
    
    def test_container_has_centering(self):
        """Test container includes centering styles"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_product_svg_container(svg_content)
        
        assert "text-align: center" in html
    
    def test_force_width_only_mode(self):
        """Test force_width_only mode produces different styling"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html_default = render_product_svg_container(svg_content, force_width_only=False)
        html_width_only = render_product_svg_container(svg_content, force_width_only=True)
        
        # Different HTML should be produced
        assert html_default != html_width_only
        assert "height: auto" in html_width_only


class TestWarehouseCellRendering:
    """Test warehouse cell rendering with 3x3 grid constraints"""
    
    def test_warehouse_cell_size(self):
        """Test warehouse cell has 200x200 dimensions"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_warehouse_cell(svg_content)
        
        # Check that HTML contains 200px dimensions
        assert "200px" in html
        assert svg_content in html
    
    def test_warehouse_cell_with_label(self):
        """Test warehouse cell includes position label"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_warehouse_cell(svg_content, position_label="A1", workpiece_type="BLUE")
        
        assert "A1" in html
        assert "BLUE" in html
    
    def test_warehouse_cell_empty(self):
        """Test warehouse cell displays EMPTY for None workpiece"""
        svg_content = '<svg viewBox="0 0 24 24"><path d="M0,0h24v24H0V0z"/></svg>'
        html = render_warehouse_cell(svg_content, position_label="A1", workpiece_type=None)
        
        assert "A1" in html
        assert "EMPTY" in html


class TestProductCardRendering:
    """Test complete product card rendering"""
    
    def test_product_card_basic(self):
        """Test basic product card with name"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_product_card(svg_content, "Test Product", scale=1.0)
        
        assert "Test Product" in html
        assert svg_content in html
        assert "200px" in html
    
    def test_product_card_with_additional_info(self):
        """Test product card with additional information"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        additional_info = {
            "Material": "Plastic",
            "Color": "Blue"
        }
        html = render_product_card(svg_content, "Test Product", additional_info=additional_info)
        
        assert "Material" in html
        assert "Plastic" in html
        assert "Color" in html
        assert "Blue" in html
    
    def test_product_card_scaled(self):
        """Test product card scales correctly"""
        svg_content = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40"/></svg>'
        html = render_product_card(svg_content, "Test Product", scale=1.5)
        
        # Should contain 300px (200 * 1.5)
        assert "300px" in html


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_multiple_products_same_size(self):
        """Test that multiple products render with same size"""
        products = ["BLUE", "WHITE", "RED"]
        svg_template = '<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="{}"/></svg>'
        
        rendered = []
        for product in products:
            svg = svg_template.format(product.lower())
            html = render_product_svg_container(svg, scale=1.0)
            rendered.append(html)
        
        # All should have 200px
        for html in rendered:
            assert "200px" in html
    
    def test_warehouse_grid_3x3(self):
        """Test that warehouse grid constant enforces 3x3 layout"""
        # This ensures grid is 3x3 regardless of product variations
        assert WAREHOUSE_GRID_COLUMNS == 3
        
        # 3 rows × 3 columns = 9 cells total
        total_cells = WAREHOUSE_GRID_COLUMNS * 3
        assert total_cells == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
