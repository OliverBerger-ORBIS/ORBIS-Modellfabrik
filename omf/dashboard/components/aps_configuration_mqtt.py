"""
APS Configuration - MQTT
Zeigt MQTT-Konfiguration für die APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSConfigurationMQTTManager:
    """Manager für APS MQTT Configuration"""
    
    def __init__(self):
        self.mqtt_config = {}
        self.last_update = None
    
    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die MQTT-Konfiguration basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to MQTT configuration topics
            mqtt_client.subscribe_many([
                "ccu/mqtt/config",
                "ccu/mqtt/status",
                "ccu/mqtt/topics"
            ])
            
            # Get messages from buffer
            config_messages = list(mqtt_client.get_buffer("ccu/mqtt/config"))
            status_messages = list(mqtt_client.get_buffer("ccu/mqtt/status"))
            topics_messages = list(mqtt_client.get_buffer("ccu/mqtt/topics"))
            
            # Process MQTT configuration data
            self.mqtt_config = {
                "config_messages": config_messages,
                "status_messages": status_messages,
                "topics_messages": topics_messages,
                "total_messages": len(config_messages) + len(status_messages) + len(topics_messages)
            }
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der MQTT-Konfiguration: {e}")

def show_aps_configuration_mqtt():
    """Zeigt MQTT-Konfiguration an"""
    st.subheader("📡 MQTT Config")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_configuration_mqtt_manager" not in st.session_state:
        st.session_state["aps_configuration_mqtt_manager"] = APSConfigurationMQTTManager()
    
    manager = st.session_state["aps_configuration_mqtt_manager"]
    
    # Update MQTT configuration from MQTT
    manager.update_from_mqtt_client(client)
    
    # Display MQTT metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Config Messages", len(manager.mqtt_config.get("config_messages", [])))
    
    with col2:
        st.metric("Status Messages", len(manager.mqtt_config.get("status_messages", [])))
    
    with col3:
        st.metric("Total Messages", manager.mqtt_config.get("total_messages", 0))
    
    # Show config messages
    if manager.mqtt_config.get("config_messages"):
        st.write("**MQTT Configuration**")
        for msg in manager.mqtt_config["config_messages"][:3]:
            with st.expander(f"Config: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Show status messages
    if manager.mqtt_config.get("status_messages"):
        st.write("**MQTT Status**")
        for msg in manager.mqtt_config["status_messages"][:3]:
            with st.expander(f"Status: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Show topics messages
    if manager.mqtt_config.get("topics_messages"):
        st.write("**MQTT Topics**")
        for msg in manager.mqtt_config["topics_messages"][:3]:
            with st.expander(f"Topics: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Auto-refresh info
    st.info("💡 **MQTT-Konfiguration wird automatisch aus MQTT-Nachrichten aktualisiert**")
