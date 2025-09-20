"""
APS Overview - Controllers
Zeigt die APS Controller an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSControllersManager:
    """Manager für APS Controller"""
    
    def __init__(self):
        self.controllers = {}
        self.messages = []
        self.last_update = None
    
    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die Controller basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to APS controller topics
            mqtt_client.subscribe_many([
                "module/v1/ff/+/state",
                "module/v1/ff/+/connection", 
                "ccu/pairing/state",
                "module/v1/ff/+/factsheet"
            ])
            
            # Get messages from buffer
            state_messages = list(mqtt_client.get_buffer("module/v1/ff/+/state"))
            connection_messages = list(mqtt_client.get_buffer("module/v1/ff/+/connection"))
            pairing_messages = list(mqtt_client.get_buffer("ccu/pairing/state"))
            factsheet_messages = list(mqtt_client.get_buffer("module/v1/ff/+/factsheet"))
            
            self.messages = state_messages + connection_messages + pairing_messages + factsheet_messages
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der APS-Controller: {e}")

def show_aps_controllers():
    """Zeigt die APS Controller an"""
    st.subheader("🎮 Controllers")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_controllers_manager" not in st.session_state:
        st.session_state["aps_controllers_manager"] = APSControllersManager()
    
    manager = st.session_state["aps_controllers_manager"]
    
    # Update controllers from MQTT
    manager.update_from_mqtt_client(client)
    
    if manager.messages:
        st.success(f"✅ {len(manager.messages)} APS-Nachrichten empfangen")
        
        # Show first few messages as example
        for i, msg in enumerate(manager.messages[:3]):
            with st.expander(f"📨 Message {i+1}: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    else:
        st.warning("⚠️ Keine APS-Nachrichten empfangen")
    
    # Auto-refresh info
    st.info("💡 **Controller werden automatisch aus MQTT-Nachrichten aktualisiert**")
