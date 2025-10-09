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
        """Initialisiert den Asset Manager"""
        self.assets_dir = Path(__file__).parent
        self.icons_dir = self.assets_dir / "icons"
        self.module_icons = self._load_module_icons()
        self.html_templates = self._load_html_templates()

    def _load_module_icons(self) -> Dict[str, str]:
        """Lädt verfügbare Module-Icons (SVG bevorzugt)"""
        icons = {}
        
        # SVG-Icons Verzeichnis
        svg_dir = self.assets_dir / "svgs"
        
        # Module-Icon-Mapping (SVG-Icons bevorzugt)
        icon_mapping = {
            "HBW": "warehouse_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "DRILL": "tools_power_drill_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "MILL": "construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "AIQS": "robot_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "DPS": "conveyor_belt_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "CHRG": "ev_station_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "FTS": "rv_hookup_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "TXT": "barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "RPI": "barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "MOSQUITTO": "barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "ROUTER": "barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "MACHINE": "construction_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "PLATINE": "barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "PC_TABLET": "barcode_scanner_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            # Spezielle Icons
            "INTERSECTION": "add_2_40dp_1F1F1F_FILL0_wght400_GRAD0_opsz40.svg",
            "EMPTY": None,  # Leer - kein Icon
        }

        for module_name, icon_file in icon_mapping.items():
            if icon_file is None:
                icons[module_name] = None  # EMPTY hat kein Icon
                continue
                
            # Zuerst SVG-Icon versuchen
            svg_path = svg_dir / icon_file
            if svg_path.exists():
                icons[module_name] = str(svg_path)
            else:
                # Fallback zu PNG-Icons
                png_path = self.icons_dir / icon_file.replace('.svg', '.png')
                if png_path.exists():
                    icons[module_name] = str(png_path)
                else:
                    # Fallback zu Standard-Icon
                    fallback_path = self.icons_dir / "machine_icon.png"
                    if fallback_path.exists():
                        icons[module_name] = str(fallback_path)
                    else:
                        logger.warning(f"⚠️ No icon found for {module_name}: {icon_file}")
                        icons[module_name] = None

        logger.info(f"📁 Loaded {len(icons)} module icons (SVG + PNG fallbacks) from {self.assets_dir}")
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
                "READY": "#4caf50",      # Grün
                "BUSY": "#ff9800",       # Orange
                "BLOCKED": "#f44336",    # Rot
                "OFFLINE": "#9e9e9e",    # Grau
                "ACTIVE": "#2196f3",     # Blau (für aktive Station)
            }
        }

    def get_module_icon_path(self, module_name: str) -> Optional[str]:
        """Gibt den Pfad zum Modul-Icon zurück"""
        return self.module_icons.get(module_name.upper())

    def display_module_icon(self, module_name: str, width: int = 50, caption: str = None) -> None:
        """Zeigt ein Modul-Icon in Streamlit an"""
        icon_path = self.get_module_icon_path(module_name)
        if icon_path and os.path.exists(icon_path):
            st.image(icon_path, width=width, caption=caption or module_name)
        else:
            # Fallback zu Emoji
            fallback_emojis = {
                "HBW": "🏭", "DRILL": "🛠️", "MILL": "⚙️", "AIQS": "🤖",
                "DPS": "📦", "CHRG": "🔋", "FTS": "🚗", "EMPTY": "⚪",
                "INTERSECTION": "➕"
            }
            emoji = fallback_emojis.get(module_name.upper(), "🔧")
            st.markdown(f"{emoji} {module_name}")

    def get_shopfloor_module_html(self, module_type: str, module_id: str = "", 
                                 is_active: bool = False, size: int = 100) -> str:
        """Generiert HTML für Shopfloor-Modul mit SVG-Icon und Hervorhebung (quadratisches Grid)"""
        icon_path = self.get_module_icon_path(module_type)
        
        # Aktive Station hervorheben
        border_color = "#2196f3" if is_active else "#e0e0e0"
        border_width = "4px" if is_active else "2px"
        shadow = "0 4px 12px rgba(33, 150, 243, 0.3)" if is_active else "0 2px 6px rgba(0,0,0,0.1)"
        
        # Icon-Größe berechnen (60% der Zellengröße)
        icon_size = int(size * 0.6)
        
        # Icon-Generierung
        icon_html = ""
        if icon_path and os.path.exists(icon_path):
            # SVG oder PNG Icon
            if icon_path.endswith('.svg'):
                # SVG-Icon direkt einbetten
                with open(icon_path, "r", encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()
                    # SVG-Größe anpassen
                    svg_content = svg_content.replace('width="40"', f'width="{icon_size}"')
                    svg_content = svg_content.replace('height="40"', f'height="{icon_size}"')
                    svg_content = svg_content.replace('viewBox="0 0 40 40"', f'viewBox="0 0 {icon_size} {icon_size}"')
                    icon_html = svg_content
            else:
                # PNG-Icon als Base64
                import base64
                with open(icon_path, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                    icon_html = f'<img src="data:image/png;base64,{img_data}" width="{icon_size}" height="{icon_size}" style="object-fit: contain;">'
        else:
            # Fallback zu Emoji (nur für INTERSECTION und unbekannte Module)
            if module_type.upper() == "INTERSECTION":
                icon_html = f'<div style="font-size: {icon_size}px;">➕</div>'
            elif module_type.upper() == "EMPTY":
                icon_html = ""  # Leer - kein Icon
            else:
                fallback_emojis = {
                    "HBW": "🏭", "DRILL": "🛠️", "MILL": "⚙️", "AIQS": "🤖",
                    "DPS": "📦", "CHRG": "🔋", "FTS": "🚗"
                }
                emoji = fallback_emojis.get(module_type.upper(), "🔧")
                icon_html = f'<div style="font-size: {icon_size}px;">{emoji}</div>'

        # Text nur für Module (nicht für EMPTY oder INTERSECTION)
        text_html = ""
        if module_type.upper() not in ["EMPTY", "INTERSECTION"] and module_id:
            text_html = f"""<div style="font-size: 9px; font-weight: bold; text-align: center; line-height: 1.1; max-width: 100%; word-wrap: break-word; position: absolute; bottom: 2px; left: 2px; right: 2px;">{module_id}</div>"""

        return f"""<div style="border: {border_width} solid {border_color}; border-radius: 8px; background: #fff; width: {size}px; height: {size}px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: {shadow}; margin: 2px; padding: 4px; transition: all 0.3s ease; position: relative;"><div style="flex: 1; display: flex; align-items: center; justify-content: center;">{icon_html}</div>{text_html}</div>"""

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
    """Gibt die Singleton-Instanz des Asset Managers zurück"""
    global _asset_manager_instance
    if _asset_manager_instance is None:
        _asset_manager_instance = OMF2AssetManager()
        logger.info("📁 OMF2 Asset Manager initialized")
    return _asset_manager_instance
