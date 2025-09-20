"""
APS System Control - Status
Zeigt den System Status der APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSSystemControlStatusManager:
    """Manager für APS System Control Status"""
    
    def __init__(self):
        self.status = {}
        self.last_update = None
    
    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert den Status basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to system status topics
            mqtt_client.subscribe_many([
                "ccu/status",
                "ccu/pairing/state",
                "module/v1/ff/+/state",
                "module/v1/ff/+/connection"
            ])
            
            # Get messages from buffer
            ccu_status = list(mqtt_client.get_buffer("ccu/status"))
            pairing_state = list(mqtt_client.get_buffer("ccu/pairing/state"))
            module_states = list(mqtt_client.get_buffer("module/v1/ff/+/state"))
            module_connections = list(mqtt_client.get_buffer("module/v1/ff/+/connection"))
            
            # Process status data
            self.status = {
                "ccu_status": ccu_status,
                "pairing_state": pairing_state,
                "module_states": module_states,
                "module_connections": module_connections,
                "total_messages": len(ccu_status) + len(pairing_state) + len(module_states) + len(module_connections)
            }
            
        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden des System Status: {e}")

def show_aps_system_control_status():
    """Zeigt den System Status an"""
    st.subheader("📊 System Status")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_system_control_status_manager" not in st.session_state:
        st.session_state["aps_system_control_status_manager"] = APSSystemControlStatusManager()
    
    manager = st.session_state["aps_system_control_status_manager"]
    
    # Update status from MQTT
    manager.update_from_mqtt_client(client)
    
    # Display status metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("CCU Status", len(manager.status.get("ccu_status", [])))
    
    with col2:
        st.metric("Pairing State", len(manager.status.get("pairing_state", [])))
    
    with col3:
        st.metric("Module States", len(manager.status.get("module_states", [])))
    
    with col4:
        st.metric("Total Messages", manager.status.get("total_messages", 0))
    
    # Show detailed status
    if manager.status.get("ccu_status"):
        st.write("**CCU Status**")
        for msg in manager.status["ccu_status"][:3]:
            with st.expander(f"CCU Status: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    if manager.status.get("pairing_state"):
        st.write("**Pairing State**")
        for msg in manager.status["pairing_state"][:3]:
            with st.expander(f"Pairing: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)
    
    # Auto-refresh info
    st.info("💡 **System Status wird automatisch aus MQTT-Nachrichten aktualisiert**")
