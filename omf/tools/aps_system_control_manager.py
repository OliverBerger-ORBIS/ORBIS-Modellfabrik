#!/usr/bin/env python3
"""
APS System Control Manager
Verwaltet System Control Commands für APS basierend auf Registry-Templates
Version: 1.0.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.tools.registry_manager import get_registry


class APSSystemControlManager:
    """Verwaltet APS System Control Commands"""

    def __init__(self):
        self.logger = get_logger("omf.tools.aps_system_control_manager")
        self.registry = get_registry()

        # System Control Commands basierend auf Registry-Templates
        self.system_commands = self._load_system_commands()

        self.logger.info("APSSystemControlManager initialisiert")

    def _load_system_commands(self) -> Dict[str, Dict[str, Any]]:
        """Lädt System Control Commands aus Registry"""
        try:
            # System Control Commands basierend auf Registry-Templates
            commands = {
                "reset": {
                    "topic": "ccu/set/reset",
                    "description": "Factory Reset",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "charge": {
                    "topic": "ccu/set/charge",
                    "description": "FTS Charge",
                    "parameters": {"charge": True},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "layout": {
                    "topic": "ccu/set/layout",
                    "description": "Layout Management",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "flows": {
                    "topic": "ccu/set/flows",
                    "description": "Flow Control",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "calibration": {
                    "topic": "ccu/set/calibration",
                    "description": "System Calibration",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "park": {
                    "topic": "ccu/set/park",
                    "description": "Park Factory",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "delete_module": {
                    "topic": "ccu/set/delete-module",
                    "description": "Delete Module",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "module_duration": {
                    "topic": "ccu/set/module-duration",
                    "description": "Set Module Duration",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "default_layout": {
                    "topic": "ccu/set/default_layout",
                    "description": "Set Default Layout",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
                "config": {
                    "topic": "ccu/set/config",
                    "description": "System Configuration",
                    "parameters": {},
                    "qos": 2,
                    "retain": False,
                    "direction": "outbound",
                },
            }

            return commands

        except Exception as e:
            self.logger.warning(f"Registry-Konfiguration nicht verfügbar: {e}")
            return {}

    def send_system_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sendet System Control Command"""
        try:
            if command not in self.system_commands:
                self.logger.error(f"❌ Unbekanntes System Command: {command}")
                return {}

            cmd_info = self.system_commands[command]
            if parameters is None:
                parameters = cmd_info["parameters"]

            command_data = {
                "command": command,
                "topic": cmd_info["topic"],
                "parameters": parameters,
                "timestamp": datetime.now().isoformat(),
                "qos": cmd_info["qos"],
                "retain": cmd_info["retain"],
            }

            self.logger.info(f"🎮 System Command gesendet: {command}")
            return command_data

        except Exception as e:
            self.logger.error(f"❌ System Command Erstellung fehlgeschlagen: {e}")
            return {}

    def get_available_commands(self) -> List[str]:
        """Gibt verfügbare System Commands zurück"""
        return list(self.system_commands.keys())

    def get_command_info(self, command: str) -> Optional[Dict[str, Any]]:
        """Gibt Command-Informationen zurück"""
        return self.system_commands.get(command)

    def reset_factory(self) -> Dict[str, Any]:
        """Factory Reset Command"""
        return self.send_system_command("reset")

    def charge_fts(self) -> Dict[str, Any]:
        """FTS Charge Command"""
        return self.send_system_command("charge")

    def park_factory(self) -> Dict[str, Any]:
        """Park Factory Command"""
        return self.send_system_command("park")

    def calibrate_system(self) -> Dict[str, Any]:
        """System Calibration Command"""
        return self.send_system_command("calibration")

    def set_layout(self, layout_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Layout Management Command"""
        parameters = layout_data or {}
        return self.send_system_command("layout", parameters)

    def set_flows(self, flow_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Flow Control Command"""
        parameters = flow_data or {}
        return self.send_system_command("flows", parameters)

    def delete_module(self, module_id: str) -> Dict[str, Any]:
        """Delete Module Command"""
        parameters = {"moduleId": module_id}
        return self.send_system_command("delete_module", parameters)

    def set_module_duration(self, module_id: str, duration: int) -> Dict[str, Any]:
        """Set Module Duration Command"""
        parameters = {"moduleId": module_id, "duration": duration}
        return self.send_system_command("module_duration", parameters)

    def set_default_layout(self, layout_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Set Default Layout Command"""
        parameters = layout_data or {}
        return self.send_system_command("default_layout", parameters)

    def set_system_config(self, config_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """System Configuration Command"""
        parameters = config_data or {}
        return self.send_system_command("config", parameters)

    def get_command_topics(self) -> List[str]:
        """Gibt alle Command Topics zurück"""
        return [cmd["topic"] for cmd in self.system_commands.values()]

    def get_commands_by_category(self, category: str = None) -> Dict[str, Dict[str, Any]]:
        """Gibt Commands nach Kategorie zurück"""
        if not category:
            return self.system_commands.copy()

        # Kategorien basierend auf Topic-Struktur
        category_mapping = {
            "factory": ["reset", "park"],
            "transport": ["charge"],
            "layout": ["layout", "default_layout"],
            "system": ["flows", "calibration", "config"],
            "module": ["delete_module", "module_duration"],
        }

        if category not in category_mapping:
            return {}

        return {cmd: info for cmd, info in self.system_commands.items() if cmd in category_mapping[category]}

    def validate_command_parameters(self, command: str, parameters: Dict[str, Any]) -> List[str]:
        """Validiert Command-Parameter"""
        errors = []

        if command not in self.system_commands:
            errors.append(f"Unbekanntes Command: {command}")
            return errors

        cmd_info = self.system_commands[command]
        expected_params = cmd_info.get("parameters", {})

        # Parameter-Validierung (vereinfacht)
        for param, expected_value in expected_params.items():
            if param not in parameters:
                errors.append(f"Erforderlicher Parameter fehlt: {param}")
            elif not isinstance(parameters[param], type(expected_value)):
                errors.append(f"Falscher Parametertyp für {param}: erwartet {type(expected_value)}")

        return errors

    def get_command_statistics(self) -> Dict[str, Any]:
        """Gibt Command-Statistiken zurück"""
        total_commands = len(self.system_commands)

        # Kategorien zählen
        categories = {}
        for cmd_info in self.system_commands.values():
            topic = cmd_info["topic"]
            if topic.startswith("ccu/set/"):
                category = topic.split("/")[2]
                categories[category] = categories.get(category, 0) + 1

        return {"total_commands": total_commands, "categories": categories, "last_updated": datetime.now().isoformat()}
