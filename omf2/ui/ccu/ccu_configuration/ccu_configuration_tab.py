#!/usr/bin/env python3
"""
CCU Configuration Tab - CCU Configuration UI Component
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_ccu_configuration_tab():
    """Render CCU Configuration Tab with Subtabs"""
    logger.info("⚙️ Rendering CCU Configuration Tab")
    try:
        st.header("⚙️ CCU Configuration")
        st.markdown("CCU System Configuration and Settings")
        
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