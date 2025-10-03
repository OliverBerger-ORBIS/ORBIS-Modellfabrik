#!/usr/bin/env python3
"""
Admin Settings Tab - Admin Settings UI Component
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_admin_settings_tab():
    """Render Admin Settings Tab with Subtabs"""
    logger.info(f"{UISymbols.get_tab_icon('admin_settings')} Rendering Admin Settings Tab")
    try:
        st.header(f"{UISymbols.get_tab_icon('admin_settings')} Admin Settings")
        st.markdown("Dashboard configuration and registry information")
        
        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
            return
        
        # Get Registry Manager from session state
        registry_manager = st.session_state.get('registry_manager')
        
        # Create subtabs using UISymbols for consistent icon management
        subtab_labels = [
            f"{UISymbols.get_functional_icon('dashboard')} Dashboard",
            f"{UISymbols.get_functional_icon('mqtt_connect')} MQTT Clients", 
            f"{UISymbols.get_functional_icon('topic_driven')} Topics",
            f"{UISymbols.get_functional_icon('schema_driven')} Schemas",
            f"{UISymbols.get_tab_icon('ccu_modules')} Modules",
            f"{UISymbols.get_functional_icon('stations')} Stations",
            f"{UISymbols.get_functional_icon('txt_controllers')} TXT Controllers",
            f"{UISymbols.get_workpiece_icon('all_workpieces')} Workpieces"
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
        logger.error(f"{UISymbols.get_status_icon('error')} Admin Settings Tab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Admin Settings Tab failed: {e}")
        st.info("💡 This component is currently under development.")