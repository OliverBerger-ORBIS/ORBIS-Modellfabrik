#!/usr/bin/env python3
"""
Admin Settings - Topics Subtab
"""

import streamlit as st
from omf2.admin.admin_gateway import AdminGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_topics_subtab():
    """Render Topics Configuration Subtab"""
    # Only log on first render
    if "topics_subtab_logged" not in st.session_state:
        logger.info("📋 Rendering Topics Configuration Subtab (init only)")
        st.session_state["topics_subtab_logged"] = True
    try:
        st.subheader("📋 Topics Configuration")
        st.markdown("Configure MQTT topics and their mappings")
        
        # Placeholder content
        st.info("💡 Topics configuration will be implemented here")
        
        # Example configuration sections
        with st.expander("📡 Topic Definitions", expanded=True):
            st.write("Manage MQTT topic definitions")
            st.text_input("Topic Pattern", key="admin_settings_topics_topic_pattern")
            st.selectbox("Topic Type", ["command", "status", "telemetry"], key="admin_settings_topics_topic_type")
            st.selectbox("QoS Level", [0, 1, 2], key="admin_settings_topics_topic_qos")
        
        with st.expander("🔄 Topic Mappings", expanded=False):
            st.write("Configure topic to template mappings")
            st.text_input("Template Name", key="admin_settings_topics_template_name")
            st.checkbox("Auto-generate Messages", key="admin_settings_topics_auto_generate")
        
        with st.expander("📊 Topic Analytics", expanded=False):
            st.write("View topic usage and performance metrics")
            st.metric("Active Topics", "42")
            st.metric("Messages/sec", "156")
            st.metric("Error Rate", "0.2%")
        
    except Exception as e:
        logger.error(f"❌ Topics Subtab rendering error: {e}")
        st.error(f"❌ Topics Subtab failed: {e}")
        st.info("💡 This component is currently under development.")
