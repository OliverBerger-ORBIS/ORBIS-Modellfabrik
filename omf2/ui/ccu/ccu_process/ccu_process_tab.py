#!/usr/bin/env python3
"""
CCU Process Tab - Process Management UI Component
Wrapper Tab with Subtabs for Production Plan and Production Monitoring
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.common.i18n import I18nManager

logger = get_logger(__name__)


def render_ccu_process_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Process Tab with Subtabs
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("⚙️ Rendering CCU Process Tab")
    try:
        # Initialize CCU Gateway if not provided
        if not ccu_gateway:
            if 'ccu_gateway' not in st.session_state:
                # Use Gateway Factory to create CCU Gateway with MQTT Client
                from omf2.factory.gateway_factory import get_gateway_factory
                gateway_factory = get_gateway_factory()
                st.session_state['ccu_gateway'] = gateway_factory.get_ccu_gateway()
            ccu_gateway = st.session_state['ccu_gateway']

        # Initialize Registry Manager if not provided
        if not registry_manager:
            from omf2.registry.manager.registry_manager import get_registry_manager
            registry_manager = get_registry_manager()

        # Initialize i18n
        i18n = I18nManager()
        
        st.header(f"{UISymbols.get_tab_icon('ccu_process')} {i18n.translate('tabs.ccu_process')}")
        st.markdown("Production Planning and Process Monitoring")

        # Create subtabs
        subtab_labels = [
            f"{UISymbols.get_tab_icon('production_plan')} Production Plan",
            f"{UISymbols.get_tab_icon('production_monitoring')} Production Monitoring"
        ]

        subtabs = st.tabs(subtab_labels)

        # Render subtab content
        with subtabs[0]:
            from omf2.ui.ccu.ccu_process.ccu_production_plan_subtab import render_ccu_production_plan_subtab
            render_ccu_production_plan_subtab()

        with subtabs[1]:
            from omf2.ui.ccu.ccu_process.ccu_production_monitoring_subtab import render_ccu_production_monitoring_subtab
            render_ccu_production_monitoring_subtab()

    except Exception as e:
        logger.error(f"❌ CCU Process Tab rendering error: {e}")
        st.error(f"❌ CCU Process Tab failed: {e}")
        st.info("💡 This component is currently under development.")
