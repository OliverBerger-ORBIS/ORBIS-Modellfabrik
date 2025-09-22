"""
APS Steering - FTS
Zeigt FTS Steering für die APS an
"""

import streamlit as st


class APSSteeringFTSManager:
    """Manager für APS FTS Steering"""

    def __init__(self):
        self.fts_commands = []
        self.last_update = None

    def send_fts_command(self, mqtt_client, command, payload=None):
        """Sendet einen FTS Command nach APS-Standard"""
        try:
            if payload is None:
                payload = {}
            
            # Logging für Analyse
            from omf.dashboard.tools.logging_config import get_logger
            logger = get_logger("omf.dashboard.components.aps_steering_fts")
            logger.info(f"🔍 APS FTS Command: Topic='{command}', Payload={payload}")
            
            # APS-Standard: Direkter MQTT Publish wie in Original APS Quellen
            # QoS=2, retain=True (Standard APS-Verhalten)
            result = mqtt_client.publish(command, payload, qos=2, retain=True)
            
            logger.info(f"📤 APS FTS Command gesendet: Result={result}")
            return result

        except Exception as e:
            from omf.dashboard.tools.logging_config import get_logger
            logger = get_logger("omf.dashboard.components.aps_steering_fts")
            logger.error(f"❌ Fehler beim Senden des FTS Commands: {e}")
            st.error(f"❌ Fehler beim Senden des FTS Commands: {e}")
            return False


def show_aps_steering_fts():
    """Zeigt FTS Steering an"""
    st.subheader("🚗 FTS Steering")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_steering_fts_manager" not in st.session_state:
        st.session_state["aps_steering_fts_manager"] = APSSteeringFTSManager()

    manager = st.session_state["aps_steering_fts_manager"]

    # FTS Control
    st.write("**FTS Control**")
    col1, col2 = st.columns(2)

    with col1:
        st.info("💡 FTS Commands sind in APS Overview verfügbar")

    with col2:
        st.info("💡 Weitere FTS Commands sind in APS Overview verfügbar")

        if st.button("📊 FTS Status", key="asfts_fts_status"):
            result = manager.send_fts_command(client, "ccu/get/ftsStatus")
            if result:
                st.success("✅ FTS Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔍 FTS Debug", key="asfts_fts_debug"):
            result = manager.send_fts_command(client, "ccu/debug/fts")
            if result:
                st.success("✅ FTS Debug gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # FTS Navigation
    st.write("**FTS Navigation**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 FTS Go to DPS", key="asfts_go_to_dps"):
            result = manager.send_fts_command(client, "ccu/set/ftsGoTo", {"target": "DPS"})
            if result:
                st.success("✅ FTS Go to DPS gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🎯 FTS Go to HBW", key="asfts_go_to_hbw"):
            result = manager.send_fts_command(client, "ccu/set/ftsGoTo", {"target": "HBW"})
            if result:
                st.success("✅ FTS Go to HBW gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("🎯 FTS Go to AIQS", key="asfts_go_to_aiqs"):
            result = manager.send_fts_command(client, "ccu/set/ftsGoTo", {"target": "AIQS"})
            if result:
                st.success("✅ FTS Go to AIQS gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🎯 FTS Go to CHRG", key="asfts_go_to_chrg"):
            result = manager.send_fts_command(client, "ccu/set/ftsGoTo", {"target": "CHRG"})
            if result:
                st.success("✅ FTS Go to CHRG gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # FTS Battery
    st.write("**FTS Battery**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔋 FTS Battery Status", key="asfts_battery_status"):
            result = manager.send_fts_command(client, "ccu/get/ftsBattery")
            if result:
                st.success("✅ FTS Battery Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("⚡ FTS Start Charging", key="asfts_start_charging"):
            result = manager.send_fts_command(client, "ccu/set/ftsStartCharging")
            if result:
                st.success("✅ FTS Start Charging gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("⏹️ FTS Stop Charging", key="asfts_stop_charging"):
            result = manager.send_fts_command(client, "ccu/set/ftsStopCharging")
            if result:
                st.success("✅ FTS Stop Charging gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔋 FTS Battery Info", key="asfts_battery_info"):
            result = manager.send_fts_command(client, "ccu/get/ftsBatteryInfo")
            if result:
                st.success("✅ FTS Battery Info gesendet")
            else:
                st.error("❌ Fehler beim Senden")
