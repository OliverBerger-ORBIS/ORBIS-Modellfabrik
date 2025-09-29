#!/usr/bin/env python3
"""
CCU MQTT Client - Thread-sicherer Singleton für CCU MQTT-Kommunikation
"""

import logging
import threading
import json
from typing import Dict, List, Optional, Any, Callable
from omf2.common.message_templates import get_message_templates
from omf2.common.logger import get_logger

logger = get_logger(__name__)


class CCUMQTTClient:
    """
    Thread-sicherer Singleton für CCU MQTT-Kommunikation
    
    Kapselt alle Verbindungs- und Kommunikationsdetails.
    Nutzt Registry v2 für Topic-Konfiguration.
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if CCUMQTTClient._initialized:
            return
            
        self.message_templates = get_message_templates()
        self.client_id = "omf_ccu"  # Dynamisch, wechselt bei jeder Anmeldung
        
        # Thread-sichere Locks
        self._client_lock = threading.Lock()
        self._buffer_lock = threading.Lock()
        
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
        
        # Topic-Buffer für Per-Topic-Buffer Pattern (thread-safe)
        self.topic_buffers = {}
        
        # Published/Subscribed Topics aus Registry
        self.published_topics = self._get_published_topics()
        self.subscribed_topics = self._get_subscribed_topics()
        
        CCUMQTTClient._initialized = True
        logger.info("🏗️ CCU MQTT Client initialized")
    
    def _get_published_topics(self) -> List[str]:
        """Lädt Published Topics aus Registry"""
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            ccu_client = mqtt_clients.get('mqtt_clients', {}).get('ccu_mqtt_client', {})
            return ccu_client.get('published_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to load CCU published topics: {e}")
            return []
    
    def _get_subscribed_topics(self) -> List[str]:
        """Lädt Subscribed Topics aus Registry"""
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            ccu_client = mqtt_clients.get('mqtt_clients', {}).get('ccu_mqtt_client', {})
            return ccu_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to load CCU subscribed topics: {e}")
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
            
            logger.info("🔌 CCU MQTT Client connected (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ CCU MQTT Client connection failed: {e}")
            return False
    
    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        try:
            # TODO: MQTT-Client Disconnect implementieren
            # self.client.loop_stop()
            # self.client.disconnect()
            
            logger.info("🔌 CCU MQTT Client disconnected (TODO: MQTT integration)")
            
        except Exception as e:
            logger.error(f"❌ CCU MQTT Client disconnect failed: {e}")
    
    def publish(self, topic: str, message: Dict[str, Any], qos: int = None, retain: bool = None) -> bool:
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
    
    def subscribe(self, topic: str, callback: Callable = None) -> bool:
        """
        Topic subscriben
        
        Args:
            topic: MQTT Topic
            callback: Callback-Funktion für eingehende Messages
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Subscribe implementieren
            # self.client.subscribe(topic)
            # if callback:
            #     self.client.message_callback_add(topic, callback)
            
            logger.info(f"📥 Subscribed to {topic} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscribe failed for topic {topic}: {e}")
            return False
    
    def get_buffer(self, topic: str) -> Optional[Dict]:
        """
        Letzte Message aus Topic-Buffer abrufen (thread-safe)
        
        Args:
            topic: MQTT Topic
            
        Returns:
            Letzte Message oder None
        """
        try:
            with self._buffer_lock:
                return self.topic_buffers.get(topic)
        except Exception as e:
            logger.error(f"❌ Failed to get buffer for topic {topic}: {e}")
            return None
    
    def get_all_buffers(self) -> Dict[str, Dict]:
        """
        Alle Topic-Buffer abrufen (thread-safe)
        
        Returns:
            Dict mit allen Topic-Buffern
        """
        try:
            with self._buffer_lock:
                return self.topic_buffers.copy()
        except Exception as e:
            logger.error(f"❌ Failed to get all buffers: {e}")
            return {}
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            logger.info("✅ CCU MQTT Client connected successfully")
            # TODO: Subscriptions aktivieren
            # for topic in self.subscribed_topics:
            #     self.subscribe(topic)
        else:
            logger.error(f"❌ CCU MQTT Client connection failed: {rc}")
    
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
        logger.info("🔌 CCU MQTT Client disconnected")


# Singleton Factory
def get_ccu_mqtt_client() -> CCUMQTTClient:
    """
    Factory-Funktion für CCU MQTT Client Singleton
    
    Returns:
        CCU MQTT Client Singleton Instance
    """
    return CCUMQTTClient()