#!/usr/bin/env python3
"""
Tests für UI-Komponenten (CCU, Node-RED, Admin)
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.ccu_mqtt_client import CCUMQTTClient, get_ccu_mqtt_client
from omf2.nodered.nodered_gateway import NoderedGateway
from omf2.nodered.nodered_pub_mqtt_client import NodeREDPubMQTTClient, get_nodered_pub_mqtt_client
from omf2.nodered.nodered_sub_mqtt_client import NodeREDSubMQTTClient, get_nodered_sub_mqtt_client
from omf2.admin.admin_gateway import AdminGateway
from omf2.admin.admin_mqtt_client import AdminMQTTClient, get_admin_mqtt_client


class TestCCUGateway(unittest.TestCase):
    """Test-Klasse für CCU Gateway"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        CCUMQTTClient._instance = None
        CCUMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        CCUMQTTClient._instance = None
        CCUMQTTClient._initialized = False
    
    def test_ccu_gateway_initialization(self):
        """Test: CCU Gateway Initialisierung"""
        gateway = CcuGateway()
        self.assertIsNotNone(gateway.message_templates)
        self.assertIsNone(gateway.mqtt_client)
    
    def test_reset_factory(self):
        """Test: Factory Reset"""
        gateway = CcuGateway()
        result = gateway.reset_factory()
        self.assertTrue(result)
    
    def test_send_global_command(self):
        """Test: Global Command senden"""
        gateway = CcuGateway()
        result = gateway.send_global_command("test_command", {"param": "value"})
        self.assertTrue(result)
    
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


class TestCCUMQTTClient(unittest.TestCase):
    """Test-Klasse für CCU MQTT Client"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        CCUMQTTClient._instance = None
        CCUMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        CCUMQTTClient._instance = None
        CCUMQTTClient._initialized = False
    
    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = CCUMQTTClient()
        instance2 = CCUMQTTClient()
        self.assertIs(instance1, instance2)
    
    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_ccu_mqtt_client()
        instance2 = get_ccu_mqtt_client()
        self.assertIs(instance1, instance2)
    
    def test_initialization(self):
        """Test: Initialisierung"""
        client = CCUMQTTClient()
        self.assertEqual(client.client_id, "omf_ccu")
        self.assertIsInstance(client.published_topics, list)
        self.assertIsInstance(client.subscribed_topics, list)
    
    def test_connect(self):
        """Test: Verbindung"""
        client = CCUMQTTClient()
        result = client.connect()
        self.assertTrue(result)
    
    def test_disconnect(self):
        """Test: Trennung"""
        client = CCUMQTTClient()
        client.disconnect()  # Sollte nicht fehlschlagen
    
    def test_publish(self):
        """Test: Publish"""
        client = CCUMQTTClient()
        result = client.publish("test/topic", {"test": "data"})
        self.assertTrue(result)
    
    def test_subscribe(self):
        """Test: Subscribe"""
        client = CCUMQTTClient()
        result = client.subscribe("test/topic")
        self.assertTrue(result)
    
    def test_get_buffer(self):
        """Test: Buffer abrufen"""
        client = CCUMQTTClient()
        buffer = client.get_buffer("test/topic")
        self.assertIsNone(buffer)  # Leer bei Initialisierung
    
    def test_get_all_buffers(self):
        """Test: Alle Buffers abrufen"""
        client = CCUMQTTClient()
        buffers = client.get_all_buffers()
        self.assertIsInstance(buffers, dict)


class TestNodeREDGateway(unittest.TestCase):
    """Test-Klasse für Node-RED Gateway"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singletons zurücksetzen
        NodeREDPubMQTTClient._instance = None
        NodeREDPubMQTTClient._initialized = False
        NodeREDSubMQTTClient._instance = None
        NodeREDSubMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        NodeREDPubMQTTClient._instance = None
        NodeREDPubMQTTClient._initialized = False
        NodeREDSubMQTTClient._instance = None
        NodeREDSubMQTTClient._initialized = False
    
    def test_nodered_gateway_initialization(self):
        """Test: Node-RED Gateway Initialisierung"""
        gateway = NoderedGateway()
        self.assertIsNotNone(gateway.message_templates)
        self.assertIsNone(gateway.pub_mqtt_client)
        self.assertIsNone(gateway.sub_mqtt_client)
    
    def test_get_normalized_module_states(self):
        """Test: Normalisierte Module States abrufen"""
        gateway = NoderedGateway()
        states = gateway.get_normalized_module_states()
        self.assertIsInstance(states, list)
    
    def test_get_ccu_commands(self):
        """Test: CCU Commands abrufen"""
        gateway = NoderedGateway()
        commands = gateway.get_ccu_commands()
        self.assertIsInstance(commands, list)
    
    def test_get_opc_ua_states(self):
        """Test: OPC-UA States abrufen"""
        gateway = NoderedGateway()
        states = gateway.get_opc_ua_states()
        self.assertIsInstance(states, list)
    
    def test_send_ccu_feedback(self):
        """Test: CCU Feedback senden"""
        gateway = NoderedGateway()
        feedback = {"status": "ok", "message": "test"}
        result = gateway.send_ccu_feedback(feedback)
        self.assertTrue(result)
    
    def test_send_order_completed(self):
        """Test: Order Completed senden"""
        gateway = NoderedGateway()
        order_data = {"order_id": "123", "status": "completed"}
        result = gateway.send_order_completed(order_data)
        self.assertTrue(result)
    
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


class TestNodeREDPubMQTTClient(unittest.TestCase):
    """Test-Klasse für Node-RED Publisher MQTT Client"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        NodeREDPubMQTTClient._instance = None
        NodeREDPubMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        NodeREDPubMQTTClient._instance = None
        NodeREDPubMQTTClient._initialized = False
    
    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = NodeREDPubMQTTClient()
        instance2 = NodeREDPubMQTTClient()
        self.assertIs(instance1, instance2)
    
    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_nodered_pub_mqtt_client()
        instance2 = get_nodered_pub_mqtt_client()
        self.assertIs(instance1, instance2)
    
    def test_initialization(self):
        """Test: Initialisierung"""
        client = NodeREDPubMQTTClient()
        self.assertEqual(client.client_id, "omf_nodered_pub")
        self.assertIsInstance(client.published_topics, list)
        self.assertEqual(client.subscribed_topics, [])  # Publisher ist nie Subscriber
    
    def test_publish_normalized_state(self):
        """Test: Normalisierten State publizieren"""
        client = NodeREDPubMQTTClient()
        result = client.publish_normalized_state("SVR3QA0022", {"state": "idle"})
        self.assertTrue(result)
    
    def test_publish_ccu_feedback(self):
        """Test: CCU Feedback publizieren"""
        client = NodeREDPubMQTTClient()
        feedback = {"status": "ok"}
        result = client.publish_ccu_feedback(feedback)
        self.assertTrue(result)
    
    def test_publish_order_completed(self):
        """Test: Order Completed publizieren"""
        client = NodeREDPubMQTTClient()
        order_data = {"order_id": "123"}
        result = client.publish_order_completed(order_data)
        self.assertTrue(result)


class TestNodeREDSubMQTTClient(unittest.TestCase):
    """Test-Klasse für Node-RED Subscriber MQTT Client"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        NodeREDSubMQTTClient._instance = None
        NodeREDSubMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        NodeREDSubMQTTClient._instance = None
        NodeREDSubMQTTClient._initialized = False
    
    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = NodeREDSubMQTTClient()
        instance2 = NodeREDSubMQTTClient()
        self.assertIs(instance1, instance2)
    
    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_nodered_sub_mqtt_client()
        instance2 = get_nodered_sub_mqtt_client()
        self.assertIs(instance1, instance2)
    
    def test_initialization(self):
        """Test: Initialisierung"""
        client = NodeREDSubMQTTClient()
        self.assertEqual(client.client_id, "omf_nodered_sub")
        self.assertIsInstance(client.subscribed_topics, list)
        self.assertEqual(client.published_topics, [])  # Subscriber ist nie Publisher
    
    def test_subscribe_to_ccu_commands(self):
        """Test: CCU Commands subscriben"""
        client = NodeREDSubMQTTClient()
        result = client.subscribe_to_ccu_commands()
        self.assertTrue(result)
    
    def test_subscribe_to_opc_ua_states(self):
        """Test: OPC-UA States subscriben"""
        client = NodeREDSubMQTTClient()
        result = client.subscribe_to_opc_ua_states()
        self.assertTrue(result)
    
    def test_subscribe_to_txt_commands(self):
        """Test: TXT Commands subscriben"""
        client = NodeREDSubMQTTClient()
        result = client.subscribe_to_txt_commands()
        self.assertTrue(result)
    
    def test_get_ccu_command_buffers(self):
        """Test: CCU Command Buffers abrufen"""
        client = NodeREDSubMQTTClient()
        buffers = client.get_ccu_command_buffers()
        self.assertIsInstance(buffers, dict)
    
    def test_get_opc_ua_state_buffers(self):
        """Test: OPC-UA State Buffers abrufen"""
        client = NodeREDSubMQTTClient()
        buffers = client.get_opc_ua_state_buffers()
        self.assertIsInstance(buffers, dict)


class TestAdminGateway(unittest.TestCase):
    """Test-Klasse für Admin Gateway"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        AdminMQTTClient._instance = None
        AdminMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        AdminMQTTClient._instance = None
        AdminMQTTClient._initialized = False
    
    def test_admin_gateway_initialization(self):
        """Test: Admin Gateway Initialisierung"""
        gateway = AdminGateway()
        self.assertIsNotNone(gateway.message_templates)
        self.assertIsNone(gateway.mqtt_client)
    
    def test_generate_message_template(self):
        """Test: Message Template generieren"""
        gateway = AdminGateway()
        template = gateway.generate_message_template("test/topic", {"param": "value"})
        # Kann None sein wenn Template nicht gefunden
        self.assertTrue(template is None or isinstance(template, dict))
    
    def test_validate_message(self):
        """Test: Message validieren"""
        gateway = AdminGateway()
        result = gateway.validate_message("test/topic", {"test": "data"})
        self.assertIsInstance(result, dict)
        self.assertIn("errors", result)
        self.assertIn("warnings", result)
    
    def test_publish_message(self):
        """Test: Message publizieren"""
        gateway = AdminGateway()
        result = gateway.publish_message("test/topic", {"test": "data"})
        self.assertTrue(result)
    
    def test_get_all_topics(self):
        """Test: Alle Topics abrufen"""
        gateway = AdminGateway()
        topics = gateway.get_all_topics()
        self.assertIsInstance(topics, list)
    
    def test_get_topic_templates(self):
        """Test: Topic Templates abrufen"""
        gateway = AdminGateway()
        templates = gateway.get_topic_templates()
        self.assertIsInstance(templates, dict)
    
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


class TestAdminMQTTClient(unittest.TestCase):
    """Test-Klasse für Admin MQTT Client"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        AdminMQTTClient._instance = None
        AdminMQTTClient._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        AdminMQTTClient._instance = None
        AdminMQTTClient._initialized = False
    
    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        instance1 = AdminMQTTClient()
        instance2 = AdminMQTTClient()
        self.assertIs(instance1, instance2)
    
    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_admin_mqtt_client()
        instance2 = get_admin_mqtt_client()
        self.assertIs(instance1, instance2)
    
    def test_initialization(self):
        """Test: Initialisierung"""
        client = AdminMQTTClient()
        self.assertEqual(client.client_id, "omf_admin")
        self.assertIsInstance(client.published_topics, list)
        self.assertIsInstance(client.subscribed_topics, list)
    
    def test_publish_message(self):
        """Test: Message publizieren"""
        client = AdminMQTTClient()
        result = client.publish_message("test/topic", {"test": "data"})
        self.assertTrue(result)
    
    def test_subscribe_to_all(self):
        """Test: Alle Topics subscriben"""
        client = AdminMQTTClient()
        result = client.subscribe_to_all()
        self.assertTrue(result)
    
    def test_get_system_overview(self):
        """Test: System Overview abrufen"""
        client = AdminMQTTClient()
        overview = client.get_system_overview()
        self.assertIsInstance(overview, dict)
        self.assertIn("total_topics", overview)


if __name__ == '__main__':
    unittest.main()
