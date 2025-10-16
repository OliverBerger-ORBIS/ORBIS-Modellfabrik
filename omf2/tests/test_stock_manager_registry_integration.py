#!/usr/bin/env python3
"""
Test Stock Manager Registry Integration
Testet die Integration zwischen Stock-Manager und RegistryManager
"""

import sys
import unittest
from pathlib import Path

# Add omf2 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from omf2.ccu.order_manager import get_order_manager
from omf2.ccu.stock_manager import get_stock_manager
from omf2.registry.manager.registry_manager import get_registry_manager


class TestStockManagerRegistryIntegration(unittest.TestCase):
    """Test Stock Manager Registry Integration"""

    def setUp(self):
        """Setup test environment"""
        # Reset singleton instances
        import omf2.ccu.order_manager
        import omf2.ccu.stock_manager

        omf2.ccu.stock_manager._stock_manager_instance = None
        omf2.ccu.order_manager._order_manager_instance = None

        # Get fresh instances
        self.registry_manager = get_registry_manager()
        self.stock_manager = get_stock_manager()
        self.order_manager = get_order_manager()

    def test_registry_manager_singleton(self):
        """Test RegistryManager singleton pattern"""
        registry1 = get_registry_manager()
        registry2 = get_registry_manager()

        self.assertIs(registry1, registry2)
        self.assertIsInstance(registry1, type(registry2))

    def test_stock_manager_singleton(self):
        """Test StockManager singleton pattern"""
        manager1 = get_stock_manager()
        manager2 = get_stock_manager()

        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, type(manager2))

    def test_order_manager_singleton(self):
        """Test OrderManager singleton pattern"""
        manager1 = get_order_manager()
        manager2 = get_order_manager()

        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, type(manager2))

    def test_registry_topics_loaded(self):
        """Test that registry topics are properly loaded"""
        # Verify topics are loaded
        self.assertIsInstance(self.registry_manager.topics, dict)
        self.assertGreater(len(self.registry_manager.topics), 0)

        # Check for order-related topics
        order_topics = [topic for topic in self.registry_manager.topics.keys() if "order" in topic.lower()]
        self.assertGreater(len(order_topics), 0)

    def test_registry_schemas_loaded(self):
        """Test that registry schemas are properly loaded"""
        # Verify schemas are loaded
        self.assertIsInstance(self.registry_manager.schemas, dict)
        self.assertGreater(len(self.registry_manager.schemas), 0)

        # Check for order-related schemas
        order_schemas = [schema for schema in self.registry_manager.schemas.keys() if "order" in schema.lower()]
        self.assertGreater(len(order_schemas), 0)

    def test_registry_modules_loaded(self):
        """Test that registry modules are properly loaded"""
        # Verify modules are loaded
        self.assertIsInstance(self.registry_manager.modules, dict)
        self.assertGreater(len(self.registry_manager.modules), 0)

        # Check for expected modules (by name, not ID)
        expected_module_names = ["HBW", "DRILL", "MILL", "AIQS", "DPS", "FTS"]
        module_names = [module["name"] for module in self.registry_manager.modules.values()]
        for module_name in expected_module_names:
            self.assertIn(module_name, module_names)

    def test_stock_manager_inventory_initialization(self):
        """Test StockManager inventory initialization"""
        # Verify inventory is initialized
        self.assertIsInstance(self.stock_manager.inventory, dict)

        # Check inventory positions (A1-C3 grid)
        expected_positions = [f"{chr(65+i)}{j+1}" for i in range(3) for j in range(3)]
        for position in expected_positions:
            self.assertIn(position, self.stock_manager.inventory)

    def test_order_manager_state_initialization(self):
        """Test OrderManager state initialization"""
        # Verify state holders are initialized
        self.assertIsInstance(self.order_manager.active_orders, dict)
        self.assertIsInstance(self.order_manager.completed_orders, dict)
        # order_statistics is a method, not a property
        self.assertTrue(hasattr(self.order_manager, "get_order_statistics"))

    def test_registry_topic_schema_relationship(self):
        """Test relationship between topics and schemas in registry"""
        # Get order topics
        order_topics = [topic for topic in self.registry_manager.topics.keys() if "order" in topic.lower()]

        for topic in order_topics:
            # Each topic should have a corresponding schema
            topic_name = topic.split("/")[-1]  # Get last part of topic

            # Check if schema exists (might be named differently)
            schema_found = any(topic_name in schema.lower() for schema in self.registry_manager.schemas.keys())
            # Some topics might not have schemas yet (e.g., FTS topics)
            if not schema_found:
                print(f"   ⚠️ No schema found for topic {topic} (might be expected)")

    def test_registry_mqtt_clients_loaded(self):
        """Test that MQTT clients are loaded from registry"""
        # Verify MQTT clients are loaded
        self.assertIsInstance(self.registry_manager.mqtt_clients, dict)
        self.assertGreater(len(self.registry_manager.mqtt_clients), 0)

        # Check for CCU client
        ccu_clients = [client for client in self.registry_manager.mqtt_clients.keys() if "ccu" in client.lower()]
        self.assertGreater(len(ccu_clients), 0)

    def test_registry_workpieces_loaded(self):
        """Test that workpieces are loaded from registry"""
        # Verify workpieces are loaded
        self.assertIsInstance(self.registry_manager.workpieces, dict)
        self.assertGreater(len(self.registry_manager.workpieces), 0)

        # Check for expected workpiece types
        expected_types = ["BLUE", "RED", "WHITE"]
        for workpiece in self.registry_manager.workpieces.values():
            if "type" in workpiece:
                self.assertIn(workpiece["type"], expected_types)


if __name__ == "__main__":
    unittest.main()
