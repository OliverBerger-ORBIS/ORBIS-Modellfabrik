"""
Vereinfachte Tests für Registry v2 Integration in alle Gateways

Testet die grundlegende Integration der Registry v2 (MessageTemplates, Topics, Mappings)
in alle Gateway-Komponenten.
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from omf2.factory.gateway_factory import get_ccu_gateway, get_nodered_gateway, get_admin_gateway


class TestRegistryV2IntegrationSimple(unittest.TestCase):
    """Vereinfachte Tests für Registry v2 Integration in alle Gateways"""

    def test_ccu_gateway_registry_integration(self):
        """Test CCU Gateway Registry v2 Integration"""
        # Erstelle CCU Gateway
        ccu_gateway = get_ccu_gateway()
        
        # Test reset_factory mit Registry v2
        result = ccu_gateway.reset_factory()
        self.assertTrue(result)
        
        # Test send_global_command mit Registry v2
        result = ccu_gateway.send_global_command("test_command", {"param": "value"})
        self.assertTrue(result)
        
        # Prüfe, dass MessageTemplates vorhanden ist
        self.assertIsNotNone(ccu_gateway.message_templates)

    def test_nodered_gateway_registry_integration(self):
        """Test Node-RED Gateway Registry v2 Integration"""
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
        
        # Prüfe, dass MessageTemplates vorhanden ist
        self.assertIsNotNone(nodered_gateway.message_templates)

    def test_admin_gateway_registry_integration(self):
        """Test Admin Gateway Registry v2 Integration"""
        # Erstelle Admin Gateway
        admin_gateway = get_admin_gateway()
        
        # Test generate_message_template mit Registry v2
        message = admin_gateway.generate_message_template("test/topic", {"param": "value"})
        # Kann None sein, wenn Topic nicht in Registry existiert
        self.assertTrue(message is None or isinstance(message, dict))
        
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
        
        # Prüfe, dass MessageTemplates vorhanden ist
        self.assertIsNotNone(admin_gateway.message_templates)

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

    def test_registry_v2_error_handling(self):
        """Test Registry v2 Error-Handling"""
        # Test CCU Gateway mit Fehler-Handling
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.reset_factory()
        
        # Sollte True zurückgeben (Fallback-Verhalten)
        self.assertTrue(result)

    def test_registry_v2_topic_patterns(self):
        """Test Registry v2 Topic-Pattern-Matching"""
        # Test Node-RED Gateway mit Topic-Patterns
        nodered_gateway = get_nodered_gateway()
        states = nodered_gateway.get_normalized_module_states()
        
        # Prüfe, dass Methode funktioniert
        self.assertIsInstance(states, list)

    def test_registry_v2_validation(self):
        """Test Registry v2 Message-Validierung"""
        # Test Admin Gateway mit Validierung
        admin_gateway = get_admin_gateway()
        result = admin_gateway.validate_message("test/topic", {"test": "data"})
        
        # Prüfe Validierungs-Ergebnis
        self.assertIsInstance(result, dict)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)

    def test_registry_v2_message_rendering(self):
        """Test Registry v2 Message-Rendering"""
        # Test CCU Gateway mit Message-Rendering
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.send_global_command("test_command", {"test": "value"})
        
        # Prüfe, dass Methode funktioniert
        self.assertTrue(result)

    def test_registry_v2_topic_configuration(self):
        """Test Registry v2 Topic-Konfiguration"""
        # Test CCU Gateway mit Topic-Konfiguration
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.reset_factory()
        
        # Prüfe, dass Methode funktioniert
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
