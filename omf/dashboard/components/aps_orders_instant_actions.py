"""
APS Orders - Instant Actions
Zeigt Instant Actions für APS Module an
"""

import streamlit as st


class APSInstantActionsManager:
    """Manager für Instant Actions"""

    def __init__(self):
        self.actions = []
        self.last_update = None

    def send_instant_action(self, mqtt_client, module, action, parameters=None):
        """Sendet eine Instant Action"""
        try:
            topic = f"{module.lower()}/instantAction"

            if parameters:
                payload = f'{{"action": "{action}", "parameters": {parameters}}}'
            else:
                payload = f'{{"action": "{action}"}}'

            result = mqtt_client.publish(topic, payload, qos=2, retain=True)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Senden der Instant Action: {e}")
            return False


def show_aps_orders_instant_actions():
    """Zeigt Instant Actions an"""
    st.subheader("⚡ Instant Actions")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_instant_actions_manager" not in st.session_state:
        st.session_state["aps_instant_actions_manager"] = APSInstantActionsManager()

    manager = st.session_state["aps_instant_actions_manager"]

    # DPS Instant Actions
    st.write("**DPS Instant Actions**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📷 Camera Up", key="aoia_camera_up"):
            result = manager.send_instant_action(client, "dps", "cameraUp")
            if result:
                st.success("✅ Camera Up gesendet")

        if st.button("📷 Camera Down", key="aoia_camera_down"):
            result = manager.send_instant_action(client, "dps", "cameraDown")
            if result:
                st.success("✅ Camera Down gesendet")

        if st.button("📷 Camera Left", key="aoia_camera_left"):
            result = manager.send_instant_action(client, "dps", "cameraLeft")
            if result:
                st.success("✅ Camera Left gesendet")

        if st.button("📷 Camera Right", key="aoia_camera_right"):
            result = manager.send_instant_action(client, "dps", "cameraRight")
            if result:
                st.success("✅ Camera Right gesendet")

    with col2:
        if st.button("📖 NFC Read", key="aoia_nfc_read"):
            result = manager.send_instant_action(client, "dps", "nfcRead")
            if result:
                st.success("✅ NFC Read gesendet")

        if st.button("🗑️ NFC Clear", key="aoia_nfc_clear"):
            result = manager.send_instant_action(client, "dps", "nfcClear")
            if result:
                st.success("✅ NFC Clear gesendet")

        if st.button("🔄 DPS Reset", key="aoia_dps_reset"):
            result = manager.send_instant_action(client, "dps", "reset")
            if result:
                st.success("✅ DPS Reset gesendet")

    # AIQS Instant Actions
    st.write("**AIQS Instant Actions**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 AIQS Calibration", key="aoia_aiqs_calibration"):
            result = manager.send_instant_action(client, "aiqs", "calibration")
            if result:
                st.success("✅ AIQS Calibration gesendet")

        if st.button("📸 AIQS Photo", key="aoia_aiqs_photo"):
            result = manager.send_instant_action(client, "aiqs", "takePhoto")
            if result:
                st.success("✅ AIQS Photo gesendet")

    with col2:
        if st.button("🔄 AIQS Reset", key="aoia_aiqs_reset"):
            result = manager.send_instant_action(client, "aiqs", "reset")
            if result:
                st.success("✅ AIQS Reset gesendet")

    # Custom Instant Action
    st.write("**Custom Instant Action**")
    col1, col2 = st.columns(2)

    with col1:
        module = st.selectbox("Module", ["DPS", "AIQS", "HBW", "FTS"], key="custom_module")
        action = st.text_input("Action", key="custom_action")

    with col2:
        parameters = st.text_input("Parameters (JSON)", key="custom_parameters")

    if st.button("🚀 Send Custom Action", key="aoia_custom_action"):
        if action:
            result = manager.send_instant_action(client, module, action, parameters if parameters else None)
            if result:
                st.success(f"✅ Custom Action gesendet: {module}/{action}")
            else:
                st.error("❌ Fehler beim Senden der Custom Action")
        else:
            st.error("❌ Action ist erforderlich")
