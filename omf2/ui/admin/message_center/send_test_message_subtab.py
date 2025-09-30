#!/usr/bin/env python3
"""
Send Test Message Subtab - MQTT Message Sending Interface
"""

import streamlit as st
import json
import time
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_send_test_message_subtab(admin_client, conn_info):
    """Render Send Test Message Subtab"""
    logger.info("🚀 Rendering Send Test Message Subtab")
    
    try:
        st.subheader("🚀 Send Test Messages")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_topic = st.text_input(
                "Topic:", 
                value="omf2/test/message", 
                key="test_topic",
                help="MQTT topic to publish to"
            )
            # Default JSON message (editable)
            default_message = {
                "message": "Hello from OMF2 Message Center",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "environment": conn_info.get('environment', 'unknown')
            }
            
            test_message = st.text_area(
                "Message (JSON):", 
                value=json.dumps(default_message, indent=2),
                height=150,
                key="test_message",
                help="JSON message to send - fully editable"
            )
        
        with col2:
            qos_level = st.selectbox(
                "QoS Level:", 
                [0, 1, 2], 
                index=1, 
                key="qos_level",
                help="MQTT Quality of Service level"
            )
            retain_flag = st.checkbox(
                "Retain Message", 
                value=False, 
                key="retain_flag",
                help="Keep message on broker for new subscribers"
            )
            
            # Send button in right column
            if st.button("🚀 Send Message", key="send_test_btn", type="primary", use_container_width=True):
                try:
                    message_dict = json.loads(test_message)
                    
                    success = admin_client.publish_message(
                        topic=test_topic,
                        message=message_dict,
                        qos=qos_level,
                        retain=retain_flag
                    )
                    
                    if success:
                        st.success(f"✅ Message sent to `{test_topic}`")
                        st.caption(f"QoS: {qos_level}, Retain: {retain_flag}")
                    else:
                        st.error("❌ Send failed")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
    except Exception as e:
        logger.error(f"❌ Send Test Message Subtab error: {e}")
        st.error(f"❌ Send Test Message failed: {e}")
