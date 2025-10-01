#!/usr/bin/env python3
"""
Topic Steering Subtab - Commands from omf/dashboard/components/admin/steering_generic.py
Gateway-Pattern konform: Nutzt AdminGateway statt direkten MQTT-Client
"""

import streamlit as st
import json
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_topic_steering_subtab(admin_gateway, registry_manager):
    """Render Topic Steering Subtab with commands from steering_generic.py
    
    Args:
        admin_gateway: AdminGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz
    """
    logger.info("🔧 Rendering Topic Steering Subtab")
    
    try:
        st.subheader("🔧 Generic Steuerung")
        st.markdown("**Erweiterte Steuerungsmöglichkeiten für direkte MQTT-Nachrichten:**")
        
        # Free Mode Section
        st.markdown("### 📝 Freier Modus")
        st.markdown("**Direkte Eingabe von Topic und Message-Payload:**")
        
        with st.expander("📝 Free Mode Commands", expanded=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Topic:**")
                topic_input = st.text_input(
                    "MQTT Topic:",
                    value="ccu/command",
                    key="free_mode_topic",
                    help="Enter MQTT topic for the message"
                )
                
                st.markdown("**QoS Level:**")
                qos_level = st.selectbox(
                    "QoS:",
                    options=[0, 1, 2],
                    index=0,
                    key="free_mode_qos",
                    help="Quality of Service level"
                )
                
                retain_message = st.checkbox(
                    "Retain Message",
                    value=False,
                    key="free_mode_retain",
                    help="Retain message on broker"
                )
            
            with col2:
                st.markdown("**Message Payload (JSON):**")
                default_payload = {
                    "command": "status",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "source": "omf2_admin"
                }
                
                payload_input = st.text_area(
                    "JSON Payload:",
                    value=json.dumps(default_payload, indent=2),
                    height=150,
                    key="free_mode_payload",
                    help="Enter JSON payload for the message"
                )
            
            # Send button
            if st.button("🚀 Send Message", key="free_mode_send_btn", type="primary"):
                try:
                    # Parse JSON payload
                    payload = json.loads(payload_input)
                    
                    # Gateway-Pattern: Nutze AdminGateway publish_message
                    success = admin_gateway.publish_message(
                        topic=topic_input,
                        message=payload,
                        qos=qos_level,
                        retain=retain_message
                    )
                    
                    if success:
                        st.success(f"✅ Message sent to topic: {topic_input}")
                        st.json(payload)
                        logger.info(f"📤 Free mode message sent: {topic_input} (QoS: {qos_level}, Retain: {retain_message})")
                    else:
                        st.error(f"❌ Failed to send message to {topic_input}")
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Send failed: {e}")
                    logger.error(f"❌ Free mode send error: {e}")
        
        # Topic-driven Mode Section
        st.markdown("---")
        st.markdown("### 📡 Topic-getriebener Ansatz")
        st.markdown("**Topic auswählen und passende Message-Templates verwenden:**")
        
        with st.expander("📡 Topic-driven Commands", expanded=False):
            # TODO: Implement topic selection from registry_manager
            if registry_manager:
                topics = registry_manager.get_topics()
                topic_options = list(topics.keys())[:10]  # Limit for demo
                st.info(f"📚 Available topics from Registry: {len(topics)} total")
            else:
                topic_options = ["ccu/command", "module/status", "txt/control"]
                st.warning("⚠️ Registry Manager not available, using default topics")
            
            selected_topic = st.selectbox(
                "Select Topic:",
                options=topic_options,
                key="topic_driven_topic",
                help="Select topic from available options"
            )
            
            # TODO: Implement message templates based on selected topic
            st.info("🚧 TODO: Implement message templates based on selected topic")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Status Request", key="status_request_btn"):
                    st.success("Status request sent! (TODO: Implement)")
                if st.button("🔄 Reset Command", key="reset_command_btn"):
                    st.warning("Reset command sent! (TODO: Implement)")
            with col2:
                if st.button("▶️ Start Command", key="start_command_btn"):
                    st.success("Start command sent! (TODO: Implement)")
                if st.button("⏹️ Stop Command", key="stop_command_btn"):
                    st.error("Stop command sent! (TODO: Implement)")
        
        # Message-driven Mode Section (Placeholder)
        st.markdown("---")
        st.markdown("### 📋 Message-getriebener Ansatz")
        st.markdown("**Message-Template auswählen und passende Topics verwenden:**")
        
        with st.expander("📋 Message-driven Commands", expanded=False):
            st.info("🚧 TODO: Implement message-driven mode from steering_generic.py")
            st.markdown("**Geplante Funktionen:**")
            st.markdown("- Message Template Selection")
            st.markdown("- Auto Topic Detection")
            st.markdown("- Template Parameter Filling")
            
            # Placeholder message templates
            template_options = ["Status Message", "Command Message", "Control Message"]
            selected_template = st.selectbox(
                "Select Template:",
                options=template_options,
                key="message_driven_template",
                help="Select message template"
            )
            
            if st.button("📝 Load Template", key="load_template_btn"):
                st.info(f"Template '{selected_template}' loaded! (TODO: Implement)")
        
        # Connection Info via Gateway
        conn_info = admin_gateway.get_connection_info()
        if conn_info.get('connected', False):
            st.info(f"🔗 MQTT Client: {conn_info.get('client_id', 'Unknown')} | Connected: {conn_info.get('connected', False)}")
        else:
            st.warning("⚠️ MQTT Client not connected")
            
    except Exception as e:
        logger.error(f"❌ Topic Steering Subtab error: {e}")
        st.error(f"❌ Topic Steering failed: {e}")
