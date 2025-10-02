#!/usr/bin/env python3
"""
Node-RED Subscriber MQTT Client - Thread-sicherer Singleton für Node-RED Subscribing
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from omf2.registry.manager.registry_manager import get_registry_manager

logger = logging.getLogger(__name__)


class NoderedSubMqttClient:
    """
    Thread-sicherer Singleton für Node-RED Subscriber MQTT-Kommunikation
    
    Kapselt alle Verbindungs- und Kommunikationsdetails für Node-RED Subscriber.
    Nutzt Registry v2 für Topic-Konfiguration.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if NoderedSubMqttClient._initialized:
            return
            
        self.registry_manager = get_registry_manager()
        self.client_id = "omf_nodered_sub"  # Dynamisch
        
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
        
        # Subscribed Topics aus Registry (Node-RED Subscriber ist NUR Subscriber)
        self.subscribed_topics = self._get_subscribed_topics()
        self.published_topics = []  # Node-RED Subscriber ist nie Publisher
        
        NoderedSubMqttClient._initialized = True
        logger.info("🏗️ Node-RED Subscriber MQTT Client initialized")
    
    def _get_subscribed_topics(self) -> List[str]:
        """Lädt Subscribed Topics aus Registry"""
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            nodered_sub_client = mqtt_clients.get('mqtt_clients', {}).get('nodered_sub_mqtt_client', {})
            return nodered_sub_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to load Node-RED sub topics: {e}")
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
            
            logger.info("🔌 Node-RED Subscriber MQTT Client connected (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Node-RED Subscriber MQTT Client connection failed: {e}")
            return False
    
    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        try:
            # TODO: MQTT-Client Disconnect implementieren
            # self.client.loop_stop()
            # self.client.disconnect()
            
            logger.info("🔌 Node-RED Subscriber MQTT Client disconnected (TODO: MQTT integration)")
            
        except Exception as e:
            logger.error(f"❌ Node-RED Subscriber MQTT Client disconnect failed: {e}")
    
    def subscribe_to_ccu_commands(self) -> bool:
        """
        CCU Commands subscriben
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            ccu_topics = [topic for topic in self.subscribed_topics if topic.startswith("ccu/")]
            
            # TODO: MQTT-Client Subscribe implementieren
            # for topic in ccu_topics:
            #     self.client.subscribe(topic)
            
            logger.info(f"📥 Subscribed to CCU commands: {ccu_topics} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscribe to CCU commands failed: {e}")
            return False
    
    def subscribe_to_opc_ua_states(self) -> bool:
        """
        OPC-UA States subscriben
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            opc_ua_topics = [topic for topic in self.subscribed_topics if topic.startswith("opc_ua/")]
            
            # TODO: MQTT-Client Subscribe implementieren
            # for topic in opc_ua_topics:
            #     self.client.subscribe(topic)
            
            logger.info(f"📥 Subscribed to OPC-UA states: {opc_ua_topics} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscribe to OPC-UA states failed: {e}")
            return False
    
    def subscribe_to_txt_commands(self) -> bool:
        """
        TXT Commands subscriben
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            txt_topics = [topic for topic in self.subscribed_topics if topic.startswith("/j1/txt/")]
            
            # TODO: MQTT-Client Subscribe implementieren
            # for topic in txt_topics:
            #     self.client.subscribe(topic)
            
            logger.info(f"📥 Subscribed to TXT commands: {txt_topics} (TODO: MQTT integration)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscribe to TXT commands failed: {e}")
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
    
    def get_ccu_command_buffers(self) -> Dict[str, Dict]:
        """
        CCU Command Buffers abrufen
        
        Returns:
            Dict mit CCU Command Buffers
        """
        try:
            ccu_buffers = {}
            for topic, buffer in self.topic_buffers.items():
                if topic.startswith("ccu/"):
                    ccu_buffers[topic] = buffer
            return ccu_buffers
        except Exception as e:
            logger.error(f"❌ Failed to get CCU command buffers: {e}")
            return {}
    
    def get_opc_ua_state_buffers(self) -> Dict[str, Dict]:
        """
        OPC-UA State Buffers abrufen
        
        Returns:
            Dict mit OPC-UA State Buffers
        """
        try:
            opc_ua_buffers = {}
            for topic, buffer in self.topic_buffers.items():
                if topic.startswith("opc_ua/"):
                    opc_ua_buffers[topic] = buffer
            return opc_ua_buffers
        except Exception as e:
            logger.error(f"❌ Failed to get OPC-UA state buffers: {e}")
            return {}
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            logger.info("✅ Node-RED Subscriber MQTT Client connected successfully")
            # TODO: Alle Subscriptions aktivieren
            # for topic in self.subscribed_topics:
            #     self.client.subscribe(topic)
        else:
            logger.error(f"❌ Node-RED Subscriber MQTT Client connection failed: {rc}")
    
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
        logger.info("🔌 Node-RED Subscriber MQTT Client disconnected")


# Singleton Factory
def get_nodered_sub_mqtt_client() -> NoderedSubMqttClient:
    """
    Factory-Funktion für Node-RED Subscriber MQTT Client Singleton
    
    Returns:
        Node-RED Subscriber MQTT Client Singleton Instance
    """
    return NoderedSubMqttClient()
