#!/usr/bin/env python3
"""
Message Center Tab - Enhanced with Live MQTT Subscribe and Message History
"""

import streamlit as st
import json
import time
from typing import Dict, List, Any
from omf2.admin.admin_mqtt_client import get_admin_mqtt_client
from omf2.admin.admin_gateway import AdminGateway
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_message_center_tab():
    """Render Message Center Tab - Enhanced with Live MQTT and History"""
    logger.info("📨 Rendering Enhanced Message Center Tab")
    try:
        st.header("📨 Message Center")
        st.markdown("**MQTT Message Testing and Live Monitoring**")
        
        # Initialize Admin MQTT Client and Gateway
        if 'admin_mqtt_client' not in st.session_state:
            st.session_state['admin_mqtt_client'] = get_admin_mqtt_client()
        
        if 'admin_gateway' not in st.session_state:
            st.session_state['admin_gateway'] = AdminGateway()
        
        admin_client = st.session_state['admin_mqtt_client']
        admin_gateway = st.session_state['admin_gateway']
        
        # Get current environment and connection info (safe)
        current_env = st.session_state.get('current_environment', 'mock')
        try:
            conn_info = admin_client.get_connection_info()
        except Exception as e:
            logger.warning(f"⚠️ Failed to get connection info: {e}")
            conn_info = {
                "connected": False,
                "environment": current_env,
                "client_id": "unknown",
                "host": "unknown",
                "port": 1883,
                "mock_mode": True
            }
        
        # NO auto-connect in tabs - let main dashboard handle connections
        # This prevents multiple connection attempts per tab render
        
        # Connection Status Display
        col1, col2, col3 = st.columns(3)
        with col1:
            if conn_info['connected']:
                if conn_info['mock_mode']:
                    st.success("🧪 Mock Mode Active")
                else:
                    st.success("🟢 MQTT Connected")
            else:
                st.error("🔴 MQTT Disconnected")
        
        with col2:
            st.info(f"🌍 Environment: **{current_env}**")
        
        with col3:
            st.info(f"🆔 Client: `{conn_info['client_id']}`")
        
        # Tabs for different functions
        tab1, tab2, tab3 = st.tabs(["🚀 Send Messages", "📡 Live Monitor", "📋 Message History"])
        
        with tab1:
            _render_send_messages_tab(admin_client, conn_info)
        
        with tab2:
            _render_live_monitor_tab(admin_client, conn_info)
        
        with tab3:
            _render_message_history_tab(admin_client, conn_info)
        
    except Exception as e:
        logger.error(f"❌ Message Center Tab error: {e}")
        st.error(f"❌ Message Center failed: {e}")


def _render_send_messages_tab(admin_client, conn_info):
    """Render the Send Messages tab"""
    st.subheader("🚀 Send Test Messages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_topic = st.text_input(
            "Topic:", 
            value="omf2/test/message", 
            key="test_topic",
            help="MQTT topic to publish to"
        )
        test_message = st.text_area(
            "Message (JSON):", 
            value=json.dumps({
                "test": True,
                "message": "Hello from OMF2 Message Center",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "environment": conn_info.get('environment', 'unknown')
            }, indent=2),
            height=150,
            key="test_message",
            help="JSON message to send"
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
        
        st.markdown("**Quick Templates:**")
        if st.button("📊 Status Message", key="template_status", use_container_width=True):
            st.session_state.test_topic = "omf2/status/heartbeat"
            st.session_state.test_message = json.dumps({
                "status": "online",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "client_id": conn_info.get('client_id', 'unknown'),
                "environment": conn_info.get('environment', 'unknown')
            }, indent=2)
            request_refresh()
        
        if st.button("🎯 Command Message", key="template_command", use_container_width=True):
            st.session_state.test_topic = "omf2/commands/test"
            st.session_state.test_message = json.dumps({
                "command": "ping",
                "target": "system",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sender": conn_info.get('client_id', 'unknown')
            }, indent=2)
            request_refresh()
    
    # Send button
    col_send1, col_send2, col_send3 = st.columns([1, 2, 1])
    with col_send2:
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


def _render_live_monitor_tab(admin_client, conn_info):
    """Render the Live Monitor tab"""
    st.subheader("📡 Live MQTT Topic Monitor")
    
    # Get all current topic buffers
    all_buffers = admin_client.get_all_buffers()
    
    if not all_buffers:
        st.info("📡 No MQTT messages received yet. Topics will appear here when messages arrive.")
        
        if not conn_info['mock_mode']:
            st.info("💡 Send a test message from the 'Send Messages' tab to see live monitoring in action!")
        else:
            st.info("🧪 Mock mode active - messages will be logged but not sent to real MQTT broker.")
        return
    
    # Topic filter
    col1, col2 = st.columns([3, 1])
    with col1:
        topic_filter = st.text_input(
            "Filter topics (supports wildcards like test/*):",
            key="topic_filter",
            placeholder="Leave empty to show all topics"
        )
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=True, key="auto_refresh_monitor")
        if st.button("🔄 Refresh Now", key="manual_refresh_monitor"):
            request_refresh()
    
    # Filter topics based on input
    filtered_topics = []
    if topic_filter:
        import fnmatch
        filtered_topics = [topic for topic in all_buffers.keys() 
                          if fnmatch.fnmatch(topic, topic_filter)]
    else:
        filtered_topics = list(all_buffers.keys())
    
    # Sort topics by most recent activity
    filtered_topics.sort(key=lambda t: all_buffers[t].get('timestamp', 0), reverse=True)
    
    st.write(f"**{len(filtered_topics)} active topics** (showing most recent first)")
    
    # Display topics with their latest messages
    for i, topic in enumerate(filtered_topics[:20]):  # Limit to first 20 topics
        buffer = all_buffers[topic]
        
        with st.expander(f"📨 {topic}", expanded=(i < 3)):  # Expand first 3 topics
            if 'timestamp' in buffer:
                timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(buffer['timestamp']))
                st.caption(f"⏰ Last updated: {timestamp_str}")
            
            # Display message content
            if 'raw_payload' in buffer:
                # Raw message
                st.text(f"Raw payload: {buffer['raw_payload']}")
            else:
                # JSON message
                display_dict = {k: v for k, v in buffer.items() if k != 'timestamp'}
                st.json(display_dict)
    
    if len(filtered_topics) > 20:
        st.info(f"📄 Showing first 20 of {len(filtered_topics)} topics. Use topic filter to narrow down results.")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(2)  # Wait 2 seconds before next refresh
        request_refresh()


def _render_message_history_tab(admin_client, conn_info):
    """Render the Message History tab"""
    st.subheader("📋 Message History & System Overview")
    
    # System overview
    system_overview = admin_client.get_system_overview()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Topics", system_overview.get('total_topics', 0))
    with col2:
        st.metric("Active Topics", len(system_overview.get('active_topics', [])))
    with col3:
        st.metric("Connection", "✅ Connected" if system_overview.get('mqtt_connected', False) else "❌ Disconnected")
    with col4:
        st.metric("Environment", conn_info.get('environment', 'unknown'))
    
    # Recent activity
    all_buffers = admin_client.get_all_buffers()
    if all_buffers:
        st.subheader("📊 Recent Activity")
        
        # Create a list of all messages with timestamps
        all_messages = []
        for topic, buffer in all_buffers.items():
            if 'timestamp' in buffer:
                all_messages.append({
                    'topic': topic,
                    'timestamp': buffer['timestamp'],
                    'data': buffer
                })
        
        # Sort by timestamp (most recent first)
        all_messages.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Display recent messages
        st.write(f"**Last {min(10, len(all_messages))} messages:**")
        
        for msg in all_messages[:10]:
            timestamp_str = time.strftime('%H:%M:%S', time.localtime(msg['timestamp']))
            
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.caption(f"⏰ {timestamp_str}")
                with col2:
                    st.caption(f"📨 **{msg['topic']}**")
                
                # Show message preview
                if 'raw_payload' in msg['data']:
                    st.text(f"Raw: {msg['data']['raw_payload'][:100]}...")
                else:
                    display_dict = {k: v for k, v in msg['data'].items() if k != 'timestamp'}
                    preview = json.dumps(display_dict)[:100]
                    st.text(f"JSON: {preview}...")
                
                st.markdown("---")
    
    else:
        st.info("📋 No message history available yet.")
        st.info("💡 Messages will appear here as they are received from MQTT topics.")