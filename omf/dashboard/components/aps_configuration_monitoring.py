"""
APS Configuration - Monitoring
Zeigt Monitoring-Konfiguration für die APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh


class APSConfigurationMonitoringManager:
    """Manager für APS Monitoring Configuration"""

    def __init__(self):
        self.monitoring_config = {}
        self.last_update = None

    def update_from_mqtt_client(self, mqtt_client):
        """Aktualisiert die Monitoring-Konfiguration basierend auf MQTT-Nachrichten"""
        try:
            # Subscribe to monitoring configuration topics
            mqtt_client.subscribe_many(["ccu/monitoring/config", "ccu/monitoring/status", "ccu/monitoring/alerts"])

            # Get messages from buffer
            config_messages = list(mqtt_client.get_buffer("ccu/monitoring/config"))
            status_messages = list(mqtt_client.get_buffer("ccu/monitoring/status"))
            alerts_messages = list(mqtt_client.get_buffer("ccu/monitoring/alerts"))

            # Process monitoring configuration data
            self.monitoring_config = {
                "config_messages": config_messages,
                "status_messages": status_messages,
                "alerts_messages": alerts_messages,
                "total_messages": len(config_messages) + len(status_messages) + len(alerts_messages),
            }

        except Exception as e:
            st.warning(f"⚠️ Fehler beim Laden der Monitoring-Konfiguration: {e}")


def show_aps_configuration_monitoring():
    """Zeigt Monitoring-Konfiguration an"""
    st.subheader("📊 Monitoring Config")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_configuration_monitoring_manager" not in st.session_state:
        st.session_state["aps_configuration_monitoring_manager"] = APSConfigurationMonitoringManager()

    manager = st.session_state["aps_configuration_monitoring_manager"]

    # Update monitoring configuration from MQTT
    manager.update_from_mqtt_client(client)

    # Display monitoring metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Config Messages", len(manager.monitoring_config.get("config_messages", [])))

    with col2:
        st.metric("Status Messages", len(manager.monitoring_config.get("status_messages", [])))

    with col3:
        st.metric("Total Messages", manager.monitoring_config.get("total_messages", 0))

    # Show config messages
    if manager.monitoring_config.get("config_messages"):
        st.write("**Monitoring Configuration**")
        for msg in manager.monitoring_config["config_messages"][:3]:
            with st.expander(f"Config: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)

    # Show status messages
    if manager.monitoring_config.get("status_messages"):
        st.write("**Monitoring Status**")
        for msg in manager.monitoring_config["status_messages"][:3]:
            with st.expander(f"Status: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)

    # Show alerts messages
    if manager.monitoring_config.get("alerts_messages"):
        st.write("**Monitoring Alerts**")
        for msg in manager.monitoring_config["alerts_messages"][:3]:
            with st.expander(f"Alert: {msg.get('topic', 'Unknown')}", expanded=False):
                st.json(msg)

    # Auto-refresh info
    st.info("💡 **Monitoring-Konfiguration wird automatisch aus MQTT-Nachrichten aktualisiert**")
