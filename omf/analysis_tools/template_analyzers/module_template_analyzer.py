from omf.tools.module_manager import get_omf_module_manager

#!/usr/bin/env python3
"""
Module Template Analyzer for ORBIS Modellfabrik

Analyzes MQTT message templates for MODULE topics from session data.
Extracts template structures, examples, and validation rules.
"""

import glob
import json
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import yaml

from omf.analysis_tools.nfc_code_manager import get_nfc_manager
from omf.tools.message_template_manager import get_message_template_manager


class ModuleTemplateAnalyzer:
    """Analyzer for MODULE MQTT message templates"""

    def __init__(self, session_dir: str = None, output_dir: str = None):
        """Initialize the analyzer"""
        # Use absolute paths for better reliability
        project_root = os.path.abspath(str(Path(__file__).parent / ".." / ".." / ".."))

        self.session_dir = session_dir or os.path.join(project_root, "data/omf-data/sessions")
        self.output_dir = output_dir or os.path.join(project_root, "registry/observations/payloads")

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize managers
        self.nfc_manager = get_nfc_manager()
        self.module_mapping = get_omf_module_manager()
        self.message_template_manager = get_message_template_manager()

        # MODULE topic patterns (based on actual session data)
        self.module_topics = [
            # Connection topics
            "module/v1/ff/NodeRed/*/connection",
            "module/v1/ff/*/connection",
            # State topics
            "module/v1/ff/NodeRed/*/state",
            "module/v1/ff/*/state",
            # Order topics
            "module/v1/ff/NodeRed/*/order",
            "module/v1/ff/*/order",
            # Factsheet topics
            "module/v1/ff/NodeRed/*/factsheet",
            "module/v1/ff/*/factsheet",
            # Instant action topics
            "module/v1/ff/NodeRed/*/instantAction",
            # Status topics
            "module/v1/ff/NodeRed/status",
        ]

        # Module IDs from configuration and session data
        self.module_ids = self.module_mapping.get_all_module_ids()
        # Add additional module IDs found in session data
        self.module_ids.extend(["SVR4H73275", "SVR4H76530", "SVR3QA0022", "5iO4", "NodeRed"])

        print("🔧 Module Template Analyzer initialisiert")
        print(f"   📁 Session-Verzeichnis: {self.session_dir}")
        print(f"   📁 Ausgabe-Verzeichnis: {self.output_dir}")
        print(f"   🏭 Module-IDs: {len(self.module_ids)} gefunden")
        print(f"   📡 Topic-Patterns: {len(self.module_topics)} definiert")

    def _determine_sub_category(self, topic: str) -> str:
        """Determine sub-category based on topic"""
        if "connection" in topic:
            return "Connection"
        elif "state" in topic:
            return "State"
        elif "order" in topic:
            return "Order"
        elif "factsheet" in topic:
            return "Factsheet"
        elif "instantAction" in topic:
            return "InstantAction"
        elif "status" in topic and not any(x in topic for x in ["connection", "state", "order", "factsheet"]):
            return "Status"
        else:
            return "General"

    def _determine_module_id(self, topic: str) -> str:
        """Extract module ID from topic"""
        # Pattern: module/v1/ff/NodeRed/{module_id}/...
        match = re.match(r"module/v1/ff/NodeRed/([^/]+)/", topic)
        if match:
            module_id = match.group(1)
            if module_id in self.module_ids:
                return module_id

        # Pattern: module/v1/ff/{module_id}/...
        match = re.match(r"module/v1/ff/([^/]+)/", topic)
        if match:
            module_id = match.group(1)
            if module_id in self.module_ids:
                return module_id

        # Pattern: module/{module_id}/... (fallback)
        match = re.match(r"module/([^/]+)/", topic)
        if match:
            module_id = match.group(1)
            if module_id in self.module_ids:
                return module_id

        return "unknown"

    def _get_placeholder_for_field(self, field_name: str, values: Set[str], module_id: str = None) -> str:
        """Generate placeholder for field based on values and field name"""
        if not values:
            return "<string>"

        # Check for specific patterns
        if field_name.lower() in ["timestamp", "time", "date"]:
            return "<datetime>"
        elif field_name.lower() in ["id", "uuid", "guid"]:
            return "<uuid>"
        elif field_name.lower() in ["nfc", "nfc_code", "workpiece_id"]:
            return "<nfcCode>"
        elif field_name.lower() in ["module", "module_id", "moduleid"]:
            return "<moduleId>"
        elif field_name.lower() in ["status", "state"]:
            # Check if it's a known enum
            if len(values) <= 10:  # Reasonable enum size
                return f"[{', '.join(sorted(values))}]"
            else:
                return "<string>"
        elif field_name.lower() in ["type", "order_type", "action_type"]:
            # Check for known enums
            if len(values) <= 10:
                return f"[{', '.join(sorted(values))}]"
            else:
                return "<string>"
        elif field_name.lower() in ["position", "pos"]:
            return "<position>"
        elif field_name.lower() in ["error", "error_code"]:
            return "<errorCode>"
        elif field_name.lower() in ["message", "msg"]:
            return "<message>"
        elif field_name.lower() in ["data", "payload"]:
            return "<data>"
        else:
            # Check if it's a small set of values (likely enum)
            if len(values) <= 5:
                return f"[{', '.join(sorted(values))}]"
            else:
                return "<string>"

    def _analyze_topic_structure(self, topic: str, messages: List[Dict]) -> Dict:
        """Analyze structure for a specific topic"""
        if not messages:
            return {
                "template_structure": {},
                "examples": [],
                "statistics": {
                    "total_messages": 0,
                    "enum_fields": 0,
                    "variable_fields": 0,
                },
            }

        # Collect all field values
        field_values = {}
        examples = []

        for msg in messages:
            payload = msg.get("payload", {})
            if isinstance(payload, dict):
                examples.append(payload)

                for field, value in payload.items():
                    if field not in field_values:
                        field_values[field] = set()
                    field_values[field].add(str(value))

        # Generate template structure
        template_structure = {}
        enum_fields = 0
        variable_fields = 0

        module_id = self._determine_module_id(topic)

        for field, values in field_values.items():
            placeholder = self._get_placeholder_for_field(field, values, module_id)
            template_structure[field] = placeholder

            if placeholder.startswith("[") and placeholder.endswith("]"):
                enum_fields += 1
            else:
                variable_fields += 1

        return {
            "template_structure": template_structure,
            "examples": examples[:5],  # Keep first 5 examples
            "statistics": {
                "total_messages": len(messages),
                "enum_fields": enum_fields,
                "variable_fields": variable_fields,
            },
        }

    def _generate_validation_rules(self, template_structure: Dict) -> List[str]:
        """Generate validation rules for template structure"""
        rules = []

        def add_rules_for_structure(structure, prefix=""):
            for field, placeholder in structure.items():
                field_path = f"{prefix}.{field}" if prefix else field

                if isinstance(placeholder, str):
                    if placeholder.startswith("["):
                        # ENUM validation
                        enum_values = placeholder[1:-1].split(", ")
                        rules.append(f"{field} muss in {placeholder} sein")
                    elif placeholder == "<datetime>":
                        rules.append(f"{field} muss ISO 8601 Format haben")
                    elif placeholder == "<uuid>":
                        rules.append(f"{field} muss UUID Format haben")
                    elif placeholder == "<nfcCode>":
                        rules.append(f"{field} muss gültiger NFC-Code sein")
                    elif placeholder == "<moduleId>":
                        rules.append(f"{field} muss gültige Modul-ID sein")
                    elif placeholder == "<position>":
                        rules.append(f"{field} muss gültige Position sein")
                    elif placeholder == "<errorCode>":
                        rules.append(f"{field} muss gültiger Fehler-Code sein")
                elif isinstance(placeholder, dict):
                    add_rules_for_structure(placeholder, field_path)
                elif isinstance(placeholder, list):
                    if placeholder and isinstance(placeholder[0], dict):
                        add_rules_for_structure(placeholder[0], f"{field_path}[0]")

        add_rules_for_structure(template_structure)
        return rules

    def load_all_sessions(self) -> List[str]:
        """Load all available session databases"""
        session_files = glob.glob(os.path.join(self.session_dir, "*.db"))
        sessions = []

        for session_file in session_files:
            try:
                conn = sqlite3.connect(session_file)
                cursor = conn.cursor()

                # Check if table exists and has data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM mqtt_messages")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        sessions.append(session_file)

                conn.close()
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {session_file}: {e}")

        print(f"📊 {len(sessions)} Session-Dateien gefunden")
        return sessions

    def analyze_topic_structure(self, topic: str, sessions: List[str]) -> Dict:
        """Analyze structure for a specific topic across all sessions"""
        all_messages = []

        for session_file in sessions:
            try:
                conn = sqlite3.connect(session_file)
                cursor = conn.cursor()

                # Get messages for this topic
                cursor.execute(
                    """
                    SELECT topic, payload, timestamp
                    FROM mqtt_messages
                    WHERE topic = ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                """,
                    (topic,),
                )

                messages = cursor.fetchall()
                for msg in messages:
                    try:
                        payload = json.loads(msg[1]) if msg[1] else {}
                        all_messages.append({"topic": msg[0], "payload": payload, "timestamp": msg[2]})
                    except json.JSONDecodeError:
                        continue

                conn.close()
            except Exception as e:
                print(f"⚠️ Fehler beim Analysieren von {topic} in {session_file}: {e}")

        return self._analyze_topic_structure(topic, all_messages)

    def analyze_all_topics(self, sessions: List[str]) -> Dict:
        """Analyze all MODULE topics"""
        results = {}

        # Generate all possible topic combinations
        all_topics = set()
        for pattern in self.module_topics:
            for module_id in self.module_ids:
                topic = pattern.replace("*", module_id)
                all_topics.add(topic)

        print(f"🔍 Analysiere {len(all_topics)} MODULE Topics...")

        for i, topic in enumerate(sorted(all_topics), 1):
            print(f"   [{i:2d}/{len(all_topics)}] {topic}")

            result = self.analyze_topic_structure(topic, sessions)
            if result["statistics"]["total_messages"] > 0:
                results[topic] = result

        return results

    def save_results(self, results: Dict) -> str:
        """Save analysis results to JSON file"""
        output_file = f"{self.output_dir}/module_template_analysis.json"

        output_data = {
            "metadata": {
                "analyzer": "Module Template Analyzer",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "total_topics": len(results),
                "total_messages": sum(template["statistics"]["total_messages"] for template in results.values()),
            },
            "templates": results,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"💾 JSON-Ergebnisse gespeichert in: {output_file}")
        return output_file

    def save_results_to_yaml(self, results: Dict):
        """Save analysis results to YAML file"""
        output_file = f"{self.output_dir}/module_analysis_results.yml"

        # Convert results to YAML format
        yaml_data = {
            "metadata": {
                "analyzer": "Module Template Analyzer",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "total_topics": len(results),
                "total_messages": sum(template["statistics"]["total_messages"] for template in results.values()),
            },
            "templates": {},
        }

        for topic, template in results.items():
            yaml_data["templates"][topic] = {
                "category": "MODULE",
                "sub_category": self._determine_sub_category(topic),
                "module": self._determine_module_id(topic),
                "description": f"Module {self._determine_module_id(topic)} {self._determine_sub_category(topic)}",
                "template_structure": template["template_structure"],
                "examples": template["examples"],
                "validation_rules": self._generate_validation_rules(template["template_structure"]),
                "statistics": template["statistics"],
            }

        # Save to YAML file
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)

        print(f"💾 YAML-Ergebnisse gespeichert in: {output_file}")
        return output_file

    def update_message_templates_yaml(self, results: Dict):
        """Update the main message_templates.yml with MODULE analysis results"""
        try:
            # Load existing message templates
            config_file = Path(__file__).parent.parent / "config" / "message_templates.yml"

            if config_file.exists():
                with open(config_file, encoding="utf-8") as f:
                    templates_data = yaml.safe_load(f)
            else:
                templates_data = {
                    "metadata": {"version": "1.0"},
                    "topics": {},
                    "categories": {},
                    "validation_patterns": {},
                }

            # Update with MODULE templates
            for topic, template in results.items():
                templates_data["topics"][topic] = {
                    "category": "MODULE",
                    "sub_category": self._determine_sub_category(topic),
                    "module": self._determine_module_id(topic),
                    "description": f"Module {self._determine_module_id(topic)} {self._determine_sub_category(topic)}",
                    "template_structure": template["template_structure"],
                    "examples": template["examples"],
                    "validation_rules": self._generate_validation_rules(template["template_structure"]),
                }

            # Save updated templates
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    templates_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            print(f"✅ Message Templates YAML aktualisiert: {config_file}")

        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der YAML-Datei: {e}")

    def save_observations(self, results: Dict):
        """Save analysis results as individual observation files"""
        saved_files = []

        for topic, template_data in results.items():
            # Create observation filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            category = "module"
            module_id = self._determine_module_id(topic)
            sub_category = self._determine_sub_category(topic)
            short_desc = f"{module_id.lower()}-{sub_category.lower()}"
            filename = f"{date_str}_{category}_{short_desc}.yml"
            filepath = os.path.join(self.output_dir, filename)

            # Create observation data
            observation = {
                "metadata": {
                    "date": date_str,
                    "author": "Module Template Analyzer",
                    "source": "analysis",
                    "topic": topic,
                    "related_template": f"module.{module_id.lower()}.{sub_category.lower()}",
                    "status": "open",
                },
                "observation": {
                    "description": f"Auto-analyzed MODULE topic '{topic}' with {template_data.get('statistics', {}).get('total_messages', 0)} messages",
                    "payload_example": template_data.get("examples", [{}])[0] if template_data.get("examples") else {},
                },
                "analysis": {
                    "initial_assessment": f"Template structure generated with {template_data.get('statistics', {}).get('variable_fields', 0)} variable fields and {template_data.get('statistics', {}).get('enum_fields', 0)} enum fields",
                    "open_questions": [
                        "Soll diese Template-Struktur in die Registry übernommen werden?",
                        "Sind alle Felder korrekt typisiert?",
                        "Gibt es fehlende Validierungsregeln?",
                    ],
                },
                "proposed_action": [
                    f"Template '{topic}' in Registry v1 übernehmen",
                    "Validierungsregeln definieren",
                    "Beispiele in Registry dokumentieren",
                ],
                "tags": ["module", "auto-generated", "template", module_id.lower()],
                "priority": "medium",
            }

            # Save observation
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    yaml.dump(observation, f, default_flow_style=False, allow_unicode=True, indent=2)
                saved_files.append(filepath)
                print(f"📝 Observation gespeichert: {filename}")
            except Exception as e:
                print(f"❌ Fehler beim Speichern von {filename}: {e}")

        return saved_files

    def migrate_to_registry_v0(self, results: Dict):
        """Direct migration to Registry v0 in initial phase"""
        project_root = os.path.abspath(str(Path(__file__).parent / ".." / ".." / ".."))
        registry_dir = os.path.join(project_root, "registry/model/v2/templates")
        os.makedirs(registry_dir, exist_ok=True)

        migrated_files = []

        for topic, template_data in results.items():
            # Create template filename
            module_id = self._determine_module_id(topic)
            sub_category = self._determine_sub_category(topic)
            template_key = f"module.{module_id.lower()}.{sub_category.lower()}"
            filename = f"{template_key}.yml"
            filepath = os.path.join(registry_dir, filename)

            # Create Registry v0 template
            registry_template = {
                "metadata": {
                    "category": "MODULE",
                    "module_id": module_id,
                    "sub_category": sub_category,
                    "description": f"Auto-analyzed template for {topic}",
                    "version": "0.1.0",
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "source": "module_template_analyzer",
                },
                "templates": {
                    template_key: {
                        "category": "MODULE",
                        "module_id": module_id,
                        "sub_category": sub_category,
                        "description": f"Template for {topic}",
                        "direction": "inbound" if "state" in topic or "connection" in topic else "outbound",
                        "structure": template_data.get("structure", {}),
                        "examples": template_data.get("examples", [])[:3],
                        "validation": {
                            "required_fields": list(template_data.get("structure", {}).keys()),
                            "field_types": {
                                k: v.get("type", "string") for k, v in template_data.get("structure", {}).items()
                            },
                        },
                    }
                },
            }

            # Save Registry v0 template
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    yaml.dump(registry_template, f, default_flow_style=False, allow_unicode=True, indent=2)
                migrated_files.append(filepath)
                print(f"📦 Registry v0 Template: {filename}")
            except Exception as e:
                print(f"❌ Fehler beim Speichern von {filename}: {e}")

        return migrated_files

    def run_analysis(self):
        """Run complete MODULE template analysis"""
        print("🚀 Starte MODULE Template Analyse...")

        # Load sessions
        sessions = self.load_all_sessions()
        if not sessions:
            print("❌ Keine Session-Dateien gefunden!")
            return

        # Analyze all topics
        results = self.analyze_all_topics(sessions)

        if results:
            # Save results
            output_file = self.save_results(results)

            # Save to YAML
            yaml_file = self.save_results_to_yaml(results)

            # Save as individual observations (NEW)
            observation_files = self.save_observations(results)

            # In initial phase: Direct migration to Registry v0 (NEW)
            registry_files = self.migrate_to_registry_v0(results)

            # Update main message templates
            self.update_message_templates_yaml(results)

            # Print summary
            total_messages = sum(template["statistics"]["total_messages"] for template in results.values())
            total_enum_fields = sum(template["statistics"]["enum_fields"] for template in results.values())
            total_variable_fields = sum(template["statistics"]["variable_fields"] for template in results.values())

            print("\n" + "=" * 60)
            print("📊 MODULE TEMPLATE ANALYSE ABGESCHLOSSEN")
            print("=" * 60)
            print(f"✅ Analysierte Topics: {len(results)}")
            print(f"📨 Gesamt Nachrichten: {total_messages}")
            print(f"🔢 ENUM-Felder: {total_enum_fields}")
            print(f"📝 Variable Felder: {total_variable_fields}")
            print(f"💾 JSON-Ergebnisse: {output_file}")
            print(f"💾 YAML-Ergebnisse: {yaml_file}")
            print("=" * 60)

            # Show topic breakdown
            print("\n📋 Topic-Übersicht:")
            for topic, template in results.items():
                module_id = self._determine_module_id(topic)
                sub_category = self._determine_sub_category(topic)
                msg_count = template["statistics"]["total_messages"]
                print(f"   • {topic} ({module_id}/{sub_category}): {msg_count} Nachrichten")
        else:
            print("❌ Keine MODULE Topics mit Daten gefunden!")


def main():
    """Main function for standalone execution"""
    analyzer = ModuleTemplateAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
