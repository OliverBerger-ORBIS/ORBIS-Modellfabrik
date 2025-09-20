"""
APS Configuration - System
Zeigt System-Konfiguration für die APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSConfigurationSystemManager:
    """Manager für APS System Configuration"""
    
    def __init__(self):
        self.system_config = {}
        self.last_update = None
    
    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die System-Konfiguration basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to system configuration topics
            mqtt_client.subscribe_many([
                "ccu/config",
                "ccu/config/system",
                "ccu/config/modules"
            ])
            
            # Get messages from buffer
            config_messages = list(mqtt_client.get_buffer("ccu/config"))
            system_config_messages = list(mqtt_client.get_buffer("ccu/config/system"))
            modules_config_messages = list(mqtt_client.get_buffer("ccu/config/modules"))
            
            # Process system configuration data
            self.system_config = {
                "config_messages": config_messages,
                "system_config_messages": system_config_messages,
                "modules_config_messages": modules_config_messages,
                "total_messages": len(config_messages) + len(system_config_messages) + len(modules_config_messages)
            }
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der System-Konfiguration: {e}")

def show_aps_configuration_system():
    """Zeigt System-Konfiguration an"""
    st.subheader("🔧 System Config")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_configuration_system_manager" not in st.session_state:
        st.session_state["aps_configuration_system_manager"] = APSConfigurationSystemManager()
    
    manager = st.session_state["aps_configuration_system_manager"]
    
    # Update system configuration from MQTT
    manager.update_from_mqtt_client(client)
    
    # Display system metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Config Messages", len(manager.system_config.get("config_messages", [])))
    
    with col2:
        st.metric("System Config", len(manager.system_config.get("system_config_messages", [])))
    
    with col3:
        st.metric("Total Messages", manager.system_config.get("total_messages", 0))
    
    # Show config messages
    if manager.system_config.get("config_messages"):
        st.write("**System Configuration**")
        for msg in manager.system_config["config_messages"][:3]:
            with st.expander(f"Config: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Show system config messages
    if manager.system_config.get("system_config_messages"):
        st.write("**System Config Messages**")
        for msg in manager.system_config["system_config_messages"][:3]:
            with st.expander(f"System Config: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Show modules config messages
    if manager.system_config.get("modules_config_messages"):
        st.write("**Modules Configuration**")
        for msg in manager.system_config["modules_config_messages"][:3]:
            with st.expander(f"Modules Config: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Auto-refresh info
    st.info("💡 **System-Konfiguration wird automatisch aus MQTT-Nachrichten aktualisiert**")
