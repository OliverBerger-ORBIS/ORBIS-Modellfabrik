#!/usr/bin/env python3
"""
Overview Subtab - General CCU Overview with Auto-Refresh
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.common.refresh_polling import init_auto_refresh_polling, get_api_url
from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload

logger = get_logger(__name__)


def load_overview_data(ccu_gateway=None, registry_manager=None):
    """Load overview data and store in session state."""
    try:
        # Load various overview data
        overview_data = {
            'timestamp': None,
            'modules_count': 0,
            'active_orders': 0,
            'completed_orders': 0,
        }
        
        # Get data from gateway if available
        if ccu_gateway:
            try:
                # Get modules info
                from omf2.ccu.module_manager import get_ccu_module_manager
                module_manager = get_ccu_module_manager()
                modules = module_manager.get_all_modules()
                overview_data['modules_count'] = len(modules)
            except Exception as e:
                logger.warning(f"Could not load modules count: {e}")
        
        if ccu_gateway:
            try:
                # Get orders info
                from omf2.ccu.order_manager import get_order_manager
                order_manager = get_order_manager()
                active = order_manager.get_active_orders()
                completed = order_manager.get_completed_orders()
                overview_data['active_orders'] = len(active)
                overview_data['completed_orders'] = len(completed)
            except Exception as e:
                logger.warning(f"Could not load orders count: {e}")
        
        # Store in session state
        st.session_state['overview_data'] = overview_data
        logger.debug(f"📊 Loaded overview data: {overview_data}")
        
    except Exception as e:
        logger.error(f"❌ Error loading overview data: {e}")
        st.session_state['overview_data'] = {}


def render_overview_subtab(ccu_gateway=None, registry_manager=None, asset_manager=None):
    """Render Overview Subtab with Auto-Refresh
    
    Args:
        ccu_gateway: CcuGateway instance
        registry_manager: RegistryManager instance
        asset_manager: AssetManager instance
    """
    logger.info("📊 Rendering Overview Subtab")
    
    try:
        # Get i18n manager
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            st.error("❌ I18n Manager not found")
            return
        
        # Initialize auto-refresh polling (1 second interval)
        init_auto_refresh_polling('order_updates', interval_ms=1000)
        
        # Use check_and_reload for consistent refresh handling
        API_BASE = get_api_url()
        
        def reload_wrapper():
            load_overview_data(ccu_gateway, registry_manager)
        
        check_and_reload(
            API_BASE,
            group='order_updates',
            reload_callable=reload_wrapper,
            session_state_key='overview_last_refresh'
        )
        
        # Get data from session state
        overview_data = st.session_state.get('overview_data')
        
        # Initial load if not in session state
        if overview_data is None:
            load_overview_data(ccu_gateway, registry_manager)
            overview_data = st.session_state.get('overview_data', {})
        
        # Display overview
        st.markdown(f"### {UISymbols.get_functional_icon('dashboard')} Overview")
        st.markdown("Real-time overview of CCU system status")
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"{UISymbols.get_functional_icon('module')} Modules",
                value=overview_data.get('modules_count', 0)
            )
        
        with col2:
            st.metric(
                label=f"{UISymbols.get_status_icon('in_progress')} Active Orders",
                value=overview_data.get('active_orders', 0)
            )
        
        with col3:
            st.metric(
                label=f"{UISymbols.get_status_icon('success')} Completed Orders",
                value=overview_data.get('completed_orders', 0)
            )
        
        st.divider()
        
        # Additional overview information
        st.info(f"{UISymbols.get_status_icon('info')} This overview provides a real-time summary of the CCU system.")
        
    except Exception as e:
        logger.error(f"❌ Overview Subtab rendering error: {e}")
        st.error(f"❌ Overview Subtab failed: {e}")
