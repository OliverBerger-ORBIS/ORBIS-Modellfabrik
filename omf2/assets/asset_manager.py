#!/usr/bin/env python3
"""
OMF2 Asset Manager
Zentraler Asset-Manager für alle SVG-Assets (Module-Icons, Headings, Workpieces, Shopfloor)
Version: 3.0.0 - Unified Asset Management
"""

import re
import uuid
from pathlib import Path
from typing import Dict, Optional, Tuple

import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Product SVG sizing constants
PRODUCT_SVG_BASE_SIZE = 200  # Default base size in pixels for product SVGs (200x200 container)

# Globale Defaults
ASSET_DEFAULTS = {
    "fallback": "placeholders/question.svg",
    "empty": "placeholders/empty.svg",
}

# Zentrale Mapping-Struktur: logical_key -> (subdirectory, filename)
# Unter assets/svg/ -> subdirectory/filename
ASSET_MAPPINGS: Dict[str, Tuple[Optional[str], Optional[str]]] = {
    # === MODULE ICONS (shopfloor) ===
    "MILL": ("shopfloor", "milling-machine.svg"),
    "DRILL": ("shopfloor", "bohrer.svg"),
    "HBW": ("shopfloor", "stock.svg"),
    "DPS": ("shopfloor", "robot-arm.svg"),
    "FTS": ("shopfloor", "robotic.svg"),
    "AIQS": ("shopfloor", "ai-assistant.svg"),
    "CHRG": ("shopfloor", "fuel.svg"),
    # Unterstützende Objekte
    "TXT": ("shopfloor", "mixer.svg"),
    "ROUTER": ("shopfloor", "wifi-router.svg"),
    "PLATINE": ("shopfloor", "cpu.svg"),
    "RPI": ("shopfloor", "microcontroller.svg"),
    "MOSQUITTO": ("shopfloor", "wifi.svg"),
    "MACHINE": ("shopfloor", "robot-arm.svg"),
    "PC_TABLET": ("shopfloor", "responsive.svg"),
    "OPC_UA": ("shopfloor", "database.svg"),
    # === SHOPFLOOR ASSETS ===
    # Intersections
    "INTERSECTION-1": ("shopfloor", "intersection1.svg"),
    "INTERSECTION-2": ("shopfloor", "intersection2.svg"),
    "INTERSECTION-3": ("shopfloor", "intersection3.svg"),
    "INTERSECTION-4": ("shopfloor", "intersection4.svg"),
    # Legacy aliases for backward compatibility
    "1": ("shopfloor", "intersection1.svg"),
    "2": ("shopfloor", "intersection2.svg"),
    "3": ("shopfloor", "intersection3.svg"),
    "4": ("shopfloor", "intersection4.svg"),
    # Company/Software Logos
    "COMPANY_rectangle": ("shopfloor", "ORBIS_logo_RGB.svg"),
    "SOFTWARE_rectangle": ("shopfloor", "information-technology.svg"),
    "ORBIS": ("shopfloor", "ORBIS_logo_RGB.svg"),  # Legacy alias
    "DSP": ("shopfloor", "information-technology.svg"),  # Legacy alias
    # Attached Assets
    "HBW_SQUARE1": ("shopfloor", "factory.svg"),
    "HBW_SQUARE2": ("shopfloor", "conveyor.svg"),
    "DPS_SQUARE1": ("shopfloor", "warehouse.svg"),
    "DPS_SQUARE2": ("shopfloor", "order-tracking.svg"),
    # === HEADING ICONS ===
    "DASHBOARD_ADMIN": ("headings", "visualisierung.svg"),
    "ORDERS": ("headings", "lieferung-bestellen.svg"),
    "PROCESS": ("headings", "gang.svg"),
    "CONFIGURATION": ("headings", "system.svg"),
    "MODULES_TAB": ("headings", "mehrere.svg"),
    "MESSAGE_CENTER": ("headings", "zentral.svg"),
    "GENERIC_STEERING": ("headings", "dezentral_1.svg"),
    "SYSTEM_LOGS": ("headings", "log.svg"),
    "ADMIN_SETTINGS": ("headings", "unterstutzung.svg"),
    "DASHBOARD": ("headings", "visualisierung.svg"),
    "MQTT_CLIENTS": ("headings", "satellitenschussel.svg"),
    "GATEWAY": ("headings", "router_1.svg"),
    "TOPIC": ("headings", "etikett.svg"),
    "TOPICS": ("headings", "etikett.svg"),
    "SCHEMAS": ("headings", "diagramm.svg"),
    "MODULES_ADMIN": ("headings", "mehrere.svg"),
    "STATIONS": ("headings", "dezentral.svg"),
    "TXT_CONTROLLERS": ("headings", "system.svg"),
    "WORKPIECES": ("headings", "box.svg"),
    "PRODUCTION_ORDERS": ("headings", "maschine.svg"),
    "STORAGE_ORDERS": ("headings", "ladung.svg"),
    "FACTORY_CONFIGURATION": ("headings", "grundriss.svg"),
    "SHOPFLOOR_LAYOUT": ("headings", "grundriss.svg"),
    "CUSTOMER_ORDERS": ("headings", "lieferung-bestellen.svg"),
    "PURCHASE_ORDERS": ("headings", "box.svg"),
    "INVENTORY": ("headings", "warehouse.svg"),
    "SENSOR_DATA": ("headings", "smart.svg"),
    # === PLACEHOLDERS ===
    "CAMERA_PLACEHOLDER": ("placeholders", "camera-placeholder.svg"),
    "EMPTY": ("placeholders", "empty.svg"),
    "QUESTION": ("placeholders", "question.svg"),
    # Special
    "EMPTY_MODULE": (None, None),  # Explizit kein Icon (für leere Shopfloor-Positionen)
}


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
    """Zentraler Asset-Manager für alle SVG-Assets (Module-Icons, Headings, Workpieces, Shopfloor)"""

    def __init__(self):
        """Initialisiert den Asset Manager mit neuer vereinheitlichten Struktur"""
        self.assets_dir = Path(__file__).parent
        self.svg_dir = self.assets_dir / "svg"  # Zentrale SVG-Verzeichnis mit Unterverzeichnissen
        # SVG-Content Cache (key -> SVG content)
        self._svg_cache: Dict[str, str] = {}

    # =========================================================================
    # CORE ASSET METHODS (neue vereinheitlichte API)
    # =========================================================================

    def get_asset_path(self, key: str) -> Optional[Path]:
        """Gibt Pfad zu Asset zurück oder None (mit Default-Fallback bei unbekannten Keys)

        Args:
            key: Logical asset key (z.B. "MILL", "DASHBOARD", "QUESTION")

        Returns:
            Path zum Asset oder None wenn nicht gefunden
        """
        # Direct lookup im Mapping
        if key not in ASSET_MAPPINGS:
            # Unbekannter Key - verwende Fallback
            fallback_key = ASSET_DEFAULTS["fallback"]
            if fallback_key in ASSET_MAPPINGS:
                subdir, filename = ASSET_MAPPINGS[fallback_key]
                if subdir and filename:
                    path = self.svg_dir / subdir / filename
                    if path.exists():
                        logger.warning(f"⚠️ Unknown asset key '{key}', using fallback: {path}")
                        return path
            return None

        subdir, filename = ASSET_MAPPINGS[key]

        # Special case: EMPTY_MODULE
        if subdir is None or filename is None:
            return None

        # Build path
        path = self.svg_dir / subdir / filename
        if path.exists():
            return path

        # Asset existiert nicht - sollte bei Pre-Commit gefangen werden
        logger.error(f"❌ Asset missing: {key} -> {path}")
        # Fallback zu question.svg (direkt Pfad auflösen)
        fallback_rel = ASSET_DEFAULTS["fallback"]
        if "/" in fallback_rel:
            fallback_subdir, fallback_filename = fallback_rel.split("/", 1)
            fallback_path = self.svg_dir / fallback_subdir / fallback_filename
            if fallback_path.exists():
                return fallback_path
        return None

    def get_asset_content(self, key: str, scoped: bool = True) -> Optional[str]:
        """Lädt SVG-Inhalt mit optionalem CSS-Scoping

        Args:
            key: Logical asset key
            scoped: Ob CSS-Scoping angewendet werden soll (default: True)

        Returns:
            SVG-Inhalt als String oder None
        """
        # Check cache first
        cache_key = f"{key}_scoped" if scoped else key
        if cache_key in self._svg_cache:
            return self._svg_cache[cache_key]

        path = self.get_asset_path(key)
        if not path or not path.exists():
            return None

        try:
            with open(path, encoding="utf-8") as f:
                svg_content = f.read()
                # Remove XML declaration for inline HTML
                svg_content = re.sub(r"<\?xml.*?\?>", "", svg_content)

                # Apply scoping if requested
                if scoped:
                    svg_content = scope_svg_styles(svg_content)

                # Cache result
                self._svg_cache[cache_key] = svg_content
                return svg_content
        except Exception as e:
            logger.error(f"❌ Error loading asset {key} from {path}: {e}")
            return None

    def get_asset_inline(self, key: str, size_px: Optional[int] = None, color: Optional[str] = None) -> Optional[str]:
        """Lädt SVG als inline HTML (für Headings)

        Args:
            key: Logical asset key
            size_px: Optional width/height injection
            color: Optional CSS color (if SVG uses currentColor)

        Returns:
            SVG-Inhalt als inline HTML oder None
        """
        svg = self.get_asset_content(key, scoped=True)
        if svg is None:
            return None

        # Size injection - replace existing width/height or add if missing
        if size_px:
            svg = re.sub(r'\s+width="[^"]*"', "", svg)
            svg = re.sub(r'\s+height="[^"]*"', "", svg)
            svg = re.sub(r"<svg\b", f'<svg width="{size_px}"', svg, count=1)

        # Color handling
        if color:
            if "currentColor" in svg or "--icon-fill" in svg:
                return f'<span style="display:inline-block; color:{color}; line-height:0; vertical-align:middle;">{svg}</span>'
            # Fallback: replace fill attributes
            svg_colored = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg)
            return f'<span style="display:inline-block; line-height:0; vertical-align:middle;">{svg_colored}</span>'

        return svg

    # =========================================================================
    # WORKPIECE SVG METHODS
    # =========================================================================

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
        workpiece_dir = self.svg_dir / "workpiece"
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
        workpiece_dir = self.svg_dir / "workpiece"

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
        """Zeigt ein Modul-Icon in Streamlit an (new unified API)"""
        icon_path = self.get_asset_path(module_name)
        if not icon_path:
            # Fallback: uppercase for modules (MILL, DRILL etc.)
            icon_path = self.get_asset_path(module_name.upper())

        if icon_path and icon_path.exists():
            st.image(str(icon_path), width=width, caption=caption or module_name)
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
        path = self.get_asset_path("COMPANY_rectangle")
        if path:
            logger.debug(f"🏢 ORBIS logo found: {path}")
            return str(path)
        else:
            logger.warning("⚠️ ORBIS logo not found")
            return None

    def get_shopfloor_module_html(
        self, module_type: str, module_id: str = "", is_active: bool = False, size: int = 100
    ) -> str:
        """Generiert HTML für Shopfloor-Modul mit SVG-Icon und Hervorhebung (quadratisches Grid) - new unified API"""
        # Get SVG content directly (already scoped)
        svg_content = self.get_asset_content(module_type, scoped=True)
        if not svg_content:
            # Fallback: uppercase for modules (MILL, DRILL etc.)
            svg_content = self.get_asset_content(module_type.upper(), scoped=True)

        # Aktive Station hervorheben (gelb wie IN_PROGRESS Icon)
        border_color = "#ff9800" if is_active else "#e0e0e0"  # Orange/Gelb für aktive Module
        border_width = "4px" if is_active else "2px"
        shadow = "0 4px 12px rgba(255, 152, 0, 0.3)" if is_active else "0 2px 6px rgba(0,0,0,0.1)"  # Gelber Schatten

        # Icon-Größe berechnen (66% der Zellengröße für prominente Darstellung)
        icon_size = int(size * 0.66)

        # Icon-Generierung
        icon_html = ""
        if svg_content:
            # SVG-Icon direkt einbetten
            # Remove existing width/height and add new size
            svg_content_clean = re.sub(r'\s+width="[^"]*"', "", svg_content)
            svg_content_clean = re.sub(r'\s+height="[^"]*"', "", svg_content_clean)
            svg_content_clean = re.sub(
                r"<svg\b", f'<svg width="{icon_size}" height="{icon_size}"', svg_content_clean, count=1
            )
            icon_html = svg_content_clean
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
