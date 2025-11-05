"""
Shopfloor Layout - SVG-Based Rendering Implementation
=====================================================

Scalable, interactive SVG-based shopfloor layout renderer.

Features:
- SVG-based rendering with scalable output (via scale parameter)
- JSON-driven configuration (cell_size, background_color, is_compound, etc.)
- Consistent highlighting across view and interactive modes
- Route visualization with AGV/FTS marker
- Compound cell support (HBW/DPS with attached assets)
- Graceful fallback if config or assets are unavailable

Implementation:
- Uses st.components.v1.html() for rendering SVG
- Pure SVG rendering (no HTML/CSS Grid)
- Client-side JavaScript for interactive highlighting (hover/click)
- Reuses existing helper functions for config/asset loading
"""

import html
import re
from typing import List, Optional, Tuple

import streamlit as st

# OMF2 Imports
from omf2.assets.asset_manager import get_asset_manager
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Constants for SVG rendering
CELL_SIZE = 200
GRID_W = 4
GRID_H = 3
# Add 4px padding (2px on each side) for uniform highlighting at edges
CANVAS_W = CELL_SIZE * GRID_W + 4
CANVAS_H = CELL_SIZE * GRID_H + 4
CANVAS_PADDING = 2


# ============================================================================
# Helper Functions for SVG Rendering (from Example App)
# ============================================================================


def cell_anchor(row: int, col: int) -> Tuple[int, int]:
    """Calculate cell anchor position (top-left corner) in pixel coordinates."""
    return col * CELL_SIZE + CANVAS_PADDING, row * CELL_SIZE + CANVAS_PADDING


def center_of_cell(row: int, col: int) -> Tuple[int, int]:
    """Calculate center of cell in pixel coordinates."""
    x, y = cell_anchor(row, col)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2


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
    # Check intersections (last, as they can overlap with modules)
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


def _scale_svg_properly(svg_content: str, target_width: int, target_height: int) -> Tuple[str, int, int]:
    """
    Scale SVG properly based on viewBox to avoid distortion.
    Returns (scaled_svg_content, actual_width, actual_height)
    """
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
    module_type: str,
    target_width: int,
    target_height: int,
    asset_manager: Optional[object] = None,
    entity_type: str = None,
    cell_size: Tuple[int, int] = None,
) -> str:
    """
    Load and scale icon from asset manager with proper centering.

    For fixed_positions: General scaling approach:
    1. Find limiting factor (width or height) by comparing SVG aspect ratio with cell aspect ratio
    2. Scale SVG to 100% of limiting factor
    3. Apply 80% ratio
    4. Return scaled SVG
    """
    if not asset_manager:
        logger.error(f"❌ asset_manager is None for module_type='{module_type}'")
        return ""

    try:
        # Use get_asset_content with scoped=True as in production
        logger.info(f"🔍 Looking up asset key: '{module_type}' for entity_type={entity_type}")
        icon_svg = asset_manager.get_asset_content(module_type, scoped=True)

        if icon_svg:
            logger.info(f"✅ Successfully loaded SVG for '{module_type}': length={len(icon_svg)}")
        else:
            # Fallback to QUESTION.svg (fallback) if asset not found
            logger.warning(f"⚠️ Asset key '{module_type}' returned None/empty, trying QUESTION fallback")
            icon_svg = asset_manager.get_asset_content("QUESTION", scoped=True)
            if icon_svg:
                logger.info(f"✅ QUESTION fallback loaded: length={len(icon_svg)}")
            else:
                logger.error(f"❌ Fallback (QUESTION) also returned None/empty for asset key '{module_type}'")
                return ""

        if icon_svg:
            logger.debug(f"Successfully loaded SVG for asset key '{module_type}'")
            # For fixed_positions, use general scaling approach
            if entity_type == "fixed_position" and cell_size:
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
                        logger.info(
                            f"✅ Scaled fixed_position SVG '{module_type}': {final_width}x{final_height} → {actual_w}x{actual_h}"
                        )
                        return scaled_svg

                # Fallback: use target dimensions if viewBox parsing fails
                logger.warning(f"⚠️ viewBox parsing failed for '{module_type}', using target dimensions")
                scaled_svg, actual_w, actual_h = _scale_svg_properly(icon_svg, target_width, target_height)
                return scaled_svg
            else:
                scaled_svg, actual_w, actual_h = _scale_svg_properly(icon_svg, target_width, target_height)
                logger.info(f"✅ Scaled SVG '{module_type}': {target_width}x{target_height} → {actual_w}x{actual_h}")
                return scaled_svg
    except Exception as e:
        logger.error(f"❌ Exception in _get_icon_svg for '{module_type}': {e}", exc_info=True)
        # Try fallback (QUESTION) even on exception
        try:
            fallback_svg = asset_manager.get_asset_content("QUESTION", scoped=True)
            if fallback_svg:
                scaled_svg, actual_w, actual_h = _scale_svg_properly(fallback_svg, target_width, target_height)
                return scaled_svg
        except Exception:
            pass

    # Final fallback: try QUESTION if we haven't already
    try:
        if asset_manager:
            fallback_svg = asset_manager.get_asset_content("QUESTION", scoped=True)
            if fallback_svg:
                scaled_svg, actual_w, actual_h = _scale_svg_properly(fallback_svg, target_width, target_height)
                return scaled_svg
    except Exception:
        pass

    return ""


def render_shopfloor_svg(
    layout: dict,
    asset_manager: Optional[object] = None,
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
    # Debug: Log asset manager status
    if not asset_manager:
        logger.warning("render_shopfloor_svg called without asset_manager - SVGs will not be rendered!")
    else:
        logger.debug(
            f"render_shopfloor_svg: asset_manager available, layout has {len(layout.get('modules', []))} modules, {len(layout.get('fixed_positions', []))} fixed positions, {len(layout.get('intersections', []))} intersections"
        )

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

            # Debug logging for entity lookup
            if entity_data:
                entity = entity_data.get("data", {})
                name = entity.get("id", f"[{r},{c}]")
                entity_type = entity_data.get("type")
                entity_type_str = entity.get("type")
                logger.debug(f"Entity at [{r},{c}]: type={entity_type}, entity_type_str={entity_type_str}, id={name}")
            else:
                name = f"[{r},{c}]"

            # Get cell size from entity or use default
            cell_size = _get_cell_size(entity_data)
            w, h = cell_size

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
            if entity_data and asset_manager:
                entity = entity_data.get("data", {})
                entity_type_str = entity.get("type")
                entity_type = entity_data.get("type")  # "module", "fixed_position", or "intersection"

                # Skip intersections - they are rendered separately
                if entity_type == "intersection":
                    pass
                elif entity_type_str:
                    # Ensure we have a valid entity_type_str to look up
                    logger.info(
                        f"🎨 Rendering {entity_type} '{entity_type_str}' at [{r},{c}] - entity.keys()={list(entity.keys())}, entity['type']={entity.get('type')}"
                    )
                    try:
                        is_compound = _is_compound_cell(entity_data)
                        # Calculate icon size based on entity type and cell size
                        icon_width, icon_height = _calculate_icon_size(cell_size, entity_type, is_compound)
                        show_label = _should_show_label(entity_data)

                        # Get SVG content for fixed_positions to calculate correct size
                        svg_content_for_calc = None
                        if entity_type == "fixed_position" and asset_manager:
                            try:
                                svg_content_for_calc = asset_manager.get_asset_content(entity_type_str, scoped=True)
                            except Exception as e:
                                logger.debug(f"Could not get SVG content for fixed_position {entity_type_str}: {e}")

                        # Recalculate icon size with SVG content for fixed_positions
                        if svg_content_for_calc:
                            icon_width, icon_height = _calculate_icon_size(
                                cell_size, entity_type, is_compound, svg_content_for_calc
                            )

                        # For compound modules, center icon in main 200×200 compartment (lower portion)
                        if entity_type == "module" and is_compound:
                            # Main compartment is 200×200 in the lower portion (y=200 to y=400)
                            main_comp_y = 200  # Main compartment starts at y=200
                            icon_svg = _get_icon_svg(
                                entity_type_str, icon_width, icon_height, asset_manager, entity_type, cell_size
                            )
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
                                    module_label = (
                                        f'<text x="{comp_x + w/2}" y="{label_y}" font-family="Arial" '
                                        f'font-size="14" fill="#333" text-anchor="middle">{html.escape(label_text)}</text>'
                                    )
                            else:
                                # Icon not loaded - try QUESTION fallback
                                logger.warning(
                                    f"Could not load icon for compound module {entity_type_str} at [{r},{c}], trying QUESTION fallback"
                                )
                                # Try to load QUESTION fallback
                                try:
                                    fallback_svg = _get_icon_svg(
                                        "QUESTION", icon_width, icon_height, asset_manager, entity_type, cell_size
                                    )
                                    if fallback_svg:
                                        label_offset = 10 if show_label else 0
                                        icon_x = comp_x + (w - icon_width) / 2
                                        icon_y = main_comp_y + (200 - icon_height) / 2 - label_offset
                                        module_icon = f'<g transform="translate({icon_x},{icon_y})">{fallback_svg}</g>'
                                        logger.debug(
                                            f"Using QUESTION fallback for compound module {entity_type_str} at [{r},{c}]"
                                        )
                                except Exception as e2:
                                    logger.warning(f"Could not load QUESTION fallback either: {e2}")
                        else:
                            # Standard positioning - center icon in cell (including fixed_positions)
                            icon_svg = _get_icon_svg(
                                entity_type_str, icon_width, icon_height, asset_manager, entity_type, cell_size
                            )
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
                                    module_label = (
                                        f'<text x="{comp_x + w/2}" y="{label_y}" font-family="Arial" '
                                        f'font-size="14" fill="#333" text-anchor="middle">{html.escape(label_text)}</text>'
                                    )
                            else:
                                # Icon not loaded - try QUESTION fallback
                                logger.warning(
                                    f"Could not load icon for {entity_type} {entity_type_str} at [{r},{c}], trying QUESTION fallback"
                                )
                                # Try to load QUESTION fallback
                                try:
                                    fallback_svg = _get_icon_svg(
                                        "QUESTION", icon_width, icon_height, asset_manager, entity_type, cell_size
                                    )
                                    if fallback_svg:
                                        label_offset = 10 if (show_label and entity_type != "fixed_position") else 0
                                        icon_x = comp_x + (w - icon_width) / 2
                                        icon_y = comp_y + (h - icon_height) / 2 - label_offset
                                        module_icon = f'<g transform="translate({icon_x},{icon_y})">{fallback_svg}</g>'
                                        logger.debug(f"Using QUESTION fallback for {entity_type_str} at [{r},{c}]")
                                except Exception as e2:
                                    logger.warning(f"Could not load QUESTION fallback either: {e2}")
                    except Exception as e:
                        logger.error(
                            f"Error loading icon for {entity_type} {entity_type_str} at [{r},{c}]: {e}",
                            exc_info=True,
                        )
                        # Try QUESTION fallback on exception
                        try:
                            if entity_type_str:
                                icon_width, icon_height = _calculate_icon_size(cell_size, entity_type, False)
                                fallback_svg = _get_icon_svg("QUESTION", icon_width, icon_height, asset_manager)
                                if fallback_svg:
                                    icon_x = comp_x + (w - icon_width) / 2
                                    icon_y = comp_y + (h - icon_height) / 2
                                    module_icon = f'<g transform="translate({icon_x},{icon_y})">{fallback_svg}</g>'
                                    logger.debug(
                                        f"Using QUESTION fallback after exception for {entity_type_str} at [{r},{c}]"
                                    )
                        except Exception:
                            pass

            # Compound inner assets - load icons from asset manager using positions array
            compound_inner = ""
            if entity_data and _is_compound_cell(entity_data):
                entity = entity_data.get("data", {})
                attached_assets = entity.get("attached_assets", [])
                compound_layout = _get_compound_layout(entity_data)

                logger.info(
                    f"🔧 Compound cell at [{r},{c}]: attached_assets={attached_assets}, compound_layout={compound_layout}"
                )

                if compound_layout and attached_assets and asset_manager:
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
                            logger.info(f"🔍 Loading compound asset '{asset_key}' at position [{rel_x},{rel_y}]")
                            # For compound assets, we don't need entity_type or cell_size - they're just icons
                            asset_svg = _get_icon_svg(asset_key, icon_size, icon_size, asset_manager, None, None)
                            if asset_svg:
                                logger.info(f"✅ Successfully loaded compound asset '{asset_key}'")
                                icon_x = abs_x + icon_offset
                                icon_y = abs_y + icon_offset
                                compound_inner += f'<g transform="translate({icon_x},{icon_y})">{asset_svg}</g>'
                            else:
                                logger.warning(f"⚠️ Failed to load compound asset '{asset_key}'")
                        else:
                            logger.warning(
                                f"⚠️ No position available for compound asset {i} '{attached_assets[i] if i < len(attached_assets) else 'unknown'}'"
                            )
                else:
                    logger.warning(
                        f"⚠️ Compound cell at [{r},{c}] missing data: compound_layout={compound_layout}, attached_assets={attached_assets}, asset_manager={asset_manager is not None}"
                    )

            # Highlight fill for view mode (when is_active is true)
            highlight_fill = "rgba(255, 140, 0, 0.1)" if is_active else cell_fill

            # Add data attribute for highlighting state to enable CSS targeting
            highlight_class = " cell-highlighted" if is_active else ""
            cell_elem = (
                f'<g class="cell-group{highlight_class}" data-pos="{r},{c}" data-name="{html.escape(name)}">'
                f'<rect x="{comp_x}" y="{comp_y}" width="{w}" height="{h}" fill="{highlight_fill}" '
                f'stroke="{stroke}" stroke-width="{stroke_width}" rx="6" ry="6" />'
                f"{compound_inner}"
                f"{module_icon}"
                f"{module_label}"
                f'<text x="{comp_x+6}" y="{comp_y+16}" style="display:none" class="tooltip">'
                f"{html.escape(name)} [{r},{c}]</text>"
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
                f'<line x1="{cx-40}" y1="{cy}" x2="{cx+40}" y2="{cy}" stroke="#9b6fd6" '
                f'stroke-width="12" stroke-linecap="round"/>'
                f'<line x1="{cx}" y1="{cy-40}" x2="{cx}" y2="{cy+40}" stroke="#9b6fd6" '
                f'stroke-width="12" stroke-linecap="round"/>'
                f'<circle cx="{cx}" cy="{cy}" r="14" fill="#6f6f6f" />'
                f'<text x="{cx}" y="{cy+5}" fill="#fff" font-size="14" text-anchor="middle">{iid}</text>'
                f"</g>"
            )
            continue

        # Calculate icon size: 80% of cell size (200px)
        icon_size = int(CELL_SIZE * 0.8)  # 160px

        # Try to load intersection icon from asset manager using type field ONLY
        inter_icon_svg = ""
        if asset_manager:
            # For intersections, we don't need entity_type or cell_size - they're just icons
            inter_icon_svg = _get_icon_svg(inter_type, icon_size, icon_size, asset_manager, None, None)

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
                f'<line x1="{cx-40}" y1="{cy}" x2="{cx+40}" y2="{cy}" stroke="#9b6fd6" '
                f'stroke-width="12" stroke-linecap="round"/>'
                f'<line x1="{cx}" y1="{cy-40}" x2="{cx}" y2="{cy+40}" stroke="#9b6fd6" '
                f'stroke-width="12" stroke-linecap="round"/>'
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
        if asset_manager and len(route_points) >= 2:
            try:
                # Get FTS icon
                fts_svg_content = asset_manager.get_asset_inline("FTS")
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

                    agv_marker_svg = (
                        f'<g transform="translate({agv_x - half_size}, {agv_y - half_size}) '
                        f'scale({scale_factor})">{svg_content_clean}</g>'
                    )
            except Exception:
                # Fallback to circle if FTS icon fails
                agv_x = route_points[len(route_points) // 2][0]
                agv_y = route_points[len(route_points) // 2][1]
                agv_marker_svg = (
                    f'<circle cx="{agv_x}" cy="{agv_y}" r="16" fill="#4CAF50" stroke="#fff" stroke-width="2" />'
                )

        # Route thickness reduced by 25% (from 8 to 6)
        route_svg = (
            f'<polyline points="{pts}" stroke="#ff8c00" stroke-width="6" fill="none" '
            f'stroke-linejoin="round" stroke-linecap="round" />'
            f'<circle cx="{start[0]}" cy="{start[1]}" r="6" fill="#ff8c00" stroke="#fff" stroke-width="2" />'
            f'<circle cx="{end[0]}" cy="{end[1]}" r="6" fill="#ff8c00" stroke="#fff" stroke-width="2" />'
            f"{agv_marker_svg}"
        )

    # Container border - medium gray
    container_border = (
        f'<rect x="0" y="0" width="{CANVAS_W}" height="{CANVAS_H}" fill="none" ' f'stroke="#888888" stroke-width="2" />'
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'width="{int(CANVAS_W*scale)}" height="{int(CANVAS_H*scale)}">'
        f"<style>"
        f".cell-group .tooltip {{ font-family: Arial; font-size: 12px; }}"
        f".cell-group:hover .tooltip {{ display: block !important; font-weight: bold; }}"
        f".cell-group {{ cursor: {'pointer' if enable_click else 'default'}; }}"
        f".cell-group:hover rect {{ stroke: #ff8c00 !important; fill: rgba(255, 152, 0, 0.1) !important; }}"
        f".cell-group.clicked rect {{ stroke-width: 4 !important; stroke: #ff8c00 !important; "
        f"fill: rgba(255, 152, 0, 0.1) !important; }}"
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


# ============================================================================
# Main API Function
# ============================================================================


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
    highlight_cells: Optional[list] = None,
    scale: Optional[float] = None,
) -> None:
    """
    Display scalable SVG-based shopfloor layout with highlighting and route visualization.

    Args:
        active_module_id: ID of active module (for highlighting)
        active_intersections: List of active intersection IDs
        title: Component title
        show_controls: Show control elements (default: False)
        unique_key: Unique key for Streamlit components
        mode: Usage mode (kept for API compatibility, defaults to "view_mode")
        max_width: Container width in pixels (default: 800) - used to calculate scale if scale not provided
        max_height: Container height in pixels (default: 600) - used to calculate scale if scale not provided
        layout_config: Optional layout configuration dict (loads from config if None)
        asset_manager: Optional asset manager instance (loads if None)
        route_points: Optional list of (x, y) pixel coordinates for AGV route visualization
        agv_progress: Progress along route (0.0 to 1.0) for AGV marker positioning
        on_cell_click: Optional callback function for cell click events (not used, kept for compatibility)
        enable_click: Enable click-to-select functionality (default: False)
        highlight_cells: Optional list of (row, col) tuples to highlight (for compound regions)
        scale: Optional scale factor (0.25 to 2.0). If not provided, calculated from max_width/max_height.
    """
    # Calculate scale from max_width/max_height if not provided
    if scale is None:
        # Calculate scale based on max_width (default CANVAS_W = 804)
        scale = max_width / CANVAS_W if max_width else 1.0
        # Also consider max_height if provided
        if max_height:
            scale_from_height = max_height / CANVAS_H if max_height else 1.0
            scale = min(scale, scale_from_height)  # Use smaller scale to fit both dimensions

    # Generate hint HTML if click is enabled (rendered inside HTML to avoid spacing)
    hint_html = ""
    if enable_click:
        hint_html = """
        <div style="margin: 0.25rem 0 0.5rem 0; padding: 0.75rem; background-color: #e3f2fd; border-radius: 0.5rem; border-left: 4px solid #2196F3;">
            <span style="font-size: 1.2em;">💡</span>
            <span style="margin-left: 0.5rem;">Click on any position in the grid to view its details below</span>
        </div>
        """

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
        layout_config = {"modules": [], "fixed_positions": [], "intersections": []}

    # Load asset manager if not provided
    if asset_manager is None:
        try:
            asset_manager = get_asset_manager()
        except Exception as e:
            logger.warning(f"Failed to load asset manager: {e}")
            asset_manager = None

    # If active_module_id is provided and no highlight_cells, convert to highlight_cells for compound regions
    if active_module_id and not highlight_cells:
        try:
            from omf2.config.ccu.shopfloor_display import get_display_region_for_key

            # Get the display region for this module (handles compound regions like HBW/DPS)
            highlight_cells = get_display_region_for_key(active_module_id)
            logger.debug(f"Active module {active_module_id} → highlight_cells: {highlight_cells}")
        except Exception as e:
            logger.warning(f"Failed to get display region for {active_module_id}: {e}")
            # Fallback to old behavior - just use active_module_id
            pass

    # Convert highlight_cells to list of tuples if provided
    highlight_tuples = None
    if highlight_cells:
        highlight_tuples = []
        for cell in highlight_cells:
            if isinstance(cell, (list, tuple)) and len(cell) >= 2:
                highlight_tuples.append((int(cell[0]), int(cell[1])))

    # Generate heading HTML if title is provided (with Streamlit-standard font styling)
    heading_html = ""
    if title:
        try:
            shop_icon = get_asset_manager().get_asset_inline("SHOPFLOOR_LAYOUT", size_px=32) or ""
            heading_html = f"""
            <div style="margin: 0.25rem 0 0.25rem 0;">
                <h3 style="margin: 0; padding: 0; font-size: 1.5rem; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; display:flex; align-items:center; gap:8px; line-height: 1.4;">
                    {shop_icon} {title}
                </h3>
            </div>
            """
        except Exception:
            heading_html = f"""
            <div style="margin: 0.25rem 0 0.25rem 0;">
                <h3 style="margin: 0; padding: 0; font-size: 1.5rem; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.4;">🏭 {title}</h3>
            </div>
            """

    # Debug: Log asset manager status
    if asset_manager:
        logger.debug(f"Asset manager available: {type(asset_manager)}")
    else:
        logger.warning("Asset manager is None - SVGs will not be rendered!")

    # Render SVG using new renderer
    try:
        svg_content = render_shopfloor_svg(
            layout=layout_config,
            asset_manager=asset_manager,
            highlight_cells=highlight_tuples,
            enable_click=enable_click,
            route_points=route_points,
            agv_progress=agv_progress,
            scale=scale,
        )
        logger.info(f"✅ SVG content generated: length={len(svg_content) if svg_content else 0}")
        if not svg_content or len(svg_content) < 100:
            logger.error(f"❌ SVG content is too short or empty! length={len(svg_content) if svg_content else 0}")
    except Exception as e:
        logger.error(f"❌ Error in render_shopfloor_svg: {e}", exc_info=True)
        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><text x="400" y="300" text-anchor="middle" fill="red">Error rendering SVG: {e}</text></svg>'

    # Add JavaScript for interactive highlighting (hover/click)
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

    # Combine heading + hint + SVG + JavaScript
    # Add unique ID to force refresh (prevent caching)
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    # Ensure SVG container has proper styling and is visible
    html_fragment = f"""
    {heading_html}
    {hint_html}
    <div id="shopfloor-svg-{unique_id}" style="width:{int(CANVAS_W*scale)}px; height:{int(CANVAS_H*scale)}px; overflow:visible; position:relative;">
      {svg_content}
    </div>
    {click_script}
    """

    # Debug: Log HTML fragment info
    logger.info(
        f"📄 HTML fragment length: {len(html_fragment)}, contains SVG: {'<svg' in html_fragment}, contains cell-group: {'cell-group' in html_fragment}"
    )

    # Render using st.components.v1.html (st.markdown doesn't properly render complex HTML with SVG)
    try:
        extra_height = 60  # heading spacing
        if enable_click:
            extra_height += 60  # hint box
        total_height = int(CANVAS_H * scale) + extra_height + 20  # +20px padding
        logger.info(f"🎬 Rendering with st.components.v1.html: height={total_height}")
        st.components.v1.html(html_fragment, height=total_height, scrolling=False)
        logger.info("✅ st.components.v1.html rendered successfully")
    except Exception as e:
        logger.error(f"❌ st.components.v1.html failed: {e}", exc_info=True)
        # Fallback: try st.markdown (may not work well for complex HTML)
        try:
            logger.warning("⚠️ Falling back to st.markdown (may not render correctly)")
            st.markdown(html_fragment, unsafe_allow_html=True)
        except Exception as e2:
            logger.error(f"❌ st.markdown also failed: {e2}", exc_info=True)


# ============================================================================
# REMOVED: Legacy HTML/CSS Grid Functions (replaced by SVG rendering)
# All legacy functions have been removed and replaced by the SVG-based
# rendering in render_shopfloor_svg()
# ============================================================================


# Export für OMF2-Integration
__all__ = ["show_shopfloor_layout"]
