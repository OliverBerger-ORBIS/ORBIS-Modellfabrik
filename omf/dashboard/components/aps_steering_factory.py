"""
APS Steering - Factory
Zeigt Factory Steering für die APS an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

class APSSteeringFactoryManager:
    """Manager für APS Factory Steering"""
    
    def __init__(self):
        self.factory_commands = []
        self.last_update = None
    
    def send_factory_command(self, mqtt_client, command, payload=None):
        """Sendet einen Factory Command"""
        try:
            if payload is None:
                payload = {}
            result = mqtt_client.publish(command, payload, qos=1, retain=False)
            return result
            
        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Factory Commands: {e}")
            return False

def show_aps_steering_factory():
    """Zeigt Factory Steering an"""
    st.subheader("🏭 Factory Steering")
    
    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Initialize manager in session state
    if "aps_steering_factory_manager" not in st.session_state:
        st.session_state["aps_steering_factory_manager"] = APSSteeringFactoryManager()
    
    manager = st.session_state["aps_steering_factory_manager"]
    
    # Factory Control
    st.write("**Factory Control**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("💡 Factory Commands sind in APS Overview verfügbar")
    
    with col2:
        st.info("💡 Weitere Factory Commands sind in APS Overview verfügbar")
        
        if st.button("📊 Factory Status", key="asf_factory_status"):
            result = manager.send_factory_command(client, "ccu/get/status")
            if result:
                st.success("✅ Factory Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")
        
        if st.button("🧹 Factory Clean", key="asf_factory_clean"):
            result = manager.send_factory_command(client, "ccu/set/clean")
            if result:
                st.success("✅ Factory Clean gesendet")
            else:
                st.error("❌ Fehler beim Senden")
    
    # Factory Settings
    st.write("**Factory Settings**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⚙️ Factory Settings", key="asf_factory_settings"):
            result = manager.send_factory_command(client, "ccu/get/settings")
            if result:
                st.success("✅ Factory Settings gesendet")
            else:
                st.error("❌ Fehler beim Senden")
        
        if st.button("🔧 Factory Config", key="asf_factory_config"):
            result = manager.send_factory_command(client, "ccu/get/config")
            if result:
                st.success("✅ Factory Config gesendet")
            else:
                st.error("❌ Fehler beim Senden")
    
    with col2:
        if st.button("📋 Factory Info", key="asf_factory_info"):
            result = manager.send_factory_command(client, "ccu/get/info")
            if result:
                st.success("✅ Factory Info gesendet")
            else:
                st.error("❌ Fehler beim Senden")
        
        if st.button("🔍 Factory Debug", key="asf_factory_debug"):
            result = manager.send_factory_command(client, "ccu/debug/info")
            if result:
                st.success("✅ Factory Debug gesendet")
            else:
                st.error("❌ Fehler beim Senden")
