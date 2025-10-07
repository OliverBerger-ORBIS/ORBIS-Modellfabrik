#!/usr/bin/env python3
"""
Generic Steering Tab - Modular Architecture with Factory and Topic Steering
Gateway-Pattern konform: Nutzt AdminGateway aus Gateway-Factory
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols
from omf2.common.i18n import I18nManager

logger = get_logger(__name__)


def render_generic_steering_tab():
    """Render Generic Steering Tab with Factory and Topic Steering Subtabs"""
    logger.info("🎛️ Rendering Generic Steering Tab")
    
    try:
        # Initialize i18n
        i18n = I18nManager()
        
        st.title(f"{UISymbols.get_tab_icon('generic_steering')} {i18n.translate('tabs.generic_steering')}")
        st.markdown("**Factory Management and Control with Modular Architecture**")
        
        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
            return
        
        # Get Registry Manager from session state
        registry_manager = st.session_state.get('registry_manager')
        
        # Connection status shown in sidebar only
        
        # Registry Manager Status
        if registry_manager:
            stats = registry_manager.get_registry_stats()
            total_entities = (stats['topics_count'] + stats['schemas_count'] + 
                            stats['mqtt_clients_count'] + stats['workpieces_count'] + 
                            stats['modules_count'] + stats['stations_count'] + 
                            stats['txt_controllers_count'])
            st.info(f"{UISymbols.get_status_icon('history')} **Registry:** {total_entities} entities loaded")
        else:
            st.warning(f"{UISymbols.get_status_icon('warning')} **Registry Manager not available**")
        
        # Tabs for different steering modes using UISymbols
        tab1, tab2 = st.tabs([
            f"{UISymbols.get_tab_icon('ccu_dashboard')} Factory Steering", 
            f"{UISymbols.get_functional_icon('topic_driven')} Topic Steering"
        ])
        
        with tab1:
            _render_factory_steering_tab(admin_gateway, registry_manager)
        
        with tab2:
            _render_topic_steering_tab(admin_gateway, registry_manager)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Generic Steering Tab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Generic Steering failed: {e}")


def _render_factory_steering_tab(admin_gateway, registry_manager):
    """Render Factory Steering Tab"""
    from omf2.ui.admin.generic_steering.factory_steering_subtab import render_factory_steering_subtab
    render_factory_steering_subtab(admin_gateway, registry_manager)


def _render_topic_steering_tab(admin_gateway, registry_manager):
    """Render Topic Steering Tab"""
    from omf2.ui.admin.generic_steering.topic_steering_subtab import render_topic_steering_subtab
    render_topic_steering_subtab(admin_gateway, registry_manager)