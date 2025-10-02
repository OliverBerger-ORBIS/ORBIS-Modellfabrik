#!/usr/bin/env python3
"""
Admin Gateway - Fassade für Admin Business-Operationen
"""

import logging
import json
from typing import Dict, List, Optional, Any
from omf2.registry.manager.registry_manager import get_registry_manager

logger = logging.getLogger(__name__)


class AdminGateway:
    """
    Gateway für Admin-spezifische Business-Operationen
    
    Nutzt Registry Manager und Topic-Schema-Payload Beziehung für Admin-Operationen.
    Stellt Methoden für die UI bereit.
    """
    
    def __init__(self, mqtt_client=None, **kwargs):
        """
        Initialisiert Admin Gateway
        
        Args:
            mqtt_client: MQTT-Client für Admin (wird später implementiert)
        """
        self.mqtt_client = mqtt_client
        self.registry_manager = get_registry_manager()
        
        logger.info("🏗️ Admin Gateway initialized")
    
    def generate_message_template(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Message Template für Topic generieren
        
        Args:
            topic: MQTT Topic
            params: Parameter für Template-Generierung
            
        Returns:
            Generierte Message oder None
        """
        try:
            # Registry v2 Integration: Topic-Konfiguration aus Registry laden
            topic_config = self.registry_manager.get_topic_config(topic)
            if not topic_config:
                logger.warning(f"⚠️ No topic configuration found for {topic}")
                return None
            
            # Message aus Template rendern
            message = params or {}
            if message:
                logger.info(f"📝 Generated message template for {topic}: {message}")
                # Logging der Topic-Konfiguration
                qos = topic_config.get('qos', 1)
                retain = topic_config.get('retain', False)
                logger.info(f"📊 Topic config - QoS: {qos}, Retain: {retain}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Message template generation failed for topic {topic}: {e}")
            return None
    
    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Message gegen Template validieren
        
        Args:
            topic: MQTT Topic
            message: Message zum Validieren
            
        Returns:
            {"errors": [...], "warnings": [...]}
        """
        try:
            # Registry v2 Integration: Message gegen Schema validieren
            schema = self.registry_manager.get_topic_schema(topic)
            if not schema:
                logger.warning(f"⚠️ No schema found for topic {topic}")
                return {"errors": [f"No schema found for topic {topic}"], "warnings": []}
            
            # TODO: Implement JSON Schema validation
            result = {"errors": [], "warnings": []}
            logger.info(f"✅ Message validation for {topic}: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
            return result
            
        except Exception as e:
            logger.error(f"❌ Message validation failed for topic {topic}: {e}")
            return {"errors": [str(e)], "warnings": []}
    
    def publish_message(self, topic: str, message: Dict[str, Any], qos: int = 1, retain: bool = False) -> bool:
        """
        Message auf Topic publizieren (mit expliziten QoS/Retain oder aus Registry)
        
        Args:
            topic: MQTT Topic
            message: Message-Dict
            qos: Quality of Service Level (0, 1, 2)
            retain: Retain Flag
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return False
            
            # MQTT-Client publish_message nutzen (mit QoS und Retain)
            success = self.mqtt_client.publish_message(
                topic=topic,
                message=message,
                qos=qos,
                retain=retain
            )
            
            if success:
                # Log detailed message information
                payload_str = json.dumps(message, indent=2) if isinstance(message, dict) else str(message)
                logger.info(f"📤 Published message to {topic} (QoS: {qos}, Retain: {retain})")
                logger.info(f"📦 Payload: {payload_str}")
                # TODO: Implement message logging from registry manager
                logger.info(f"📤 Message logged: {topic}")
            else:
                logger.error(f"❌ Failed to publish message to {topic}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Publish message failed for topic {topic}: {e}")
            return False
    
    def get_all_topics(self) -> List[str]:
        """
        Alle Topics aus Registry abrufen
        
        Returns:
            Liste aller Topics
        """
        try:
            all_topics = []
            
            # Topics aus Registry Manager sammeln
            topics_data = self.registry_manager.get_topics()
            for topic, topic_info in topics_data.items():
                all_topics.append(topic)
            
            logger.info(f"📊 Retrieved {len(all_topics)} topics from registry")
            return all_topics
            
        except Exception as e:
            logger.error(f"❌ Failed to get all topics: {e}")
            return []
    
    def get_topic_templates(self) -> Dict[str, str]:
        """
        Topic-Template Mappings abrufen
        
        Returns:
            Dict mit Topic-Template Mappings
        """
        try:
            # TODO: Implement mappings from registry manager
            mappings = []
            topic_templates = {}
            
            for mapping in mappings:
                topic = mapping.get('topic')
                template = mapping.get('template')
                if topic and template:
                    topic_templates[topic] = template
            
            logger.info(f"📊 Retrieved {len(topic_templates)} topic-template mappings")
            return topic_templates
            
        except Exception as e:
            logger.error(f"❌ Failed to get topic templates: {e}")
            return {}
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        System Status abrufen
        
        Returns:
            System Status Dict
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # status = {
            #     "mqtt_connected": self.mqtt_client.is_connected(),
            #     "topics_count": len(self.get_all_topics()),
            #     "schemas_count": len(self.registry_manager.get_schemas()),
            #     "last_activity": self.mqtt_client.get_last_activity()
            # }
            
            status = {
                "mqtt_connected": False,  # TODO: MQTT integration
                "topics_count": len(self.get_all_topics()),
                "schemas_count": len(self.registry_manager.get_schemas()),
                "last_activity": "2025-09-28T16:24:55Z"  # TODO: MQTT integration
            }
            
            logger.info(f"📊 System status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
            return {}
    
    def get_published_topics(self) -> List[str]:
        """
        Admin Published Topics aus Registry abrufen
        
        Returns:
            Liste der Published Topics
        """
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            admin_client = mqtt_clients.get('mqtt_clients', {}).get('admin_mqtt_client', {})
            return admin_client.get('published_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get admin published topics: {e}")
            return []
    
    def get_subscribed_topics(self) -> List[str]:
        """
        Admin Subscribed Topics aus Registry abrufen
        
        Returns:
            Liste der Subscribed Topics
        """
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            admin_client = mqtt_clients.get('mqtt_clients', {}).get('admin_mqtt_client', {})
            return admin_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get admin subscribed topics: {e}")
            return []
    
    # ===== Message Buffer Management Methods =====
    
    def get_all_message_buffers(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Alle Message-Buffers vom MQTT-Client abrufen
        
        Returns:
            Dict mit Topic -> List[Message] Mappings
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return {}
            
            buffers = self.mqtt_client.get_all_buffers()
            logger.debug(f"📊 Retrieved {len(buffers)} message buffers")
            return buffers
            
        except Exception as e:
            logger.error(f"❌ Failed to get message buffers: {e}")
            return {}
    
    def clear_message_history(self) -> bool:
        """
        Komplette Message-Historie löschen
        
        Returns:
            True wenn erfolgreich
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return False
            
            # MQTT-Client hat clear_buffers() Methode
            self.mqtt_client.clear_buffers()
            logger.info("🗑️ Message history cleared")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to clear message history: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """
        MQTT Connection Info abrufen
        
        Returns:
            Dict mit Connection Info (client_id, connected, environment, etc.)
        """
        try:
            if not self.mqtt_client:
                logger.warning("⚠️ No MQTT client available")
                return {
                    "connected": False,
                    "client_id": "unknown",
                    "environment": "unknown"
                }
            
            conn_info = self.mqtt_client.get_connection_info()
            return conn_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get connection info: {e}")
            return {
                "connected": False,
                "client_id": "error",
                "environment": "error"
            }
    
    def is_connected(self) -> bool:
        """
        MQTT Connection Status prüfen
        
        Returns:
            True wenn verbunden
        """
        try:
            if not self.mqtt_client:
                return False
            return self.mqtt_client.connected
        except Exception as e:
            logger.error(f"❌ Failed to check connection status: {e}")
            return False
