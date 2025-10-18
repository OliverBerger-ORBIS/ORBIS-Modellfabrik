#!/usr/bin/env python3
"""
Monitor Manager - Business Logic für Message Monitor
"""

from typing import Any, Dict, List, Optional

from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import RegistryManager

logger = get_logger(__name__)


class MonitorManager:
    """
    Monitor Manager für CCU Message Monitor

    Verantwortlichkeiten:
    - Topic-Klassifizierung (FTS, Module, CCU, TXT)
    - Filter-Listen Verwaltung
    - Business Logic für Message Monitor
    """

    def __init__(self, registry_manager: Optional[RegistryManager] = None):
        """
        Initialisiert Monitor Manager

        Args:
            registry_manager: Registry Manager Instanz
        """
        self.registry_manager = registry_manager or RegistryManager()
        self.all_topics = []
        self.module_fts_topics = []
        self.ccu_topics = []
        self.txt_topics = []
        self.other_topics = []

    def classify_topic(self, topic: str) -> str:
        """
        Klassifiziert Topic nach Typ

        Args:
            topic: Topic-String

        Returns:
            Topic-Typ: "FTS", "Module", "CCU", "TXT", "Other"
        """
        try:
            if topic.startswith("fts/v1/ff/"):
                return "FTS"
            elif topic.startswith("module/v1/ff/"):
                return "Module"
            elif topic.startswith("ccu/"):
                return "CCU"
            elif "/j1/txt/" in topic:
                return "TXT"
            else:
                return "Other"
        except Exception as e:
            logger.error(f"❌ Failed to classify topic {topic}: {e}")
            return "Other"

    def process_message(self, topic: str, payload: Any, meta: Optional[Dict] = None):
        """
        Verarbeitet eingehende Message für Monitor

        Args:
            topic: MQTT Topic
            payload: Message Payload
            meta: Message Metadaten
        """
        try:
            # Topic zur entsprechenden Liste hinzufügen
            if topic not in self.all_topics:
                self.all_topics.append(topic)

                topic_type = self.classify_topic(topic)

                if topic_type in ["FTS", "Module"]:
                    if topic not in self.module_fts_topics:
                        self.module_fts_topics.append(topic)
                elif topic_type == "CCU":
                    if topic not in self.ccu_topics:
                        self.ccu_topics.append(topic)
                elif topic_type == "TXT":
                    if topic not in self.txt_topics:
                        self.txt_topics.append(topic)
                else:
                    if topic not in self.other_topics:
                        self.other_topics.append(topic)

                logger.debug(f"📊 Topic {topic} classified as {topic_type}")

        except Exception as e:
            logger.error(f"❌ Failed to process message for topic {topic}: {e}")

    def get_filter_lists(self) -> Dict[str, List[str]]:
        """
        Gibt alle Filter-Listen zurück

        Returns:
            Dictionary mit verschiedenen Topic-Listen
        """
        try:
            return {
                "all_topics": sorted(self.all_topics),
                "module_fts_topics": sorted(self.module_fts_topics),
                "ccu_topics": sorted(self.ccu_topics),
                "txt_topics": sorted(self.txt_topics),
                "other_topics": sorted(self.other_topics),
            }
        except Exception as e:
            logger.error(f"❌ Failed to get filter lists: {e}")
            return {"all_topics": [], "module_fts_topics": [], "ccu_topics": [], "txt_topics": [], "other_topics": []}

    def get_topic_count(self) -> Dict[str, int]:
        """
        Gibt Topic-Anzahl pro Typ zurück

        Returns:
            Dictionary mit Topic-Anzahl pro Typ
        """
        try:
            return {
                "all": len(self.all_topics),
                "module_fts": len(self.module_fts_topics),
                "ccu": len(self.ccu_topics),
                "txt": len(self.txt_topics),
                "other": len(self.other_topics),
            }
        except Exception as e:
            logger.error(f"❌ Failed to get topic count: {e}")
            return {"all": 0, "module_fts": 0, "ccu": 0, "txt": 0, "other": 0}

    def clear_topics(self):
        """Löscht alle Topic-Listen"""
        try:
            self.all_topics.clear()
            self.module_fts_topics.clear()
            self.ccu_topics.clear()
            self.txt_topics.clear()
            self.other_topics.clear()
            logger.debug("🧹 All topic lists cleared")
        except Exception as e:
            logger.error(f"❌ Failed to clear topics: {e}")


# Singleton Pattern
_monitor_manager = None


def get_monitor_manager(registry_manager: Optional[RegistryManager] = None) -> MonitorManager:
    """
    Singleton Pattern für Monitor Manager

    Args:
        registry_manager: Registry Manager Instanz

    Returns:
        MonitorManager Instanz
    """
    global _monitor_manager
    if _monitor_manager is None:
        _monitor_manager = MonitorManager(registry_manager)
    return _monitor_manager
