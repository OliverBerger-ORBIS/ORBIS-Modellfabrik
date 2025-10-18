#!/usr/bin/env python3
"""
OMF2 Asset Manager
Verwaltet Module-Icons und HTML-Templates für Dashboard-Visualisierung
Version: 2.0.0
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)


class OMF2AssetManager:
    """Verwaltet OMF2-Assets (Icons, Templates) für konsistente Visualisierung"""

    def __init__(self):
        """Initialisiert den Asset Manager - vereinfacht"""
        self.assets_dir = Path(__file__).parent
        self.svgs_dir = self.assets_dir / "svgs"  # Alle SVGs (Icons + Logos) in einem Verzeichnis
        self.module_icons = self._load_module_icons()
        self.html_templates = self._load_html_templates()

    def _load_module_icons(self) -> Dict[str, str]:
        """Lädt verfügbare Module-Icons (alle SVGs in svgs/) - vereinfacht"""
        icons = {}

        # Direktes Icon-Mapping - einfach und klar
        icon_mapping = {
            # Hauptmodule (Registry-definiert)
            "HBW": "ic_ft_hbw.svg",  # High-Bay Warehouse
            "DPS": "ic_ft_dps.svg",  # Delivery/Pickup Station
            "MILL": "ic_ft_mill.svg",  # Milling Station
            "DRILL": "ic_ft_drill.svg",  # Drilling Station
            "AIQS": "ic_ft_aiqs.svg",  # AI Quality System
            "CHRG": "ic_ft_chrg.svg",  # Charging Station
            "FTS": "ic_ft_fts.svg",  # Flexible Transport System
            # Unterstützende Objekte
            "TXT": "router.svg",  # TXT Controller
            "ROUTER": "router.svg",  # Network Router
            "PLATINE": "construction.svg",  # Circuit Board
            "RPI": "router.svg",  # Raspberry Pi
            "MOSQUITTO": "wifi.svg",  # MQTT Broker
            "MACHINE": "precision_manufacturing.svg",  # Generic Machine
            "PC_TABLET": "router.svg",  # PC/Tablet
        }

        # Spezielle Icons - IDs aus shopfloor_layout.json (BINDEND!) - neue sz24 Icons
        icon_mapping.update(
            {
                "1": "point_scan_3sections.svg",  # Intersection 1 (3 Sektionen)
                "2": "point_scan_3sections.svg",  # Intersection 2 (3 Sektionen)
                "3": "point_scan_3sections.svg",  # Intersection 3 (3 Sektionen)
                "4": "point_scan_3sections.svg",  # Intersection 4 (3 Sektionen)
                "EMPTY": None,  # Leer - kein Icon
            }
        )

        # Empty-Position-Assets - spezifische Zuordnung für Rectangle/Square1/Square2
        empty_assets = {
            # EMPTY1 Assets (Position [0,0])
            "EMPTY1_rectangle": "ORBIS_logo_RGB.svg",
            "EMPTY1_square1": "shelves.svg",
            "EMPTY1_square2": "conveyor_belt.svg",
            # EMPTY2 Assets (Position [0,3])
            "EMPTY2_rectangle": "DSP_ITOT_Control_2x1.svg",  # DSP test logo
            "EMPTY2_square1": "warehouse.svg",
            "EMPTY2_square2": "delivery_truck_speed.svg",
            # Fallback für direkte Namen (für Hybrid-App)
            "ORBIS": "ORBIS_logo_RGB.svg",
        }

        # Empty-Assets zu icon_mapping hinzufügen
        icon_mapping.update(empty_assets)

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

    def _load_html_templates(self) -> Dict[str, Any]:
        """Lädt HTML-Templates für UI-Komponenten"""
        return {
            "workpiece_colors": {
                "RED": {"bg": "#ff0000", "border": "#cc0000", "text": "white"},
                "BLUE": {"bg": "#0066ff", "border": "#0044cc", "text": "white"},
                "WHITE": {"bg": "#e0e0e0", "border": "#b0b0b0", "text": "black"},
            },
            "status_colors": {
                "READY": "#4caf50",  # Grün
                "BUSY": "#ff9800",  # Orange
                "BLOCKED": "#f44336",  # Rot
                "OFFLINE": "#9e9e9e",  # Grau
                "ACTIVE": "#2196f3",  # Blau (für aktive Station)
            },
        }

    def get_module_icon_path(self, module_name: str) -> Optional[str]:
        """Gibt den Pfad zum Modul-Icon zurück"""
        # Direkte Suche (case-sensitive für EMPTY1_rectangle etc.)
        if module_name in self.module_icons:
            return self.module_icons[module_name]
        # Fallback: uppercase für Module (MILL, DRILL etc.)
        return self.module_icons.get(module_name.upper())

    def get_workpiece_svg_path(self, workpiece_type: str, state: str = "product") -> Optional[str]:
        """Gibt den Pfad zur Workpiece-SVG zurück - vereinheitlichte Namenskonvention"""
        workpiece_dir = self.assets_dir / "workpiece"

        # NEUE VEREINHEITLICHTE NAMENSKONVENTION:
        # blue_product.svg, white_product.svg, red_product.svg
        # Passt zu Registry-Entitäten und CCU-Domain-Konfiguration

        # Haupt-SVG: Produkt-spezifisch
        product_svg_filename = f"{workpiece_type.lower()}_product.svg"
        product_svg_path = workpiece_dir / product_svg_filename

        if product_svg_path.exists():
            return str(product_svg_path)

        # Fallback: Legacy-Unterstützung für spezifische Zustände
        legacy_filenames = {
            "unprocessed": f"{workpiece_type.lower()}_unprocessed.svg",
            "instock_unprocessed": f"{workpiece_type.lower()}_instock_unprocessed.svg",
            "instock_reserved": f"{workpiece_type.lower()}_instock_reserved.svg",
            "3dim": f"{workpiece_type.lower()}_3dim.svg",
        }

        # Versuche Legacy-Zustand falls gewünscht
        if state in legacy_filenames:
            legacy_filename = legacy_filenames[state]
            legacy_path = workpiece_dir / legacy_filename

            if legacy_path.exists():
                return str(legacy_path)

        # Letzter Fallback: Palett-SVG
        palett_path = workpiece_dir / "palett.svg"
        if palett_path.exists():
            return str(palett_path)

        return None

    def get_workpiece_svg_content(self, workpiece_type: str, state: str = "unprocessed") -> Optional[str]:
        """Lädt den Inhalt einer Workpiece-SVG"""
        svg_path = self.get_workpiece_svg_path(workpiece_type, state)
        if svg_path and os.path.exists(svg_path):
            try:
                with open(svg_path, encoding="utf-8") as svg_file:
                    return svg_file.read()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Workpiece-SVG {svg_path}: {e}")
        return None

    # =========================================================================
    # WORKPIECE SVG METHODS
    # =========================================================================

    def get_workpiece_product(self, color: str) -> Optional[str]:
        """Lädt Product-SVG für gegebene Farbe (BLUE, WHITE, RED)"""
        return self._get_workpiece_svg_by_pattern(f"{color.lower()}_product.svg")

    def get_workpiece_3dim(self, color: str) -> Optional[str]:
        """Lädt 3D-SVG für gegebene Farbe"""
        return self._get_workpiece_svg_by_pattern(f"{color.lower()}_3dim.svg")

    def get_workpiece_unprocessed(self, color: str) -> Optional[str]:
        """Lädt Unprocessed-SVG für gegebene Farbe"""
        return self._get_workpiece_svg_by_pattern(f"{color.lower()}_unprocessed.svg")

    def get_workpiece_instock_unprocessed(self, color: str) -> Optional[str]:
        """Lädt Instock Unprocessed-SVG für gegebene Farbe"""
        return self._get_workpiece_svg_by_pattern(f"{color.lower()}_instock_unprocessed.svg")

    def get_workpiece_instock_reserved(self, color: str) -> Optional[str]:
        """Lädt Instock Reserved-SVG für gegebene Farbe"""
        return self._get_workpiece_svg_by_pattern(f"{color.lower()}_instock_reserved.svg")

    def get_workpiece_palett(self) -> Optional[str]:
        """Lädt die spezielle Palett-SVG für alle Workpieces"""
        return self._get_workpiece_svg_by_pattern("palett.svg")

    def _get_workpiece_svg_by_pattern(self, filename: str) -> Optional[str]:
        """Hilfsmethode: Lädt SVG-Inhalt basierend auf Dateinamen"""
        workpiece_dir = self.assets_dir / "workpiece"
        svg_path = workpiece_dir / filename
        if svg_path.exists():
            try:
                with open(svg_path, encoding="utf-8") as svg_file:
                    return svg_file.read()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Workpiece-SVG {svg_path}: {e}")
        return None

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
        """Gibt den Asset-Pfad für Empty-Position-Assets zurück

        Args:
            empty_id: Empty-Position ID (z.B. "EMPTY1", "EMPTY2")
            asset_type: Asset-Typ (z.B. "rectangle", "square1", "square2")

        Returns:
            Asset-Pfad oder None wenn nicht gefunden
        """
        asset_key = f"{empty_id}_{asset_type}"
        if asset_key in self.module_icons:
            icon_file = self.module_icons[asset_key]
            if icon_file:
                return str(self.svgs_dir / icon_file)
        return None

    def get_empty_position_asset_by_name(self, asset_name: str) -> Optional[str]:
        """Gibt den Asset-Pfad für Empty-Position-Assets zurück (Fallback-Methode)

        Args:
            asset_name: Direkter Asset-Name (z.B. "ORBIS", "shelves")

        Returns:
            Asset-Pfad oder None wenn nicht gefunden
        """
        if asset_name in self.module_icons:
            icon_file = self.module_icons[asset_name]
            if icon_file:
                return str(self.svgs_dir / icon_file)
        return None

    def get_workpiece_box_html(self, workpiece_type: str, count: int = 0, available: bool = True) -> str:
        """Generiert HTML für Werkstück-Box"""
        colors = self.html_templates["workpiece_colors"]
        color_config = colors.get(workpiece_type.upper(), colors["WHITE"])

        return f"""
        <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: flex-start; height: 100%; text-align: left; margin: 10px;">
            <div style="width: 120px; height: 80px; background-color: {color_config['bg']}; border: 2px solid {color_config['border']}; border-radius: 4px; margin: 0 0 10px 0; display: flex; align-items: center; justify-content: center;">
                <div style="color: {color_config['text']}; font-weight: bold; font-size: 14px;">{workpiece_type}</div>
            </div>
            <div style="margin: 5px 0;">
                <strong>Bestand: {count}</strong>
            </div>
            <div style="margin: 5px 0;">
                <strong>Verfügbar: {'✅ Ja' if available else '❌ Nein'}</strong>
            </div>
        </div>
        """

    def get_status_badge_html(self, status: str, status_type: str = "info") -> str:
        """Generiert HTML für Status-Badge"""
        status_colors = self.html_templates["status_colors"]
        color = status_colors.get(status.upper(), "#2196f3")

        return f"""
        <span style="
            background-color: {color};
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
        ">
            {status}
        </span>
        """


# Singleton-Instanz
_asset_manager_instance = None


def get_asset_manager() -> OMF2AssetManager:
    """Gibt die Singleton-Instanz des Asset Managers zurück - vereinfacht"""
    global _asset_manager_instance
    if _asset_manager_instance is None:
        _asset_manager_instance = OMF2AssetManager()
        logger.info("📁 OMF2 Asset Manager initialized")
    return _asset_manager_instance
