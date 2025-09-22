"""
APS Steering - Modules
Zeigt Module Steering für die APS an
"""

import streamlit as st


class APSSteeringModulesManager:
    """Manager für APS Module Steering"""

    def __init__(self):
        self.module_commands = []
        self.last_update = None

    def send_module_command(self, mqtt_client, command, payload=None):
        """Sendet einen Module Command"""
        try:
            if payload is None:
                payload = {}
            result = mqtt_client.publish(command, payload, qos=1, retain=False)
            return result

        except Exception as e:
            st.error(f"❌ Fehler beim Senden des Module Commands: {e}")
            return False


def show_aps_steering_modules():
    """Zeigt Module Steering an"""
    st.subheader("🔧 Module Steering")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state
    if "aps_steering_modules_manager" not in st.session_state:
        st.session_state["aps_steering_modules_manager"] = APSSteeringModulesManager()

    manager = st.session_state["aps_steering_modules_manager"]

    # DPS Module Control
    st.write("**DPS Module Control**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 DPS Reset", key="asm_dps_reset"):
            result = manager.send_module_command(client, "dps/set/reset")
            if result:
                st.success("✅ DPS Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📷 DPS Camera Up", key="asm_dps_camera_up"):
            result = manager.send_module_command(client, "dps/instantAction", {"action": "cameraUp"})
            if result:
                st.success("✅ DPS Camera Up gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📖 DPS NFC Read", key="asm_dps_nfc_read"):
            result = manager.send_module_command(client, "dps/instantAction", {"action": "nfcRead"})
            if result:
                st.success("✅ DPS NFC Read gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("📷 DPS Camera Down", key="asm_dps_camera_down"):
            result = manager.send_module_command(client, "dps/instantAction", {"action": "cameraDown"})
            if result:
                st.success("✅ DPS Camera Down gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🗑️ DPS NFC Clear", key="asm_dps_nfc_clear"):
            result = manager.send_module_command(client, "dps/instantAction", {"action": "nfcClear"})
            if result:
                st.success("✅ DPS NFC Clear gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📊 DPS Status", key="asm_dps_status"):
            result = manager.send_module_command(client, "dps/get/status")
            if result:
                st.success("✅ DPS Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # AIQS Module Control
    st.write("**AIQS Module Control**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 AIQS Reset", key="asm_aiqs_reset"):
            result = manager.send_module_command(client, "aiqs/set/reset")
            if result:
                st.success("✅ AIQS Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔍 AIQS Calibration", key="asm_aiqs_calibration"):
            result = manager.send_module_command(client, "aiqs/instantAction", {"action": "calibration"})
            if result:
                st.success("✅ AIQS Calibration gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("📸 AIQS Photo", key="asm_aiqs_photo"):
            result = manager.send_module_command(client, "aiqs/instantAction", {"action": "takePhoto"})
            if result:
                st.success("✅ AIQS Photo gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📊 AIQS Status", key="asm_aiqs_status"):
            result = manager.send_module_command(client, "aiqs/get/status")
            if result:
                st.success("✅ AIQS Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # HBW Module Control
    st.write("**HBW Module Control**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 HBW Reset", key="asm_hbw_reset"):
            result = manager.send_module_command(client, "hbw/set/reset")
            if result:
                st.success("✅ HBW Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📊 HBW Status", key="asm_hbw_status"):
            result = manager.send_module_command(client, "hbw/get/status")
            if result:
                st.success("✅ HBW Status gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        if st.button("📦 HBW Storage", key="asm_hbw_storage"):
            result = manager.send_module_command(client, "hbw/set/storage")
            if result:
                st.success("✅ HBW Storage gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("📤 HBW Retrieval", key="asm_hbw_retrieval"):
            result = manager.send_module_command(client, "hbw/set/retrieval")
            if result:
                st.success("✅ HBW Retrieval gesendet")
            else:
                st.error("❌ Fehler beim Senden")
