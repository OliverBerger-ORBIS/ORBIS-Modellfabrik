#!/usr/bin/env python3
"""
Generic Steering Tab - Simplified for Development
"""

import streamlit as st
from omf2.admin.admin_gateway import AdminGateway
from omf2.admin.admin_mqtt_client import get_admin_mqtt_client
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_generic_steering_tab():
    """Render Generic Steering Tab - Simplified for Development"""
    logger.info("🎛️ Rendering Generic Steering Tab")
    try:
        st.header("🎛️ Factory Control")
        st.markdown("**Factory Management and Control**")
        
        # Initialize Gateways and MQTT Client
        if 'admin_gateway' not in st.session_state:
            st.session_state['admin_gateway'] = AdminGateway()
        
        if 'ccu_gateway' not in st.session_state:
            st.session_state['ccu_gateway'] = CcuGateway()
        
        if 'admin_mqtt_client' not in st.session_state:
            st.session_state['admin_mqtt_client'] = get_admin_mqtt_client()
        
        admin_gateway = st.session_state['admin_gateway']
        ccu_gateway = st.session_state['ccu_gateway']
        admin_client = st.session_state['admin_mqtt_client']
        
        # Connect to MQTT (based on current environment)
        current_env = st.session_state.get('current_environment', 'mock')
        if not admin_client.connected:
            admin_client.connect(current_env)
        
        # Simple Status
        st.info(f"🔗 **Client:** {admin_client.client_id} | **Environment:** {current_env}")
        
        # Factory Commands (Main Focus)
        st.subheader("🚨 Factory Commands")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Factory", key="reset_factory_btn"):
                if ccu_gateway.reset_factory():
                    st.success("✅ Factory Reset initiated!")
                else:
                    st.error("❌ Factory Reset failed")
        
        with col2:
            global_command = st.text_input("Global Command:", key="global_command_input")
            if st.button("🚀 Send Command", key="send_command_btn"):
                if global_command:
                    if ccu_gateway.send_global_command(global_command):
                        st.success(f"✅ Command '{global_command}' sent!")
                    else:
                        st.error(f"❌ Command '{global_command}' failed")
                else:
                    st.warning("⚠️ Please enter a command")
        
        # Simple Module Control
        st.subheader("🔧 Module Control")
        
        module_options = ["Module A", "Module B", "Module C"]
        selected_module = st.selectbox("Select Module:", module_options, key="module_selector")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"▶️ Start {selected_module}", key=f"start_{selected_module}_btn"):
                st.success(f"Starting {selected_module}...")
            if st.button(f"⏸️ Pause {selected_module}", key=f"pause_{selected_module}_btn"):
                st.warning(f"Pausing {selected_module}...")
        
        with col2:
            if st.button(f"⏹️ Stop {selected_module}", key=f"stop_{selected_module}_btn"):
                st.error(f"Stopping {selected_module}...")
            if st.button(f"🔄 Calibrate {selected_module}", key=f"calibrate_{selected_module}_btn"):
                st.info(f"Calibrating {selected_module}...")
        
    except Exception as e:
        logger.error(f"❌ Generic Steering Tab error: {e}")
        st.error(f"❌ Generic Steering failed: {e}")