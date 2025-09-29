#!/usr/bin/env python3
"""
Admin Settings - Templates Subtab
"""

import streamlit as st
from omf2.admin.admin_gateway import AdminGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_templates_subtab():
    """Render Templates Configuration Subtab"""
    # Only log on first render
    if "templates_subtab_logged" not in st.session_state:
        logger.info("📝 Rendering Templates Configuration Subtab (init only)")
        st.session_state["templates_subtab_logged"] = True
    try:
        st.subheader("📝 Templates Configuration")
        st.markdown("Configure message templates and schemas")
        
        # Placeholder content
        st.info("💡 Templates configuration will be implemented here")
        
        # Example configuration sections
        with st.expander("📋 Template Definitions", expanded=True):
            st.write("Manage message template definitions")
            st.text_input("Template Name", key="admin_settings_templates_template_name")
            st.selectbox("Template Category", ["module", "ccu", "fts", "nodered"], key="admin_settings_templates_template_category")
            st.text_area("Template Schema", key="admin_settings_templates_template_schema")
        
        with st.expander("🔄 Template Validation", expanded=False):
            st.write("Configure template validation rules")
            st.checkbox("Enable Schema Validation", value=True, key="admin_settings_templates_schema_validation")
            st.checkbox("Enable Field Validation", value=True, key="admin_settings_templates_field_validation")
        
        with st.expander("📊 Template Analytics", expanded=False):
            st.write("View template usage and performance")
            st.metric("Total Templates", "28")
            st.metric("Active Templates", "24")
            st.metric("Validation Errors", "3")
        
    except Exception as e:
        logger.error(f"❌ Templates Subtab rendering error: {e}")
        st.error(f"❌ Templates Subtab failed: {e}")
        st.info("💡 This component is currently under development.")
