#!/usr/bin/env python3
"""
Admin MQTT Client - Thread-sicherer Singleton für Admin MQTT-Kommunikation
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from omf2.common.message_templates import get_message_templates

logger = logging.getLogger(__name__)


class AdminMQTTClient:
    """
    Thread-sicherer Singleton für Admin MQTT-Kommunikation
    
    Kapselt alle Verbindungs- und Kommunikationsdetails für Admin.
    Nutzt Registry v2 für Topic-Konfiguration.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if AdminMQTTClient._initialized:
            return
            
        self.message_templates = get_message_templates()
        self.client_id = "omf_admin"
        
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
        
        # Published/Subscribed Topics aus Registry
        self.published_topics = self._get_published_topics()
        self.subscribed_topics = self._get_subscribed_topics()
        
        AdminMQTTClient._initialized = True
        logger.info("🏗️ Admin MQTT Client initialized")
    
    def _get_published_topics(self) -> List[str]:
        """Lädt Published Topics aus Registry"""
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            admin_client = mqtt_clients.get('mqtt_clients', {}).get('admin_mqtt_client', {})
            return admin_client.get('published_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to load admin published topics: {e}")
            return []
    
    def _get_subscribed_topics(self) -> List[str]:
        """Lädt Subscribed Topics aus Registry"""
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            admin_client = mqtt_clients.get('mqtt_clients', {}).get('admin_mqtt_client', {})
            return admin_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to load admin subscribed topics: {e}")
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
            
            logger.info("🔌 Admin MQTT Client connected (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Admin MQTT Client connection failed: {e}")
            return False
    
    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        try:
            # TODO: MQTT-Client Disconnect implementieren
            # self.client.loop_stop()
            # self.client.disconnect()
            
            logger.info("🔌 Admin MQTT Client disconnected (TODO: MQTT integration)")
            
        except Exception as e:
            logger.error(f"❌ Admin MQTT Client disconnect failed: {e}")
    
    def publish_message(self, topic: str, message: Dict[str, Any], qos: int = None, retain: bool = None) -> bool:
        """
        Message auf Topic publizieren
        
        Args:
            topic: MQTT Topic
            message: Message-Dict
            qos: QoS-Level (wird aus Registry geladen wenn None)
            retain: Retain-Flag (wird aus Registry geladen wenn None)
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # QoS/Retain aus Registry laden wenn nicht angegeben
            if qos is None or retain is None:
                topic_qos, topic_retain = self.message_templates.get_topic_config(topic)
                qos = qos if qos is not None else topic_qos
                retain = retain if retain is not None else topic_retain
            
            # TODO: MQTT-Client Publish implementieren
            # import json
            # payload = json.dumps(message)
            # result = self.client.publish(topic, payload, qos=qos, retain=retain)
            # return result.rc == 0
            
            logger.info(f"📤 Published to {topic}: {message} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Publish failed for topic {topic}: {e}")
            return False
    
    def subscribe_to_all(self) -> bool:
        """
        Alle Topics subscriben (Admin subscribiert alles mit '#')
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Subscribe implementieren
            # self.client.subscribe("#")
            
            logger.info("📥 Subscribed to all topics (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscribe to all topics failed: {e}")
            return False
    
    def get_buffer(self, topic: str) -> Optional[Dict]:
        """
        Letzte Message aus Topic-Buffer abrufen
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Letzte Message oder None
        """
        try:
            return self.topic_buffers.get(topic)
        except Exception as e:
            logger.error(f"❌ Failed to get buffer for topic {topic}: {e}")
            return None
    
    def get_all_buffers(self) -> Dict[str, Dict]:
        """
        Alle Topic-Buffer abrufen
        
        Returns:
            Dict mit allen Topic-Buffern
        """
        try:
            return self.topic_buffers.copy()
        except Exception as e:
            logger.error(f"❌ Failed to get all buffers: {e}")
            return {}
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        System Overview abrufen
        
        Returns:
            System Overview Dict
        """
        try:
            overview = {
                "total_topics": len(self.topic_buffers),
                "active_topics": [topic for topic, buffer in self.topic_buffers.items() if buffer],
                "last_activity": max([buffer.get('timestamp', '') for buffer in self.topic_buffers.values() if buffer], default=''),
                "mqtt_connected": False  # TODO: MQTT integration
            }
            
            logger.info(f"📊 System overview: {overview}")
            return overview
            
        except Exception as e:
            logger.error(f"❌ Failed to get system overview: {e}")
            return {}
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            logger.info("✅ Admin MQTT Client connected successfully")
            # TODO: Alle Subscriptions aktivieren
            # self.subscribe_to_all()
        else:
            logger.error(f"❌ Admin MQTT Client connection failed: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT on_message Callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # TODO: JSON-Parsing und Buffer-Update
            # import json
            # message = json.loads(payload)
            # self.topic_buffers[topic] = message
            
            logger.debug(f"📥 Received on {topic}: {payload}")
            
        except Exception as e:
            logger.error(f"❌ Message processing failed: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        logger.info("🔌 Admin MQTT Client disconnected")


# Singleton Factory
def get_admin_mqtt_client() -> AdminMQTTClient:
    """
    Factory-Funktion für Admin MQTT Client Singleton
    
    Returns:
        Admin MQTT Client Singleton Instance
    """
    return AdminMQTTClient()
