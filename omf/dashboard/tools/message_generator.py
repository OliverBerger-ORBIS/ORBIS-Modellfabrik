#!/usr/bin/env python3
"""
Message Generator für OMF Dashboard
Verwendet Message-Templates um semantisch korrekte MQTT-Nachrichten zu generieren
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class MessageGenerator:
    """Generiert semantisch korrekte MQTT-Nachrichten basierend auf Templates"""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.module_config_path = self.config_dir / "module_config.yml"
        self.topic_config_path = self.config_dir / "topic_config.yml"
        self.template_dir = self.config_dir / "message_templates" / "templates"

        # Lade Konfigurationen
        self.module_config = self._load_module_config()
        self.topic_config = self._load_topic_config()
        self.semantic_templates = self._load_semantic_templates()

    def _load_module_config(self) -> Dict[str, Any]:
        """Lädt Module-Konfiguration"""
        try:
            with open(self.module_config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Fehler beim Laden der Module-Konfiguration: {e}")
            return {}

    def _load_topic_config(self) -> Dict[str, Any]:
        """Lädt Topic-Konfiguration"""
        try:
            with open(self.topic_config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Fehler beim Laden der Topic-Konfiguration: {e}")
            return {}

    def _load_semantic_templates(self) -> Dict[str, Any]:
        """Lädt semantische Templates und normale Templates"""
        templates = {}

        # Lade semantische Templates
        semantic_dir = self.template_dir / "semantic"
        if semantic_dir.exists():
            for file_path in semantic_dir.glob("*_semantic.yml"):
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if "templates" in data:
                            templates.update(data["templates"])
                except Exception as e:
                    print(f"❌ Fehler beim Laden von {file_path}: {e}")

        # Lade normale Templates (für FTS, Module, etc.)
        for file_path in self.template_dir.glob("**/*.yml"):
            if "_semantic.yml" not in file_path.name:  # Überspringe semantische Templates
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if "templates" in data:
                            templates.update(data["templates"])
                except Exception as e:
                    print(f"❌ Fehler beim Laden von {file_path}: {e}")

        return templates

    def get_available_modules(self) -> List[str]:
        """Gibt verfügbare Module zurück"""
        modules = self.module_config.get("modules", {})
        return [module_id for module_id, module_info in modules.items() if module_info.get("enabled", True)]

    def get_module_commands(self, module_id: str) -> List[str]:
        """Gibt verfügbare Commands für ein Modul zurück"""
        modules = self.module_config.get("modules", {})
        module_info = modules.get(module_id, {})
        return module_info.get("commands", [])

    def get_available_templates(self) -> List[str]:
        """Gibt verfügbare Template-Namen zurück"""
        return list(self.semantic_templates.keys())

    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Gibt Template-Informationen zurück"""
        return self.semantic_templates.get(template_name)

    def generate_message(self, template_name: str, **parameters) -> Tuple[str, Dict[str, Any]]:
        """
        Generiert eine MQTT-Nachricht basierend auf Template und Parametern

        Args:
            template_name: Name des Templates (z.B. 'module/order')
            **parameters: Parameter für die Nachricht (z.B. module_id='SVR3QA0022', command='PICK')

        Returns:
            Tuple von (topic, payload)
        """
        template = self.semantic_templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' nicht gefunden")

        # Generiere Topic
        topic = self._generate_topic(template, parameters)

        # Generiere Payload
        payload = self._generate_payload(template, parameters)

        return topic, payload

    def generate_factory_reset_message(self, with_storage: bool = False) -> Optional[Dict[str, Any]]:
        """Generiert Factory Reset Message mit dem bewährten Template"""
        try:
            # Bewährte Factory Reset Message (funktioniert)
            return {
                "topic": "ccu/set/reset",
                "payload": {
                    "timestamp": datetime.now().isoformat().replace("+00:00", "Z"),
                    "withStorage": with_storage,
                },
            }

        except Exception as e:
            print(f"❌ Fehler beim Generieren der Factory Reset Message: {e}")
            return None

    def generate_module_sequence_message(
        self, module: str, step: str, step_number: int = 1, order_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """Generiert Message für Modul-Sequenz-Schritt mit WorkflowOrderManager"""
        try:
            # Modul-spezifische Serial Number
            module_serial = self._get_module_serial(module)
            if not module_serial:
                print(f"❌ Keine Serial Number für Modul {module} gefunden")
                return None

            # Command aus Step extrahieren
            command = step.split("(")[0] if "(" in step else step

            # WorkflowOrderManager für ORDER-ID Management
            try:
                from .workflow_order_manager import get_workflow_order_manager
            except ImportError:
                from workflow_order_manager import get_workflow_order_manager
            workflow_manager = get_workflow_order_manager()

            # ORDER-ID und orderUpdateId verwalten
            if order_id is None:
                # Neuer Workflow starten
                commands = ["PICK", "PROCESS", "DROP"]
                order_id = workflow_manager.start_workflow(module, commands)

            # Nächste orderUpdateId holen
            workflow_info = workflow_manager.execute_command(order_id, command)
            order_update_id = workflow_info["orderUpdateId"]

            # Template verwenden
            template_name = "module/order"
            template = self.semantic_templates.get(template_name)

            if not template:
                # Fallback: Einfache Module Order Message (exakt wie in funktionierendem Commit)
                return {
                    "topic": f"module/v1/ff/{module_serial}/order",
                    "payload": {
                        "serialNumber": module_serial,
                        "orderId": order_id,
                        "orderUpdateId": order_update_id,
                        "action": {
                            "id": str(uuid.uuid4()),
                            "command": command,
                            "metadata": {
                                "priority": "NORMAL",
                                "timeout": 300,
                                "type": "WHITE",  # Default workpiece type
                            },
                        },
                    },
                }

            # Verwende Template-basierte Generierung
            topic, payload = self.generate_message(
                template_name,
                module_id=module_serial,
                command=command,
                order_id=order_id,
                parameters={
                    "orderUpdateId": order_update_id,
                    "subActionId": step_number,
                },
            )

            return {"topic": topic, "payload": payload}

        except Exception as e:
            print(f"❌ Fehler beim Generieren der Modul-Sequenz Message: {e}")
            return None

    def generate_fts_command_message(self, command: str) -> Optional[Dict[str, Any]]:
        """Generiert FTS-Command Message"""
        try:
            # FTS Serial Number
            fts_serial = "5iO4"  # FTS Serial Number

            # Fallback: Einfache FTS Command Message (bewährte Struktur)
            return {
                "topic": f"fts/v1/ff/{fts_serial}/command",
                "payload": {
                    "serialNumber": fts_serial,
                    "orderId": str(uuid.uuid4()),
                    "orderUpdateId": 1,
                    "action": {
                        "id": str(uuid.uuid4()),
                        "command": command.upper(),
                        "metadata": {
                            "priority": "NORMAL",
                            "timeout": 300,
                            "type": "TRANSPORT",
                        },
                    },
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            print(f"❌ Fehler beim Generieren der FTS Command Message: {e}")
            return None

    def generate_fts_navigation_message(
        self,
        route_type: str,
        order_id: str = None,
        order_update_id: int = 0,
        load_type: str = "WHITE",
        load_id: str = None,
    ) -> Optional[Dict[str, Any]]:
        """Generiert FTS-Navigation Message basierend auf Route-Typ"""
        try:
            # FTS Serial Number
            fts_serial = "5iO4"

            # Order-ID generieren falls nicht vorhanden
            if order_id is None:
                order_id = f"fts-navigation-{route_type.lower()}-{uuid.uuid4().hex[:8]}"

            # Load-ID generieren falls nicht vorhanden
            if load_id is None:
                load_id = f"04{uuid.uuid4().hex[:12]}"

            # Route-Definitionen basierend auf Session-Analyse
            route_definitions = {
                "DPS_HBW": {
                    "nodes": [
                        {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
                        {
                            "id": "2",
                            "linkedEdges": ["SVR4H73275-2", "2-1"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "1",
                            "linkedEdges": ["2-1", "1-SVR3QA0022"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "SVR3QA0022",
                            "linkedEdges": ["1-SVR3QA0022"],
                            "action": {
                                "type": "DOCK",
                                "id": str(uuid.uuid4()),
                                "metadata": {"loadId": load_id, "loadType": load_type, "loadPosition": "1"},
                            },
                        },
                    ],
                    "edges": [
                        {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
                        {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
                        {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]},
                    ],
                },
                "HBW_DPS": {
                    "nodes": [
                        {"id": "SVR3QA0022", "linkedEdges": ["SVR3QA0022-1"]},
                        {
                            "id": "1",
                            "linkedEdges": ["SVR3QA0022-1", "1-2"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "2",
                            "linkedEdges": ["1-2", "2-SVR4H73275"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "SVR4H73275",
                            "linkedEdges": ["2-SVR4H73275"],
                            "action": {
                                "type": "DOCK",
                                "id": str(uuid.uuid4()),
                                "metadata": {"loadId": load_id, "loadType": load_type, "loadPosition": "1"},
                            },
                        },
                    ],
                    "edges": [
                        {"id": "SVR3QA0022-1", "length": 380, "linkedNodes": ["SVR3QA0022", "1"]},
                        {"id": "1-2", "length": 360, "linkedNodes": ["1", "2"]},
                        {"id": "2-SVR4H73275", "length": 380, "linkedNodes": ["2", "SVR4H73275"]},
                    ],
                },
                "RED_Prod": {
                    "nodes": [
                        {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
                        {
                            "id": "2",
                            "linkedEdges": ["SVR4H73275-2", "2-1"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "1",
                            "linkedEdges": ["2-1", "1-SVR3QA0022"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "SVR3QA0022",
                            "linkedEdges": ["1-SVR3QA0022"],
                            "action": {
                                "type": "DOCK",
                                "id": str(uuid.uuid4()),
                                "metadata": {"loadId": load_id, "loadType": "RED", "loadPosition": "1"},
                            },
                        },
                    ],
                    "edges": [
                        {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
                        {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
                        {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]},
                    ],
                },
                "BLUE_Prod": {
                    "nodes": [
                        {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
                        {
                            "id": "2",
                            "linkedEdges": ["SVR4H73275-2", "2-1"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "1",
                            "linkedEdges": ["2-1", "1-SVR3QA0022"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "SVR3QA0022",
                            "linkedEdges": ["1-SVR3QA0022"],
                            "action": {
                                "type": "DOCK",
                                "id": str(uuid.uuid4()),
                                "metadata": {"loadId": load_id, "loadType": "BLUE", "loadPosition": "1"},
                            },
                        },
                    ],
                    "edges": [
                        {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
                        {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
                        {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]},
                    ],
                },
                "WHITE_Prod": {
                    "nodes": [
                        {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
                        {
                            "id": "2",
                            "linkedEdges": ["SVR4H73275-2", "2-1"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "1",
                            "linkedEdges": ["2-1", "1-SVR3QA0022"],
                            "action": {"id": str(uuid.uuid4()), "type": "PASS"},
                        },
                        {
                            "id": "SVR3QA0022",
                            "linkedEdges": ["1-SVR3QA0022"],
                            "action": {
                                "type": "DOCK",
                                "id": str(uuid.uuid4()),
                                "metadata": {"loadId": load_id, "loadType": "WHITE", "loadPosition": "1"},
                            },
                        },
                    ],
                    "edges": [
                        {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
                        {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
                        {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]},
                    ],
                },
            }

            # Route-Definition holen
            route_def = route_definitions.get(route_type)
            if not route_def:
                print(f"❌ Unbekannte Route: {route_type}")
                return None

            # Navigation Message generieren
            return {
                "topic": f"fts/v1/ff/{fts_serial}/order",
                "payload": {
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    "orderId": order_id,
                    "orderUpdateId": order_update_id,
                    "nodes": route_def["nodes"],
                    "edges": route_def["edges"],
                    "serialNumber": fts_serial,
                },
            }

        except Exception as e:
            print(f"❌ Fehler beim Generieren der FTS Navigation Message: {e}")
            return None

    def _get_module_serial(self, module: str) -> Optional[str]:
        """Gibt Serial Number für ein Modul zurück"""
        modules = self.module_config.get("modules", {})

        # Suche nach Modul-Namen in allen Modulen
        for _module_id, module_info in modules.items():
            if module_info.get("name") == module:
                return module_info.get("id")

        # Fallback: Direkte Suche nach ID
        module_info = modules.get(module, {})
        return module_info.get("id")

    def _generate_topic(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        """Generiert MQTT-Topic aus Template-Pattern"""
        topic_pattern = template.get("mqtt_topic_pattern", "")

        # Ersetze Variablen im Topic-Pattern
        topic = topic_pattern
        for param_name, param_value in parameters.items():
            placeholder = f"{{{param_name}}}"
            if placeholder in topic:
                topic = topic.replace(placeholder, str(param_value))

        return topic

    def _generate_payload(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generiert MQTT-Payload aus Template-Struktur"""
        template_structure = template.get("template_structure", {})
        variable_fields = template.get("variable_fields", {})

        payload = {}

        # Füge alle Felder aus der Template-Struktur hinzu
        for field_name, field_type in template_structure.items():
            if field_name in parameters:
                # Verwende bereitgestellten Parameter
                payload[field_name] = parameters[field_name]
            else:
                # Generiere Standard-Wert basierend auf Feld-Typ
                payload[field_name] = self._generate_default_value(field_name, field_type, variable_fields)

        # Füge Timestamp hinzu falls nicht vorhanden
        if "timestamp" not in payload:
            payload["timestamp"] = datetime.now().isoformat() + "Z"

        return payload

    def _generate_default_value(self, field_name: str, field_type: str, variable_fields: Dict[str, Any]) -> Any:
        """Generiert Standard-Werte für Felder"""
        field_info = variable_fields.get(field_name, {})

        if field_type == "<datetime>":
            return datetime.now().isoformat() + "Z"
        elif field_type == "<boolean>":
            return True
        elif field_type == "<number>":
            return 0
        elif field_type == "<string>":
            return ""
        elif field_type == "<array>":
            return []
        elif field_type == "<object>":
            return {}
        elif field_type == "<module_serial_number>":
            # Verwende erstes verfügbares Modul
            modules = self.get_available_modules()
            return modules[0] if modules else "UNKNOWN"
        elif field_type == "<ip_address>":
            # Verwende erste verfügbare IP
            modules = self.module_config.get("modules", {})
            for module_info in modules.values():
                if "ip_addresses" in module_info and module_info["ip_addresses"]:
                    return module_info["ip_addresses"][0]
            return "192.168.0.1"
        elif field_type == "<module_version>":
            return "1.0.0"
        elif field_type == "<module_state>":
            return "IDLE"
        elif field_type == "<module_status>":
            return "OK"
        elif field_type == "<module_command>":
            # Verwende erstes verfügbares Command
            field_values = field_info.get("values", [])
            return field_values[0] if field_values else "UNKNOWN"
        elif field_type == "<ccu_command>":
            return "start"
        elif field_type == "<order_state>":
            return "WAITING_FOR_ORDER"
        elif field_type == "<workpiece_type>":
            return "RED"
        elif field_type == "<dashboard_status>":
            return "running"
        elif field_type == "<order_id>":
            return f"ORDER_{uuid.uuid4().hex[:8].upper()}"
        elif field_type == "<command_parameters>":
            # Standard-Parameter für Module-Commands
            return {"orderUpdateId": 1, "subActionId": 1}
        else:
            # Fallback für unbekannte Typen
            return ""

    def generate_module_order_message(
        self, module_id: str, command: str, **additional_params
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generiert eine Modul-Order-Nachricht

        Args:
            module_id: Serial Number des Moduls
            command: Befehl für das Modul
            **additional_params: Zusätzliche Parameter

        Returns:
            Tuple von (topic, payload)
        """
        # Validiere Module und Command
        if module_id not in self.get_available_modules():
            raise ValueError(f"Modul '{module_id}' nicht verfügbar")

        available_commands = self.get_module_commands(module_id)
        if command not in available_commands:
            raise ValueError(
                f"Command '{command}' nicht verfügbar für Modul '{module_id}'. Verfügbar: {available_commands}"
            )

        # Generiere Nachricht
        parameters = {
            "module_id": module_id,
            "command": command,
            "order_id": f"ORDER_{uuid.uuid4().hex[:8].upper()}",
            **additional_params,
        }

        return self.generate_message("module/order", **parameters)

    def generate_module_connection_message(self, module_id: str, connected: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Generiert eine Modul-Connection-Nachricht

        Args:
            module_id: Serial Number des Moduls
            connected: Verbindungsstatus

        Returns:
            Tuple von (topic, payload)
        """
        if module_id not in self.get_available_modules():
            raise ValueError(f"Modul '{module_id}' nicht verfügbar")

        # Hole Module-Info für IP und Version
        modules = self.module_config.get("modules", {})
        module_info = modules.get(module_id, {})

        parameters = {
            "module_id": module_id,
            "connected": connected,
            "ip": module_info.get("ip_addresses", ["192.168.0.1"])[0],
            "serialNumber": module_id,
            "version": module_info.get("version", "1.0.0"),
        }

        return self.generate_message("module/connection", **parameters)

    def generate_module_state_message(
        self, module_id: str, state: str = "IDLE", status: str = "OK"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generiert eine Modul-State-Nachricht

        Args:
            module_id: Serial Number des Moduls
            state: Modul-Zustand
            status: Modul-Status

        Returns:
            Tuple von (topic, payload)
        """
        if module_id not in self.get_available_modules():
            raise ValueError(f"Modul '{module_id}' nicht verfügbar")

        parameters = {"module_id": module_id, "state": state, "status": status}

        return self.generate_message("module/state", **parameters)

    def generate_ccu_control_message(self, command: str, **parameters) -> Tuple[str, Dict[str, Any]]:
        """
        Generiert eine CCU-Control-Nachricht

        Args:
            command: CCU-Befehl
            **parameters: Zusätzliche Parameter

        Returns:
            Tuple von (topic, payload)
        """
        params = {"command": command, "parameters": parameters}

        return self.generate_message("ccu/control", **params)

    def generate_ccu_order_request_message(
        self,
        color: str,
        order_type: str,
        workpiece_id: str,
        ai_inspection: bool = False,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generiert eine CCU-Order-Request-Nachricht

        Args:
            color: Werkstück-Farbe (RED, WHITE, BLUE)
            order_type: Auftragstyp (STORAGE, PRODUCTION)
            workpiece_id: Werkstück-ID (NFC-ID)
            ai_inspection: AI-Qualitätsprüfung aktiviert

        Returns:
            Tuple von (topic, payload)
        """
        # Template verwenden
        template_name = "ccu/order/request"
        template = self.semantic_templates.get(template_name)

        if not template:
            # Fallback: Einfache CCU Order Request Message
            payload = {
                "type": color,
                "workpieceId": workpiece_id,
                "orderType": order_type,
                "timestamp": datetime.now().isoformat(),
            }

            if ai_inspection:
                payload["aiInspection"] = True

            return ("ccu/order/request", payload)

        # Template-basierte Generierung
        params = {"type": color, "workpieceId": workpiece_id, "orderType": order_type}

        if ai_inspection:
            params["aiInspection"] = True

        return self.generate_message(template_name, **params)

    def validate_message(self, template_name: str, payload: Dict[str, Any]) -> List[str]:
        """
        Validiert eine Nachricht gegen Template-Regeln

        Args:
            template_name: Name des Templates
            payload: Zu validierende Payload

        Returns:
            Liste von Validierungsfehlern
        """
        template = self.semantic_templates.get(template_name)
        if not template:
            return [f"Template '{template_name}' nicht gefunden"]

        # validation_rules = template.get("validation_rules", [])  # TODO: Implement validation
        errors = []

        # Implementiere Validierungslogik hier
        # (Vereinfachte Version - kann erweitert werden)

        return errors


# Singleton-Instanz
_message_generator = None


def get_omf_message_generator() -> MessageGenerator:
    """Gibt die Singleton-Instanz des MessageGenerator zurück"""
    global _message_generator
    if _message_generator is None:
        _message_generator = MessageGenerator()
    return _message_generator


def main():
    """Hauptfunktion für Tests"""
    print("\n🔧 Message Generator")
    print("=" * 50)

    generator = MessageGenerator()

    print(f"\n📋 Verfügbare Module: {generator.get_available_modules()}")
    print(f"📋 Verfügbare Templates: {generator.get_available_templates()}")

    # Test: Modul-Order-Nachricht
    try:
        module_id = "SVR3QA0022"  # HBW
        command = "PICK"

        print(f"\n🧪 Test: Modul-Order für {module_id} mit Command {command}")
        topic, payload = generator.generate_module_order_message(module_id, command, position="A1")

        print(f"📡 Topic: {topic}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")

    except Exception as e:
        print(f"❌ Fehler: {e}")

    # Test: Modul-Connection-Nachricht
    try:
        print(f"\n🧪 Test: Modul-Connection für {module_id}")
        topic, payload = generator.generate_module_connection_message(module_id, connected=True)

        print(f"📡 Topic: {topic}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")

    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    main()
