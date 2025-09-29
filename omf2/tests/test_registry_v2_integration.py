"""
Tests für Registry v2 Integration in alle Gateways

Testet die Integration der Registry v2 (MessageTemplates, Topics, Mappings)
in alle Gateway-Komponenten.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from omf2.factory.gateway_factory import get_ccu_gateway, get_nodered_gateway, get_admin_gateway
from omf2.common.message_templates import get_message_templates


class TestRegistryV2Integration(unittest.TestCase):
    """Tests für Registry v2 Integration in alle Gateways"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock MessageTemplates für Tests
        self.mock_message_templates = MagicMock()
        self.mock_message_templates.get_topic_config.return_value = {
            'qos': 1,
            'retain': False
        }
        self.mock_message_templates.render_message.return_value = {
            'test': 'message'
        }
        self.mock_message_templates.validate_message.return_value = {
            'errors': [],
            'warnings': []
        }
        self.mock_message_templates.get_pub_topics.return_value = [
            'module/v1/ff/NodeRed/test/state',
            'ccu/global'
        ]
        self.mock_message_templates.get_sub_topics.return_value = [
            'ccu/commands',
            'opc_ua/states'
        ]

    @patch('omf2.common.message_templates.get_message_templates')
    def test_ccu_gateway_registry_integration(self, mock_get_templates):
        """Test CCU Gateway Registry v2 Integration"""
        mock_get_templates.return_value = self.mock_message_templates
        
        # Erstelle CCU Gateway
        ccu_gateway = get_ccu_gateway()
        
        # Test reset_factory mit Registry v2
        result = ccu_gateway.reset_factory()
        self.assertTrue(result)
        
        # Test send_global_command mit Registry v2
        result = ccu_gateway.send_global_command("test_command", {"param": "value"})
        self.assertTrue(result)
        
        # Prüfe, dass MessageTemplates verwendet wurde
        self.mock_message_templates.get_topic_config.assert_called()
        self.mock_message_templates.render_message.assert_called()

    @patch('omf2.common.message_templates.get_message_templates')
    def test_nodered_gateway_registry_integration(self, mock_get_templates):
        """Test Node-RED Gateway Registry v2 Integration"""
        mock_get_templates.return_value = self.mock_message_templates
        
        # Erstelle Node-RED Gateway
        nodered_gateway = get_nodered_gateway()
        
        # Test get_normalized_module_states mit Registry v2
        states = nodered_gateway.get_normalized_module_states()
        self.assertIsInstance(states, list)
        
        # Test get_pub_topics mit Registry v2
        pub_topics = nodered_gateway.get_pub_topics()
        self.assertIsInstance(pub_topics, list)
        
        # Test get_sub_topics mit Registry v2
        sub_topics = nodered_gateway.get_sub_topics()
        self.assertIsInstance(sub_topics, list)

    @patch('omf2.common.message_templates.get_message_templates')
    def test_admin_gateway_registry_integration(self, mock_get_templates):
        """Test Admin Gateway Registry v2 Integration"""
        mock_get_templates.return_value = self.mock_message_templates
        
        # Erstelle Admin Gateway
        admin_gateway = get_admin_gateway()
        
        # Test generate_message_template mit Registry v2
        message = admin_gateway.generate_message_template("test/topic", {"param": "value"})
        self.assertIsNotNone(message)
        
        # Test validate_message mit Registry v2
        validation_result = admin_gateway.validate_message("test/topic", {"test": "data"})
        self.assertIsInstance(validation_result, dict)
        self.assertIn('errors', validation_result)
        self.assertIn('warnings', validation_result)
        
        # Test get_all_topics mit Registry v2
        all_topics = admin_gateway.get_all_topics()
        self.assertIsInstance(all_topics, list)
        
        # Test get_topic_templates mit Registry v2
        topic_templates = admin_gateway.get_topic_templates()
        self.assertIsInstance(topic_templates, dict)

    @patch('omf2.common.message_templates.get_message_templates')
    def test_registry_v2_topic_configuration(self, mock_get_templates):
        """Test Registry v2 Topic-Konfiguration"""
        # Mock mit spezifischer Topic-Konfiguration
        mock_templates = MagicMock()
        mock_templates.get_topic_config.return_value = {
            'qos': 2,
            'retain': True,
            'description': 'Test topic'
        }
        mock_templates.render_message.return_value = {'status': 'success'}
        mock_get_templates.return_value = mock_templates
        
        # Test CCU Gateway mit Topic-Konfiguration
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.reset_factory()
        
        # Prüfe, dass Topic-Konfiguration abgerufen wurde
        mock_templates.get_topic_config.assert_called_with("ccu/set/reset")
        self.assertTrue(result)

    @patch('omf2.common.message_templates.get_message_templates')
    def test_registry_v2_message_rendering(self, mock_get_templates):
        """Test Registry v2 Message-Rendering"""
        # Mock mit spezifischem Message-Rendering
        mock_templates = MagicMock()
        mock_templates.get_topic_config.return_value = {'qos': 1, 'retain': False}
        mock_templates.render_message.return_value = {
            'command': 'test_command',
            'params': {'test': 'value'},
            'timestamp': '2025-09-29T12:00:00Z'
        }
        mock_get_templates.return_value = mock_templates
        
        # Test CCU Gateway mit Message-Rendering
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.send_global_command("test_command", {"test": "value"})
        
        # Prüfe, dass Message gerendert wurde
        mock_templates.render_message.assert_called()
        self.assertTrue(result)

    @patch('omf2.common.message_templates.get_message_templates')
    def test_registry_v2_validation(self, mock_get_templates):
        """Test Registry v2 Message-Validierung"""
        # Mock mit Validierungs-Ergebnissen
        mock_templates = MagicMock()
        mock_templates.validate_message.return_value = {
            'errors': ['Missing required field: timestamp'],
            'warnings': ['Field "status" is deprecated']
        }
        mock_get_templates.return_value = mock_templates
        
        # Test Admin Gateway mit Validierung
        admin_gateway = get_admin_gateway()
        result = admin_gateway.validate_message("test/topic", {"test": "data"})
        
        # Prüfe Validierungs-Ergebnis
        self.assertIsInstance(result, dict)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(len(result['warnings']), 1)

    @patch('omf2.common.message_templates.get_message_templates')
    def test_registry_v2_error_handling(self, mock_get_templates):
        """Test Registry v2 Error-Handling"""
        # Mock mit Fehler-Szenario
        mock_templates = MagicMock()
        mock_templates.get_topic_config.return_value = None  # Keine Konfiguration gefunden
        mock_templates.render_message.return_value = None  # Rendering fehlgeschlagen
        mock_get_templates.return_value = mock_templates
        
        # Test CCU Gateway mit Fehler-Handling
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.reset_factory()
        
        # Sollte trotzdem True zurückgeben (Fallback-Verhalten)
        self.assertTrue(result)

    @patch('omf2.common.message_templates.get_message_templates')
    def test_registry_v2_topic_patterns(self, mock_get_templates):
        """Test Registry v2 Topic-Pattern-Matching"""
        # Mock mit Topic-Patterns
        mock_templates = MagicMock()
        mock_templates.get_pub_topics.return_value = [
            'module/v1/ff/NodeRed/module1/state',
            'module/v1/ff/NodeRed/module2/state',
            'ccu/global'
        ]
        mock_templates.get_sub_topics.return_value = [
            'ccu/commands',
            'opc_ua/states'
        ]
        mock_get_templates.return_value = mock_templates
        
        # Test Node-RED Gateway mit Topic-Patterns
        nodered_gateway = get_nodered_gateway()
        states = nodered_gateway.get_normalized_module_states()
        
        # Prüfe, dass Topic-Patterns verwendet wurden
        mock_templates.get_pub_topics.assert_called()
        self.assertIsInstance(states, list)

    def test_message_templates_singleton_integration(self):
        """Test MessageTemplates Singleton Integration"""
        # Teste, dass alle Gateways MessageTemplates verwenden
        ccu_gateway = get_ccu_gateway()
        nodered_gateway = get_nodered_gateway()
        admin_gateway = get_admin_gateway()
        
        # Alle Gateways sollten MessageTemplates haben
        self.assertIsNotNone(ccu_gateway.message_templates)
        self.assertIsNotNone(nodered_gateway.message_templates)
        self.assertIsNotNone(admin_gateway.message_templates)

    def test_registry_v2_comprehensive_integration(self):
        """Test umfassende Registry v2 Integration"""
        # Test alle Gateways mit Registry v2
        ccu_gateway = get_ccu_gateway()
        nodered_gateway = get_nodered_gateway()
        admin_gateway = get_admin_gateway()
        
        # Test CCU Gateway
        result1 = ccu_gateway.reset_factory()
        result2 = ccu_gateway.send_global_command("test", {})
        
        # Test Node-RED Gateway
        states = nodered_gateway.get_normalized_module_states()
        pub_topics = nodered_gateway.get_pub_topics()
        sub_topics = nodered_gateway.get_sub_topics()
        
        # Test Admin Gateway
        message = admin_gateway.generate_message_template("test/topic", {})
        validation = admin_gateway.validate_message("test/topic", {})
        all_topics = admin_gateway.get_all_topics()
        topic_templates = admin_gateway.get_topic_templates()
        
        # Prüfe, dass alle Methoden funktionieren
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertIsInstance(states, list)
        self.assertIsInstance(pub_topics, list)
        self.assertIsInstance(sub_topics, list)
        self.assertIsInstance(all_topics, list)
        self.assertIsInstance(topic_templates, dict)


if __name__ == '__main__':
    unittest.main()
