#!/usr/bin/env python3
"""
Heading icons registry and helper.

- Simple Python registry: HEADING_ICON_FILES: logical_key -> filename
- SVG files are expected in omf2/assets/headings/
- Provides get_svg_inline(key, size_px=None, color=None, locale=None)
"""

from pathlib import Path
from typing import Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)

# Directory where heading SVGs live (relative to this file)
HEADINGS_DIR = Path(__file__).parent / "headings"

# Try to reuse scoping util from existing asset_manager if available
try:
    from omf2.assets.asset_manager import scope_svg_styles as _scope_svg_styles  # type: ignore
except Exception:
    _scope_svg_styles = None


def _scope_svg(svg: str) -> str:
    if _scope_svg_styles:
        try:
            return _scope_svg_styles(svg)
        except Exception:
            logger.exception("scope_svg_styles failed; returning original SVG")
            return svg
    # minimal fallback: do nothing
    return svg


# --- Registry: logical keys -> filename (keep simple) -----------------------
HEADING_ICON_FILES: Dict[str, str] = {
    # CCU-TABS
    "DASHBOARD_ADMIN": "visualisierung.svg",
    "ORDERS": "lieferung-bestellen.svg",
    "PROCESS": "gang.svg",
    "CONFIGURATION": "system.svg",
    "MODULES_TAB": "mehrere.svg",
    # ADMIN-tabs
    "MESSAGE_CENTER": "zentral.svg",
    "GENERIC_STEERING": "dezentral_1.svg",
    "SYSTEM_LOGS": "log.svg",
    "ADMIN_SETTINGS": "unterstutzung.svg",
    # ADMIN-Settings-subtabs
    "DASHBOOARD": "visualisierung.svg",
    "MQTT_CLIENTS": "satellitenschussel.svg",
    "GATEWAY": "router_1.svg",
    "TOPIC": "etikett.svg",
    "SCHEMAS": "diagramm.svg",
    "MODULES_ADMIN": "mehrere.svg",
    "STATIONS": "dezentral.svg",
    "TXT_CONTROLLERS": "system.svg",
    "WORKPIECES": "box.svg",
    # CCU-ORDERS-Subtab
    "PRODUCTION_ORDERS": "maschine.svg",
    "STORAGE_ORDERS": "ladung.svg",
    # CCU-SUBTABS
    "FACTORY_CONFIGURATION": "grundriss.svg",
    "SHOPFLOOR_LAYOUT": "grundriss.svg",
}


# simple cache for loaded SVG contents
_SVG_CACHE: Dict[str, str] = {}


def _load_svg_file(filename: str) -> Optional[str]:
    if filename in _SVG_CACHE:
        return _SVG_CACHE[filename]
    path = HEADINGS_DIR / filename
    if not path.exists():
        logger.debug(f"Heading SVG not found: {path}")
        return None
    try:
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"<\?xml.*?\?>", "", content)  # remove xml declaration for inline HTML
        content = _scope_svg(content)
        _SVG_CACHE[filename] = content
        return content
    except Exception:
        logger.exception(f"Failed to read heading svg: {path}")
        return None


def get_svg_inline(key: str, size_px: Optional[int] = None, color: Optional[str] = None, locale: Optional[str] = None) -> Optional[str]:
    """Return inline SVG HTML for the given logical key.

    - key: logical registry key (from HEADING_ICON_FILES)
    - size_px: optional width/height injection
    - color: optional CSS color; if SVG uses currentColor, we wrap with a styled span
    - locale: not used in simple registry but kept for API compatibility
    """
    filename = HEADING_ICON_FILES.get(key)
    if not filename:
        logger.debug(f"Heading key not found: {key}")
        return None

    svg = _load_svg_file(filename)
    if svg is None:
        return None

    # size injection (only if width/height missing)
    if size_px:
        svg = re.sub(r"<svg\\b(?![^>]*\\bwidth=)(?![^>]*\\bheight=)", f'<svg width="{size_px}" height="{size_px}"', svg, count=1)

    # color handling (heuristic)
    if color:
        if "currentColor" in svg or "--icon-fill" in svg:
            return f'<span style="display:inline-block; color:{color}; line-height:0; vertical-align:middle;">{svg}</span>'
        # naive fallback: replace fill attributes
        svg_colored = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg)
        return f'<span style="display:inline-block; line-height:0; vertical-align:middle;">{svg_colored}</span>'

    return svg


def get_recommended_size(key: str) -> Optional[int]:
    # No recommendations in this simplified registry; return None
    return None
