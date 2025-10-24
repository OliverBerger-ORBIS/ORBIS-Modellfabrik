#!/usr/bin/env python3
"""
CCU Overview - Product Catalog Subtab
"""

import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.common.product_rendering import render_product_svg_container

logger = get_logger(__name__)


def render_product_catalog_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """Render Product Catalog Subtab

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
        asset_manager: AssetManager Instanz (Singleton)
    """
    logger.info("📋 Rendering Product Catalog Subtab")

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    try:
        # Use UISymbols for consistent icon usage
        st.subheader(
            f"{UISymbols.get_functional_icon('product_catalog')} {i18n.t('ccu_overview.product_catalog.title')}"
        )
        st.markdown(i18n.t("ccu_overview.product_catalog.subtitle"))

        # Show Product Catalog Panel (wie in omf/ aps_overview.py)
        _show_ccu_product_catalog_panel(asset_manager)

    except Exception as e:
        logger.error(f"❌ Product Catalog Subtab rendering error: {e}")
        st.error(f"❌ Product Catalog Subtab failed: {e}")
        i18n_fallback = st.session_state.get("i18n_manager")
        if i18n_fallback:
            st.info(f"💡 {i18n_fallback.t('common.status.under_development')}")


def _show_ccu_product_catalog_panel(asset_manager):
    """Zeigt das CCU: Produktkatalog Panel - wie in omf/ aps_overview.py"""
    logger.info("📦 Rendering CCU Product Catalog Panel")

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    try:
        # Produktkatalog direkt laden (wie in omf/)
        from omf2.common.product_manager import get_omf2_product_manager

        product_manager = get_omf2_product_manager()
        catalog = product_manager.get_all_products()

        if not catalog:
            st.error(f"❌ {i18n.t('ccu_overview.product_catalog.no_products')}")
            return

        # Asset Manager wird als Parameter übergeben (Singleton)

        # 3 Spalten für die Produkte
        col1, col2, col3 = st.columns(3)

        # Schleife über die Produkte in der Registry
        product_order = ["blue", "white", "red"]  # Definierte Reihenfolge
        columns = [col1, col2, col3]

        for i, product_id in enumerate(product_order):
            if product_id in catalog and i < 3:
                product = catalog[product_id]
                color_name = product.get("name", product_id.capitalize())
                color_emoji = product.get(
                    "icon", "🔵" if product_id == "blue" else "⚪" if product_id == "white" else "🔴"
                )

                with columns[i]:
                    st.markdown(f"#### {color_emoji} **{color_name.upper()}**")

                    # 3DIM SVG - STANDARDIZED 200x200 CONTAINER
                    st.markdown("**3DIM SVG:**")
                    svg_content = asset_manager.get_workpiece_svg(product_id.upper(), "3dim")
                    if svg_content:
                        st.markdown(
                            render_product_svg_container(svg_content, scale=1.0),
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ {product_id.lower()}_3dim.svg nicht gefunden!")

                    # PRODUCT SVG - STANDARDIZED 200x200 CONTAINER
                    st.markdown("**Product SVG:**")
                    svg_content = asset_manager.get_workpiece_svg(product_id.upper(), "product")
                    if svg_content:
                        st.markdown(
                            render_product_svg_container(svg_content, scale=1.0),
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ {product_id.lower()}_product.svg nicht gefunden!")

                    # Produktdaten aus Registry
                    st.markdown("**Produktdaten:**")
                    name_label = i18n.t("ccu_overview.product_catalog.name")
                    desc_label = i18n.t("ccu_overview.product_catalog.description")
                    material_label = i18n.t("ccu_overview.product_catalog.material")
                    st.write(f"**{name_label}:** {product.get('name', 'Kein Name')}")
                    st.write(f"**{material_label}:** {product.get('material', 'Kein Material')}")
                    st.write(f"**{desc_label}:** {product.get('description', 'Keine Beschreibung')}")

        # Einfache Produktstatistiken
        summary_text = i18n.t("ccu_overview.product_catalog.summary")
        products_available_text = i18n.t("ccu_overview.product_catalog.products_available")
        st.info(f"📊 **{summary_text}:** {len(catalog)} {products_available_text}")

    except Exception as e:
        logger.error(f"❌ Fehler beim Laden des Produktkatalog Panels: {e}")
        st.error(f"❌ Fehler beim Laden des Produktkatalog Panels: {e}")
        error_loading_text = i18n.t("ccu_overview.product_catalog.error_loading")
        st.info(f"💡 {error_loading_text}")
