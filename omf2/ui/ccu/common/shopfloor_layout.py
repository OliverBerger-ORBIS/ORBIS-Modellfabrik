"""
Shopfloor Layout - OMF2 Integration with Streamlit-native Components
=====================================================================

Streamlit-native implementation replacing the previous Bokeh/iframe-based approach.

Features:
- 3x4 Grid with special cells (0,0) and (0,3) 
- OMF2 Asset Manager for SVG icons (ORBIS-Logo, shelves, conveyor_belt, etc.)
- View-mode highlighting for production/storage orders
- Interactive mode with Details buttons for module selection
- No Bokeh, no iframe, no complex event forwarding - just pure Streamlit

Modes:
- view_mode: Display-only with highlighting (used in production/storage orders)
- ccu_configuration: Interactive with Details buttons for module configuration
- interactive: Standard interactivity
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

# OMF2 Imports
from omf2.assets import get_asset_manager
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def show_shopfloor_layout(
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
    title: str = "Shopfloor Layout",
    show_controls: bool = True,
    unique_key: Optional[str] = None,
    mode: str = "interactive",  # "view_mode", "ccu_configuration", "interactive"
) -> None:
    """
    Zeigt das interaktive Shopfloor Layout mit OMF2-Integration (Streamlit-native)

    Args:
        active_module_id: ID des aktiven Moduls (für Hervorhebung)
        active_intersections: Liste aktiver Intersections
        title: Titel der Komponente
        show_controls: Ob Steuerungselemente angezeigt werden sollen
        unique_key: Eindeutiger Key für Streamlit-Komponenten (verhindert Key-Konflikte)
        mode: Verwendungsmodus
            - "view_mode": Nur aktive Module anzeigen, keine Klicks
            - "ccu_configuration": Single/Double Click für Auswahl/Navigation
            - "interactive": Standard-Interaktivität
    """
    st.subheader(f"🏭 {title}")

    # Asset Manager initialisieren
    asset_manager = get_asset_manager()

    # Layout-Konfiguration laden
    config_loader = get_ccu_config_loader()
    layout_config = config_loader.load_shopfloor_layout()

    # Module aus Konfiguration laden
    modules = layout_config.get("modules", [])
    empty_positions = layout_config.get("empty_positions", [])
    intersections = layout_config.get("intersections", [])

    # 3x4 Grid mit st.columns
    for row in range(3):
        cols = st.columns(4)
        for col in range(4):
            with cols[col]:
                # Spezielle Behandlung für Positionen (0,0) und (0,3)
                if (row == 0 and col == 0) or (row == 0 and col == 3):
                    _render_split_cell(row, col, asset_manager, active_module_id, mode, show_controls, unique_key)
                else:
                    # Normale Zelle
                    cell_data = _find_cell_data(row, col, modules, empty_positions, intersections)
                    _render_normal_cell(
                        row, col, cell_data, asset_manager, active_module_id, 
                        active_intersections, mode, show_controls, unique_key
                    )


def _render_split_cell(
    row: int, 
    col: int, 
    asset_manager, 
    active_module_id: Optional[str],
    mode: str,
    show_controls: bool,
    unique_key: Optional[str]
) -> None:
    """Renders split cells (0,0) and (0,3) using Streamlit components"""
    position_id = "EMPTY1" if (row == 0 and col == 0) else "EMPTY2"
    
    # Load SVG icons
    rectangle_icon = _get_module_icon_svg(asset_manager, f"{position_id}_rectangle", 120, 60, None)
    square1_icon = _get_module_icon_svg(asset_manager, f"{position_id}_square1", 60, 60, None)
    square2_icon = _get_module_icon_svg(asset_manager, f"{position_id}_square2", 60, 60, None)
    
    # Display rectangle (ORBIS logo area)
    st.markdown(
        f'<div style="border: 1px solid #87CEEB; background-color: rgba(135, 206, 250, 0.3); '
        f'padding: 5px; text-align: center; height: 80px;">'
        f'{rectangle_icon}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Display two squares below
    subcols = st.columns(2)
    with subcols[0]:
        st.markdown(
            f'<div style="border: 1px solid #e0e0e0; background-color: #FFFFFF; '
            f'padding: 5px; text-align: center; height: 80px;">'
            f'{square1_icon}'
            f'</div>',
            unsafe_allow_html=True
        )
    with subcols[1]:
        st.markdown(
            f'<div style="border: 1px solid #e0e0e0; background-color: #FFFFFF; '
            f'padding: 5px; text-align: center; height: 80px;">'
            f'{square2_icon}'
            f'</div>',
            unsafe_allow_html=True
        )


def _render_normal_cell(
    row: int,
    col: int,
    cell_data: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str],
    active_intersections: Optional[list],
    mode: str,
    show_controls: bool,
    unique_key: Optional[str]
) -> None:
    """Renders a normal cell using Streamlit components"""
    
    if not cell_data:
        # Empty cell
        st.markdown(
            f'<div style="border: 1px solid #e0e0e0; background-color: #FFFFFF; '
            f'padding: 10px; text-align: center; height: 160px;">'
            f'<p style="color: #999; margin-top: 60px;">Empty</p>'
            f'</div>',
            unsafe_allow_html=True
        )
        return
    
    cell_type = cell_data.get("type", "unknown")
    cell_id = cell_data.get("id", f"{row}-{col}")
    
    # Load icon
    icon_svg = _get_module_icon_svg(asset_manager, cell_type, 86, 86, cell_data)
    
    # Determine highlighting
    is_active = active_module_id and cell_data.get("id") == active_module_id
    is_selected = st.session_state.get("selected_module_id") == cell_id
    
    # Determine border and background based on state
    if is_selected and mode != "view_mode":
        border_color = "#FF9800"
        border_width = "3px"
        bg_color = "rgba(255, 152, 0, 0.1)"
    elif is_active:
        border_color = "#FF9800"
        border_width = "4px"
        bg_color = "#FFFFFF"
    else:
        border_color = "#e0e0e0"
        border_width = "1px"
        bg_color = "#FFFFFF"
    
    # Display cell
    st.markdown(
        f'<div style="border: {border_width} solid {border_color}; background-color: {bg_color}; '
        f'padding: 10px; text-align: center; height: 160px;">'
        f'<div style="margin: 20px 0;">{icon_svg}</div>'
        f'<p style="font-weight: bold; font-size: 12px; margin: 5px 0;">{cell_id}</p>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Add Details button for interactive modes
    if mode != "view_mode" and show_controls:
        button_key = f"details_{unique_key or 'default'}_{row}_{col}"
        if st.button("📋 Details", key=button_key, use_container_width=True):
            st.session_state.selected_module_id = cell_id
            st.session_state.selected_module_type = cell_type
            st.session_state.show_module_details = True
            st.rerun()


def _generate_omf2_svg_grid_with_roads(
    layout_config: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
    mode: str = "interactive",
) -> str:
    """
    DEPRECATED: This function is no longer used.
    The shopfloor layout now uses pure Streamlit components (st.columns).
    Kept for backward compatibility only.
    """
    logger.warning("_generate_omf2_svg_grid_with_roads is deprecated and should not be called")
    return ""


# API-Kompatibilität: Ursprüngliche Funktion als Alias
def _generate_omf2_svg_grid(
    layout_config: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
) -> str:
    """
    DEPRECATED: This function is no longer used.
    The shopfloor layout now uses pure Streamlit components (st.columns).
    Kept for backward compatibility only.
    """
    logger.warning("_generate_omf2_svg_grid is deprecated and should not be called")
    return ""


def _generate_roads_layer(
    layout_config: Dict[str, Any],
    grid_width: int,
    grid_height: int,
    cell_width: int,
    cell_height: int,
    active_intersections: Optional[list] = None,
) -> str:
    """
    DEPRECATED: This function is no longer used.
    Roads are not displayed in the new Streamlit-native implementation.
    Kept for backward compatibility only.
    """
    logger.warning("_generate_roads_layer is deprecated and should not be called")
    return ""


def _generate_split_cell_svg(
    row: int,
    col: int,
    x_pos: int,
    y_pos: int,
    cell_width: int,
    cell_height: int,
    asset_manager,
    active_module_id: Optional[str],
) -> str:
    """
    DEPRECATED: This function is no longer used.
    Split cells are now rendered using Streamlit components.
    Kept for backward compatibility only.
    """
    logger.warning("_generate_split_cell_svg is deprecated and should not be called")
    return ""


def _generate_normal_cell_svg(
    row: int,
    col: int,
    x_pos: int,
    y_pos: int,
    cell_width: int,
    cell_height: int,
    cell_data: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str],
) -> str:
    """
    DEPRECATED: This function is no longer used.
    Normal cells are now rendered using Streamlit components.
    Kept for backward compatibility only.
    """
    logger.warning("_generate_normal_cell_svg is deprecated and should not be called")
    return ""


def _find_cell_data(
    row: int, col: int, modules: list, empty_positions: list, intersections: list
) -> Optional[Dict[str, Any]]:
    """Findet die Daten für eine Grid-Position"""

    logger.debug(f"🔍 DEBUG: Suche Position [{row},{col}]")

    # Module suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for module in modules:
        position = module.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            logger.debug(f"✅ Modul gefunden - Position: {position}, ID: {module.get('id')}")
            return {"type": module.get("type", "unknown"), "id": module.get("id", "unknown"), "data": module}

    # Intersections suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for intersection in intersections:
        position = intersection.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            logger.debug(f"✅ Intersection gefunden - Position: {position}, ID: {intersection.get('id')}")
            return {"type": "intersection", "id": intersection.get("id", "unknown"), "data": intersection}

    # Empty positions suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for empty in empty_positions:
        position = empty.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            print(f"✅ DEBUG: Empty Position gefunden - Position: {position}")
            return {"type": "empty", "id": empty.get("id", "unknown"), "data": empty}

    logger.warning(f"❌ DEBUG: Keine Daten gefunden für Position [{row},{col}]")
    return None


def _get_single_intersection_icon(
    module_type: str, width: int, height: int, cell_data: dict = None, asset_manager=None
) -> str:
    """Lädt ein einzelnes Icon für eine Intersection - VEREINFACHT ohne Spezial-Effekte"""
    try:
        # Intersection-ID aus cell_data ermitteln
        intersection_id = "1"  # Default
        if cell_data and "data" in cell_data:
            intersection_id = cell_data["data"].get("id", "1")
        elif cell_data:
            intersection_id = cell_data.get("id", "1")

        # Asset Manager verwenden für Icon-Pfad (wie alle anderen Module)
        if asset_manager:
            icon_path = asset_manager.get_module_icon_path(intersection_id)
        else:
            # Fallback falls kein Asset Manager übergeben wurde
            assets_dir = Path(__file__).parent.parent.parent.parent / "assets"
            intersection_icons = {
                "1": "fiber_manual_record_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
                "2": "rotate_right_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
                "3": "rotate_left_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
                "4": "mode_standby_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
            }
            icon_file = intersection_icons.get(intersection_id, "add_cross_10px_whitebg.svg")
            icon_path = assets_dir / "svgs" / icon_file

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as f:
                svg_content = f.read()
                # ViewBox-bewusste Skalierung - keine Verzerrung!
                svg_content = _scale_svg_properly(svg_content, width, height)
                return svg_content
        else:
            return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">+</text>'
    except Exception as e:
        logger.error(f"Error loading intersection icon: {e}")
        return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">+</text>'


def _get_orbis_logo_svg(asset_manager, width: int, height: int) -> str:
    """Lädt das ORBIS-Logo SVG - VEREINFACHT mit Asset Manager"""
    try:
        # Asset Manager hat bereits ORBIS-Logo-Mapping
        orbis_logo_path = asset_manager.get_empty_position_asset_by_name("ORBIS")
        if orbis_logo_path and Path(orbis_logo_path).exists():
            with open(orbis_logo_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # SVG-Größe anpassen
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
                return svg_content
    except Exception as e:
        logger.warning(f"Could not load ORBIS logo: {e}")

    return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="12" fill="#164194">ORBIS</text>'


def _scale_svg_properly(svg_content: str, width: int, height: int) -> str:
    """Skaliert SVG korrekt basierend auf ViewBox - keine Verzerrung!"""
    try:
        # ViewBox aus SVG extrahieren
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        if viewbox_match:
            viewbox = viewbox_match.group(1)
            # ViewBox-Parameter extrahieren: "x y width height"
            viewbox_parts = viewbox.split()
            if len(viewbox_parts) == 4:
                vb_x, vb_y, vb_width, vb_height = map(float, viewbox_parts)

                # Seitenverhältnis der ViewBox berechnen
                vb_aspect_ratio = vb_width / vb_height
                target_aspect_ratio = width / height

                # Skalierung basierend auf Seitenverhältnis
                if vb_aspect_ratio > target_aspect_ratio:
                    # ViewBox ist breiter - Höhe anpassen
                    scale = width / vb_width
                    new_height = int(vb_height * scale)
                    # SVG mit korrekter Skalierung
                    svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{new_height}"', 1)
                else:
                    # ViewBox ist höher - Breite anpassen
                    scale = height / vb_height
                    new_width = int(vb_width * scale)
                    # SVG mit korrekter Skalierung
                    svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = svg_content.replace("<svg", f'<svg width="{new_width}" height="{height}"', 1)
            else:
                # Fallback: Standard-Skalierung
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
        else:
            # Keine ViewBox gefunden - Standard-Skalierung
            svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
            svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
            svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)

        return svg_content
    except Exception as e:
        logger.warning(f"Error scaling SVG: {e}")
        # Fallback: Standard-Skalierung
        svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
        svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
        return svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)


def _get_module_icon_svg(asset_manager, module_type: str, width: int, height: int, cell_data: dict = None) -> str:
    """Lädt das SVG-Icon für ein Modul - ViewBox-bewusste Skalierung"""
    try:
        # Spezielle Behandlung für Intersections - ein Icon pro Intersection
        if module_type == "intersection":
            # Ein Icon pro Intersection basierend auf der ID
            return _get_single_intersection_icon(module_type, width, height, cell_data, asset_manager)

        # Für alle anderen Module: Asset Manager verwenden
        icon_path = asset_manager.get_module_icon_path(module_type)

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # ViewBox-bewusste Skalierung - keine Verzerrung!
                svg_content = _scale_svg_properly(svg_content, width, height)
                return svg_content
    except Exception as e:
        logger.warning(f"Could not load icon for {module_type}: {e}")

    return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">{module_type}</text>'


def _process_grid_events(unique_key: Optional[str] = None):
    """
    DEPRECATED: This function is no longer used.
    Events are now handled natively by Streamlit buttons.
    Kept for backward compatibility only.
    """
    logger.warning("_process_grid_events is deprecated and should not be called")
    pass


def _handle_grid_event(event_data: Dict[str, Any]):
    """
    DEPRECATED: This function is no longer used.
    Events are now handled natively by Streamlit buttons.
    Kept for backward compatibility only.
    """
    logger.warning("_handle_grid_event is deprecated and should not be called")
    pass


# Export für OMF2-Integration
__all__ = ["show_shopfloor_layout"]
