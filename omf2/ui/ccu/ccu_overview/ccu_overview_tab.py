#!/usr/bin/env python3
"""
CCU Overview Tab - CCU Dashboard UI Component with Subtabs
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_overview_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Overview Tab with Subtabs

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("🏭 Rendering CCU Overview Tab")
    try:
        # Gateway-Pattern: Get CcuGateway from Factory (EXACT like Admin)
        from omf2.factory.gateway_factory import get_ccu_gateway

        ccu_gateway = get_ccu_gateway()
        if not ccu_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway not available")
            return

        # Initialize Registry Manager if not provided
        if not registry_manager:
            from omf2.registry.manager.registry_manager import get_registry_manager

            registry_manager = get_registry_manager()

        # Initialize Asset Manager (Singleton)
        from omf2.assets.asset_manager import get_asset_manager

        asset_manager = get_asset_manager()

        # i18n Manager aus Session State holen (zentrale Instanz)
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # Heading with SVG icon for Overview
        try:
            from omf2.assets.heading_icons import get_svg_inline

            overview_icon = get_svg_inline("DASHBOARD", size_px=32) or ""
            st.markdown(
                f"<h2 style='margin-bottom: 0.25rem; display:flex; align-items:center; gap:8px;'>{overview_icon} {i18n.t('tabs.ccu_dashboard')}</h2>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.header(f"{UISymbols.get_tab_icon('ccu_overview')} {i18n.t('tabs.ccu_dashboard')}")
        st.markdown(i18n.t("ccu_overview.subtitle"))

        # Create subtabs (i18n: Alle Tab-Titel übersetzt, Icons bleiben universell)
        tab1, tab2, tab3 = st.tabs(
            [
                f"{UISymbols.get_tab_icon('product_catalog')} {i18n.t('ccu_overview.tabs.product_catalog')}",
                f"{UISymbols.get_tab_icon('inventory')} {i18n.t('ccu_overview.tabs.inventory')}",
                f"{UISymbols.get_tab_icon('sensor_data')} {i18n.t('ccu_overview.tabs.sensor_data')}",
            ]
        )

        with tab1:
            from omf2.ui.ccu.ccu_overview.product_catalog_subtab import render_product_catalog_subtab

            render_product_catalog_subtab(ccu_gateway, registry_manager, asset_manager)

        with tab2:
            from omf2.ui.ccu.ccu_overview.inventory_subtab import render_inventory_subtab

            render_inventory_subtab(ccu_gateway, registry_manager, asset_manager)

        with tab3:
            from omf2.ui.ccu.ccu_overview.sensor_data_subtab import render_sensor_data_subtab

            render_sensor_data_subtab(ccu_gateway, registry_manager, asset_manager)

    except Exception as e:
        logger.error(f"❌ CCU Overview Tab rendering error: {e}")
        st.error(f"❌ CCU Overview Tab failed: {e}")
        i18n = st.session_state.get("i18n_manager")
        if i18n:
            st.info(f"💡 {i18n.t('common.status.under_development')}")
