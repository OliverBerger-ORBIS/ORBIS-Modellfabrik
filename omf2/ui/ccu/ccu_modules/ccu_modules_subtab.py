#!/usr/bin/env python3
"""
CCU Modules Subtab - Module Management with Auto-Refresh
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.common.refresh_polling import init_auto_refresh_polling
from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload

logger = get_logger(__name__)


def load_ccu_modules():
    """Load CCU modules data and store in session state."""
    try:
        from omf2.ccu.module_manager import get_ccu_module_manager
        
        module_manager = get_ccu_module_manager()
        
        # Get all modules
        modules = module_manager.get_all_modules()
        
        # Get status for each module
        modules_data = []
        for module_id, module_info in modules.items():
            if not module_info.get("enabled", True):
                continue
            
            # Get real-time status
            status = module_manager.get_module_status_from_state(module_id)
            
            modules_data.append({
                'id': module_id,
                'name': module_info.get('name', module_id),
                'enabled': module_info.get('enabled', True),
                'connected': status.get('connected', False),
                'available': status.get('available', 'Unknown'),
                'message_count': status.get('message_count', 0),
                'last_update': status.get('last_update', 'Never'),
            })
        
        # Store in session state
        st.session_state['ccu_modules_data'] = modules_data
        logger.debug(f"🏗️ Loaded {len(modules_data)} CCU modules")
        
    except Exception as e:
        logger.error(f"❌ Error loading CCU modules: {e}")
        st.session_state['ccu_modules_data'] = []


def render_ccu_modules_subtab(ccu_gateway=None, registry_manager=None):
    """Render CCU Modules Subtab with Auto-Refresh
    
    Args:
        ccu_gateway: CcuGateway instance
        registry_manager: RegistryManager instance
    """
    logger.info("🏗️ Rendering CCU Modules Subtab")
    
    try:
        # Get i18n manager
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            st.error("❌ I18n Manager not found")
            return
        
        # Initialize auto-refresh polling (1 second interval)
        init_auto_refresh_polling('order_updates', interval_ms=1000)
        
        # Use check_and_reload for consistent refresh handling
        check_and_reload(
            group='order_updates',
            reload_callable=load_ccu_modules,
            session_state_key='ccu_modules_last_refresh'
        )
        
        # Get data from session state
        modules_data = st.session_state.get('ccu_modules_data')
        
        # Initial load if not in session state
        if modules_data is None:
            load_ccu_modules()
            modules_data = st.session_state.get('ccu_modules_data', [])
        
        # Display modules
        st.markdown(f"### {UISymbols.get_tab_icon('ccu_modules')} CCU Modules")
        st.markdown("Real-time status of CCU modules")
        
        if not modules_data:
            st.info(f"{UISymbols.get_status_icon('info')} No modules available")
            return
        
        # Display module cards
        for module in modules_data:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                
                with col1:
                    st.markdown(f"**{module['id']}**")
                    st.caption(module['name'])
                
                with col2:
                    connected_icon = UISymbols.get_status_icon('success') if module['connected'] else UISymbols.get_status_icon('error')
                    st.markdown(f"{connected_icon} {'Connected' if module['connected'] else 'Disconnected'}")
                
                with col3:
                    if module['available'] == 'READY':
                        avail_icon = UISymbols.get_status_icon('success')
                    elif module['available'] == 'BUSY':
                        avail_icon = UISymbols.get_status_icon('in_progress')
                    else:
                        avail_icon = UISymbols.get_status_icon('pending')
                    st.markdown(f"{avail_icon} {module['available']}")
                
                with col4:
                    st.caption(f"Messages: {module['message_count']}")
                    st.caption(f"Updated: {module['last_update']}")
                
                st.divider()
        
        # Summary metrics
        st.markdown("#### Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Modules", len(modules_data))
        
        with col2:
            connected_count = sum(1 for m in modules_data if m['connected'])
            st.metric("Connected", connected_count)
        
        with col3:
            ready_count = sum(1 for m in modules_data if m['available'] == 'READY')
            st.metric("Ready", ready_count)
        
    except Exception as e:
        logger.error(f"❌ CCU Modules Subtab rendering error: {e}")
        st.error(f"❌ CCU Modules Subtab failed: {e}")
