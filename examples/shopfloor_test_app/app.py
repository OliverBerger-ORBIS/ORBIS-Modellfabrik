"""
Streamlit test app: interactive, scalable SVG shopfloor layout demo.

- Uses examples/shopfloor_test_app/shopfloor_layout.json as default layout.
- Uses omf2.assets.asset_manager.get_asset_manager() to fetch inline SVG icons where available.
- Implements show_shopfloor_layout(...) API for embedding in other code.
"""

import sys
from pathlib import Path

# Add project root to Python path for imports (must be before other imports)
_here = Path(__file__).resolve()
project_root = _here.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import html  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
from typing import List, Optional, Tuple  # noqa: E402

import streamlit as st  # noqa: E402

from examples.shopfloor_test_app import route_utils  # noqa: E402

# try to import asset manager from omf2 (if running in repo environment)
try:
    from omf2.assets.asset_manager import get_asset_manager

    ASSET_MANAGER = get_asset_manager()
except Exception:
    ASSET_MANAGER = None

HERE = pathlib.Path(__file__).parent
LAYOUT_PATH = HERE / "shopfloor_layout.json"
CELL_SIZE = 200
GRID_W = 4
GRID_H = 3
# Add 4px padding (2px on each side) for uniform highlighting at edges
CANVAS_W = CELL_SIZE * GRID_W + 4
CANVAS_H = CELL_SIZE * GRID_H + 4
CANVAS_PADDING = 2

# Visual spec derived from user message (colors & sizes)
VIS_SPEC = {
    (0, 0): {"name": "COMPANY", "w": 200, "h": 100, "color": "#cfe6ff"},  # blaues Rechteck
    (0, 1): {"name": "MILL", "w": 200, "h": 200, "color": "#ffd5d5"},  # rotes Quadrat
    (0, 2): {"name": "AIQS", "w": 200, "h": 200, "color": "#ffd5d5"},
    (0, 3): {"name": "SOFTWARE", "w": 200, "h": 100, "color": "#cfe6ff"},
    (1, 0): {"name": "HBW", "w": 200, "h": 300, "color": "#d7f0c8"},  # grünes Compound
    (1, 1): {"name": "INTERSECTION-1", "w": 200, "h": 200, "color": "#e3d0ff"},
    (1, 2): {"name": "INTERSECTION-2", "w": 200, "h": 200, "color": "#e3d0ff"},
    (1, 3): {"name": "DPS", "w": 200, "h": 300, "color": "#d7f0c8"},  # grünes Compound
    (2, 0): {"name": "DRILL", "w": 200, "h": 200, "color": "#ffd5d5"},
    (2, 1): {"name": "INTERSECTION-3", "w": 200, "h": 200, "color": "#e3d0ff"},
    (2, 2): {"name": "INTERSECTION-4", "w": 200, "h": 200, "color": "#e3d0ff"},
    (2, 3): {"name": "CHRG", "w": 200, "h": 200, "color": "#ffd5d5"},
}


def load_layout(path: pathlib.Path = LAYOUT_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _scale_svg_properly(svg_content: str, target_width: int, target_height: int) -> tuple:
    """
    Scale SVG properly based on viewBox to avoid distortion.
    Returns (scaled_svg_content, actual_width, actual_height)
    """
    import re

    try:
        # Extract viewBox from SVG
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        if viewbox_match:
            viewbox = viewbox_match.group(1)
            viewbox_parts = viewbox.split()
            if len(viewbox_parts) == 4:
                vb_x, vb_y, vb_width, vb_height = map(float, viewbox_parts)

                # Calculate aspect ratios
                vb_aspect_ratio = vb_width / vb_height
                target_aspect_ratio = target_width / target_height

                # Scale based on aspect ratio to avoid distortion
                if vb_aspect_ratio > target_aspect_ratio:
                    # ViewBox is wider - scale by width
                    scale = target_width / vb_width
                    new_height = int(vb_height * scale)
                    new_width = target_width
                else:
                    # ViewBox is taller - scale by height
                    scale = target_height / vb_height
                    new_width = int(vb_width * scale)
                    new_height = target_height

                # Remove existing width/height and add new ones
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = svg_content.replace("<svg", f'<svg width="{new_width}" height="{new_height}"', 1)
                return svg_content, new_width, new_height

        # Fallback: use target dimensions
        svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
        svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
        svg_content = svg_content.replace("<svg", f'<svg width="{target_width}" height="{target_height}"', 1)
        return svg_content, target_width, target_height
    except Exception:
        return svg_content, target_width, target_height


def _get_icon_svg(
    module_type: str, target_width: int, target_height: int, entity_type: str = None, cell_size: Tuple[int, int] = None
) -> str:
    """
    Load and scale icon from asset manager with proper centering.
    
    For fixed_positions: General scaling approach:
    1. Find limiting factor (width or height) by comparing SVG aspect ratio with cell aspect ratio
    2. Scale SVG to 100% of limiting factor
    3. Apply 80% ratio
    4. Return scaled SVG
    """
    if not ASSET_MANAGER:
        return ""

    try:
        # Use get_asset_content with scoped=True as in production
        icon_svg = ASSET_MANAGER.get_asset_content(module_type, scoped=True)
        if icon_svg:
            # For fixed_positions, use general scaling approach
            if entity_type == "fixed_position" and cell_size:
                import re

                cell_width, cell_height = cell_size
                cell_aspect_ratio = cell_width / cell_height

                # Extract viewBox from SVG to determine aspect ratio
                viewbox_match = re.search(r'viewBox="([^"]*)"', icon_svg)
                if viewbox_match:
                    viewbox_parts = viewbox_match.group(1).split()
                    if len(viewbox_parts) >= 4:
                        vb_width, vb_height = float(viewbox_parts[2]), float(viewbox_parts[3])
                        svg_aspect_ratio = vb_width / vb_height

                        # Determine limiting factor: if SVG is wider relative to cell, width is limiting
                        # Otherwise, height is limiting
                        if svg_aspect_ratio > cell_aspect_ratio:
                            # Width is limiting factor
                            # Step 1: Scale to 100% width
                            scaled_width_100 = cell_width
                            scaled_height_100 = int(cell_width / svg_aspect_ratio)
                        else:
                            # Height is limiting factor
                            # Step 1: Scale to 100% height
                            scaled_height_100 = cell_height
                            scaled_width_100 = int(cell_height * svg_aspect_ratio)

                        # Step 2: Apply 80% ratio to both dimensions
                        final_width = int(scaled_width_100 * 0.8)
                        final_height = int(scaled_height_100 * 0.8)

                        # Scale SVG to final dimensions
                        scaled_svg, actual_w, actual_h = _scale_svg_properly(icon_svg, final_width, final_height)
                        return scaled_svg

                # Fallback: use target dimensions if viewBox parsing fails
                scaled_svg, actual_w, actual_h = _scale_svg_properly(icon_svg, target_width, target_height)
                return scaled_svg
            else:
                scaled_svg, actual_w, actual_h = _scale_svg_properly(icon_svg, target_width, target_height)
                return scaled_svg
    except Exception:
        pass

    return ""


def cell_anchor(row: int, col: int) -> Tuple[int, int]:
    return col * CELL_SIZE + CANVAS_PADDING, row * CELL_SIZE + CANVAS_PADDING


def center_of_cell(row: int, col: int) -> Tuple[int, int]:
    x, y = cell_anchor(row, col)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2


# Helper functions for JSON-based configuration
def _get_entity_at_position(layout: dict, row: int, col: int) -> Optional[dict]:
    """Find entity (module, fixed_position, or intersection) at given position."""
    # Check modules first
    for mod in layout.get("modules", []):
        if mod.get("position") == [row, col]:
            return {"type": "module", "data": mod}
    # Check fixed_positions
    for fixed in layout.get("fixed_positions", []):
        if fixed.get("position") == [row, col]:
            return {"type": "fixed_position", "data": fixed}
    # Check intersections
    for inter in layout.get("intersections", []):
        if inter.get("position") == [row, col]:
            return {"type": "intersection", "data": inter}
    return None


def _get_cell_size(entity_data: Optional[dict], default: Tuple[int, int] = (200, 200)) -> Tuple[int, int]:
    """Get cell size from entity, or return default."""
    if not entity_data:
        return default
    entity = entity_data.get("data", {})
    cell_size = entity.get("cell_size")
    if cell_size and isinstance(cell_size, list) and len(cell_size) >= 2:
        return (int(cell_size[0]), int(cell_size[1]))
    return default


def _is_compound_cell(entity_data: Optional[dict]) -> bool:
    """Check if entity is a compound cell."""
    if not entity_data:
        return False
    entity = entity_data.get("data", {})
    return entity.get("is_compound", False)


def _get_background_color(entity_data: Optional[dict]) -> str:
    """Get background color from entity, or return 'none'."""
    if not entity_data:
        return "none"
    entity = entity_data.get("data", {})
    bg_color = entity.get("background_color")
    if bg_color:
        return bg_color
    return "none"


def _should_show_label(entity_data: Optional[dict]) -> bool:
    """Check if label should be shown."""
    if not entity_data:
        return False
    entity = entity_data.get("data", {})
    return entity.get("show_label", False)


def _get_label_text(entity_data: Optional[dict]) -> str:
    """Get label text from entity, or return id."""
    if not entity_data:
        return ""
    entity = entity_data.get("data", {})
    label_text = entity.get("label_text")
    if label_text:
        return label_text
    return entity.get("id", "")


def _get_icon_size_ratio(entity_type: str) -> float:
    """Get icon size ratio based on entity type."""
    if entity_type == "intersection":
        return 0.8  # 80%
    elif entity_type == "module":
        return 0.56  # 56%
    elif entity_type == "fixed_position":
        return 0.8  # 80%
    return 0.56  # Default fallback


def _calculate_icon_size(
    cell_size: Tuple[int, int], entity_type: str, is_compound: bool = False, svg_content: str = None
) -> Tuple[int, int]:
    """
    Calculate icon size based on cell size and entity type.
    For fixed_positions: determine limiting factor (width or height) and apply general scaling.
    For modules: use main component size (200x200 for compounds).
    """
    ratio = _get_icon_size_ratio(entity_type)
    width, height = cell_size

    if entity_type == "fixed_position" and svg_content:
        # General scaling: find limiting factor and apply 80% ratio
        import re

        cell_aspect_ratio = width / height
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        if viewbox_match:
            viewbox_parts = viewbox_match.group(1).split()
            if len(viewbox_parts) >= 4:
                vb_width, vb_height = float(viewbox_parts[2]), float(viewbox_parts[3])
                svg_aspect_ratio = vb_width / vb_height

                # Determine limiting factor
                if svg_aspect_ratio > cell_aspect_ratio:
                    # Width is limiting
                    icon_width = int(width * ratio)
                    icon_height = int(width / svg_aspect_ratio * ratio)
                else:
                    # Height is limiting
                    icon_height = int(height * ratio)
                    icon_width = int(height * svg_aspect_ratio * ratio)
                return (icon_width, icon_height)

        # Fallback: use width as limiting factor
        icon_size = int(width * ratio)
        return (icon_size, icon_size)
    elif entity_type == "module" and is_compound:
        # For compounds, use main component size (200x200)
        icon_size = int(200 * ratio)
        return (icon_size, icon_size)
    else:
        # For modules and intersections, use min(width, height)
        icon_size = int(min(width, height) * ratio)
        return (icon_size, icon_size)


def _get_compound_layout(entity_data: Optional[dict]) -> Optional[dict]:
    """Get compound layout configuration from entity."""
    if not entity_data:
        return None
    entity = entity_data.get("data", {})
    return entity.get("compound_layout")


def compute_route_edge_points(path, layout, cell_size=CELL_SIZE):
    """
    Compute route points that start/end at cell edges rather than centers.
    Routes should only be visible on intersection cells.

    Args:
        path: List of node IDs in the route
        layout: Layout configuration dict
        cell_size: Size of each cell in pixels

    Returns:
        List of (x, y) tuples for route visualization
    """
    if not path or len(path) < 2:
        return []

    # Get position map (with canvas padding for correct positioning)
    pos_map = route_utils.id_to_position_map(layout, cell_size, CANVAS_PADDING)

    # Identify which nodes are intersections
    intersection_ids = {str(inter["id"]) for inter in layout.get("intersections", [])}

    route_pts = []
    for i, node in enumerate(path):
        if node not in pos_map:
            continue

        cx, cy = pos_map[node]

        # Only add intersection points or start/end points at edges
        if i == 0:
            # Start point - find edge towards next intersection
            if len(path) > 1 and path[1] in pos_map:
                next_cx, next_cy = pos_map[path[1]]
                # Calculate edge point
                if next_cx > cx:  # Moving right
                    route_pts.append((cx + cell_size // 2, cy))
                elif next_cx < cx:  # Moving left
                    route_pts.append((cx - cell_size // 2, cy))
                elif next_cy > cy:  # Moving down
                    route_pts.append((cx, cy + cell_size // 2))
                else:  # Moving up
                    route_pts.append((cx, cy - cell_size // 2))
        elif i == len(path) - 1:
            # End point - find edge from previous intersection
            if i > 0 and path[i - 1] in pos_map:
                prev_cx, prev_cy = pos_map[path[i - 1]]
                # Calculate edge point
                if cx > prev_cx:  # Coming from left
                    route_pts.append((cx - cell_size // 2, cy))
                elif cx < prev_cx:  # Coming from right
                    route_pts.append((cx + cell_size // 2, cy))
                elif cy > prev_cy:  # Coming from top
                    route_pts.append((cx, cy - cell_size // 2))
                else:  # Coming from bottom
                    route_pts.append((cx, cy + cell_size // 2))
        elif node in intersection_ids:
            # Intersection - use center point
            route_pts.append((cx, cy))

    return route_pts


def render_shopfloor_svg(
    layout: dict,
    highlight_cells: Optional[List[Tuple[int, int]]] = None,
    enable_click: bool = True,
    route_points: Optional[List[Tuple[int, int]]] = None,
    agv_progress: float = 0.0,
    scale: float = 1.0,
) -> str:
    """
    Returns an SVG string for embedding. This is a pure renderer (no Streamlit side effects),
    so it can be tested by pytest.
    highlight_cells: list of [row,col] tuples that should be highlighted programmatically
    """
    highlight_set = set(highlight_cells or [])
    # build grid cells and components
    # Separate normal and highlighted cells for proper z-ordering (SVG renders in order)
    cell_elems = []
    comp_elems = []
    comp_elems_highlighted = []  # Highlighted cells rendered after normal cells
    inter_elems = []

    for r in range(GRID_H):
        for c in range(GRID_W):
            x, y = cell_anchor(r, c)
            # invisible grid rect (for overlay)
            cell_elems.append(
                f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="none" stroke="none" />'
            )
            
            # Get entity at this position (module, fixed_position, or intersection)
            entity_data = _get_entity_at_position(layout, r, c)
            
            # Get cell size from entity or use default
            cell_size = _get_cell_size(entity_data)
            w, h = cell_size
            
            # Get entity name/id
            if entity_data:
                entity = entity_data.get("data", {})
                name = entity.get("id", f"[{r},{c}]")
            else:
                name = f"[{r},{c}]"
            
            # Calculate component position (center in cell)
            comp_x = x + (CELL_SIZE - w) / 2
            
            # Calculate comp_y based on cell size
            # For cells smaller than CELL_SIZE, center them vertically
            # For compound cells (height > CELL_SIZE), position at y=100 (row 0 position)
            is_compound = _is_compound_cell(entity_data)
            if h > CELL_SIZE or is_compound:
                # Compound cell extends beyond cell boundary - start at y=100 (row 0 position)
                comp_y = 100 + CANVAS_PADDING  # Start at row 0 position
            elif h < CELL_SIZE:
                # Smaller cell - center vertically, move up slightly for fixed positions
                comp_y = y + (CELL_SIZE - h) / 2 - 50 if h == 100 else y + (CELL_SIZE - h) / 2
            else:
                # Standard size cell
                comp_y = y + (CELL_SIZE - h) / 2

            # Border logic - orange stroke for highlighted cells, gray for normal cells
            is_active = (r, c) in highlight_set
            stroke = "#ff8c00" if is_active else "#e0e0e0"  # Orange for highlighted, gray for normal
            stroke_width = 4 if is_active else 2  # 4px for highlighted (same as click), 2px for normal

            # Get background color from entity
            cell_fill = _get_background_color(entity_data)

            # Get icon from layout JSON (only for modules and fixed_positions, NOT intersections)
            # Intersections are rendered separately to avoid double rendering
            module_icon = ""
            module_label = ""
            if entity_data and ASSET_MANAGER:
                entity = entity_data.get("data", {})
                entity_type_str = entity.get("type")
                entity_type = entity_data.get("type")  # "module", "fixed_position", or "intersection"
                
                # Skip intersections - they are rendered separately
                if entity_type == "intersection":
                    pass
                elif entity_type_str:
                    try:
                        is_compound = _is_compound_cell(entity_data)
                        # Calculate icon size based on entity type and cell size
                        icon_width, icon_height = _calculate_icon_size(cell_size, entity_type, is_compound)
                        show_label = _should_show_label(entity_data)
                        
                        # Get SVG content for fixed_positions to calculate correct size
                        svg_content_for_calc = None
                        if entity_type == "fixed_position" and ASSET_MANAGER:
                            try:
                                svg_content_for_calc = ASSET_MANAGER.get_asset_content(entity_type_str, scoped=True)
                            except Exception:
                                pass
                        
                        # Recalculate icon size with SVG content for fixed_positions
                        if svg_content_for_calc:
                            icon_width, icon_height = _calculate_icon_size(cell_size, entity_type, is_compound, svg_content_for_calc)
                        
                        # For compound modules, center icon in main 200×200 compartment (lower portion)
                        if entity_type == "module" and is_compound:
                            # Main compartment is 200×200 in the lower portion (y=200 to y=400)
                            main_comp_y = 200  # Main compartment starts at y=200
                            icon_svg = _get_icon_svg(entity_type_str, icon_width, icon_height, entity_type, cell_size)
                            if icon_svg:
                                # Center icon vertically - only move up if label is shown
                                label_offset = 10 if show_label else 0
                                icon_x = comp_x + (w - icon_width) / 2
                                icon_y = main_comp_y + (200 - icon_height) / 2 - label_offset
                                module_icon = f'<g transform="translate({icon_x},{icon_y})">{icon_svg}</g>'
                                # Add label if needed
                                if show_label:
                                    label_text = _get_label_text(entity_data) or name
                                    label_y = main_comp_y + (200 + icon_height) / 2 + 15
                                    module_label = f'<text x="{comp_x + w/2}" y="{label_y}" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">{html.escape(label_text)}</text>'
                        else:
                            # Standard positioning - center icon in cell (including fixed_positions)
                            icon_svg = _get_icon_svg(entity_type_str, icon_width, icon_height, entity_type, cell_size)
                            if icon_svg:
                                # Center icon perfectly - no offset for fixed_positions without labels
                                label_offset = 10 if (show_label and entity_type != "fixed_position") else 0
                                icon_x = comp_x + (w - icon_width) / 2
                                icon_y = comp_y + (h - icon_height) / 2 - label_offset
                                module_icon = f'<g transform="translate({icon_x},{icon_y})">{icon_svg}</g>'
                                # Add label if needed (only for modules, not fixed_positions)
                                if show_label and entity_type != "fixed_position":
                                    label_text = _get_label_text(entity_data) or name
                                    label_y = comp_y + (h + icon_height) / 2 + 15
                                    module_label = f'<text x="{comp_x + w/2}" y="{label_y}" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">{html.escape(label_text)}</text>'
                    except Exception:
                        pass  # Silently fail if asset not found

            # Compound inner assets - load icons from asset manager using positions array
            compound_inner = ""
            if entity_data and _is_compound_cell(entity_data):
                entity = entity_data.get("data", {})
                attached_assets = entity.get("attached_assets", [])
                compound_layout = _get_compound_layout(entity_data)
                
                if compound_layout and attached_assets and ASSET_MANAGER:
                    positions = compound_layout.get("positions", [])
                    asset_size = compound_layout.get("size", [100, 100])  # Default 100×100
                    asset_w, asset_h = asset_size[0], asset_size[1] if len(asset_size) >= 2 else asset_size[0]
                    
                    # Icon size: 60% of asset size
                    icon_size = int(min(asset_w, asset_h) * 0.6)
                    icon_offset = (asset_w - icon_size) / 2
                    
                    # For compound cells, attached_assets are positioned at the top
                    # comp_y is at the cell anchor, but assets should be at row 0 position (y=100)
                    # Adjust base_y to account for compound cell positioning
                    base_y = 100 + CANVAS_PADDING  # Top of compound (row 1 starts at y=100)
                    
                    for i, asset_key in enumerate(attached_assets):
                        if i < len(positions):
                            pos = positions[i]
                            rel_x, rel_y = pos[0], pos[1] if len(pos) >= 2 else 0
                            
                            # Absolute position: x relative to comp_x, y relative to base_y
                            abs_x = comp_x + rel_x
                            abs_y = base_y + rel_y
                            
                            # Load and render icon
                            asset_svg = _get_icon_svg(asset_key, icon_size, icon_size)
                            if asset_svg:
                                icon_x = abs_x + icon_offset
                                icon_y = abs_y + icon_offset
                                compound_inner += f'<g transform="translate({icon_x},{icon_y})">{asset_svg}</g>'
            # Highlight fill for view mode (when is_active is true)
            highlight_fill = "rgba(255, 140, 0, 0.1)" if is_active else cell_fill
            
            # Add data attribute for highlighting state to enable CSS targeting
            highlight_class = " cell-highlighted" if is_active else ""
            cell_elem = (
                f'<g class="cell-group{highlight_class}" data-pos="{r},{c}" data-name="{html.escape(name)}">'
                f'<rect x="{comp_x}" y="{comp_y}" width="{w}" height="{h}" fill="{highlight_fill}" stroke="{stroke}" stroke-width="{stroke_width}" rx="6" ry="6" />'
                f"{compound_inner}"
                f"{module_icon}"
                f"{module_label}"
                f'<text x="{comp_x+6}" y="{comp_y+16}" style="display:none" class="tooltip">{html.escape(name)} [{r},{c}]</text>'
                f"</g>"
            )
            
            # Render highlighted cells after normal cells for proper z-ordering
            if is_active:
                comp_elems_highlighted.append(cell_elem)
            else:
                comp_elems.append(cell_elem)

    # intersections - load icons from asset manager using type field ONLY (not ID to avoid double rendering)
    for inter in layout.get("intersections", []):
        r, c = inter["position"]
        cx, cy = center_of_cell(r, c)
        iid = inter["id"]
        # Use ONLY type field, NOT id - to avoid double rendering
        inter_type = inter.get("type")  # Use type field only
        
        if not inter_type:
            # Fallback: if no type field, skip asset manager and use fallback rendering
            inter_elems.append(
                f'<g id="inter_{iid}">'
                f'<line x1="{cx-40}" y1="{cy}" x2="{cx+40}" y2="{cy}" stroke="#9b6fd6" stroke-width="12" stroke-linecap="round"/>'
                f'<line x1="{cx}" y1="{cy-40}" x2="{cx}" y2="{cy+40}" stroke="#9b6fd6" stroke-width="12" stroke-linecap="round"/>'
                f'<circle cx="{cx}" cy="{cy}" r="14" fill="#6f6f6f" />'
                f'<text x="{cx}" y="{cy+5}" fill="#fff" font-size="14" text-anchor="middle">{iid}</text>'
                f"</g>"
            )
            continue
        
        # Calculate icon size: 80% of cell size (200px)
        icon_size = int(CELL_SIZE * 0.8)  # 160px

        # Try to load intersection icon from asset manager using type field ONLY
        inter_icon_svg = ""
        if ASSET_MANAGER:
            inter_icon_svg = _get_icon_svg(inter_type, icon_size, icon_size)

        if inter_icon_svg:
            # Center the intersection icon perfectly
            icon_x = cx - icon_size / 2
            icon_y = cy - icon_size / 2
            inter_elems.append(
                f'<g id="inter_{iid}">' f'<g transform="translate({icon_x},{icon_y})">{inter_icon_svg}</g>' f"</g>"
            )
        else:
            # Fallback to purple crosses if icon not found
            inter_elems.append(
                f'<g id="inter_{iid}">'
                f'<line x1="{cx-40}" y1="{cy}" x2="{cx+40}" y2="{cy}" stroke="#9b6fd6" stroke-width="12" stroke-linecap="round"/>'
                f'<line x1="{cx}" y1="{cy-40}" x2="{cx}" y2="{cy+40}" stroke="#9b6fd6" stroke-width="12" stroke-linecap="round"/>'
                f'<circle cx="{cx}" cy="{cy}" r="14" fill="#6f6f6f" />'
                f'<text x="{cx}" y="{cy+5}" fill="#fff" font-size="14" text-anchor="middle">{iid}</text>'
                f"</g>"
            )

    # route drawing (polyline through route_points)
    route_svg = ""
    if route_points:
        pts = " ".join(f"{int(x)},{int(y)}" for (x, y) in route_points)
        start = route_points[0]
        end = route_points[-1]

        # Calculate AGV position at middle of route (or at agv_progress if specified)
        agv_marker_svg = ""
        if ASSET_MANAGER and len(route_points) >= 2:
            try:
                # Get FTS icon
                fts_svg_content = ASSET_MANAGER.get_asset_inline("FTS")
                if fts_svg_content:
                    # Calculate position along route based on progress (default 0.5 = middle)
                    progress = agv_progress if agv_progress > 0 else 0.5
                    total_length = sum(
                        (
                            (route_points[i + 1][0] - route_points[i][0]) ** 2
                            + (route_points[i + 1][1] - route_points[i][1]) ** 2
                        )
                        ** 0.5
                        for i in range(len(route_points) - 1)
                    )
                    target_dist = total_length * progress

                    # Find point at target distance
                    current_dist = 0
                    agv_x, agv_y = route_points[0]
                    for i in range(len(route_points) - 1):
                        segment_length = (
                            (route_points[i + 1][0] - route_points[i][0]) ** 2
                            + (route_points[i + 1][1] - route_points[i][1]) ** 2
                        ) ** 0.5
                        if current_dist + segment_length >= target_dist:
                            # Interpolate within this segment
                            t = (target_dist - current_dist) / segment_length if segment_length > 0 else 0
                            agv_x = route_points[i][0] + t * (route_points[i + 1][0] - route_points[i][0])
                            agv_y = route_points[i][1] + t * (route_points[i + 1][1] - route_points[i][1])
                            break
                        current_dist += segment_length

                    # Extract original size from viewBox
                    import re

                    original_size = 24  # Default fallback
                    viewbox_match = re.search(r'viewBox="([^"]*)"', fts_svg_content)
                    if viewbox_match:
                        viewbox_parts = viewbox_match.group(1).split()
                        if len(viewbox_parts) >= 4:
                            original_size = float(viewbox_parts[2])

                    # Scale to 72px (increased from 48px by 50%)
                    icon_size = 72
                    half_size = icon_size / 2
                    scale_factor = icon_size / original_size

                    # Remove SVG wrapper for embedding
                    svg_content_clean = fts_svg_content.replace("<svg", "<g").replace("</svg>", "</g>")
                    svg_content_clean = re.sub(r'width="[^"]*"', "", svg_content_clean)
                    svg_content_clean = re.sub(r'height="[^"]*"', "", svg_content_clean)

                    agv_marker_svg = f'<g transform="translate({agv_x - half_size}, {agv_y - half_size}) scale({scale_factor})">{svg_content_clean}</g>'
            except Exception:
                # Fallback to circle if FTS icon fails
                agv_x = route_points[len(route_points) // 2][0]
                agv_y = route_points[len(route_points) // 2][1]
                agv_marker_svg = (
                    f'<circle cx="{agv_x}" cy="{agv_y}" r="16" fill="#4CAF50" stroke="#fff" stroke-width="2" />'
                )

        # Route thickness reduced by 25% (from 8 to 6)
        route_svg = (
            f'<polyline points="{pts}" stroke="#ff8c00" stroke-width="6" fill="none" stroke-linejoin="round" stroke-linecap="round" />'
            f'<circle cx="{start[0]}" cy="{start[1]}" r="6" fill="#ff8c00" stroke="#fff" stroke-width="2" />'
            f'<circle cx="{end[0]}" cy="{end[1]}" r="6" fill="#ff8c00" stroke="#fff" stroke-width="2" />'
            f"{agv_marker_svg}"
        )

    # Container border - medium gray
    container_border = f'<rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="none" stroke="#888888" stroke-width="2" />'
    
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="{int(CANVAS_W*scale)}" height="{int(CANVAS_H*scale)}">'
        f"<style>"
        f".cell-group .tooltip {{ font-family: Arial; font-size: 12px; }}"
        f".cell-group:hover .tooltip {{ display: block !important; font-weight: bold; }}"
        f".cell-group {{ cursor: {'pointer' if enable_click else 'default'}; }}"
        f".cell-group:hover rect {{ stroke: #ff8c00 !important; fill: rgba(255, 152, 0, 0.1) !important; }}"
        f".cell-group.clicked rect {{ stroke-width: 4 !important; stroke: #ff8c00 !important; fill: rgba(255, 152, 0, 0.1) !important; }}"
        f".cell-highlighted rect {{ stroke-width: 4 !important; stroke: #ff8c00 !important; }}"
        f"</style>"
        f"{container_border}"
        f'{"".join(cell_elems)}'
        f'{"".join(comp_elems)}'  # Normal cells first
        f'{"".join(comp_elems_highlighted)}'  # Highlighted cells after (on top)
        f'{"".join(inter_elems)}'
        f"{route_svg}"
        f"</svg>"
    )
    return svg


def show_shopfloor_layout(
    title: str = "Shopfloor Layout",
    unique_key: str = "shopfloor_layout_demo",
    mode: str = "view",
    enable_click: bool = True,
    highlight_cells: Optional[List[List[int]]] = None,
    route_points: Optional[List[Tuple[int, int]]] = None,
    agv_progress: float = 0.0,
    active_module_id: Optional[str] = None,
    active_intersections: Optional[List[str]] = None,
    show_controls: bool = True,
):
    """
    Streamlit wrapper to render the shopfloor SVG and controls.
    This mirrors the API requested in the PR description.
    """
    layout = load_layout()
    st.header(title)
    if show_controls:
        st.columns([3, 1])  # Reserved for future use

    scale = st.sidebar.slider("Scale (100% = 1.0)", 0.25, 2.0, 1.0, 0.05) if show_controls else 1.0
    # parse highlight_cells
    highlight = []
    if highlight_cells:
        for it in highlight_cells:
            if isinstance(it, (list, tuple)) and len(it) == 2:
                highlight.append((int(it[0]), int(it[1])))

    svg = render_shopfloor_svg(
        layout,
        highlight_cells=highlight,
        enable_click=enable_click,
        route_points=route_points,
        agv_progress=agv_progress,
        scale=scale,
    )
    # embed HTML with JS for hover/click (clientside)
    # Use same render-order logic as View-Mode: move hover/click cells to end of SVG
    click_script = ""
    if enable_click:
        click_script = """
        <script>
        (function() {
            const svg = document.querySelector('svg');
            const groups = document.querySelectorAll('.cell-group');
            let activeGroup = null;
            let hoverGroup = null;

            // Move group to end of SVG for proper z-ordering (like View-Mode)
            function moveToEnd(group) {
                if (group && svg && group.parentNode === svg) {
                    svg.appendChild(group);
                }
            }

            groups.forEach(group => {
                // Handle hover: move to end when hovering
                group.addEventListener('mouseenter', function(e) {
                    hoverGroup = this;
                    moveToEnd(this);
                });

                // Handle click: move to end and add clicked class
                group.addEventListener('click', function(e) {
                    // Remove clicked class from previous active
                    if (activeGroup && activeGroup !== this) {
                        activeGroup.classList.remove('clicked');
                    }
                    // Toggle clicked class on current
                    this.classList.toggle('clicked');
                    activeGroup = this.classList.contains('clicked') ? this : null;
                    // Move to end for proper z-ordering
                    moveToEnd(this);
                    e.stopPropagation();
                });
            });

            // Click outside to deselect
            document.addEventListener('click', function(e) {
                if (activeGroup && !activeGroup.contains(e.target)) {
                    activeGroup.classList.remove('clicked');
                    activeGroup = null;
                }
            });
        })();
        </script>
        """

    html_fragment = f"""
    <div style="width:{int(CANVAS_W*scale)}px; height:{int(CANVAS_H*scale)}px;">
      {svg}
    </div>
    {click_script}
    """
    st.components.v1.html(html_fragment, height=int(CANVAS_H * scale) + 20, scrolling=True)


# If run directly, show the demo app
def main():
    st.title("Shopfloor Test App (examples/shopfloor_test_app)")
    layout = load_layout()

    # Mode selection
    mode = st.sidebar.radio(
        "Display Mode", ["Mode 1: Interactive (Click & Mouse-Over)", "Mode 2: View (Highlighting & Routes)"], index=1
    )

    enable_click = "Mode 1" in mode

    # Select start/goal from candidate modules (red & green)
    candidates = []
    for (r, c), v in VIS_SPEC.items():
        if v["color"] in ("#ffd5d5", "#d7f0c8"):
            candidates.append((r, c, v["name"]))
    opts = ["-- none --"] + [f"{name} [{r},{c}]" for r, c, name in candidates]

    # Show route controls only in Mode 2
    route_pts = None
    highlight_cells = []
    if "Mode 2" in mode:
        st.sidebar.subheader("Route & Highlighting")
        start_sel = st.sidebar.selectbox("Route Start", opts, index=0)
        goal_sel = st.sidebar.selectbox("Route Goal", opts, index=0)

        # Highlight selection (multi-select)
        st.sidebar.subheader("Highlight Cells")
        highlight_opts = [
            f"{name} [{r},{c}]" for r, c, name in [(r, c, VIS_SPEC[(r, c)]["name"]) for r, c in VIS_SPEC.keys()]
        ]
        highlight_sel = st.sidebar.multiselect("Select cells to highlight", highlight_opts, default=[])

        # Convert highlight selection to cell coordinates
        for sel in highlight_sel:
            # Parse "[r,c]" from the selection string
            import re

            match = re.search(r"\[(\d+),(\d+)\]", sel)
            if match:
                highlight_cells.append([int(match.group(1)), int(match.group(2))])

        # compute route when requested
        if start_sel != "-- none --" and goal_sel != "-- none --":
            # convert selection to id (use module id mapping from layout)
            def sel_to_id(s):
                if not s or s == "-- none --":
                    return None
                name = s.split()[0]
                # try modules and fixed positions
                for m in layout.get("modules", []):
                    if m.get("id") == name:
                        return m.get("serialNumber") or m.get("id")
                for f in layout.get("fixed_positions", []):
                    if f.get("id") == name:
                        return f.get("id")
                return name

            start_id = sel_to_id(start_sel)
            goal_id = sel_to_id(goal_sel)
            graph = route_utils.build_graph(layout)
            # special rules: if no start and goal is HBW -> start is INTERSECTION-2 ; if goal is DPS -> start = INTERSECTION-1
            if not start_id and goal_id:
                # find if goal is HBW or DPS
                goal_name = None
                for m in layout.get("modules", []):
                    if m.get("serialNumber") == goal_id or m.get("id") == goal_id:
                        goal_name = m.get("id")
                if goal_name == "HBW":
                    start_id = "2"
                if goal_name == "DPS":
                    start_id = "1"
            if start_id and goal_id:
                path = route_utils.find_path(graph, start_id, goal_id)
                if path:
                    # Convert path to edge-based route points (only on intersections)
                    route_pts = compute_route_edge_points(path, layout, CELL_SIZE)
                    if len(route_pts) < 2:
                        route_pts = None

    show_shopfloor_layout(
        title=f"Shopfloor Layout - {mode}",
        unique_key="examples_shopfloor",
        mode="demo",
        enable_click=enable_click,
        highlight_cells=highlight_cells,
        route_points=route_pts,
        agv_progress=0.0,
        show_controls=True,
    )


if __name__ == "__main__":
    main()
