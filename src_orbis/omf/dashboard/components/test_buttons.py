import uuid
from datetime import datetime
from typing import Any, Dict

import streamlit as st


class TestMessageGenerator:
    """Generiert Test-Nachrichten basierend auf funktionierenden Commits"""

    @staticmethod
    def generate_aiqs_pick_message() -> Dict[str, Any]:
        """AIQS PICK-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "PICK",
            "module_id": "SVR4H76530",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 1, "subActionId": 1},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_aiqs_check_quality_message() -> Dict[str, Any]:
        """AIQS CHECK_QUALITY-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "CHECK_QUALITY",
            "module_id": "SVR4H76530",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 2, "subActionId": 2},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_aiqs_drop_message() -> Dict[str, Any]:
        """AIQS DROP-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "DROP",
            "module_id": "SVR4H76530",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 3, "subActionId": 3},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_mill_pick_message() -> Dict[str, Any]:
        """MILL PICK-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "PICK",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 1, "subActionId": 1},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_mill_mill_message() -> Dict[str, Any]:
        """MILL MILL-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "MILL",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 2, "subActionId": 2},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_mill_drop_message() -> Dict[str, Any]:
        """MILL DROP-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "DROP",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 3, "subActionId": 3},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_drill_pick_message() -> Dict[str, Any]:
        """DRILL PICK-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "PICK",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 1, "subActionId": 1},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_drill_drill_message() -> Dict[str, Any]:
        """DRILL DRILL-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "DRILL",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 2, "subActionId": 2},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_drill_drop_message() -> Dict[str, Any]:
        """DRILL DROP-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "DROP",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 3, "subActionId": 3},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_hbw_drop_message() -> Dict[str, Any]:
        """HBW DROP-Nachricht basierend auf Commit 807c29a"""
        return {
            "command": "DROP",
            "module_id": "SVR3QA2098",
            "order_id": str(uuid.uuid4()),
            "parameters": {"orderUpdateId": 1, "subActionId": 1},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_fts_charge_message() -> Dict[str, Any]:
        """FTS CHARGE-Nachricht basierend auf Commit 4378dbe"""
        return {
            "serialNumber": "5iO4",
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": "CHARGE",
                "metadata": {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"},
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_fts_dock_to_dps_message() -> Dict[str, Any]:
        """FTS DOCK_TO_DPS-Nachricht basierend auf Commit 4378dbe"""
        return {
            "serialNumber": "5iO4",
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": "DOCK_TO_DPS",
                "metadata": {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"},
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_fts_transport_message() -> Dict[str, Any]:
        """FTS TRANSPORT-Nachricht basierend auf Commit 4378dbe"""
        return {
            "serialNumber": "5iO4",
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": "TRANSPORT",
                "metadata": {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"},
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    @staticmethod
    def generate_factory_reset_message() -> Dict[str, Any]:
        """Factory Reset-Nachricht basierend auf Commit 4378dbe"""
        return {"timestamp": datetime.utcnow().isoformat() + "Z", "withStorage": False}

    @staticmethod
    def generate_order_message(color: str) -> Dict[str, Any]:
        """Bestellungs-Nachricht basierend auf Commit c126781"""
        return {"type": color, "ts": datetime.utcnow().isoformat() + "Z"}


def show_test_buttons():
    """Zeigt Test-Buttons für alle identifizierten funktionierenden Befehle"""
    st.header("🧪 Test-Bereich")
    st.info("Teste MQTT-Nachrichten mit hart codierten, funktionierenden Strukturen")

    # MQTT-Client aus Session-State holen
    mqtt_client = st.session_state.get("mqtt_client")

    if not mqtt_client:
        st.error("❌ MQTT-Client nicht verfügbar")
        return

    if not mqtt_client.connected:
        st.warning("⚠️ MQTT-Client nicht verbunden")
        return

    st.success("✅ MQTT-Client verbunden - Tests verfügbar")

    # Modul-Sequenzen (funktionieren bereits)
    st.subheader("🔧 Modul-Sequenzen (funktionieren)")
    st.info("Diese Befehle funktionieren bereits mit dem Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧪 AIQS PICK", key="test_aiqs_pick"):
            message = TestMessageGenerator.generate_aiqs_pick_message()
            topic = "module/v1/ff/SVR4H76530/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ AIQS PICK gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ AIQS PICK fehlgeschlagen: {topic}")

    with col2:
        if st.button("🧪 MILL PICK", key="test_mill_pick"):
            message = TestMessageGenerator.generate_mill_pick_message()
            topic = "module/v1/ff/SVR3QA2098/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ MILL PICK gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ MILL PICK fehlgeschlagen: {topic}")

    with col3:
        if st.button("🧪 DRILL PICK", key="test_drill_pick"):
            message = TestMessageGenerator.generate_drill_pick_message()
            topic = "module/v1/ff/SVR3QA2098/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ DRILL PICK gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ DRILL PICK fehlgeschlagen: {topic}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧪 AIQS CHECK_QUALITY", key="test_aiqs_check"):
            message = TestMessageGenerator.generate_aiqs_check_quality_message()
            topic = "module/v1/ff/SVR4H76530/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ AIQS CHECK_QUALITY gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ AIQS CHECK_QUALITY fehlgeschlagen: {topic}")

    with col2:
        if st.button("🧪 MILL MILL", key="test_mill_mill"):
            message = TestMessageGenerator.generate_mill_mill_message()
            topic = "module/v1/ff/SVR3QA2098/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ MILL MILL gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ MILL MILL fehlgeschlagen: {topic}")

    with col3:
        if st.button("🧪 DRILL DRILL", key="test_drill_drill"):
            message = TestMessageGenerator.generate_drill_drill_message()
            topic = "module/v1/ff/SVR3QA2098/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ DRILL DRILL gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ DRILL DRILL fehlgeschlagen: {topic}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧪 AIQS DROP", key="test_aiqs_drop"):
            message = TestMessageGenerator.generate_aiqs_drop_message()
            topic = "module/v1/ff/SVR4H76530/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ AIQS DROP gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ AIQS DROP fehlgeschlagen: {topic}")

    with col2:
        if st.button("🧪 MILL DROP", key="test_mill_drop"):
            message = TestMessageGenerator.generate_mill_drop_message()
            topic = "module/v1/ff/SVR3QA2098/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ MILL DROP gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ MILL DROP fehlgeschlagen: {topic}")

    with col3:
        if st.button("🧪 DRILL DROP", key="test_drill_drop"):
            message = TestMessageGenerator.generate_drill_drop_message()
            topic = "module/v1/ff/SVR3QA2098/order"
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ DRILL DROP gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ DRILL DROP fehlgeschlagen: {topic}")

    # HBW DROP (funktioniert bereits)
    st.subheader("📦 HBW DROP (funktioniert)")
    if st.button("🧪 HBW DROP", key="test_hbw_drop"):
        message = TestMessageGenerator.generate_hbw_drop_message()
        topic = "module/v1/ff/SVR3QA2098/order"
        result = mqtt_client.publish(topic, message)
        if result:
            st.success(f"✅ HBW DROP gesendet: {topic}")
            st.json(message)
        else:
            st.error(f"❌ HBW DROP fehlgeschlagen: {topic}")

    # Factory Reset (funktioniert bereits)
    st.subheader("🏭 Factory Reset (funktioniert)")
    if st.button("🧪 Factory Reset", key="test_factory_reset"):
        message = TestMessageGenerator.generate_factory_reset_message()
        topic = "ccu/set/reset"
        result = mqtt_client.publish(topic, message)
        if result:
            st.success(f"✅ Factory Reset gesendet: {topic}")
            st.json(message)
        else:
            st.error(f"❌ Factory Reset fehlgeschlagen: {topic}")

    # FTS Commands (VERGLEICH: Alte vs. neue Topics)
    st.subheader("🚗 FTS Commands (VERGLEICH: Alte vs. neue Topics)")
    st.info("Teste beide Topics parallel: fts/v1/ff/5iO4/order (alt) vs. fts/v1/ff/5iO4/command (neu)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**FTS CHARGE - Vergleich:**")
        if st.button("🧪 FTS CHARGE (alt: order)", key="test_fts_charge_old"):
            message = TestMessageGenerator.generate_fts_charge_message()
            topic = "fts/v1/ff/5iO4/order"  # ALTER TOPIC
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ FTS CHARGE (alt) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ FTS CHARGE (alt) fehlgeschlagen: {topic}")

        if st.button("🧪 FTS CHARGE (neu: command)", key="test_fts_charge_new"):
            message = TestMessageGenerator.generate_fts_charge_message()
            topic = "fts/v1/ff/5iO4/command"  # NEUER TOPIC aus Commit 4378dbe
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ FTS CHARGE (neu) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ FTS CHARGE (neu) fehlgeschlagen: {topic}")

    with col2:
        st.write("**FTS DOCK_TO_DPS - Vergleich:**")
        if st.button("🧪 FTS DOCK (alt: order)", key="test_fts_dock_old"):
            message = TestMessageGenerator.generate_fts_dock_to_dps_message()
            topic = "fts/v1/ff/5iO4/order"  # ALTER TOPIC
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ FTS DOCK (alt) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ FTS DOCK (alt) fehlgeschlagen: {topic}")

        if st.button("🧪 FTS DOCK (neu: command)", key="test_fts_dock_new"):
            message = TestMessageGenerator.generate_fts_dock_to_dps_message()
            topic = "fts/v1/ff/5iO4/command"  # NEUER TOPIC aus Commit 4378dbe
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ FTS DOCK (neu) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ FTS DOCK (neu) fehlgeschlagen: {topic}")

    with col3:
        st.write("**FTS TRANSPORT - Vergleich:**")
        if st.button("🧪 FTS TRANSPORT (alt: order)", key="test_fts_transport_old"):
            message = TestMessageGenerator.generate_fts_transport_message()
            topic = "fts/v1/ff/5iO4/order"  # ALTER TOPIC
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ FTS TRANSPORT (alt) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ FTS TRANSPORT (alt) fehlgeschlagen: {topic}")

        if st.button("🧪 FTS TRANSPORT (neu: command)", key="test_fts_transport_new"):
            message = TestMessageGenerator.generate_fts_transport_message()
            topic = "fts/v1/ff/5iO4/command"  # NEUER TOPIC aus Commit 4378dbe
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ FTS TRANSPORT (neu) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ FTS TRANSPORT (neu) fehlgeschlagen: {topic}")

    # Orders (VERGLEICH: Alte vs. neue Topics)
    st.subheader("📦 Orders (VERGLEICH: Alte vs. neue Topics)")
    st.info("Teste beide Topics parallel: ccu/order/request (alt) vs. /j1/txt/1/f/o/order (neu)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Order ROT - Vergleich:**")
        if st.button("🧪 Order ROT (alt: ccu)", key="test_order_rot_old"):
            message = TestMessageGenerator.generate_order_message("ROT")
            topic = "ccu/order/request"  # ALTER TOPIC
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ Order ROT (alt) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ Order ROT (alt) fehlgeschlagen: {topic}")

        if st.button("🧪 Order ROT (neu: txt)", key="test_order_rot_new"):
            message = TestMessageGenerator.generate_order_message("ROT")
            topic = "/j1/txt/1/f/o/order"  # NEUER TOPIC aus Commit c126781
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ Order ROT (neu) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ Order ROT (neu) fehlgeschlagen: {topic}")

    with col2:
        st.write("**Order WEISS - Vergleich:**")
        if st.button("🧪 Order WEISS (alt: ccu)", key="test_order_weiss_old"):
            message = TestMessageGenerator.generate_order_message("WEISS")
            topic = "ccu/order/request"  # ALTER TOPIC
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ Order WEISS (alt) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ Order WEISS (alt) fehlgeschlagen: {topic}")

        if st.button("🧪 Order WEISS (neu: txt)", key="test_order_weiss_new"):
            message = TestMessageGenerator.generate_order_message("WEISS")
            topic = "/j1/txt/1/f/o/order"  # NEUER TOPIC aus Commit c126781
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ Order WEISS (neu) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ Order WEISS (neu) fehlgeschlagen: {topic}")

    with col3:
        st.write("**Order BLAU - Vergleich:**")
        if st.button("🧪 Order BLAU (alt: ccu)", key="test_order_blau_old"):
            message = TestMessageGenerator.generate_order_message("BLAU")
            topic = "ccu/order/request"  # ALTER TOPIC
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ Order BLAU (alt) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ Order BLAU (alt) fehlgeschlagen: {topic}")

        if st.button("🧪 Order BLAU (neu: txt)", key="test_order_blau_new"):
            message = TestMessageGenerator.generate_order_message("BLAU")
            topic = "/j1/txt/1/f/o/order"  # NEUER TOPIC aus Commit c126781
            result = mqtt_client.publish(topic, message)
            if result:
                st.success(f"✅ Order BLAU (neu) gesendet: {topic}")
                st.json(message)
            else:
                st.error(f"❌ Order BLAU (neu) fehlgeschlagen: {topic}")

    # Debug-Informationen
    st.subheader("🔍 Debug-Informationen")
    st.json({"mqtt_client_connected": mqtt_client.connected})
