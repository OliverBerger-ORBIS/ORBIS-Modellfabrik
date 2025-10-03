#!/usr/bin/env python3
"""
Admin Gateway - Fassade für Admin Business-Operationen
"""

import logging
import json
from typing import Dict, List, Optional, Any
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.admin.admin_message_manager import get_admin_message_manager
from omf2.common.topic_manager import get_admin_topic_manager

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
        
        # Initialize Message Manager
        self.message_manager = get_admin_message_manager(
            registry_manager=self.registry_manager,
            mqtt_client=self.mqtt_client
        )
        
        # Initialize Topic Manager
        self.topic_manager = get_admin_topic_manager(
            registry_manager=self.registry_manager
        )
        
        logger.info("🏗️ Admin Gateway initialized")
    
    def generate_message(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Message für Topic generieren - Delegiert an Message Manager
        
        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung
            
        Returns:
            Generierte Message oder None
        """
        return self.message_manager.generate_message(topic, params)
    
    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Message gegen Schema validieren - Delegiert an Message Manager
        
        Args:
            topic: MQTT Topic
            message: Message zum Validieren
            
        Returns:
            {"errors": [...], "warnings": [...]}
        """
        return self.message_manager.validate_message(topic, message)
    
    
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
                # Message logging via registry manager
                try:
                    # Log message to registry for audit trail
                    self.registry_manager.log_message(topic, message, "published")
                    logger.info(f"📤 Message logged to registry: {topic}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to log message to registry: {e}")
                    logger.info(f"📤 Message published: {topic}")
            else:
                logger.error(f"❌ Failed to publish message to {topic}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Publish message failed for topic {topic}: {e}")
            return False
    
    def get_all_topics(self) -> List[str]:
        """
        Alle Topics aus Registry abrufen - Delegiert an Topic Manager
        
        Returns:
            Liste aller Topics
        """
        return self.topic_manager.get_all_topics()
    
    def get_topic_schemas(self) -> Dict[str, Dict]:
        """
        Topic-Schema Mappings abrufen - Delegiert an Topic Manager
        
        Returns:
            Dict mit Topic-Schema Mappings
        """
        return self.topic_manager.get_topic_schemas()
    
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        System Status abrufen
        
        Returns:
            System Status Dict
        """
        try:
            # MQTT integration for system status
            mqtt_connected = False
            last_activity = "2025-09-28T16:24:55Z"  # Default fallback
            
            if self.mqtt_client:
                try:
                    mqtt_connected = self.mqtt_client.connected
                    # Get last activity from MQTT client if available
                    if hasattr(self.mqtt_client, 'get_last_activity'):
                        last_activity = self.mqtt_client.get_last_activity()
                except Exception as e:
                    logger.warning(f"⚠️ Failed to get MQTT status: {e}")
            
            status = {
                "mqtt_connected": mqtt_connected,
                "topics_count": len(self.get_all_topics()),
                "schemas_count": len(self.registry_manager.get_schemas()) if hasattr(self.registry_manager, 'get_schemas') else 0,
                "last_activity": last_activity
            }
            
            logger.info(f"📊 System status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
            return {}
    
    def get_published_topics(self) -> List[str]:
        """
        Admin Published Topics aus Registry abrufen - Delegiert an Topic Manager
        
        Returns:
            Liste der Published Topics
        """
        return self.topic_manager.get_published_topics()
    
    def get_subscribed_topics(self) -> List[str]:
        """
        Admin Subscribed Topics aus Registry abrufen - Delegiert an Topic Manager
        
        Returns:
            Liste der Subscribed Topics
        """
        return self.topic_manager.get_subscribed_topics()
    
    # ===== Message Buffer Management Methods =====
    
    def get_all_message_buffers(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Alle Message-Buffers vom MQTT-Client abrufen - Delegiert an Message Manager
        
        Returns:
            Dict mit Topic -> List[Message] Mappings
        """
        return self.message_manager.get_all_message_buffers()
    
    def clear_message_history(self) -> bool:
        """
        Komplette Message-Historie löschen - Delegiert an Message Manager
        
        Returns:
            True wenn erfolgreich
        """
        return self.message_manager.clear_message_history()
    
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
