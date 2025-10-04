#!/usr/bin/env python3
"""
CCU Overview - Product Catalog Subtab
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_product_catalog_subtab(ccu_gateway: CcuGateway, registry_manager):
    """Render Product Catalog Subtab
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📋 Rendering Product Catalog Subtab")
    try:
        # Use UISymbols for consistent icon usage
        st.subheader(f"{UISymbols.get_functional_icon('product_catalog')} Product Catalog")
        st.markdown("Verfügbare Produkte und deren Konfiguration")
        
        # Show Product Catalog Panel (wie in omf/ aps_overview.py)
        _show_ccu_product_catalog_panel()
        
    except Exception as e:
        logger.error(f"❌ Product Catalog Subtab rendering error: {e}")
        st.error(f"❌ Product Catalog Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_ccu_product_catalog_panel():
    """Zeigt das CCU: Produktkatalog Panel - wie in omf/ aps_overview.py"""
    logger.info("📦 Rendering CCU Product Catalog Panel")
    try:
        # Produktkatalog direkt laden (wie in omf/)
        from omf2.common.product_manager import get_omf2_product_manager
        product_manager = get_omf2_product_manager()
        catalog = product_manager.get_all_products()
        
        if not catalog:
            st.error("❌ Keine Produkte gefunden")
            return

        # 3 Spalten für die Produkte (Reihenfolge: Blau, Weiß, Rot)
        col1, col2, col3 = st.columns(3)

        # HTML-Templates importieren
        try:
            from omf2.assets.html_templates import get_product_catalog_template
            TEMPLATES_AVAILABLE = True
        except ImportError:
            TEMPLATES_AVAILABLE = False

        # BLAU (Spalte 1)
        with col1:
            if "blue" in catalog:
                product = catalog["blue"]
                if TEMPLATES_AVAILABLE:
                    html_content = get_product_catalog_template("BLUE")
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.write("🔵 **BLAU**")
                st.write(f"**Name:** {product.get('name', 'Blau')}")
                st.write(f"**Beschreibung:** {product.get('description', 'Blau')}")
                st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
                st.write(f"**Farbe:** {product.get('color', 'Blau')}")

        # WEISS (Spalte 2)
        with col2:
            if "white" in catalog:
                product = catalog["white"]
                if TEMPLATES_AVAILABLE:
                    html_content = get_product_catalog_template("WHITE")
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.write("⚪ **WEISS**")
                st.write(f"**Name:** {product.get('name', 'Weiß')}")
                st.write(f"**Beschreibung:** {product.get('description', 'Weiß')}")
                st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
                st.write(f"**Farbe:** {product.get('color', 'Weiß')}")

        # ROT (Spalte 3)
        with col3:
            if "red" in catalog:
                product = catalog["red"]
                if TEMPLATES_AVAILABLE:
                    html_content = get_product_catalog_template("RED")
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.write("🔴 **ROT**")
                st.write(f"**Name:** {product.get('name', 'Rot')}")
                st.write(f"**Beschreibung:** {product.get('description', 'Rot')}")
                st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
                st.write(f"**Farbe:** {product.get('color', 'Rot')}")

        # Einfache Produktstatistiken
        st.info(f"📊 **Produktkatalog:** {len(catalog)} Produkte verfügbar")

    except Exception as e:
        logger.error(f"❌ Fehler beim Laden des Produktkatalog Panels: {e}")
        st.error(f"❌ Fehler beim Laden des Produktkatalog Panels: {e}")
        st.info("💡 Produktkatalog Panel konnte nicht geladen werden.")
