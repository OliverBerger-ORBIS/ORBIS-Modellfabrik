#!/usr/bin/env python3
"""
Message Center Tab - Standard konform mit 3 Subtabs
Gateway-Pattern konform: Nutzt AdminGateway aus Gateway-Factory
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_message_center_tab():
    """Render Message Center Tab - Standard konform"""
    logger.info("📧 Rendering Message Center Tab")
    
    try:
        # Header
        st.subheader(f"{UISymbols.get_tab_icon('message_center')} Message Center")
        st.markdown("**MQTT Live Monitoring and Message Testing**")
        
        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
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
        st.error(f"{UISymbols.get_status_icon('error')} Message Center failed: {e}")


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