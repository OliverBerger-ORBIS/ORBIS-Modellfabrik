#!/usr/bin/env python3
"""
CCU Shopfloor Layout Component
Reusable component for displaying shopfloor layout from CCU Config Loader
Enhanced with Asset Manager and improved visualization
"""

import streamlit as st
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh
from omf2.assets import get_asset_manager

logger = get_logger(__name__)


def show_shopfloor_layout(active_module_id: str = None, show_controls: bool = True):
    """Show enhanced shopfloor layout component with asset manager
    
    Args:
        active_module_id: ID of currently active module (for highlighting)
        show_controls: Whether to show zoom controls and metadata
    """
    try:
        st.subheader("🗺️ Shopfloor Layout")
        st.write("Factory layout with modules, intersections, and connections")
        
        # Load shopfloor layout from CCU Config Loader
        config_loader = get_ccu_config_loader()
        layout_data = config_loader.load_shopfloor_layout()
        
        # Show enhanced grid visualization with asset manager
        _show_enhanced_shopfloor_grid(layout_data, active_module_id)
        
        # Show metadata if requested
        if show_controls:
            _show_shopfloor_metadata(layout_data)
        
    except Exception as e:
        logger.error(f"❌ Shopfloor layout display error: {e}")
        st.error(f"❌ Failed to load shopfloor layout: {e}")


def _show_enhanced_shopfloor_grid(layout_data, active_module_id: str = None):
    """Show enhanced 4x3 grid visualization with asset manager and highlighting (quadratic cells)"""
    grid = layout_data.get("grid", {})
    modules = layout_data.get("modules", [])
    intersections = layout_data.get("intersections", [])
    empty_positions = layout_data.get("empty_positions", [])
    
    rows = grid.get("rows", 3)
    columns = grid.get("columns", 4)
    
    st.write(f"**Grid Layout ({rows}×{columns})** - Quadratische Zellen für gleichmäßige Darstellung")
    
    # Get asset manager
    asset_manager = get_asset_manager()
    
    # Create grid array - WICHTIG: [row][col] Format für korrekte Darstellung
    grid_array = [[None for _ in range(columns)] for _ in range(rows)]
    
    # Fill grid with modules (position format: [x, y] where x=column, y=row)
    for module in modules:
        position = module.get("position", [0, 0])
        col, row = position[0], position[1]  # position is [x, y] = [column, row]
        if 0 <= row < rows and 0 <= col < columns:
            grid_array[row][col] = {"type": "module", "data": module}
    
    # Fill grid with intersections (position format: [x, y] where x=column, y=row)
    for intersection in intersections:
        position = intersection.get("position", [0, 0])
        col, row = position[0], position[1]  # position is [x, y] = [column, row]
        if 0 <= row < rows and 0 <= col < columns:
            grid_array[row][col] = {"type": "intersection", "data": intersection}
    
    # Fill grid with empty positions (position format: [x, y] where x=column, y=row)
    for empty in empty_positions:
        position = empty.get("position", [0, 0])
        col, row = position[0], position[1]  # position is [x, y] = [column, row]
        if 0 <= row < rows and 0 <= col < columns:
            grid_array[row][col] = {"type": "empty", "data": empty}
    
    # Display enhanced grid with fixed 3:4 aspect ratio container
    _display_fixed_aspect_ratio_grid(grid_array, rows, columns, active_module_id, asset_manager)


def _display_fixed_aspect_ratio_grid(grid_array, rows, columns, active_module_id: str, asset_manager):
    """Display grid with fixed 3:4 aspect ratio container"""
    # Calculate container dimensions maintaining 3:4 aspect ratio
    # Container should be 3:4 (width:height) regardless of cell size
    cell_size = 80  # Base cell size
    
    # Calculate container dimensions
    container_width = columns * cell_size + (columns - 1) * 4  # 4px margin between cells
    container_height = rows * cell_size + (rows - 1) * 4
    
    # Ensure 3:4 aspect ratio
    aspect_ratio = 3 / 4
    if container_width / container_height > aspect_ratio:
        # Too wide, adjust height
        container_height = container_width / aspect_ratio
        cell_size = (container_height - (rows - 1) * 4) / rows
    else:
        # Too tall, adjust width
        container_width = container_height * aspect_ratio
        cell_size = (container_width - (columns - 1) * 4) / columns
    
    # Generate HTML for fixed aspect ratio container
    html_content = ""
    for row in range(rows):
        for col in range(columns):
            cell = grid_array[row][col]
            
            # Calculate position within container
            x_pos = col * (cell_size + 4)
            y_pos = row * (cell_size + 4)
            
            # Generate cell HTML
            cell_html = _generate_grid_cell_html(cell, row, col, active_module_id, asset_manager, int(cell_size))
            
            html_content += f'<div style="position: absolute; left: {x_pos}px; top: {y_pos}px; width: {cell_size}px; height: {cell_size}px;">{cell_html}</div>'
    
    # Container HTML with fixed 3:4 aspect ratio
    container_html = f'<div style="position: relative; width: {container_width}px; height: {container_height}px; border: 2px solid #e0e0e0; border-radius: 8px; background: #f8f9fa; margin: 10px auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">{html_content}</div>'
    
    st.markdown(container_html, unsafe_allow_html=True)


def _generate_grid_cell_html(cell, row, col, active_module_id: str, asset_manager, cell_size: int):
    """Generate HTML for individual grid cell"""
    if not cell:
        return asset_manager.get_shopfloor_module_html("EMPTY", f"Empty_{row}_{col}", False, size=cell_size)
    
    cell_type = cell.get("type")
    cell_data = cell.get("data", {})
    
    # Check if this is the active module
    is_active = False
    if cell_type == "module" and active_module_id:
        module_id = cell_data.get("id", "")
        is_active = module_id == active_module_id
    
    if cell_type == "module":
        module_id = cell_data.get("id", "")
        module_type = cell_data.get("type", "")
        return asset_manager.get_shopfloor_module_html(module_type, module_id, is_active, size=cell_size)
    elif cell_type == "intersection":
        intersection_id = cell_data.get("id", "")
        return asset_manager.get_shopfloor_module_html("INTERSECTION", intersection_id, is_active, size=cell_size)
    elif cell_type == "empty":
        empty_id = cell_data.get("id", "")
        return asset_manager.get_shopfloor_module_html("EMPTY", empty_id, is_active, size=cell_size)
    else:
        return asset_manager.get_shopfloor_module_html("MACHINE", f"Unknown_{row}_{col}", is_active, size=cell_size)


def _display_enhanced_grid_cell(cell, row, col, active_module_id: str, asset_manager):
    """Display enhanced individual grid cell with asset manager and highlighting (quadratic)"""
    if not cell:
        # Empty cell with asset manager - Quadratische Zelle
        html = asset_manager.get_shopfloor_module_html("EMPTY", f"Empty_{row}_{col}", False, size=100)
        st.markdown(html, unsafe_allow_html=True)
        return
    
    cell_type = cell.get("type")
    cell_data = cell.get("data", {})
    
    # Check if this is the active module
    is_active = False
    if cell_type == "module" and active_module_id:
        module_id = cell_data.get("id", "")
        is_active = module_id == active_module_id
    
    if cell_type == "module":
        _display_enhanced_module_cell(cell_data, is_active, asset_manager)
    elif cell_type == "intersection":
        _display_enhanced_intersection_cell(cell_data, is_active, asset_manager)
    elif cell_type == "empty":
        _display_enhanced_empty_cell(cell_data, is_active, asset_manager)
    else:
        html = asset_manager.get_shopfloor_module_html("MACHINE", f"Unknown_{row}_{col}", is_active, size=100)
        st.markdown(html, unsafe_allow_html=True)


def _display_enhanced_module_cell(module, is_active: bool, asset_manager):
    """Display enhanced module cell with asset manager (quadratic)"""
    module_id = module.get("id", "")
    module_type = module.get("type", "")
    
    # Use asset manager for enhanced HTML display - Quadratische Zelle
    html = asset_manager.get_shopfloor_module_html(module_type, module_id, is_active, size=100)
    st.markdown(html, unsafe_allow_html=True)


def _display_enhanced_intersection_cell(intersection, is_active: bool, asset_manager):
    """Display enhanced intersection cell with asset manager (quadratic)"""
    intersection_id = intersection.get("id", "")
    
    # Use asset manager for enhanced HTML display - Quadratische Zelle
    html = asset_manager.get_shopfloor_module_html("INTERSECTION", intersection_id, is_active, size=100)
    st.markdown(html, unsafe_allow_html=True)


def _display_enhanced_empty_cell(empty, is_active: bool, asset_manager):
    """Display enhanced empty cell with asset manager (quadratic)"""
    empty_id = empty.get("id", "")
    
    # Use asset manager for enhanced HTML display - Quadratische Zelle
    html = asset_manager.get_shopfloor_module_html("EMPTY", empty_id, is_active, size=100)
    st.markdown(html, unsafe_allow_html=True)


# Legacy function - now handled by Asset Manager
def _get_module_icon(module_type):
    """Get icon for module type (legacy - use Asset Manager instead)"""
    icon_mapping = {
        "HBW": "🏬",      # High Bay Warehouse
        "MILL": "⚙️",     # Mill
        "DRILL": "🔩",    # Drill
        "AIQS": "🤖",     # AI Quality System
        "DPS": "📦",      # Delivery and Pickup Station
        "CHRG": "🔋",     # Charging Station
        "FTS": "🚗",      # Fleet Transport System
    }
    return icon_mapping.get(module_type, "🔧")


def _show_shopfloor_metadata(layout_data):
    """Show shopfloor layout metadata"""
    meta = layout_data.get("_meta", {})
    
    if meta:
        with st.expander("📋 Layout Information", expanded=False):
            st.write(f"**Description:** {meta.get('_description', 'N/A')}")
            st.write(f"**Version:** {meta.get('_version', 'N/A')}")
            st.write(f"**Domain:** {meta.get('_domain', 'N/A')}")
            
            notes = meta.get("_notes", [])
            if notes:
                st.write("**Notes:**")
                for note in notes:
                    st.write(f"• {note}")


def get_shopfloor_layout_data():
    """Get shopfloor layout data for external use"""
    try:
        config_loader = get_ccu_config_loader()
        return config_loader.load_shopfloor_layout()
    except Exception as e:
        logger.error(f"❌ Failed to get shopfloor layout data: {e}")
        return None


def get_module_positions():
    """Get module positions for external use"""
    try:
        layout_data = get_shopfloor_layout_data()
        if not layout_data:
            return []
        
        modules = layout_data.get("modules", [])
        return [
            {
                "id": module.get("id"),
                "type": module.get("type"),
                "serialNumber": module.get("serialNumber"),
                "position": module.get("position", [0, 0])
            }
            for module in modules
        ]
    except Exception as e:
        logger.error(f"❌ Failed to get module positions: {e}")
        return []


def get_intersection_positions():
    """Get intersection positions for external use"""
    try:
        layout_data = get_shopfloor_layout_data()
        if not layout_data:
            return []
        
        intersections = layout_data.get("intersections", [])
        return [
            {
                "id": intersection.get("id"),
                "position": intersection.get("position", [0, 0]),
                "connected_modules": intersection.get("connected_modules", [])
            }
            for intersection in intersections
        ]
    except Exception as e:
        logger.error(f"❌ Failed to get intersection positions: {e}")
        return []


def show_shopfloor_grid_only(active_module_id: str = None, title: str = "Shopfloor Layout"):
    """Show only the shopfloor grid without metadata (for reuse in other components)
    
    Args:
        active_module_id: ID of currently active module (for highlighting)
        title: Optional title for the grid
    """
    try:
        if title:
            st.subheader(f"🗺️ {title}")
        
        # Load shopfloor layout from CCU Config Loader
        config_loader = get_ccu_config_loader()
        layout_data = config_loader.load_shopfloor_layout()
        
        # Show enhanced grid visualization only
        _show_enhanced_shopfloor_grid(layout_data, active_module_id)
        
    except Exception as e:
        logger.error(f"❌ Shopfloor grid display error: {e}")
        st.error(f"❌ Failed to load shopfloor grid: {e}")


def show_shopfloor_with_zoom_controls(active_module_id: str = None):
    """Show shopfloor layout with zoom controls (like in original application)"""
    try:
        st.subheader("🗺️ Shopfloor Layout")
        
        # Zoom controls (like in original application)
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🔍+", help="Zoom In"):
                st.session_state.shopfloor_zoom = st.session_state.get("shopfloor_zoom", 100) + 10
                request_refresh()
        with col2:
            if st.button("🔍-", help="Zoom Out"):
                st.session_state.shopfloor_zoom = max(50, st.session_state.get("shopfloor_zoom", 100) - 10)
                request_refresh()
        with col3:
            zoom_level = st.session_state.get("shopfloor_zoom", 100)
            st.write(f"Zoom: {zoom_level}%")
        
        # Load and display shopfloor layout
        config_loader = get_ccu_config_loader()
        layout_data = config_loader.load_shopfloor_layout()
        
        # Show enhanced grid with zoom
        _show_enhanced_shopfloor_grid(layout_data, active_module_id)
        
    except Exception as e:
        logger.error(f"❌ Shopfloor layout with controls error: {e}")
        st.error(f"❌ Failed to load shopfloor layout: {e}")
