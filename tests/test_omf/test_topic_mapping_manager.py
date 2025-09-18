import sys
import tempfile
import unittest
from pathlib import Path

import yaml

# Add the omf directory to the Python path

from omf.tools.topic_mapping_manager import TopicMappingManager

class TestTopicMappingManager(unittest.TestCase):
    """Unit Tests für TopicMappingManager"""

    def setUp(self):
        """Test-Setup mit temporärer Mapping-Datei"""
        self.temp_dir = tempfile.mkdtemp()
        self.mapping_file = Path(self.temp_dir) / "topic_message_mapping.yml"

        # Test-Mapping-Daten
        self.test_mappings = {
            "topic_mappings": {
                "ccu/control": {
                    "template": "ccu/control",
                    "direction": "outbound",
                    "description": "CCU-Befehle senden",
                    "semantic_purpose": "Steuerung der CCU",
                },
                "module/v1/ff/{module_id}/order": {
                    "template": "module/order",
                    "direction": "outbound",
                    "description": "Modul-Befehle senden",
                    "semantic_purpose": "Modul steuern",
                    "variable_fields": {"module_id": "<module_serial_number>"},
                },
                "module/v1/ff/{module_id}/state": {
                    "template": "module/state",
                    "direction": "bidirectional",
                    "description": "Modul-Zustand",
                    "semantic_purpose": "Modul-Zustand überwachen",
                    "variable_fields": {"module_id": "<module_serial_number>"},
                },
                "ccu/state/stock": {
                    "template": "ccu/state/stock",
                    "direction": "inbound",
                    "description": "CCU-Lagerbestand",
                    "semantic_purpose": "Lagerbestand überwachen",
                },
            },
            "template_categories": {
                "CCU": ["ccu/control", "ccu/state/stock"],
                "Module": [
                    "module/v1/ff/{module_id}/order",
                    "module/v1/ff/{module_id}/state",
                ],
            },
        }

        # Temporäre Mapping-Datei erstellen
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            yaml.dump(self.test_mappings, f, default_flow_style=False, allow_unicode=True)

        # Mock OMFConfig
        self.original_config_path = None
        self._mock_config_path()

    def _mock_config_path(self):
        """Mock für OMFConfig.get_config_path()"""

        # Direkte Mock-Implementierung ohne Import
        class MockOMFConfig:
            def __init__(self, temp_dir):
                self.temp_dir = temp_dir

            def get_config_path(self):
                return self.temp_dir

        # Mock in TopicMappingManager injizieren
        import omf.tools.topic_mapping_manager

        omf.tools.topic_mapping_manager.OmfConfig = lambda: MockOMFConfig(self.temp_dir)

    def tearDown(self):
        """Test-Cleanup"""
        # Temporäre Dateien löschen
        if self.mapping_file.exists():
            self.mapping_file.unlink()
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def test_init_loads_mappings(self):
        """Test: Initialisierung lädt Topic-Mappings"""
        manager = TopicMappingManager()

        self.assertIsNotNone(manager.topic_mappings)
        self.assertIsNotNone(manager.template_categories)
        self.assertEqual(len(manager.topic_mappings), 4)
        self.assertEqual(len(manager.template_categories), 2)

    def test_get_available_topics(self):
        """Test: Verfügbare Topics abrufen"""
        manager = TopicMappingManager()
        topics = manager.get_available_topics()

        expected_topics = [
            "ccu/control",
            "module/v1/ff/{module_id}/order",
            "module/v1/ff/{module_id}/state",
            "ccu/state/stock",
        ]

        self.assertEqual(set(topics), set(expected_topics))

    def test_get_topic_categories(self):
        """Test: Topic-Kategorien abrufen"""
        manager = TopicMappingManager()
        categories = manager.get_topic_categories()

        expected_categories = ["CCU", "Module"]
        self.assertEqual(set(categories), set(expected_categories))

    def test_get_topics_by_category(self):
        """Test: Topics nach Kategorie abrufen"""
        manager = TopicMappingManager()

        ccu_topics = manager.get_topics_by_category("CCU")
        expected_ccu = ["ccu/control", "ccu/state/stock"]
        self.assertEqual(set(ccu_topics), set(expected_ccu))

        module_topics = manager.get_topics_by_category("Module")
        expected_module = [
            "module/v1/ff/{module_id}/order",
            "module/v1/ff/{module_id}/state",
        ]
        self.assertEqual(set(module_topics), set(expected_module))

    def test_get_template_for_topic(self):
        """Test: Template für Topic finden"""
        manager = TopicMappingManager()

        template = manager.get_template_for_topic("ccu/control")
        self.assertEqual(template, "ccu/control")

        template = manager.get_template_for_topic("module/v1/ff/{module_id}/order")
        self.assertEqual(template, "module/order")

        template = manager.get_template_for_topic("nonexistent/topic")
        self.assertIsNone(template)

    def test_get_topic_info(self):
        """Test: Vollständige Topic-Informationen abrufen"""
        manager = TopicMappingManager()

        info = manager.get_topic_info("ccu/control")
        self.assertIsNotNone(info)
        self.assertEqual(info["template"], "ccu/control")
        self.assertEqual(info["direction"], "outbound")
        self.assertEqual(info["description"], "CCU-Befehle senden")

        info = manager.get_topic_info("nonexistent/topic")
        self.assertIsNone(info)

    def test_get_topics_for_template(self):
        """Test: Topics für Template finden"""
        manager = TopicMappingManager()

        topics = manager.get_topics_for_template("module/order")
        expected = ["module/v1/ff/{module_id}/order"]
        self.assertEqual(topics, expected)

        topics = manager.get_topics_for_template("nonexistent/template")
        self.assertEqual(topics, [])

    def test_resolve_topic_variables(self):
        """Test: Variable in Topic-Patterns auflösen"""
        manager = TopicMappingManager()

        # Module-ID auflösen
        resolved = manager.resolve_topic_variables("module/v1/ff/{module_id}/order", module_id="SVR3QA2098")
        self.assertEqual(resolved, "module/v1/ff/SVR3QA2098/order")

        # Mehrere Variable
        resolved = manager.resolve_topic_variables(
            "module/v1/ff/{module_id}/{action}", module_id="SVR3QA2098", action="order"
        )
        self.assertEqual(resolved, "module/v1/ff/SVR3QA2098/order")

        # Keine Variable
        resolved = manager.resolve_topic_variables("ccu/control")
        self.assertEqual(resolved, "ccu/control")

    def test_get_variable_fields(self):
        """Test: Variable Felder für Topic abrufen"""
        manager = TopicMappingManager()

        fields = manager.get_variable_fields("module/v1/ff/{module_id}/order")
        expected = {"module_id": "<module_serial_number>"}
        self.assertEqual(fields, expected)

        fields = manager.get_variable_fields("ccu/control")
        self.assertEqual(fields, {})

        fields = manager.get_variable_fields("nonexistent/topic")
        self.assertEqual(fields, {})

    def test_missing_mapping_file(self):
        """Test: Verhalten bei fehlender Mapping-Datei"""
        # Mapping-Datei löschen
        if self.mapping_file.exists():
            self.mapping_file.unlink()

        manager = TopicMappingManager()

        # Sollte keine Fehler werfen, aber leere Mappings haben
        self.assertEqual(len(manager.topic_mappings), 0)
        self.assertEqual(len(manager.template_categories), 0)

    def test_invalid_yaml_file(self):
        """Test: Verhalten bei ungültiger YAML-Datei"""
        # Ungültige YAML schreiben
        with open(self.mapping_file, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content: [")

        manager = TopicMappingManager()

        # Sollte keine Fehler werfen, aber leere Mappings haben
        self.assertEqual(len(manager.topic_mappings), 0)
        self.assertEqual(len(manager.template_categories), 0)

def run_tests():
    """Führt alle Tests aus"""
    # Test-Suite erstellen
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTopicMappingManager)

    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
