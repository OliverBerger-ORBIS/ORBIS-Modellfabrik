"""
APS Steering - Orders
Zeigt Order Steering für die APS an
"""

import streamlit as st


class APSSteeringOrdersManager:
    """Manager für APS Order Steering"""

    def __init__(self):
        self.order_commands = []
        self.last_update = None

    def send_order_command(self, mqtt_client, command, payload=None):
        """Sendet einen Order Command"""
        try:
            if payload is None:
                payload = {}
            result = mqtt_client.publish(command, payload, qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Order Commands: {e}")
            return False


def show_aps_steering_orders():
    """Zeigt Order Steering an"""
    st.subheader("📋 Order Steering")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_steering_orders_manager" not in st.session_state:
        st.session_state["aps_steering_orders_manager"] = APSSteeringOrdersManager()

    manager = st.session_state["aps_steering_orders_manager"]

    # Order Control
    st.write("**Order Control**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏹️ Stop All Orders", key="aso_stop_all_orders"):
            result = manager.send_order_command(client, "ccu/order/stop")
            if result:
                st.success("✅ Stop All Orders gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔄 Reset Orders", key="aso_reset_orders"):
            result = manager.send_order_command(client, "ccu/order/reset")
            if result:
                st.success("✅ Reset Orders gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📊 Order Status", key="aso_order_status"):
            result = manager.send_order_command(client, "ccu/order/status")
            if result:
                st.success("✅ Order Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("🧹 Clear Order Queue", key="aso_clear_order_queue"):
            result = manager.send_order_command(client, "ccu/order/clear")
            if result:
                st.success("✅ Clear Order Queue gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📋 Order List", key="aso_order_list"):
            result = manager.send_order_command(client, "ccu/order/list")
            if result:
                st.success("✅ Order List gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔍 Order Debug", key="aso_order_debug"):
            result = manager.send_order_command(client, "ccu/order/debug")
            if result:
                st.success("✅ Order Debug gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # Order Management
    st.write("**Order Management**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📦 Create Storage Order", key="aso_create_storage_order"):
            order_payload = {"orderType": "STORAGE", "loadType": "RED", "targetModule": "DPS"}
            result = manager.send_order_command(client, "ccu/order/request", order_payload)
            if result:
                st.success("✅ Create Storage Order gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📤 Create Retrieval Order", key="aso_create_retrieval_order"):
            order_payload = {"orderType": "RETRIEVAL", "loadType": "RED", "targetModule": "DPS"}
            result = manager.send_order_command(client, "ccu/order/request", order_payload)
            if result:
                st.success("✅ Create Retrieval Order gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("⏸️ Pause Orders", key="aso_pause_orders"):
            result = manager.send_order_command(client, "ccu/order/pause")
            if result:
                st.success("✅ Pause Orders gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("▶️ Resume Orders", key="aso_resume_orders"):
            result = manager.send_order_command(client, "ccu/order/resume")
            if result:
                st.success("✅ Resume Orders gesendet")
            else:
                st.error("❌ Fehler beim Senden")
