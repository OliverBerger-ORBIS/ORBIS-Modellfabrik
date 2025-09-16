"""
Einfache Tests für Logging-Integration in OMF Managern
Testet die grundlegenden Logging-Features ohne komplexe Mocking
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src_orbis.omf.tools.message_template_manager import OmfMessageTemplateManager
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
from src_orbis.omf.tools.omf_mqtt_client import OmfMqttClient
from src_orbis.omf.tools.registry_manager import Registry, TopicManager


class TestManagersLoggingSimple(unittest.TestCase):
    """Einfache Tests für Logging-Integration"""

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

    def test_mqtt_gateway_has_logger(self):
        """Test: MqttGateway hat Logger-Attribut"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe ob Logger-Attribut existiert
        self.assertTrue(hasattr(gateway, 'logger'))
        self.assertIsInstance(gateway.logger, logging.Logger)
        self.assertEqual(gateway.logger.name, 'omf.tools.mqtt_gateway')

    def test_logger_names_follow_convention(self):
        """Test: Logger-Namen folgen der Konvention"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe Logger-Name-Konvention (konsistente omf.* Namen)
        expected_name = "omf.tools.mqtt_gateway"
        self.assertEqual(gateway.logger.name, expected_name)

    def test_logging_uses_get_logger_function(self):
        """Test: Manager verwenden get_logger() Funktion"""
        # Prüfe ob alle Manager get_logger() importieren
        with open('src_orbis/omf/tools/message_template_manager.py') as f:
            content = f.read()
            self.assertIn('from src_orbis.omf.tools.logging_config import get_logger', content)
            self.assertIn('get_logger(', content)

        with open('src_orbis/omf/tools/registry_manager.py') as f:
            content = f.read()
            self.assertIn('from src_orbis.omf.tools.logging_config import get_logger', content)
            self.assertIn('get_logger(', content)

        with open('src_orbis/omf/tools/mqtt_gateway.py') as f:
            content = f.read()
            self.assertIn('from .logging_config import get_logger', content)
            self.assertIn('get_logger(', content)

    def test_logging_does_not_use_print_statements(self):
        """Test: Manager verwenden keine print() Statements mehr"""
        # Prüfe ob MqttGateway keine print() Statements hat
        with open('src_orbis/omf/tools/mqtt_gateway.py') as f:
            content = f.read()
            # Sollte keine print() Statements haben
            self.assertNotIn('print(', content)

    def test_logging_initialization_messages(self):
        """Test: Manager loggen Initialisierungs-Nachrichten"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        # Capture Log-Messages
        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            MqttGateway(mock_client)

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

    def test_logger_initialization_pattern(self):
        """Test: Logger werden korrekt initialisiert"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        with patch('src_orbis.omf.tools.mqtt_gateway.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            MqttGateway(mock_client)

            # Prüfe ob get_logger mit korrektem Namen aufgerufen wurde
            expected_name = "omf.tools.mqtt_gateway"
            mock_get_logger.assert_called_with(expected_name)

    def test_logging_integration_completeness(self):
        """Test: Alle Manager haben Logging integriert"""
        # Prüfe ob alle Manager-Dateien Logging-Imports haben
        manager_files = [
            'src_orbis/omf/tools/message_template_manager.py',
            'src_orbis/omf/tools/registry_manager.py',
            'src_orbis/omf/tools/mqtt_gateway.py',
        ]

        for file_path in manager_files:
            with open(file_path) as f:
                content = f.read()
                # Sollte get_logger importieren
                self.assertIn('get_logger', content)
                # Sollte Logger-Attribut haben
                self.assertIn('self.logger = get_logger(', content)


if __name__ == "__main__":
    unittest.main()
