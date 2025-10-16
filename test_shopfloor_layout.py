#!/usr/bin/env python3
"""
Temporäre Streamlit App für Shopfloor Layout Testing
Testet die neue Grid-Aufteilung mit Rechteck + 2 Quadrate für Position 0,0 und 0,3
"""

import streamlit as st
import os
import re
from pathlib import Path

# OMF2 Imports
from omf2.assets import get_asset_manager
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger

logger = get_logger(__name__)

def main():
    st.title("🏭 Shopfloor Layout Test")
    st.markdown("**Test der neuen Grid-Aufteilung mit Rechteck + 2 Quadrate für Position 0,0 und 0,3**")
    
    # Icon-Style Auswahl
    col1, col2 = st.columns([1, 3])
    with col1:
        icon_style = st.selectbox(
            "Icon-Style:",
            ["ic_ft", "omf"],
            index=0,
            help="ic_ft: Fischertechnik-Icons | omf: OMF-Icons"
        )
    
    with col2:
        st.write(f"**Aktueller Style:** {icon_style}")
    
    # Asset Manager mit gewähltem Style initialisieren
    asset_manager = get_asset_manager(icon_style=icon_style)
    
    # Shopfloor Layout laden
    try:
        config_loader = get_ccu_config_loader()
        layout_data = config_loader.load_shopfloor_layout()
        
        st.subheader("📋 Aktuelle Layout-Konfiguration")
        st.json(layout_data)
        
        st.subheader("🗺️ Aktuelles Shopfloor Layout (3×4 Grid)")
        _show_current_shopfloor_grid(layout_data, asset_manager)
        
        st.subheader("🎯 Neue Grid-Aufteilung (Position 0,0 und 0,3)")
        _show_new_shopfloor_grid(layout_data, asset_manager)
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Shopfloor Layouts: {e}")
        logger.error(f"Shopfloor Layout Test Fehler: {e}")

def _show_current_shopfloor_grid(layout_data, asset_manager):
    """Zeigt das aktuelle 3×4 Grid"""
    grid = layout_data.get("grid", {})
    modules = layout_data.get("modules", [])
    intersections = layout_data.get("intersections", [])
    empty_positions = layout_data.get("empty_positions", [])
    
    rows = grid.get("rows", 3)
    columns = grid.get("columns", 4)
    
    st.write(f"**Aktuelles Grid ({rows}×{columns})** - Alle Positionen als Quadrate")
    
    # Grid Array erstellen
    grid_array = [[None for _ in range(columns)] for _ in range(rows)]
    
    # Module, Intersections und Empty Positions füllen
    for module in modules:
        position = module.get("position", [0, 0])
        col, row = position[0], position[1]
        if 0 <= row < rows and 0 <= col < columns:
            grid_array[row][col] = {"type": "module", "data": module}
    
    for intersection in intersections:
        position = intersection.get("position", [0, 0])
        col, row = position[0], position[1]
        if 0 <= row < rows and 0 <= col < columns:
            grid_array[row][col] = {"type": "intersection", "data": intersection}
    
    for empty in empty_positions:
        position = empty.get("position", [0, 0])
        col, row = position[0], position[1]
        if 0 <= row < rows and 0 <= col < columns:
            grid_array[row][col] = {"type": "empty", "data": empty}
    
    # Aktuelles Grid anzeigen
    _display_current_grid(grid_array, rows, columns, asset_manager)

def _show_new_shopfloor_grid(layout_data, asset_manager):
    """Zeigt das neue Grid mit Rechteck + 2 Quadrate für Position 0,0 und 0,3"""
    st.write("**Neue Aufteilung:** Position 0,0 und 0,3 als Rechteck + 2 Quadrate darunter")
    
    # Test-Layout für neue Aufteilung
    test_layout = {
        "0,0": {
            "type": "split_rectangle",
            "top": {"type": "rectangle", "content": "ORBIS-Logo", "position": "0,0-top"},
            "bottom_left": {"type": "square", "content": "DSP-Info", "position": "0,0-bl"},
            "bottom_right": {"type": "square", "content": "Status", "position": "0,0-br"}
        },
        "0,3": {
            "type": "split_rectangle", 
            "top": {"type": "rectangle", "content": "ORBIS-Logo", "position": "0,3-top"},
            "bottom_left": {"type": "square", "content": "DSP-Info", "position": "0,3-bl"},
            "bottom_right": {"type": "square", "content": "Status", "position": "0,3-br"}
        }
    }
    
    # Neue Grid-Darstellung
    _display_new_grid(test_layout, asset_manager)

def _display_current_grid(grid_array, rows, columns, asset_manager):
    """Zeigt das aktuelle Grid als 3×4 Quadrate - nach OMF2-Vorbild"""
    # Calculate container dimensions maintaining 3:4 aspect ratio (wie in OMF2)
    cell_size = 80  # Base cell size
    
    # Calculate container dimensions
    container_width = columns * cell_size + (columns - 1) * 4  # 4px margin between cells
    container_height = rows * cell_size + (rows - 1) * 4
    
    # Ensure 3:4 aspect ratio (wie in OMF2)
    aspect_ratio = 3 / 4
    if container_width / container_height > aspect_ratio:
        # Too wide, adjust height
        container_height = container_width / aspect_ratio
        cell_size = (container_height - (rows - 1) * 4) / rows
    else:
        # Too tall, adjust width
        container_width = container_height * aspect_ratio
        cell_size = (container_width - (columns - 1) * 4) / columns
    
    html_content = ""
    for row in range(rows):
        for col in range(columns):
            cell = grid_array[row][col]
            
            # Calculate position within container (wie in OMF2)
            x_pos = col * (cell_size + 4)
            y_pos = row * (cell_size + 4)
            
            # Zellinhalt generieren
            if cell:
                cell_type = cell.get("type")
                cell_data = cell.get("data", {})
                
                # Spezielle Behandlung für EMPTY1 (0,0) und EMPTY2 (0,3)
                if cell_type == "empty":
                    empty_id = cell_data.get("id", "")
                    if empty_id == "EMPTY1" and row == 0 and col == 0:
                        # Position 0,0: Neue aufgeteilte Position mit echten SVGs
                        cell_html = _generate_split_position_html("0,0", cell_size, asset_manager)
                    elif empty_id == "EMPTY2" and row == 0 and col == 3:
                        # Position 0,3: Neue aufgeteilte Position mit echten SVGs
                        cell_html = _generate_split_position_html("0,3", cell_size, asset_manager)
                    else:
                        # Andere EMPTY-Positionen: Normal
                        cell_html = asset_manager.get_shopfloor_module_html(empty_id, empty_id, False, size=cell_size)
                elif cell_type == "module":
                    module_id = cell_data.get("id", "")
                    module_type = cell_data.get("type", "")
                    cell_html = asset_manager.get_shopfloor_module_html(module_type, module_id, False, size=cell_size)
                elif cell_type == "intersection":
                    intersection_id = cell_data.get("id", "")
                    cell_html = asset_manager.get_shopfloor_module_html(intersection_id, intersection_id, False, size=cell_size)
                else:
                    cell_html = f'<div style="width: {cell_size}px; height: {cell_size}px; border: 2px solid #ccc; display: flex; align-items: center; justify-content: center; background: #f0f0f0;">{row},{col}</div>'
            else:
                cell_html = f'<div style="width: {cell_size}px; height: {cell_size}px; border: 2px solid #ccc; display: flex; align-items: center; justify-content: center; background: #f0f0f0;">{row},{col}</div>'
            
            html_content += f'<div style="position: absolute; left: {x_pos}px; top: {y_pos}px; width: {cell_size}px; height: {cell_size}px;">{cell_html}</div>'
    
    # Container HTML with fixed 3:4 aspect ratio - transparent background (wie in OMF2)
    container_html = f'<div style="position: relative; width: {container_width}px; height: {container_height}px; margin: 10px auto; border: 2px solid #333;">{html_content}</div>'
    st.markdown(container_html, unsafe_allow_html=True)

def _generate_split_position_html(position, cell_size, asset_manager):
    """Generiert HTML für aufgeteilte Position im Grid mit echten SVGs"""
    gap = 4
    outer_padding = 2  # Padding on the main cell div
    
    # Inner usable width/height for content
    inner_dim = cell_size - 2 * outer_padding
    
    # ORBIS rectangle dimensions
    orbis_rect_width = inner_dim
    orbis_rect_height = (inner_dim - gap) // 2
    
    # Square dimensions (for both width and height)
    square_side = (inner_dim - gap) // 2
    
    # SVG-Icons laden
    orbis_logo_path = asset_manager.get_orbis_logo_path()
    assets_dir = Path(__file__).parent / "omf2" / "assets"
    
    # Icons basierend auf Position auswählen
    if position == "0,0":
        square1_icon_path = assets_dir / "svgs" / "shelves.svg"
        square2_icon_path = assets_dir / "svgs" / "conveyor_belt.svg"
        square1_fallback_text = "DSP"
        square2_fallback_text = "Status"
    else:  # position == "0,3"
        square1_icon_path = assets_dir / "svgs" / "warehouse.svg"
        square2_icon_path = assets_dir / "svgs" / "delivery_truck_speed.svg"
        square1_fallback_text = "Warehouse"
        square2_fallback_text = "Delivery"
    
    # Helper to get SVG HTML
    def _get_svg_html(svg_path, width, height, fallback_text):
        if svg_path and svg_path.exists():
            with open(svg_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # Remove existing width/height attributes to ensure our injected ones take precedence
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r'<svg\1', svg_content, 1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r'<svg\1', svg_content, 1)
                # Inject new width and height
                svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
                return svg_content
        else:
            return f'<div style="width: {width}px; height: {height}px; display: flex; align-items: center; justify-content: center; font-size: 10px; border: 1px dashed #ccc;">{fallback_text}</div>'
    
    # Get SVG HTML for each part, adjusting for inner padding/borders if necessary
    orbis_logo_path_obj = Path(orbis_logo_path) if orbis_logo_path else None
    orbis_logo_svg_html = _get_svg_html(orbis_logo_path_obj, orbis_rect_width - 2, orbis_rect_height - 2, "ORBIS")  # -2 for inner border
    square1_svg_html = _get_svg_html(square1_icon_path, square_side - 2, square_side - 2, square1_fallback_text)  # -2 for inner border
    square2_svg_html = _get_svg_html(square2_icon_path, square_side - 2, square_side - 2, square2_fallback_text)  # -2 for inner border
    
    # Komplettes HTML für aufgeteilte Position mit Flexbox
    return f'''
    <div style="width: {cell_size}px; height: {cell_size}px; border: 2px solid #333; background: white; display: flex; flex-direction: column; justify-content: space-between; padding: {outer_padding}px;">
        <!-- ORBIS-Logo Rechteck oben -->
        <div style="width: {orbis_rect_width}px; height: {orbis_rect_height}px; border: 1px solid #2196f3; display: flex; align-items: center; justify-content: center; background: #e3f2fd;">
            {orbis_logo_svg_html}
        </div>
    
        <!-- Zwei Quadrate darunter -->
        <div style="display: flex; justify-content: space-between; width: {inner_dim}px; height: {square_side}px;">
            <!-- Quadrat 1: Links unten -->
            <div style="width: {square_side}px; height: {square_side}px; border: 1px solid #4caf50; display: flex; align-items: center; justify-content: center; background: #e8f5e8;">
                {square1_svg_html}
            </div>
            <!-- Quadrat 2: Rechts unten -->
            <div style="width: {square_side}px; height: {square_side}px; border: 1px solid #ff9800; display: flex; align-items: center; justify-content: center; background: #fff3e0;">
                {square2_svg_html}
            </div>
        </div>
    </div>
    '''

def _display_new_grid(test_layout, asset_manager):
    """Zeigt das neue Grid mit Rechteck + 2 Quadrate"""
    st.write("**Position 0,0:**")
    _display_split_rectangle("0,0", test_layout["0,0"], asset_manager)
    
    st.write("**Position 0,3:**")
    _display_split_rectangle("0,3", test_layout["0,3"], asset_manager)

def _display_split_rectangle(position, layout_data, asset_manager):
    """Zeigt eine Position als Rechteck + 2 Quadrate (verwendet _generate_split_position_html)"""
    cell_size = 80  # Consistent cell size
    split_html = _generate_split_position_html(position, cell_size, asset_manager)
    st.markdown(split_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
