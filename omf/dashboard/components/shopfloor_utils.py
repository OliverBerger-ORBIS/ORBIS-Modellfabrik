from omf.dashboard.tools.path_constants import PROJECT_ROOT

"""
OMF Dashboard Shopfloor Utils - Gemeinsame Shopfloor-Funktionen
Gemeinsame Utility-Funktionen für alle Shopfloor-Komponenten
"""

from typing import Any, Dict, List, Optional

import streamlit as st
import yaml


def load_shopfloor_config() -> Dict[str, Any]:
    """Lädt die Shopfloor-Konfiguration aus YAML-Dateien"""
    try:
        config_dir = PROJECT_ROOT / "config" / "shopfloor"

        # Layout-Konfiguration laden
        layout_file = config_dir / "layout.yml"
        if layout_file.exists():
            with open(layout_file, encoding="utf-8") as f:
                layout_config = yaml.safe_load(f)
        else:
            layout_config = {}

        # Routen-Konfiguration laden
        routes_file = config_dir / "routes.yml"
        if routes_file.exists():
            with open(routes_file, encoding="utf-8") as f:
                routes_config = yaml.safe_load(f)
        else:
            routes_config = {}

        return {"layout": layout_config, "routes": routes_config}
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Shopfloor-Konfiguration: {e}")
        return {"layout": {}, "routes": {}}


def get_shopfloor_metadata() -> Dict[str, Any]:
    """Gibt Shopfloor-Metadaten zurück"""
    config = load_shopfloor_config()

    layout_meta = config.get("layout", {}).get("metadata", {})
    routes_meta = config.get("routes", {}).get("metadata", {})

    return {
        "version": layout_meta.get("version", "3.0.0"),
        "grid_size": layout_meta.get("grid_size", "4x3"),
        "total_positions": layout_meta.get("total_positions", 12),
        "fts_serial": routes_meta.get("fts_serial", "5iO4"),
        "last_updated": layout_meta.get("last_updated", "2025-01-19"),
    }


def get_module_positions() -> List[Dict[str, Any]]:
    """Gibt alle Modul-Positionen zurück"""
    config = load_shopfloor_config()
    return config.get("layout", {}).get("positions", [])


def get_intersections() -> List[Dict[str, Any]]:
    """Gibt alle Intersection-Positionen zurück"""
    config = load_shopfloor_config()
    return config.get("layout", {}).get("intersections", [])


def get_enabled_modules() -> List[str]:
    """Gibt die aktivierten Module zurück"""
    config = load_shopfloor_config()
    return config.get("layout", {}).get("enabled_modules", [])


def get_fts_routes() -> List[Dict[str, Any]]:
    """Gibt alle FTS-Routen zurück"""
    config = load_shopfloor_config()
    return config.get("routes", {}).get("routes", [])


def get_product_routes() -> Dict[str, Any]:
    """Gibt alle Produkt-Routen zurück"""
    config = load_shopfloor_config()
    return config.get("routes", {}).get("products", {})


def find_route_between_modules(start_module: str, end_module: str) -> Optional[Dict[str, Any]]:
    """Findet eine Route zwischen zwei Modulen"""
    fts_routes = get_fts_routes()

    # Einfache Route-Suche (kann erweitert werden)
    for route in fts_routes:
        if route.get("from") == start_module and route.get("to") == end_module:
            return route

    return None


def get_shopfloor_statistics() -> Dict[str, Any]:
    """Gibt Shopfloor-Statistiken zurück"""
    try:
        positions = get_module_positions()
        intersections = get_intersections()
        enabled_modules = get_enabled_modules()
        fts_routes = get_fts_routes()
        product_routes = get_product_routes()

        return {
            "modules": {
                "total": len(positions),
                "enabled": len(enabled_modules),
                "disabled": len(positions) - len(enabled_modules),
            },
            "intersections": len(intersections),
            "routes": {"fts": len(fts_routes), "products": len(product_routes)},
        }
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Shopfloor-Statistiken: {e}")
        return {
            "modules": {"total": 0, "enabled": 0, "disabled": 0},
            "intersections": 0,
            "routes": {"fts": 0, "products": 0},
        }
