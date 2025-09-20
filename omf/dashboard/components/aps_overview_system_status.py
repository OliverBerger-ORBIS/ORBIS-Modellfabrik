"""
APS Overview - System Status
Zeigt den System-Status der APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh


class APSSystemStatusManager:
    """Manager für APS System Status"""

    def __init__(self):
        self.controllers = {}
        self.total_messages = 0
        self.last_update = None

    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert den Status basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to APS topics
            mqtt_client.subscribe_many(
                ["module/v1/ff/+/state", "module/v1/ff/+/connection", "ccu/pairing/state", "module/v1/ff/+/factsheet"]
            )

            # Get message counts
            state_messages = list(mqtt_client.get_buffer("module/v1/ff/+/state"))
            connection_messages = list(mqtt_client.get_buffer("module/v1/ff/+/connection"))
            pairing_messages = list(mqtt_client.get_buffer("ccu/pairing/state"))
            factsheet_messages = list(mqtt_client.get_buffer("module/v1/ff/+/factsheet"))

            self.total_messages = (
                len(state_messages) + len(connection_messages) + len(pairing_messages) + len(factsheet_messages)
            )
            self.controllers = len(
                set(
                    [
                        msg.get('topic', '').split('/')[3]
                        for msg in state_messages + connection_messages
                        if '/ff/' in msg.get('topic', '')
                    ]
                )
            )

        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der APS-Status: {e}")


def show_aps_system_status():
    """Zeigt den APS System Status an"""
    st.subheader("📊 System Status")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_system_status_manager" not in st.session_state:
        st.session_state["aps_system_status_manager"] = APSSystemStatusManager()

    manager = st.session_state["aps_system_status_manager"]

    # Update status from MQTT
    manager.update_from_mqtt_client(client)

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Controllers", manager.controllers)

    with col2:
        st.metric("Messages", manager.total_messages)

    with col3:
        status = "🟢 Active" if manager.total_messages > 0 else "🔴 Inactive"
        st.metric("Status", status)

    # Auto-refresh info
    st.info("💡 **Status wird automatisch aus MQTT-Nachrichten aktualisiert**")
