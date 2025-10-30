#!/usr/bin/env python3
"""
CCU Process Tab - Process Management UI Component
Wrapper Tab with Subtabs for Production Plan and Production Monitoring
"""

import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_process_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Process Tab with Subtabs

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("⚙️ Rendering CCU Process Tab")
    try:
        # Initialize CCU Gateway if not provided
        if not ccu_gateway:
            if "ccu_gateway" not in st.session_state:
                # Use Gateway Factory to create CCU Gateway with MQTT Client
                from omf2.factory.gateway_factory import get_gateway_factory

                gateway_factory = get_gateway_factory()
                st.session_state["ccu_gateway"] = gateway_factory.get_ccu_gateway()
            ccu_gateway = st.session_state["ccu_gateway"]

        # Initialize Registry Manager if not provided
        if not registry_manager:
            from omf2.registry.manager.registry_manager import get_registry_manager

            registry_manager = get_registry_manager()

        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # Use heading SVG for Process tab (32px)
        try:
            process_icon = get_svg_inline("PROCESS", size_px=32) or ""
            st.markdown(
                f"<h2 style='margin-bottom: 0.25rem; display:flex; align-items:center; gap:8px;'>{process_icon} {i18n.translate('tabs.ccu_process')}</h2>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.header(f"{UISymbols.get_tab_icon('ccu_process')} {i18n.translate('tabs.ccu_process')}")
        st.markdown(i18n.t("ccu_process.subtitle"))

        # Create subtabs
        subtab_labels = [
            i18n.t("ccu_process.subtabs.production_plan"),
            i18n.t("ccu_process.subtabs.production_monitoring"),
        ]

        subtabs = st.tabs(subtab_labels)

        # Render subtab content
        with subtabs[0]:
            from omf2.ui.ccu.ccu_process.ccu_production_plan_subtab import render_ccu_production_plan_subtab

            render_ccu_production_plan_subtab()

        with subtabs[1]:
            from omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab import render_ccu_production_monitoring_subtab

            render_ccu_production_monitoring_subtab()

    except Exception as e:
        logger.error(f"❌ CCU Process Tab rendering error: {e}")
        i18n = st.session_state.get("i18n_manager")
        if i18n:
            error_msg = i18n.t("ccu_process.error.tab_failed").format(error=e)
            st.error(f"❌ {error_msg}")
            st.info(f"💡 {i18n.t('ccu_process.under_development')}")
        else:
            st.error(f"❌ CCU Process Tab failed: {e}")
            st.info("💡 This component is currently under development.")
