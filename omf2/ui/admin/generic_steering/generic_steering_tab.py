#!/usr/bin/env python3
"""
Generic Steering Tab - Modular Architecture with Factory and Topic Steering
"""

import streamlit as st
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_generic_steering_tab():
    """Render Generic Steering Tab with Factory and Topic Steering Subtabs"""
    logger.info("🎛️ Rendering Generic Steering Tab")
    
    try:
        st.title("🎛️ Generic Steering")
        st.markdown("**Factory Management and Control with Modular Architecture**")
        
        # Get Admin MQTT Client from session state (already initialized in omf.py)
        admin_mqtt_client = st.session_state.get('admin_mqtt_client')
        if not admin_mqtt_client:
            st.error("❌ Admin MQTT client not available")
            return
        
        # Get Registry Manager from session state
        registry_manager = st.session_state.get('registry_manager')
        
        # Reconnect only if connection was lost (central connection in omf.py)
        current_env = st.session_state.get('current_environment', 'mock')
        if not admin_mqtt_client.connected:
            admin_mqtt_client.connect(current_env)
            logger.warning(f"🔄 Reconnecting to {current_env} (connection was lost)")
        
        # Connection Status
        conn_info = admin_mqtt_client.get_connection_info()
        if conn_info['connected']:
            st.success(f"🔗 **Connected:** {conn_info['client_id']} | **Environment:** {current_env}")
        else:
            st.error(f"🔴 **Disconnected:** {conn_info['client_id']} | **Environment:** {current_env}")
        
        # Registry Manager Status
        if registry_manager:
            stats = registry_manager.get_registry_stats()
            total_entities = (stats['topics_count'] + stats['templates_count'] + 
                            stats['mqtt_clients_count'] + stats['workpieces_count'] + 
                            stats['modules_count'] + stats['stations_count'] + 
                            stats['txt_controllers_count'])
            st.info(f"📚 **Registry:** {total_entities} entities loaded")
        else:
            st.warning("⚠️ **Registry Manager not available**")
        
        # Tabs for different steering modes
        tab1, tab2 = st.tabs(["🏭 Factory Steering", "🔧 Topic Steering"])
        
        with tab1:
            _render_factory_steering_tab(admin_mqtt_client, registry_manager)
        
        with tab2:
            _render_topic_steering_tab(admin_mqtt_client, registry_manager)
        
    except Exception as e:
        logger.error(f"❌ Generic Steering Tab error: {e}")
        st.error(f"❌ Generic Steering failed: {e}")


def _render_factory_steering_tab(admin_mqtt_client, registry_manager):
    """Render Factory Steering Tab"""
    from omf2.ui.admin.generic_steering.factory_steering_subtab import render_factory_steering_subtab
    render_factory_steering_subtab(admin_mqtt_client, registry_manager)


def _render_topic_steering_tab(admin_mqtt_client, registry_manager):
    """Render Topic Steering Tab"""
    from omf2.ui.admin.generic_steering.topic_steering_subtab import render_topic_steering_subtab
    render_topic_steering_subtab(admin_mqtt_client, registry_manager)