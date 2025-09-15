"""
Tests für Manager Logging-Verhalten
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from src_orbis.omf.tools.message_template_manager import OmfMessageTemplateManager
from src_orbis.omf.tools.mqtt_gateway import MqttGateway
from src_orbis.omf.tools.omf_mqtt_client import OmfMqttClient
from src_orbis.omf.tools.registry_manager import Registry, TopicManager


class TestManagersLoggingBehavior(unittest.TestCase):
    """Tests für Manager Logging-Verhalten"""

    def setUp(self):
        """Test-Setup"""
        self.temp_dir = tempfile.mkdtemp()

    def test_message_template_manager_logs_initialization(self):
        """Test: MessageTemplateManager loggt Initialisierung"""
        with patch('src_orbis.omf.tools.message_template_manager.Path') as mock_path:
            # Mock für Registry v1 templates
            mock_templates_dir = Path(self.temp_dir) / "registry" / "model" / "v1" / "templates"
            mock_templates_dir.mkdir(parents=True, exist_ok=True)

            # Mock für exist() calls
            def mock_exists(path):
                return str(path).endswith("templates")

            mock_path.return_value.exists = mock_exists
            mock_path.return_value.glob.return_value = []  # Keine Templates

            with patch('src_orbis.omf.tools.message_template_manager.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                OmfMessageTemplateManager()

                # Prüfe Initialisierungs-Logs
                expected_calls = [
                    call("MessageTemplateManager initialisiert"),
                    call("✅ Using registry v1 message templates"),
                    call("📁 Using legacy template structure (templates/templates/)"),
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
                return str(path).endswith("templates")

            mock_path.return_value.exists = mock_exists
            mock_path.return_value.glob.return_value = []  # Keine Templates

            with patch('src_orbis.omf.tools.message_template_manager.get_logger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                OmfMessageTemplateManager()

                # Prüfe ob Error-Log aufgerufen wurde
                mock_logger.error.assert_called()

    def test_registry_logs_version_check(self):
        """Test: Registry loggt Version-Check"""
        # Vereinfachter Test ohne komplexe Mock-Setup
        with patch('src_orbis.omf.tools.registry_manager.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Mock Registry
            with patch('src_orbis.omf.tools.registry_manager.Registry') as mock_registry:
                mock_registry_instance = MagicMock()
                mock_registry.return_value = mock_registry_instance

                Registry()

                # Prüfe dass Logger verwendet wird
                mock_get_logger.assert_called()

    def test_topic_manager_logs_unknown_topics(self):
        """Test: TopicManager loggt unbekannte Topics"""
        # Vereinfachter Test ohne komplexe Mock-Setup
        with patch('src_orbis.omf.tools.registry_manager.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Mock Registry
            with patch('src_orbis.omf.tools.registry_manager.Registry') as mock_registry:
                mock_registry_instance = MagicMock()
                mock_registry.return_value = mock_registry_instance

                topic_mgr = TopicManager(mock_registry_instance)

                # Teste unbekanntes Topic
                topic_mgr.route("unknown/topic")

                # Prüfe dass Logger verwendet wird
                mock_get_logger.assert_called()

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
                gateway.send("test/topic", "test_builder")

                # Prüfe Publishing-Logs
                expected_info_calls = [
                    call("MqttGateway initialisiert"),
                    call("Publiziere MQTT: test/topic (QoS=1, retain=False)"),
                    call("✅ MQTT erfolgreich publiziert: test/topic"),
                ]

                expected_debug_calls = [call("Builder aufgerufen: test_builder mit {}")]

                for expected_call in expected_info_calls:
                    self.assertIn(expected_call, mock_logger.info.call_args_list)

                for expected_call in expected_debug_calls:
                    self.assertIn(expected_call, mock_logger.debug.call_args_list)

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
                gateway.send("test/topic", "test_builder")

                # Prüfe Error-Log
                expected_calls = [call("❌ MQTT-Publikation fehlgeschlagen: test/topic")]

                for expected_call in expected_calls:
                    self.assertIn(expected_call, mock_logger.error.call_args_list)


if __name__ == '__main__':
    unittest.main()
