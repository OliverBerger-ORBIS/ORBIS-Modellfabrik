"""
Tests für Logging-Verhalten in OMF Managern
Testet ob Manager korrekte Log-Messages ausgeben
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

from src_orbis.omf.tools.message_template_manager import OmfMessageTemplateManager
from src_orbis.omf.tools.registry_manager import Registry, TopicManager
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
from src_orbis.omf.tools.omf_mqtt_client import OmfMqttClient


class TestManagersLoggingBehavior(unittest.TestCase):
    """Tests für Logging-Verhalten in allen Managern"""

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

    def test_message_template_manager_logs_initialization(self):
        """Test: MessageTemplateManager loggt Initialisierung"""
        with patch('src_orbis.omf.tools.message_template_manager.Path') as mock_path:
            # Mock für Registry v1 templates
            mock_templates_dir = Path(self.temp_dir) / "registry" / "model" / "v1" / "templates"
            mock_templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Mock für exist() calls
            def mock_exists(path):
                if "registry" in str(path) and "templates" in str(path):
                    return True
                return False
            
            with patch.object(Path, 'exists', side_effect=mock_exists):
                with patch('src_orbis.omf.tools.message_template_manager.get_logger') as mock_get_logger:
                    mock_logger = MagicMock()
                    mock_get_logger.return_value = mock_logger
                    
                    manager = OmfMessageTemplateManager()
                    
                    # Prüfe Initialisierungs-Logs
                    expected_calls = [
                        call("MessageTemplateManager initialisiert"),
                        call("Templates-Verzeichnis: " + str(mock_templates_dir)),
                        call("✅ Using registry v1 message templates"),
                        call("✅ 0 Templates geladen")
                    ]
                    
                    # Prüfe ob alle erwarteten Logs aufgerufen wurden
                    for expected_call in expected_calls:
                        self.assertIn(expected_call, mock_logger.info.call_args_list)

    def test_message_template_manager_logs_errors(self):
        """Test: MessageTemplateManager loggt Fehler korrekt"""
        with patch('src_orbis.omf.tools.message_template_manager.Path') as mock_path:
            # Mock für Registry v1 templates
            mock_templates_dir = Path(self.temp_dir) / "registry" / "model" / "v1" / "templates"
            mock_templates_dir.mkdir(parents=True, exist_ok=True)
            
            # Mock für exist() calls
            def mock_exists(path):
                if "registry" in str(path) and "templates" in str(path):
                    return True
                return False
            
            with patch.object(Path, 'exists', side_effect=mock_exists):
                with patch('src_orbis.omf.tools.message_template_manager.get_logger') as mock_get_logger:
                    mock_logger = MagicMock()
                    mock_get_logger.return_value = mock_logger
                    
                    # Mock für _load_metadata um Fehler zu simulieren
                    with patch.object(OmfMessageTemplateManager, '_load_metadata', side_effect=Exception("Test error")):
                        manager = OmfMessageTemplateManager()
                        
                        # Prüfe ob Error-Log aufgerufen wurde
                        mock_logger.error.assert_called()

    def test_registry_logs_version_check(self):
        """Test: Registry loggt Version-Check"""
        with patch('src_orbis.omf.tools.registry_manager.Path') as mock_path:
            # Mock für Registry-Struktur
            mock_root = Path(self.temp_dir) / "registry" / "model" / "v1"
            mock_root.mkdir(parents=True, exist_ok=True)
            
            # Mock manifest.yml
            manifest_file = mock_root / "manifest.yml"
            manifest_file.write_text("version: 1.0.0")
            
            mock_path.return_value.parent.parent.parent = Path(self.temp_dir)
            mock_path.return_value.parent.parent.parent.__truediv__.return_value = mock_root
            
            with patch('src_orbis.omf.tools.registry_manager.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                registry = Registry()
                
                # Prüfe Version-Check-Log
                expected_calls = [
                    call("Registry v1 Manager initialisiert"),
                    call("Registry-Root: " + str(mock_root)),
                    call("✅ Registry version check passed: 1.0.0")
                ]
                
                for expected_call in expected_calls:
                    self.assertIn(expected_call, mock_logger.info.call_args_list)

    def test_topic_manager_logs_unknown_topics(self):
        """Test: TopicManager loggt unbekannte Topics"""
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
            
            with patch('src_orbis.omf.tools.registry_manager.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                
                registry = Registry()
                topic_manager = TopicManager(registry)
                
                # Teste unbekanntes Topic
                result = topic_manager.route("unknown/topic")
                
                # Prüfe ob Warning-Log aufgerufen wurde
                mock_logger.warning.assert_called_with("⚠️ Unknown topic: unknown/topic")
                self.assertIsNone(result)

    def test_mqtt_gateway_logs_publishing(self):
        """Test: MqttGateway loggt MQTT-Publishing"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        mock_client.publish_json.return_value = True
        
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Mock message generator
            with patch('src_orbis.omf.tools.mqtt_gateway.mg') as mock_mg:
                mock_mg.test_builder = MagicMock(return_value={"test": "data"})
                
                # Teste MQTT-Publishing
                result = gateway.send("test/topic", "test_builder")
                
                # Prüfe Publishing-Logs
                expected_calls = [
                    call("MqttGateway initialisiert"),
                    call("Builder aufgerufen: test_builder mit {}"),
                    call("Publiziere MQTT: test/topic (QoS=1, retain=False)"),
                    call("✅ MQTT erfolgreich publiziert: test/topic")
                ]
                
                for expected_call in expected_calls:
                    self.assertIn(expected_call, mock_logger.info.call_args_list)

    def test_mqtt_gateway_logs_publishing_errors(self):
        """Test: MqttGateway loggt MQTT-Publishing-Fehler"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        mock_client.publish_json.return_value = False  # Simuliere Fehler
        
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Mock message generator
            with patch('src_orbis.omf.tools.mqtt_gateway.mg') as mock_mg:
                mock_mg.test_builder = MagicMock(return_value={"test": "data"})
                
                # Teste MQTT-Publishing mit Fehler
                result = gateway.send("test/topic", "test_builder")
                
                # Prüfe Error-Log
                mock_logger.error.assert_called_with("❌ MQTT-Publikation fehlgeschlagen: test/topic")
                self.assertFalse(result)

    def test_mqtt_gateway_logs_builder_errors(self):
        """Test: MqttGateway loggt Builder-Fehler"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Teste unbekannten Builder
            try:
                gateway.build_via_mg("nonexistent_builder")
            except ValueError:
                pass  # Erwarteter Fehler
            
            # Prüfe Error-Log
            mock_logger.error.assert_called_with("Unbekannter message_generator-Builder: nonexistent_builder")

    def test_logging_uses_correct_levels(self):
        """Test: Manager verwenden korrekte Log-Level"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Teste verschiedene Log-Level
            gateway.logger.info("Info message")
            gateway.logger.warning("Warning message")
            gateway.logger.error("Error message")
            gateway.logger.debug("Debug message")
            
            # Prüfe ob korrekte Methoden aufgerufen wurden
            mock_logger.info.assert_called_with("Info message")
            mock_logger.warning.assert_called_with("Warning message")
            mock_logger.error.assert_called_with("Error message")
            mock_logger.debug.assert_called_with("Debug message")

    def test_logging_messages_are_structured(self):
        """Test: Log-Messages sind strukturiert und informativ"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)
        
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            gateway = MqttGateway(mock_client)
            
            # Teste strukturierte Log-Messages
            gateway.logger.info("✅ MQTT erfolgreich publiziert: test/topic")
            gateway.logger.error("❌ MQTT-Publikation fehlgeschlagen: test/topic")
            gateway.logger.warning("⚠️ Unknown topic: test/topic")
            
            # Prüfe ob Messages strukturiert sind
            info_calls = [call for call in mock_logger.info.call_args_list if "✅" in str(call)]
            error_calls = [call for call in mock_logger.error.call_args_list if "❌" in str(call)]
            warning_calls = [call for call in mock_logger.warning.call_args_list if "⚠️" in str(call)]
            
            self.assertTrue(len(info_calls) > 0)
            self.assertTrue(len(error_calls) > 0)
            self.assertTrue(len(warning_calls) > 0)


if __name__ == "__main__":
    unittest.main()
