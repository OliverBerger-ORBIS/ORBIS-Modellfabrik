"""
APS System Control - Commands
Zeigt System Commands für die APS an
"""

import streamlit as st


class APSSystemControlCommandsManager:
    """Manager für APS System Control Commands"""

    def __init__(self):
        self.commands = []
        self.last_update = None

    def send_system_command(self, mqtt_client, command, payload=None):
        """Sendet einen Command nach APS-Standard"""
        try:
            if payload is None:
                payload = {}
            
            # APS-Standard: Direkter MQTT Publish wie in Original APS Quellen
            # QoS=2, retain=True (Standard APS-Verhalten)
            result = mqtt_client.publish(command, payload, qos=2, retain=True)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Commands: {e}")
            return False


def show_aps_system_control_commands():
    """Zeigt System Commands an"""
    st.subheader("⚡ System Commands")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_system_control_commands_manager" not in st.session_state:
        st.session_state["aps_system_control_commands_manager"] = APSSystemControlCommandsManager()

    manager = st.session_state["aps_system_control_commands_manager"]

    # Factory Control
    st.write("**Factory Control**")
    st.info("💡 Factory Commands (Reset, Start, Stop, Calibration) sind in APS Overview verfügbar")

    # FTS Control
    st.write("**FTS Control**")
    st.info("💡 FTS Commands (Charge, Park, Move, Reset) sind in APS Overview verfügbar")

    # Module Control
    st.write("**Module Control**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 DPS Reset"):
            result = manager.send_system_command(client, "dps/set/reset")
            if result:
                st.success("✅ DPS Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔄 AIQS Reset"):
            result = manager.send_system_command(client, "aiqs/set/reset")
            if result:
                st.success("✅ AIQS Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("🔄 HBW Reset"):
            result = manager.send_system_command(client, "hbw/set/reset")
            if result:
                st.success("✅ HBW Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔄 MILL Reset"):
            result = manager.send_system_command(client, "mill/set/reset")
            if result:
                st.success("✅ MILL Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")
