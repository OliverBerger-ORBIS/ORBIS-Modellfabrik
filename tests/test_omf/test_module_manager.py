#!/usr/bin/env python3
"""
Unit Tests for Module Manager
Tests the ModuleManager class functionality
"""

import os
import sys
import tempfile
import unittest

import yaml

# Add omf to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "omf"))

from omf.analysis_tools.module_manager import ModuleManager


class TestModuleManager(unittest.TestCase):
    """Test cases for ModuleManager class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary YAML config for testing
        self.test_config = {
            "metadata": {"version": "2.0", "description": "Test Module Configuration"},
            "modules": {
                "SVR3QA0022": {
                    "id": "SVR3QA0022",
                    "name": "HBW",
                    "name_lang_en": "High Bay Warehouse",
                    "name_lang_de": "Hochregallager",
                    "type": "Storage",
                    "ip_range": "192.168.0.80",
                    "description": "Hochregallager für Werkstück-Lagerung",
                    "commands": ["PICK", "DROP", "STORE"],
                    "sub_type": "HBW",
                },
                "SVR4H76449": {
                    "id": "SVR4H76449",
                    "name": "DRILL",
                    "name_lang_en": "Drill",
                    "name_lang_de": "Bohrer",
                    "type": "Processing",
                    "ip_range": "192.168.0.50",
                    "description": "Bohrmodul für Werkstück-Bearbeitung",
                    "commands": ["PICK", "DRILL", "DROP"],
                    "sub_type": "DRILL",
                },
                "SVR4H76530": {
                    "id": "SVR4H76530",
                    "name": "AIQS",
                    "name_lang_en": "Quality Inspection",
                    "name_lang_de": "Qualitätsprüfung",
                    "type": "Quality-Control",
                    "ip_range": "192.168.0.70",
                    "description": "KI-basierte Qualitätsprüfung",
                    "commands": ["PICK", "DROP", "CHECK_QUALITY"],
                    "sub_type": "AIQS",
                },
                "SVR4H73275": {
                    "id": "SVR4H73275",
                    "name": "DPS",
                    "name_lang_en": "Delivery and Pickup Station",
                    "name_lang_de": "Warenein- und Ausgang",
                    "type": "Input/Output",
                    "ip_range": "192.168.0.90",
                    "description": "Warenein- und Ausgangsstation",
                    "commands": ["PICK", "DROP", "INPUT_RGB", "RGB_NFC"],
                    "sub_type": "DPS",
                },
                "CHRG0": {
                    "id": "CHRG0",
                    "name": "CHRG",
                    "name_lang_en": "Charging Station",
                    "name_lang_de": "Ladestation",
                    "type": "Charging",
                    "ip_range": "192.168.0.65",
                    "description": "Ladestation für FTS-Akkus",
                    "commands": ["start_charging", "stop_charging", "get_status"],
                    "sub_type": "CHRG",
                },
            },
            "transports": {
                "5iO4": {
                    "id": "5iO4",
                    "name": "FTS",
                    "name_lang_en": "Automated Guided Vehicle",
                    "name_lang_de": "Fahrerloses Transportsystem",
                    "type": "Transport",
                    "ip_range": "192.168.0.100",
                    "description": "Fahrerloses Transportsystem",
                    "commands": ["NAVIGATE", "PICK", "DROP"],
                    "sub_type": "FTS",
                }
            },
            "module_types": [
                "Processing",
                "Quality-Control",
                "Storage",
                "Input/Output",
                "Charging",
                "Transport",
            ],
            "commands": [
                "PICK",
                "DROP",
                "STORE",
                "MILL",
                "DRILL",
                "CHECK_QUALITY",
                "NAVIGATE",
            ],
            "availability_status": ["READY", "BUSY", "ERROR", "OFFLINE"],
            "template_placeholders": {
                "module_id": "<moduleId>",
                "module_name": "<moduleName>",
                "module_type": "<moduleType>",
                "ip_range": "<ipRange>",
            },
            "mqtt_paths": [["moduleId"], ["id"], ["source"], ["target"]],
        }

        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
        yaml.dump(self.test_config, self.temp_file)
        self.temp_file.close()

        # Initialize manager with test config
        self.manager = ModuleManager(self.temp_file.name)

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_init_with_valid_config(self):
        """Test initialization with valid YAML config"""
        self.assertIsNotNone(self.manager.config)
        self.assertEqual(len(self.manager.config["modules"]), 5)
        self.assertEqual(len(self.manager.config["transports"]), 1)

    def test_init_with_invalid_path(self):
        """Test initialization with invalid config path"""
        with self.assertRaises(ValueError):
            ModuleManager("/nonexistent/path/config.yml")

    def test_get_module_info(self):
        """Test getting complete module information"""
        # Test valid module ID
        info = self.manager.get_module_info("SVR3QA0022")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "HBW")
        self.assertEqual(info["type"], "Storage")
        self.assertEqual(info["ip_range"], "192.168.0.80")

        # Test valid transport ID
        info = self.manager.get_module_info("5iO4")
        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "FTS")
        self.assertEqual(info["type"], "Transport")

        # Test invalid module ID
        info = self.manager.get_module_info("invalid_id")
        self.assertIsNone(info)

    def test_get_module_name(self):
        """Test getting module name for module ID"""
        # Test valid module ID
        name = self.manager.get_module_name("SVR3QA0022")
        self.assertEqual(name, "HBW")

        # Test valid transport ID
        name = self.manager.get_module_name("5iO4")
        self.assertEqual(name, "FTS")

        # Test invalid module ID
        name = self.manager.get_module_name("invalid_id")
        self.assertEqual(name, "invalid_id")

    def test_get_module_name_long_en(self):
        """Test getting English long name for module ID"""
        name = self.manager.get_module_name_long_en("SVR3QA0022")
        self.assertEqual(name, "High Bay Warehouse")

        name = self.manager.get_module_name_long_en("invalid_id")
        self.assertEqual(name, "invalid_id")

    def test_get_module_name_long_de(self):
        """Test getting German long name for module ID"""
        name = self.manager.get_module_name_long_de("SVR3QA0022")
        self.assertEqual(name, "Hochregallager")

        name = self.manager.get_module_name_long_de("invalid_id")
        self.assertEqual(name, "invalid_id")

    def test_get_module_type(self):
        """Test getting module type for module ID"""
        module_type = self.manager.get_module_type("SVR3QA0022")
        self.assertEqual(module_type, "Storage")

        module_type = self.manager.get_module_type("SVR4H76449")
        self.assertEqual(module_type, "Processing")

        module_type = self.manager.get_module_type("SVR4H76530")
        self.assertEqual(module_type, "Quality-Control")

        module_type = self.manager.get_module_type("5iO4")
        self.assertEqual(module_type, "Transport")

        module_type = self.manager.get_module_type("invalid_id")
        self.assertEqual(module_type, "Unknown")

    def test_get_module_ip_range(self):
        """Test getting IP range for module ID"""
        ip_range = self.manager.get_module_ip_range("SVR3QA0022")
        self.assertEqual(ip_range, "192.168.0.80")

        ip_range = self.manager.get_module_ip_range("invalid_id")
        self.assertEqual(ip_range, "Unknown")

    def test_get_module_description(self):
        """Test getting description for module ID"""
        description = self.manager.get_module_description("SVR3QA0022")
        self.assertEqual(description, "Hochregallager für Werkstück-Lagerung")

        description = self.manager.get_module_description("invalid_id")
        self.assertEqual(description, "")

    def test_get_module_commands(self):
        """Test getting available commands for module ID"""
        commands = self.manager.get_module_commands("SVR3QA0022")
        expected_commands = ["PICK", "DROP", "STORE"]
        self.assertEqual(commands, expected_commands)

        commands = self.manager.get_module_commands("invalid_id")
        self.assertEqual(commands, [])

    def test_get_module_sub_type(self):
        """Test getting sub type for module ID"""
        sub_type = self.manager.get_module_sub_type("SVR3QA0022")
        self.assertEqual(sub_type, "HBW")

        sub_type = self.manager.get_module_sub_type("invalid_id")
        self.assertEqual(sub_type, "Unknown")

    def test_get_all_modules(self):
        """Test getting all modules"""
        all_modules = self.manager.get_all_modules()
        self.assertEqual(len(all_modules), 6)  # 5 modules + 1 transport

        expected_ids = [
            "SVR3QA0022",
            "SVR4H76449",
            "SVR4H76530",
            "SVR4H73275",
            "CHRG0",
            "5iO4",
        ]
        for module_id in expected_ids:
            self.assertIn(module_id, all_modules)

    def test_get_modules_by_type(self):
        """Test getting modules by type"""
        storage_modules = self.manager.get_modules_by_type("Storage")
        self.assertEqual(len(storage_modules), 1)
        self.assertIn("SVR3QA0022", storage_modules)

        processing_modules = self.manager.get_modules_by_type("Processing")
        self.assertEqual(len(processing_modules), 1)
        self.assertIn("SVR4H76449", processing_modules)

        quality_modules = self.manager.get_modules_by_type("Quality-Control")
        self.assertEqual(len(quality_modules), 1)
        self.assertIn("SVR4H76530", quality_modules)

        transport_modules = self.manager.get_modules_by_type("Transport")
        self.assertEqual(len(transport_modules), 1)
        self.assertIn("5iO4", transport_modules)

        input_output_modules = self.manager.get_modules_by_type("Input/Output")
        self.assertEqual(len(input_output_modules), 1)
        self.assertIn("SVR4H73275", input_output_modules)

        charging_modules = self.manager.get_modules_by_type("Charging")
        self.assertEqual(len(charging_modules), 1)
        self.assertIn("CHRG0", charging_modules)

    def test_get_all_module_ids(self):
        """Test getting all module IDs"""
        module_ids = self.manager.get_all_module_ids()
        self.assertEqual(len(module_ids), 6)

        expected_ids = [
            "SVR3QA0022",
            "SVR4H76449",
            "SVR4H76530",
            "SVR4H73275",
            "CHRG0",
            "5iO4",
        ]
        for module_id in expected_ids:
            self.assertIn(module_id, module_ids)

    def test_get_all_module_names(self):
        """Test getting all module names"""
        module_names = self.manager.get_all_module_names()
        self.assertEqual(len(module_names), 6)

        expected_names = ["HBW", "DRILL", "AIQS", "DPS", "CHRG", "FTS"]
        for name in expected_names:
            self.assertIn(name, module_names)

    def test_is_module_id(self):
        """Test checking if value is a known module ID"""
        self.assertTrue(self.manager.is_module_id("SVR3QA0022"))
        self.assertTrue(self.manager.is_module_id("5iO4"))
        self.assertFalse(self.manager.is_module_id("invalid_id"))

    def test_is_module_name(self):
        """Test checking if value is a known module name"""
        self.assertTrue(self.manager.is_module_name("HBW"))
        self.assertTrue(self.manager.is_module_name("FTS"))
        self.assertFalse(self.manager.is_module_name("INVALID"))

    def test_validate_module_id(self):
        """Test module ID validation"""
        self.assertTrue(self.manager.validate_module_id("SVR3QA0022"))
        self.assertFalse(self.manager.validate_module_id("invalid_id"))

    def test_get_module_id_by_name(self):
        """Test getting module ID for module name"""
        module_id = self.manager.get_module_id_by_name("HBW")
        self.assertEqual(module_id, "SVR3QA0022")

        module_id = self.manager.get_module_id_by_name("FTS")
        self.assertEqual(module_id, "5iO4")

        module_id = self.manager.get_module_id_by_name("INVALID")
        self.assertIsNone(module_id)

    def test_format_module_display_name(self):
        """Test formatting module name for display"""
        # Test with ID included
        display_name = self.manager.format_module_display_name("SVR3QA0022", include_id=True)
        self.assertEqual(display_name, "HBW (SVR3QA0022)")

        # Test without ID
        display_name = self.manager.format_module_display_name("SVR3QA0022", include_id=False)
        self.assertEqual(display_name, "HBW")

        # Test invalid ID
        display_name = self.manager.format_module_display_name("invalid_id", include_id=True)
        self.assertEqual(display_name, "invalid_id")

    def test_get_module_types(self):
        """Test getting all available module types"""
        types = self.manager.get_module_types()
        expected_types = [
            "Processing",
            "Quality-Control",
            "Storage",
            "Input/Output",
            "Charging",
            "Transport",
        ]
        self.assertEqual(types, expected_types)

    def test_get_commands(self):
        """Test getting all available commands"""
        commands = self.manager.get_commands()
        expected_commands = [
            "PICK",
            "DROP",
            "STORE",
            "MILL",
            "DRILL",
            "CHECK_QUALITY",
            "NAVIGATE",
        ]
        self.assertEqual(commands, expected_commands)

    def test_get_availability_status(self):
        """Test getting all available availability status"""
        status = self.manager.get_availability_status()
        expected_status = ["READY", "BUSY", "ERROR", "OFFLINE"]
        self.assertEqual(status, expected_status)

    def test_get_template_placeholders(self):
        """Test getting template placeholders"""
        placeholders = self.manager.get_template_placeholders()
        self.assertEqual(placeholders["module_id"], "<moduleId>")
        self.assertEqual(placeholders["module_name"], "<moduleName>")
        self.assertEqual(placeholders["module_type"], "<moduleType>")
        self.assertEqual(placeholders["ip_range"], "<ipRange>")

    def test_get_mqtt_paths(self):
        """Test getting MQTT paths"""
        paths = self.manager.get_mqtt_paths()
        self.assertEqual(len(paths), 4)
        self.assertIn(["moduleId"], paths)
        self.assertIn(["id"], paths)
        self.assertIn(["source"], paths)
        self.assertIn(["target"], paths)

    def test_get_statistics(self):
        """Test getting module statistics"""
        stats = self.manager.get_statistics()

        self.assertEqual(stats["total_modules"], 6)
        self.assertEqual(stats["type_counts"]["Storage"], 1)
        self.assertEqual(stats["type_counts"]["Processing"], 1)
        self.assertEqual(stats["type_counts"]["Quality-Control"], 1)
        self.assertEqual(stats["type_counts"]["Input/Output"], 1)
        self.assertEqual(stats["type_counts"]["Charging"], 1)
        self.assertEqual(stats["type_counts"]["Transport"], 1)

        self.assertIn("Storage", stats["module_types"])
        self.assertIn("Processing", stats["module_types"])
        self.assertIn("Quality-Control", stats["module_types"])
        self.assertIn("Input/Output", stats["module_types"])
        self.assertIn("Charging", stats["module_types"])
        self.assertIn("Transport", stats["module_types"])

        self.assertIn("PICK", stats["commands"])
        self.assertIn("DROP", stats["commands"])
        self.assertIn("STORE", stats["commands"])

    def test_reload_config(self):
        """Test reloading configuration"""
        # Modify config
        new_config = self.test_config.copy()
        new_config["modules"]["TEST123"] = {
            "id": "TEST123",
            "name": "TEST",
            "name_lang_en": "Test Module",
            "name_lang_de": "Test Modul",
            "type": "Storage",
            "ip_range": "192.168.0.200",
            "description": "Test Module",
            "commands": ["TEST"],
            "sub_type": "TEST",
        }

        # Write new config
        with open(self.temp_file.name, "w") as f:
            yaml.dump(new_config, f)

        # Reload and test
        success = self.manager.reload_config()
        self.assertTrue(success)

        # Check if new module is available
        self.assertTrue(self.manager.is_module_id("TEST123"))
        self.assertEqual(self.manager.get_module_name("TEST123"), "TEST")


class TestModuleManagerBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility functions"""

    def setUp(self):
        """Set up test fixtures"""
        # Create minimal test config
        self.test_config = {
            "modules": {
                "SVR3QA0022": {
                    "id": "SVR3QA0022",
                    "name": "HBW",
                    "name_lang_en": "High Bay Warehouse",
                    "name_lang_de": "Hochregallager",
                    "type": "Storage",
                    "ip_range": "192.168.0.80",
                    "description": "Hochregallager",
                    "commands": ["PICK", "DROP", "STORE"],
                    "sub_type": "HBW",
                }
            }
        }

        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
        yaml.dump(self.test_config, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions"""
        from omf.tools.module_manager import (
            get_module_info,
            get_module_name,
            get_module_type,
            validate_module_id,
        )

        # Test backward compatibility functions
        module_info = get_module_info("SVR3QA0022")
        self.assertIsNotNone(module_info)
        self.assertEqual(module_info["name"], "HBW")

        module_name = get_module_name("SVR3QA0022")
        self.assertEqual(module_name, "HBW")

        module_type = get_module_type("SVR3QA0022")
        self.assertEqual(module_type, "Storage")

        self.assertTrue(validate_module_id("SVR3QA0022"))
        self.assertFalse(validate_module_id("invalid_id"))


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
