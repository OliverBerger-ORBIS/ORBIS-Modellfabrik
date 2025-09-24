"""
APS System Control - Monitor
Zeigt System Monitoring für die APS an
"""

import streamlit as st


class APSSystemControlMonitorManager:
    """Manager für APS System Control Monitor"""

    def __init__(self):
        self.monitor_data = {}
        self.last_update = None

    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die Monitor-Daten basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to monitoring topics
            mqtt_client.subscribe_many(
                ["module/v1/ff/+/state", "module/v1/ff/+/connection", "ccu/pairing/state", "ccu/status"]
            )

            # Get messages from buffer
            module_states = list(mqtt_client.get_buffer("module/v1/ff/+/state"))
            module_connections = list(mqtt_client.get_buffer("module/v1/ff/+/connection"))
            pairing_state = list(mqtt_client.get_buffer("ccu/pairing/state"))
            ccu_status = list(mqtt_client.get_buffer("ccu/status"))

            # Process monitor data
            self.monitor_data = {
                "module_states": module_states,
                "module_connections": module_connections,
                "pairing_state": pairing_state,
                "ccu_status": ccu_status,
                "total_messages": len(module_states) + len(module_connections) + len(pairing_state) + len(ccu_status),
            }

        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der Monitor-Daten: {e}")


def show_wl_system_control_monitor():
    """Zeigt System Monitoring an"""
    st.subheader("📈 System Monitor")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_system_control_monitor_manager" not in st.session_state:
        st.session_state["aps_system_control_monitor_manager"] = APSSystemControlMonitorManager()

    manager = st.session_state["aps_system_control_monitor_manager"]

    # Update monitor data from MQTT
    manager.update_from_mqtt_client(client)

    # Display monitor metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Module States", len(manager.monitor_data.get("module_states", [])))

    with col2:
        st.metric("Module Connections", len(manager.monitor_data.get("module_connections", [])))

    with col3:
        st.metric("Total Messages", manager.monitor_data.get("total_messages", 0))

    # Show module states
    if manager.monitor_data.get("module_states"):
        st.write("**Module States**")
        for msg in manager.monitor_data["module_states"][:5]:
            with st.expander(f"Module State: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)

    # Show module connections
    if manager.monitor_data.get("module_connections"):
        st.write("**Module Connections**")
        for msg in manager.monitor_data["module_connections"][:5]:
            with st.expander(f"Module Connection: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)

    # Show pairing state
    if manager.monitor_data.get("pairing_state"):
        st.write("**Pairing State**")
        for msg in manager.monitor_data["pairing_state"][:3]:
            with st.expander(f"Pairing State: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)

    # Auto-refresh info
    st.info("💡 **System Monitor wird automatisch aus MQTT-Nachrichten aktualisiert**")
