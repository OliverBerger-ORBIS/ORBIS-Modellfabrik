#!/usr/bin/env python3
"""
Admin MQTT Client - Thread-sicherer Singleton für Admin MQTT-Kommunikation
"""

import logging
import threading
import json
import time
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import yaml

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None

from omf2.common.message_templates import get_message_templates
from omf2.common.logger import get_logger

logger = get_logger(__name__)


class AdminMQTTClient:
    """
    Thread-sicherer Singleton für Admin MQTT-Kommunikation
    
    Kapselt alle Verbindungs- und Kommunikationsdetails für Admin.
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
        if AdminMQTTClient._initialized:
            return
            
        self.message_templates = get_message_templates()
        # Get client_id from registry as prefix
        self.base_client_id = self._get_base_client_id()
        self.client_id = self.base_client_id  # Will be updated based on environment
        
        # Thread-sichere Locks
        self._client_lock = threading.Lock()
        self._buffer_lock = threading.Lock()
        
        # MQTT-Client und Konfiguration
        self.client = None
        self.connected = False
        self.config = self._load_config()
        
        # Topic-Buffer für Per-Topic-Buffer Pattern (thread-safe)
        self.topic_buffers = {}
        
        # Published/Subscribed Topics aus Registry
        self.published_topics = self._get_published_topics()
        self.subscribed_topics = self._get_subscribed_topics()
        
        AdminMQTTClient._initialized = True
        logger.info("🏗️ Admin MQTT Client initialized")
    
    def _get_base_client_id(self) -> str:
        """Get base client_id from registry"""
        try:
            mqtt_clients = self.message_templates.mqtt_clients
            admin_client = mqtt_clients.get('mqtt_clients', {}).get('admin_mqtt_client', {})
            return admin_client.get('client_id', 'omf_admin')
        except Exception as e:
            logger.error(f"❌ Failed to load base client_id from registry: {e}")
            return 'omf_admin'
    
    def _load_config(self) -> Dict[str, Any]:
        """Lädt MQTT-Konfiguration aus mqtt_settings.yml"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "mqtt_settings.yml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"⚠️ Config file not found: {config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback-Konfiguration"""
        return {
            'mqtt': {
                'host': 'localhost',
                'port': 1883,
                'username': '',
                'password': '',
                'keepalive': 60,
                'clean_session': True
            },
            'default_environment': 'mock'
        }
    
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
    
    def connect(self, environment: str = 'mock') -> bool:
        """
        Verbindung zum MQTT-Broker herstellen
        
        Args:
            environment: Environment ('live', 'replay', 'mock')
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        with self._client_lock:
            try:
                if not MQTT_AVAILABLE:
                    logger.warning("⚠️ paho-mqtt not available, using mock mode")
                    self.connected = True
                    return True
                
                # Environment-spezifische Konfiguration laden
                env_config = self.config.get('environments', {}).get(environment, {})
                mqtt_config = {**self.config.get('mqtt', {}), **env_config.get('mqtt', {})}
                
                # Mock-Modus für 'mock' environment
                if environment == 'mock' or not mqtt_config.get('enabled', True):
                    # Update client_id even in mock mode - use postfix from config
                    client_id_postfix = mqtt_config.get('client_id_postfix', f"_{environment}")
                    self.client_id = f"{self.base_client_id}{client_id_postfix}"
                    logger.info(f"🧪 Mock mode - no real MQTT connection (Client ID: {self.client_id})")
                    self.connected = True
                    return True
                
                # MQTT-Client initialisieren - Registry client_id als Prefix + Postfix aus mqtt_settings
                client_id_postfix = mqtt_config.get('client_id_postfix', f"_{environment}")
                client_id = f"{self.base_client_id}{client_id_postfix}"
                self.client_id = client_id  # Update instance client_id
                self.client = mqtt.Client(client_id=client_id)
                self.client.on_connect = self._on_connect
                self.client.on_message = self._on_message
                self.client.on_disconnect = self._on_disconnect
                
                # Authentifizierung falls vorhanden
                username = mqtt_config.get('username')
                password = mqtt_config.get('password')
                if username:
                    self.client.username_pw_set(username, password)
                
                # Verbindung herstellen
                host = mqtt_config.get('host', 'localhost')
                port = mqtt_config.get('port', 1883)
                keepalive = mqtt_config.get('keepalive', 60)
                
                self.client.connect(host, port, keepalive)
                self.client.loop_start()
                
                # Warten auf Verbindung
                timeout = 5
                start_time = time.time()
                while not self.connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                if self.connected:
                    logger.info(f"🔌 Admin MQTT Client connected to {host}:{port}")
                    # Alle Topics subscriben
                    self.subscribe_to_all()
                    return True
                else:
                    logger.error("❌ Admin MQTT Client connection timeout")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Admin MQTT Client connection failed: {e}")
                return False
    
    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen"""
        with self._client_lock:
            try:
                if self.client and self.connected:
                    self.client.loop_stop()
                    self.client.disconnect()
                    self.connected = False
                    logger.info("🔌 Admin MQTT Client disconnected")
                else:
                    logger.info("🔌 Admin MQTT Client was not connected")
                    
            except Exception as e:
                logger.error(f"❌ Admin MQTT Client disconnect failed: {e}")
    
    def publish_message(self, topic: str, message: Dict[str, Any], qos: int = None, retain: bool = None) -> bool:
        """
        Message auf Topic publizieren (thread-safe)
        
        Args:
            topic: MQTT Topic
            message: Message-Dict
            qos: QoS-Level (wird aus Registry geladen wenn None)
            retain: Retain-Flag (wird aus Registry geladen wenn None)
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        with self._client_lock:
            try:
                # QoS/Retain aus Registry laden wenn nicht angegeben
                if qos is None or retain is None:
                    try:
                        topic_qos, topic_retain = self.message_templates.get_topic_config(topic)
                        qos = qos if qos is not None else topic_qos
                        retain = retain if retain is not None else topic_retain
                    except Exception:
                        # Fallback für unbekannte Topics
                        qos = qos if qos is not None else 1
                        retain = retain if retain is not None else False
                
                # Mock-Modus
                if not self.connected or not self.client:
                    logger.info(f"📤 Mock publish to {topic}: {message}")
                    return True
                
                # JSON-Payload erstellen
                payload = json.dumps(message, ensure_ascii=False)
                
                # MQTT-Publish
                result = self.client.publish(topic, payload, qos=qos, retain=retain)
                
                if result.rc == 0:
                    logger.info(f"📤 Published to {topic}: {message}")
                    return True
                else:
                    logger.error(f"❌ Publish failed for topic {topic}: {result.rc}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Publish failed for topic {topic}: {e}")
                return False
    
    def subscribe_to_all(self) -> bool:
        """
        Alle Topics subscriben (Admin subscribiert alles mit '#')
        
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        with self._client_lock:
            try:
                if not self.connected or not self.client:
                    logger.info("📥 Mock subscribe to all topics")
                    return True
                
                # Wildcard-Subscription für Admin
                result = self.client.subscribe("#", qos=1)
                
                if result[0] == 0:
                    logger.info("📥 Subscribed to all topics (#)")
                    return True
                else:
                    logger.error(f"❌ Subscribe to all topics failed: {result[0]}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Subscribe to all topics failed: {e}")
                return False
    
    def get_broker_key(self) -> str:
        """
        Broker-Key für Subscription-Tracking (wie im alten Dashboard)
        
        Returns:
            Broker-Key String (host:port)
        """
        try:
            if hasattr(self, 'config') and self.config:
                host = self.config.get('host', 'localhost')
                port = self.config.get('port', 1883)
                return f"{host}:{port}"
            else:
                return "localhost:1883"
        except Exception as e:
            logger.error(f"❌ Failed to get broker key: {e}")
            return "unknown:unknown"
    
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
    
    def get_system_overview(self) -> Dict[str, Any]:
        """
        System Overview abrufen (thread-safe)
        
        Returns:
            System Overview Dict
        """
        try:
            with self._buffer_lock:
                overview = {
                    "total_topics": len(self.topic_buffers),
                    "active_topics": [topic for topic, buffer in self.topic_buffers.items() if buffer],
                    "last_activity": max([buffer.get('timestamp', '') for buffer in self.topic_buffers.values() if buffer], default=''),
                    "mqtt_connected": self.connected,
                    "client_id": self.client_id
                }
            
            logger.info(f"📊 System overview: {overview}")
            return overview
            
        except Exception as e:
            logger.error(f"❌ Failed to get system overview: {e}")
            return {}
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        if rc == 0:
            self.connected = True
            logger.info("✅ Admin MQTT Client connected successfully")
        else:
            self.connected = False
            logger.error(f"❌ Admin MQTT Client connection failed: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT on_message Callback (thread-safe)"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            # JSON-Parsing und Buffer-Update
            try:
                message = json.loads(payload)
                message['timestamp'] = time.time()
                
                with self._buffer_lock:
                    self.topic_buffers[topic] = message
                
                logger.debug(f"📥 Received on {topic}: {message}")
                
            except json.JSONDecodeError:
                # Nicht-JSON Messages als Text speichern
                with self._buffer_lock:
                    self.topic_buffers[topic] = {
                        'raw_payload': payload,
                        'timestamp': time.time()
                    }
                logger.debug(f"📥 Received raw on {topic}: {payload}")
            
        except Exception as e:
            logger.error(f"❌ Message processing failed: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        self.connected = False
        logger.info("🔌 Admin MQTT Client disconnected")


# Singleton Factory
def get_admin_mqtt_client() -> AdminMQTTClient:
    """
    Factory-Funktion für Admin MQTT Client Singleton
    
    Returns:
        Admin MQTT Client Singleton Instance
    """
    return AdminMQTTClient()
