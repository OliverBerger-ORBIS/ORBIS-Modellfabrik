#!/usr/bin/env python3
"""
Template Generator - Generiert Module-spezifische Templates aus generischen Templates
Version: 3.0.0
"""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


class TemplateGenerator:
    """Generiert Module-spezifische Templates aus generischen Templates"""

    def __init__(self, module_config_path: str = None, templates_dir: str = None):
        """Initialisiert den Template Generator"""
        if module_config_path is None:
            module_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "module_config.yml")

        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), "..", "config", "message_templates")

        self.module_config_path = Path(module_config_path)
        self.templates_dir = Path(templates_dir)
        self.module_config = self._load_module_config()

    def _load_module_config(self) -> Dict[str, Any]:
        """Lädt die Module-Konfiguration"""
        try:
            if self.module_config_path.exists():
                with open(self.module_config_path, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                print(f"⚠️ Module-Konfiguration nicht gefunden: {self.module_config_path}")
                return {}
        except Exception as e:
            print(f"❌ Fehler beim Laden der Module-Konfiguration: {e}")
            return {}

    def generate_module_templates(self, template_type: str = "connection") -> Dict[str, Any]:
        """Generiert Module-spezifische Templates"""
        if not self.module_config:
            return {}

        generated_templates = {}
        modules = self.module_config.get("modules", {})

        for module_id, module_info in modules.items():
            if not module_info.get("enabled", True):
                continue

            # Generiere Template basierend auf Template-Typ
            if template_type == "connection":
                template = self._generate_connection_template(module_id, module_info)
            elif template_type == "state":
                template = self._generate_state_template(module_id, module_info)
            elif template_type == "order":
                template = self._generate_order_template(module_id, module_info)
            elif template_type == "factsheet":
                template = self._generate_factsheet_template(module_id, module_info)
            else:
                template = self._generate_generic_template(module_id, module_info, template_type)

            if template:
                topic = f"module/v1/ff/{module_id}/{template_type}"
                generated_templates[topic] = template

        return generated_templates

    def _generate_connection_template(self, module_id: str, module_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Connection Template für ein Modul"""
        ip_addresses = module_info.get("ip_addresses", [])
        primary_ip = ip_addresses[0] if ip_addresses else "192.168.0.0"

        return {
            "category": "MODULE",
            "description": f"Module {module_id} Connection",
            "examples": [
                {
                    "connectionState": "ONLINE",
                    "headerId": 26,
                    "ip": primary_ip,
                    "manufacturer": "Fischertechnik",
                    "serialNumber": module_id,
                    "timestamp": "2025-08-19T09:13:34.483Z",
                    "version": "1.3.0",  # Standard-Version, könnte aus Config kommen
                }
            ],
            "module": module_id,
            "sub_category": "Connection",
            "template_structure": {
                "connectionState": "[ONLINE]",
                "headerId": "<string>",
                "ip": f"[{primary_ip}]",
                "manufacturer": "[Fischertechnik]",
                "serialNumber": f"[{module_id}]",
                "timestamp": "<datetime>",
                "version": "[1.3.0]",
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                f"ip muss in [{primary_ip}] sein",
                "version muss in [1.3.0] sein",
                "manufacturer muss in [Fischertechnik] sein",
                f"serialNumber muss in [{module_id}] sein",
                "connectionState muss in [ONLINE] sein",
            ],
        }

    def _generate_state_template(self, module_id: str, module_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert State Template für ein Modul"""
        return {
            "category": "MODULE",
            "description": f"Module {module_id} State",
            "examples": [
                {
                    "module_id": module_id,
                    "status": "READY",
                    "timestamp": "2025-08-19T09:13:34.483Z",
                }
            ],
            "module": module_id,
            "sub_category": "State",
            "template_structure": {
                "module_id": f"[{module_id}]",
                "status": "<string>",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                f"module_id muss in [{module_id}] sein",
                "status muss gültiger Status sein",
            ],
        }

    def _generate_order_template(self, module_id: str, module_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Order Template für ein Modul"""
        commands = module_info.get("commands", [])

        return {
            "category": "MODULE",
            "description": f"Module {module_id} Order",
            "examples": [
                {
                    "module_id": module_id,
                    "command": commands[0] if commands else "PICK",
                    "parameters": {},
                    "timestamp": "2025-08-19T09:13:34.483Z",
                }
            ],
            "module": module_id,
            "sub_category": "Order",
            "template_structure": {
                "module_id": f"[{module_id}]",
                "command": f"[{', '.join(commands)}]",
                "parameters": "<object>",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                f"module_id muss in [{module_id}] sein",
                f"command muss in [{', '.join(commands)}] sein",
            ],
        }

    def _generate_factsheet_template(self, module_id: str, module_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert Factsheet Template für ein Modul"""
        return {
            "category": "MODULE",
            "description": f"Module {module_id} Factsheet",
            "examples": [
                {
                    "module_id": module_id,
                    "name": module_info.get("name", "Unknown"),
                    "type": module_info.get("type", "Unknown"),
                    "sub_type": module_info.get("sub_type", "Unknown"),
                    "description": module_info.get("description", ""),
                    "ip_addresses": module_info.get("ip_addresses", []),
                    "commands": module_info.get("commands", []),
                    "enabled": module_info.get("enabled", True),
                    "timestamp": "2025-08-19T09:13:34.483Z",
                }
            ],
            "module": module_id,
            "sub_category": "Factsheet",
            "template_structure": {
                "module_id": f"[{module_id}]",
                "name": f"[{module_info.get('name', 'Unknown')}]",
                "type": f"[{module_info.get('type', 'Unknown')}]",
                "sub_type": f"[{module_info.get('sub_type', 'Unknown')}]",
                "description": "<string>",
                "ip_addresses": "<array>",
                "commands": "<array>",
                "enabled": "<boolean>",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                f"module_id muss in [{module_id}] sein",
                f"name muss in [{module_info.get('name', 'Unknown')}] sein",
                f"type muss in [{module_info.get('type', 'Unknown')}] sein",
                f"sub_type muss in [{module_info.get('sub_type', 'Unknown')}] sein",
                "enabled muss boolean sein",
            ],
        }

    def _generate_generic_template(
        self, module_id: str, module_info: Dict[str, Any], template_type: str
    ) -> Dict[str, Any]:
        """Generiert generisches Template für ein Modul"""
        return {
            "category": "MODULE",
            "description": f"Module {module_id} {template_type.title()}",
            "examples": [{"module_id": module_id, "timestamp": "2025-08-19T09:13:34.483Z"}],
            "module": module_id,
            "sub_category": template_type.title(),
            "template_structure": {
                "module_id": f"[{module_id}]",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "timestamp muss ISO 8601 Format haben",
                f"module_id muss in [{module_id}] sein",
            ],
        }

    def save_generated_templates(self, templates: Dict[str, Any], template_type: str) -> bool:
        """Speichert generierte Templates in eine YAML-Datei"""
        try:
            output_file = self.templates_dir / "templates" / "module" / f"{template_type}_generated.yml"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            template_data = {
                "metadata": {
                    "version": "3.0.0",
                    "last_updated": "2025-08-29",
                    "description": f"Generated {template_type} Templates",
                    "category": "MODULE",
                    "sub_category": template_type.title(),
                    "icon": "🔗",
                    "generated": True,
                    "source": "module_config.yml",
                },
                "templates": templates,
            }

            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    template_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    indent=2,
                )

            print(f"✅ {len(templates)} generierte Templates in {output_file} gespeichert")
            return True

        except Exception as e:
            print(f"❌ Fehler beim Speichern der Templates: {e}")
            return False

    def generate_all_module_templates(self) -> Dict[str, Dict[str, Any]]:
        """Generiert alle Module-Template-Typen"""
        template_types = ["connection", "state", "order", "factsheet"]
        all_templates = {}

        for template_type in template_types:
            templates = self.generate_module_templates(template_type)
            all_templates[template_type] = templates

            # Speichere Templates
            self.save_generated_templates(templates, template_type)

        return all_templates

    def generate_ccu_templates(self) -> Dict[str, Any]:
        """Generiert CCU-spezifische Templates"""
        ccu_templates = {}

        # CCU Control Templates
        ccu_templates["ccu/control"] = {
            "category": "CCU",
            "description": "CCU Control Commands",
            "examples": [
                {
                    "command": "start",
                    "parameters": {"module": "hbw"},
                    "timestamp": "2025-08-29T10:00:00Z",
                },
                {
                    "command": "stop",
                    "parameters": {"module": "vgr"},
                    "timestamp": "2025-08-29T10:05:00Z",
                },
            ],
            "sub_category": "Control",
            "template_structure": {
                "command": "<string>",
                "parameters": "<object>",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "command muss gültiger Befehl sein (start, stop, reset, pause)",
                "timestamp muss ISO 8601 Format haben",
                "parameters muss ein gültiges JSON-Objekt sein",
            ],
        }

        # CCU State Templates
        ccu_templates["ccu/state/config"] = {
            "category": "CCU",
            "description": "CCU Configuration State",
            "examples": [
                {
                    "version": "1.0.0",
                    "modules": ["SVR3QA2098", "SVR4H73275", "SVR4H76530"],
                    "timestamp": "2025-08-19T09:08:26.191Z",
                }
            ],
            "sub_category": "State",
            "template_structure": {
                "version": "<string>",
                "modules": "<array>",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "version muss gültige Versionsnummer sein",
                "modules muss Array von Module-IDs sein",
                "timestamp muss ISO 8601 Format haben",
            ],
        }

        return ccu_templates

    def generate_txt_templates(self) -> Dict[str, Any]:
        """Generiert TXT-spezifische Templates"""
        txt_templates = {}

        # TXT Control Templates
        txt_templates["/j1/txt/1/c/bme680"] = {
            "category": "TXT",
            "description": "TXT Controller BME680 Sensor Control",
            "examples": [{"period": 60, "ts": "2025-08-20T09:57:49.496Z"}],
            "sub_category": "Control",
            "template_structure": {"period": "<number>", "ts": "<datetime>"},
            "validation_rules": [
                "period muss positive Zahl sein",
                "ts muss ISO 8601 Format haben",
            ],
        }

        # TXT Input Templates
        txt_templates["/j1/txt/1/f/i/order"] = {
            "category": "TXT",
            "description": "TXT Controller Order Input",
            "examples": [
                {"state": "WAITING_FOR_ORDER", "ts": "2025-08-19T09:13:09.366Z"},
                {
                    "state": "IN_PROCESS",
                    "ts": "2025-08-19T09:16:14.679Z",
                    "type": "RED",
                },
            ],
            "sub_category": "Input",
            "template_structure": {
                "state": "<string>",
                "ts": "<datetime>",
                "type": "<string>",
            },
            "validation_rules": [
                "state muss gültiger Zustand sein (WAITING_FOR_ORDER, IN_PROCESS, COMPLETED)",
                "ts muss ISO 8601 Format haben",
                "type ist optional (RED, WHITE, BLUE)",
            ],
        }

        return txt_templates

    def generate_node_red_templates(self) -> Dict[str, Any]:
        """Generiert Node-RED-spezifische Templates"""
        node_red_templates = {}

        # Node-RED State Templates
        node_red_templates["ccu/state/dashboard"] = {
            "category": "Node-RED",
            "description": "Node-RED Dashboard State",
            "examples": [
                {
                    "status": "running",
                    "flows": 5,
                    "active_flows": 3,
                    "timestamp": "2025-08-19T09:08:26.191Z",
                }
            ],
            "sub_category": "State",
            "template_structure": {
                "status": "<string>",
                "flows": "<number>",
                "active_flows": "<number>",
                "timestamp": "<datetime>",
            },
            "validation_rules": [
                "status muss gültiger Status sein (running, stopped, error)",
                "flows muss positive Zahl sein",
                "active_flows muss positive Zahl sein",
                "timestamp muss ISO 8601 Format haben",
            ],
        }

        # Node-RED Connection Templates
        node_red_templates["module/v1/ff/NodeRed/connection"] = {
            "category": "Node-RED",
            "description": "Node-RED Connection Status",
            "examples": [
                {
                    "connected": True,
                    "module_id": "NodeRed",
                    "timestamp": "2025-08-19T09:08:26.191Z",
                    "version": "1.0.0",
                }
            ],
            "sub_category": "Connection",
            "template_structure": {
                "connected": "<boolean>",
                "module_id": "<string>",
                "timestamp": "<datetime>",
                "version": "<string>",
            },
            "validation_rules": [
                "connected muss boolean sein",
                "module_id muss 'NodeRed' sein",
                "timestamp muss ISO 8601 Format haben",
                "version muss gültige Versionsnummer sein",
            ],
        }

        return node_red_templates

    def generate_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """Generiert alle Template-Typen"""
        all_templates = {}

        # Module Templates
        all_templates["module"] = self.generate_all_module_templates()

        # CCU Templates
        all_templates["ccu"] = self.generate_ccu_templates()

        # TXT Templates
        all_templates["txt"] = self.generate_txt_templates()

        # Node-RED Templates
        all_templates["node_red"] = self.generate_node_red_templates()

        return all_templates


def main():
    """Hauptfunktion für Template-Generierung"""
    print("🔧 Template Generator")
    print("=" * 50)

    generator = TemplateGenerator()

    # Generiere alle Module-Templates
    print("\n📊 Generiere Module-Templates...")
    all_templates = generator.generate_all_module_templates()

    total_templates = sum(len(templates) for templates in all_templates.values())
    print(f"✅ {total_templates} Templates generiert")

    for template_type, templates in all_templates.items():
        print(f"   📁 {template_type}: {len(templates)} Templates")


if __name__ == "__main__":
    main()
