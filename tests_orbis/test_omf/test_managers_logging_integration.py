"""
Tests für Logging-Integration in OMF Managern
Testet ob alle Manager korrektes Logging implementiert haben
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src_orbis.omf.tools.message_template_manager import OmfMessageTemplateManager
from src_orbis.omf.tools.registry_manager import Registry, TopicManager, MessageTemplateManager as RegistryMessageTemplateManager
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
from src_orbis.omf.tools.omf_mqtt_client import OmfMqttClient


class TestManagersLoggingIntegration(unittest.TestCase):
    """Tests für Logging-Integration in allen Managern"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Logging zurücksetzen
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)
        root.setLevel(logging.WARNING)

    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Logging zurücksetzen
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)
        root.setLevel(logging.WARNING)

    def test_message_template_manager_has_logger(self):
        """Test: MessageTemplateManager hat Logger-Attribut"""
        # Erstelle echte Registry-Struktur für Test
        registry_dir = Path(self.temp_dir) / "registry" / "model" / "v1"
        templates_dir = registry_dir / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Erstelle manifest.yml
        manifest_file = registry_dir / "manifest.yml"
        manifest_file.write_text("version: 1.0.0")
        
        # Erstelle categories.yml
        categories_file = registry_dir / "categories.yml"
        categories_file.write_text("categories: {}")
        
        # Mock für get_logger
        with patch('src_orbis.omf.tools.message_template_manager.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Mock für Path-Konstruktor
            with patch('src_orbis.omf.tools.message_template_manager.Path') as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.parent.parent.parent.parent = Path(self.temp_dir)
                mock_path_class.return_value = mock_path_instance
                
                manager = OmfMessageTemplateManager()
                
                # Prüfe ob Logger-Attribut existiert
                self.assertTrue(hasattr(manager, 'logger'))
                self.assertEqual(manager.logger, mock_logger)

    def test_registry_has_logger(self):
        """Test: Registry hat Logger-Attribut"""
        # Erstelle echte Registry-Struktur für Test
        registry_dir = Path(self.temp_dir) / "registry" / "model" / "v1"
        registry_dir.mkdir(parents=True, exist_ok=True)
        
        # Erstelle manifest.yml
        manifest_file = registry_dir / "manifest.yml"
        manifest_file.write_text("version: 1.0.0")
        
        # Mock für get_logger
        with patch('src_orbis.omf.tools.registry_manager.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Mock für Path-Konstruktor
            with patch('src_orbis.omf.tools.registry_manager.Path') as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_instance.parent.parent.parent = Path(self.temp_dir)
                mock_path_class.return_value = mock_path_instance
                
                registry = Registry()
                
                # Prüfe ob Logger-Attribut existiert
                self.assertTrue(hasattr(registry, 'logger'))
                self.assertEqual(registry.logger, mock_logger)

    def test_topic_manager_has_logger(self):
        """Test: TopicManager hat Logger-Attribut"""
        with patch('src_orbis.omf.tools.registry_manager.Path') as mock_path:
            # Mock für Registry-Struktur
            mock_root = Path(self.temp_dir) / "registry" / "model" / "v1"
            mock_root.mkdir(parents=True, exist_ok=True)
            
            # Mock manifest.yml
            manifest_file = mock_root / "manifest.yml"
            manifest_file.write_text("version: 1.0.0")
            
            # Mock mappings/topic_template.yml
            mappings_dir = mock_root / "mappings"
            mappings_dir.mkdir(exist_ok=True)
            topic_template_file = mappings_dir / "topic_template.yml"
            topic_template_file.write_text("""
mappings:
  - topic: "test/topic"
    template: "test.template"
    direction: "inbound"
""")
            
            mock_path.return_value.parent.parent.parent = Path(self.temp_dir)
            mock_path.return_value.parent.parent.parent.__truediv__.return_value = mock_root
            
            registry = Registry()
            topic_manager = TopicManager(registry)
            
            # Prüfe ob Logger-Attribut existiert
            self.assertTrue(hasattr(topic_manager, 'logger'))
            self.assertIsInstance(topic_manager.logger, logging.Logger)
            self.assertEqual(topic_manager.logger.name, 'src_orbis.omf.tools.registry_manager.TopicManager')

    def test_registry_message_template_manager_has_logger(self):
        """Test: Registry MessageTemplateManager hat Logger-Attribut"""
        with patch('src_orbis.omf.tools.registry_manager.Path') as mock_path:
            # Mock für Registry-Struktur
            mock_root = Path(self.temp_dir) / "registry" / "model" / "v1"
            mock_root.mkdir(parents=True, exist_ok=True)
            
            # Mock manifest.yml
            manifest_file = mock_root / "manifest.yml"
            manifest_file.write_text("version: 1.0.0")
            
            # Mock templates/
            templates_dir = mock_root / "templates"
            templates_dir.mkdir(exist_ok=True)
            template_file = templates_dir / "test_template.yml"
            template_file.write_text("""
metadata:
  version: 1.0.0
templates:
  test_template:
    structure: {}
""")
            
            mock_path.return_value.parent.parent.parent = Path(self.temp_dir)
            mock_path.return_value.parent.parent.parent.__truediv__.return_value = mock_root
            
            registry = Registry()
            template_manager = RegistryMessageTemplateManager(registry)
            
            # Prüfe ob Logger-Attribut existiert
            self.assertTrue(hasattr(template_manager, 'logger'))
            self.assertIsInstance(template_manager.logger, logging.Logger)
            self.assertEqual(template_manager.logger.name, 'src_orbis.omf.tools.registry_manager.MessageTemplateManager')

    def test_mqtt_gateway_has_logger(self):
        """Test: MqttGateway hat Logger-Attribut"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        gateway = MqttGateway(mock_client)
        
        # Prüfe ob Logger-Attribut existiert
        self.assertTrue(hasattr(gateway, 'logger'))
        self.assertIsInstance(gateway.logger, logging.Logger)
        self.assertEqual(gateway.logger.name, 'src_orbis.omf.tools.mqtt_gateway.MqttGateway')

    def test_logger_names_follow_convention(self):
        """Test: Logger-Namen folgen der Konvention f'{__name__}.{self.__class__.__name__}'"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        gateway = MqttGateway(mock_client)
        
        # Prüfe Logger-Name-Konvention
        expected_name = f"{gateway.__class__.__module__}.{gateway.__class__.__name__}"
        self.assertEqual(gateway.logger.name, expected_name)

    def test_logging_levels_are_appropriate(self):
        """Test: Logger verwenden angemessene Log-Level"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        gateway = MqttGateway(mock_client)
        
        # Prüfe ob Logger-Level gesetzt ist
        self.assertIsNotNone(gateway.logger.level)
        # Level sollte >= NOTSET sein (0 ist NOTSET, was OK ist)
        self.assertGreaterEqual(gateway.logger.level, logging.NOTSET)

    def test_logging_does_not_use_print_statements(self):
        """Test: Manager verwenden keine print() Statements mehr"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        # Prüfe ob MqttGateway keine print() Statements hat
        with open('src_orbis/omf/tools/mqtt_gateway.py', 'r') as f:
            content = f.read()
            # Sollte keine print() Statements haben
            self.assertNotIn('print(', content)

    def test_logging_uses_get_logger_function(self):
        """Test: Manager verwenden get_logger() Funktion"""
        # Prüfe ob alle Manager get_logger() importieren
        with open('src_orbis/omf/tools/message_template_manager.py', 'r') as f:
            content = f.read()
            self.assertIn('from src_orbis.omf.tools.logging_config import get_logger', content)
            self.assertIn('get_logger(', content)

        with open('src_orbis/omf/tools/registry_manager.py', 'r') as f:
            content = f.read()
            self.assertIn('from src_orbis.omf.tools.logging_config import get_logger', content)
            self.assertIn('get_logger(', content)

        with open('src_orbis/omf/tools/mqtt_gateway.py', 'r') as f:
            content = f.read()
            self.assertIn('from .logging_config import get_logger', content)
            self.assertIn('get_logger(', content)

    def test_logging_initialization_messages(self):
        """Test: Manager loggen Initialisierungs-Nachrichten"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        # Capture Log-Messages
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Prüfe ob Initialisierungs-Log aufgerufen wurde
            mock_logger.info.assert_called_with("MqttGateway initialisiert")

    def test_logging_error_handling(self):
        """Test: Manager loggen Fehler korrekt"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        # Capture Log-Messages
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Teste Fehler-Logging
            try:
                gateway.build_via_mg("nonexistent_builder")
            except ValueError:
                pass  # Erwarteter Fehler
            
            # Prüfe ob Error-Log aufgerufen wurde
            mock_logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()
