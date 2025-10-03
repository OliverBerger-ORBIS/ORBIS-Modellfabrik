#!/usr/bin/env python3
"""
CCU Orders Tab - Order Management UI Component
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_ccu_orders_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Orders Tab
    
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
        
        st.header("📦 CCU Orders")
        st.markdown("Order Management and Processing")
        
        # Order Statistics Section
        with st.expander("📊 Order Statistics", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Orders", "47", "↗️ +3")
            
            with col2:
                st.metric("Active Orders", "3", "Processing")
            
            with col3:
                st.metric("Completed Today", "12", "↗️ +2")
            
            with col4:
                st.metric("Success Rate", "98%", "↗️ +1%")
        
        # Order Management Section
        with st.expander("📋 Order Management", expanded=True):
            st.markdown("### Active Orders")
            
            # Order Control Buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Refresh Orders", key="ccu_orders_refresh_btn"):
                    _refresh_orders(ccu_gateway)
            
            with col2:
                if st.button("📊 Order Statistics", key="ccu_orders_stats_btn"):
                    st.info("📊 Order statistics feature coming soon!")
            
            with col3:
                if st.button("⚙️ Order Settings", key="ccu_orders_settings_btn"):
                    st.info("⚙️ Order settings feature coming soon!")
            
            st.divider()
            
            # Placeholder order data
            orders = [
                {"id": "ORD-001", "workpiece": "WP-001", "status": "processing", "progress": 75, "priority": "high"},
                {"id": "ORD-002", "workpiece": "WP-002", "status": "queued", "progress": 0, "priority": "medium"},
                {"id": "ORD-003", "workpiece": "WP-003", "status": "completed", "progress": 100, "priority": "low"},
            ]
            
            for order in orders:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{order['id']}**")
                    
                    with col2:
                        st.write(order['workpiece'])
                    
                    with col3:
                        status_color = {
                            "processing": "🟡",
                            "queued": "⚪",
                            "completed": "🟢"
                        }.get(order['status'], "⚪")
                        st.write(f"{status_color} {order['status']}")
                    
                    with col4:
                        st.progress(order['progress'] / 100)
                    
                    with col5:
                        priority_color = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(order['priority'], "⚪")
                        st.write(f"{priority_color} {order['priority']}")
        
        # Order Actions Section
        with st.expander("🎛️ Order Actions", expanded=True):
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


def _refresh_orders(ccu_gateway):
    """Refresh Orders using CCU Gateway"""
    try:
        logger.info("🔄 Refreshing Orders via CCU Gateway")
        # TODO: Implement actual order refresh via ccu_gateway
        # orders = ccu_gateway.get_orders()
        st.success("✅ Orders refreshed via CCU Gateway!")
    except Exception as e:
        logger.error(f"❌ Order refresh error: {e}")
        st.error(f"❌ Order refresh failed: {e}")


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
