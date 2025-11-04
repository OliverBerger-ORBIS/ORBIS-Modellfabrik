"""
Streamlit test app: interactive, scalable SVG shopfloor layout demo.

- Uses examples/shopfloor_test_app/shopfloor_layout.json as default layout.
- Uses omf2.assets.asset_manager.get_asset_manager() to fetch inline SVG icons where available.
- Implements show_shopfloor_layout(...) API for embedding in other code.
"""

import html
import json
import pathlib
from typing import List, Optional, Tuple

import streamlit as st

from examples.shopfloor_test_app import route_utils

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


def _get_icon_svg(module_type: str, target_width: int, target_height: int) -> str:
    """Load and scale icon from asset manager with proper centering."""
    if not ASSET_MANAGER:
        return ""

    try:
        # Use get_asset_content with scoped=True as in production
        icon_svg = ASSET_MANAGER.get_asset_content(module_type, scoped=True)
        if icon_svg:
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

    # Get position map
    pos_map = route_utils.id_to_position_map(layout, cell_size)

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
    cell_elems = []
    comp_elems = []
    inter_elems = []

    for r in range(GRID_H):
        for c in range(GRID_W):
            x, y = cell_anchor(r, c)
            # invisible grid rect (for overlay)
            cell_elems.append(
                f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="none" stroke="none" />'
            )
            spec = VIS_SPEC.get((r, c))
            if spec:
                w = spec["w"]
                h = spec["h"]
                fill = spec["color"]
                name = spec["name"]
            else:
                w, h, fill, name = 180, 180, "#ffffff", f"[{r},{c}]"
            comp_x = x + (CELL_SIZE - w) / 2

            # Special positioning for different cell types
            # COMPANY/SOFTWARE (100px tall in row 0, cols 0 and 3): move up 50px
            if (r, c) in ((0, 0), (0, 3)) and h == 100:
                comp_y = y + (CELL_SIZE - h) / 2 - 50
            # HBW/DPS compounds (300px tall in row 1, cols 0 and 3): start at y=100
            elif (r, c) in ((1, 0), (1, 3)) and h == 300:
                comp_y = 100
            else:
                comp_y = y + (CELL_SIZE - h) / 2

            # border logic - use transparent fill, only colored border
            is_active = (r, c) in highlight_set
            stroke = "#2a7d2a" if fill == "#d7f0c8" else "#d22a2a" if fill == "#ffd5d5" else "#3a6ea5"
            # Normal border width is 2, highlighted is 8
            stroke_width = 8 if is_active else 2

            # Get module icon if available
            module_icon = ""
            module_label = ""
            if spec and ASSET_MANAGER:
                module_type = name  # Use the name from VIS_SPEC
                try:
                    # Use 56% of cell size (reduced by 20% from 70%)
                    icon_size = int(min(w, h) * 0.56)

                    # For compounds (HBW/DPS), center main icon in the 200×200 main compartment, not full 200×300
                    if (r, c) in ((1, 0), (1, 3)) and h == 300:
                        # Main compartment is 200×200 in the lower portion (y=200 to y=400)
                        # Icon should be centered in that 200×200 area
                        icon_size = int(200 * 0.56)  # 112px based on 200×200 compartment (reduced 20%)
                        icon_svg = _get_icon_svg(module_type, icon_size, icon_size)
                        if icon_svg:
                            # Center in the main 200×200 compartment (lower portion)
                            main_comp_y = 200  # Main compartment starts at y=200
                            icon_x = comp_x + (w - icon_size) / 2
                            icon_y = main_comp_y + (200 - icon_size) / 2 - 10  # Move up 10px to make room for label
                            module_icon = f'<g transform="translate({icon_x},{icon_y})">{icon_svg}</g>'
                            # Add label below icon
                            label_y = main_comp_y + (200 + icon_size) / 2 + 15
                            module_label = f'<text x="{comp_x + w/2}" y="{label_y}" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">{html.escape(name)}</text>'
                    else:
                        icon_svg = _get_icon_svg(module_type, icon_size, icon_size)
                        if icon_svg:
                            # Center the icon in the cell, move up slightly for label
                            icon_x = comp_x + (w - icon_size) / 2
                            icon_y = comp_y + (h - icon_size) / 2 - 10
                            module_icon = f'<g transform="translate({icon_x},{icon_y})">{icon_svg}</g>'
                            # Add label below icon
                            label_y = comp_y + (h + icon_size) / 2 + 15
                            module_label = f'<text x="{comp_x + w/2}" y="{label_y}" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">{html.escape(name)}</text>'
                except Exception:
                    pass  # Silently fail if asset not found

            # compound inner squares for HBW/DPS - load icons from asset manager
            compound_inner = ""
            if (r, c) in ((1, 0), (1, 3)):
                # Get module data to access attached_assets
                module_data = None
                for mod in layout.get("modules", []):
                    if mod.get("position") == [r, c]:
                        module_data = mod
                        break

                # Squares are 100×100px at y=100 (top of compound at row 1)
                # Position them higher up, not at comp_y + 8
                sx1 = comp_x  # Left square
                sy1 = 100 + CANVAS_PADDING  # At top of compound (row 1 starts at y=100 for the main area)
                sx2 = comp_x + 100  # Right square
                sy2 = 100 + CANVAS_PADDING

                square1_svg = ""
                square2_svg = ""
                if module_data and ASSET_MANAGER:
                    attached_assets = module_data.get("attached_assets", [])
                    if len(attached_assets) >= 1:
                        # Use 60% of square size for icons (60px in 100px square) for better fit
                        square1_svg = _get_icon_svg(attached_assets[0], 60, 60)
                    if len(attached_assets) >= 2:
                        square2_svg = _get_icon_svg(attached_assets[1], 60, 60)

                # Render squares WITHOUT yellow borders - only icons (no rectangles, no lines)
                # Center icons within the 100x100 square
                icon_offset = (100 - 60) / 2 if square1_svg or square2_svg else 0

                # Remove rectangles - only render icons
                square1_elem = ""
                if square1_svg:
                    square1_elem = (
                        f'<g transform="translate({sx1 + icon_offset},{sy1 + icon_offset})">{square1_svg}</g>'
                    )

                square2_elem = ""
                if square2_svg:
                    square2_elem = (
                        f'<g transform="translate({sx2 + icon_offset},{sy2 + icon_offset})">{square2_svg}</g>'
                    )

                compound_inner = square1_elem + square2_elem
            comp_elems.append(
                f'<g class="cell-group" data-pos="{r},{c}" data-name="{html.escape(name)}">'
                f'<rect x="{comp_x}" y="{comp_y}" width="{w}" height="{h}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" rx="6" ry="6" />'
                f"{compound_inner}"
                f"{module_icon}"
                f"{module_label}"
                f'<text x="{comp_x+6}" y="{comp_y+16}" style="display:none" class="tooltip">{html.escape(name)} [{r},{c}]</text>'
                f"</g>"
            )

    # intersections - load icons from asset manager instead of drawing crosses
    for inter in layout.get("intersections", []):
        r, c = inter["position"]
        cx, cy = center_of_cell(r, c)
        iid = inter["id"]

        # Try to load intersection icon from asset manager
        inter_icon_svg = ""
        if ASSET_MANAGER:
            inter_icon_svg = _get_icon_svg(iid, 140, 140)  # 70% of 200px cell

        if inter_icon_svg:
            # Center the intersection icon
            icon_x = cx - 70
            icon_y = cy - 70
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

        route_svg = (
            f'<polyline points="{pts}" stroke="#ff8c00" stroke-width="8" fill="none" stroke-linejoin="round" stroke-linecap="round" />'
            f'<circle cx="{start[0]}" cy="{start[1]}" r="8" fill="#ff8c00" stroke="#fff" stroke-width="2" />'
            f'<circle cx="{end[0]}" cy="{end[1]}" r="8" fill="#ff8c00" stroke="#fff" stroke-width="2" />'
            f"{agv_marker_svg}"
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" width="{int(CANVAS_W*scale)}" height="{int(CANVAS_H*scale)}">'
        f"<style>"
        f".cell-group .tooltip {{ font-family: Arial; font-size: 12px; }}"
        f".cell-group:hover .tooltip {{ display: block !important; font-weight: bold; }}"
        f".cell-group:hover rect {{ stroke-width: 4 !important; stroke: #ff8c00 !important; }}"
        f".cell-group {{ cursor: {'pointer' if enable_click else 'default'}; }}"
        f".cell-group.clicked rect {{ stroke-width: 8 !important; }}"
        f"</style>"
        f'{"".join(cell_elems)}'
        f'{"".join(comp_elems)}'
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
    click_script = ""
    if enable_click:
        click_script = """
        <script>
        (function() {
            const groups = document.querySelectorAll('.cell-group');
            let activeGroup = null;

            groups.forEach(group => {
                group.addEventListener('click', function(e) {
                    // Remove clicked class from previous active
                    if (activeGroup && activeGroup !== this) {
                        activeGroup.classList.remove('clicked');
                    }
                    // Toggle clicked class on current
                    this.classList.toggle('clicked');
                    activeGroup = this.classList.contains('clicked') ? this : null;
                    e.stopPropagation();
                });
            });

            // Click outside to deselect
            document.addEventListener('click', function() {
                if (activeGroup) {
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
