"""
OMF Dashboard Production Order - Produktplanung
Komponente für die Planung von Fertigungsaufträgen aus dem Produktkatalog
"""

from pathlib import Path

import streamlit as st
import yaml

# Template-Import hinzufügen
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "assets"))  # Nicht mehr nötig nach pip install -e .
try:
    from omf.dashboard.assets.html_templates import get_product_catalog_template

    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    st.error(f"❌ Templates nicht verfügbar: {e}")


def load_product_catalog():
    """Lädt den Produktkatalog aus der YAML-Datei"""
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "omf" / "config" / "products" / "product_catalog.yml"
        with open(config_path, encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Produktkatalogs: {e}")
        return None


def get_module_icon(module_name):
    """Get module icon from module name"""
    icons = {"HBW": "🏬", "DRILL": "🔩", "MILL": "⚙️", "AIQS": "🤖", "DPS": "📦", "FTS": "🚗"}
    return icons.get(module_name.upper(), "❓")


def show_manufacturing_flow(product_name, manufacturing_steps):
    """Zeigt den Fertigungsablauf für ein Produkt"""
    st.write(f"**Fertigungsablauf für {product_name}:**")

    # 1. Box: HBW (Anlieferung)
    with st.container():
        st.markdown(
            """
        <div style="border: 2px solid #007bff; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f8f9fa;">
            <h4 style="margin: 0; color: #007bff;">📥 Anlieferung</h4>
            <p style="margin: 5px 0; font-size: 18px;">🏬 HBW</p>
            <p style="margin: 0; color: #666;">High-Bay Warehouse</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Manufacturing Steps in Boxen
    for step in manufacturing_steps:
        with st.container():
            st.markdown(
                f"""
            <div style="border: 2px solid #28a745; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f8f9fa;">
                <h4 style="margin: 0; color: #28a745;">Step {step['step']}</h4>
                <p style="margin: 5px 0; font-size: 18px;">{get_module_icon(step['module'])} {step['module']}</p>
                <p style="margin: 0; color: #666;">{step['description']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Letzte Box: DPS (Abgabe)
    with st.container():
        st.markdown(
            """
        <div style="border: 2px solid #dc3545; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f8f9fa;">
            <h4 style="margin: 0; color: #dc3545;">📤 Abgabe</h4>
            <p style="margin: 5px 0; font-size: 18px;">📦 DPS</p>
            <p style="margin: 0; color: #666;">Delivery and Pickup Station</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


def show_production_order_production_planning():
    """Hauptfunktion für die Produktplanung"""
    st.header("📋 Produktplanung")
    st.markdown("Planung von Fertigungsaufträgen aus dem Produktkatalog")

    # Produktkatalog laden
    catalog = load_product_catalog()
    if not catalog:
        return

    # 3 Spalten für die Produkte
    col1, col2, col3 = st.columns(3)

    # Produkte aus der Konfiguration laden
    products = catalog.get("products", {})

    # ROT
    with col1:
        if "red" in products:
            product = products["red"]
            if TEMPLATES_AVAILABLE:
                html_content = get_product_catalog_template("RED")
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.write("🔴 ROT")

            # Fertigungsablauf anzeigen
            show_manufacturing_flow("ROT", product.get("manufacturing_steps", []))

    # BLAU
    with col2:
        if "blue" in products:
            product = products["blue"]
            if TEMPLATES_AVAILABLE:
                html_content = get_product_catalog_template("BLUE")
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.write("🔵 BLAU")

            # Fertigungsablauf anzeigen
            show_manufacturing_flow("BLAU", product.get("manufacturing_steps", []))

    # WEISS
    with col3:
        if "white" in products:
            product = products["white"]
            if TEMPLATES_AVAILABLE:
                html_content = get_product_catalog_template("WHITE")
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.write("⚪ WEISS")

            # Fertigungsablauf anzeigen
            show_manufacturing_flow("WEISS", product.get("manufacturing_steps", []))
