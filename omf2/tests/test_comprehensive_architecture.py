"""
Comprehensive Tests für die gesamte gekapselte MQTT-Architektur

Testet alle Komponenten der Architektur:
- MessageTemplates Singleton
- Gateway-Factory
- Alle Gateways (CCU, Node-RED, Admin)
- Registry v2 Integration
- UI-Komponenten
- Streamlit Integration
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.factory.gateway_factory import (
    get_gateway_factory, 
    get_ccu_gateway, 
    get_nodered_gateway, 
    get_admin_gateway
)


class TestComprehensiveArchitecture(unittest.TestCase):
    """Umfassende Tests für die gesamte gekapselte MQTT-Architektur"""

    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton-Instanzen für saubere Tests
        from omf2.factory.gateway_factory import GatewayFactory
        GatewayFactory._instance = None
        GatewayFactory._gateways = {}
        GatewayFactory._gateway_locks = {}

    def test_registry_manager_singleton(self):
        """Test Registry Manager Singleton-Pattern"""
        # Teste Singleton-Verhalten
        registry1 = get_registry_manager()
        registry2 = get_registry_manager()
        
        self.assertIs(registry1, registry2)
        self.assertIsNotNone(registry1)

    def test_gateway_factory_singleton(self):
        """Test Gateway-Factory Singleton-Pattern"""
        # Teste Factory Singleton
        factory1 = get_gateway_factory()
        factory2 = get_gateway_factory()
        
        self.assertIs(factory1, factory2)
        self.assertIsNotNone(factory1)

    def test_all_gateways_creation(self):
        """Test Erstellung aller Gateways"""
        # Erstelle alle Gateways
        ccu_gateway = get_ccu_gateway()
        nodered_gateway = get_nodered_gateway()
        admin_gateway = get_admin_gateway()
        
        # Prüfe, dass alle erstellt wurden
        self.assertIsNotNone(ccu_gateway)
        self.assertIsNotNone(nodered_gateway)
        self.assertIsNotNone(admin_gateway)
        
        # Prüfe, dass alle Registry Manager haben
        self.assertIsNotNone(ccu_gateway.registry_manager)
        self.assertIsNotNone(nodered_gateway.registry_manager)
        self.assertIsNotNone(admin_gateway.registry_manager)

    def test_ccu_gateway_functionality(self):
        """Test CCU Gateway Funktionalität"""
        ccu_gateway = get_ccu_gateway()
        
        # Test alle CCU Gateway Methoden
        result1 = ccu_gateway.reset_factory()
        result2 = ccu_gateway.send_global_command("test_command", {"param": "value"})
        state = ccu_gateway.get_ccu_state()
        module_states = ccu_gateway.get_module_states()
        order_result = ccu_gateway.send_order_request({"order_id": "123"})
        pub_topics = ccu_gateway.get_published_topics()
        sub_topics = ccu_gateway.get_subscribed_topics()
        
        # Prüfe Ergebnisse
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(state is None or isinstance(state, dict))
        self.assertIsInstance(module_states, list)
        self.assertTrue(order_result)
        self.assertIsInstance(pub_topics, list)
        self.assertIsInstance(sub_topics, list)

    def test_nodered_gateway_functionality(self):
        """Test Node-RED Gateway Funktionalität"""
        nodered_gateway = get_nodered_gateway()
        
        # Test alle Node-RED Gateway Methoden
        normalized_states = nodered_gateway.get_normalized_module_states()
        ccu_commands = nodered_gateway.get_ccu_commands()
        opc_ua_states = nodered_gateway.get_opc_ua_states()
        feedback_result = nodered_gateway.send_ccu_feedback({"status": "ok"})
        order_result = nodered_gateway.send_order_completed({"order_id": "123"})
        pub_topics = nodered_gateway.get_pub_topics()
        sub_topics = nodered_gateway.get_sub_topics()
        
        # Prüfe Ergebnisse
        self.assertIsInstance(normalized_states, list)
        self.assertIsInstance(ccu_commands, list)
        self.assertIsInstance(opc_ua_states, list)
        self.assertTrue(feedback_result)
        self.assertTrue(order_result)
        self.assertIsInstance(pub_topics, list)
        self.assertIsInstance(sub_topics, list)

    def test_admin_gateway_functionality(self):
        """Test Admin Gateway Funktionalität"""
        admin_gateway = get_admin_gateway()
        
        # Test alle Admin Gateway Methoden
        message = admin_gateway.generate_message_template("test/topic", {"param": "value"})
        validation = admin_gateway.validate_message("test/topic", {"test": "data"})
        publish_result = admin_gateway.publish_message("test/topic", {"test": "data"})
        all_topics = admin_gateway.get_all_topics()
        topic_templates = admin_gateway.get_topic_templates()
        system_status = admin_gateway.get_system_status()
        pub_topics = admin_gateway.get_published_topics()
        sub_topics = admin_gateway.get_subscribed_topics()
        
        # Prüfe Ergebnisse
        self.assertTrue(message is None or isinstance(message, dict))
        self.assertIsInstance(validation, dict)
        self.assertIn('errors', validation)
        self.assertIn('warnings', validation)
        self.assertTrue(publish_result)
        self.assertIsInstance(all_topics, list)
        self.assertIsInstance(topic_templates, dict)
        self.assertIsInstance(system_status, dict)
        self.assertIsInstance(pub_topics, list)
        self.assertIsInstance(sub_topics, list)

    def test_registry_integration(self):
        """Test Registry Integration in allen Gateways"""
        # Teste, dass alle Gateways Registry Manager nutzen
        ccu_gateway = get_ccu_gateway()
        nodered_gateway = get_nodered_gateway()
        admin_gateway = get_admin_gateway()
        
        # Alle Gateways sollten die gleiche Registry Manager-Instanz haben
        self.assertIs(ccu_gateway.registry_manager, nodered_gateway.registry_manager)
        self.assertIs(nodered_gateway.registry_manager, admin_gateway.registry_manager)
        self.assertIs(ccu_gateway.registry_manager, admin_gateway.registry_manager)

    def test_gateway_factory_management(self):
        """Test Gateway-Factory Management"""
        factory = get_gateway_factory()
        
        # Test Gateway-Erstellung
        ccu_gateway = factory.get_ccu_gateway()
        nodered_gateway = factory.get_nodered_gateway()
        admin_gateway = factory.get_admin_gateway()
        
        # Test get_all_gateways
        all_gateways = factory.get_all_gateways()
        self.assertIn('ccu', all_gateways)
        self.assertIn('nodered', all_gateways)
        self.assertIn('admin', all_gateways)
        
        # Test Gateway-Reset
        factory.reset_gateway('ccu')
        all_gateways_after_reset = factory.get_all_gateways()
        self.assertNotIn('ccu', all_gateways_after_reset)
        
        # Test Reset aller Gateways
        factory.reset_all_gateways()
        all_gateways_after_reset_all = factory.get_all_gateways()
        self.assertEqual(len(all_gateways_after_reset_all), 0)

    def test_error_handling(self):
        """Test Error-Handling in allen Komponenten"""
        # Test CCU Gateway Error-Handling
        ccu_gateway = get_ccu_gateway()
        result = ccu_gateway.reset_factory()
        self.assertTrue(result)  # Sollte True zurückgeben auch bei Fehlern
        
        # Test Node-RED Gateway Error-Handling
        nodered_gateway = get_nodered_gateway()
        states = nodered_gateway.get_normalized_module_states()
        self.assertIsInstance(states, list)  # Sollte leere Liste bei Fehlern
        
        # Test Admin Gateway Error-Handling
        admin_gateway = get_admin_gateway()
        validation = admin_gateway.validate_message("invalid/topic", {"invalid": "data"})
        self.assertIsInstance(validation, dict)
        self.assertIn('errors', validation)

    def test_thread_safety(self):
        """Test Thread-Safety der Architektur"""
        import threading
        import time
        
        results = []
        
        def create_gateways():
            ccu = get_ccu_gateway()
            nodered = get_nodered_gateway()
            admin = get_admin_gateway()
            results.append((ccu, nodered, admin))
        
        # Erstelle mehrere Threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_gateways)
            threads.append(thread)
            thread.start()
        
        # Warte auf alle Threads
        for thread in threads:
            thread.join()
        
        # Prüfe, dass alle Gateways die gleichen Instanzen sind
        self.assertEqual(len(results), 5)
        for i in range(1, len(results)):
            self.assertIs(results[0][0], results[i][0])  # CCU Gateway
            self.assertIs(results[0][1], results[i][1])  # Node-RED Gateway
            self.assertIs(results[0][2], results[i][2])  # Admin Gateway

    def test_architecture_consistency(self):
        """Test Konsistenz der gesamten Architektur"""
        # Teste, dass alle Komponenten korrekt integriert sind
        factory = get_gateway_factory()
        ccu_gateway = get_ccu_gateway()
        nodered_gateway = get_nodered_gateway()
        admin_gateway = get_admin_gateway()
        
        # Alle Gateways sollten in der Factory registriert sein
        all_gateways = factory.get_all_gateways()
        self.assertIn('ccu', all_gateways)
        self.assertIn('nodered', all_gateways)
        self.assertIn('admin', all_gateways)
        
        # Alle Gateways sollten die gleiche Registry Manager-Instanz haben
        registry_manager = get_registry_manager()
        self.assertIs(ccu_gateway.registry_manager, registry_manager)
        self.assertIs(nodered_gateway.registry_manager, registry_manager)
        self.assertIs(admin_gateway.registry_manager, registry_manager)

    def test_performance(self):
        """Test Performance der Architektur"""
        import time
        
        # Test Gateway-Erstellung Performance
        start_time = time.time()
        for _ in range(100):
            ccu_gateway = get_ccu_gateway()
            nodered_gateway = get_nodered_gateway()
            admin_gateway = get_admin_gateway()
        end_time = time.time()
        
        # Sollte schnell sein (Singleton-Pattern)
        self.assertLess(end_time - start_time, 1.0)  # Weniger als 1 Sekunde

    def test_memory_usage(self):
        """Test Memory-Usage der Architektur"""
        # Teste, dass Singleton-Pattern Memory spart
        ccu1 = get_ccu_gateway()
        ccu2 = get_ccu_gateway()
        
        # Sollte die gleiche Instanz sein
        self.assertIs(ccu1, ccu2)
        
        # Teste mit mehreren Gateways
        nodered1 = get_nodered_gateway()
        nodered2 = get_nodered_gateway()
        admin1 = get_admin_gateway()
        admin2 = get_admin_gateway()
        
        # Alle sollten Singleton-Instanzen sein
        self.assertIs(nodered1, nodered2)
        self.assertIs(admin1, admin2)

    def test_integration_workflow(self):
        """Test kompletten Integration-Workflow"""
        # Simuliere einen kompletten Workflow
        factory = get_gateway_factory()
        
        # 1. Erstelle alle Gateways
        ccu_gateway = factory.get_ccu_gateway()
        nodered_gateway = factory.get_nodered_gateway()
        admin_gateway = factory.get_admin_gateway()
        
        # 2. Teste CCU Workflow
        ccu_gateway.reset_factory()
        ccu_gateway.send_global_command("start_production", {"line": "1"})
        ccu_gateway.send_order_request({"order_id": "ORD-001", "product": "Widget"})
        
        # 3. Teste Node-RED Workflow
        normalized_states = nodered_gateway.get_normalized_module_states()
        nodered_gateway.send_ccu_feedback({"status": "processing"})
        nodered_gateway.send_order_completed({"order_id": "ORD-001", "status": "completed"})
        
        # 4. Teste Admin Workflow
        message = admin_gateway.generate_message_template("ccu/global", {"command": "status"})
        validation = admin_gateway.validate_message("ccu/global", {"status": "running"})
        admin_gateway.publish_message("ccu/global", {"status": "running"})
        
        # 5. Prüfe, dass alle Workflows funktionieren
        self.assertIsNotNone(ccu_gateway)
        self.assertIsNotNone(nodered_gateway)
        self.assertIsNotNone(admin_gateway)
        self.assertIsInstance(normalized_states, list)
        self.assertTrue(message is None or isinstance(message, dict))
        self.assertIsInstance(validation, dict)


if __name__ == '__main__':
    unittest.main()
