"""
Shopfloor Layout - Stable View-Only Implementation
===================================================

Minimal, robust implementation with fixed aspect ratio and gapless grid.

Features:
- Fixed 4:3 aspect ratio (configurable, default 800x600)
- Gapless 4x3 grid (CSS Grid with gap: 0)
- Single HTML block rendering (no Streamlit columns creating gaps)
- View-only highlighting for active modules and intersections
- Graceful fallback if config or assets are unavailable
- No Bokeh, no iframe, no CustomJS dependencies
- API compatible with existing callers (production/storage subtabs)

Implementation:
- Uses st.components.v1.html() for rendering
- Falls back to st.markdown() if components unavailable
- Inline CSS for complete control over layout
- Reuses existing helper functions for config/asset loading
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
    show_controls: bool = False,
    unique_key: Optional[str] = None,
    mode: str = "view_mode",
    max_width: int = 800,
    max_height: int = 600,
    layout_config: Optional[dict] = None,
    asset_manager: Optional[object] = None,
    route_points: Optional[list] = None,
    agv_progress: float = 0.0,
    on_cell_click: Optional[callable] = None,
    enable_click: bool = False,
) -> None:
    """
    Display stable, view-only shopfloor layout with fixed aspect ratio and gapless grid.

    Args:
        active_module_id: ID of active module (for highlighting)
        active_intersections: List of active intersection IDs
        title: Component title
        show_controls: Show control elements (default: False for stable view-only mode)
        unique_key: Unique key for Streamlit components
        mode: Usage mode (kept for API compatibility, defaults to "view_mode")
        max_width: Container width in pixels (default: 800)
        max_height: Container height in pixels (default: 600)
        layout_config: Optional layout configuration dict (loads from config if None)
        asset_manager: Optional asset manager instance (loads if None)
        route_points: Optional list of (x, y) pixel coordinates for AGV route visualization
        agv_progress: Progress along route (0.0 to 1.0) for AGV marker positioning
        on_cell_click: Optional callback function for cell click events
        enable_click: Enable click-to-select functionality (default: False)
    """
    st.subheader(f"🏭 {title}")
    
    # Show hint if click is enabled
    if enable_click:
        st.info("💡 Click on any position in the grid to view its details below")

    # Load layout configuration if not provided
    if layout_config is None:
        try:
            config_loader = get_ccu_config_loader()
            layout_config = config_loader.load_shopfloor_layout()
        except Exception as e:
            logger.error(f"Failed to load shopfloor layout config: {e}")
            layout_config = None

    # Check if config is valid
    if not layout_config or not isinstance(layout_config, dict):
        st.error("❌ Shopfloor layout configuration not available. Please check configuration files.")
        # Render empty grid as fallback
        layout_config = {"modules": [], "empty_positions": [], "intersections": []}

    # Load asset manager if not provided
    if asset_manager is None:
        try:
            asset_manager = get_asset_manager()
        except Exception as e:
            logger.warning(f"Failed to load asset manager: {e}")
            asset_manager = None

    # Extract data from config
    modules = layout_config.get("modules", [])
    fixed_positions = layout_config.get("fixed_positions", [])  # New structure (v2.0)
    # Fallback for old structure
    if not fixed_positions:
        fixed_positions = layout_config.get("empty_positions", [])
    intersections = layout_config.get("intersections", [])

    # Generate HTML grid
    html_content = _generate_html_grid(
        modules=modules,
        fixed_positions=fixed_positions,
        intersections=intersections,
        asset_manager=asset_manager,
        active_module_id=active_module_id,
        active_intersections=active_intersections,
        max_width=max_width,
        max_height=max_height,
        route_points=route_points,
        agv_progress=agv_progress,
        enable_click=enable_click,
        unique_key=unique_key or "shopfloor",
    )

    # Render using st.components or fallback to markdown
    try:
        # Use experimental query params for click communication if enabled
        if enable_click:
            # Check for clicked position in query params
            try:
                query_params = st.query_params
                if "pos" in query_params:
                    clicked_pos = query_params["pos"]
                    st.session_state.clicked_position = f"Position {clicked_pos}"
                    # Clear the query param after processing
                    del st.query_params["pos"]
            except:
                pass
        
        st.components.v1.html(html_content, height=max_height + 20, scrolling=False)
    except Exception as e:
        logger.warning(f"st.components.v1.html failed, falling back to markdown: {e}")
        st.markdown(html_content, unsafe_allow_html=True)


def _generate_html_grid(
    modules: list,
    fixed_positions: list,
    intersections: list,
    asset_manager,
    active_module_id: Optional[str],
    active_intersections: Optional[list],
    max_width: int,
    max_height: int,
    route_points: Optional[list] = None,
    agv_progress: float = 0.0,
    enable_click: bool = False,
    unique_key: str = "shopfloor",
) -> str:
    """
    Generate complete HTML grid with inline CSS for gapless layout.

    Returns a single HTML string containing the entire 4x3 grid.
    """
    # Calculate cell dimensions - use square cells (200x200px default)
    cell_size = 200  # Default cell size
    cell_width = cell_size
    cell_height = cell_size
    
    # Update container dimensions to match grid
    max_width = cell_width * 4
    max_height = cell_height * 3

    # CSS styles
    css = f"""
    <style>
        .shopfloor-container {{
            width: {max_width}px;
            height: {max_height}px;
            display: grid;
            grid-template-columns: repeat(4, {cell_width}px);
            grid-template-rows: repeat(3, {cell_height}px);
            gap: 0;
            border: 2px solid #ddd;
            background: white;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            position: relative;
            overflow: visible;
        }}
        .shopfloor-container::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 2px;
            background: #ddd;
            pointer-events: none;
        }}
        .cell {{
            width: {cell_width}px;
            height: {cell_height}px;
            border: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 8px;
            box-sizing: border-box;
            background: white;
            position: relative;
            {"cursor: pointer; transition: background-color 0.2s ease;" if enable_click else ""}
        }}
        {"" if not enable_click else '''
        .cell:hover {
            background: rgba(255, 152, 0, 0.1);
            border-color: #FF9800;
        }
        '''}
        .cell-active {{
            border: 4px solid #FF9800 !important;
            background: white;
            z-index: 1;
        }}
        .cell-intersection-active {{
            border: 3px dashed #FF9800 !important;
        }}
        .cell-empty {{
            background: rgba(135, 206, 235, 0.1);
        }}
        .cell-split {{
            display: grid;
            grid-template-rows: 1fr 1fr;
            grid-template-columns: 1fr 1fr;
            gap: 2px;
            padding: 2px;
        }}
        .split-top {{
            grid-column: 1 / 3;
            background: rgba(135, 206, 235, 0.3);
            border: 1px solid #87CEEB;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .split-bottom {{
            background: white;
            border: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .cell-label {{
            font-size: 11px;
            font-weight: bold;
            text-align: center;
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
            position: absolute;
            bottom: 8px;
            left: 0;
            right: 0;
        }}
        .icon-container {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 80%;
            height: 80%;
            flex-shrink: 0;
        }}
        .icon-container img {{
            object-fit: contain;
            max-width: 100%;
            max-height: 100%;
        }}
        /* SVG Overlay for routes */
        .route-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }}
        .route-path {{
            fill: none;
            stroke: #FF9800;
            stroke-width: 4;
            stroke-linecap: round;
            stroke-linejoin: round;
        }}
        .agv-marker {{
            fill: #FF9800;
            stroke: white;
            stroke-width: 2;
        }}
    </style>
    """

    # Generate grid cells
    cells_html = []
    for row in range(3):
        for col in range(4):
            cell_html = _generate_cell_html(
                row,
                col,
                modules,
                fixed_positions,
                intersections,
                asset_manager,
                active_module_id,
                active_intersections,
                cell_width,
                cell_height,
                enable_click,
                unique_key,
            )
            cells_html.append(cell_html)

    # Generate SVG overlay for route visualization
    svg_overlay = ""
    if route_points and len(route_points) >= 2:
        svg_overlay = _generate_route_overlay(route_points, agv_progress, max_width, max_height)
    
    # Add JavaScript for click handling if enabled
    javascript = ""
    if enable_click:
        javascript = f"""
        <script>
            // Handle cell clicks by setting URL query parameter
            document.addEventListener('DOMContentLoaded', function() {{
                const cells = document.querySelectorAll('.cell[data-position]');
                cells.forEach(cell => {{
                    cell.addEventListener('click', function() {{
                        const position = this.getAttribute('data-position');
                        // Try to communicate with parent Streamlit app
                        if (window.parent) {{
                            // Use postMessage to send to parent
                            window.parent.postMessage({{
                                type: 'shopfloor_click',
                                position: position
                            }}, '*');
                        }}
                        // Visual feedback
                        cells.forEach(c => c.style.outline = 'none');
                        this.style.outline = '3px solid #FF9800';
                        this.style.outlineOffset = '-3px';
                    }});
                }});
            }});
        </script>
        """
    
    # Combine into complete HTML
    html = f"""
    {css}
    <div class="shopfloor-container">
        {''.join(cells_html)}
        {svg_overlay}
    </div>
    {javascript}
    """

    return html


def _generate_route_overlay(
    route_points: list,
    agv_progress: float,
    max_width: int,
    max_height: int,
) -> str:
    """
    Generate SVG overlay with route polyline and AGV/FTS marker icon
    
    Args:
        route_points: List of (x, y) pixel coordinates
        agv_progress: Progress along route (0.0 to 1.0)
        max_width: Container width
        max_height: Container height
        
    Returns:
        HTML string with SVG overlay
    """
    if not route_points or len(route_points) < 2:
        return ""
    
    # Convert points to SVG polyline format
    points_str = " ".join([f"{x},{y}" for x, y in route_points])
    
    # Calculate AGV marker position based on progress
    agv_position = None
    if 0.0 <= agv_progress <= 1.0:
        from omf2.ui.ccu.common.route_utils import point_on_polyline
        agv_position = point_on_polyline(route_points, agv_progress)
    
    # Generate AGV marker SVG with FTS icon
    agv_marker_svg = ""
    if agv_position:
        agv_x, agv_y = agv_position
        # Load FTS icon and embed it at the AGV position
        try:
            from omf2.assets.asset_manager import get_asset_manager
            from pathlib import Path
            
            asset_manager = get_asset_manager()
            fts_icon_path = asset_manager.get_module_icon_path('FTS')
            
            if fts_icon_path and Path(fts_icon_path).exists():
                with open(fts_icon_path, 'r', encoding='utf-8') as f:
                    fts_svg_content = f.read()
                    # Extract SVG content (without <?xml> declaration)
                    if '<?xml' in fts_svg_content:
                        fts_svg_content = fts_svg_content.split('?>', 1)[1].strip()
                    
                    # Replace SVG tag with g tag for embedding, position at agv_x, agv_y
                    # FTS icon is 24x24, scale it to 32x32 for better visibility
                    icon_size = 32
                    half_size = icon_size / 2
                    
                    # Create a group with transform to position and scale the icon
                    agv_marker_svg = f'''
                    <g transform="translate({agv_x - half_size}, {agv_y - half_size}) scale({icon_size/24})">
                        {fts_svg_content.replace('<svg', '<g').replace('</svg>', '</g>').replace('width="24"', '').replace('height="24"', '')}
                    </g>
                    '''
            else:
                # Fallback to circle if FTS icon not found
                agv_marker_svg = f'<circle class="agv-marker" cx="{agv_x}" cy="{agv_y}" r="12"/>'
        except Exception as e:
            logger.warning(f"Could not load FTS icon for AGV marker: {e}")
            # Fallback to circle
            agv_marker_svg = f'<circle class="agv-marker" cx="{agv_x}" cy="{agv_y}" r="12"/>'
    
    svg = f"""
    <svg class="route-overlay" viewBox="0 0 {max_width} {max_height}" xmlns="http://www.w3.org/2000/svg">
        <polyline class="route-path" points="{points_str}"/>
        {agv_marker_svg}
    </svg>
    """
    
    return svg


def _generate_cell_html(
    row: int,
    col: int,
    modules: list,
    fixed_positions: list,
    intersections: list,
    asset_manager,
    active_module_id: Optional[str],
    active_intersections: Optional[list],
    cell_width: int,
    cell_height: int,
    enable_click: bool = False,
    unique_key: str = "shopfloor",
) -> str:
    """Generate HTML for a single grid cell."""

    # Handle special split cells at (0,0) and (0,3)
    if (row == 0 and col == 0) or (row == 0 and col == 3):
        return _generate_split_cell_html(row, col, fixed_positions, asset_manager, cell_width, cell_height, enable_click)

    # Find cell data
    cell_data = _find_cell_data(row, col, modules, fixed_positions, intersections)

    # Determine cell classes and styling
    cell_classes = ["cell"]
    if not cell_data:
        cell_classes.append("cell-empty")

    # Check if this module is active
    if cell_data and active_module_id:
        cell_id = cell_data.get("id", "")
        if cell_id == active_module_id:
            cell_classes.append("cell-active")

    # Check if this is an active intersection
    if cell_data and cell_data.get("type") == "intersection" and active_intersections:
        intersection_id = cell_data.get("id", "")
        if intersection_id in active_intersections:
            cell_classes.append("cell-intersection-active")

    # Generate icon
    icon_svg = ""
    cell_label = ""
    if cell_data:
        cell_type = cell_data.get("type", "unknown")
        cell_id = cell_data.get("id", "")
        
        # FIX: Show labels for all cells including intersections
        # This makes it clearer where routes go and doesn't rely on embedded SVG text
        cell_label = cell_id

        # Get icon SVG (90% of cell width/height for padding)
        icon_width = int(cell_width * 0.7)
        icon_height = int(cell_height * 0.7)
        icon_svg = _get_module_icon_svg(asset_manager, cell_type, icon_width, icon_height, cell_data)
    else:
        cell_label = ""

    # Add data attribute for position if click is enabled
    data_attr = f'data-position="[{row},{col}]"' if enable_click else ''

    # Build cell HTML
    cell_html = f"""
    <div class="{' '.join(cell_classes)}" {data_attr}>
        <div class="icon-container">
            {icon_svg}
        </div>
        {f'<div class="cell-label">{cell_label}</div>' if cell_label else ''}
    </div>
    """

    return cell_html


def _generate_split_cell_html(
    row: int,
    col: int,
    fixed_positions: list,
    asset_manager,
    cell_width: int,
    cell_height: int,
    enable_click: bool = False,
) -> str:
    """Generate HTML for split cells (0,0) and (0,3)."""

    # Find fixed position config for this position
    fixed_config = None
    for fixed in fixed_positions:
        if fixed.get("position") == [row, col]:
            fixed_config = fixed
            break

    # Default icons if config not found
    rectangle_type = "ORBIS"
    square1_type = "shelves"
    square2_type = "conveyor_belt"

    if fixed_config:
        assets = fixed_config.get("assets", {})
        rectangle_type = assets.get("rectangle", rectangle_type)
        square1_type = assets.get("square1", square1_type)
        square2_type = assets.get("square2", square2_type)

    # Generate icons (smaller for split cells)
    rect_width = int(cell_width * 0.8)
    rect_height = int(cell_height * 0.4)
    square_width = int(cell_width * 0.4)
    square_height = int(cell_height * 0.4)

    rectangle_svg = _get_split_cell_icon(asset_manager, rectangle_type, rect_width, rect_height)
    square1_svg = _get_split_cell_icon(asset_manager, square1_type, square_width, square_height)
    square2_svg = _get_split_cell_icon(asset_manager, square2_type, square_width, square_height)

    # Add data attribute for position if click is enabled
    data_attr = f'data-position="[{row},{col}]"' if enable_click else ''

    cell_html = f"""
    <div class="cell cell-split" {data_attr}>
        <div class="split-top">
            {rectangle_svg}
        </div>
        <div class="split-bottom">
            {square1_svg}
        </div>
        <div class="split-bottom">
            {square2_svg}
        </div>
    </div>
    """

    return cell_html


def _get_split_cell_icon(asset_manager, icon_type: str, width: int, height: int) -> str:
    """Get icon for split cell components with fallback to empty.svg."""
    try:
        if asset_manager:
            # Try to get icon from asset manager
            if icon_type == "ORBIS":
                icon_path = asset_manager.get_empty_position_asset_by_name("ORBIS")
            else:
                icon_path = asset_manager.get_empty_position_asset_by_name(icon_type)

            if icon_path and Path(icon_path).exists():
                with open(icon_path, encoding="utf-8") as f:
                    svg_content = f.read()
                    svg_content = _scale_svg_properly(svg_content, width, height)
                    return svg_content
            
            # Fallback to empty.svg if icon not found
            empty_svg_path = Path(asset_manager.svgs_dir) / "empty.svg"
            if empty_svg_path.exists():
                with open(empty_svg_path, encoding="utf-8") as f:
                    svg_content = f.read()
                    svg_content = _scale_svg_properly(svg_content, width, height)
                    return svg_content
                    
    except Exception as e:
        logger.debug(f"Could not load split cell icon {icon_type}: {e}")

    # Final fallback: text representation
    return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">{icon_type}</text>'


def _render_split_cell(
    row: int,
    col: int,
    asset_manager,
    active_module_id: Optional[str],
    mode: str,
    show_controls: bool,
    unique_key: Optional[str],
) -> None:
    """
    DEPRECATED: This function is no longer used.
    Split cells are now rendered as part of the HTML grid.
    Kept for backward compatibility only.
    """
    logger.warning("_render_split_cell is deprecated and should not be called")
    pass


def _render_normal_cell(
    row: int,
    col: int,
    cell_data: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str],
    active_intersections: Optional[list],
    mode: str,
    show_controls: bool,
    unique_key: Optional[str],
) -> None:
    """
    DEPRECATED: This function is no longer used.
    Normal cells are now rendered as part of the HTML grid.
    Kept for backward compatibility only.
    """
    logger.warning("_render_normal_cell is deprecated and should not be called")
    pass


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
    row: int, col: int, modules: list, fixed_positions: list, intersections: list
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

    # Fixed positions suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for fixed in fixed_positions:
        position = fixed.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            logger.debug(f"✅ Fixed Position gefunden - Position: {position}, ID: {fixed.get('id')}")
            return {"type": "fixed", "id": fixed.get("id", "unknown"), "data": fixed}

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
    """Lädt das SVG-Icon für ein Modul - ViewBox-bewusste Skalierung mit fallback zu empty.svg"""
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
        
        # Fallback to empty.svg if icon not found
        empty_svg_path = Path(asset_manager.svgs_dir) / "empty.svg"
        if empty_svg_path.exists():
            with open(empty_svg_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                svg_content = _scale_svg_properly(svg_content, width, height)
                return svg_content
                
    except Exception as e:
        logger.warning(f"Could not load icon for {module_type}: {e}")

    # Final fallback: text representation
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
