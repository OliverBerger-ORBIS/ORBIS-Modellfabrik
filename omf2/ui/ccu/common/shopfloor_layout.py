#!/usr/bin/env python3
"""
CCU Shopfloor Layout Component
Reusable component for displaying shopfloor layout from CCU Config Loader
"""

import streamlit as st
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def show_shopfloor_layout():
    """Show shopfloor layout component"""
    try:
        st.subheader("🗺️ Shopfloor Layout")
        st.write("Factory layout with modules, intersections, and connections")
        
        # Load shopfloor layout from CCU Config Loader
        config_loader = get_ccu_config_loader()
        layout_data = config_loader.load_shopfloor_layout()
        
        # Show grid visualization
        _show_shopfloor_grid(layout_data)
        
        # Show metadata
        _show_shopfloor_metadata(layout_data)
        
    except Exception as e:
        logger.error(f"❌ Shopfloor layout display error: {e}")
        st.error(f"❌ Failed to load shopfloor layout: {e}")


def _show_shopfloor_grid(layout_data):
    """Show 4x3 grid visualization"""
    grid = layout_data.get("grid", {})
    modules = layout_data.get("modules", [])
    intersections = layout_data.get("intersections", [])
    empty_positions = layout_data.get("empty_positions", [])
    
    rows = grid.get("rows", 3)
    columns = grid.get("columns", 4)
    
    st.write(f"**Grid Layout ({rows}×{columns})** (Standard: {rows} rows × {columns} columns)")
    
    # Create grid array
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
    
    # Display grid
    for row in range(rows):
        cols = st.columns(columns)
        for col in range(columns):
            with cols[col]:
                cell = grid_array[row][col]
                _display_grid_cell(cell, row, col)


def _display_grid_cell(cell, row, col):
    """Display individual grid cell"""
    if not cell:
        st.info("Empty")
        return
    
    cell_type = cell.get("type")
    cell_data = cell.get("data", {})
    
    if cell_type == "module":
        _display_module_cell(cell_data)
    elif cell_type == "intersection":
        _display_intersection_cell(cell_data)
    elif cell_type == "empty":
        _display_empty_cell(cell_data)
    else:
        st.info("Unknown")


def _display_module_cell(module):
    """Display module cell"""
    module_id = module.get("id", "")
    module_type = module.get("type", "")
    serial_number = module.get("serialNumber", "")
    position = module.get("position", [0, 0])
    
    # Get module icon from UISymbols or Registry
    icon = _get_module_icon(module_type)
    
    st.markdown(f"**{icon} {module_id}**")
    st.caption(f"Type: {module_type}")
    st.caption(f"Serial: {serial_number}")
    st.caption(f"Position: [{position[0]}, {position[1]}] (x=col, y=row)")


def _display_intersection_cell(intersection):
    """Display intersection cell"""
    intersection_id = intersection.get("id", "")
    position = intersection.get("position", [0, 0])
    connected_modules = intersection.get("connected_modules", [])
    
    st.markdown(f"**➕ Intersection {intersection_id}**")
    st.caption(f"Position: [{position[0]}, {position[1]}] (x=col, y=row)")
    if connected_modules:
        st.caption(f"Connected: {', '.join(connected_modules)}")


def _display_empty_cell(empty):
    """Display empty cell"""
    empty_id = empty.get("id", "")
    position = empty.get("position", [0, 0])
    
    st.markdown(f"**⚪ {empty_id}**")
    st.caption(f"Position: [{position[0]}, {position[1]}] (x=col, y=row)")
    st.caption("Empty Position")


def _get_module_icon(module_type):
    """Get icon for module type"""
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
