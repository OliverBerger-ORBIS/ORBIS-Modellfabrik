"""
OMF Dashboard Product Catalog - Produktkatalog-Visualisierung
Zeigt Produkte (BLAU, WEISS, ROT) mit HTML-Templates und Icons
Version: 3.3.0
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
import yaml

from ..assets.asset_manager import get_asset_manager

# Pfad zur Produktkatalog-Konfiguration
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "config" / "products" / "product_catalog.yml"


def load_product_catalog_config():
    """Lädt die Produktkatalog-Konfiguration aus der YAML-Datei."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return None


def show_product_catalog():
    """Zeigt den Produktkatalog mit visuellen Elementen"""
    st.subheader("📦 Produktkatalog")

    config = load_product_catalog_config()
    if not config:
        st.error("Produktkatalog-Konfiguration konnte nicht geladen werden.")
        return

    asset_manager = get_asset_manager()

    # Metadaten anzeigen
    show_catalog_metadata(config)

    st.divider()

    # Produkte anzeigen
    show_products(config, asset_manager)

    st.divider()

    # Produkt-Statistiken
    show_product_statistics(config)


def show_catalog_metadata(config: Dict[str, Any]):
    """Zeigt Metadaten des Produktkatalogs"""
    metadata = config.get("metadata", {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Version", metadata.get("version", "3.3.0"))
    with col2:
        st.metric("Produkte", len(config.get("products", {})))
    with col3:
        st.metric("Letzte Aktualisierung", metadata.get("last_updated", "Unbekannt"))
    with col4:
        st.metric("Status", "✅ Aktiv" if metadata.get("enabled", True) else "❌ Inaktiv")


def show_products(config: Dict[str, Any], asset_manager):
    """Zeigt alle Produkte mit visuellen Elementen"""
    st.subheader("🎨 Produkte")

    products = config.get("products", {})

    if not products:
        st.warning("Keine Produkte im Katalog gefunden.")
        return

    # Produkte in Spalten anzeigen
    product_cols = st.columns(len(products))

    for i, (product_id, product_info) in enumerate(products.items()):
        with product_cols[i]:
            show_single_product(product_id, product_info, asset_manager)


def show_single_product(product_id: str, product_info: Dict[str, Any], asset_manager):
    """Zeigt ein einzelnes Produkt mit visuellen Elementen"""
    # Produkt-Box mit HTML-Template
    asset_manager.display_product_box(
        product_id, count=0, available=product_info.get("enabled", True)  # TODO: Echte Bestandszahlen aus DB
    )

    # Produkt-Details
    with st.expander(f"Details: {product_info.get('name', product_id)}", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**ID:** {product_id}")
            st.write(f"**Name:** {product_info.get('name', 'Unbekannt')}")
            st.write(f"**Farbe:** {product_info.get('color', 'Unbekannt')}")
            st.write(f"**Status:** {'✅ Aktiv' if product_info.get('enabled', True) else '❌ Inaktiv'}")

        with col2:
            st.write(f"**Geschätzte Zeit:** {product_info.get('estimated_time', 0)} Sekunden")
            st.write(f"**Priorität:** {product_info.get('priority', 'NORMAL')}")

            # Fertigungsroute anzeigen
            route = product_info.get("manufacturing_route", [])
            if route:
                st.write("**Fertigungsroute:**")
                for i, step in enumerate(route):
                    st.write(f"{i+1}. {step}")
            else:
                st.write("**Keine Fertigungsroute definiert**")

        # Beschreibung
        description = product_info.get("description", "Keine Beschreibung verfügbar")
        st.write(f"**Beschreibung:** {description}")


def show_product_statistics(config: Dict[str, Any]):
    """Zeigt Produkt-Statistiken"""
    st.subheader("📊 Produkt-Statistiken")

    products = config.get("products", {})

    if not products:
        return

    # Statistiken berechnen
    total_products = len(products)
    active_products = sum(1 for p in products.values() if p.get("enabled", True))
    inactive_products = total_products - active_products

    # Durchschnittliche Fertigungszeit
    times = [p.get("estimated_time", 0) for p in products.values() if p.get("estimated_time")]
    avg_time = sum(times) / len(times) if times else 0

    # Prioritäten
    priorities = {}
    for p in products.values():
        priority = p.get("priority", "NORMAL")
        priorities[priority] = priorities.get(priority, 0) + 1

    # Anzeige
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Gesamtprodukte", total_products)
        st.metric("Aktive Produkte", active_products)

    with col2:
        st.metric("Inaktive Produkte", inactive_products)
        st.metric("Durchschn. Zeit", f"{avg_time:.1f}s")

    with col3:
        st.write("**Prioritäten:**")
        for priority, count in priorities.items():
            st.write(f"- {priority}: {count}")

    with col4:
        st.write("**Fertigungsrouten:**")
        route_counts = {}
        for p in products.values():
            route = tuple(p.get("manufacturing_route", []))
            route_counts[route] = route_counts.get(route, 0) + 1

        for route, count in route_counts.items():
            if route:
                route_str = " → ".join(route)
                st.write(f"- {route_str}: {count}")


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Gibt ein Produkt anhand der ID zurück"""
    config = load_product_catalog_config()
    if config:
        return config.get("products", {}).get(product_id.upper())
    return None


def get_all_products() -> Dict[str, Any]:
    """Gibt alle Produkte zurück"""
    config = load_product_catalog_config()
    if config:
        return config.get("products", {})
    return {}


def get_active_products() -> Dict[str, Any]:
    """Gibt alle aktiven Produkte zurück"""
    products = get_all_products()
    return {k: v for k, v in products.items() if v.get("enabled", True)}


def get_products_by_route(route_step: str) -> List[str]:
    """Gibt alle Produkte zurück, die einen bestimmten Fertigungsschritt enthalten"""
    products = get_all_products()
    matching_products = []

    for product_id, product_info in products.items():
        route = product_info.get("manufacturing_route", [])
        if route_step.upper() in [step.upper() for step in route]:
            matching_products.append(product_id)

    return matching_products


def get_manufacturing_routes() -> Dict[str, List[str]]:
    """Gibt alle Fertigungsrouten zurück"""
    products = get_all_products()
    routes = {}

    for product_id, product_info in products.items():
        route = product_info.get("manufacturing_route", [])
        if route:
            routes[product_id] = route

    return routes


def show_product_route_visualization():
    """Zeigt eine visuelle Darstellung der Fertigungsrouten"""
    st.subheader("🔄 Fertigungsrouten-Visualisierung")

    routes = get_manufacturing_routes()
    asset_manager = get_asset_manager()

    if not routes:
        st.warning("Keine Fertigungsrouten gefunden.")
        return

    for product_id, route in routes.items():
        with st.expander(f"Route für {product_id}", expanded=False):
            st.write(f"**Produkt:** {product_id}")

            # Route mit Icons visualisieren
            if len(route) > 1:
                cols = st.columns(len(route))
                for i, step in enumerate(route):
                    with cols[i]:
                        if i == 0:
                            asset_manager.display_module_icon(step, width=50, caption="Start")
                        elif i == len(route) - 1:
                            asset_manager.display_module_icon(step, width=50, caption="Ende")
                        else:
                            asset_manager.display_module_icon(step, width=50, caption="Schritt")

                        if i < len(route) - 1:
                            st.markdown("→")
            else:
                st.write(f"**Einzelschritt:** {route[0] if route else 'Keine Route'}")


def show_product_comparison():
    """Zeigt einen Vergleich der Produkte"""
    st.subheader("⚖️ Produktvergleich")

    products = get_all_products()

    if len(products) < 2:
        st.info("Mindestens 2 Produkte erforderlich für Vergleich.")
        return

    # Vergleichstabelle
    comparison_data = []
    for product_id, product_info in products.items():
        comparison_data.append(
            {
                "Produkt": product_id,
                "Name": product_info.get("name", "Unbekannt"),
                "Farbe": product_info.get("color", "Unbekannt"),
                "Zeit (s)": product_info.get("estimated_time", 0),
                "Priorität": product_info.get("priority", "NORMAL"),
                "Schritte": len(product_info.get("manufacturing_route", [])),
                "Status": "✅ Aktiv" if product_info.get("enabled", True) else "❌ Inaktiv",
            }
        )

    st.dataframe(comparison_data, use_container_width=True)
