from omf.dashboard.tools.path_constants import PROJECT_ROOT

"""
OMF Dashboard Overview - Produktkatalog
Komponente für die Anzeige des Produktkatalogs mit HTML-Templates
"""


import streamlit as st
import yaml

# Template-Import hinzufügen
try:
    from omf.dashboard.assets.html_templates import get_product_catalog_template

    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    st.error(f"❌ Templates nicht verfügbar: {e}")


def load_product_catalog():
    """Lädt den Produktkatalog über den Product Manager"""
    try:
        from omf.tools.product_manager import get_omf_product_manager
        product_manager = get_omf_product_manager()
        return product_manager.get_all_products()
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

    # Produkte aus der Registry laden (products ist bereits ein Dict)
    if not isinstance(catalog, dict):
        st.error("❌ Produktkatalog hat falsches Format")
        return

    # 3 Spalten für die Produkte
    col1, col2, col3 = st.columns(3)

    # ROT
    with col1:
        if "red" in catalog:
            product = catalog["red"]
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
        if "blue" in catalog:
            product = catalog["blue"]
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
        if "white" in catalog:
            product = catalog["white"]
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
