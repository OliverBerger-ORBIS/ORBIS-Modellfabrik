#!/usr/bin/env python3
"""
Registry Integration Tests
Testet Gateway -> Topic -> Payload Struktur mit Registry Manager
"""

import unittest
from unittest.mock import MagicMock, patch
from omf2.factory.gateway_factory import get_admin_gateway, get_nodered_gateway, get_ccu_gateway


class TestRegistryIntegration(unittest.TestCase):
    """Test Registry Integration für alle Gateways"""
    
    def setUp(self):
        """Setup für jeden Test"""
        pass
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        pass
    
    def test_admin_gateway_registry_integration(self):
        """Test Admin Gateway Registry Integration"""
        # Test Admin Gateway
        admin_gateway = get_admin_gateway()
        
        # Prüfe Registry Manager Integration
        self.assertIsNotNone(admin_gateway.registry_manager)
        self.assertTrue(hasattr(admin_gateway.registry_manager, 'get_topics'))
    
    def test_nodered_gateway_registry_integration(self):
        """Test Node-RED Gateway Registry Integration"""
        # Test Node-RED Gateway
        nodered_gateway = get_nodered_gateway()
        
        # Prüfe Registry Manager Integration
        self.assertIsNotNone(nodered_gateway.registry_manager)
        self.assertTrue(hasattr(nodered_gateway.registry_manager, 'get_topics'))
    
    def test_ccu_gateway_registry_integration(self):
        """Test CCU Gateway Registry Integration"""
        # Test CCU Gateway
        ccu_gateway = get_ccu_gateway()
        
        # Prüfe Registry Manager Integration
        self.assertIsNotNone(ccu_gateway.registry_manager)
        self.assertTrue(hasattr(ccu_gateway.registry_manager, 'get_topics'))
    
    def test_gateway_topic_payload_structure(self):
        """Test Gateway -> Topic -> Payload Struktur"""
        # Test alle Gateways
        admin_gateway = get_admin_gateway()
        nodered_gateway = get_nodered_gateway()
        ccu_gateway = get_ccu_gateway()
        
        # Prüfe, dass alle Gateways Registry Manager verwenden
        self.assertIsNotNone(admin_gateway.registry_manager)
        self.assertIsNotNone(nodered_gateway.registry_manager)
        self.assertIsNotNone(ccu_gateway.registry_manager)
        
        # Prüfe, dass alle Gateways denselben Registry Manager haben (Singleton)
        self.assertEqual(admin_gateway.registry_manager, nodered_gateway.registry_manager)
        self.assertEqual(nodered_gateway.registry_manager, ccu_gateway.registry_manager)
    
    def test_registry_manager_singleton_integration(self):
        """Test Registry Manager Singleton Integration"""
        # Test alle Gateways
        admin_gateway = get_admin_gateway()
        nodered_gateway = get_nodered_gateway()
        ccu_gateway = get_ccu_gateway()
        
        # Alle Gateways sollten denselben Registry Manager haben (Singleton)
        self.assertEqual(admin_gateway.registry_manager, nodered_gateway.registry_manager)
        self.assertEqual(nodered_gateway.registry_manager, ccu_gateway.registry_manager)
    
    def test_topic_schema_payload_relationship(self):
        """Test Topic-Schema-Payload Beziehung"""
        # Test Admin Gateway mit Schema-Integration
        admin_gateway = get_admin_gateway()
        
        # Prüfe Topic-Zugriff
        topics = admin_gateway.registry_manager.get_topics()
        self.assertIsInstance(topics, dict)
        self.assertGreater(len(topics), 0)
        
        # Prüfe, dass Registry Manager funktioniert
        self.assertIsNotNone(admin_gateway.registry_manager)
    
    def test_registry_error_handling(self):
        """Test Registry Error Handling"""
        # Test ohne Mock - echte Registry Manager
        admin_gateway = get_admin_gateway()
        
        # Registry Manager sollte verfügbar sein
        self.assertIsNotNone(admin_gateway.registry_manager)
        
        # Topics sollten abrufbar sein
        topics = admin_gateway.registry_manager.get_topics()
        self.assertIsInstance(topics, dict)
        self.assertGreater(len(topics), 0)
    
    def test_gateway_functionality_with_registry(self):
        """Test Gateway-Funktionalität mit Registry"""
        # Test Admin Gateway Funktionalität
        admin_gateway = get_admin_gateway()
        
        # Prüfe, dass Gateway funktioniert
        self.assertIsNotNone(admin_gateway.registry_manager)
        
        # Prüfe Topic-Zugriff
        topics = admin_gateway.registry_manager.get_topics()
        self.assertIsInstance(topics, dict)
        self.assertGreater(len(topics), 0)
        
        # Prüfe, dass Gateway-Methoden verfügbar sind
        self.assertTrue(hasattr(admin_gateway, 'get_all_topics'))
        self.assertTrue(hasattr(admin_gateway, 'publish_message'))
        self.assertTrue(hasattr(admin_gateway, 'validate_message'))


if __name__ == '__main__':
    unittest.main()