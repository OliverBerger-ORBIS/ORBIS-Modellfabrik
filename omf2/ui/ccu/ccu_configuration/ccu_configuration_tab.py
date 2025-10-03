#!/usr/bin/env python3
"""
CCU Configuration Tab - CCU Configuration UI Component
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_ccu_configuration_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Configuration Tab with Subtabs
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("⚙️ Rendering CCU Configuration Tab")
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
        
        st.header("⚙️ CCU Configuration")
        st.markdown("CCU System Configuration and Settings")
        
        # Configuration Control Section
        with st.expander("🎛️ Configuration Control", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Refresh Configuration", key="ccu_config_refresh_btn"):
                    _refresh_configuration(ccu_gateway)
            
            with col2:
                if st.button("💾 Save Configuration", key="ccu_config_save_btn"):
                    _save_configuration(ccu_gateway)
            
            with col3:
                if st.button("🔄 Reset Configuration", key="ccu_config_reset_btn"):
                    _reset_configuration(ccu_gateway)
        
        # Create subtabs
        subtab_labels = [
            "🏭 Factory Configuration",
            "⚙️ Parameter Configuration"
        ]
        
        subtabs = st.tabs(subtab_labels)
        
        # Render subtab content
        with subtabs[0]:
            from omf2.ui.ccu.ccu_configuration.ccu_factory_configuration_subtab import render_ccu_factory_configuration_subtab
            render_ccu_factory_configuration_subtab()
        
        with subtabs[1]:
            from omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab import render_ccu_parameter_configuration_subtab
            render_ccu_parameter_configuration_subtab()
        
    except Exception as e:
        logger.error(f"❌ CCU Configuration Tab rendering error: {e}")
        st.error(f"❌ CCU Configuration Tab failed: {e}")
        st.info("💡 This component is currently under development.")


def _refresh_configuration(ccu_gateway):
    """Refresh Configuration using CCU Gateway"""
    try:
        logger.info("🔄 Refreshing Configuration via CCU Gateway")
        # TODO: Implement actual configuration refresh via ccu_gateway
        # config = ccu_gateway.get_configuration()
        st.success("✅ Configuration refreshed via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Configuration refresh error: {e}")
        st.error(f"❌ Configuration refresh failed: {e}")


def _save_configuration(ccu_gateway):
    """Save Configuration using CCU Gateway"""
    try:
        logger.info("💾 Saving Configuration via CCU Gateway")
        # TODO: Implement actual configuration save via ccu_gateway
        # ccu_gateway.save_configuration(config_data)
        st.success("✅ Configuration saved via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Configuration save error: {e}")
        st.error(f"❌ Configuration save failed: {e}")


def _reset_configuration(ccu_gateway):
    """Reset Configuration using CCU Gateway"""
    try:
        logger.info("🔄 Resetting Configuration via CCU Gateway")
        # TODO: Implement actual configuration reset via ccu_gateway
        # ccu_gateway.reset_configuration()
        st.warning("🔄 Configuration reset via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Configuration reset error: {e}")
        st.error(f"❌ Configuration reset failed: {e}")