#!/usr/bin/env python3
"""
Session Manager MQTT Client
Persistenter MQTT-Client für Session Manager mit Batch-Sending
"""

import time
from typing import Any, Dict, List

import paho.mqtt.client as mqtt

# Absolute import for potential standalone use
from session_manager.utils.logging_config import get_logger

logger = get_logger(__name__)


class SessionManagerMqttClient:
    """Persistenter MQTT-Client für Session Manager"""

    def __init__(self, client_id: str = "session_manager_replay", host: str = "localhost", port: int = 1883):
        # Eindeutige Client-ID mit Timestamp
        import time
        self.client_id = f"{client_id}_{int(time.time())}"
        self.host = host
        self.port = port
        self.client = None
        self.connected = False
        self.logger = get_logger(f"{__name__}.{client_id}")

    def connect(self) -> bool:
        """Verbindung zum MQTT-Broker herstellen"""
        try:
            if self.connected:
                self.logger.info("✅ MQTT-Client bereits verbunden")
                return True

            self.client = mqtt.Client(client_id=self.client_id, clean_session=False)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish

            self.logger.info(f"🔌 Verbinde zu MQTT-Broker: {self.host}:{self.port}")
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()

            # Warten auf Verbindung
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1

            if self.connected:
                self.logger.info("✅ MQTT-Client erfolgreich verbunden")
                return True
            else:
                self.logger.error("❌ MQTT-Client Verbindung fehlgeschlagen")
                return False

        except Exception as e:
            self.logger.error(f"❌ MQTT-Client Verbindungsfehler: {e}")
            return False

    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        try:
            if self.client and self.connected:
                self.logger.info("🔌 MQTT-Client wird getrennt")
                self.client.loop_stop()
                self.client.disconnect()
                self.connected = False
                self.logger.info("✅ MQTT-Client getrennt")
        except Exception as e:
            self.logger.error(f"❌ MQTT-Client Trennungsfehler: {e}")

    def send_message(self, topic: str, payload: str, qos: int = 1) -> bool:
        """Einzelne Nachricht senden"""
        try:
            if not self.connected:
                self.logger.warning("⚠️ MQTT-Client nicht verbunden, versuche Verbindung")
                if not self.connect():
                    return False

            result = self.client.publish(topic, payload, qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"📤 Nachricht gesendet: {topic}")
                return True
            else:
                self.logger.error(f"❌ Nachricht senden fehlgeschlagen: {topic}, RC: {result.rc}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Nachricht senden Fehler: {e}")
            return False

    def send_batch(self, messages: List[Dict[str, Any]], delay: float = 0.1) -> int:
        """Batch von Nachrichten senden"""
        try:
            if not self.connected:
                self.logger.warning("⚠️ MQTT-Client nicht verbunden, versuche Verbindung")
                if not self.connect():
                    return 0

            sent_count = 0
            for i, message in enumerate(messages):
                topic = message.get("topic", "")
                payload = message.get("payload", "")
                qos = message.get("qos", 1)

                if self.send_message(topic, payload, qos):
                    sent_count += 1

                # Kleine Verzögerung zwischen Nachrichten
                if delay > 0 and i < len(messages) - 1:
                    time.sleep(delay)

            self.logger.info(f"📤 Batch gesendet: {sent_count}/{len(messages)} Nachrichten")
            return sent_count

        except Exception as e:
            self.logger.error(f"❌ Batch senden Fehler: {e}")
            return 0

    def test_connection(self) -> bool:
        """Verbindung testen"""
        try:
            if not self.connected:
                return self.connect()

            # Test-Nachricht senden
            test_topic = "test/connection"
            test_payload = "test"
            return self.send_message(test_topic, test_payload, 1)

        except Exception as e:
            self.logger.error(f"❌ Verbindungstest Fehler: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            self.connected = True
            self.logger.info("✅ MQTT-Client verbunden")
        else:
            self.connected = False
            self.logger.error(f"❌ MQTT-Client Verbindung fehlgeschlagen: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"⚠️ MQTT-Client unerwartet getrennt: {rc}")
        else:
            self.logger.info("✅ MQTT-Client getrennt")

    def _on_publish(self, client, userdata, mid):
        """MQTT on_publish Callback"""
        self.logger.debug(f"📤 Nachricht veröffentlicht: {mid}")

    def __enter__(self):
        """Context Manager Entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager Exit"""
        self.disconnect()


def get_replay_client() -> SessionManagerMqttClient:
    """Singleton für Replay Station MQTT-Client - in st.session_state"""
    import streamlit as st

    # MQTT-Client in st.session_state speichern (wie OMF Dashboard)
    if "session_manager_mqtt_client" not in st.session_state:
        st.session_state["session_manager_mqtt_client"] = SessionManagerMqttClient("session_manager_replay_station")
        logger.info("🔌 Session Manager MQTT-Client erstellt (st.session_state)")

    return st.session_state["session_manager_mqtt_client"]


def get_recorder_client() -> SessionManagerMqttClient:
    """Singleton für Session Recorder MQTT-Client - in st.session_state"""
    import streamlit as st

    if "session_manager_recorder_mqtt_client" not in st.session_state:
        st.session_state["session_manager_recorder_mqtt_client"] = SessionManagerMqttClient("session_manager_session_recorder")
        logger.info("🔌 Session Recorder MQTT-Client erstellt (st.session_state)")

    return st.session_state["session_manager_recorder_mqtt_client"]


def get_settings_client() -> SessionManagerMqttClient:
    """Singleton für Settings MQTT-Client - in st.session_state"""
    import streamlit as st

    if "session_manager_settings_mqtt_client" not in st.session_state:
        st.session_state["session_manager_settings_mqtt_client"] = SessionManagerMqttClient("session_manager_settings")
        logger.info("🔌 Session Settings MQTT-Client erstellt (st.session_state)")

    return st.session_state["session_manager_settings_mqtt_client"]


def cleanup_all_clients():
    """Alle MQTT-Clients trennen"""
    import streamlit as st

    if "session_manager_mqtt_client" in st.session_state:
        st.session_state["session_manager_mqtt_client"].disconnect()
        del st.session_state["session_manager_mqtt_client"]

    if "session_manager_recorder_mqtt_client" in st.session_state:
        st.session_state["session_manager_recorder_mqtt_client"].disconnect()
        del st.session_state["session_manager_recorder_mqtt_client"]

    if "session_manager_settings_mqtt_client" in st.session_state:
        st.session_state["session_manager_settings_mqtt_client"].disconnect()
        del st.session_state["session_manager_settings_mqtt_client"]

    logger.info("🧹 Alle Session Manager MQTT-Clients getrennt")
