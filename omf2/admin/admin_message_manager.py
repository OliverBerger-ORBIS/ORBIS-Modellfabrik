#!/usr/bin/env python3
"""
Admin Message Manager - Domain-spezifische Wrapper für generischen MessageManager
Nutzt den generischen MessageManager für Admin-spezifische Message-Operationen
"""

from typing import Any, Dict, List, Optional

from omf2.common.logger import get_logger
from omf2.common.message_manager import MessageManager
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


class AdminMessageManager:
    """
    Admin Message Manager - Domain-spezifische Wrapper für generischen MessageManager

    Verantwortlichkeiten:
    - Admin-spezifische Message-Operationen
    - Delegation an generischen MessageManager
    - Admin-spezifische Business-Logik
    """

    def __init__(self, registry_manager=None, mqtt_client=None):
        """
        Initialize Admin Message Manager

        Args:
            registry_manager: Registry Manager instance
            mqtt_client: MQTT Client for buffer operations
        """
        self.registry_manager = registry_manager or get_registry_manager()
        self.mqtt_client = mqtt_client

        # Verwende generischen MessageManager für Admin-Domain
        self.message_manager = MessageManager("admin", self.registry_manager, self.mqtt_client)

        logger.info("🏗️ Admin Message Manager initialized (using generic MessageManager)")

    def generate_message(self, topic: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Message für Topic generieren - Delegiert an generischen MessageManager

        Args:
            topic: MQTT Topic
            params: Parameter für Message-Generierung

        Returns:
            Generierte Message oder None
        """
        return self.message_manager.generate_message(topic, params)

    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Message gegen Schema validieren - Delegiert an generischen MessageManager

        Args:
            topic: MQTT Topic
            message: Message zum Validieren

        Returns:
            {"errors": [...], "warnings": [...]}
        """
        return self.message_manager.validate_message(topic, message)

    def get_all_message_buffers(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Alle Message-Buffers vom MQTT-Client abrufen - Delegiert an generischen MessageManager

        Returns:
            Dict mit Topic -> List[Message] Mappings
        """
        return self.message_manager.get_all_message_buffers()

    def clear_message_history(self) -> bool:
        """
        Komplette Message-Historie löschen - Delegiert an generischen MessageManager

        Returns:
            True wenn erfolgreich
        """
        return self.message_manager.clear_message_history()

    def get_message_count_by_topic(self) -> Dict[str, int]:
        """
        Message-Anzahl pro Topic abrufen - Delegiert an generischen MessageManager

        Returns:
            Dict mit Topic -> Anzahl Mappings
        """
        return self.message_manager.get_message_count_by_topic()

    def get_latest_message_by_topic(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        Neueste Message pro Topic abrufen - Delegiert an generischen MessageManager

        Returns:
            Dict mit Topic -> Latest Message Mappings
        """
        return self.message_manager.get_latest_message_by_topic()


def get_admin_message_manager(registry_manager=None, mqtt_client=None) -> AdminMessageManager:
    """
    Factory function für Admin Message Manager (Singleton Pattern)

    Args:
        registry_manager: Registry Manager instance
        mqtt_client: MQTT Client instance

    Returns:
        AdminMessageManager instance
    """
    if not hasattr(get_admin_message_manager, "_instance"):
        get_admin_message_manager._instance = AdminMessageManager(registry_manager, mqtt_client)
    return get_admin_message_manager._instance
