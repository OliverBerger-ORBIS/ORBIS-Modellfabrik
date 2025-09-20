"""
APS Orders - VDA5050 Orders
Zeigt VDA5050-kompatible Orders an
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh


class APSVDA5050OrdersManager:
    """Manager für VDA5050 Orders"""

    def __init__(self):
        self.orders = []
        self.last_update = None

    def create_storage_order(self, mqtt_client, load_type, target_module, workpiece_id=None):
        """Erstellt eine Storage Order"""
        try:
            order_payload = {
                "orderType": "STORAGE",
                "loadType": load_type,
                "targetModule": target_module,
                "workpieceId": workpiece_id if workpiece_id else None,
            }

            result = mqtt_client.publish("ccu/order/request", str(order_payload), qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Erstellen der Storage Order: {e}")
            return False

    def create_retrieval_order(self, mqtt_client, load_type, target_module, workpiece_id=None):
        """Erstellt eine Retrieval Order"""
        try:
            order_payload = {
                "orderType": "RETRIEVAL",
                "loadType": load_type,
                "targetModule": target_module,
                "workpieceId": workpiece_id if workpiece_id else None,
            }

            result = mqtt_client.publish("ccu/order/request", str(order_payload), qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Erstellen der Retrieval Order: {e}")
            return False


def show_aps_orders_vda5050():
    """Zeigt VDA5050 Orders an"""
    st.subheader("📋 VDA5050 Orders")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_vda5050_orders_manager" not in st.session_state:
        st.session_state["aps_vda5050_orders_manager"] = APSVDA5050OrdersManager()

    manager = st.session_state["aps_vda5050_orders_manager"]

    # Order Creation
    st.write("**Create VDA5050 Order**")

    col1, col2 = st.columns(2)

    with col1:
        order_type = st.selectbox("Order Type", ["STORAGE", "RETRIEVAL"], key="vda5050_order_type")
        load_type = st.selectbox("Load Type", ["RED", "BLUE", "WHITE"], key="vda5050_load_type")

    with col2:
        target_module = st.selectbox("Target Module", ["DPS", "HBW", "AIQS"], key="vda5050_target_module")

    workpiece_id = st.text_input("Workpiece ID (optional)", key="vda5050_workpiece_id")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📦 Create Storage Order", key="aov_storage_order"):
            result = manager.create_storage_order(client, load_type, target_module, workpiece_id)
            if result:
                st.success(f"✅ Storage Order erstellt: {load_type} -> {target_module}")
            else:
                st.error("❌ Fehler beim Erstellen der Storage Order")

    with col2:
        if st.button("📤 Create Retrieval Order", key="aov_retrieval_order"):
            result = manager.create_retrieval_order(client, load_type, target_module, workpiece_id)
            if result:
                st.success(f"✅ Retrieval Order erstellt: {load_type} -> {target_module}")
            else:
                st.error("❌ Fehler beim Erstellen der Retrieval Order")

    # Order Templates
    st.write("**Quick Order Templates**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔴 RED Storage", key="aov_red_storage"):
            result = manager.create_storage_order(client, "RED", "DPS")
            if result:
                st.success("✅ RED Storage Order erstellt")

    with col2:
        if st.button("🔵 BLUE Storage", key="aov_blue_storage"):
            result = manager.create_storage_order(client, "BLUE", "DPS")
            if result:
                st.success("✅ BLUE Storage Order erstellt")

    with col3:
        if st.button("⚪ WHITE Storage", key="aov_white_storage"):
            result = manager.create_storage_order(client, "WHITE", "DPS")
            if result:
                st.success("✅ WHITE Storage Order erstellt")
