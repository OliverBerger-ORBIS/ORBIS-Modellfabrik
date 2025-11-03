#!/usr/bin/env python3
"""
Generic Steering Tab - Modular Architecture with Factory and Topic Steering
Gateway-Pattern konform: Nutzt AdminGateway aus Gateway-Factory
"""

import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_generic_steering_tab():
    """Render Generic Steering Tab with Factory and Topic Steering Subtabs"""
    logger.info("🎛️ Rendering Generic Steering Tab")

    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # Get SVG icon for Generic Steering heading
        try:
            steering_icon = get_asset_manager().get_asset_inline("GENERIC_STEERING", size_px=32) or ""
            st.markdown(
                f"<h1 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{steering_icon} {i18n.translate('tabs.generic_steering')}</h1>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.title(f"{UISymbols.get_tab_icon('generic_steering')} {i18n.translate('tabs.generic_steering')}")
        st.markdown(f"**{i18n.t('admin.generic_steering.subtitle')}**")

        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} {i18n.t('admin.generic_steering.gateway_not_available')}")
            return

        # Get Registry Manager from session state
        registry_manager = st.session_state.get("registry_manager")

        # Connection status shown in sidebar only

        # Registry Manager Status
        if registry_manager:
            stats = registry_manager.get_registry_stats()
            total_entities = (
                stats["topics_count"]
                + stats["schemas_count"]
                + stats["mqtt_clients_count"]
                + stats["workpieces_count"]
                + stats["modules_count"]
                + stats["stations_count"]
                + stats["txt_controllers_count"]
            )
            registry_msg = i18n.t("admin.generic_steering.registry_entities").format(count=total_entities)
            st.info(f"{UISymbols.get_status_icon('history')} **{registry_msg}**")
        else:
            st.warning(
                f"{UISymbols.get_status_icon('warning')} **{i18n.t('admin.generic_steering.registry_not_available')}**"
            )

        # Tabs for different steering modes using centralized TAB_ICONS
        tab1, tab2 = st.tabs(
            [
                f"{UISymbols.get_tab_icon('factory_steering')} Factory Steering",
                f"{UISymbols.get_tab_icon('topic_steering')} Topic Steering",
            ]
        )

        with tab1:
            _render_factory_steering_tab(admin_gateway, registry_manager)

        with tab2:
            _render_topic_steering_tab(admin_gateway, registry_manager)

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Generic Steering Tab error: {e}")
        i18n = st.session_state.get("i18n_manager")
        error_msg = (
            i18n.t("admin.generic_steering.tab_failed").format(error=e) if i18n else f"Generic Steering failed: {e}"
        )
        st.error(f"{UISymbols.get_status_icon('error')} {error_msg}")


def _render_factory_steering_tab(admin_gateway, registry_manager):
    """Render Factory Steering Tab"""
    from omf2.ui.admin.generic_steering.factory_steering_subtab import render_factory_steering_subtab

    render_factory_steering_subtab(admin_gateway, registry_manager)


def _render_topic_steering_tab(admin_gateway, registry_manager):
    """Render Topic Steering Tab"""
    from omf2.ui.admin.generic_steering.topic_steering_subtab import render_topic_steering_subtab

    render_topic_steering_subtab(admin_gateway, registry_manager)
