"""
APS Configuration - Controllers
Zeigt Controller-Konfiguration für die APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSConfigurationControllersManager:
    """Manager für APS Controller Configuration"""
    
    def __init__(self):
        self.controllers = {}
        self.last_update = None
    
    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die Controller-Konfiguration basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to controller configuration topics
            mqtt_client.subscribe_many([
                "module/v1/ff/+/factsheet",
                "module/v1/ff/+/state",
                "ccu/pairing/state"
            ])
            
            # Get messages from buffer
            factsheet_messages = list(mqtt_client.get_buffer("module/v1/ff/+/factsheet"))
            state_messages = list(mqtt_client.get_buffer("module/v1/ff/+/state"))
            pairing_messages = list(mqtt_client.get_buffer("ccu/pairing/state"))
            
            # Process controller data
            self.controllers = {
                "factsheet_messages": factsheet_messages,
                "state_messages": state_messages,
                "pairing_messages": pairing_messages,
                "total_messages": len(factsheet_messages) + len(state_messages) + len(pairing_messages)
            }
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der Controller-Konfiguration: {e}")

def show_aps_configuration_controllers():
    """Zeigt Controller-Konfiguration an"""
    st.subheader("🎮 Controller Config")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_configuration_controllers_manager" not in st.session_state:
        st.session_state["aps_configuration_controllers_manager"] = APSConfigurationControllersManager()
    
    manager = st.session_state["aps_configuration_controllers_manager"]
    
    # Update controller configuration from MQTT
    manager.update_from_mqtt_client(client)
    
    # Display controller metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Factsheet Messages", len(manager.controllers.get("factsheet_messages", [])))
    
    with col2:
        st.metric("State Messages", len(manager.controllers.get("state_messages", [])))
    
    with col3:
        st.metric("Total Messages", manager.controllers.get("total_messages", 0))
    
    # Show factsheet messages
    if manager.controllers.get("factsheet_messages"):
        st.write("**Controller Factsheets**")
        for msg in manager.controllers["factsheet_messages"][:3]:
            with st.expander(f"Factsheet: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Show state messages
    if manager.controllers.get("state_messages"):
        st.write("**Controller States**")
        for msg in manager.controllers["state_messages"][:3]:
            with st.expander(f"State: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Show pairing messages
    if manager.controllers.get("pairing_messages"):
        st.write("**Pairing State**")
        for msg in manager.controllers["pairing_messages"][:3]:
            with st.expander(f"Pairing: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Auto-refresh info
    st.info("💡 **Controller-Konfiguration wird automatisch aus MQTT-Nachrichten aktualisiert**")
