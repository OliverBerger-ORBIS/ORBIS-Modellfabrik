import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Add the src_orbis directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_orbis_path = os.path.join(current_dir, "..", "..", "..")
if src_orbis_path not in sys.path:
    sys.path.insert(0, src_orbis_path)

try:
    from src_orbis.omf.config.config_loader import OmfConfig
except ImportError:
    # Fallback für Tests
    class OmfConfig:
        def get_config_path(self):
            return os.path.join(os.path.dirname(__file__), "..", "config")


class TopicMappingManager:
    """Verwaltet das Mapping zwischen MQTT-Topics und Message-Templates"""

    def __init__(self):
        self.config = OmfConfig()
        self.topic_mappings = {}
        self.template_categories = {}
        self._load_topic_mappings()

    def _load_topic_mappings(self):
        """Lädt das Topic-Message-Mapping aus der YAML-Datei"""
        try:
            mapping_file = Path(self.config.get_config_path()) / "topic_message_mapping.yml"
            if mapping_file.exists():
                with open(mapping_file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.topic_mappings = data.get("topic_mappings", {})
                    self.template_categories = data.get("template_categories", {})
                print(f"✅ Topic-Mappings geladen: {len(self.topic_mappings)} Topics")
            else:
                print("⚠️ Topic-Mapping-Datei nicht gefunden")
        except Exception as e:
            print(f"❌ Fehler beim Laden der Topic-Mappings: {e}")

    def get_available_topics(self) -> List[str]:
        """Gibt alle verfügbaren Topics zurück"""
        return list(self.topic_mappings.keys())

    def get_topics_by_category(self, category: str) -> List[str]:
        """Gibt Topics einer bestimmten Kategorie zurück"""
        category_topics = self.template_categories.get(category, [])
        return [topic for topic in category_topics if topic in self.topic_mappings]

    def get_topic_categories(self) -> List[str]:
        """Gibt alle verfügbaren Topic-Kategorien zurück"""
        return list(self.template_categories.keys())

    def get_template_for_topic(self, topic: str) -> Optional[str]:
        """Gibt das Template für ein bestimmtes Topic zurück"""
        mapping = self.topic_mappings.get(topic)
        return mapping.get("template") if mapping else None

    def get_topic_info(self, topic: str) -> Optional[Dict]:
        """Gibt vollständige Informationen zu einem Topic zurück"""
        return self.topic_mappings.get(topic)

    def get_topics_for_template(self, template: str) -> List[str]:
        """Gibt alle Topics zurück, die ein bestimmtes Template verwenden"""
        return [topic for topic, mapping in self.topic_mappings.items() if mapping.get("template") == template]

    def resolve_topic_variables(self, topic_pattern: str, **variables) -> str:
        """Löst Variable in Topic-Patterns auf (z.B. {module_id})"""
        resolved_topic = topic_pattern
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in resolved_topic:
                resolved_topic = resolved_topic.replace(placeholder, str(var_value))
        return resolved_topic

    def get_variable_fields(self, topic: str) -> Dict[str, str]:
        """Gibt die variablen Felder für ein Topic zurück"""
        mapping = self.topic_mappings.get(topic)
        return mapping.get("variable_fields", {}) if mapping else {}


# Singleton-Instanz
_topic_mapping_manager = None


def get_omf_topic_mapping_manager() -> TopicMappingManager:
    """Gibt die Singleton-Instanz des TopicMappingManager zurück"""
    global _topic_mapping_manager
    if _topic_mapping_manager is None:
        _topic_mapping_manager = TopicMappingManager()
    return _topic_mapping_manager
