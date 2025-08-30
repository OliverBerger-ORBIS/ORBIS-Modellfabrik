#!/usr/bin/env python3
"""
Semantic Template Generator für OMF Dashboard
Erstellt generische Message Templates mit Variablen für MQTT-Control
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml


class SemanticTemplateGenerator:
    """Generiert semantische Message Templates mit Variablen"""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.module_config_path = self.config_dir / "module_config.yml"
        self.template_dir = self.config_dir / "message_templates" / "templates"

    def load_module_config(self) -> Dict[str, Any]:
        """Lädt Module-Konfiguration"""
        try:
            with open(self.module_config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Fehler beim Laden der Module-Konfiguration: {e}")
            return {}

    def generate_semantic_templates(self) -> Dict[str, Any]:
        """Generiert semantische Templates für alle Kategorien"""
        semantic_templates = {}

        # Module Templates
        semantic_templates["module"] = self._generate_module_semantic_templates()

        # CCU Templates
        semantic_templates["ccu"] = self._generate_ccu_semantic_templates()

        # TXT Templates
        semantic_templates["txt"] = self._generate_txt_semantic_templates()

        # Node-RED Templates
        semantic_templates["node_red"] = self._generate_node_red_semantic_templates()

        return semantic_templates

    def _generate_module_semantic_templates(self) -> Dict[str, Any]:
        """Generiert semantische Module-Templates"""
        module_config = self.load_module_config()
        templates = {}

        # Extrahiere Module aus der korrekten Struktur
        modules = module_config.get("modules", {})
        enabled_modules = {
            module_id: module_info
            for module_id, module_info in modules.items()
            if module_info.get("enabled", True)
        }

        # Connection Template (generisch für alle Module)
        templates["module/connection"] = {
            "category": "MODULE",
            "description": "Module Connection Status - Generisch für alle Module",
            "semantic_purpose": "Verbindungsstatus eines Moduls überwachen",
            "mqtt_topic_pattern": "module/v1/ff/{module_id}/connection",
            "template_structure": {
                "module_id": "<module_serial_number>",
                "connected": "<boolean>",
                "ip": "<ip_address>",
                "serialNumber": "<module_serial_number>",
                "version": "<module_version>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "module_id": {
                    "type": "enum",
                    "values": list(enabled_modules.keys()),
                    "description": "Serial Number des Moduls",
                },
                "ip": {
                    "type": "enum",
                    "values": self._get_all_module_ips(modules),
                    "description": "IP-Adresse des Moduls",
                },
                "serialNumber": {
                    "type": "enum",
                    "values": list(enabled_modules.keys()),
                    "description": "Serial Number des Moduls",
                },
                "version": {
                    "type": "enum",
                    "values": self._get_all_module_versions(modules),
                    "description": "Version des Moduls",
                },
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "connected muss boolean sein",
                "module_id muss gültige Serial Number sein",
                "ip muss gültige IP-Adresse sein",
                "version muss gültige Versionsnummer sein",
            ],
            "mqtt_control_usage": {
                "description": "Verbindungsstatus eines spezifischen Moduls abfragen",
                "example_topic": "module/v1/ff/SVR3QA0022/connection",
                "example_payload": {
                    "module_id": "SVR3QA0022",
                    "connected": True,
                    "ip": "192.168.0.80",
                    "serialNumber": "SVR3QA0022",
                    "version": "1.3.0",
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        # State Template (generisch für alle Module)
        templates["module/state"] = {
            "category": "MODULE",
            "description": "Module State - Generisch für alle Module",
            "semantic_purpose": "Aktuellen Zustand eines Moduls abfragen",
            "mqtt_topic_pattern": "module/v1/ff/{module_id}/state",
            "template_structure": {
                "module_id": "<module_serial_number>",
                "state": "<module_state>",
                "status": "<module_status>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "module_id": {
                    "type": "enum",
                    "values": list(enabled_modules.keys()),
                    "description": "Serial Number des Moduls",
                },
                "state": {
                    "type": "enum",
                    "values": ["IDLE", "BUSY", "ERROR", "MAINTENANCE", "OFFLINE"],
                    "description": "Aktueller Zustand des Moduls",
                },
                "status": {
                    "type": "enum",
                    "values": ["OK", "WARNING", "ERROR", "UNKNOWN"],
                    "description": "Status des Moduls",
                },
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "module_id muss gültige Serial Number sein",
                "state muss gültiger Modul-Zustand sein",
                "status muss gültiger Status sein",
            ],
            "mqtt_control_usage": {
                "description": "Zustand eines spezifischen Moduls abfragen",
                "example_topic": "module/v1/ff/SVR3QA0022/state",
                "example_payload": {
                    "module_id": "SVR3QA0022",
                    "state": "IDLE",
                    "status": "OK",
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        # Order Template (generisch für alle Module)
        templates["module/order"] = {
            "category": "MODULE",
            "description": "Module Order - Generisch für alle Module",
            "semantic_purpose": "Auftrag an ein Modul senden",
            "mqtt_topic_pattern": "module/v1/ff/{module_id}/order",
            "template_structure": {
                "module_id": "<module_serial_number>",
                "command": "<module_command>",
                "parameters": "<command_parameters>",
                "order_id": "<order_id>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "module_id": {
                    "type": "enum",
                    "values": list(enabled_modules.keys()),
                    "description": "Serial Number des Moduls",
                },
                "command": {
                    "type": "enum",
                    "values": self._get_all_module_commands(modules),
                    "description": "Befehl für das Modul",
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameter für den Befehl (modulspezifisch)",
                },
                "order_id": {"type": "string", "description": "Eindeutige Auftrags-ID"},
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "module_id muss gültige Serial Number sein",
                "command muss gültiger Befehl für das Modul sein",
                "order_id muss eindeutig sein",
            ],
            "mqtt_control_usage": {
                "description": "Auftrag an ein spezifisches Modul senden",
                "example_topic": "module/v1/ff/SVR3QA0022/order",
                "example_payload": {
                    "module_id": "SVR3QA0022",
                    "command": "PICK",
                    "parameters": {"position": "A1"},
                    "order_id": "ORDER_001",
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        return templates

    def _generate_ccu_semantic_templates(self) -> Dict[str, Any]:
        """Generiert semantische CCU-Templates"""
        templates = {}

        # CCU Control Template
        templates["ccu/control"] = {
            "category": "CCU",
            "description": "CCU Control Commands - Generisch",
            "semantic_purpose": "Befehle an die CCU senden",
            "mqtt_topic_pattern": "ccu/control",
            "template_structure": {
                "command": "<ccu_command>",
                "parameters": "<command_parameters>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "command": {
                    "type": "enum",
                    "values": [
                        "start",
                        "stop",
                        "reset",
                        "pause",
                        "resume",
                        "emergency_stop",
                    ],
                    "description": "CCU-Befehl",
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameter für den Befehl",
                },
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "command muss gültiger CCU-Befehl sein",
                "parameters muss gültiges JSON-Objekt sein",
            ],
            "mqtt_control_usage": {
                "description": "CCU-Befehl senden",
                "example_topic": "ccu/control",
                "example_payload": {
                    "command": "start",
                    "parameters": {"module": "SVR3QA0022"},
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        # CCU State Config Template
        templates["ccu/state/config"] = {
            "category": "CCU",
            "description": "CCU State Config - Generisch",
            "semantic_purpose": "CCU-Konfigurationsstatus überwachen",
            "mqtt_topic_pattern": "ccu/state/config",
            "template_structure": {
                "version": "<string>",
                "modules": "<array>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "version": {"type": "string", "description": "CCU-Version"},
                "modules": {"type": "array", "description": "Verfügbare Module"},
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "version muss gültige Versionsnummer sein",
                "modules muss Array von Module-IDs sein",
            ],
            "mqtt_control_usage": {
                "description": "CCU-Konfigurationsstatus abfragen",
                "example_topic": "ccu/state/config",
                "example_payload": {
                    "version": "1.0.0",
                    "modules": ["SVR3QA2098", "SVR4H73275", "SVR4H76530"],
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        # CCU State Status Template
        templates["ccu/state/status"] = {
            "category": "CCU",
            "description": "CCU State Status - Generisch",
            "semantic_purpose": "CCU-Status überwachen",
            "mqtt_topic_pattern": "ccu/state/status",
            "template_structure": {
                "status": "<string>",
                "health": "<string>",
                "active_modules": "<number>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "status": {
                    "type": "enum",
                    "values": ["running", "stopped", "error", "maintenance"],
                    "description": "CCU-Status",
                },
                "health": {
                    "type": "enum",
                    "values": ["good", "warning", "critical"],
                    "description": "CCU-Gesundheit",
                },
                "active_modules": {
                    "type": "number",
                    "description": "Anzahl aktiver Module",
                },
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "status muss gültiger CCU-Status sein",
                "health muss gültiger Gesundheitsstatus sein",
                "active_modules muss positive Zahl sein",
            ],
            "mqtt_control_usage": {
                "description": "CCU-Status abfragen",
                "example_topic": "ccu/state/status",
                "example_payload": {
                    "status": "running",
                    "health": "good",
                    "active_modules": 5,
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        return templates

    def _generate_txt_semantic_templates(self) -> Dict[str, Any]:
        """Generiert semantische TXT-Templates"""
        templates = {}

        # TXT Order Input Template
        templates["txt/order_input"] = {
            "category": "TXT",
            "description": "TXT Order Input - Generisch",
            "semantic_purpose": "Auftragseingang über TXT-Controller",
            "mqtt_topic_pattern": "/j1/txt/1/f/i/order",
            "template_structure": {
                "state": "<order_state>",
                "type": "<workpiece_type>",
                "ts": "<datetime>",
            },
            "variable_fields": {
                "state": {
                    "type": "enum",
                    "values": [
                        "WAITING_FOR_ORDER",
                        "IN_PROCESS",
                        "COMPLETED",
                        "FINISHED",
                        "RAW",
                        "RESERVED",
                    ],
                    "description": "Zustand des Auftrags",
                },
                "type": {
                    "type": "enum",
                    "values": ["RED", "WHITE", "BLUE"],
                    "description": "Typ des Werkstücks",
                },
            },
            "validation_rules": [
                "ts muss ISO 8601 Format haben",
                "state muss gültiger Auftragszustand sein",
                "type muss gültiger Werkstück-Typ sein",
            ],
            "mqtt_control_usage": {
                "description": "Auftragszustand über TXT-Controller abfragen",
                "example_topic": "/j1/txt/1/f/i/order",
                "example_payload": {
                    "state": "WAITING_FOR_ORDER",
                    "type": "RED",
                    "ts": "2025-08-29T10:00:00Z",
                },
            },
        }

        return templates

    def _generate_node_red_semantic_templates(self) -> Dict[str, Any]:
        """Generiert semantische Node-RED-Templates"""
        templates = {}

        # Node-RED Dashboard State Template
        templates["node_red/dashboard_state"] = {
            "category": "Node-RED",
            "description": "Node-RED Dashboard State - Generisch",
            "semantic_purpose": "Dashboard-Status von Node-RED abfragen",
            "mqtt_topic_pattern": "ccu/state/dashboard",
            "template_structure": {
                "status": "<dashboard_status>",
                "flows": "<number_of_flows>",
                "active_flows": "<active_flows_count>",
                "timestamp": "<datetime>",
            },
            "variable_fields": {
                "status": {
                    "type": "enum",
                    "values": ["running", "stopped", "error", "maintenance"],
                    "description": "Status des Dashboards",
                },
                "flows": {"type": "number", "description": "Anzahl aller Flows"},
                "active_flows": {
                    "type": "number",
                    "description": "Anzahl aktiver Flows",
                },
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                "status muss gültiger Dashboard-Status sein",
                "flows muss positive Zahl sein",
                "active_flows muss positive Zahl sein",
            ],
            "mqtt_control_usage": {
                "description": "Dashboard-Status von Node-RED abfragen",
                "example_topic": "ccu/state/dashboard",
                "example_payload": {
                    "status": "running",
                    "flows": 5,
                    "active_flows": 3,
                    "timestamp": "2025-08-29T10:00:00Z",
                },
            },
        }

        return templates

    def _get_all_module_ips(self, module_config: Dict[str, Any]) -> List[str]:
        """Extrahiert alle IP-Adressen aus Module-Config"""
        ips = set()
        for module_info in module_config.values():
            if isinstance(module_info, dict) and "ip_addresses" in module_info:
                ips.update(module_info["ip_addresses"])
        return sorted(ips)

    def _get_all_module_versions(self, module_config: Dict[str, Any]) -> List[str]:
        """Extrahiert alle Versionen aus Module-Config"""
        versions = set()
        for module_info in module_config.values():
            if isinstance(module_info, dict) and "version" in module_info:
                versions.add(module_info["version"])
        return sorted(versions)

    def _get_all_module_commands(self, module_config: Dict[str, Any]) -> List[str]:
        """Extrahiert alle Commands aus Module-Config"""
        commands = set()
        for module_info in module_config.values():
            if isinstance(module_info, dict) and "commands" in module_info:
                commands.update(module_info["commands"])
        return sorted(commands)

    def save_semantic_templates(self, templates: Dict[str, Any]) -> None:
        """Speichert semantische Templates in YAML-Dateien"""
        semantic_dir = self.template_dir / "semantic"
        semantic_dir.mkdir(exist_ok=True)

        for category, category_templates in templates.items():
            file_path = semantic_dir / f"{category}_semantic.yml"

            yaml_content = {
                "metadata": {
                    "category": category.upper(),
                    "description": f"Semantic {category.title()} Templates",
                    "generated": True,
                    "semantic": True,
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "version": "3.0.0",
                },
                "templates": category_templates,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    yaml_content,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            print(
                f"✅ {len(category_templates)} semantische {category.title()}-Templates in {file_path} gespeichert"
            )


def main():
    """Hauptfunktion"""
    print("\n🔧 Semantic Template Generator")
    print("=" * 50)

    generator = SemanticTemplateGenerator()

    print("\n📊 Generiere semantische Templates...")
    semantic_templates = generator.generate_semantic_templates()

    # Speichere Templates
    generator.save_semantic_templates(semantic_templates)

    # Zeige Statistiken
    total_templates = sum(len(templates) for templates in semantic_templates.values())
    print(f"\n✅ {total_templates} semantische Templates generiert")

    for category, templates in semantic_templates.items():
        print(f"   📁 {category.title()}: {len(templates)} Templates")

    print("\n🎯 Semantische Templates für MQTT-Control bereit!")


if __name__ == "__main__":
    main()
