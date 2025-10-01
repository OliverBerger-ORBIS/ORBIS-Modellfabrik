#!/usr/bin/env python3
"""
Message Center Tab - Standard konform mit 3 Subtabs
Gateway-Pattern konform: Nutzt AdminGateway aus Gateway-Factory
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway

logger = get_logger(__name__)


def render_message_center_tab():
    """Render Message Center Tab - Standard konform"""
    logger.info("📧 Rendering Message Center Tab")
    
    try:
        # Header
        st.subheader("📧 Message Center")
        st.markdown("**MQTT Live Monitoring and Message Testing**")
        
        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error("❌ Admin Gateway not available")
            return
        
        # Get connection info via Gateway
        conn_info = admin_gateway.get_connection_info()
        
        # Connection Status removed - shown in sidebar instead
        
        # Tabs for different functions - Standard konform
        tab1, tab2, tab3 = st.tabs(["📊 Message Monitor", "📡 Topic Monitor", "🚀 Send Messages"])
        
        with tab1:
            _render_message_monitor_tab(admin_gateway, conn_info)
        
        with tab2:
            _render_topic_monitor_tab(admin_gateway, conn_info)
        
        with tab3:
            _render_send_test_message_tab(admin_gateway, conn_info)
        
    except Exception as e:
        logger.error(f"❌ Message Center Tab error: {e}")
        st.error(f"❌ Message Center failed: {e}")


def _render_message_monitor_tab(admin_gateway, conn_info):
    """Render Message Monitor tab (formerly Enhanced View)"""
    from omf2.ui.admin.message_center.message_monitor_subtab import render_message_monitor_subtab
    render_message_monitor_subtab(admin_gateway, conn_info)


def _render_topic_monitor_tab(admin_gateway, conn_info):
    """Render Topic Monitor tab"""
    from omf2.ui.admin.message_center.topic_monitor_subtab import render_topic_monitor_subtab
    render_topic_monitor_subtab(admin_gateway, conn_info)


def _render_send_test_message_tab(admin_gateway, conn_info):
    """Render Send Test Message tab"""
    from omf2.ui.admin.message_center.send_test_message_subtab import render_send_test_message_subtab
    render_send_test_message_subtab(admin_gateway, conn_info)