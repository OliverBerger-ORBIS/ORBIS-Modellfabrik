#!/usr/bin/env python3
"""
Admin Settings - Dashboard Subtab
"""

import streamlit as st
from omf2.admin.admin_gateway import AdminGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_dashboard_subtab():
    """Render Dashboard Configuration Subtab"""
    # Only log on first render
    if "dashboard_subtab_logged" not in st.session_state:
        logger.info("📊 Rendering Dashboard Configuration Subtab (init only)")
        st.session_state["dashboard_subtab_logged"] = True
    try:
        st.subheader("📊 Dashboard Configuration")
        st.markdown("Configure dashboard appearance and behavior")
        
        # Placeholder content
        st.info("💡 Dashboard configuration will be implemented here")
        
        # Example configuration sections
        with st.expander("🎨 Appearance Settings", expanded=True):
            st.write("Customize dashboard appearance")
            st.selectbox("Theme", ["light", "dark", "auto"], key="admin_settings_dashboard_theme")
            st.selectbox("Language", ["de", "en", "fr"], key="admin_settings_dashboard_language")
            st.slider("Refresh Rate (seconds)", 1, 60, 5, key="admin_settings_dashboard_refresh_rate")
        
        with st.expander("📱 Layout Configuration", expanded=False):
            st.write("Configure dashboard layout and components")
            st.checkbox("Show Connection Status", value=True, key="admin_settings_dashboard_show_connection")
            st.checkbox("Show System Logs", value=True, key="admin_settings_dashboard_show_logs")
        
        with st.expander("🔔 Notifications", expanded=False):
            st.write("Configure notification settings")
            st.checkbox("Enable Sound Notifications", key="admin_settings_dashboard_sound_notifications")
            st.checkbox("Enable Email Notifications", key="admin_settings_dashboard_email_notifications")
        
    except Exception as e:
        logger.error(f"❌ Dashboard Subtab rendering error: {e}")
        st.error(f"❌ Dashboard Subtab failed: {e}")
        st.info("💡 This component is currently under development.")
