#!/usr/bin/env python3
"""
Product Rendering Utilities
Helper functions for rendering product SVGs with standardized sizes
"""

from typing import Optional

from omf2.ui.common.ui_constants import PRODUCT_SVG_BASE_SIZE, WAREHOUSE_CELL_SIZE


def render_product_svg_container(
    svg_content: str,
    scale: float = 1.0,
    border_style: str = "1px solid #ccc",
    padding: str = "10px",
    margin: str = "5px",
    force_width_only: bool = False,
) -> str:
    """
    Renders a product SVG in a standardized container with fixed size.

    Args:
        svg_content: The SVG content to render
        scale: Scaling factor (default 1.0 = 200px)
        border_style: CSS border style
        padding: CSS padding
        margin: CSS margin
        force_width_only: If True, fix width to 200px and let height be proportional

    Returns:
        HTML string with styled SVG container
    """
    import re
    
    size = int(PRODUCT_SVG_BASE_SIZE * scale)

    # Add explicit width/height to SVG for proper rendering
    # This ensures SVGs render correctly even at small sizes
    if svg_content and '<svg' in svg_content:
        # Remove existing width/height attributes if present
        svg_content = re.sub(r'\s+width="[^"]*"', '', svg_content)
        svg_content = re.sub(r'\s+height="[^"]*"', '', svg_content)
        # Add width/height to fill container (100%)
        svg_content = re.sub(
            r'(<svg\s+[^>]*?)(>)',
            r'\1 width="100%" height="100%"\2',
            svg_content,
            count=1
        )

    if force_width_only:
        # Fix width, let height be proportional
        container_style = f"border: {border_style}; padding: {padding}; margin: {margin}; text-align: center;"
    else:
        # Square container with object-fit: contain
        container_style = f"border: {border_style}; padding: {padding}; margin: {margin}; text-align: center; width: {size}px; height: {size}px; display: flex; align-items: center; justify-content: center; overflow: hidden;"

    return f'<div style="{container_style}">{svg_content}</div>'


def render_warehouse_cell(
    svg_content: str, position_label: Optional[str] = None, workpiece_type: Optional[str] = None
) -> str:
    """
    Renders a warehouse cell with standardized size (200x200).

    Args:
        svg_content: The SVG content to render
        position_label: Label for the position (e.g., "A1")
        workpiece_type: Type of workpiece (e.g., "BLUE", "RED", "WHITE") or None for empty

    Returns:
        HTML string with styled warehouse cell
    """
    size = WAREHOUSE_CELL_SIZE

    # Container for the cell
    container_style = f"border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center; width: {size}px; height: {size}px; display: flex; flex-direction: column; align-items: center; justify-content: center;"

    html = f'<div style="{container_style}">'
    html += f'<div style="max-width: 100%; max-height: 100%; overflow: hidden;">{svg_content}</div>'
    html += "</div>"

    # Add label below if provided
    if position_label:
        status = f"[{workpiece_type}]" if workpiece_type else "[EMPTY]"
        html += f"<div style='text-align: center;'><strong>{position_label} {status}</strong></div>"

    return html


def render_product_card(
    svg_content: str, product_name: str, scale: float = 1.0, additional_info: Optional[dict] = None
) -> str:
    """
    Renders a complete product card with SVG and information.

    Args:
        svg_content: The SVG content to render
        product_name: Name of the product
        scale: Scaling factor (default 1.0 = 200px)
        additional_info: Optional dict with additional product information

    Returns:
        HTML string with complete product card
    """
    # SVG container
    svg_html = render_product_svg_container(svg_content, scale)

    # Product card wrapper
    card_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; margin: 10px;">
        {svg_html}
        <div style="text-align: center; margin-top: 10px;">
            <strong>{product_name}</strong>
        </div>
    """

    # Add additional info if provided
    if additional_info:
        card_html += '<div style="text-align: center; font-size: 0.9em; color: #666;">'
        for key, value in additional_info.items():
            card_html += f"<div>{key}: {value}</div>"
        card_html += "</div>"

    card_html += "</div>"

    return card_html
