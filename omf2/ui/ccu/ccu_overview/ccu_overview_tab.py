#!/usr/bin/env python3
"""
CCU Overview Tab - CCU Dashboard UI Component
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.ccu_mqtt_client import get_ccu_mqtt_client
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_ccu_overview_tab():
    """Render CCU Overview Tab"""
    logger.info("🏭 Rendering CCU Overview Tab")
    try:
        st.header("🏭 CCU Dashboard")
        st.markdown("Central Control Unit - Factory Management")
        
        # Initialize CCU Gateway
        if 'ccu_gateway' not in st.session_state:
            st.session_state['ccu_gateway'] = CcuGateway()
        
        ccu_gateway = st.session_state['ccu_gateway']
        
        # CCU Status Section
        with st.expander("📊 CCU Status", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", "🟢 Connected", "Online")
            
            with col2:
                st.metric("Modules", "7", "Active")
            
            with col3:
                st.metric("Orders", "3", "Processing")
        
        # Factory Control Section
        with st.expander("🎛️ Factory Control", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Reset Factory", type="primary", key="ccu_overview_reset_btn"):
                    if ccu_gateway.reset_factory():
                        st.success("✅ Factory reset initiated")
                    else:
                        st.error("❌ Factory reset failed")
            
            with col2:
                if st.button("📤 Send Global Command", key="ccu_overview_global_cmd_btn"):
                    command = st.text_input("Command:", value="status", key="ccu_overview_global_cmd_input")
                    if st.button("Send", key="ccu_overview_global_cmd_send"):
                        if ccu_gateway.send_global_command(command):
                            st.success(f"✅ Command '{command}' sent")
                        else:
                            st.error(f"❌ Command '{command}' failed")
        
        # Module States Section
        with st.expander("📋 Module States", expanded=True):
            st.markdown("### Active Modules")
            
            # Placeholder module data
            modules = [
                {"id": "SVR3QA0022", "name": "DPS", "state": "idle", "status": "🟢"},
                {"id": "SVR4H76449", "name": "FTS", "state": "moving", "status": "🟡"},
                {"id": "SVR3QA2098", "name": "AIQS", "state": "processing", "status": "🟢"},
                {"id": "SVR4H76530", "name": "CHRG", "state": "charging", "status": "🟢"},
                {"id": "SVR4H73275", "name": "CGW", "state": "idle", "status": "🟢"},
            ]
            
            for module in modules:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.write(f"**{module['name']}**")
                with col2:
                    st.write(module['id'])
                with col3:
                    st.write(module['state'])
                with col4:
                    st.write(module['status'])
        
        # Order Management Section
        with st.expander("📦 Order Management", expanded=True):
            st.markdown("### Active Orders")
            
            # Placeholder order data
            orders = [
                {"id": "ORD-001", "workpiece": "WP-001", "status": "processing", "progress": 75},
                {"id": "ORD-002", "workpiece": "WP-002", "status": "queued", "progress": 0},
                {"id": "ORD-003", "workpiece": "WP-003", "status": "completed", "progress": 100},
            ]
            
            for order in orders:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.write(f"**{order['id']}**")
                with col2:
                    st.write(order['workpiece'])
                with col3:
                    st.write(order['status'])
                with col4:
                    st.progress(order['progress'] / 100)
        
        # MQTT Client Info Section
        with st.expander("🔗 MQTT Client Info", expanded=False):
            st.markdown("### CCU MQTT Client Configuration")
            
            # Get MQTT client info
            ccu_mqtt_client = get_ccu_mqtt_client()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Published Topics:**")
                published_topics = ccu_gateway.get_published_topics()
                for topic in published_topics[:5]:  # Show first 5
                    st.write(f"• {topic}")
                if len(published_topics) > 5:
                    st.write(f"• ... and {len(published_topics) - 5} more")
            
            with col2:
                st.markdown("**Subscribed Topics:**")
                subscribed_topics = ccu_gateway.get_subscribed_topics()
                for topic in subscribed_topics[:5]:  # Show first 5
                    st.write(f"• {topic}")
                if len(subscribed_topics) > 5:
                    st.write(f"• ... and {len(subscribed_topics) - 5} more")
        
    except Exception as e:
        logger.error(f"❌ CCU Overview Tab rendering error: {e}")
        st.error(f"❌ CCU Overview Tab failed: {e}")
        st.info("💡 This component is currently under development.")
