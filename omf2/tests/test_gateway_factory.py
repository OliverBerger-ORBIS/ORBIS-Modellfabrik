"""
Tests für Gateway-Factory

Testet die Gateway-Factory Singleton-Pattern, Gateway-Erstellung
und alle Factory-Methoden.
"""

import unittest
from unittest.mock import patch, MagicMock
import threading
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from omf2.factory.gateway_factory import (
    GatewayFactory, 
    get_gateway_factory,
    get_ccu_gateway,
    get_nodered_gateway,
    get_admin_gateway,
    get_gateway
)


class TestGatewayFactory(unittest.TestCase):
    """Tests für GatewayFactory Singleton und Factory-Methoden"""

    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton-Instanzen
        GatewayFactory._instance = None
        GatewayFactory._gateways = {}
        GatewayFactory._gateway_locks = {}

    def test_singleton_pattern(self):
        """Test Singleton-Pattern für GatewayFactory"""
        factory1 = GatewayFactory()
        factory2 = GatewayFactory()
        
        self.assertIs(factory1, factory2)
        self.assertIsNotNone(factory1)

    def test_factory_function_singleton(self):
        """Test Factory-Funktion für Singleton"""
        factory1 = get_gateway_factory()
        factory2 = get_gateway_factory()
        
        self.assertIs(factory1, factory2)
        self.assertIsInstance(factory1, GatewayFactory)

    def test_get_ccu_gateway(self):
        """Test CcuGateway Erstellung"""
        # Teste, dass Gateway erstellt wird
        gateway = get_ccu_gateway()
        
        self.assertIsNotNone(gateway)
        self.assertIsInstance(gateway, object)  # Gateway ist ein Objekt

    def test_get_nodered_gateway(self):
        """Test NoderedGateway Erstellung"""
        # Teste, dass Gateway erstellt wird
        gateway = get_nodered_gateway()
        
        self.assertIsNotNone(gateway)
        self.assertIsInstance(gateway, object)  # Gateway ist ein Objekt

    def test_get_admin_gateway(self):
        """Test AdminGateway Erstellung"""
        # Teste, dass Gateway erstellt wird
        gateway = get_admin_gateway()
        
        self.assertIsNotNone(gateway)
        self.assertIsInstance(gateway, object)  # Gateway ist ein Objekt

    def test_get_gateway_generic(self):
        """Test generische Gateway-Erstellung"""
        # Teste, dass Gateway erstellt wird
        gateway = get_gateway('ccu')
        
        self.assertIsNotNone(gateway)
        self.assertIsInstance(gateway, object)  # Gateway ist ein Objekt

    def test_get_gateway_unknown_domain(self):
        """Test Gateway-Erstellung für unbekannte Domäne"""
        with self.assertRaises(ValueError):
            get_gateway('unknown_domain')

    def test_get_all_gateways(self):
        """Test Abrufen aller Gateways"""
        # Erstelle Gateway
        get_ccu_gateway()
        
        # Teste get_all_gateways
        factory = get_gateway_factory()
        all_gateways = factory.get_all_gateways()
        
        self.assertIn('ccu', all_gateways)
        self.assertIsNotNone(all_gateways['ccu'])

    def test_reset_gateway(self):
        """Test Gateway-Reset"""
        # Erstelle Gateway
        get_ccu_gateway()
        
        # Reset Gateway
        factory = get_gateway_factory()
        factory.reset_gateway('ccu')
        
        # Prüfe, dass Gateway entfernt wurde
        all_gateways = factory.get_all_gateways()
        self.assertNotIn('ccu', all_gateways)

    def test_reset_all_gateways(self):
        """Test Reset aller Gateways"""
        # Erstelle Gateway
        get_ccu_gateway()
        
        # Reset alle Gateways
        factory = get_gateway_factory()
        factory.reset_all_gateways()
        
        # Prüfe, dass alle Gateways entfernt wurden
        all_gateways = factory.get_all_gateways()
        self.assertEqual(len(all_gateways), 0)

    def test_thread_safety(self):
        """Test Thread-Safety der Factory"""
        results = []
        
        def create_gateway():
            gateway = get_ccu_gateway()
            results.append(gateway)
        
        # Erstelle mehrere Threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_gateway)
            threads.append(thread)
            thread.start()
        
        # Warte auf alle Threads
        for thread in threads:
            thread.join()
        
        # Alle Gateways sollten die gleiche Instanz sein
        self.assertEqual(len(results), 5)
        for gateway in results:
            self.assertIs(results[0], gateway)

    def test_gateway_creation_with_kwargs(self):
        """Test Gateway-Erstellung mit Parametern"""
        # Erstelle Gateway mit Parametern
        gateway = get_ccu_gateway(test_param="test_value")
        
        self.assertIsNotNone(gateway)
        self.assertIsInstance(gateway, object)  # Gateway ist ein Objekt

    def test_multiple_domains(self):
        """Test Erstellung mehrerer Domänen-Gateways"""
        # Erstelle alle Gateways
        ccu_gateway = get_ccu_gateway()
        nodered_gateway = get_nodered_gateway()
        admin_gateway = get_admin_gateway()
        
        # Prüfe, dass alle erstellt wurden
        self.assertIsNotNone(ccu_gateway)
        self.assertIsNotNone(nodered_gateway)
        self.assertIsNotNone(admin_gateway)
        
        # Prüfe, dass alle in Factory registriert sind
        factory = get_gateway_factory()
        all_gateways = factory.get_all_gateways()
        
        self.assertIn('ccu', all_gateways)
        self.assertIn('nodered', all_gateways)
        self.assertIn('admin', all_gateways)

    def test_gateway_reuse(self):
        """Test Wiederverwendung von Gateways"""
        # Erstelle Gateway zweimal
        gateway1 = get_ccu_gateway()
        gateway2 = get_ccu_gateway()
        
        # Sollte die gleiche Instanz sein
        self.assertIs(gateway1, gateway2)


if __name__ == '__main__':
    unittest.main()
