"""
APS System Control - Debug Tools
Zeigt Debug Tools für die APS an
"""

import streamlit as st


class APSSystemControlDebugManager:
    """Manager für APS System Control Debug Tools"""

    def __init__(self):
        self.debug_data = {}
        self.last_update = None

    def send_debug_command(self, mqtt_client, command, payload=None):
        """Sendet einen Debug Command"""
        try:
            if payload is None:
                payload = {}
            result = mqtt_client.publish(command, payload, qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Debug Commands: {e}")
            return False


def show_aps_system_control_debug():
    """Zeigt Debug Tools an"""
    st.subheader("🔧 Debug Tools")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_system_control_debug_manager" not in st.session_state:
        st.session_state["aps_system_control_debug_manager"] = APSSystemControlDebugManager()

    manager = st.session_state["aps_system_control_debug_manager"]

    # Debug Commands
    st.write("**Debug Commands**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 System Info"):
            result = manager.send_debug_command(client, "ccu/debug/info")
            if result:
                st.success("✅ System Info gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📊 System Stats"):
            result = manager.send_debug_command(client, "ccu/debug/stats")
            if result:
                st.success("✅ System Stats gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔄 System Restart"):
            result = manager.send_debug_command(client, "ccu/debug/restart")
            if result:
                st.success("✅ System Restart gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("🧹 Clear Logs"):
            result = manager.send_debug_command(client, "ccu/debug/clearLogs")
            if result:
                st.success("✅ Clear Logs gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📋 Module List"):
            result = manager.send_debug_command(client, "ccu/debug/moduleList")
            if result:
                st.success("✅ Module List gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔧 System Test"):
            result = manager.send_debug_command(client, "ccu/debug/systemTest")
            if result:
                st.success("✅ System Test gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # Custom Debug Command
    st.write("**Custom Debug Command**")
    col1, col2 = st.columns(2)

    with col1:
        debug_command = st.text_input("Debug Command", key="debug_command")

    with col2:
        debug_payload = st.text_input("Debug Payload (JSON)", key="debug_payload")

    if st.button("🚀 Send Custom Debug Command"):
        if debug_command:
            result = manager.send_debug_command(client, debug_command, debug_payload if debug_payload else "{}")
            if result:
                st.success(f"✅ Custom Debug Command gesendet: {debug_command}")
            else:
                st.error("❌ Fehler beim Senden des Custom Debug Commands")
        else:
            st.error("❌ Debug Command ist erforderlich")

    # Debug Information
    st.write("**Debug Information**")
    show_debug = st.checkbox("Debug Information anzeigen")

    if show_debug:
        st.write("**Debug Information:**")
        st.json(
            {
                "status": "APS System Control Debug aktiviert",
                "manager": "APSSystemControlDebugManager",
                "mqtt_client": "verfügbar" if client else "nicht verfügbar",
            }
        )
