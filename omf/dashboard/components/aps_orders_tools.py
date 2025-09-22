"""
APS Orders - Order Tools
Zeigt Order Tools und Utilities an
"""

import streamlit as st


class APSOrderToolsManager:
    """Manager für Order Tools"""

    def __init__(self):
        self.tools = []
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


def show_aps_orders_tools():
    """Zeigt Order Tools an"""
    st.subheader("🔧 Order Tools")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_order_tools_manager" not in st.session_state:
        st.session_state["aps_order_tools_manager"] = APSOrderToolsManager()

    manager = st.session_state["aps_order_tools_manager"]

    # System Commands
    st.write("**System Commands**")
    col1, col2 = st.columns(2)

    with col1:
        st.info("💡 Factory Reset und FTS Charge sind in APS Overview verfügbar")

    with col2:
        if st.button("🅿️ FTS Park", key="aot_fts_park"):
            result = manager.send_system_command(client, "ccu/set/park")
            if result:
                st.success("✅ FTS Park gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔧 System Calibration", key="aot_system_calibration"):
            result = manager.send_system_command(client, "ccu/set/calibration")
            if result:
                st.success("✅ System Calibration gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # Order Management
    st.write("**Order Management**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏹️ Stop All Orders", key="aot_stop_orders"):
            result = manager.send_system_command(client, "ccu/order/stop")
            if result:
                st.success("✅ Stop All Orders gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔄 Reset Orders", key="aot_reset_orders"):
            result = manager.send_system_command(client, "ccu/order/reset")
            if result:
                st.success("✅ Reset Orders gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("📊 Order Status", key="aot_order_status"):
            result = manager.send_system_command(client, "ccu/order/status")
            if result:
                st.success("✅ Order Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🧹 Clear Order Queue", key="aot_clear_queue"):
            result = manager.send_system_command(client, "ccu/order/clear")
            if result:
                st.success("✅ Clear Order Queue gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # Debug Information
    st.write("**Debug Information**")
    show_debug = st.checkbox("Debug Information anzeigen", key="aot_debug_info")

    if show_debug:
        st.write("**Debug Information:**")
        st.json(
            {
                "status": "APS Order Tools aktiviert",
                "manager": "APSOrderToolsManager",
                "mqtt_client": "verfügbar" if client else "nicht verfügbar",
            }
        )
