#!/usr/bin/env python3
"""
Test Registry Migration - Neue Registry-Struktur ohne model/v2/
"""

import unittest
from pathlib import Path
from omf2.registry.manager.registry_manager import get_registry_manager, RegistryManager


class TestRegistryMigration(unittest.TestCase):
    """Test Registry Migration von model/v2/ zu direkter Struktur"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton
        RegistryManager._instance = None
        RegistryManager._initialized = False
    
    def test_registry_path_correct(self):
        """Test: Registry-Pfad ist korrekt (ohne model/v2/)"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        # Prüfe Registry-Pfad
        expected_path = Path("omf2/registry")
        self.assertEqual(registry_manager.registry_path, expected_path)
        
        # Prüfe dass model/v2/ nicht mehr existiert
        old_path = registry_manager.registry_path / "model" / "v2"
        self.assertFalse(old_path.exists(), "Alte model/v2/ Struktur sollte nicht mehr existieren")
    
    def test_schemas_directory_exists(self):
        """Test: Schemas-Verzeichnis existiert"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        schemas_path = registry_manager.registry_path / "schemas"
        self.assertTrue(schemas_path.exists(), "Schemas-Verzeichnis sollte existieren")
        self.assertTrue(schemas_path.is_dir(), "Schemas sollte ein Verzeichnis sein")
    
    def test_schemas_loaded_correctly(self):
        """Test: Schemas werden korrekt geladen"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        schemas = registry_manager.get_schemas()
        self.assertIsInstance(schemas, dict, "Schemas sollten ein Dictionary sein")
        self.assertGreater(len(schemas), 0, "Es sollten Schemas geladen werden")
        
        # Prüfe spezifische Schemas (Schema-Namen ohne .json)
        expected_schemas = [
            "ccu_global.schema",
            "module_v1_ff_serial_connection.schema",
            "j1_txt_1_i_bme680.schema"
        ]
        
        for schema_name in expected_schemas:
            self.assertIn(schema_name, schemas, f"Schema {schema_name} sollte geladen werden")
    
    def test_topics_directory_exists(self):
        """Test: Topics-Verzeichnis existiert"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        topics_path = registry_manager.registry_path / "topics"
        self.assertTrue(topics_path.exists(), "Topics-Verzeichnis sollte existieren")
        self.assertTrue(topics_path.is_dir(), "Topics sollte ein Verzeichnis sein")
    
    def test_topics_loaded_correctly(self):
        """Test: Topics werden korrekt geladen"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        topics = registry_manager.get_topics()
        self.assertIsInstance(topics, dict, "Topics sollten ein Dictionary sein")
        self.assertGreater(len(topics), 0, "Es sollten Topics geladen werden")
        
        # Prüfe dass Topics Schema-Informationen haben
        for topic, info in topics.items():
            if isinstance(info, dict):
                # Prüfe dass Schema-Feld existiert (kann None sein)
                self.assertIn('schema', info, f"Topic {topic} sollte ein Schema-Feld haben")
                self.assertIn('description', info, f"Topic {topic} sollte ein Description-Feld haben")
    
    def test_registry_files_exist(self):
        """Test: Registry-Dateien existieren direkt unter registry/"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        expected_files = [
            "modules.yml",
            "mqtt_clients.yml", 
            "stations.yml",
            "txt_controllers.yml",
            "workpieces.yml"
        ]
        
        for filename in expected_files:
            file_path = registry_manager.registry_path / filename
            self.assertTrue(file_path.exists(), f"Datei {filename} sollte existieren")
    
    def test_tools_directory_exists(self):
        """Test: Tools-Verzeichnis existiert"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        tools_path = registry_manager.registry_path / "tools"
        self.assertTrue(tools_path.exists(), "Tools-Verzeichnis sollte existieren")
        self.assertTrue(tools_path.is_dir(), "Tools sollte ein Verzeichnis sein")
        
        # Prüfe spezifische Tools
        expected_tools = [
            "add_schema_to_topics.py",
            "test_payload_generator.py"
        ]
        
        for tool_name in expected_tools:
            tool_path = tools_path / tool_name
            self.assertTrue(tool_path.exists(), f"Tool {tool_name} sollte existieren")
    
    def test_schema_validation_works(self):
        """Test: Schema-Validierung funktioniert"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        # Test mit einem bekannten Topic
        test_topic = "module/v1/ff/SVR3QA0022/state"
        schema = registry_manager.get_topic_schema(test_topic)
        
        # Schema sollte gefunden werden (kann None sein wenn kein Schema definiert)
        self.assertIsNotNone(schema, f"Schema für Topic {test_topic} sollte gefunden werden")
    
    def test_registry_stats_correct(self):
        """Test: Registry-Statistiken sind korrekt"""
        registry_manager = get_registry_manager("omf2/registry/")
        
        stats = registry_manager.get_registry_stats()
        
        # Prüfe dass Statistiken Schema-Informationen enthalten
        self.assertIn('schemas_count', stats, "Statistiken sollten schemas_count enthalten")
        self.assertIn('topics_count', stats, "Statistiken sollten topics_count enthalten")
        
        # Prüfe dass Schema-Count größer als 0 ist
        self.assertGreater(stats['schemas_count'], 0, "Es sollten Schemas geladen werden")
        self.assertGreater(stats['topics_count'], 0, "Es sollten Topics geladen werden")


if __name__ == '__main__':
    unittest.main()
