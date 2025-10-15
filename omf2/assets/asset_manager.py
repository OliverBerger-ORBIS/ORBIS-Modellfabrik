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

    def __init__(self, icon_style: str = "ic_ft"):
        """Initialisiert den Asset Manager
        
        Args:
            icon_style: Icon-Style ("ic_ft" für Fischertechnik, "omf" für OMF-Icons)
        """
        self.assets_dir = Path(__file__).parent
        self.svgs_dir = self.assets_dir / "svgs"
        self.logos_dir = self.assets_dir / "logos"
        self.icon_style = icon_style
        self.module_icons = self._load_module_icons()
        self.html_templates = self._load_html_templates()

    def _load_module_icons(self) -> Dict[str, str]:
        """Lädt verfügbare Module-Icons (alle SVGs in svgs/)"""
        icons = {}
        
        # Module-Icon-Mapping basierend auf icon_style
        if self.icon_style == "ic_ft":
            # Fischertechnik-Icons (ic_ft_*)
            icon_mapping = {
                "HBW": "ic_ft_hbw.svg",
                "DRILL": "ic_ft_drill.svg",
                "MILL": "ic_ft_mill.svg",
                "AIQS": "ic_ft_aiqs.svg",
                "DPS": "ic_ft_dps.svg",
                "CHRG": "ic_ft_chrg.svg",
                "FTS": "ic_ft_fts.svg",
                # Fallbacks für andere Module
                "TXT": "ic_ft_hbw.svg",      # Fallback
                "RPI": "ic_ft_hbw.svg",      # Fallback
                "MOSQUITTO": "ic_ft_hbw.svg", # Fallback
                "ROUTER": "ic_ft_hbw.svg",   # Fallback
                "MACHINE": "ic_ft_mill.svg", # Fallback
                "PLATINE": "ic_ft_hbw.svg",  # Fallback
                "PC_TABLET": "ic_ft_hbw.svg", # Fallback
            }
        else:  # icon_style == "omf"
            # OMF-Module - verwende ic_ft Icons als Fallback bis echte OMF SVGs erstellt sind
            icon_mapping = {
                # Hauptmodule (Registry-definiert) - Fallback zu ic_ft bis echte omf_ SVGs
                "HBW": "ic_ft_hbw.svg",      # High-Bay Warehouse
                "DPS": "ic_ft_dps.svg",      # Delivery/Pickup Station  
                "MILL": "ic_ft_mill.svg",    # Milling Station
                "DRILL": "ic_ft_drill.svg",  # Drilling Station
                "AIQS": "ic_ft_aiqs.svg",    # AI Quality System
                "CHRG": "ic_ft_chrg.svg",    # Charging Station
                "FTS": "ic_ft_fts.svg",      # Flexible Transport System
                
                # Unterstützende Objekte (seltener verwendet) - Fallback
                "TXT": "ic_ft_hbw.svg",      # TXT Controller - Fallback
                "ROUTER": "ic_ft_hbw.svg",   # Network Router - Fallback
                "PLATINE": "ic_ft_hbw.svg",  # Circuit Board - Fallback
                "RPI": "ic_ft_hbw.svg",      # Raspberry Pi - Fallback
                "MOSQUITTO": "ic_ft_hbw.svg", # MQTT Broker - Fallback
                "MACHINE": "ic_ft_mill.svg", # Generic Machine - Fallback
                "PC_TABLET": "ic_ft_hbw.svg", # PC/Tablet - Fallback
            }
        
        # Spezielle Icons - IDs aus shopfloor_layout.json (BINDEND!) - immer gleich
        icon_mapping.update({
            "1": "add_2.svg",              # Intersection 1
            "2": "point_scan.svg",         # Intersection 2
            "3": "align_flex_center.svg",  # Intersection 3
            "4": "add.svg",                # Intersection 4
            "EMPTY1": "shelves.svg",       # Empty Position 1
            "EMPTY2": "delivery_truck_speed.svg",  # Empty Position 2
            # Generische Fallbacks
            "INTERSECTION": "add_2.svg",   # Fallback für alle Intersections
            "EMPTY": None,                 # Leer - kein Icon
        })

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

        logger.info(f"📁 Loaded {len(icons)} module icons ({self.icon_style} style) from {self.svgs_dir}")
        return icons
    
    def set_icon_style(self, icon_style: str):
        """Ändert den Icon-Style und lädt Icons neu
        
        Args:
            icon_style: "ic_ft" für Fischertechnik, "omf" für OMF-Icons
        """
        if icon_style != self.icon_style:
            self.icon_style = icon_style
            self.module_icons = self._load_module_icons()
            logger.info(f"🔄 Switched to {icon_style} icon style")

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
            if icon_path.endswith('.svg'):
                # SVG-Icon direkt einbetten
                with open(icon_path, "r", encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()
                    # SVG-Größe anpassen (alle Icons sind 24x24)
                    if 'viewBox="0 0 24 24"' in svg_content:
                        # 24x24 Icons - direkt width/height hinzufügen
                        svg_content = svg_content.replace('<svg', f'<svg width="{icon_size}" height="{icon_size}"')
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
            if module_type.upper() == "INTERSECTION":
                # Sollte nicht mehr auftreten, da INTERSECTION jetzt echte SVG-Icons hat
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
    
    # =========================================================================
    # LOGO MANAGEMENT
    # =========================================================================
    
    def get_orbis_logo_path(self) -> Optional[str]:
        """Returns path to ORBIS company logo (SVG)"""
        logo_path = self.logos_dir / "ORBIS_logo_RGB.svg"
        if logo_path.exists():
            logger.debug(f"🏢 ORBIS logo found: {logo_path}")
            return str(logo_path)
        else:
            logger.warning(f"⚠️ ORBIS logo not found: {logo_path}")
            return None
    
    def display_orbis_logo(self, width: int = 150, use_container_width: bool = False):
        """
        Display ORBIS company logo with fallback
        
        Args:
            width: Logo width in pixels (default: 150 for prominent display)
            use_container_width: If True, logo fills container width
        """
        logo_path = self.get_orbis_logo_path()
        
        if logo_path:
            st.image(logo_path, width=width if not use_container_width else None, 
                    use_container_width=use_container_width)
            logger.debug(f"🏢 ORBIS logo displayed (width={width})")
        else:
            # Fallback: Factory emoji with caption
            st.markdown("# 🏭")
            st.caption("ORBIS Modellfabrik")
            logger.warning("⚠️ ORBIS logo fallback used (emoji)")


# Singleton-Instanz
_asset_manager_instance = None


def get_asset_manager(icon_style: str = "ic_ft") -> OMF2AssetManager:
    """Gibt die Singleton-Instanz des Asset Managers zurück
    
    Args:
        icon_style: Icon-Style ("ic_ft" für Fischertechnik, "omf" für OMF-Icons)
    """
    global _asset_manager_instance
    if _asset_manager_instance is None:
        _asset_manager_instance = OMF2AssetManager(icon_style)
        logger.info(f"📁 OMF2 Asset Manager initialized with {icon_style} icons")
    else:
        # Icon-Style ändern falls gewünscht - Singleton zurücksetzen
        if _asset_manager_instance.icon_style != icon_style:
            _asset_manager_instance = OMF2AssetManager(icon_style)
            logger.info(f"🔄 Asset Manager reinitialized with {icon_style} icons")
    return _asset_manager_instance
