from omf.tools.logging_config import get_logger
"""
Topic Filter Manager - Handles topic filtering and categorization
"""

import logging
from typing import Dict, List

from omf.tools.topic_manager import OmfTopicManager

logger = get_logger(__name__)


class TopicFilterManager:
    """Manages topic filtering and categorization based on OMF configuration"""

    def __init__(self):
        self.topic_manager = OmfTopicManager()

    def get_topic_categories(self, topics: List[str]) -> Dict[str, List[str]]:
        """Gruppiert Topics nach Kategorien basierend auf OMF Config"""
        logger.info(f"Verfügbare Topics: {topics}")
        categories = {}

        for topic in topics:
            try:
                topic_info = self.topic_manager.get_topic_info(topic)
                category = topic_info.get("category", "Unknown")
                logger.debug(f"Topic {topic} -> Kategorie: {category}")

                if category not in categories:
                    categories[category] = []
                categories[category].append(topic)
            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten von Topic {topic}: {e}")
                category = "Unknown"
                if category not in categories:
                    categories[category] = []
                categories[category].append(topic)

        logger.debug(f"Topic-Kategorien: {categories}")
        return categories

    def get_topic_subcategories(self, topics: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """Gruppiert Topics nach Kategorien und Sub-Kategorien basierend auf OMF Config"""
        logger.debug(f"Verfügbare Topics für Sub-Kategorien: {topics}")

        subcategories = {}

        for topic in topics:
            try:
                topic_info = self.topic_manager.get_topic_info(topic)
                category = topic_info.get("category", "Unknown")
                sub_category = topic_info.get("sub_category", "Sonstige")

                logger.debug(f"Topic {topic} -> Kategorie: {category}, Sub-Kategorie: {sub_category}")

                if category not in subcategories:
                    subcategories[category] = {}
                if sub_category not in subcategories[category]:
                    subcategories[category][sub_category] = []
                subcategories[category][sub_category].append(topic)
            except Exception as e:
                logger.error(f"Fehler beim Sub-Kategorisieren von Topic {topic}: {e}")
                # Fallback: Kategorie und Sub-Kategorie aus Topic-Name ableiten
                category, sub_category = self._get_fallback_category_subcategory(topic)

                if category not in subcategories:
                    subcategories[category] = {}
                if sub_category not in subcategories[category]:
                    subcategories[category][sub_category] = []
                subcategories[category][sub_category].append(topic)

        logger.debug(f"Topic-Sub-Kategorien: {subcategories}")
        return subcategories

    def _get_fallback_category_subcategory(self, topic: str) -> tuple[str, str]:
        """Fallback-Logik für Kategorie und Sub-Kategorie basierend auf Topic-Name"""
        if topic.startswith("ccu/"):
            category = "CCU"
            if "state" in topic:
                sub_category = "State"
            elif "control" in topic or "set" in topic:
                sub_category = "Control"
            elif "order" in topic:
                sub_category = "Order"
            elif "status" in topic or "pairing" in topic:
                sub_category = "Status"
            else:
                sub_category = "Sonstige"
        elif topic.startswith("module/"):
            category = "MODULE"
            if "connection" in topic:
                sub_category = "Connection"
            elif "factsheet" in topic:
                sub_category = "Factsheet"
            elif "instantAction" in topic:
                sub_category = "InstantAction"
            elif "order" in topic:
                sub_category = "Order"
            elif "state" in topic:
                sub_category = "State"
            else:
                sub_category = "Sonstige"
        elif topic.startswith("/j1/txt/"):
            category = "TXT"
            if "/f/i/" in topic:
                sub_category = "Function Input"
            elif "/f/o/" in topic:
                sub_category = "Function Output"
            elif "/i/" in topic:
                sub_category = "Input"
            elif "/o/" in topic:
                sub_category = "Output"
            elif "/c/" in topic:
                sub_category = "Control"
            else:
                sub_category = "General"
        elif topic.startswith("fts/"):
            category = "FTS"
            if "connection" in topic:
                sub_category = "Connection"
            elif "factsheet" in topic:
                sub_category = "Factsheet"
            elif "instantAction" in topic:
                sub_category = "InstantAction"
            elif "order" in topic:
                sub_category = "Order"
            elif "state" in topic:
                sub_category = "State"
            else:
                sub_category = "Sonstige"
        else:
            category = "Unknown"
            sub_category = "Sonstige"

        return category, sub_category

    def filter_topics_by_category(self, topics: List[str], selected_categories: List[str]) -> List[str]:
        """Filtert Topics basierend auf ausgewählten Kategorien"""
        if not selected_categories:
            return topics

        categories = self.get_topic_categories(topics)
        filtered_topics = []

        for category in selected_categories:
            if category in categories:
                filtered_topics.extend(categories[category])

        return list(set(filtered_topics))  # Duplikate entfernen

    def filter_topics_by_subcategory(self, topics: List[str], selected_subcategories: List[str]) -> List[str]:
        """Filtert Topics basierend auf ausgewählten Sub-Kategorien"""
        if not selected_subcategories:
            return topics

        subcategories = self.get_topic_subcategories(topics)
        filtered_topics = []

        for subcat_str in selected_subcategories:
            category, subcat = subcat_str.split(" → ", 1)
            if category in subcategories and subcat in subcategories[category]:
                filtered_topics.extend(subcategories[category][subcat])

        return list(set(filtered_topics))  # Duplikate entfernen

    def filter_topics_by_friendly_name(self, topics: List[str], search_term: str) -> List[str]:
        """Filtert Topics basierend auf Friendly Name Suche"""
        if not search_term:
            return topics

        filtered_topics = []
        for topic in topics:
            try:
                friendly_name = self.topic_manager.get_friendly_name(topic)
                if search_term.lower() in friendly_name.lower():
                    filtered_topics.append(topic)
            except Exception as e:
                logger.warning(f"Fehler beim Abrufen des Friendly Names für {topic}: {e}")
                # Fallback: Suche im Topic-Namen
                if search_term.lower() in topic.lower():
                    filtered_topics.append(topic)

        return filtered_topics

    def filter_topics_by_name(self, topics: List[str], search_term: str) -> List[str]:
        """Filtert Topics basierend auf Topic-Name Suche"""
        if not search_term:
            return topics

        return [topic for topic in topics if search_term.lower() in topic.lower()]

    def get_friendly_names(self, topics: List[str]) -> Dict[str, str]:
        """Gibt Friendly Names für eine Liste von Topics zurück"""
        friendly_names = {}
        for topic in topics:
            try:
                friendly_names[topic] = self.topic_manager.get_friendly_name(topic)
            except Exception as e:
                logger.warning(f"Fehler beim Abrufen des Friendly Names für {topic}: {e}")
                friendly_names[topic] = topic  # Fallback: Topic-Name verwenden

        return friendly_names
