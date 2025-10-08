#!/usr/bin/env python3
"""
CCU Orders Tab - Order Management UI Component (Wrapper mit Subtabs)
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.production_order_manager import get_production_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.common.i18n import I18nManager
from .production_orders_subtab import show_production_orders_subtab
from .storage_orders_subtab import show_storage_orders_subtab

logger = get_logger(__name__)


def render_ccu_orders_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Orders Tab (Wrapper mit Production/Storage Subtabs)
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📝 Rendering CCU Orders Tab")
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
        
        st.header(f"{UISymbols.get_tab_icon('ccu_orders')} {i18n.translate('tabs.ccu_orders')}")
        st.markdown("Order Management and Processing")
        
        # Business Logic über ProductionOrderManager
        production_order_manager = get_production_order_manager()
        statistics = production_order_manager.get_order_statistics()
        
        # Order Statistics Section (oberhalb der Tabs)
        with st.expander(f"{UISymbols.get_status_icon('stats')} Order Statistics", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Orders", statistics.get('total_count', 0))
            
            with col2:
                st.metric("Active Orders", statistics.get('active_count', 0), "Processing")
            
            with col3:
                st.metric("Completed Orders", statistics.get('completed_count', 0))
            
            with col4:
                stub_mode = "🔧 STUB" if statistics.get('stub_mode') else "✅ Live"
                st.metric("Mode", stub_mode)
        
        # Tabs für Production vs Storage Orders
        tab1, tab2 = st.tabs(["🏭 Production Orders", "📦 Storage Orders"])
        
        with tab1:
            show_production_orders_subtab()
        
        with tab2:
            show_storage_orders_subtab()
        
        # Order Actions Section (unterhalb der Tabs)
        with st.expander("🎛️ Order Actions", expanded=False):
            st.markdown("### Order Control")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Create New Order", key="ccu_orders_create_btn"):
                    _create_new_order(ccu_gateway)
            
            with col2:
                if st.button("⏸️ Pause All Orders", key="ccu_orders_pause_btn"):
                    _pause_all_orders(ccu_gateway)
            
            with col3:
                if st.button("▶️ Resume All Orders", key="ccu_orders_resume_btn"):
                    _resume_all_orders(ccu_gateway)
        
    except Exception as e:
        logger.error(f"❌ CCU Orders Tab rendering error: {e}")
        st.error(f"❌ CCU Orders Tab failed: {e}")
        st.info("💡 This component is currently under development.")


def _create_new_order(ccu_gateway):
    """Create New Order using CCU Gateway"""
    try:
        logger.info("📝 Creating New Order via CCU Gateway")
        # TODO: Implement actual order creation via ccu_gateway
        # order_id = ccu_gateway.create_order(workpiece_data)
        st.success("✅ New order created via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Order creation error: {e}")
        st.error(f"❌ Order creation failed: {e}")


def _pause_all_orders(ccu_gateway):
    """Pause All Orders using CCU Gateway"""
    try:
        logger.info("⏸️ Pausing All Orders via CCU Gateway")
        # TODO: Implement actual order pause via ccu_gateway
        # ccu_gateway.pause_all_orders()
        st.success("⏸️ All orders paused via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Order pause error: {e}")
        st.error(f"❌ Order pause failed: {e}")


def _resume_all_orders(ccu_gateway):
    """Resume All Orders using CCU Gateway"""
    try:
        logger.info("▶️ Resuming All Orders via CCU Gateway")
        # TODO: Implement actual order resume via ccu_gateway
        # ccu_gateway.resume_all_orders()
        st.success("▶️ All orders resumed via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Order resume error: {e}")
        st.error(f"❌ Order resume failed: {e}")