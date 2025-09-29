#!/usr/bin/env python3
"""
Message Center Tab - Simplified for Development
"""

import streamlit as st
from omf2.admin.admin_mqtt_client import get_admin_mqtt_client
from omf2.admin.admin_gateway import AdminGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_message_center_tab():
    """Render Message Center Tab - Simplified for Development"""
    logger.info("📨 Rendering Message Center Tab")
    try:
        st.header("📨 Message Center")
        st.markdown("**MQTT Message Testing and Development**")
        
        # Initialize Admin MQTT Client and Gateway
        if 'admin_mqtt_client' not in st.session_state:
            st.session_state['admin_mqtt_client'] = get_admin_mqtt_client()
        
        if 'admin_gateway' not in st.session_state:
            st.session_state['admin_gateway'] = AdminGateway()
        
        admin_client = st.session_state['admin_mqtt_client']
        admin_gateway = st.session_state['admin_gateway']
        
        # Get current environment
        current_env = st.session_state.get('current_environment', 'mock')
        
        # Connect to MQTT (based on current environment)
        if not admin_client.connected:
            admin_client.connect(current_env)
        
        # Simple Status
        st.info(f"🔗 **Client:** {admin_client.client_id} | **Environment:** {current_env}")
        
        # Test Message Generation (Main Focus)
        st.subheader("🧪 Test Message Generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_topic = st.text_input("Topic:", value="omf2/test/message", key="test_topic")
            test_message = st.text_area(
                "Message (JSON):", 
                value='{"test": true, "message": "Hello from OMF2", "timestamp": "2025-09-29T14:00:00Z"}',
                key="test_message"
            )
        
        with col2:
            qos_level = st.selectbox("QoS:", [0, 1, 2], index=1, key="qos_level")
            retain_flag = st.checkbox("Retain", value=False, key="retain_flag")
            
            if st.button("🚀 Send Test Message", key="send_test_btn"):
                try:
                    import json
                    message_dict = json.loads(test_message)
                    
                    success = admin_client.publish_message(
                        topic=test_topic,
                        message=message_dict,
                        qos=qos_level,
                        retain=retain_flag
                    )
                    
                    if success:
                        st.success(f"✅ Sent to {test_topic}")
                        st.caption(f"QoS: {qos_level}, Retain: {retain_flag}")
                    else:
                        st.error("❌ Send failed")
                        
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # Simple Topic Overview
        st.subheader("📡 Active Topics")
        all_buffers = admin_client.get_all_buffers()
        if all_buffers:
            st.write(f"**{len(all_buffers)} topics active:**")
            for topic in list(all_buffers.keys())[:5]:
                st.write(f"• {topic}")
            if len(all_buffers) > 5:
                st.write(f"• ... and {len(all_buffers) - 5} more")
        else:
            st.write("**No topics active**")
        
    except Exception as e:
        logger.error(f"❌ Message Center Tab error: {e}")
        st.error(f"❌ Message Center failed: {e}")