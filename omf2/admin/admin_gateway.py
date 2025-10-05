#!/usr/bin/env python3
"""
Admin Gateway - Fassade für Admin Business-Operationen
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.admin.admin_message_manager import get_admin_message_manager
from omf2.common.topic_manager import get_admin_topic_manager
from omf2.common.logger import get_logger

logger = get_logger("omf2.admin.admin_gateway")


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
    
    def on_mqtt_message(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None):
        """
        Gateway-Routing mit Schema-Validierung für Admin Messages
        
        Diese Methode wird vom admin_mqtt_client im on_message Callback aufgerufen.
        Sie implementiert das Gateway-Pattern für Topic-Routing mit Schema-Validierung.
        
        Args:
            topic: MQTT Topic (String)
            message: Payload-Daten (Dict, List, str) - NIE raw bytes!
            meta: Metadaten (timestamp, raw, qos, retain)
        
        Returns:
            bool: True wenn Message verarbeitet wurde, False bei Fehler
        """
        try:
            logger.debug(f"🔀 Admin Gateway processing message for topic: {topic}")
            
            # 1. Schema aus Registry holen
            schema = self.registry_manager.get_topic_schema(topic)
            
            # 2. Schema-Validierung (wenn Schema vorhanden)
            if schema:
                logger.debug(f"📋 Found schema for topic {topic}, validating payload")
                validated_message = self._validate_message(topic, message, schema)
                if not validated_message:
                    logger.warning(f"⚠️ Message rejected due to schema validation failure: {topic}")
                    return False  # Validierung fehlgeschlagen
            else:
                validated_message = message
                logger.debug(f"📋 No schema found for topic {topic}, skipping validation")
            
            # 3. Gateway-Routing mit validierter Message
            logger.debug(f"📤 Routing validated message to message center: {topic}")
            return self._route_admin_message(topic, validated_message, meta)
            
        except Exception as e:
            logger.error(f"❌ Admin Gateway processing failed for topic {topic}: {e}")
            return False
    
    def _validate_message(self, topic: str, message: Union[Dict, List, str], schema: Dict) -> Optional[Union[Dict, List, str]]:
        """
        Validiert Message gegen Schema
        
        Args:
            topic: MQTT Topic
            message: Message-Daten
            schema: JSON-Schema
            
        Returns:
            Validierte Message oder None bei Fehler
        """
        try:
            import jsonschema
            
            # Schema-Validierung starten
            logger.debug(f"🔍 Validating schema for topic: {topic}")
            
            jsonschema.validate(instance=message, schema=schema)
            
            # Erfolgreiche Validierung
            logger.debug(f"✅ Schema validation successful for {topic}")
            return message
            
        except ImportError:
            logger.warning(f"⚠️ jsonschema library not available, skipping validation for {topic}")
            return message
            
        except jsonschema.ValidationError as e:
            # Schema-Validierung fehlgeschlagen - Detailliertes Logging für Troubleshooting
            logger.warning(f"❌ Schema validation failed for {topic}: {e.message}")
            logger.warning(f"   Schema: {schema}")
            logger.warning(f"   Payload: {str(message)[:200]}...")  # Erste 200 Zeichen des Payloads
            logger.warning(f"   → Troubleshooting: Prüfe Registry-Topic-Schema Beziehung, Schema-Flexibilität oder MQTT-Sender")
            return None
            
        except Exception as e:
            logger.error(f"❌ Validation error for {topic}: {e}")
            return None
    
    def _route_admin_message(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None) -> bool:
        """
        Admin Message-Routing - Alle Topics werden verarbeitet
        
        Admin Gateway empfängt ALLE Topics (subscribed zu "#") und leitet sie weiter.
        Hauptzweck: Weiterleitung an Message Center für Monitoring/Übersicht.
        
        Args:
            topic: MQTT Topic (alle Topics werden verarbeitet)
            message: Validierte Message
            meta: Metadaten
            
        Returns:
            True wenn Message verarbeitet wurde
        """
        try:
            logger.debug(f"📋 Admin Gateway routing ALL topics: {topic}")
            
            # Alle Topics an Message Center weiterleiten
            self._handle_message_center(topic, message, meta)
            
            # Optional: Weitere Weiterleitungen (aber nicht als elif!)
            if self._should_log_to_audit(topic, message):
                self._handle_audit_log(topic, message, meta)
            
            if self._should_alert_admin(topic, message):
                self._handle_admin_alert(topic, message, meta)
                
            return True
                
        except Exception as e:
            logger.error(f"❌ Admin message routing failed for {topic}: {e}")
            return False
    
    def _handle_message_center(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None):
        """Alle Topics an Message Center weiterleiten"""
        # Delegiert an Message Manager für Buffer-Update
        if self.message_manager:
            logger.debug(f"📋 Routing to message center: {topic}")
            # Message Manager für Admin-Monitoring und Übersicht
            # Hier wird die Message für das Message Center verarbeitet
            # TODO: Hier könnte die Message tatsächlich an das Message Center weitergeleitet werden
    
    def _should_log_to_audit(self, topic: str, message: Union[Dict, List, str]) -> bool:
        """Prüft ob Topic für Audit-Log relevant ist"""
        # Beispiel: Alle CCU-Topics für Audit-Log
        return topic.startswith("ccu/") or topic.startswith("module/")
    
    def _handle_audit_log(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None):
        """Behandelt Audit-Logging"""
        logger.debug(f"📝 Audit log: {topic}")
        # Audit-Logging für wichtige Topics
    
    def _should_alert_admin(self, topic: str, message: Union[Dict, List, str]) -> bool:
        """Prüft ob Admin-Alert nötig ist"""
        # Beispiel: Error-Topics oder kritische States
        return "error" in topic.lower() or "critical" in str(message).lower()
    
    def _handle_admin_alert(self, topic: str, message: Union[Dict, List, str], meta: Optional[Dict] = None):
        """Behandelt Admin-Alerts"""
        logger.warning(f"🚨 Admin alert for topic: {topic}")
        # Admin-Alert für kritische Topics

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
