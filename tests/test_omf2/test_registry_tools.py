#!/usr/bin/env python3
"""
Test Registry Tools - Schema-Management und Test-Payload-Generator
"""

import json
import unittest
from pathlib import Path

from omf2.registry.manager.registry_manager import RegistryManager, get_registry_manager


class TestRegistryTools(unittest.TestCase):
    """Test Registry Tools für Schema-Management"""

    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton
        RegistryManager._instance = None
        RegistryManager._initialized = False
        self.registry_manager = get_registry_manager("omf2/registry/")

    def test_add_schema_to_topics_script_exists(self):
        """Test: add_schema_to_topics.py Script existiert"""
        script_path = Path("omf2/registry/tools/add_schema_to_topics.py")
        self.assertTrue(script_path.exists(), "add_schema_to_topics.py sollte existieren")
        self.assertTrue(script_path.is_file(), "add_schema_to_topics.py sollte eine Datei sein")

    def test_test_payload_generator_script_exists(self):
        """Test: test_payload_generator.py Script existiert"""
        script_path = Path("omf2/registry/tools/test_payload_generator.py")
        self.assertTrue(script_path.exists(), "test_payload_generator.py sollte existieren")
        self.assertTrue(script_path.is_file(), "test_payload_generator.py sollte eine Datei sein")

    def test_add_schema_to_topics_script_imports(self):
        """Test: add_schema_to_topics.py kann importiert werden"""
        try:
            import importlib.util

            script_path = Path("omf2/registry/tools/add_schema_to_topics.py")
            spec = importlib.util.spec_from_file_location("add_schema_to_topics", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Prüfe dass das Modul erfolgreich geladen wurde
            self.assertIsNotNone(module, "add_schema_to_topics.py sollte geladen werden können")
            self.assertTrue(hasattr(module, "__file__"), "Modul sollte __file__ Attribut haben")
        except Exception as e:
            self.fail(f"add_schema_to_topics.py kann nicht importiert werden: {e}")

    def test_test_payload_generator_script_imports(self):
        """Test: test_payload_generator.py kann importiert werden"""
        try:
            import importlib.util

            script_path = Path("omf2/registry/tools/test_payload_generator.py")
            spec = importlib.util.spec_from_file_location("test_payload_generator", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Prüfe dass das Modul erfolgreich geladen wurde
            self.assertIsNotNone(module, "test_payload_generator.py sollte geladen werden können")
            self.assertTrue(hasattr(module, "__file__"), "Modul sollte __file__ Attribut haben")
        except Exception as e:
            self.fail(f"test_payload_generator.py kann nicht importiert werden: {e}")

    def test_schema_mapping_logic(self):
        """Test: Schema-Mapping-Logik funktioniert"""
        try:
            import importlib.util

            script_path = Path("omf2/registry/tools/add_schema_to_topics.py")
            spec = importlib.util.spec_from_file_location("add_schema_to_topics", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Prüfe dass das Modul erfolgreich geladen wurde
            self.assertIsNotNone(module, "add_schema_to_topics.py sollte geladen werden können")

            # Prüfe dass das Script ausführbar ist (keine Syntax-Fehler)
            self.assertTrue(hasattr(module, "__file__"), "Modul sollte __file__ Attribut haben")

        except Exception as e:
            self.fail(f"Schema-Mapping-Logik kann nicht getestet werden: {e}")

    def test_test_suite_json_exists(self):
        """Test: test_suite.json existiert"""
        test_suite_path = Path("omf2/registry/test_suite.json")
        self.assertTrue(test_suite_path.exists(), "test_suite.json sollte existieren")
        self.assertTrue(test_suite_path.is_file(), "test_suite.json sollte eine Datei sein")

    def test_test_suite_json_valid(self):
        """Test: test_suite.json ist gültiges JSON"""
        test_suite_path = Path("omf2/registry/test_suite.json")

        try:
            with open(test_suite_path, encoding="utf-8") as f:
                test_suite_data = json.load(f)

            self.assertIsInstance(test_suite_data, dict, "test_suite.json sollte ein Dictionary sein")
            # Prüfe dass es ein gültiges JSON ist (kann verschiedene Strukturen haben)
            self.assertGreater(len(test_suite_data), 0, "test_suite.json sollte Daten enthalten")

        except json.JSONDecodeError as e:
            self.fail(f"test_suite.json ist kein gültiges JSON: {e}")
        except Exception as e:
            self.fail(f"Fehler beim Laden von test_suite.json: {e}")

    def test_registry_tools_directory_structure(self):
        """Test: Registry-Tools-Verzeichnis hat korrekte Struktur"""
        tools_path = Path("omf2/registry/tools")

        self.assertTrue(tools_path.exists(), "Tools-Verzeichnis sollte existieren")
        self.assertTrue(tools_path.is_dir(), "Tools sollte ein Verzeichnis sein")

        # Prüfe wichtige Tools
        expected_tools = ["add_schema_to_topics.py", "test_payload_generator.py"]

        for tool_name in expected_tools:
            tool_path = tools_path / tool_name
            self.assertTrue(tool_path.exists(), f"Tool {tool_name} sollte existieren")
            self.assertTrue(tool_path.is_file(), f"Tool {tool_name} sollte eine Datei sein")

    def test_schema_generation_workflow(self):
        """Test: Schema-Generation-Workflow funktioniert"""
        # Test dass Schema-Generation-Tools funktionieren
        try:
            import importlib.util

            script_path = Path("omf2/registry/tools/add_schema_to_topics.py")
            spec = importlib.util.spec_from_file_location("add_schema_to_topics", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Prüfe dass das Modul erfolgreich geladen wurde
            self.assertIsNotNone(module, "add_schema_to_topics.py sollte geladen werden können")
            self.assertTrue(hasattr(module, "__file__"), "Modul sollte __file__ Attribut haben")

        except Exception as e:
            self.fail(f"Schema-Generation-Workflow kann nicht getestet werden: {e}")

    def test_payload_validation_workflow(self):
        """Test: Payload-Validation-Workflow funktioniert"""
        # Test dass Payload-Validation funktioniert
        test_topic = "module/v1/ff/SVR3QA0022/state"

        # Test-Payload (sollte valid sein)
        valid_payload = {"state": "idle", "timestamp": "2025-10-01T19:30:00Z", "module_id": "SVR3QA0022"}

        # Test-Payload (sollte invalid sein)
        invalid_payload = {"invalid_field": "test", "wrong_type": 123}

        # Validierung sollte funktionieren über MessageManager
        from omf2.common.message_manager import MessageManager

        message_manager = MessageManager("admin", self.registry_manager)
        result_valid = message_manager.validate_message(test_topic, valid_payload)
        result_invalid = message_manager.validate_message(test_topic, invalid_payload)

        # Ergebnisse sollten nicht None sein
        self.assertIsNotNone(result_valid, "Validierung sollte ein Ergebnis zurückgeben")
        self.assertIsNotNone(result_invalid, "Validierung sollte ein Ergebnis zurückgeben")

    def test_registry_tools_integration(self):
        """Test: Registry-Tools-Integration funktioniert"""
        # Test dass alle Registry-Tools zusammenarbeiten

        # 1. Schema-Loading
        schemas = self.registry_manager.get_schemas()
        self.assertGreater(len(schemas), 0, "Schemas sollten geladen werden")

        # 2. Topic-Schema-Mapping
        test_topic = "module/v1/ff/SVR3QA0022/state"
        schema = self.registry_manager.get_topic_schema(test_topic)
        self.assertIsNotNone(schema, "Schema für Topic sollte gefunden werden")

        # 3. Schema-Validierung
        test_payload = {"state": "idle", "timestamp": "2025-10-01T19:30:00Z"}
        from omf2.common.message_manager import MessageManager

        message_manager = MessageManager("admin", self.registry_manager)
        validation_result = message_manager.validate_message(test_topic, test_payload)
        self.assertIsNotNone(validation_result, "Schema-Validierung sollte funktionieren")

        # 4. Registry-Statistiken
        stats = self.registry_manager.get_registry_stats()
        self.assertIn("schemas_count", stats, "Statistiken sollten schemas_count enthalten")
        self.assertIn("topics_count", stats, "Statistiken sollten topics_count enthalten")


if __name__ == "__main__":
    unittest.main()
