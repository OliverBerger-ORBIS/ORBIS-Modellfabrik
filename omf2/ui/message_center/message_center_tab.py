"""
Message Center Tab Component
MQTT-based messaging interface and communication center
"""

import streamlit as st
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from omf2.common.i18n import translate, get_current_language
from omf2.common.env_manager import EnvironmentManager
from omf2.message_center.mqtt_gateway import MqttGateway
from omf2.message_center.message_handler import MessageHandler, MessageRow
from omf.dashboard.utils.ui_refresh import request_refresh


def show_message_center_tab(logger: logging.Logger):
    """
    Show MQTT-based Message Center Tab
    
    Args:
        logger: Logger instance for this component
    """
    logger.info("📡 MQTT Message Center Tab geöffnet")
    
    current_lang = get_current_language()
    
    st.header("📡 MQTT Nachrichtenzentrale")
    st.markdown("Empfängt und verwaltet MQTT-Nachrichten in Echtzeit")
    
    # Initialize components
    env_manager = EnvironmentManager()
    message_handler = MessageHandler()
    
    # Initialize MQTT Gateway in session state
    if "mqtt_gateway" not in st.session_state:
        current_env = env_manager.get_current_environment()
        st.session_state.mqtt_gateway = MqttGateway(current_env)
        
        # Connect and subscribe to all topics
        if st.session_state.mqtt_gateway.connect():
            st.session_state.mqtt_gateway.subscribe_to_all_topics()
            logger.info(f"MQTT Gateway connected and subscribed to all topics in {current_env} environment")
    
    gateway = st.session_state.mqtt_gateway
    
    # Show sidebar with environment management
    selected_env = env_manager.show_complete_sidebar(gateway)
    
    # Handle environment switch
    if selected_env != gateway.environment:
        logger.info(f"Environment switch requested: {gateway.environment} -> {selected_env}")
        
        if gateway.switch_environment(selected_env):
            gateway.subscribe_to_all_topics()
            st.success(f"✅ Umgebung gewechselt zu {selected_env}")
            request_refresh()
        else:
            st.error(f"❌ Fehler beim Wechseln zu {selected_env}")
    
    # Connection status header
    status = gateway.get_connection_status()
    
    col_status, col_stats, col_actions = st.columns([2, 2, 1])
    
    with col_status:
        if status["connected"]:
            st.success(f"✅ Verbunden mit {status['environment']} ({status['broker']})")
        else:
            st.error(f"❌ Nicht verbunden mit {status['environment']}")
            if st.button("🔄 Verbindung wiederherstellen"):
                if gateway.connect():
                    gateway.subscribe_to_all_topics()
                    st.success("✅ Verbindung wiederhergestellt")
                    request_refresh()
    
    with col_stats:
        messages_info = status.get("messages", {})
        st.metric(
            "📊 Nachrichten", 
            f"{messages_info.get('total', 0)}/{messages_info.get('max_capacity', 1000)}",
            f"↑{messages_info.get('received', 0)} ↓{messages_info.get('sent', 0)}"
        )
    
    with col_actions:
        if st.button("🗑️ Historie löschen"):
            gateway.clear_message_history()
            logger.info("Message history cleared")
            st.success("✅ Historie gelöscht")
            request_refresh()
    
    # Filter section
    st.subheader("🔍 Filter & Einstellungen")
    
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        message_type_filter = st.selectbox(
            "Nachrichtentyp:",
            ["all", "received", "sent"],
            format_func=lambda x: {"all": "Alle", "received": "📥 Empfangen", "sent": "📤 Gesendet"}.get(x, x),
            key="msg_type_filter"
        )
    
    with col_filter2:
        module_filter = st.selectbox(
            "Modul:",
            ["all", "HBW", "FTS", "MILL", "DRILL", "OVEN", "AIQS", "CCU", "TXT", "Node-RED"],
            key="module_filter"
        )
    
    with col_filter3:
        topic_filter = st.text_input(
            "Topic-Filter:",
            placeholder="z.B. f/i/order",
            key="topic_filter"
        )
    
    with col_filter4:
        max_messages = st.number_input(
            "Max. Nachrichten:",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            key="max_messages"
        )
    
    # Get and process messages
    raw_messages = gateway.get_all_messages()
    
    if raw_messages:
        # Convert to MessageRow objects
        message_rows = message_handler.convert_messages_to_rows(raw_messages)
        
        # Apply filters
        filtered_messages = message_rows
        
        if message_type_filter != "all":
            filtered_messages = message_handler.filter_messages_by_type(filtered_messages, message_type_filter)
        
        if module_filter != "all":
            filtered_messages = message_handler.filter_messages_by_module(filtered_messages, module_filter)
        
        if topic_filter:
            filtered_messages = message_handler.filter_messages_by_topic(filtered_messages, topic_filter)
        
        # Sort by timestamp (newest first)
        filtered_messages = message_handler.sort_messages(filtered_messages, "timestamp", ascending=False)
        
        # Limit number of messages
        filtered_messages = filtered_messages[:max_messages]
        
        # Statistics
        stats = message_handler.get_message_statistics(filtered_messages)
        
        # Show statistics
        st.subheader("📊 Statistiken")
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Gesamt", f"{stats['total']}")
        
        with col_stat2:
            st.metric("Empfangen", f"{stats['received']}")
        
        with col_stat3:
            st.metric("Gesendet", f"{stats['sent']}")
        
        with col_stat4:
            st.metric("Topics", f"{stats['unique_topics']}")
        
        # Recent activity
        recent_activity = message_handler.get_recent_activity_summary(filtered_messages)
        if recent_activity["count"] > 0:
            st.info(f"📈 Letzte 5 Min: {recent_activity['count']} Nachrichten "
                   f"(↑{recent_activity['received']} ↓{recent_activity['sent']})")
        
        # Messages table
        st.subheader("📨 Nachrichten")
        
        if filtered_messages:
            # Create table data
            headers, rows = message_handler.create_table_data(filtered_messages)
            
            # Convert to DataFrame for better display
            df = pd.DataFrame(rows, columns=headers)
            
            # Display as dataframe with fixed columns
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Zeit": st.column_config.TextColumn("Zeit", width="small"),
                    "Typ": st.column_config.TextColumn("Typ", width="small"),
                    "Topic": st.column_config.TextColumn("Topic", width="medium"),
                    "Payload": st.column_config.TextColumn("Payload", width="large"),
                    "QoS": st.column_config.TextColumn("QoS", width="small"),
                    "Retain": st.column_config.TextColumn("Retain", width="small")
                }
            )
            
            # Show active topics
            if stats["topics"]:
                with st.expander("📂 Aktive Topics", expanded=False):
                    for topic in stats["topics"]:
                        st.code(topic)
        else:
            st.info("📭 Keine Nachrichten entsprechen den Filterkriterien")
    
    else:
        st.info("📭 Noch keine MQTT-Nachrichten empfangen")
        st.markdown("💡 Nachrichten erscheinen hier sobald sie über MQTT empfangen werden")
    
    # Manual message sending (for testing)
    with st.expander("📤 Nachricht senden (Test)", expanded=False):
        with st.form("send_mqtt_test_message"):
            test_topic = st.text_input("Topic:", placeholder="test/message")
            test_payload = st.text_area("Payload (JSON):", placeholder='{"message": "Hello World"}')
            test_qos = st.selectbox("QoS:", [0, 1, 2])
            test_retain = st.checkbox("Retain")
            
            if st.form_submit_button("📤 Senden"):
                if test_topic and test_payload:
                    try:
                        import json
                        payload_data = json.loads(test_payload) if test_payload.startswith('{') else test_payload
                        
                        if gateway.publish_message(test_topic, payload_data, test_qos, test_retain):
                            st.success("✅ Nachricht gesendet!")
                            logger.info(f"Test message sent: {test_topic}")
                            request_refresh()
                        else:
                            st.error("❌ Fehler beim Senden")
                    except json.JSONDecodeError:
                        st.error("❌ Ungültiges JSON-Format")
                else:
                    st.error("❌ Topic und Payload sind erforderlich")


def _get_sample_messages():
    """Generate sample messages (kept for backward compatibility)"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return [
        {
            "title": "System-Start",
            "content": "Das OMF Dashboard wurde erfolgreich gestartet.",
            "sender": "System",
            "recipient": "All Users",
            "type": "Info",
            "priority": "Normal",
            "timestamp": current_time,
            "icon": "ℹ️",
            "unread": True
        }
    ]


def _get_message_icon(message_type: str) -> str:
    """Get icon for message type (kept for backward compatibility)"""
    icons = {
        "Info": "ℹ️",
        "Warnung": "⚠️", 
        "Fehler": "❌",
        "Anfrage": "❓"
    }
    return icons.get(message_type, "📝")