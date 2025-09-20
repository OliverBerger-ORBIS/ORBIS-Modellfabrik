"""
APS Overview - Orders
Zeigt APS Orders und Bestellungen an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh


class APSOrdersManager:
    """Manager für APS Orders"""

    def __init__(self):
        self.orders = []
        self.last_update = None

    def create_order(self, mqtt_client, order_type, load_type, target_module, workpiece_id=None):
        """Erstellt eine neue Order"""
        try:
            # Create order payload
            order_payload = {
                "orderType": order_type,
                "loadType": load_type,
                "targetModule": target_module,
                "workpieceId": workpiece_id if workpiece_id else None,
            }

            # Send order request
            result = mqtt_client.publish("ccu/order/request", order_payload, qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Erstellen der Order: {e}")
            return False

    def send_instant_action(self, mqtt_client, module, action):
        """Sendet eine Instant Action"""
        try:
            topic = f"{module.lower()}/instantAction"
            payload = {"action": action}
            result = mqtt_client.publish(topic, payload, qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Senden der Instant Action: {e}")
            return False


def show_aps_orders():
    """Zeigt APS Orders an"""
    st.subheader("📋 Orders")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_orders_manager" not in st.session_state:
        st.session_state["aps_orders_manager"] = APSOrdersManager()

    manager = st.session_state["aps_orders_manager"]

    # Order Creation
    st.write("**Create Order**")

    col1, col2 = st.columns(2)

    with col1:
        color = st.selectbox("Farbe", ["RED", "BLUE", "WHITE"], key="aoo_color")
        order_type = st.selectbox("Order Type", ["STORAGE", "RETRIEVAL"], key="aoo_order_type")

    with col2:
        target_module = st.selectbox("Target Module", ["DPS", "HBW", "AIQS"], key="aoo_target_module")

    workpiece_id = st.text_input("Workpiece ID (optional)", key="aoo_workpiece_id")

    if st.button("📋 Order erstellen", key="aoo_create_order"):
        result = manager.create_order(client, order_type, color, target_module, workpiece_id)
        if result:
            st.success(f"✅ Order erstellt: {color} {order_type} -> {target_module}")
        else:
            st.error("❌ Fehler beim Erstellen der Order")

    # Camera Controls
    st.write("**Camera Controls**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📷 Camera Up", key="aoo_camera_up"):
            result = manager.send_instant_action(client, "dps", "cameraUp")
            if result:
                st.success("✅ Camera Up gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📷 Camera Down", key="aoo_camera_down"):
            result = manager.send_instant_action(client, "dps", "cameraDown")
            if result:
                st.success("✅ Camera Down gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("📷 Camera Left", key="aoo_camera_left"):
            result = manager.send_instant_action(client, "dps", "cameraLeft")
            if result:
                st.success("✅ Camera Left gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📷 Camera Right", key="aoo_camera_right"):
            result = manager.send_instant_action(client, "dps", "cameraRight")
            if result:
                st.success("✅ Camera Right gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # NFC Controls
    st.write("**NFC Controls**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📖 NFC Read", key="aoo_nfc_read"):
            result = manager.send_instant_action(client, "dps", "nfcRead")
            if result:
                st.success("✅ NFC Read gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("🗑️ NFC Clear", key="aoo_nfc_clear"):
            result = manager.send_instant_action(client, "dps", "nfcClear")
            if result:
                st.success("✅ NFC Clear gesendet")
            else:
                st.error("❌ Fehler beim Senden")
