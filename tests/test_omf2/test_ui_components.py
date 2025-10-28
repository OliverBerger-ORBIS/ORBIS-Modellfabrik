
#!/usr/bin/env python3
"""
Tests für UI-Komponenten (CCU, Node-RED, Admin)
"""

import unittest

from omf2.admin.admin_gateway import AdminGateway
from omf2.admin.admin_mqtt_client import AdminMqttClient, get_admin_mqtt_client
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.ccu_mqtt_client import CcuMqttClient, get_ccu_mqtt_client
from omf2.nodered.nodered_gateway import NoderedGateway
from omf2.nodered.nodered_pub_mqtt_client import NoderedPubMqttClient, get_nodered_pub_mqtt_client
from omf2.nodered.nodered_sub_mqtt_client import NoderedSubMqttClient, get_nodered_sub_mqtt_client


class TestCcuGateway(unittest.TestCase):
    """Test-Klasse für CCU Gateway"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        CcuMqttClient._instance = None
        CcuMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        CcuMqttClient._instance = None
        CcuMqttClient._initialized = False

    def test_ccu_gateway_initialization(self):
        """Test: CCU Gateway Initialisierung"""
        gateway = CcuGateway()
        self.assertIsNotNone(gateway.registry_manager)
        self.assertIsNone(gateway.mqtt_client)

    def test_reset_factory(self):
        """Test: Factory Reset"""
        gateway = CcuGateway()
        result = gateway.reset_factory()
        # Should return False (no MQTT client available in test)
        self.assertFalse(result)

    def test_send_global_command(self):
        """Test: Global Command senden"""
        gateway = CcuGateway()
        result = gateway.send_global_command("test_command", {"param": "value"})
        # Should return False (no MQTT client available in test)
        self.assertFalse(result)

    def test_get_ccu_state(self):
        """Test: CCU State abrufen"""
        gateway = CcuGateway()
        state = gateway.get_ccu_state()
        self.assertIsNotNone(state)
        self.assertIn("status", state)

    def test_get_module_states(self):
        """Test: Module States abrufen"""
        gateway = CcuGateway()
        states = gateway.get_module_states()
        self.assertIsInstance(states, list)

    def test_send_order_request(self):
        """Test: Order Request senden"""
        gateway = CcuGateway()
        order_data = {"order_id": "123", "workpiece": "test"}
        result = gateway.send_order_request(order_data)
        self.assertTrue(result)

    def test_get_published_topics(self):
        """Test: Published Topics abrufen"""
        gateway = CcuGateway()
        topics = gateway.get_published_topics()
        self.assertIsInstance(topics, list)

    def test_get_subscribed_topics(self):
        """Test: Subscribed Topics abrufen"""
        gateway = CcuGateway()
        topics = gateway.get_subscribed_topics()
        self.assertIsInstance(topics, list)


class TestCcuMqttClient(unittest.TestCase):
    """Test-Klasse für CCU MQTT Client"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        CcuMqttClient._instance = None
        CcuMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        CcuMqttClient._instance = None
        CcuMqttClient._initialized = False

    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = CcuMqttClient()
        instance2 = CcuMqttClient()
        self.assertIs(instance1, instance2)

    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_ccu_mqtt_client()
        instance2 = get_ccu_mqtt_client()
        self.assertIs(instance1, instance2)

    def test_initialization(self):
        """Test: Initialisierung"""
        client = CcuMqttClient()
        self.assertEqual(client.client_id, "omf_ccu")
        self.assertIsInstance(client.published_topics, list)
        self.assertIsInstance(client.subscribed_topics, list)

    def test_connect(self):
        """Test: Verbindung"""
        client = CcuMqttClient()
        result = client.connect()
        self.assertTrue(result)

    def test_disconnect(self):
        """Test: Trennung"""
        client = CcuMqttClient()
        client.disconnect()  # Sollte nicht fehlschlagen

    def test_publish(self):
        """Test: Publish"""
        client = CcuMqttClient()
        result = client.publish("test/topic", {"test": "data"})
        self.assertTrue(result)

    def test_subscribe_many(self):
        """Test: Subscribe Many"""
        client = CcuMqttClient()
        result = client.subscribe_many(["test/topic"])
        # Should return True (mock mode works)
        self.assertTrue(result)

    def test_get_buffer(self):
        """Test: Buffer abrufen"""
        client = CcuMqttClient()
        buffer = client.get_buffer("test/topic")
        self.assertIsNone(buffer)  # Leer bei Initialisierung

    def test_get_all_buffers(self):
        """Test: Alle Buffers abrufen"""
        client = CcuMqttClient()
        buffers = client.get_all_buffers()
        self.assertIsInstance(buffers, dict)


class TestNoderedGateway(unittest.TestCase):
    """Test-Klasse für Node-RED Gateway"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singletons zurücksetzen
        NoderedPubMqttClient._instance = None
        NoderedPubMqttClient._initialized = False
        NoderedSubMqttClient._instance = None
        NoderedSubMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        NoderedPubMqttClient._instance = None
        NoderedPubMqttClient._initialized = False
        NoderedSubMqttClient._instance = None
        NoderedSubMqttClient._initialized = False

    def test_nodered_gateway_initialization(self):
        """Test: Node-RED Gateway Initialisierung"""
        gateway = NoderedGateway()
        self.assertIsNotNone(gateway.registry_manager)
        self.assertIsNone(gateway.pub_mqtt_client)
        self.assertIsNone(gateway.sub_mqtt_client)

    def test_get_pub_topics(self):
        """Test: Publisher Topics abrufen"""
        gateway = NoderedGateway()
        topics = gateway.get_pub_topics()
        self.assertIsInstance(topics, list)

    def test_get_sub_topics(self):
        """Test: Subscriber Topics abrufen"""
        gateway = NoderedGateway()
        topics = gateway.get_sub_topics()
        self.assertIsInstance(topics, list)


class TestNoderedPubMqttClient(unittest.TestCase):
    """Test-Klasse für Node-RED Publisher MQTT Client"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        NoderedPubMqttClient._instance = None
        NoderedPubMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        NoderedPubMqttClient._instance = None
        NoderedPubMqttClient._initialized = False

    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = NoderedPubMqttClient()
        instance2 = NoderedPubMqttClient()
        self.assertIs(instance1, instance2)

    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_nodered_pub_mqtt_client()
        instance2 = get_nodered_pub_mqtt_client()
        self.assertIs(instance1, instance2)

    def test_initialization(self):
        """Test: Initialisierung"""
        client = NoderedPubMqttClient()
        self.assertEqual(client.client_id, "omf_nodered_pub")
        self.assertIsInstance(client.published_topics, list)
        self.assertEqual(client.subscribed_topics, [])  # Publisher ist nie Subscriber


class TestNoderedSubMqttClient(unittest.TestCase):
    """Test-Klasse für Node-RED Subscriber MQTT Client"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        NoderedSubMqttClient._instance = None
        NoderedSubMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        NoderedSubMqttClient._instance = None
        NoderedSubMqttClient._initialized = False

    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = NoderedSubMqttClient()
        instance2 = NoderedSubMqttClient()
        self.assertIs(instance1, instance2)

    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_nodered_sub_mqtt_client()
        instance2 = get_nodered_sub_mqtt_client()
        self.assertIs(instance1, instance2)

    def test_initialization(self):
        """Test: Initialisierung"""
        client = NoderedSubMqttClient()
        self.assertEqual(client.client_id, "omf_nodered_sub")
        self.assertIsInstance(client.subscribed_topics, list)
        self.assertEqual(client.published_topics, [])  # Subscriber ist nie Publisher


class TestAdminGateway(unittest.TestCase):
    """Test-Klasse für Admin Gateway"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        AdminMqttClient._instance = None
        AdminMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        AdminMqttClient._instance = None
        AdminMqttClient._initialized = False

    def test_admin_gateway_initialization(self):
        """Test: Admin Gateway Initialisierung"""
        gateway = AdminGateway()
        self.assertIsNotNone(gateway.registry_manager)
        self.assertIsNone(gateway.mqtt_client)

    def test_generate_message(self):
        """Test: Message generieren"""
        gateway = AdminGateway()
        message = gateway.generate_message("test/topic", {"param": "value"})
        # Kann None sein wenn Message nicht gefunden
        self.assertTrue(message is None or isinstance(message, dict))

    def test_validate_message(self):
        """Test: Message validieren"""
        gateway = AdminGateway()
        result = gateway.validate_message("test/topic", {"test": "data"})
        self.assertIsInstance(result, dict)
        self.assertIn("errors", result)
        self.assertIn("warnings", result)

    def test_publish_message(self):
        """Test: Message publizieren"""
        from omf2.factory.gateway_factory import get_admin_gateway

        gateway = get_admin_gateway()
        result = gateway.publish_message("test/topic", {"test": "data"})
        self.assertTrue(result)

    def test_get_all_topics(self):
        """Test: Alle Topics abrufen"""
        gateway = AdminGateway()
        topics = gateway.get_all_topics()
        self.assertIsInstance(topics, list)

    def test_get_topic_schemas(self):
        """Test: Topic Schemas abrufen"""
        gateway = AdminGateway()
        schemas = gateway.get_topic_schemas()
        self.assertIsInstance(schemas, dict)

    def test_get_system_status(self):
        """Test: System Status abrufen"""
        gateway = AdminGateway()
        status = gateway.get_system_status()
        self.assertIsInstance(status, dict)
        self.assertIn("mqtt_connected", status)
        self.assertIn("topics_count", status)

    def test_get_published_topics(self):
        """Test: Published Topics abrufen"""
        gateway = AdminGateway()
        topics = gateway.get_published_topics()
        self.assertIsInstance(topics, list)

    def test_get_subscribed_topics(self):
        """Test: Subscribed Topics abrufen"""
        gateway = AdminGateway()
        topics = gateway.get_subscribed_topics()
        self.assertIsInstance(topics, list)


class TestAdminMqttClient(unittest.TestCase):
    """Test-Klasse für Admin MQTT Client"""

    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        AdminMqttClient._instance = None
        AdminMqttClient._initialized = False

    def tearDown(self):
        """Cleanup nach jedem Test"""
        AdminMqttClient._instance = None
        AdminMqttClient._initialized = False

    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = AdminMqttClient()
        instance2 = AdminMqttClient()
        self.assertIs(instance1, instance2)

    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_admin_mqtt_client()
        instance2 = get_admin_mqtt_client()
        self.assertIs(instance1, instance2)

    def test_initialization(self):
        """Test: Initialisierung"""
        client = AdminMqttClient()
        self.assertEqual(client.client_id, "omf_admin")
        self.assertIsInstance(client.published_topics, list)
        self.assertIsInstance(client.subscribed_topics, list)

    def test_publish_message(self):
        """Test: Message publizieren"""
        client = AdminMqttClient()
        result = client.publish_message("test/topic", {"test": "data"})
        self.assertTrue(result)

    def test_subscribe_to_all(self):
        """Test: Alle Topics subscriben"""
        client = AdminMqttClient()
        result = client.subscribe_to_all()
        self.assertTrue(result)

    def test_get_system_overview(self):
        """Test: System Overview abrufen"""
        client = AdminMqttClient()
        overview = client.get_system_overview()
        self.assertIsInstance(overview, dict)
        self.assertIn("total_topics", overview)


if __name__ == "__main__":
    unittest.main()
