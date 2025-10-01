#!/usr/bin/env python3
"""
Admin Settings Tab - Admin Settings UI Component
"""

import streamlit as st
from omf2.admin.admin_gateway import AdminGateway
from omf2.admin.admin_mqtt_client import get_admin_mqtt_client
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_admin_settings_tab():
    """Render Admin Settings Tab with Subtabs"""
    logger.info("⚙️ Rendering Admin Settings Tab")
    try:
        st.header("⚙️ Admin Settings")
        st.markdown("Dashboard configuration and registry information")
        
        # Create subtabs
        subtab_labels = [
            "📊 Dashboard",
            "📡 MQTT Clients", 
            "📋 Topics",
            "📝 Schemas",
            "🔧 Modules",
            "🏭 Stations",
            "🎮 TXT Controllers",
            "🔧 Workpieces"
        ]
        
        subtabs = st.tabs(subtab_labels)
        
        # Render subtab content
        with subtabs[0]:  # Dashboard
            from omf2.ui.admin.admin_settings.dashboard_subtab import render_dashboard_subtab
            render_dashboard_subtab()
        
        with subtabs[1]:  # MQTT Clients
            from omf2.ui.admin.admin_settings.mqtt_clients_subtab import render_mqtt_clients_subtab
            render_mqtt_clients_subtab()
        
        with subtabs[2]:  # Topics
            from omf2.ui.admin.admin_settings.topics_subtab import render_topics_subtab
            render_topics_subtab()
        
        with subtabs[3]:  # Schemas
            from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
            render_schemas_subtab()
        
        with subtabs[4]:  # Modules
            from omf2.ui.admin.admin_settings.module_subtab import render_module_subtab
            render_module_subtab()
        
        with subtabs[5]:  # Stations
            from omf2.ui.admin.admin_settings.stations_subtab import render_stations_subtab
            render_stations_subtab()
        
        with subtabs[6]:  # TXT Controllers
            from omf2.ui.admin.admin_settings.txt_controllers_subtab import render_txt_controllers_subtab
            render_txt_controllers_subtab()
        
        with subtabs[7]:  # Workpieces
            from omf2.ui.admin.admin_settings.workpiece_subtab import render_workpiece_subtab
            render_workpiece_subtab()
        
    except Exception as e:
        logger.error(f"❌ Admin Settings Tab rendering error: {e}")
        st.error(f"❌ Admin Settings Tab failed: {e}")
        st.info("💡 This component is currently under development.")