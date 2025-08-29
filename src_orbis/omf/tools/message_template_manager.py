#!/usr/bin/env python3
"""
OMF Message Template Manager - Modulare Template-Verwaltung
Version: 3.0.0
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class OMFMessageTemplateManager:
    """Verwaltet modulare MQTT Message Templates"""

    def __init__(self, templates_dir: str = None):
        """Initialisiert den OMF Message Template Manager"""
        if templates_dir is None:
            templates_dir = os.path.join(
                os.path.dirname(__file__), "..", "config", "message_templates"
            )

        self.templates_dir = Path(templates_dir)
        self.metadata = self._load_metadata()
        self.categories = self._load_categories()
        self.templates = {}
        self._load_all_templates()

    def _load_metadata(self) -> Dict[str, Any]:
        """Lädt die globalen Metadaten"""
        metadata_file = self.templates_dir / "metadata.yml"
        try:
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Metadaten-Datei nicht gefunden: {metadata_file}")
                return {}
        except Exception as e:
            print(f"❌ Fehler beim Laden der Metadaten: {e}")
            return {}

    def _load_categories(self) -> Dict[str, Any]:
        """Lädt die Kategorien-Definition"""
        categories_file = self.templates_dir / "categories.yml"
        try:
            if categories_file.exists():
                with open(categories_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Kategorien-Datei nicht gefunden: {categories_file}")
                return {}
        except Exception as e:
            print(f"❌ Fehler beim Laden der Kategorien: {e}")
            return {}

    def _load_all_templates(self):
        """Lädt alle Template-Dateien"""
        templates_dir = self.templates_dir / "templates"
        if not templates_dir.exists():
            print(f"⚠️ Templates-Verzeichnis nicht gefunden: {templates_dir}")
            return

        # Durchlaufe alle Kategorien
        for category in self.categories.get("categories", {}).keys():
            category_dir = templates_dir / category.lower()
            if not category_dir.exists():
                continue

            # Durchlaufe alle YAML-Dateien in der Kategorie
            for yaml_file in category_dir.glob("*.yml"):
                self._load_template_file(yaml_file)

    def _load_template_file(self, file_path: Path):
        """Lädt eine einzelne Template-Datei"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)

            if template_data and "templates" in template_data:
                # Füge Templates zur globalen Sammlung hinzu
                for topic, template in template_data["templates"].items():
                    # Füge Metadaten hinzu
                    template["file_path"] = str(file_path)
                    template["category"] = template_data.get("metadata", {}).get(
                        "category"
                    )
                    template["sub_category"] = template_data.get("metadata", {}).get(
                        "sub_category"
                    )

                    self.templates[topic] = template

                print(
                    f"✅ {len(template_data['templates'])} Templates aus {file_path.name} geladen"
                )

        except Exception as e:
            print(f"❌ Fehler beim Laden von {file_path}: {e}")

    def get_topic_template(self, topic: str) -> Optional[Dict[str, Any]]:
        """Holt das Template für ein spezifisches Topic"""
        return self.templates.get(topic)

    def get_all_topics(self) -> List[str]:
        """Gibt alle verfügbaren Topics zurück"""
        return list(self.templates.keys())

    def get_topics_by_category(self, category: str) -> List[str]:
        """Gibt alle Topics einer Kategorie zurück"""
        topics = []
        for topic, template in self.templates.items():
            if template.get("category") == category:
                topics.append(topic)
        return topics

    def get_topics_by_sub_category(self, sub_category: str) -> List[str]:
        """Gibt alle Topics einer Sub-Kategorie zurück"""
        topics = []
        for topic, template in self.templates.items():
            if template.get("sub_category") == sub_category:
                topics.append(topic)
        return topics

    def get_categories(self) -> Dict[str, Any]:
        """Gibt alle verfügbaren Kategorien zurück"""
        return self.categories.get("categories", {})

    def get_sub_categories(self, category: str) -> Dict[str, Any]:
        """Gibt alle Sub-Kategorien einer Kategorie zurück"""
        category_info = self.categories.get("categories", {}).get(category, {})
        return category_info.get("sub_categories", {})

    def get_template_structure(self, topic: str) -> Optional[Dict[str, Any]]:
        """Holt die Template-Struktur für ein Topic"""
        template = self.get_topic_template(topic)
        return template.get("structure") if template else None

    def get_template_examples(self, topic: str) -> List[Dict[str, Any]]:
        """Holt die Beispiele für ein Topic"""
        template = self.get_topic_template(topic)
        return template.get("examples", []) if template else []

    def get_validation_rules(self, topic: str) -> List[str]:
        """Holt die Validierungsregeln für ein Topic"""
        template = self.get_topic_template(topic)
        return template.get("validation_rules", []) if template else []

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Templates zurück"""
        total_templates = len(self.templates)

        # Zähle Templates pro Kategorie
        category_counts = {}
        sub_category_counts = {}

        for topic, template in self.templates.items():
            category = template.get("category", "Unknown")
            sub_category = template.get("sub_category", "Unknown")

            category_counts[category] = category_counts.get(category, 0) + 1
            sub_category_counts[sub_category] = (
                sub_category_counts.get(sub_category, 0) + 1
            )

        return {
            "total_templates": total_templates,
            "total_categories": len(category_counts),
            "total_sub_categories": len(sub_category_counts),
            "category_counts": category_counts,
            "sub_category_counts": sub_category_counts,
            "metadata": self.metadata,
        }

    def reload_templates(self) -> bool:
        """Lädt alle Templates neu"""
        try:
            self.templates = {}
            self._load_all_templates()
            return True
        except Exception as e:
            print(f"❌ Fehler beim Neuladen der Templates: {e}")
            return False

    def get_template_file_path(self, topic: str) -> Optional[str]:
        """Gibt den Dateipfad für ein Template zurück"""
        template = self.get_topic_template(topic)
        return template.get("file_path") if template else None

    def validate_message(self, topic: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Validiert eine Nachricht gegen das Template"""
        template = self.get_topic_template(topic)
        if not template:
            return {"valid": False, "error": "Template nicht gefunden"}

        structure = template.get("structure", {})

        # Einfache Struktur-Validierung
        errors = []
        for field, expected_type in structure.items():
            if field not in message:
                errors.append(f"Feld '{field}' fehlt")
            else:
                # Einfache Typ-Validierung
                value = message[field]
                if expected_type == "<string>" and not isinstance(value, str):
                    errors.append(f"Feld '{field}' muss String sein")
                elif expected_type == "<number>" and not isinstance(
                    value, (int, float)
                ):
                    errors.append(f"Feld '{field}' muss Zahl sein")
                elif expected_type == "<boolean>" and not isinstance(value, bool):
                    errors.append(f"Feld '{field}' muss Boolean sein")
                elif expected_type == "<datetime>" and not isinstance(value, str):
                    errors.append(f"Feld '{field}' muss Datetime-String sein")

        return {"valid": len(errors) == 0, "errors": errors, "template": template}


# Singleton instance
_template_manager_instance = None


def get_omf_message_template_manager() -> OMFMessageTemplateManager:
    """Get singleton instance of OMFMessageTemplateManager"""
    global _template_manager_instance
    if _template_manager_instance is None:
        _template_manager_instance = OMFMessageTemplateManager()
    return _template_manager_instance


# Backward compatibility functions
def get_message_template_manager() -> OMFMessageTemplateManager:
    """Backward compatibility function"""
    return get_omf_message_template_manager()
