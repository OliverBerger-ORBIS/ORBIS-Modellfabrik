"""
APS Overview - Commands
Zeigt APS System Commands an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSCommandsManager:
    """Manager für APS System Commands"""
    
    def __init__(self):
        self.commands = []
        self.last_update = None
    
    def send_system_command(self, mqtt_client, command, payload=None):
        """Sendet einen System Command über Singleton MQTT-Client"""
        try:
            if payload is None:
                payload = {}
            result = mqtt_client.publish(command, payload, qos=1, retain=False)
            return result
            
        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Commands: {e}")
            return False
    
    def send_instant_action(self, mqtt_client, module, action):
        """Sendet eine Instant Action über Singleton MQTT-Client"""
        try:
            topic = f"{module.lower()}/instantAction"
            payload = {"action": action}
            result = mqtt_client.publish(topic, payload, qos=1, retain=False)
            return result
            
        except Exception as e:
            st.error(f"❌ Fehler beim Senden der Instant Action: {e}")
            return False

def show_aps_commands():
    """Zeigt APS System Commands an"""
    st.subheader("⚡ System Commands")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_commands_manager" not in st.session_state:
        st.session_state["aps_commands_manager"] = APSCommandsManager()
    
    manager = st.session_state["aps_commands_manager"]
    
    # System Commands
    st.write("**System Commands**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Factory Reset", key="aoc_factory_reset"):
            result = manager.send_system_command(client, "ccu/set/factoryReset")
            if result:
                st.success("✅ Factory Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")
        
        if st.button("🔋 FTS Charge", key="aoc_fts_charge"):
            result = manager.send_system_command(client, "ccu/set/charge")
            if result:
                st.success("✅ FTS Charge gesendet")
            else:
                st.error("❌ Fehler beim Senden")
    
    with col2:
        if st.button("🅿️ Park Factory", key="aoc_park_factory"):
            result = manager.send_system_command(client, "ccu/set/park")
            if result:
                st.success("✅ Park Factory gesendet")
            else:
                st.error("❌ Fehler beim Senden")
        
        if st.button("🔧 System Calibration", key="aoc_system_calibration"):
            result = manager.send_system_command(client, "ccu/set/calibration")
            if result:
                st.success("✅ System Calibration gesendet")
            else:
                st.error("❌ Fehler beim Senden")
    
    # AIQS Calibration
    st.write("**AIQS Calibration**")
    if st.button("🔍 AIQS Calibration", key="aoc_aiqs_calibration"):
        result = manager.send_instant_action(client, "aiqs", "calibration")
        if result:
            st.success("✅ AIQS Calibration gesendet")
        else:
            st.error("❌ Fehler beim Senden")
    
    # Debug Information
    show_debug = st.checkbox("Debug Information anzeigen", key="aoc_debug_info")
    
    if show_debug:
        st.write("**Debug Information:**")
        st.json({"status": "APS Integration aktiviert", "manager": "APSCommandsManager"})
