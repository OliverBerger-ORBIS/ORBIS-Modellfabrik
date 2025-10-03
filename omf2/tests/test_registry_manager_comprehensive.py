#!/usr/bin/env python3
"""
Comprehensive Registry Manager Tests
Testet alle Funktionalitäten der Registry Manager Klasse
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from omf2.registry.manager.registry_manager import RegistryManager, get_registry_manager


class TestRegistryManagerComprehensive(unittest.TestCase):
    """Umfassende Tests für Registry Manager"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton für saubere Tests
        RegistryManager._instance = None
        RegistryManager._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Reset Singleton
        RegistryManager._instance = None
        RegistryManager._initialized = False
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_singleton_pattern(self, mock_path):
        """Test Singleton Pattern"""
        # Mock Path und Registry-Dateien
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        # Erste Instanz
        manager1 = get_registry_manager("test/registry/")
        self.assertIsNotNone(manager1)
        
        # Zweite Instanz sollte dieselbe sein
        manager2 = get_registry_manager("different/path/")
        self.assertEqual(manager1, manager2)
        self.assertIs(manager1, manager2)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_initialization_with_registry_path(self, mock_path):
        """Test Initialisierung mit Registry-Pfad"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("custom/registry/")
        self.assertEqual(manager.registry_path, mock_path.return_value)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_load_all_registry_data(self, mock_path):
        """Test Laden aller Registry-Daten"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Prüfe, dass alle Load-Methoden aufgerufen wurden
        self.assertIsNotNone(manager.topics)
        self.assertIsNotNone(manager.schemas)
        # topic_schema_mappings entfernt - Schema-Info wird direkt aus topics geladen
        self.assertIsNotNone(manager.mqtt_clients)
        self.assertIsNotNone(manager.workpieces)
        self.assertIsNotNone(manager.modules)
        self.assertIsNotNone(manager.stations)
        self.assertIsNotNone(manager.txt_controllers)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_topics(self, mock_path):
        """Test get_topics() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        topics = manager.get_topics()
        
        self.assertIsInstance(topics, dict)
        self.assertEqual(topics, manager.topics)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_schemas(self, mock_path):
        """Test get_schemas() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        schemas = manager.get_schemas()
        
        self.assertIsInstance(schemas, dict)
        self.assertEqual(schemas, manager.schemas)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_topic_schema(self, mock_path):
        """Test get_topic_schema() Methode - Schema-Info wird direkt aus Topics geladen"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Test mit existierendem Topic
        if manager.topics:
            test_topic = list(manager.topics.keys())[0]
            schema = manager.get_topic_schema(test_topic)
            # Schema kann None sein, wenn Topic kein Schema hat
            self.assertTrue(schema is None or isinstance(schema, dict))
        
        # Test mit nicht-existierendem Topic
        schema = manager.get_topic_schema("non_existent_topic")
        self.assertIsNone(schema)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_topic_description(self, mock_path):
        """Test get_topic_description() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Test mit existierendem Topic
        manager.topics = {
            "test/topic": {
                "topic": "test/topic",
                "description": "Test topic description"
            }
        }
        description = manager.get_topic_description("test/topic")
        self.assertEqual(description, "Test topic description")
        
        # Test mit nicht-existierendem Topic
        description = manager.get_topic_description("nonexistent/topic")
        self.assertIsNone(description)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_mqtt_clients(self, mock_path):
        """Test get_mqtt_clients() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        clients = manager.get_mqtt_clients()
        
        self.assertIsInstance(clients, dict)
        self.assertEqual(clients, manager.mqtt_clients)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_workpieces(self, mock_path):
        """Test get_workpieces() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        workpieces = manager.get_workpieces()
        
        self.assertIsInstance(workpieces, dict)
        self.assertEqual(workpieces, manager.workpieces)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_modules(self, mock_path):
        """Test get_modules() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        modules = manager.get_modules()
        
        self.assertIsInstance(modules, dict)
        self.assertEqual(modules, manager.modules)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_stations(self, mock_path):
        """Test get_stations() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        stations = manager.get_stations()
        
        self.assertIsInstance(stations, dict)
        self.assertEqual(stations, manager.stations)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_txt_controllers(self, mock_path):
        """Test get_txt_controllers() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        controllers = manager.get_txt_controllers()
        
        self.assertIsInstance(controllers, dict)
        self.assertEqual(controllers, manager.txt_controllers)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_active_mqtt_clients(self, mock_path):
        """Test get_active_mqtt_clients() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Mock MQTT Clients mit 'active' Flag (nicht 'status')
        manager.mqtt_clients = {
            "client1": {"active": True, "name": "Client 1"},
            "client2": {"active": False, "name": "Client 2"},
            "client3": {"active": True, "name": "Client 3"}
        }
        
        active_clients = manager.get_active_mqtt_clients()
        self.assertIsInstance(active_clients, dict)
        self.assertEqual(len(active_clients), 2)
        self.assertIn("client1", active_clients)
        self.assertIn("client3", active_clients)
        self.assertNotIn("client2", active_clients)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_mqtt_client_config(self, mock_path):
        """Test get_mqtt_client_config() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Mock MQTT Client Config
        manager.mqtt_clients = {
            "test_client": {
                "host": "localhost",
                "port": 1883,
                "username": "test",
                "password": "test"
            }
        }
        
        config = manager.get_mqtt_client_config("test_client")
        self.assertIsInstance(config, dict)
        self.assertEqual(config["host"], "localhost")
        self.assertEqual(config["port"], 1883)
        
        # Test mit nicht-existierendem Client
        config = manager.get_mqtt_client_config("nonexistent_client")
        self.assertEqual(config, {})
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_get_registry_stats(self, mock_path):
        """Test get_registry_stats() Methode"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Mock Registry-Daten
        manager.topics = {"topic1": {}, "topic2": {}}
        manager.schemas = {"schema1": {}, "schema2": {}, "schema3": {}}
        manager.mqtt_clients = {"client1": {}}
        manager.workpieces = {"workpiece1": {}, "workpiece2": {}}
        manager.modules = {"module1": {}}
        manager.stations = {"station1": {}, "station2": {}}
        manager.txt_controllers = {"controller1": {}}
        
        stats = manager.get_registry_stats()
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["topics_count"], 2)
        self.assertEqual(stats["schemas_count"], 3)
        self.assertEqual(stats["mqtt_clients_count"], 1)
        self.assertEqual(stats["workpieces_count"], 2)
        self.assertEqual(stats["modules_count"], 1)
        self.assertEqual(stats["stations_count"], 2)
        self.assertEqual(stats["txt_controllers_count"], 1)
        self.assertIn("load_timestamp", stats)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_error_handling_missing_files(self, mock_path):
        """Test Error Handling bei fehlenden Dateien"""
        mock_path.return_value.exists.return_value = False
        mock_path.return_value.glob.return_value = []
        
        # Sollte nicht crashen, sondern leere Registry erstellen
        manager = get_registry_manager("nonexistent/registry/")
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager.topics, dict)
        self.assertIsInstance(manager.schemas, dict)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_error_handling_invalid_yaml(self, mock_path):
        """Test Error Handling bei ungültigen YAML-Dateien"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        # Mock ungültige YAML-Datei
        with patch('builtins.open', side_effect=Exception("Invalid YAML")):
            manager = get_registry_manager("test/registry/")
            self.assertIsNotNone(manager)
            # Sollte leere Registry haben
            self.assertEqual(len(manager.topics), 0)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_registry_reload_functionality(self, mock_path):
        """Test Registry Reload Funktionalität"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        original_timestamp = manager._load_timestamp
        
        # Simuliere Reload - _load_timestamp wird in _load_all_registry_data aktualisiert
        import datetime
        test_time = datetime.datetime(2025, 10, 2, 10, 0, 0)
        
        # Mock datetime.now direkt in der Klasse
        with patch.object(manager, '_load_timestamp', test_time):
            manager._load_all_registry_data()
            new_timestamp = manager._load_timestamp
            
            # Timestamp sollte aktualisiert worden sein
            self.assertNotEqual(original_timestamp, new_timestamp)
            self.assertEqual(new_timestamp, test_time)
    
    @patch('omf2.registry.manager.registry_manager.Path')
    def test_registry_data_consistency(self, mock_path):
        """Test Registry-Daten Konsistenz"""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.glob.return_value = []
        
        manager = get_registry_manager("test/registry/")
        
        # Alle get_* Methoden sollten konsistente Daten zurückgeben
        topics = manager.get_topics()
        schemas = manager.get_schemas()
        
        self.assertEqual(topics, manager.topics)
        self.assertEqual(schemas, manager.schemas)
        # mappings entfernt - topic_schema_mappings nicht mehr verfügbar
        
        # Stats sollten korrekte Zählungen haben
        stats = manager.get_registry_stats()
        self.assertEqual(stats["topics_count"], len(manager.topics))
        self.assertEqual(stats["schemas_count"], len(manager.schemas))


if __name__ == '__main__':
    unittest.main()
