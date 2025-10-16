#!/usr/bin/env python3
"""
Simple MQTT Client für Session Manager
Unabhängig von OMF - nur für Session Manager
"""

import logging
import time

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class SimpleMqttClient:
    """Einfacher MQTT-Client für Session Manager - unabhängig von OMF"""

    def __init__(self, client_id: str = "session_manager", host: str = "localhost", port: int = 1883):
        # Eindeutige Client-ID
        self.client_id = f"{client_id}_{int(time.time())}"
        self.host = host
        self.port = port
        self.client = None
        self.connected = False

    def connect(self) -> bool:
        """Verbindung zum MQTT-Broker herstellen"""
        try:
            if self.connected:
                return True

            self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect

            logger.info(f"🔌 Verbinde zu MQTT-Broker: {self.host}:{self.port}")
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()

            # Warten auf Verbindung
            timeout = 5
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1

            if self.connected:
                logger.info("✅ MQTT-Client erfolgreich verbunden")
                return True
            else:
                logger.error("❌ MQTT-Client Verbindung fehlgeschlagen")
                return False

        except Exception as e:
            logger.error(f"❌ MQTT-Client Verbindungsfehler: {e}")
            return False

    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        try:
            if self.client and self.connected:
                logger.info("🔌 MQTT-Client wird getrennt")
                self.client.loop_stop()
                self.client.disconnect()
                self.connected = False
                logger.info("✅ MQTT-Client getrennt")
        except Exception as e:
            logger.error(f"❌ MQTT-Client Trennungsfehler: {e}")

    def send_message(self, topic: str, payload: str, qos: int = 1) -> bool:
        """Einzelne Nachricht senden"""
        try:
            if not self.connected:
                if not self.connect():
                    return False

            result = self.client.publish(topic, payload, qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"📤 Nachricht gesendet: {topic}")
                return True
            else:
                logger.error(f"❌ Nachricht senden fehlgeschlagen: {topic}, RC: {result.rc}")
                return False

        except Exception as e:
            logger.error(f"❌ Nachricht senden Fehler: {e}")
            return False

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
            logger.error(f"❌ Verbindungstest Fehler: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            self.connected = True
            logger.info("✅ MQTT-Client verbunden")
        else:
            self.connected = False
            logger.error(f"❌ MQTT-Client Verbindung fehlgeschlagen: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️ MQTT-Client unerwartet getrennt: {rc}")
        else:
            logger.info("✅ MQTT-Client getrennt")


# Singleton für Session Manager
_simple_mqtt_client = None


def get_simple_mqtt_client() -> SimpleMqttClient:
    """Singleton für Simple MQTT-Client"""
    global _simple_mqtt_client
    if _simple_mqtt_client is None:
        _simple_mqtt_client = SimpleMqttClient("session_manager_simple")
        logger.info("🔌 Simple MQTT-Client erstellt")
    return _simple_mqtt_client


def cleanup_simple_mqtt_client():
    """Simple MQTT-Client trennen"""
    global _simple_mqtt_client
    if _simple_mqtt_client:
        _simple_mqtt_client.disconnect()
        _simple_mqtt_client = None
        logger.info("🧹 Simple MQTT-Client getrennt")
