#!/usr/bin/env python3
"""
Product Rendering Utilities
Helper functions for rendering product SVGs with standardized sizes using Base64 data URLs
"""

from omf2.ui.common.ui_constants import PRODUCT_SVG_BASE_SIZE


def render_product_svg_as_img(
    data_url: str,
    scale: float = 1.0,
    border_style: str = "1px solid #ccc",
    padding: str = "10px",
    margin: str = "5px",
) -> str:
    """
    Renders a product SVG using <img> tag with Base64 data URL for Chrome compatibility.

    This method works around Chromium's iframe CSS class handling issue by using
    Base64-encoded SVG data URLs with the <img> tag instead of inline SVG.

    Args:
        data_url: Base64 data URL (data:image/svg+xml;base64,...)
        scale: Scaling factor (default 1.0 = 200px)
        border_style: CSS border style
        padding: CSS padding
        margin: CSS margin

    Returns:
        HTML string with styled img container
    """
    size = int(PRODUCT_SVG_BASE_SIZE * scale)

    # Use <img> tag with data URL - works in all browsers including Chromium
    container_style = f"border: {border_style}; padding: {padding}; margin: {margin}; text-align: center; width: {size}px; height: {size}px; display: inline-block;"
    img_style = f"width: {size}px; height: {size}px; object-fit: contain;"

    return f'<div style="{container_style}"><img src="{data_url}" style="{img_style}" alt="Product SVG" /></div>'
