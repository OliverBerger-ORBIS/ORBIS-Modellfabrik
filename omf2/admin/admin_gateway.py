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
    
    def generate_message(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Message für Topic generieren - NEUE ARCHITEKTUR: topic-schema-payload
        
        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung
            
        Returns:
            Generierte Message oder None
        """
        try:
            # NEUE ARCHITEKTUR: Topic → Schema → Payload
            # 1. Topic-Konfiguration aus Registry laden
            topic_config = self.registry_manager.get_topic_config(topic)
            if not topic_config:
                logger.warning(f"⚠️ No topic configuration found for {topic}")
                return None
            
            # 2. Schema für Topic laden
            schema = self.registry_manager.get_topic_schema(topic)
            if not schema:
                logger.warning(f"⚠️ No schema found for topic {topic}")
                return None
            
            # 3. Message aus Schema und Parametern generieren
            message = params or {}
            
            # Schema-driven message generation
            # - Schema als Template verwenden
            # - Parameter in Schema-Struktur einfügen
            # - Default-Werte aus Schema laden
            if isinstance(schema, dict):
                # Merge parameters into schema structure
                if params:
                    # Deep merge parameters into schema
                    def deep_merge(base_dict, update_dict):
                        for key, value in update_dict.items():
                            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                                deep_merge(base_dict[key], value)
                            else:
                                base_dict[key] = value
                        return base_dict
                    
                    # Start with schema as base, merge parameters
                    message = deep_merge(schema.copy(), params)
                else:
                    # Use schema as-is if no parameters
                    message = schema.copy()
            else:
                # Fallback for non-dict schemas
                message = params or {}
            
            if message:
                logger.info(f"📤 Generated message for {topic} using schema")
                # Logging der Topic-Konfiguration
                qos = topic_config.get('qos', 1)
                retain = topic_config.get('retain', False)
                logger.info(f"📊 Topic config - QoS: {qos}, Retain: {retain}")
                return message
            else:
                logger.warning(f"⚠️ No parameters provided for {topic}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Message generation failed for topic {topic}: {e}")
            return None
    
    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Message gegen Schema validieren - NEUE ARCHITEKTUR: topic-schema-payload
        
        Args:
            topic: MQTT Topic
            message: Message zum Validieren
            
        Returns:
            {"errors": [...], "warnings": [...]}
        """
        try:
            # NEUE ARCHITEKTUR: Schema-basierte Validierung
            schema = self.registry_manager.get_topic_schema(topic)
            if not schema:
                logger.warning(f"⚠️ No schema found for topic {topic}")
                return {"errors": [f"No schema found for topic {topic}"], "warnings": []}
            
            # JSON Schema validation
            # - JSON Schema Library verwenden (jsonschema)
            # - Schema gegen Message validieren
            # - Detaillierte Fehler- und Warnungs-Messages
            result = {"errors": [], "warnings": []}
            
            try:
                import jsonschema
                # Validate message against schema
                jsonschema.validate(instance=message, schema=schema)
                logger.debug(f"✅ Message validation successful for {topic}")
            except ImportError:
                result["warnings"].append("jsonschema library not available - validation skipped")
                logger.warning("⚠️ jsonschema library not available - validation skipped")
            except jsonschema.ValidationError as e:
                result["errors"].append(f"Schema validation failed: {e.message}")
                logger.error(f"❌ Schema validation failed for {topic}: {e.message}")
            except Exception as e:
                result["errors"].append(f"Validation error: {str(e)}")
                logger.error(f"❌ Validation error for {topic}: {e}")
            logger.info(f"✅ Message validation for {topic}: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
            return result
            
        except Exception as e:
            logger.error(f"❌ Message validation failed for topic {topic}: {e}")
            return {"errors": [str(e)], "warnings": []}
    
    def generate_message_template(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        BACKWARD COMPATIBILITY: Alte generate_message_template() Methode
        Delegiert an neue generate_message() Methode
        
        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung
            
        Returns:
            Generierte Message oder None
        """
        logger.warning(f"⚠️ DEPRECATED: generate_message_template() is deprecated, use generate_message() instead")
        return self.generate_message(topic, params)
    
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
    
    def get_topic_schemas(self) -> Dict[str, Dict]:
        """
        Topic-Schema Mappings abrufen - NEUE ARCHITEKTUR: topic-schema-payload
        
        Returns:
            Dict mit Topic-Schema Mappings
        """
        try:
            # NEUE ARCHITEKTUR: Topic → Schema Beziehung
            # Get topics from registry manager
            try:
                # Try to get topics from registry manager
                if hasattr(self.registry_manager, 'get_all_topics'):
                    all_topics = self.registry_manager.get_all_topics()
                else:
                    # Fallback: get topics from mqtt_clients configuration
                    mqtt_clients = self.registry_manager.get_mqtt_clients()
                    all_topics = []
                    for client_name, client_config in mqtt_clients.items():
                        if isinstance(client_config, dict):
                            subscribed_topics = client_config.get('subscribed_topics', [])
                            for topic_info in subscribed_topics:
                                if isinstance(topic_info, dict):
                                    topic = topic_info.get('topic', '')
                                else:
                                    topic = str(topic_info)
                                if topic and topic not in all_topics:
                                    all_topics.append(topic)
                
                topic_schemas = {}
                for topic in all_topics:
                    schema = self.registry_manager.get_topic_schema(topic)
                    if schema:
                        topic_schemas[topic] = schema
                        
            except Exception as e:
                logger.warning(f"⚠️ Failed to get topics from registry: {e}")
                topic_schemas = {}
            
            logger.info(f"📊 Retrieved {len(topic_schemas)} topic-schema mappings")
            return topic_schemas
            
        except Exception as e:
            logger.error(f"❌ Failed to get topic schemas: {e}")
            return {}
    
    def get_topic_templates(self) -> Dict[str, str]:
        """
        BACKWARD COMPATIBILITY: Alte get_topic_templates() Methode
        Delegiert an neue get_topic_schemas() Methode
        
        Returns:
            Dict mit Topic-Schema Mappings (als String-Repräsentation)
        """
        logger.warning(f"⚠️ DEPRECATED: get_topic_templates() is deprecated, use get_topic_schemas() instead")
        schemas = self.get_topic_schemas()
        # Convert schemas to string representation for backward compatibility
        return {topic: str(schema) for topic, schema in schemas.items()}
    
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
