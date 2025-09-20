"""
OMF Dashboard Asset Manager
Verwaltet Module-Icons und HTML-Templates für Dashboard-Visualisierung
Version: 3.3.0
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

from .html_templates import (
    get_status_badge_template,
    get_workpiece_box_template,
)


class DashboardAssetManager:
    """Verwaltet Dashboard-Assets (Icons, Templates) für konsistente Visualisierung"""

    def __init__(self):
        """Initialisiert den Asset Manager"""
        self.assets_dir = Path(__file__).parent
        self.module_icons = self._load_module_icons()
        self.product_templates = self._load_product_templates()

    def _load_module_icons(self) -> Dict[str, str]:
        """Lädt verfügbare Module-Icons"""
        icons = {}

        # Module-Icon-Mapping (allLowercase Variante)
        icon_mapping = {
            "HBW": "hbw_icon.png",
            "DRILL": "drill_icon.png",
            "MILL": "mill_icon.png",
            "AIQS": "aiqs_icon.png",
            "DPS": "dps_icon.png",
            "CHRG": "chrg_icon.png",  # Korrigiert: CHRG statt CHRG0
            "FTS": "fts_icon.jpeg",
            "TXT": "txt_icon.png",
            "RPI": "rpi_icon.png",
            "MOSQUITTO": "mosquitto_icon.png",
            "ROUTER": "router_icon.png",
            "MACHINE": "machine_icon.png",
            "PLATINE": "platine_icon.png",
            "PC_TABLET": "pc-tablet_icon.png",
        }

        for module_name, icon_file in icon_mapping.items():
            icon_path = self.assets_dir / icon_file
            if icon_path.exists():
                icons[module_name] = str(icon_path)
            else:
                # Fallback zu Standard-Icon
                icons[module_name] = str(self.assets_dir / "machine_icon.png")

        return icons

    def _load_product_templates(self) -> Dict[str, Dict[str, Any]]:
        """Lädt Produkt-Templates für BLAU, WEISS, ROT"""
        return {
            "BLUE": {
                "name": "Produkt Blau",
                "color": "#0066ff",
                "description": "Werkstück, das gebohrt, gefräst und qualitätsgesichert wird.",
                "manufacturing_route": ["DRILL", "MILL", "AIQS"],
                "estimated_time": 60,
            },
            "WHITE": {
                "name": "Produkt Weiß",
                "color": "#e0e0e0",
                "description": "Werkstück, das gebohrt und qualitätsgesichert wird.",
                "manufacturing_route": ["DRILL", "AIQS"],
                "estimated_time": 40,
            },
            "RED": {
                "name": "Produkt Rot",
                "color": "#ff0000",
                "description": "Werkstück, das gefräst und qualitätsgesichert wird.",
                "manufacturing_route": ["MILL", "AIQS"],
                "estimated_time": 45,
            },
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
            st.markdown(f"🔧 {module_name}")

    def get_product_template(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Gibt das Produkt-Template zurück"""
        return self.product_templates.get(product_id.upper())

    def display_product_box(self, product_id: str, count: int = 0, available: bool = True) -> None:
        """Zeigt eine Produkt-Box mit HTML-Template an"""
        template = self.get_product_template(product_id)
        if template:
            html = get_workpiece_box_template(product_id, count, available)
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning(f"Produkt-Template für {product_id} nicht gefunden")

    def display_shopfloor_module(self, module_name: str, position: tuple, status: str = "READY") -> None:
        """Zeigt ein Modul im Shopfloor-Layout mit Icon und Status"""
        col1, col2 = st.columns([1, 3])

        with col1:
            self.display_module_icon(module_name, width=40)

        with col2:
            st.write(f"**{module_name}**")
            st.write(f"Position: {position}")
            status_badge = get_status_badge_template(status, self._get_status_type(status))
            st.markdown(status_badge, unsafe_allow_html=True)

    def display_route_visualization(
        self, route_id: str, from_module: str, to_module: str, via_modules: list = None
    ) -> None:
        """Zeigt eine Route-Visualisierung mit Modul-Icons"""
        st.write(f"**Route:** {route_id}")

        # Route-Pfad anzeigen
        route_parts = [from_module]
        if via_modules:
            route_parts.extend(via_modules)
        route_parts.append(to_module)

        # Icons in einer Reihe anzeigen
        cols = st.columns(len(route_parts))
        for i, module in enumerate(route_parts):
            with cols[i]:
                if i == 0:
                    self.display_module_icon(module, width=40, caption="Start")
                elif i == len(route_parts) - 1:
                    self.display_module_icon(module, width=40, caption="Ziel")
                else:
                    self.display_module_icon(module, width=40, caption="Via")

                if i < len(route_parts) - 1:
                    st.markdown("→")

    def display_product_catalog(self, products: Dict[str, Any]) -> None:
        """Zeigt den Produktkatalog mit HTML-Templates an"""
        st.subheader("📦 Produktkatalog")

        for product_id, _product_info in products.items():
            template = self.get_product_template(product_id)
            if template:
                with st.expander(f"{template['name']} ({product_id})", expanded=False):
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        self.display_product_box(product_id, count=0, available=True)

                    with col2:
                        st.write(f"**Beschreibung:** {template['description']}")
                        st.write(f"**Fertigungsroute:** {' → '.join(template['manufacturing_route'])}")
                        st.write(f"**Geschätzte Zeit:** {template['estimated_time']} Sekunden")

    def display_shopfloor_grid(self, layout_config: Dict[str, Any]) -> None:
        """Zeigt das Shopfloor-Grid mit Modul-Icons"""
        st.subheader("🗺️ Shopfloor-Layout")

        modules = layout_config.get("modules", [])
        grid_rows = layout_config.get("grid", {}).get("rows", 3)
        grid_cols = layout_config.get("grid", {}).get("columns", 4)

        # Erstelle Grid-Darstellung
        for row in range(grid_rows):
            cols = st.columns(grid_cols)
            for col in range(grid_cols):
                with cols[col]:
                    # Finde Modul an dieser Position
                    module = next((m for m in modules if m.get("position") == [row, col]), None)

                    if module:
                        module_type = module.get("type", "UNKNOWN")
                        module_id = module.get("id", "UNKNOWN")
                        module_name = module.get("name", module_id)

                        if module_type == "MODULE":
                            self.display_module_icon(module_id, width=60, caption=module_name)
                        elif module_type == "INTERSECTION":
                            st.markdown(f"➕ {module_name}")
                        else:
                            st.markdown("⬜")
                    else:
                        st.markdown("⬜")

    def _get_status_type(self, status: str) -> str:
        """Gibt den Status-Typ für Badge-Farben zurück"""
        status_mapping = {
            "READY": "success",
            "BUSY": "warning",
            "BLOCKED": "error",
            "OFFLINE": "error",
            "PENDING": "info",
            "COMPLETED": "success",
            "WAITING": "warning",
        }
        return status_mapping.get(status, "info")

    def get_available_modules(self) -> list:
        """Gibt alle verfügbaren Module mit Icons zurück"""
        return list(self.module_icons.keys())

    def get_available_products(self) -> list:
        """Gibt alle verfügbaren Produkte zurück"""
        return list(self.product_templates.keys())


# Singleton-Instanz
_asset_manager = None


def get_asset_manager() -> DashboardAssetManager:
    """Gibt die Singleton-Instanz des Asset Managers zurück"""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = DashboardAssetManager()
    return _asset_manager
