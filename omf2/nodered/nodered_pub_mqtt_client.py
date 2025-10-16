#!/usr/bin/env python3
"""
Node-RED Publisher MQTT Client - Thread-sicherer Singleton für Node-RED Publishing
"""

import logging
from typing import Any, Dict, List

from omf2.registry.manager.registry_manager import get_registry_manager

logger = logging.getLogger(__name__)


class NoderedPubMqttClient:
    """
    Thread-sicherer Singleton für Node-RED Publisher MQTT-Kommunikation

    Kapselt alle Verbindungs- und Kommunikationsdetails für Node-RED Publisher.
    Nutzt Registry v2 für Topic-Konfiguration.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if NoderedPubMqttClient._initialized:
            return

        self.registry_manager = get_registry_manager()
        self.client_id = "omf_nodered_pub"  # Dynamisch

        # TODO: MQTT-Broker Settings aus Config laden (cfg_or_env)
        # self.broker_host = config.get("mqtt.broker.host", "localhost")
        # self.broker_port = config.get("mqtt.broker.port", 1883)
        # self.broker_username = config.get("mqtt.broker.username")
        # self.broker_password = config.get("mqtt.broker.password")

        # TODO: MQTT-Client initialisieren
        # self.client = mqtt.Client(client_id=self.client_id)
        # self.client.on_connect = self._on_connect
        # self.client.on_message = self._on_message
        # self.client.on_disconnect = self._on_disconnect

        # Topic-Buffer für Per-Topic-Buffer Pattern
        self.topic_buffers = {}

        # Published Topics aus Registry (Node-RED Publisher ist NUR Publisher)
        self.published_topics = self._get_published_topics()
        self.subscribed_topics = []  # Node-RED Publisher ist nie Subscriber

        NoderedPubMqttClient._initialized = True
        logger.info("🏗️ Node-RED Publisher MQTT Client initialized")

    def _get_published_topics(self) -> List[str]:
        """Lädt Published Topics aus Registry"""
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            nodered_pub_client = mqtt_clients.get("mqtt_clients", {}).get("nodered_pub_mqtt_client", {})
            return nodered_pub_client.get("published_topics", [])
        except Exception as e:
            logger.error(f"❌ Failed to load Node-RED pub topics: {e}")
            return []

    def connect(self) -> bool:
        """
        Verbindung zum MQTT-Broker herstellen

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Verbindung implementieren
            # self.client.connect(self.broker_host, self.broker_port)
            # self.client.loop_start()

            logger.info("🔌 Node-RED Publisher MQTT Client connected (TODO: MQTT integration)")
            return True

        except Exception as e:
            logger.error(f"❌ Node-RED Publisher MQTT Client connection failed: {e}")
            return False

    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        try:
            # TODO: MQTT-Client Disconnect implementieren
            # self.client.loop_stop()
            # self.client.disconnect()

            logger.info("🔌 Node-RED Publisher MQTT Client disconnected (TODO: MQTT integration)")

        except Exception as e:
            logger.error(f"❌ Node-RED Publisher MQTT Client disconnect failed: {e}")

    def publish_normalized_state(self, module_id: str, state_data: Dict[str, Any]) -> bool:
        """
        Normalisierten Module State publizieren

        Args:
            module_id: Module ID
            state_data: State-Daten

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:

            # TODO: MQTT-Client Publish implementieren
            # qos, retain = self.registry_manager.get_topic_config(topic)
            # import json
            # payload = json.dumps(state_data)
            # result = self.client.publish(topic, payload, qos=qos, retain=retain)
            # return result.rc == 0

            logger.info(f"📤 Published normalized state for {module_id}: {state_data} (TODO: MQTT integration)")
            return True

        except Exception as e:
            logger.error(f"❌ Publish normalized state failed for module {module_id}: {e}")
            return False

    def publish_ccu_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        CCU Feedback publizieren

        Args:
            feedback_data: Feedback-Daten

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:

            # TODO: MQTT-Client Publish implementieren
            # qos, retain = self.registry_manager.get_topic_config(topic)
            # import json
            # payload = json.dumps(feedback_data)
            # result = self.client.publish(topic, payload, qos=qos, retain=retain)
            # return result.rc == 0

            logger.info(f"📤 Published CCU feedback: {feedback_data} (TODO: MQTT integration)")
            return True

        except Exception as e:
            logger.error(f"❌ Publish CCU feedback failed: {e}")
            return False

    def publish_order_completed(self, order_data: Dict[str, Any]) -> bool:
        """
        Order Completed publizieren

        Args:
            order_data: Order-Daten

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:

            # TODO: MQTT-Client Publish implementieren
            # qos, retain = self.registry_manager.get_topic_config(topic)
            # import json
            # payload = json.dumps(order_data)
            # result = self.client.publish(topic, payload, qos=qos, retain=retain)
            # return result.rc == 0

            logger.info(f"📤 Published order completed: {order_data} (TODO: MQTT integration)")
            return True

        except Exception as e:
            logger.error(f"❌ Publish order completed failed: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            logger.info("✅ Node-RED Publisher MQTT Client connected successfully")
            # Node-RED Publisher ist nie Subscriber
        else:
            logger.error(f"❌ Node-RED Publisher MQTT Client connection failed: {rc}")

    def _on_message(self, client, userdata, msg):
        """MQTT on_message Callback (sollte nie aufgerufen werden)"""
        logger.warning(f"⚠️ Node-RED Publisher received message (should not happen): {msg.topic}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        logger.info("🔌 Node-RED Publisher MQTT Client disconnected")


# Singleton Factory
def get_nodered_pub_mqtt_client() -> NoderedPubMqttClient:
    """
    Factory-Funktion für Node-RED Publisher MQTT Client Singleton

    Returns:
        Node-RED Publisher MQTT Client Singleton Instance
    """
    return NoderedPubMqttClient()
