#!/usr/bin/env python3
"""
Test für OMF MQTT Client
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import unittest
from unittest.mock import Mock, patch

from src_orbis.omf.tools.mqtt_client import OMFMQTTClient, get_omf_mqtt_client


class TestOMFMQTTClient(unittest.TestCase):
    """Test-Klasse für OMF MQTT Client"""

    def setUp(self):
        """Setup für Tests"""
        self.mqtt_client = get_omf_mqtt_client()

    def test_singleton(self):
        """Test Singleton-Pattern"""
        client1 = get_omf_mqtt_client()
        client2 = get_omf_mqtt_client()
        self.assertIs(client1, client2)

    def test_load_config(self):
        """Test Konfiguration laden"""
        self.assertIsNotNone(self.mqtt_client.config)
        self.assertIn("broker", self.mqtt_client.config)
        self.assertIn("subscriptions", self.mqtt_client.config)
        self.assertIn("connection", self.mqtt_client.config)

    def test_client_initialization(self):
        """Test Client-Initialisierung"""
        self.assertIsNotNone(self.mqtt_client.client)
        self.assertFalse(self.mqtt_client.connected)
        self.assertIsNotNone(self.mqtt_client.message_queue)
        self.assertIsInstance(self.mqtt_client.message_handlers, dict)

    def test_get_statistics(self):
        """Test Statistiken abrufen"""
        stats = self.mqtt_client.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("messages_received", stats)
        self.assertIn("messages_sent", stats)
        self.assertIn("connection_attempts", stats)
        self.assertIn("connected", stats)
        self.assertIn("queue_size", stats)
        self.assertIn("handlers_count", stats)
        self.assertIn("history_size", stats)

        # Prüfe Initialwerte
        self.assertEqual(stats["messages_received"], 0)
        self.assertEqual(stats["messages_sent"], 0)
        self.assertEqual(stats["connection_attempts"], 0)
        self.assertFalse(stats["connected"])

    def test_is_connected(self):
        """Test Verbindungsstatus"""
        # Initial sollte nicht verbunden sein
        self.assertFalse(self.mqtt_client.is_connected())

        # Simuliere Verbindung
        self.mqtt_client.connected = True
        self.assertTrue(self.mqtt_client.is_connected())

        # Reset
        self.mqtt_client.connected = False

    def test_add_message_handler(self):
        """Test Message Handler hinzufügen"""
        topic = "test/topic"
        handler = Mock()

        # Handler hinzufügen
        self.mqtt_client.add_message_handler(topic, handler)

        # Prüfe dass Handler hinzugefügt wurde
        self.assertIn(topic, self.mqtt_client.message_handlers)
        self.assertIn(handler, self.mqtt_client.message_handlers[topic])

        # Prüfe Statistiken
        stats = self.mqtt_client.get_statistics()
        self.assertEqual(stats["handlers_count"], 1)

    def test_remove_message_handler(self):
        """Test Message Handler entfernen"""
        topic = "test/topic"
        handler = Mock()

        # Handler hinzufügen
        self.mqtt_client.add_message_handler(topic, handler)

        # Handler entfernen
        self.mqtt_client.remove_message_handler(topic, handler)

        # Prüfe dass Handler entfernt wurde
        self.assertNotIn(handler, self.mqtt_client.message_handlers[topic])

        # Prüfe Statistiken
        stats = self.mqtt_client.get_statistics()
        self.assertEqual(stats["handlers_count"], 1)  # Topic ist noch da, aber leer

    def test_get_message(self):
        """Test Message aus Queue abrufen"""
        # Queue ist initial leer
        message = self.mqtt_client.get_message(timeout=0.1)
        self.assertIsNone(message)

    def test_get_message_history(self):
        """Test Message History abrufen"""
        history = self.mqtt_client.get_message_history()
        self.assertIsInstance(history, list)
        self.assertEqual(len(history), 0)

        # Test mit Limit
        history_limited = self.mqtt_client.get_message_history(limit=10)
        self.assertIsInstance(history_limited, list)
        self.assertEqual(len(history_limited), 0)

    @patch("paho.mqtt.client.Client")
    def test_connect_failure(self, mock_client_class):
        """Test Verbindungsfehler"""
        # Mock Client für Verbindungsfehler
        mock_client = Mock()
        mock_client.connect.return_value = 1  # Fehler
        mock_client_class.return_value = mock_client

        # Erstelle neuen Client für Test
        test_client = OMFMQTTClient()

        # Teste Verbindung
        result = test_client.connect()
        self.assertFalse(result)
        self.assertFalse(test_client.connected)

    def test_topic_matches_pattern(self):
        """Test Topic Pattern Matching"""
        # Exakte Übereinstimmung
        self.assertTrue(self.mqtt_client._topic_matches_pattern("test/topic", "test/topic"))

        # Wildcard +
        self.assertTrue(self.mqtt_client._topic_matches_pattern("test/123/topic", "test/+/topic"))
        self.assertFalse(self.mqtt_client._topic_matches_pattern("test/123/topic", "test/+/other"))

        # Wildcard #
        self.assertTrue(self.mqtt_client._topic_matches_pattern("test/123/topic", "test/#"))
        self.assertTrue(self.mqtt_client._topic_matches_pattern("test/123/456/topic", "test/#"))

        # Keine Übereinstimmung
        self.assertFalse(self.mqtt_client._topic_matches_pattern("test/topic", "other/topic"))

    def test_publish_not_connected(self):
        """Test Publish ohne Verbindung"""
        # Sollte False zurückgeben wenn nicht verbunden
        result = self.mqtt_client.publish("test/topic", "test message")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
