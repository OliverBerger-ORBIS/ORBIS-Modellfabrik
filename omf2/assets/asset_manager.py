#!/usr/bin/env python3
"""
OMF2 Asset Manager
Verwaltet Module-Icons und HTML-Templates für Dashboard-Visualisierung
Version: 2.0.0
"""

import os
import re
import uuid
from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Product SVG sizing constants
PRODUCT_SVG_BASE_SIZE = 200  # Default base size in pixels for product SVGs (200x200 container)


def scope_svg_styles(svg_content: str) -> str:
    """
    Scopes SVG styles to prevent CSS class conflicts when multiple SVGs are embedded.

    This function:
    1. Generates a unique ID for each SVG instance
    2. Wraps the SVG content in a group with that unique ID
    3. Scopes all CSS selectors in the <style> section to that unique ID

    This ensures that CSS classes like .cls-1, .cls-2 don't conflict between different SVGs.
    """
    # Generate unique ID for this SVG instance
    unique_id = f"svg-{uuid.uuid4().hex[:8]}"

    # Check if SVG has a <style> section that needs scoping
    if "<style>" not in svg_content and "<style " not in svg_content:
        # No style section, return as-is
        return svg_content

    # Extract the style content
    style_pattern = r"<style[^>]*>(.*?)</style>"
    style_match = re.search(style_pattern, svg_content, re.DOTALL)

    if not style_match:
        return svg_content

    style_content = style_match.group(1)

    # Scope all CSS selectors by prepending with #unique_id
    # Match CSS selectors (e.g., .cls-1, #id, element)
    # This regex matches CSS rules like: .cls-1{fill:#000;}
    def scope_selector(match):
        selector = match.group(1).strip()
        properties = match.group(2)

        # Split multiple selectors (e.g., ".cls-1, .cls-2")
        selectors = [s.strip() for s in selector.split(",")]

        # Scope each selector
        scoped_selectors = []
        for sel in selectors:
            # Don't scope @-rules or already scoped selectors
            if sel.startswith("@") or sel.startswith("#" + unique_id):
                scoped_selectors.append(sel)
            else:
                scoped_selectors.append(f"#{unique_id} {sel}")

        return ",".join(scoped_selectors) + "{" + properties + "}"

    # Pattern to match CSS rules: selector{properties}
    css_rule_pattern = r"([^{]+)\{([^}]+)\}"
    scoped_style_content = re.sub(css_rule_pattern, scope_selector, style_content)

    # Replace the style content with scoped version
    scoped_svg = svg_content.replace(style_content, scoped_style_content)

    # Wrap the SVG content in a group with the unique ID
    # Find the opening <svg> tag and insert a <g id="unique_id"> after it
    svg_tag_pattern = r"(<svg[^>]*>)"

    def add_group(match):
        svg_tag = match.group(1)
        return f'{svg_tag}<g id="{unique_id}">'

    scoped_svg = re.sub(svg_tag_pattern, add_group, scoped_svg, count=1)

    # Close the group before the closing </svg> tag
    scoped_svg = scoped_svg.replace("</svg>", "</g></svg>", 1)

    return scoped_svg


class OMF2AssetManager:
    """Verwaltet OMF2-Assets (Icons, Templates) für konsistente Visualisierung"""

    def __init__(self):
        """Initialisiert den Asset Manager - vereinfacht"""
        self.assets_dir = Path(__file__).parent
        self.svgs_dir = self.assets_dir / "svgs"  # Alle SVGs (Icons + Logos) in einem Verzeichnis
        self.module_icons = self._load_module_icons()
        # HTML-Templates entfernt - Asset-Manager ist nur für Asset-Loading zuständig

    def _load_module_icons(self) -> Dict[str, str]:
        """Lädt verfügbare Module-Icons (alle SVGs in svgs/) - vereinfacht"""
        icons = {}

        # Direktes Icon-Mapping - einfach und klar
        icon_mapping = {
            # Hauptmodule (Registry-definiert)
            "HBW": "stock.svg",  # High-Bay Warehouse flaticon
            "DPS": "robot-arm.svg",  # Delivery/Pickup Station flaticon
            "MILL": "milling-machine.svg",  # Milling Station flaticon
            "DRILL": "bohrer.svg",  # Drilling Station flaticon
            "AIQS": "ai-assistant.svg",  # AI Quality System flaticon
            "CHRG": "fuel.svg",  # Charging Station flaticon
            "FTS": "ic_ft_fts.svg",  # Fahrerloses Transport System
            # Unterstützende Objekte
            "TXT": "mixer.svg",  # TXT Controller
            "ROUTER": "wifi-router.svg",  # Network Router
            "PLATINE": "cpu.svg",  # Circuit Board
            "RPI": "microcontroller.svg",  # Raspberry Pi
            "MOSQUITTO": "wifi.svg",  # MQTT Broker
            "MACHINE": "robot-arm.svg",  # Generic Machine
            "PC_TABLET": "responsive.svg",  # PC/Tablet
            "OPC_UA": "database.svg",  # OPC UA Server
        }

        # HEADING-ICONS - Import from dedicated module
        try:
            from omf2.assets.heading_icons import HEADING_ICON_FILES as heading_icons
        except Exception:
            logger.debug("heading_icons module not available; skipping heading icons import")
            heading_icons = {}
        icon_mapping.update(heading_icons)

        # Spezielle Icons - IDs aus shopfloor_layout.json (BINDEND!)
        # Each intersection has its number embedded in the SVG for proper route visualization
        icon_mapping.update(
            {
                "1": "intersection1.svg",  # Intersection 1 with number in center
                "2": "intersection2.svg",  # Intersection 2 with number in center
                "3": "intersection3.svg",  # Intersection 3 with number in center
                "4": "intersection4.svg",  # Intersection 4 with number in center
                "EMPTY": None,  # Leer - kein Icon
            }
        )

        # Shopfloor-Assets - canonical keys only (COMPANY_*, SOFTWARE_*)
        shopfloor_assets = {
            # Canonical COMPANY assets
            "COMPANY_rectangle": "ORBIS_logo_RGB.svg",
            "COMPANY_square1": "factory.svg",
            "COMPANY_square2": "conveyor.svg",
            # Canonical SOFTWARE assets
            "SOFTWARE_rectangle": "information-technology.svg",  # DSP logo
            "SOFTWARE_square1": "warehouse.svg",
            "SOFTWARE_square2": "order-tracking.svg",
            # Direct name fallback for backward compatibility (minimal)
            "ORBIS": "ORBIS_logo_RGB.svg",
            "DSP": "information-technology.svg",
        }

        # Shopfloor-Assets zu icon_mapping hinzufügen
        icon_mapping.update(shopfloor_assets)

        for module_name, icon_file in icon_mapping.items():
            if icon_file is None:
                icons[module_name] = None  # EMPTY hat kein Icon
                continue

            # SVG-Icon aus svgs/ Verzeichnis laden
            svg_path = self.svgs_dir / icon_file
            if svg_path.exists():
                icons[module_name] = str(svg_path)
            else:
                logger.warning(f"⚠️ No SVG icon found for {module_name}: {icon_file}")
                icons[module_name] = None

        logger.info(f"📁 Loaded {len(icons)} module icons from {self.svgs_dir}")
        return icons

    # HTML-Templates entfernt - Asset-Manager ist nur für Asset-Loading zuständig

    def get_module_icon_path(self, module_name: str) -> Optional[str]:
        """Gibt den Pfad zum Modul-Icon zurück

        Args:
            module_name: Name des Moduls oder Assets (z.B. "COMPANY_rectangle", "SOFTWARE_square1")

        Returns:
            Pfad zum SVG-Icon oder None

        Note:
            - Only canonical keys (COMPANY_*, SOFTWARE_*) are supported in productive code
            - Legacy EMPTY1/EMPTY2 keys have been removed from productive lookup
            - Fallback to uppercase for module names (MILL, DRILL, etc.)
        """
        # 1. Direct lookup (canonical keys preferred)
        if module_name in self.module_icons:
            return self.module_icons[module_name]

        # 2. Fallback: uppercase for modules (MILL, DRILL etc.)
        return self.module_icons.get(module_name.upper())

    def get_shopfloor_asset_path(self, asset_type: str, position: str) -> Optional[str]:
        """Gibt den Pfad zu einem Shopfloor-Asset zurück

        Args:
            asset_type: Typ des Assets ("COMPANY" oder "SOFTWARE") - canonical format
            position: Position des Assets ("rectangle", "square1", "square2")

        Returns:
            Pfad zum SVG-Icon oder None

        Examples:
            get_shopfloor_asset_path("COMPANY", "rectangle") -> path to ORBIS_logo_RGB.svg
            get_shopfloor_asset_path("SOFTWARE", "square1") -> path to warehouse.svg
        """
        # Use canonical key format: COMPANY_rectangle, SOFTWARE_square1, etc.
        asset_key = f"{asset_type}_{position}"
        return self.get_module_icon_path(asset_key)

    def get_asset_file(self, key: str) -> str:
        """Get deterministic asset file path for a given key

        Args:
            key: Asset key (e.g., "COMPANY_rectangle", "SOFTWARE_square1", "MILL")

        Returns:
            Deterministic path to SVG file or empty.svg as fallback

        Examples:
            get_asset_file("COMPANY_rectangle") -> "/omf2/assets/svgs/ORBIS_logo_RGB.svg"
            get_asset_file("SOFTWARE_square1") -> "/omf2/assets/svgs/warehouse.svg"
            get_asset_file("UNKNOWN") -> "/omf2/assets/svgs/empty.svg"
        """
        # Try to get the icon path
        icon_path = self.get_module_icon_path(key)

        if icon_path and Path(icon_path).exists():
            return icon_path

        # Fallback to empty.svg
        empty_path = self.svgs_dir / "empty.svg"
        if empty_path.exists():
            return str(empty_path)

        # Ultimate fallback - return empty.svg path even if it doesn't exist
        return str(self.svgs_dir / "empty.svg")

    def get_workpiece_svg_content(self, workpiece_type: str, state: str = "unprocessed") -> Optional[str]:
        """Lädt den Inhalt einer Workpiece-SVG mit CSS-Scoping für korrekte Darstellung"""
        return self._get_workpiece_svg_with_scoping(workpiece_type, state)

    def get_product_svg_with_sizing(
        self, workpiece_type: str, state: str = "product", scale: float = 1.0, enforce_width: bool = True
    ) -> Optional[str]:
        """
        Get workpiece SVG with standardized sizing (PRODUCT_SVG_BASE_SIZE = 200px)

        Args:
            workpiece_type: Workpiece color (BLUE, WHITE, RED)
            state: SVG pattern (product, 3dim, unprocessed, etc.)
            scale: Optional scale factor (default 1.0)
            enforce_width: If True and SVG is non-square, enforce width=200px with proportional height

        Returns:
            SVG content wrapped in container div with standardized sizing

        Example:
            # Get BLUE product SVG in 200x200 container
            svg_html = get_product_svg_with_sizing('BLUE', 'product')

            # Get WHITE 3dim SVG scaled to 300x300 (scale=1.5)
            svg_html = get_product_svg_with_sizing('WHITE', '3dim', scale=1.5)
        """
        svg_content = self.get_workpiece_svg(workpiece_type, state)
        if not svg_content:
            return None

        # Calculate container size with scale factor
        container_size = int(PRODUCT_SVG_BASE_SIZE * scale)

        # Wrap SVG in standardized container
        # If enforce_width and SVG is non-square, the container maintains aspect ratio
        return f"""
        <div style="width: {container_size}px; height: {container_size}px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
            {svg_content}
        </div>
        """

    # =========================================================================
    # WORKPIECE SVG METHODS
    # =========================================================================

    def get_workpiece_svg(self, color: str, pattern: str = "product") -> Optional[str]:
        """Lädt Workpiece-SVG für gegebene Farbe und Pattern

        Args:
            color: Farbe des Workpieces (BLUE, WHITE, RED)
            pattern: SVG-Pattern (product, 3dim, unprocessed, instock_unprocessed, instock_reserved)

        Returns:
            SVG-Inhalt mit CSS-Scoping oder None
        """
        return self._get_workpiece_svg_with_scoping(color, pattern)

    def get_workpiece_palett(self) -> Optional[str]:
        """Lädt die spezielle Palett-SVG für alle Workpieces in ORIGINAL-Größe"""
        workpiece_dir = self.assets_dir / "workpiece"
        palett_path = workpiece_dir / "palett.svg"
        if palett_path.exists():
            try:
                with open(palett_path, encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()
                    # Wende CSS-Scoping an für korrekte Darstellung
                    return scope_svg_styles(svg_content)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Palett-SVG {palett_path}: {e}")
        return None

    def _get_workpiece_svg_with_scoping(self, workpiece_type: str, state: str = "product") -> Optional[str]:
        """Lädt SVG-Inhalt mit CSS-Scoping für korrekte Darstellung"""
        workpiece_dir = self.assets_dir / "workpiece"

        # Erstelle Dateiname basierend auf Typ und Zustand
        filename = f"{workpiece_type.lower()}_{state}.svg"
        svg_path = workpiece_dir / filename

        if svg_path.exists():
            try:
                with open(svg_path, encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()
                    # Wende CSS-Scoping an für korrekte Darstellung
                    return scope_svg_styles(svg_content)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Workpiece-SVG {svg_path}: {e}")

        # Fallback: Palett-SVG
        palett_path = workpiece_dir / "palett.svg"
        if palett_path.exists():
            try:
                with open(palett_path, encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()
                    # Wende CSS-Scoping an für korrekte Darstellung
                    return scope_svg_styles(svg_content)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Palett-SVG {palett_path}: {e}")

        return None

    # DISPLAY_* METHODEN ENTFERNT - UI-Komponenten verwenden direkte SVG-Darstellung
    # Asset-Manager ist nur für Asset-Loading zuständig, nicht für UI-Darstellung

    def display_module_icon(self, module_name: str, width: int = 50, caption: str = None) -> None:
        """Zeigt ein Modul-Icon in Streamlit an"""
        icon_path = self.get_module_icon_path(module_name)
        if icon_path and os.path.exists(icon_path):
            st.image(icon_path, width=width, caption=caption or module_name)
        else:
            # Fallback zu Emoji
            fallback_emojis = {
                "HBW": "🏭",
                "DRILL": "🛠️",
                "MILL": "⚙️",
                "AIQS": "🤖",
                "DPS": "📦",
                "CHRG": "🔋",
                "FTS": "🚗",
                "EMPTY": "⚪",
                "INTERSECTION": "➕",
            }
            emoji = fallback_emojis.get(module_name.upper(), "🔧")
            st.markdown(f"{emoji} {module_name}")

    def display_orbis_logo(self, width: int = 150, use_container_width: bool = False):
        """
        Display ORBIS company logo with fallback

        Args:
            width: Logo width in pixels (default: 150 for prominent display)
            use_container_width: If True, logo fills container width
        """
        logo_path = self.get_orbis_logo_path()

        if logo_path:
            st.image(
                logo_path, width=width if not use_container_width else None, use_container_width=use_container_width
            )
            logger.debug(f"🏢 ORBIS logo displayed (width={width})")
        else:
            # Fallback: Factory emoji with caption
            st.markdown("# 🏭")
            st.caption("ORBIS Modellfabrik")
            logger.warning("⚠️ ORBIS logo fallback used (emoji)")

    def get_orbis_logo_path(self) -> Optional[str]:
        """Returns path to ORBIS company logo (SVG)"""
        logo_path = self.svgs_dir / "ORBIS_logo_RGB.svg"
        if logo_path.exists():
            logger.debug(f"🏢 ORBIS logo found: {logo_path}")
            return str(logo_path)
        else:
            logger.warning(f"⚠️ ORBIS logo not found: {logo_path}")
            return None

    def get_shopfloor_module_html(
        self, module_type: str, module_id: str = "", is_active: bool = False, size: int = 100
    ) -> str:
        """Generiert HTML für Shopfloor-Modul mit SVG-Icon und Hervorhebung (quadratisches Grid)"""
        icon_path = self.get_module_icon_path(module_type)

        # Aktive Station hervorheben (gelb wie IN_PROGRESS Icon)
        border_color = "#ff9800" if is_active else "#e0e0e0"  # Orange/Gelb für aktive Module
        border_width = "4px" if is_active else "2px"
        shadow = "0 4px 12px rgba(255, 152, 0, 0.3)" if is_active else "0 2px 6px rgba(0,0,0,0.1)"  # Gelber Schatten

        # Icon-Größe berechnen (66% der Zellengröße für prominente Darstellung)
        icon_size = int(size * 0.66)

        # Icon-Generierung
        icon_html = ""
        if icon_path and os.path.exists(icon_path):
            # SVG oder PNG Icon
            if icon_path.endswith(".svg"):
                # SVG-Icon direkt einbetten
                with open(icon_path, encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()
                    # SVG-Größe anpassen (alle Icons sind 24x24)
                    if 'viewBox="0 0 24 24"' in svg_content:
                        # 24x24 Icons - direkt width/height hinzufügen
                        svg_content = svg_content.replace("<svg", f'<svg width="{icon_size}" height="{icon_size}"')
                    else:
                        # Fallback: SVG-Inhalt in div einbetten mit fester Größe
                        svg_content = f'<div style="width: {icon_size}px; height: {icon_size}px; display: flex; align-items: center; justify-content: center;">{svg_content}</div>'
                    icon_html = svg_content
            else:
                # PNG-Icon als Base64
                import base64

                with open(icon_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    icon_html = f'<img src="data:image/png;base64,{img_data}" width="{icon_size}" height="{icon_size}" style="object-fit: contain;">'
        else:
            # Fallback zu Emoji (nur für unbekannte Module)
            if module_type.upper() == "EMPTY":
                icon_html = ""  # Leer - kein Icon
            else:
                fallback_emojis = {
                    "HBW": "🏭",
                    "DRILL": "🛠️",
                    "MILL": "⚙️",
                    "AIQS": "🤖",
                    "DPS": "📦",
                    "CHRG": "🔋",
                    "FTS": "🚗",
                }
                emoji = fallback_emojis.get(module_type.upper(), "🔧")
                icon_html = f'<div style="font-size: {icon_size}px;">{emoji}</div>'

        # Text nur für Module (nicht für EMPTY)
        text_html = ""
        if module_type.upper() not in ["EMPTY"] and module_id:
            text_html = f"""<div style="font-size: 9px; font-weight: bold; text-align: center; line-height: 1.1; max-width: 100%; word-wrap: break-word; position: absolute; bottom: 2px; left: 2px; right: 2px;">{module_id}</div>"""

        return f"""<div style="border: {border_width} solid {border_color}; border-radius: 8px; background: #fff; width: {size}px; height: {size}px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: {shadow}; margin: 2px; padding: 4px; transition: all 0.3s ease; position: relative;"><div style="flex: 1; display: flex; align-items: center; justify-content: center;">{icon_html}</div>{text_html}</div>"""

    def get_empty_position_asset(self, empty_id: str, asset_type: str) -> Optional[str]:
        """DEPRECATED: Use get_shopfloor_asset_path() with canonical keys instead

        Maintained for backward compatibility. Converts old EMPTY1/EMPTY2 format to canonical keys.

        Args:
            empty_id: Empty-Position ID (e.g. "COMPANY", "SOFTWARE")
            asset_type: Asset-Typ (e.g. "rectangle", "square1", "square2")

        Returns:
            Asset-Pfad oder None wenn nicht gefunden
        """
        # Convert to canonical format
        if empty_id in ["COMPANY", "SOFTWARE"]:
            return self.get_shopfloor_asset_path(empty_id, asset_type)

        # No longer support EMPTY1/EMPTY2 in productive code
        logger.warning(
            f"⚠️ DEPRECATED: get_empty_position_asset called with legacy key {empty_id}. Use canonical COMPANY/SOFTWARE keys."
        )
        return None

    def get_empty_position_asset_by_name(self, asset_name: str) -> Optional[str]:
        """DEPRECATED: Use get_module_icon_path() or get_asset_file() instead

        Maintained for backward compatibility. Returns asset path for direct names.

        Args:
            asset_name: Direkter Asset-Name (z.B. "ORBIS", "shelves")

        Returns:
            Asset-Pfad oder None wenn nicht gefunden
        """
        # Try direct lookup first
        if asset_name in self.module_icons:
            icon_file = self.module_icons[asset_name]
            if icon_file:
                return str(self.svgs_dir / icon_file)

        # Fallback: try to find in SVG directory
        potential_path = self.svgs_dir / f"{asset_name}.svg"
        if potential_path.exists():
            return str(potential_path)

        return None

    # VERALTETE HTML-TEMPLATES ENTFERNT
    # Asset-Manager ist nur für Asset-Loading zuständig, nicht für UI-Darstellung
    # UI-Komponenten verwenden direkte SVG-Darstellung mit st.markdown(..., unsafe_allow_html=True)


# Singleton-Instanz
_asset_manager_instance = None


def get_asset_manager() -> OMF2AssetManager:
    """Gibt die Singleton-Instanz des Asset Managers zurück - vereinfacht"""
    global _asset_manager_instance
    if _asset_manager_instance is None:
        _asset_manager_instance = OMF2AssetManager()
        logger.info("📁 OMF2 Asset Manager initialized")
    return _asset_manager_instance
