#!/usr/bin/env python3
"""
Generic Message Manager - Domain-agnostische Message-Generierung und -Validierung
Kann von allen Domänen (Admin, CCU, Node-RED) verwendet werden
"""

from typing import Any, Dict, List, Optional

from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


class MessageManager:
    """
    Generic Message Manager - Domain-agnostische Business-Logik für Message-Operationen

    Verantwortlichkeiten:
    - Schema-driven Message-Generierung (für alle Domänen)
    - JSON Schema Validierung (für alle Domänen)
    - Message Buffer Management (domain-spezifisch)
    - Message History Management (domain-spezifisch)

    Kann von Admin, CCU, Node-RED und anderen Domänen verwendet werden.
    """

    def __init__(self, domain: str, registry_manager=None, mqtt_client=None):
        """
        Initialize Generic Message Manager

        Args:
            domain: Domain name (e.g., 'admin', 'ccu', 'nodered')
            registry_manager: Registry Manager instance
            mqtt_client: MQTT Client for buffer operations
        """
        self.domain = domain
        self.registry_manager = registry_manager or get_registry_manager()
        self.mqtt_client = mqtt_client

        logger.info(f"🏗️ {domain.title()} Message Manager initialized")

    def generate_message(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Message für Topic generieren - Schema-driven Approach (Domain-agnostisch)

        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung

        Returns:
            Generierte Message oder None
        """
        try:
            # Schema-driven Message Generation: Topic → Schema → Payload
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
            if isinstance(schema, dict):
                # Merge parameters into schema structure
                if params:
                    # Deep merge parameters into schema
                    message = self._deep_merge(schema.copy(), params)
                else:
                    # Use schema as-is if no parameters
                    message = schema.copy()
            else:
                # Fallback for non-dict schemas
                message = params or {}

            # Ergänze Pflichtfelder, die häufig schemagebunden sind (z.B. timestamp)
            if isinstance(schema, dict):
                try:
                    required_fields = schema.get("required", []) or []
                    if "timestamp" in required_fields and "timestamp" not in message:
                        # Nur setzen, wenn top-level timestamp im Schema definiert ist
                        # und als date-time formatiert werden soll (falls angegeben)
                        from datetime import datetime

                        message["timestamp"] = datetime.now().isoformat()
                except Exception:
                    # Defensive: fehlertolerant bleiben – kein harter Abbruch der Generierung
                    pass

            if message:
                logger.info(f"📤 [{self.domain}] Generated message for {topic} using schema")
                # Log topic configuration
                qos = topic_config.get("qos", 1)
                retain = topic_config.get("retain", False)
                logger.debug(f"📊 Topic config - QoS: {qos}, Retain: {retain}")
                return message
            else:
                logger.warning(f"⚠️ [{self.domain}] No parameters provided for {topic}")
                return None

        except Exception as e:
            logger.error(f"❌ [{self.domain}] Message generation failed for topic {topic}: {e}")
            return None

    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Message gegen Schema validieren - Schema-driven Validation (Domain-agnostisch)

        Args:
            topic: MQTT Topic
            message: Message zum Validieren

        Returns:
            {"errors": [...], "warnings": [...]}
        """
        try:
            # Schema-basierte Validierung
            schema = self.registry_manager.get_topic_schema(topic)
            if not schema:
                logger.warning(f"⚠️ [{self.domain}] No schema found for topic {topic}")
                return {"errors": [f"No schema found for topic {topic}"], "warnings": []}

            result = {"errors": [], "warnings": []}

            try:
                import jsonschema

                # Validate message against schema
                jsonschema.validate(instance=message, schema=schema)
                logger.debug(f"✅ [{self.domain}] Message validation successful for {topic}")
            except ImportError:
                result["warnings"].append("jsonschema library not available - validation skipped")
                logger.warning(f"⚠️ [{self.domain}] jsonschema library not available - validation skipped")
            except jsonschema.ValidationError as e:
                result["errors"].append(f"Schema validation failed: {e.message}")
                logger.error(f"❌ [{self.domain}] Schema validation failed for {topic}: {e.message}")
            except Exception as e:
                result["errors"].append(f"Validation error: {str(e)}")
                logger.error(f"❌ [{self.domain}] Validation error for {topic}: {e}")

            logger.info(
                f"✅ [{self.domain}] Message validation for {topic}: {len(result['errors'])} errors, {len(result['warnings'])} warnings"
            )
            return result

        except Exception as e:
            logger.error(f"❌ [{self.domain}] Message validation failed for topic {topic}: {e}")
            return {"errors": [str(e)], "warnings": []}

    def get_all_message_buffers(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Alle Message-Buffers vom MQTT-Client abrufen (Domain-spezifisch)

        Returns:
            Dict mit Topic -> List[Message] Mappings
        """
        try:
            if not self.mqtt_client:
                logger.warning(f"⚠️ [{self.domain}] No MQTT client available")
                return {}

            buffers = self.mqtt_client.get_all_buffers()
            logger.debug(f"📊 [{self.domain}] Retrieved {len(buffers)} message buffers")
            return buffers

        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get message buffers: {e}")
            return {}

    def clear_message_history(self) -> bool:
        """
        Komplette Message-Historie löschen (Domain-spezifisch)

        Returns:
            True wenn erfolgreich
        """
        try:
            if not self.mqtt_client:
                logger.warning(f"⚠️ [{self.domain}] No MQTT client available")
                return False

            # MQTT-Client hat clear_buffers() Methode
            self.mqtt_client.clear_buffers()
            logger.info(f"🗑️ [{self.domain}] Message history cleared")
            return True

        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to clear message history: {e}")
            return False

    def get_message_count_by_topic(self) -> Dict[str, int]:
        """
        Message-Anzahl pro Topic abrufen (Domain-agnostisch)

        Returns:
            Dict mit Topic -> Anzahl Mappings
        """
        try:
            buffers = self.get_all_message_buffers()
            counts = {}

            for topic, messages in buffers.items():
                counts[topic] = len(messages) if messages else 0

            logger.debug(f"📊 [{self.domain}] Message counts: {counts}")
            return counts

        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get message counts: {e}")
            return {}

    def get_latest_message_by_topic(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Neueste Message pro Topic abrufen (Domain-agnostisch)

        Returns:
            Dict mit Topic -> Latest Message Mappings
        """
        try:
            buffers = self.get_all_message_buffers()
            latest = {}

            for topic, messages in buffers.items():
                if messages and len(messages) > 0:
                    # Messages sind chronologisch sortiert, neueste ist die letzte
                    latest[topic] = messages[-1]
                else:
                    latest[topic] = None

            logger.debug(
                f"📊 [{self.domain}] Latest messages: {len([m for m in latest.values() if m])} topics with messages"
            )
            return latest

        except Exception as e:
            logger.error(f"❌ [{self.domain}] Failed to get latest messages: {e}")
            return {}

    def _deep_merge(self, base_dict: Dict, update_dict: Dict) -> Dict:
        """
        Deep merge von zwei Dictionaries (Domain-agnostisch)

        Args:
            base_dict: Base Dictionary
            update_dict: Update Dictionary

        Returns:
            Merged Dictionary
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict


# Domain-specific Factory Functions
def get_admin_message_manager(registry_manager=None, mqtt_client=None) -> MessageManager:
    """Factory function für Admin Message Manager"""
    return MessageManager("admin", registry_manager, mqtt_client)


def get_ccu_message_manager(registry_manager=None, mqtt_client=None) -> MessageManager:
    """Factory function für CCU Message Manager"""
    return MessageManager("ccu", registry_manager, mqtt_client)


def get_nodered_message_manager(registry_manager=None, mqtt_client=None) -> MessageManager:
    """Factory function für Node-RED Message Manager"""
    return MessageManager("nodered", registry_manager, mqtt_client)


def get_message_manager(domain: str, registry_manager=None, mqtt_client=None) -> MessageManager:
    """
    Generic factory function für Message Manager

    Args:
        domain: Domain name (e.g., 'admin', 'ccu', 'nodered')
        registry_manager: Registry Manager instance
        mqtt_client: MQTT Client instance

    Returns:
        MessageManager instance für die angegebene Domain
    """
    return MessageManager(domain, registry_manager, mqtt_client)
