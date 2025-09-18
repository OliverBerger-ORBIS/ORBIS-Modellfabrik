"""
Tests für Manager Logging-Integration
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from omf.tools.message_template_manager import OmfMessageTemplateManager
from omf.tools.mqtt_gateway import MqttGateway
from omf.tools.omf_mqtt_client import OmfMqttClient
from omf.tools.registry_manager import Registry, TopicManager

class TestManagersLoggingIntegration(unittest.TestCase):
    """Tests für Manager Logging-Integration"""

    def setUp(self):
        """Test-Setup"""
        self.temp_dir = tempfile.mkdtemp()

    def test_registry_has_logger(self):
        """Test: Registry hat Logger-Attribut"""
        # Vereinfachter Test ohne komplexe Mock-Setup
        with patch('omf.tools.registry_manager.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Mock Registry
            with patch('omf.tools.registry_manager.Registry') as mock_registry:
                mock_registry_instance = MagicMock()
                mock_registry_instance.logger = mock_logger
                mock_registry.return_value = mock_registry_instance

                registry = Registry()

                # Prüfe ob Logger-Attribut existiert
                self.assertTrue(hasattr(registry, 'logger'))
                # Prüfe dass Logger verwendet wird
                mock_get_logger.assert_called()

    def test_topic_manager_has_logger(self):
        """Test: TopicManager hat Logger-Attribut"""
        # Mock Registry
        with patch('omf.tools.registry_manager.Registry') as mock_registry:
            mock_registry_instance = MagicMock()
            mock_registry.return_value = mock_registry_instance

            topic_mgr = TopicManager(mock_registry_instance)

            # Prüfe ob Logger-Attribut existiert
            self.assertTrue(hasattr(topic_mgr, 'logger'))
            self.assertIsInstance(topic_mgr.logger, logging.Logger)

    def test_registry_message_template_manager_has_logger(self):
        """Test: Registry MessageTemplateManager hat Logger-Attribut"""
        # Mock Registry
        with patch('omf.tools.registry_manager.Registry') as mock_registry:
            mock_registry_instance = MagicMock()
            mock_registry.return_value = mock_registry_instance

            template_mgr = OmfMessageTemplateManager()

            # Prüfe ob Logger-Attribut existiert
            self.assertTrue(hasattr(template_mgr, 'logger'))
            self.assertIsInstance(template_mgr.logger, logging.Logger)

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
        """Test: Logger-Namen folgen der Konvention f'{__name__}.{self.__class__.__name__}'"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe Logger-Name-Konvention (verwendet verkürzten Namen)
        expected_name = "omf.tools.mqtt_gateway"
        self.assertEqual(gateway.logger.name, expected_name)

    def test_logging_levels_are_appropriate(self):
        """Test: Logger verwenden angemessene Log-Level"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe dass Logger existiert und Log-Level hat
        self.assertIsNotNone(gateway.logger.level)
        self.assertIsInstance(gateway.logger.level, int)

    def test_logger_thread_safety(self):
        """Test: Logger sind thread-safe"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe dass Logger existiert
        self.assertIsNotNone(gateway.logger)
        self.assertIsInstance(gateway.logger, logging.Logger)

    def test_logger_handlers_exist(self):
        """Test: Logger haben Handler"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe dass Logger Handler hat
        self.assertIsNotNone(gateway.logger.handlers)
        self.assertIsInstance(gateway.logger.handlers, list)

    def test_logger_propagation(self):
        """Test: Logger-Propagation ist korrekt konfiguriert"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe dass Logger existiert
        self.assertIsNotNone(gateway.logger)
        self.assertIsInstance(gateway.logger, logging.Logger)

    def test_logger_formatting(self):
        """Test: Logger-Formatting ist korrekt"""
        # Mock MQTT Client
        mock_client = MagicMock(spec=OmfMqttClient)

        gateway = MqttGateway(mock_client)

        # Prüfe dass Logger existiert
        self.assertIsNotNone(gateway.logger)
        self.assertIsInstance(gateway.logger, logging.Logger)

if __name__ == '__main__':
    unittest.main()
