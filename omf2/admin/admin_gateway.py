#!/usr/bin/env python3
"""
Admin Gateway - Fassade für Admin Business-Operationen
"""

import logging
from typing import Dict, List, Optional, Any
from omf2.common.message_templates import get_message_templates

logger = logging.getLogger(__name__)


class AdminGateway:
    """
    Gateway für Admin-spezifische Business-Operationen
    
    Nutzt MessageTemplates und MQTT-Client für Admin-Operationen.
    Stellt Methoden für die UI bereit.
    """
    
    def __init__(self, mqtt_client=None, **kwargs):
        """
        Initialisiert Admin Gateway
        
        Args:
            mqtt_client: MQTT-Client für Admin (wird später implementiert)
        """
        self.mqtt_client = mqtt_client
        self.message_templates = get_message_templates()
        
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
            # Registry v2 Integration: Topic-Konfiguration prüfen
            topic_config = self.message_templates.get_topic_config(topic)
            if not topic_config:
                logger.warning(f"⚠️ No topic configuration found for {topic}")
                return None
            
            # Message aus Template rendern
            message = self.message_templates.render_message(topic, params or {})
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
            result = self.message_templates.validate_message(topic, message)
            logger.info(f"✅ Message validation for {topic}: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
            return result
            
        except Exception as e:
            logger.error(f"❌ Message validation failed for topic {topic}: {e}")
            return {"errors": [str(e)], "warnings": []}
    
    def publish_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """
        Message auf Topic publizieren
        
        Args:
            topic: MQTT Topic
            message: Message-Dict
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        try:
            # TODO: MQTT-Client Integration implementieren
            # qos, retain = self.message_templates.get_topic_config(topic)
            # success = self.mqtt_client.publish(topic, message, qos=qos, retain=retain)
            # if success:
            #     self.message_templates.log_message(topic, message, "SEND")
            # return success
            
            logger.info(f"📤 Published message to {topic}: {message} (TODO: MQTT integration)")
            self.message_templates.log_message(topic, message, "SEND")
            return True
            
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
            
            # Topics aus allen Topic-Dateien sammeln
            for topic_file, topic_data in self.message_templates.topics.items():
                topics_list = topic_data.get(f"{topic_file}_topics", [])
                for topic_config in topics_list:
                    topic = topic_config.get('topic')
                    if topic:
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
            mappings = self.message_templates.mappings.get('mappings', [])
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
            #     "templates_count": len(self.message_templates.get_all_templates()),
            #     "last_activity": self.mqtt_client.get_last_activity()
            # }
            
            status = {
                "mqtt_connected": False,  # TODO: MQTT integration
                "topics_count": len(self.get_all_topics()),
                "templates_count": len(self.message_templates.get_all_templates()),
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
            mqtt_clients = self.message_templates.mqtt_clients
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
            mqtt_clients = self.message_templates.mqtt_clients
            admin_client = mqtt_clients.get('mqtt_clients', {}).get('admin_mqtt_client', {})
            return admin_client.get('subscribed_topics', [])
        except Exception as e:
            logger.error(f"❌ Failed to get admin subscribed topics: {e}")
            return []
