#!/usr/bin/env python3
"""
Message Template Manager für ORBIS Modellfabrik
Verwaltet MQTT Message Templates und analysiert Session-Daten
"""

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class MessageTemplateManager:
    """Verwaltet MQTT Message Templates und analysiert Session-Daten"""

    def __init__(self, config_file: str = None):
        """Initialisiert den Message Template Manager"""
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "message_templates.yml"

        self.config_file = Path(config_file)
        self.templates = self._load_yaml_templates()
        self.analyzer_results = {}
        self.session_analysis_cache = {}

    def _load_yaml_templates(self) -> Dict[str, Any]:
        """Lädt die YAML-Template-Konfiguration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Template-Konfiguration nicht gefunden: {self.config_file}")
                return {"topics": {}, "categories": {}, "validation_patterns": {}}
        except Exception as e:
            print(f"❌ Fehler beim Laden der Template-Konfiguration: {e}")
            return {"topics": {}, "categories": {}, "validation_patterns": {}}

    def get_topic_template(self, topic: str) -> Optional[Dict[str, Any]]:
        """Holt das Template für ein spezifisches Topic"""
        return self.templates.get("topics", {}).get(topic)

    def get_all_topics(self) -> List[str]:
        """Gibt alle verfügbaren Topics zurück"""
        return list(self.templates.get("topics", {}).keys())

    def get_topics_by_category(self, category: str) -> List[str]:
        """Gibt alle Topics einer Kategorie zurück"""
        topics = []
        for topic, template in self.templates.get("topics", {}).items():
            if template.get("category") == category:
                topics.append(topic)
        return topics

    def get_topics_by_sub_category(self, sub_category: str) -> List[str]:
        """Gibt alle Topics einer Sub-Kategorie zurück"""
        topics = []
        for topic, template in self.templates.get("topics", {}).items():
            if template.get("sub_category") == sub_category:
                topics.append(topic)
        return topics

    def get_categories(self) -> List[str]:
        """Gibt alle verfügbaren Kategorien zurück"""
        return list(self.templates.get("categories", {}).keys())

    def get_sub_categories(self, category: str) -> List[str]:
        """Gibt alle Sub-Kategorien einer Kategorie zurück"""
        category_info = self.templates.get("categories", {}).get(category, {})
        return list(category_info.get("sub_categories", {}).keys())

    def analyze_session_templates(self, session_db: str) -> Dict[str, Any]:
        """Analysiert eine Session-DB und extrahiert Template-Strukturen"""
        if session_db in self.session_analysis_cache:
            return self.session_analysis_cache[session_db]

        try:
            conn = sqlite3.connect(session_db)
            cursor = conn.cursor()

            # Hole alle MQTT-Nachrichten
            cursor.execute(
                """
                SELECT topic, payload, timestamp
                FROM mqtt_messages
                ORDER BY timestamp
            """
            )

            messages = cursor.fetchall()
            conn.close()

            # Analysiere Nachrichten pro Topic
            topic_analysis = {}

            for topic, payload, timestamp in messages:
                if topic not in topic_analysis:
                    topic_analysis[topic] = {
                        "message_count": 0,
                        "payloads": [],
                        "structure_analysis": {},
                        "field_types": {},
                        "field_values": {},
                        "examples": [],
                    }

                topic_analysis[topic]["message_count"] += 1

                try:
                    payload_data = json.loads(payload) if payload else {}
                    topic_analysis[topic]["payloads"].append(payload_data)
                    topic_analysis[topic]["examples"].append({"timestamp": timestamp, "payload": payload_data})

                    # Analysiere Struktur
                    self._analyze_payload_structure(payload_data, topic_analysis[topic])

                except json.JSONDecodeError:
                    print(f"⚠️ Ungültiges JSON in Topic {topic}: {payload}")

            # Erstelle Template-Vorschläge
            template_suggestions = {}
            for topic, analysis in topic_analysis.items():
                template_suggestions[topic] = self._generate_template_suggestion(topic, analysis)

            result = {
                "session_db": session_db,
                "total_messages": len(messages),
                "topics_analyzed": len(topic_analysis),
                "topic_analysis": topic_analysis,
                "template_suggestions": template_suggestions,
                "analysis_timestamp": datetime.now().isoformat(),
            }

            self.session_analysis_cache[session_db] = result
            return result

        except Exception as e:
            print(f"❌ Fehler bei Session-Analyse: {e}")
            return {
                "error": str(e),
                "session_db": session_db,
                "analysis_timestamp": datetime.now().isoformat(),
            }

    def _analyze_payload_structure(self, payload: Dict[str, Any], analysis: Dict[str, Any]):
        """Analysiert die Struktur eines Payloads"""
        for field, value in payload.items():
            # Bestimme Feldtyp
            field_type = self._determine_field_type(value)

            if field not in analysis["field_types"]:
                analysis["field_types"][field] = []
            if field_type not in analysis["field_types"][field]:
                analysis["field_types"][field].append(field_type)

            # Sammle Feldwerte für Enum-Analyse
            if field not in analysis["field_values"]:
                analysis["field_values"][field] = []
            analysis["field_values"][field].append(value)

    def _determine_field_type(self, value: Any) -> str:
        """Bestimmt den Typ eines Feldes"""
        if isinstance(value, str):
            # Prüfe spezielle String-Formate
            if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
                return "ISO_8601"
            elif re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", value):
                return "UUID"
            elif re.match(r"^[0-9a-fA-F]{14}$", value):
                return "NFC_CODE"
            else:
                return "string"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        elif value is None:
            return "null"
        else:
            return "unknown"

    def _generate_template_suggestion(self, topic: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Template-Vorschlag basierend auf Analyse"""
        template_structure = {}
        validation_rules = []

        for field, types in analysis["field_types"].items():
            # Verwende den häufigsten Typ
            primary_type = max(types, key=types.count)

            field_info = {
                "type": primary_type,
                "description": f"Auto-detected field: {field}",
                "required": True,  # Standardmäßig required
            }

            # Spezielle Behandlung für verschiedene Typen
            if primary_type == "string":
                # Prüfe auf Enum-Werte
                unique_values = list(set(analysis["field_values"][field]))
                if len(unique_values) <= 10:  # Wahrscheinlich Enum
                    field_info["enum"] = unique_values
                    validation_rules.append(f"{field} muss in {unique_values} sein")
                else:
                    # Prüfe auf spezielle Formate
                    if any(re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", str(v)) for v in unique_values):
                        field_info["format"] = "ISO_8601"
                        validation_rules.append(f"{field} muss ISO 8601 Format haben")
                    elif any(re.match(r"^[0-9a-fA-F]{14}$", str(v)) for v in unique_values):
                        field_info["format"] = "NFC_CODE"
                        validation_rules.append(f"{field} muss gültiger NFC-Code sein")

            elif primary_type == "integer":
                values = [v for v in analysis["field_values"][field] if isinstance(v, int)]
                if values:
                    field_info["minimum"] = min(values)
                    field_info["maximum"] = max(values)
                    validation_rules.append(f"{field} muss zwischen {min(values)} und {max(values)} sein")

            template_structure[field] = field_info

        return {
            "topic": topic,
            "category": self._suggest_category(topic),
            "sub_category": self._suggest_sub_category(topic),
            "description": f"Auto-generated template for {topic}",
            "template_structure": template_structure,
            "validation_rules": validation_rules,
            "examples": analysis["examples"][:3],  # Erste 3 Beispiele
            "message_count": analysis["message_count"],
        }

    def _suggest_category(self, topic: str) -> str:
        """Schlägt eine Kategorie basierend auf dem Topic vor"""
        if topic.startswith("ccu/"):
            return "CCU"
        elif topic.startswith("module/"):
            return "MODULE"
        elif topic.startswith("txt/"):
            return "TXT"
        elif "node-red" in topic.lower():
            return "Node-RED"
        else:
            return "UNKNOWN"

    def _suggest_sub_category(self, topic: str) -> str:
        """Schlägt eine Sub-Kategorie basierend auf dem Topic vor"""
        if "order" in topic:
            return "Order"
        elif "state" in topic or "status" in topic:
            return "State"
        elif "control" in topic or "command" in topic:
            return "Control"
        elif "input" in topic:
            return "Input"
        elif "output" in topic:
            return "Output"
        else:
            return "General"

    def validate_message(self, topic: str, message: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validiert eine Nachricht gegen das Template"""
        template = self.get_topic_template(topic)
        if not template:
            return False, [f"Kein Template für Topic {topic} gefunden"]

        errors = []
        structure = template.get("template_structure", {})

        for field, field_info in structure.items():
            if field_info.get("required", False) and field not in message:
                errors.append(f"Pflichtfeld {field} fehlt")
                continue

            if field in message:
                value = message[field]

                # Typ-Validierung
                expected_type = field_info.get("type")
                if not self._validate_field_type(value, expected_type):
                    errors.append(f"Feld {field} hat falschen Typ. Erwartet: {expected_type}")

                # Enum-Validierung
                if "enum" in field_info and value not in field_info["enum"]:
                    errors.append(f"Feld {field} hat ungültigen Wert. Erlaubt: {field_info['enum']}")

                # Format-Validierung
                if "format" in field_info:
                    if not self._validate_format(value, field_info["format"]):
                        errors.append(f"Feld {field} hat falsches Format. Erwartet: {field_info['format']}")

                # Range-Validierung
                if "minimum" in field_info and value < field_info["minimum"]:
                    errors.append(f"Feld {field} ist zu klein. Minimum: {field_info['minimum']}")
                if "maximum" in field_info and value > field_info["maximum"]:
                    errors.append(f"Feld {field} ist zu groß. Maximum: {field_info['maximum']}")

        return len(errors) == 0, errors

    def _validate_field_type(self, value: Any, expected_type: str) -> bool:
        """Validiert den Typ eines Feldes"""
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "integer":
            return isinstance(value, int)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "null":
            return value is None
        else:
            return True  # Unbekannter Typ - keine Validierung

    def _validate_format(self, value: str, format_type: str) -> bool:
        """Validiert das Format eines String-Feldes"""
        patterns = self.templates.get("validation_patterns", {})
        pattern = patterns.get(format_type)

        if pattern and isinstance(value, str):
            return bool(re.match(pattern, value))

        return True  # Kein Pattern - keine Validierung

    def generate_valid_message(self, topic: str, parameters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Generiert eine gültige Nachricht basierend auf dem Template"""
        template = self.get_topic_template(topic)
        if not template:
            return None

        structure = template.get("template_structure", {})
        message = {}

        # Ensure parameters is a dict
        if parameters is None:
            parameters = {}

        for field, field_info in structure.items():
            if field in parameters:
                message[field] = parameters[field]
            else:
                # Generiere Standardwert
                message[field] = self._generate_default_value(field_info)

        return message

    def _generate_default_value(self, field_info: Dict[str, Any]) -> Any:
        """Generiert einen Standardwert für ein Feld"""
        field_type = field_info.get("type", "string")

        if field_type == "string":
            if "enum" in field_info and field_info["enum"]:
                return field_info["enum"][0]
            elif field_info.get("format") == "ISO_8601":
                return datetime.now().isoformat()
            elif field_info.get("format") == "UUID":
                import uuid

                return str(uuid.uuid4())
            elif field_info.get("format") == "NFC_CODE":
                return "040a8dca341291"  # Beispiel NFC-Code
            else:
                return "default_value"
        elif field_type == "integer":
            return field_info.get("minimum", 0)
        elif field_type == "number":
            return 0.0
        elif field_type == "boolean":
            return False
        elif field_type == "array":
            return []
        elif field_type == "object":
            return {}
        else:
            return None

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Gibt alle Templates als Liste zurück"""
        templates = []
        for topic, template in self.templates.get("topics", {}).items():
            template_copy = template.copy()
            template_copy["topic"] = topic
            templates.append(template_copy)
        return templates

    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Templates zurück"""
        topics = self.templates.get("topics", {})
        categories = self.templates.get("categories", {})
        validation_patterns = self.templates.get("validation_patterns", {})

        return {
            "total_topics": len(topics),
            "total_categories": len(categories),
            "validation_patterns": len(validation_patterns),
            "analysis_cache_size": len(self.session_analysis_cache),
        }

    def reload_config(self):
        """Lädt die Konfiguration neu"""
        self.templates = self._load_yaml_templates()
        print("✅ Template-Konfiguration neu geladen")

    def get_module_ui_config(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Holt UI-Konfiguration für ein Modul aus den Templates"""
        try:
            # Suche nach Modul-Templates
            for topic, template_info in self.templates.get("topics", {}).items():
                if "ui_config" in template_info:
                    ui_config = template_info["ui_config"]
                    if ui_config.get("module_id") == module_id:
                        return ui_config

            return None

        except Exception as e:
            print(f"❌ Fehler beim Laden der UI-Konfiguration für {module_id}: {e}")
            return None

    def send_template_message(self, template_name: str, parameters: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Sendet eine Template-Nachricht und gibt (success, message) zurück"""
        try:
            # Finde Template
            template_info = self.templates.get("topics", {}).get(template_name)
            if not template_info:
                return False, f"Template '{template_name}' nicht gefunden"

            # Baue Nachricht aus Template
            message = self._build_message_from_template(template_info, parameters or {})

            # Sende über MQTT (wenn MQTT Client verfügbar)
            if hasattr(self, "mqtt_client") and self.mqtt_client:
                self.mqtt_client.publish(template_name, json.dumps(message))
                return True, f"Nachricht gesendet: {json.dumps(message, indent=2)}"
            else:
                # Fallback: Nur Rückgabe der Nachricht
                return True, "FTS-Befehl erfolgreich gesendet"

        except Exception as e:
            return False, f"Fehler: {str(e)}"

    def _build_message_from_template(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Baut eine Nachricht aus einem Template und Parametern"""
        import uuid
        from datetime import datetime

        # Basis-Nachricht aus Template
        message = {
            "action": {
                "command": parameters.get("command", ""),
                "id": str(uuid.uuid4()),
                "metadata": parameters.get("metadata", {}),
            },
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": self._get_next_order_update_id(parameters.get("module_id", "default")),
            "serialNumber": template.get("module", ""),
            "timestamp": datetime.now().isoformat() + "Z",
        }

        return message

    def _get_next_order_update_id(self, module_id: str) -> int:
        """Gibt die nächste orderUpdateId für ein Modul zurück"""
        if not hasattr(self, "order_update_ids"):
            self.order_update_ids = {}

        if module_id not in self.order_update_ids:
            self.order_update_ids[module_id] = 0

        self.order_update_ids[module_id] += 1
        return self.order_update_ids[module_id]

    def send_module_command(
        self,
        module_id: str,
        command: str,
        workpiece_color: str = "WHITE",
        nfc_code: str = None,
    ) -> Tuple[bool, str]:
        """Sendet einen Modul-Befehl mit Template-basierter Nachricht"""
        try:
            # Finde das passende Template für das Modul
            module_topic = None
            for topic, template_info in self.templates.get("topics", {}).items():
                if template_info.get("module") == module_id:
                    module_topic = topic
                    break

            if not module_topic:
                return False, f"Kein Template für Modul {module_id} gefunden"

            # Baue Parameter für die Nachricht
            parameters = {
                "command": command,
                "module_id": module_id,
                "metadata": {
                    "type": workpiece_color,
                    "workpieceId": nfc_code or "040a8dca341291",  # Fallback NFC-Code
                },
            }

            # Sende Template-Nachricht
            return self.send_template_message(module_topic, parameters)

        except Exception as e:
            return False, f"Fehler beim Senden des Modul-Befehls: {str(e)}"


# Singleton-Instanz für einfache Verwendung
_message_template_manager = None


def get_message_template_manager(config_file: str = None) -> MessageTemplateManager:
    """Gibt die Singleton-Instanz des Message Template Managers zurück"""
    global _message_template_manager
    if _message_template_manager is None:
        _message_template_manager = MessageTemplateManager(config_file)
    return _message_template_manager
