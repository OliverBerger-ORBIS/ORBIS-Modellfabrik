#!/usr/bin/env python3
"""
Tests für Admin MQTT Client
"""

import os
import sys
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from omf2.admin.admin_mqtt_client import AdminMqttClient, get_admin_mqtt_client


class TestAdminMqttClient(unittest.TestCase):
    """Tests für Admin MQTT Client"""

    def setUp(self):
        """Setup für jeden Test"""
        # Reset singleton instance
        AdminMqttClient._instance = None
        AdminMqttClient._initialized = False

    def test_singleton_pattern(self):
        """Test Singleton-Pattern"""
        client1 = get_admin_mqtt_client()
        client2 = get_admin_mqtt_client()

        self.assertIs(client1, client2)
        self.assertIsInstance(client1, AdminMqttClient)

    def test_initialization(self):
        """Test Initialisierung"""
        client = get_admin_mqtt_client()

        self.assertIsNotNone(client.registry_manager)
        self.assertEqual(client.client_id, "omf_admin")
        self.assertFalse(client.connected)
        self.assertIsNone(client.client)

    def test_mock_connection(self):
        """Test Mock-Verbindung"""
        client = get_admin_mqtt_client()

        result = client.connect("mock")

        self.assertTrue(result)
        self.assertTrue(client.connected)

    @patch("omf2.admin.admin_mqtt_client.MQTT_AVAILABLE", True)
    @patch("omf2.admin.admin_mqtt_client.mqtt")
    def test_real_connection_mock(self, mock_mqtt):
        """Test echte MQTT-Verbindung (gemockt)"""
        # Mock MQTT Client
        mock_client = MagicMock()
        mock_mqtt.Client.return_value = mock_client

        client = get_admin_mqtt_client()

        # Test live environment
        client.connect("live")

        # Should attempt real connection
        mock_mqtt.Client.assert_called_once()
        # New behavior: uses connect_async instead of connect
        mock_client.connect_async.assert_called_once()
        mock_client.loop_start.assert_called_once()

    def test_publish_message_mock(self):
        """Test Message Publishing (Mock)"""
        client = get_admin_mqtt_client()
        client.connect("mock")

        result = client.publish_message("test/topic", {"test": "message"})

        self.assertTrue(result)

    def test_subscribe_to_all_mock(self):
        """Test Subscribe to All (Mock)"""
        client = get_admin_mqtt_client()
        client.connect("mock")

        result = client.subscribe_to_all()

        self.assertTrue(result)

    def test_get_buffer(self):
        """Test Buffer-Zugriff"""
        client = get_admin_mqtt_client()

        # Test empty buffer
        result = client.get_buffer("nonexistent/topic")
        self.assertIsNone(result)

        # Test with data - Mock the buffer
        from collections import deque

        mock_buffer = deque([{"test": "data"}], maxlen=1000)
        with patch.object(client, "topic_buffers", {"test/topic": mock_buffer}):
            result = client.get_buffer("test/topic")
            self.assertEqual(result, {"test": "data"})

    def test_get_all_buffers(self):
        """Test Alle Buffer abrufen"""
        client = get_admin_mqtt_client()

        # Test empty buffers
        result = client.get_all_buffers()
        self.assertEqual(result, {})

        # Test with data
        client.topic_buffers["test/topic"] = {"test": "data"}
        result = client.get_all_buffers()
        self.assertEqual(result, {"test/topic": {"test": "data"}})

    def test_get_system_overview(self):
        """Test System Overview"""
        client = get_admin_mqtt_client()
        client.connect("mock")

        overview = client.get_system_overview()

        self.assertIn("total_topics", overview)
        self.assertIn("active_topics", overview)
        self.assertIn("mqtt_connected", overview)
        self.assertIn("client_id", overview)
        self.assertTrue(overview["mqtt_connected"])

    def test_thread_safety(self):
        """Test Thread-Sicherheit"""
        client = get_admin_mqtt_client()
        results = []

        def worker():
            for i in range(10):
                client.publish_message(f"test/topic/{i}", {"data": i})
                results.append(i)

        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should have 50 results (5 threads * 10 iterations)
        self.assertEqual(len(results), 50)

    def test_config_loading(self):
        """Test Konfiguration laden"""
        client = get_admin_mqtt_client()

        self.assertIsNotNone(client.config)
        # Test actual config structure (flat merged config)
        self.assertIn("host", client.config)
        self.assertIn("port", client.config)
        self.assertIn("client_id_postfix", client.config)

    def test_disconnect(self):
        """Test Disconnect"""
        client = get_admin_mqtt_client()
        client.connect("mock")

        self.assertTrue(client.connected)

        client.disconnect()

        # New behavior: disconnect always sets connected=False
        self.assertFalse(client.connected)

    def test_message_processing(self):
        """Test Message Processing"""
        client = get_admin_mqtt_client()

        # Simulate message processing
        test_message = {"test": "data", "timestamp": time.time()}
        from collections import deque

        mock_buffer = deque([test_message], maxlen=1000)
        with patch.object(client, "topic_buffers", {"test/topic": mock_buffer}):
            result = client.get_buffer("test/topic")
            self.assertEqual(result, test_message)

    def test_factory_function(self):
        """Test Factory-Funktion"""
        client = get_admin_mqtt_client()

        self.assertIsNotNone(client)
        self.assertIsInstance(client, AdminMqttClient)

    def test_multiple_instances_singleton(self):
        """Test dass mehrere Aufrufe dieselbe Instanz zurückgeben"""
        client1 = AdminMqttClient()
        client2 = AdminMqttClient()
        client3 = get_admin_mqtt_client()

        self.assertIs(client1, client2)
        self.assertIs(client1, client3)
        self.assertIs(client2, client3)

    def test_reconnect_environment(self):
        """Test environment reconnection"""
        client = get_admin_mqtt_client()

        # Connect to mock first
        result1 = client.connect("mock")
        self.assertTrue(result1)
        self.assertEqual(getattr(client, "_current_environment", None), "mock")

        # Reconnect to replay
        result2 = client.reconnect_environment("replay")
        self.assertTrue(result2)
        self.assertEqual(getattr(client, "_current_environment", None), "replay")

    def test_get_connection_info(self):
        """Test connection info retrieval"""
        client = get_admin_mqtt_client()
        client.connect("mock")

        conn_info = client.get_connection_info()

        self.assertIsInstance(conn_info, dict)
        self.assertIn("connected", conn_info)
        self.assertIn("environment", conn_info)
        self.assertIn("client_id", conn_info)
        self.assertIn("mock_mode", conn_info)
        self.assertTrue(conn_info["connected"])
        self.assertEqual(conn_info["environment"], "mock")
        self.assertTrue(conn_info["mock_mode"])


if __name__ == "__main__":
    unittest.main()
