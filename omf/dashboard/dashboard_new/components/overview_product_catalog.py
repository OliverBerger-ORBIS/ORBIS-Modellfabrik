"""
OMF Dashboard Overview - Produktkatalog
Komponente für die Anzeige des Produktkatalogs mit HTML-Templates
"""

from pathlib import Path

import streamlit as st
import yaml

# Template-Import hinzufügen
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "assets"))  # Nicht mehr nötig nach pip install -e .
try:
    from src_orbis.omf.dashboard.assets.html_templates import get_product_catalog_template

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


def show_overview_product_catalog():
    """Hauptfunktion für den Produktkatalog"""
    st.header("📦 Produktkatalog der ORBIS Modellfabrik")

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
            # Produktdetails anzeigen
            st.write(f"**Name:** {product.get('name', 'Rot')}")
            st.write(f"**Beschreibung:** {product.get('description', 'Rot')}")
            st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
            st.write(f"**Farbe:** {product.get('color', 'Rot')}")
            st.write(f"**Größe:** {product.get('size', 'Standard')}")

    # BLAU
    with col2:
        if "blue" in products:
            product = products["blue"]
            if TEMPLATES_AVAILABLE:
                html_content = get_product_catalog_template("BLUE")
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.write("🔵 BLAU")
            # Produktdetails anzeigen
            st.write(f"**Name:** {product.get('name', 'Blau')}")
            st.write(f"**Beschreibung:** {product.get('description', 'Blau')}")
            st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
            st.write(f"**Farbe:** {product.get('color', 'Blau')}")
            st.write(f"**Größe:** {product.get('size', 'Standard')}")

    # WEISS
    with col3:
        if "white" in products:
            product = products["white"]
            if TEMPLATES_AVAILABLE:
                html_content = get_product_catalog_template("WHITE")
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.write("⚪ WEISS")
            # Produktdetails anzeigen
            st.write(f"**Name:** {product.get('name', 'Weiß')}")
            st.write(f"**Beschreibung:** {product.get('description', 'Weiß')}")
            st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
            st.write(f"**Farbe:** {product.get('color', 'Weiß')}")
            st.write(f"**Größe:** {product.get('size', 'Standard')}")
