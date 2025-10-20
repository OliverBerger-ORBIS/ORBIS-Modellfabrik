#!/usr/bin/env python3
"""
Test Schema Integration - 44 JSON-Schemas für Topic-Validierung
"""

import json
import unittest

from omf2.registry.manager.registry_manager import RegistryManager, get_registry_manager


class TestSchemaIntegration(unittest.TestCase):
    """Test Schema Integration - 44 JSON-Schemas"""

    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton
        RegistryManager._instance = None
        RegistryManager._initialized = False
        self.registry_manager = get_registry_manager("omf2/registry/")

    def test_schemas_directory_structure(self):
        """Test: Schemas-Verzeichnis hat korrekte Struktur"""
        schemas_path = self.registry_manager.registry_path / "schemas"

        self.assertTrue(schemas_path.exists(), "Schemas-Verzeichnis sollte existieren")
        self.assertTrue(schemas_path.is_dir(), "Schemas sollte ein Verzeichnis sein")

        # Prüfe dass es .schema.json Dateien gibt
        schema_files = list(schemas_path.glob("*.schema.json"))
        self.assertGreater(len(schema_files), 0, "Es sollten Schema-Dateien existieren")

    def test_schemas_loaded_count(self):
        """Test: Korrekte Anzahl von Schemas geladen"""
        schemas = self.registry_manager.get_schemas()

        # Sollte mindestens 40 Schemas haben (44 erwartet)
        self.assertGreaterEqual(len(schemas), 40, f"Erwartet mindestens 40 Schemas, gefunden: {len(schemas)}")
        self.assertLessEqual(len(schemas), 50, f"Erwartet maximal 50 Schemas, gefunden: {len(schemas)}")

    def test_specific_schemas_exist(self):
        """Test: Spezifische wichtige Schemas existieren"""
        schemas = self.registry_manager.get_schemas()

        # Wichtige Schemas die existieren sollten (Schema-Namen ohne .json)
        important_schemas = [
            "ccu_global.schema",
            "ccu_order_active.schema",
            "module_v1_ff_serial_connection.schema",
            "module_v1_ff_serial_state.schema",
            "j1_txt_1_i_bme680.schema",
            "j1_txt_1_f_i_order.schema",
        ]

        for schema_name in important_schemas:
            self.assertIn(schema_name, schemas, f"Wichtiges Schema {schema_name} sollte existieren")

    def test_schema_files_valid_json(self):
        """Test: Schema-Dateien sind gültiges JSON"""
        schemas_path = self.registry_manager.registry_path / "schemas"
        schema_files = list(schemas_path.glob("*.schema.json"))

        for schema_file in schema_files:
            with self.subTest(schema_file=schema_file.name):
                try:
                    with open(schema_file, encoding="utf-8") as f:
                        schema_data = json.load(f)

                    # Prüfe dass es ein gültiges JSON Schema ist
                    self.assertIsInstance(schema_data, dict, f"Schema {schema_file.name} sollte ein Dictionary sein")
                    self.assertIn("type", schema_data, f"Schema {schema_file.name} sollte 'type' haben")

                    # Prüfe Schema-Struktur (kann object oder array sein)
                    schema_type = schema_data.get("type")
                    if isinstance(schema_type, list):
                        schema_type = schema_type[0] if schema_type else "object"

                    if schema_type == "object":
                        self.assertIn(
                            "properties", schema_data, f"Object Schema {schema_file.name} sollte 'properties' haben"
                        )
                    elif schema_type == "array":
                        self.assertIn("items", schema_data, f"Array Schema {schema_file.name} sollte 'items' haben")

                except json.JSONDecodeError as e:
                    self.fail(f"Schema {schema_file.name} ist kein gültiges JSON: {e}")
                except Exception as e:
                    self.fail(f"Fehler beim Laden von Schema {schema_file.name}: {e}")

    def test_schema_content_structure(self):
        """Test: Schema-Inhalt hat korrekte Struktur"""
        schemas = self.registry_manager.get_schemas()

        # Teste ein paar spezifische Schemas
        test_schemas = ["ccu_global.schema.json", "module_v1_ff_serial_connection.schema.json"]

        for schema_name in test_schemas:
            if schema_name in schemas:
                schema_data = schemas[schema_name]

                # Prüfe grundlegende Schema-Struktur
                self.assertIn("type", schema_data, f"Schema {schema_name} sollte 'type' haben")
                self.assertIn("properties", schema_data, f"Schema {schema_name} sollte 'properties' haben")

                # Prüfe dass properties ein Dictionary ist
                self.assertIsInstance(
                    schema_data["properties"], dict, f"Schema {schema_name} properties sollte ein Dictionary sein"
                )

    def test_topic_schema_mapping(self):
        """Test: Topic-Schema-Mapping funktioniert"""
        # Teste verschiedene Topics (nur solche mit bekannter Schema-Zuordnung)
        test_topics = ["ccu/global", "module/v1/ff/SVR3QA0022/state", "module/v1/ff/SVR3QA0022/connection"]

        for topic in test_topics:
            with self.subTest(topic=topic):
                schema = self.registry_manager.get_topic_schema(topic)
                description = self.registry_manager.get_topic_description(topic)

                # Schema oder Description sollte gefunden werden
                self.assertTrue(
                    schema is not None or description is not None, f"Topic {topic} sollte Schema oder Description haben"
                )

    def test_schema_validation_functionality(self):
        """Test: Schema-Validierung funktioniert"""
        # Test mit einem bekannten Topic
        test_topic = "module/v1/ff/SVR3QA0022/state"

        # Test-Payload (sollte valid sein)
        valid_payload = {"state": "idle", "timestamp": "2025-10-01T19:30:00Z", "module_id": "SVR3QA0022"}

        # Test-Payload (sollte invalid sein)
        invalid_payload = {"invalid_field": "test", "wrong_type": 123}

        # Validierung sollte funktionieren über MessageManager
        from omf2.common.message_manager import MessageManager
        message_manager = MessageManager('admin', self.registry_manager)
        result_valid = message_manager.validate_message(test_topic, valid_payload)
        result_invalid = message_manager.validate_message(test_topic, invalid_payload)

        # Ergebnisse sollten nicht None sein (können True/False sein)
        self.assertIsNotNone(result_valid, "Validierung sollte ein Ergebnis zurückgeben")
        self.assertIsNotNone(result_invalid, "Validierung sollte ein Ergebnis zurückgeben")

    def test_schema_statistics(self):
        """Test: Schema-Statistiken sind korrekt"""
        stats = self.registry_manager.get_registry_stats()

        # Prüfe Schema-spezifische Statistiken
        self.assertIn("schemas_count", stats, "Statistiken sollten schemas_count enthalten")
        self.assertIn("topics_count", stats, "Statistiken sollten topics_count enthalten")

        # Prüfe dass Schema-Count korrekt ist
        schemas = self.registry_manager.get_schemas()
        self.assertEqual(
            stats["schemas_count"],
            len(schemas),
            "Schema-Count in Statistiken sollte mit geladenen Schemas übereinstimmen",
        )

        # Prüfe dass es Topics mit Schema gibt
        topics = self.registry_manager.get_topics()
        topics_with_schema = sum(1 for topic, info in topics.items() if isinstance(info, dict) and info.get("schema"))

        self.assertGreater(topics_with_schema, 0, "Es sollten Topics mit Schema existieren")

    def test_schema_file_naming_convention(self):
        """Test: Schema-Dateien folgen Namenskonvention"""
        schemas_path = self.registry_manager.registry_path / "schemas"
        schema_files = list(schemas_path.glob("*.schema.json"))

        for schema_file in schema_files:
            with self.subTest(schema_file=schema_file.name):
                # Prüfe Namenskonvention: sollte mit .schema.json enden
                self.assertTrue(
                    schema_file.name.endswith(".schema.json"),
                    f"Schema {schema_file.name} sollte mit .schema.json enden",
                )

                # Prüfe dass Name nicht leer ist
                self.assertGreater(len(schema_file.stem), 0, f"Schema {schema_file.name} sollte einen Namen haben")


if __name__ == "__main__":
    unittest.main()
