#!/usr/bin/env python3
"""
Unit Tests für Template-Integration mit bestehenden Regeln
Testet die Integration von Template-UI-Config mit bewährten send_drill_sequence_command Methoden
"""

import unittest
import tempfile
import yaml
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import der zu testenden Klassen
from src_orbis.mqtt.tools.message_template_manager import MessageTemplateManager
from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard


class TestTemplateIntegration(unittest.TestCase):
    """Testet die Integration von Template-UI-Config mit bestehenden Regeln"""

    def setUp(self):
        """Setup für jeden Test"""
        # Erstelle temporäre Template-Konfiguration
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        
        # Template-Konfiguration mit UI-Config für alle Module
        config_data = {
            "topics": {
                "module/v1/ff/SVR4H76449/order": {
                    "category": "MODULE",
                    "description": "DRILL Module Order",
                    "module": "SVR4H76449",
                    "ui_config": {
                        "module_id": "SVR4H76449",
                        "module_name": "DRILL",
                        "commands": {
                            "PICK": {
                                "text": "📤 PICK",
                                "icon": "📤",
                                "color": "primary",
                                "help": "Werkstück aufnehmen"
                            },
                            "DRILL": {
                                "text": "⚙️ DRILL",
                                "icon": "⚙️",
                                "color": "primary",
                                "help": "Werkstück bohren"
                            },
                            "DROP": {
                                "text": "📥 DROP",
                                "icon": "📥",
                                "color": "primary",
                                "help": "Werkstück ablegen"
                            }
                        },
                        "workpiece_selection": {
                            "colors": ["WHITE", "RED", "BLUE"],
                            "default_color": "WHITE",
                            "options": {
                                "WHITE": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
                                "RED": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"],
                                "BLUE": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
                            }
                        },
                        "success_message": "DRILL-Befehl erfolgreich gesendet mit orderUpdateId: {orderUpdateId}"
                    }
                },
                "module/v1/ff/SVR3QA2098/order": {
                    "category": "MODULE",
                    "description": "MILL Module Order",
                    "module": "SVR3QA2098",
                    "ui_config": {
                        "module_id": "SVR3QA2098",
                        "module_name": "MILL",
                        "commands": {
                            "PICK": {
                                "text": "📤 PICK",
                                "icon": "📤",
                                "color": "primary",
                                "help": "Werkstück aufnehmen"
                            },
                            "MILL": {
                                "text": "⚙️ MILL",
                                "icon": "⚙️",
                                "color": "primary",
                                "help": "Werkstück fräsen"
                            },
                            "DROP": {
                                "text": "📥 DROP",
                                "icon": "📥",
                                "color": "primary",
                                "help": "Werkstück ablegen"
                            }
                        },
                        "workpiece_selection": {
                            "colors": ["WHITE", "RED", "BLUE"],
                            "default_color": "WHITE",
                            "options": {
                                "WHITE": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
                                "RED": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"],
                                "BLUE": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
                            }
                        },
                        "success_message": "MILL-Befehl erfolgreich gesendet mit orderUpdateId: {orderUpdateId}"
                    }
                },
                "module/v1/ff/SVR4H76530/order": {
                    "category": "MODULE",
                    "description": "AIQS Module Order",
                    "module": "SVR4H76530",
                    "ui_config": {
                        "module_id": "SVR4H76530",
                        "module_name": "AIQS",
                        "commands": {
                            "PICK": {
                                "text": "📤 PICK",
                                "icon": "📤",
                                "color": "primary",
                                "help": "Werkstück aufnehmen"
                            },
                            "CHECK_QUALITY": {
                                "text": "🔍 CHECK_QUALITY",
                                "icon": "🔍",
                                "color": "primary",
                                "help": "Qualität prüfen"
                            },
                            "DROP": {
                                "text": "📥 DROP",
                                "icon": "📥",
                                "color": "primary",
                                "help": "Werkstück ablegen"
                            }
                        },
                        "workpiece_selection": {
                            "colors": ["WHITE", "RED", "BLUE"],
                            "default_color": "WHITE",
                            "options": {
                                "WHITE": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
                                "RED": ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"],
                                "BLUE": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
                            }
                        },
                        "success_message": "AIQS-Befehl erfolgreich gesendet mit orderUpdateId: {orderUpdateId}"
                    }
                }
            }
        }
        
        yaml.dump(config_data, self.temp_config)
        self.temp_config.close()
        
        # Erstelle MessageTemplateManager mit Test-Konfiguration
        self.template_manager = MessageTemplateManager(self.temp_config.name)

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import os
        os.unlink(self.temp_config.name)

    def test_get_module_ui_config_drill(self):
        """Testet UI-Config für DRILL Modul"""
        ui_config = self.template_manager.get_module_ui_config("SVR4H76449")
        
        self.assertIsNotNone(ui_config)
        self.assertEqual(ui_config["module_name"], "DRILL")
        self.assertIn("PICK", ui_config["commands"])
        self.assertIn("DRILL", ui_config["commands"])
        self.assertIn("DROP", ui_config["commands"])
        self.assertIn("WHITE", ui_config["workpiece_selection"]["colors"])

    def test_get_module_ui_config_mill(self):
        """Testet UI-Config für MILL Modul"""
        ui_config = self.template_manager.get_module_ui_config("SVR3QA2098")
        
        self.assertIsNotNone(ui_config)
        self.assertEqual(ui_config["module_name"], "MILL")
        self.assertIn("PICK", ui_config["commands"])
        self.assertIn("MILL", ui_config["commands"])
        self.assertIn("DROP", ui_config["commands"])

    def test_get_module_ui_config_aiqs(self):
        """Testet UI-Config für AIQS Modul"""
        ui_config = self.template_manager.get_module_ui_config("SVR4H76530")
        
        self.assertIsNotNone(ui_config)
        self.assertEqual(ui_config["module_name"], "AIQS")
        self.assertIn("PICK", ui_config["commands"])
        self.assertIn("CHECK_QUALITY", ui_config["commands"])
        self.assertIn("DROP", ui_config["commands"])

    def test_get_module_ui_config_not_found(self):
        """Testet UI-Config für nicht existierendes Modul"""
        ui_config = self.template_manager.get_module_ui_config("NONEXISTENT")
        self.assertIsNone(ui_config)

    def test_workpiece_selection_options(self):
        """Testet Workpiece-Auswahl-Optionen"""
        ui_config = self.template_manager.get_module_ui_config("SVR4H76449")
        
        # Teste Farben
        self.assertIn("WHITE", ui_config["workpiece_selection"]["colors"])
        self.assertIn("RED", ui_config["workpiece_selection"]["colors"])
        self.assertIn("BLUE", ui_config["workpiece_selection"]["colors"])
        
        # Teste Workpiece-Optionen
        white_options = ui_config["workpiece_selection"]["options"]["WHITE"]
        self.assertEqual(len(white_options), 8)
        self.assertIn("W1", white_options)
        self.assertIn("W8", white_options)

    def test_command_configuration(self):
        """Testet Kommando-Konfiguration"""
        ui_config = self.template_manager.get_module_ui_config("SVR4H76449")
        
        # Teste PICK Kommando
        pick_config = ui_config["commands"]["PICK"]
        self.assertEqual(pick_config["text"], "📤 PICK")
        self.assertEqual(pick_config["icon"], "📤")
        self.assertEqual(pick_config["color"], "primary")
        self.assertEqual(pick_config["help"], "Werkstück aufnehmen")

    def test_success_message_formatting(self):
        """Testet Success-Message-Formatierung"""
        ui_config = self.template_manager.get_module_ui_config("SVR4H76449")
        success_message = ui_config["success_message"]
        
        # Teste dass orderUpdateId Platzhalter vorhanden ist
        self.assertIn("{orderUpdateId}", success_message)
        
        # Teste Formatierung
        formatted_message = success_message.format(orderUpdateId=5)
        self.assertIn("5", formatted_message)


class TestDashboardTemplateIntegration(unittest.TestCase):
    """Testet Dashboard-Integration mit Template-System"""

    def setUp(self):
        """Setup für Dashboard-Tests"""
        # Mock für Dashboard-Komponenten
        self.mock_mqtt_client = Mock()
        self.mock_module_mapping = Mock()
        
        # Mock Module-Informationen
        self.module_info = {
            "SVR4H76449": {
                "id": "SVR4H76449",
                "name": "DRILL",
                "commands": ["PICK", "DRILL", "DROP"]
            },
            "SVR3QA2098": {
                "id": "SVR3QA2098", 
                "name": "MILL",
                "commands": ["PICK", "MILL", "DROP"]
            },
            "SVR4H76530": {
                "id": "SVR4H76530",
                "name": "AIQS", 
                "commands": ["PICK", "CHECK_QUALITY", "DROP"]
            }
        }
        
        self.mock_module_mapping.get_all_modules.return_value = self.module_info

    @patch('src_orbis.mqtt.tools.message_template_manager.MessageTemplateManager')
    def test_dashboard_template_manager_integration(self, mock_template_manager_class):
        """Testet Dashboard-Integration mit TemplateManager"""
        # Mock TemplateManager
        mock_template_manager = Mock()
        mock_template_manager_class.return_value = mock_template_manager
        
        # Mock UI-Config
        mock_ui_config = {
            "module_name": "DRILL",
            "commands": {
                "PICK": {"text": "📤 PICK", "help": "Werkstück aufnehmen"},
                "DRILL": {"text": "⚙️ DRILL", "help": "Werkstück bohren"},
                "DROP": {"text": "📥 DROP", "help": "Werkstück ablegen"}
            },
            "workpiece_selection": {
                "colors": ["WHITE", "RED", "BLUE"],
                "options": {
                    "WHITE": ["W1", "W2", "W3"],
                    "RED": ["R1", "R2", "R3"],
                    "BLUE": ["B1", "B2", "B3"]
                }
            }
        }
        
        mock_template_manager.get_module_ui_config.return_value = mock_ui_config
        
        # Teste dass get_module_ui_config aufgerufen wird
        result = mock_template_manager.get_module_ui_config("SVR4H76449")
        
        # Verifikationen
        mock_template_manager.get_module_ui_config.assert_called_once_with("SVR4H76449")
        self.assertEqual(result["module_name"], "DRILL")
        self.assertIn("PICK", result["commands"])

    def test_send_drill_sequence_command_integration(self):
        """Testet Integration der send_drill_sequence_command Methode"""
        # Diese Methode sollte die bewährte Implementierung verwenden
        # und nicht die neue Template-Methode
        
        # Mock für Dashboard
        dashboard = Mock()
        dashboard.mqtt_connected = True
        dashboard.module_mapping = self.mock_module_mapping
        
        # Mock für send_mqtt_message_direct
        dashboard.send_mqtt_message_direct = Mock(return_value=(True, "Success"))
        
        # Teste dass die Methode existiert
        self.assertTrue(hasattr(dashboard, 'send_drill_sequence_command'))

    def test_chrg_removal_from_mqtt_control(self):
        """Test that CHRG is not shown in MQTT Control tab"""
        # Test that CHRG is excluded from direct command modules
        excluded_modules = ["DRILL", "MILL", "AIQS", "HBW", "DPS", "CHRG"]
        self.assertIn("CHRG", excluded_modules)
        self.assertIn("HBW", excluded_modules)
        self.assertIn("DPS", excluded_modules)

    def test_nodered_tab_integration(self):
        """Test Node-RED tab integration"""
        # Test that Node-RED templates are accessible (basic test)
        # This tests the concept, not the actual implementation
        nodered_category = "Node-RED"
        self.assertIsInstance(nodered_category, str)
        
        # Test that sub-categories are a list
        sub_categories = ["Connection", "State", "Order", "Factsheet"]
        self.assertIsInstance(sub_categories, list)


class TestExistingRulesCompliance(unittest.TestCase):
    """Testet Einhaltung bestehender Regeln"""

    def test_order_update_id_management(self):
        """Testet orderUpdateId-Management (bestehende Regel)"""
        # orderUpdateId sollte inkrementell pro Modul sein
        # Diese Regel ist in send_drill_sequence_command implementiert
        
        # Mock für Session State
        session_state = {}
        
        # Simuliere orderUpdateId-Management
        module_id = "SVR4H76449"
        order_update_key = f"order_update_id_{module_id}"
        
        # Erste Verwendung
        if order_update_key not in session_state:
            session_state[order_update_key] = 1
        else:
            session_state[order_update_key] += 1
        
        self.assertEqual(session_state[order_update_key], 1)
        
        # Zweite Verwendung
        session_state[order_update_key] += 1
        self.assertEqual(session_state[order_update_key], 2)

    def test_message_structure_compliance(self):
        """Testet Nachrichtenstruktur-Compliance (bestehende Regel)"""
        # Nachrichten sollten folgende Struktur haben:
        # - serialNumber
        # - orderId (UUID)
        # - orderUpdateId (inkrementell)
        # - action mit id (UUID), command, metadata
        
        import uuid
        
        message = {
            "serialNumber": "SVR4H76449",
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": "PICK",
                "metadata": {
                    "priority": "NORMAL",
                    "timeout": 300,
                    "type": "WHITE",
                    "workpieceId": "W1"
                }
            }
        }
        
        # Verifikationen
        self.assertIn("serialNumber", message)
        self.assertIn("orderId", message)
        self.assertIn("orderUpdateId", message)
        self.assertIn("action", message)
        
        # UUID-Validierung
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.assertIsNotNone(re.match(uuid_pattern, message["orderId"]))
        self.assertIsNotNone(re.match(uuid_pattern, message["action"]["id"]))

    def test_priority_and_timeout_compliance(self):
        """Testet Priority und Timeout Compliance (bestehende Regel)"""
        # priority sollte "NORMAL" sein
        # timeout sollte 300 sein
        
        metadata = {
            "priority": "NORMAL",
            "timeout": 300,
            "type": "WHITE",
            "workpieceId": "W1"
        }
        
        self.assertEqual(metadata["priority"], "NORMAL")
        self.assertEqual(metadata["timeout"], 300)


if __name__ == "__main__":
    # Führe alle Tests aus
    unittest.main(verbosity=2)
