#!/usr/bin/env python3
"""
Message Center Tab - Standard konform mit 3 Subtabs
Gateway-Pattern konform: Nutzt AdminGateway aus Gateway-Factory
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols
from omf2.common.i18n import I18nManager

logger = get_logger(__name__)


def render_message_center_tab():
    """Render Message Center Tab - Standard konform"""
    logger.info("📧 Rendering Message Center Tab")
    
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return
        
        # Header
        st.subheader(f"{UISymbols.get_tab_icon('message_center')} {i18n.translate('tabs.message_center')}")
        st.markdown(f"**{i18n.t('admin.message_center.subtitle')}**")
        
        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} {i18n.t('admin.message_center.gateway_not_available')}")
            return
        
        # Connection status shown in sidebar only
        
        # Tabs for different functions - Standard konform using UISymbols
        tab1, tab2, tab3 = st.tabs([
            f"{UISymbols.get_functional_icon('dashboard')} Message Monitor", 
            f"{UISymbols.get_functional_icon('topic_driven')} Topic Monitor", 
            f"{UISymbols.get_status_icon('send')} Send Messages"
        ])
        
        with tab1:
            _render_message_monitor_tab(admin_gateway)
        
        with tab2:
            _render_topic_monitor_tab(admin_gateway)
        
        with tab3:
            _render_send_test_message_tab(admin_gateway)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Message Center Tab error: {e}")
        i18n = st.session_state.get("i18n_manager")
        error_msg = i18n.t('admin.message_center.tab_failed').format(error=e) if i18n else f"Message Center failed: {e}"
        st.error(f"{UISymbols.get_status_icon('error')} {error_msg}")


def _render_message_monitor_tab(admin_gateway):
    """Render Message Monitor tab (formerly Enhanced View)"""
    from omf2.ui.admin.message_center.message_monitor_subtab import render_message_monitor_subtab
    render_message_monitor_subtab(admin_gateway)


def _render_topic_monitor_tab(admin_gateway):
    """Render Topic Monitor tab"""
    from omf2.ui.admin.message_center.topic_monitor_subtab import render_topic_monitor_subtab
    render_topic_monitor_subtab(admin_gateway)


def _render_send_test_message_tab(admin_gateway):
    """Render Send Test Message tab"""
    from omf2.ui.admin.message_center.send_test_message_subtab import render_send_test_message_subtab
    render_send_test_message_subtab(admin_gateway)