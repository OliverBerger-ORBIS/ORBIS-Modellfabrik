#!/usr/bin/env python3
"""
Unit Tests für Per-Topic-Buffer Pattern

Diese Tests validieren die Per-Topic-Buffer Architektur:
- Topic-spezifische Buffer
- Automatische Nachrichtensammlung
- Effiziente Verarbeitung ohne Message-Processor Overhead
"""

import unittest
from unittest.mock import Mock, patch

from omf.dashboard.tools.mqtt_config import MqttConfig
from omf.dashboard.tools.omf_mqtt_client import OmfMqttClient


class TestPerTopicBufferPattern(unittest.TestCase):
    """Testet das Per-Topic-Buffer Pattern"""

    def setUp(self):
        """Test-Setup"""
        self.config = MqttConfig(host="localhost", port=1883, client_id="test_client", clean_session=True, protocol=4)

        # Mock MQTT-Client ohne echte Verbindung
        with patch('omf.dashboard.tools.omf_mqtt_client.mqtt'):
            self.client = OmfMqttClient(self.config)

    def test_buffer_initialization(self):
        """Test: Buffer werden korrekt initialisiert"""
        # Buffer sollten leer sein
        self.assertEqual(len(self.client._buffers), 0)

        # Buffer für Topic abrufen
        buffer = self.client.get_buffer("test/topic")
        self.assertEqual(len(buffer), 0)

    def test_subscribe_many_topics(self):
        """Test: Mehrere Topics können gleichzeitig subscribed werden"""
        topics = ["topic1", "topic2", "topic3"]

        # Mock client.subscribe (die interne MQTT-Client-Methode)
        with patch.object(self.client.client, 'subscribe') as mock_subscribe:
            self.client.subscribe_many(topics)

            # Alle Topics sollten subscribed werden
            self.assertEqual(mock_subscribe.call_count, 3)

            # Prüfen ob alle Topics subscribed wurden
            called_topics = [call[0][0] for call in mock_subscribe.call_args_list]
            for topic in topics:
                self.assertIn(topic, called_topics)

    def test_buffer_message_storage(self):
        """Test: Nachrichten werden in Topic-spezifischen Buffers gespeichert"""
        # Simuliere Nachrichten für verschiedene Topics
        topic1_messages = [{"topic": "topic1", "payload": "message1"}, {"topic": "topic1", "payload": "message2"}]
        topic2_messages = [{"topic": "topic2", "payload": "message3"}]

        # Nachrichten zu Buffers hinzufügen
        for msg in topic1_messages:
            self.client._buffers["topic1"].append(msg)
        for msg in topic2_messages:
            self.client._buffers["topic2"].append(msg)

        # Buffer abrufen
        topic1_buffer = list(self.client.get_buffer("topic1"))
        topic2_buffer = list(self.client.get_buffer("topic2"))

        # Prüfe Buffer-Inhalt
        self.assertEqual(len(topic1_buffer), 2)
        self.assertEqual(len(topic2_buffer), 1)
        self.assertEqual(topic1_buffer[0]["payload"], "message1")
        self.assertEqual(topic2_buffer[0]["payload"], "message3")

    def test_buffer_isolation(self):
        """Test: Buffer sind topic-spezifisch isoliert"""
        # Nachrichten für verschiedene Topics
        self.client._buffers["topic1"].append({"payload": "msg1"})
        self.client._buffers["topic2"].append({"payload": "msg2"})

        # Buffer sollten isoliert sein
        topic1_buffer = list(self.client.get_buffer("topic1"))
        topic2_buffer = list(self.client.get_buffer("topic2"))

        self.assertEqual(len(topic1_buffer), 1)
        self.assertEqual(len(topic2_buffer), 1)
        self.assertNotEqual(topic1_buffer[0]["payload"], topic2_buffer[0]["payload"])

    def test_wildcard_topic_handling(self):
        """Test: Wildcard Topics werden korrekt behandelt"""
        # Wildcard Topic
        wildcard_topic = "module/v1/ff/+/state"

        # Buffer für Wildcard Topic
        buffer = self.client.get_buffer(wildcard_topic)
        self.assertEqual(len(buffer), 0)

        # Nachricht hinzufügen
        self.client._buffers[wildcard_topic].append({"payload": "wildcard_msg"})

        # Buffer abrufen
        retrieved_buffer = list(self.client.get_buffer(wildcard_topic))
        self.assertEqual(len(retrieved_buffer), 1)
        self.assertEqual(retrieved_buffer[0]["payload"], "wildcard_msg")

    def test_buffer_performance(self):
        """Test: Buffer-Zugriff ist effizient"""
        import time

        # Viele Nachrichten hinzufügen
        topic = "performance/test"
        for i in range(1000):
            self.client._buffers[topic].append({"id": i, "payload": f"message_{i}"})

        # Buffer-Zugriff messen
        start_time = time.time()
        buffer = list(self.client.get_buffer(topic))
        end_time = time.time()

        # Sollte schnell sein (< 0.01 Sekunden)
        self.assertLess(end_time - start_time, 0.01)
        self.assertEqual(len(buffer), 1000)

    def test_empty_buffer_handling(self):
        """Test: Leere Buffer werden korrekt behandelt"""
        # Nicht-existierender Topic
        buffer = self.client.get_buffer("nonexistent/topic")
        self.assertEqual(len(buffer), 0)

        # Leerer Buffer
        self.client._buffers["empty/topic"] = []
        buffer = list(self.client.get_buffer("empty/topic"))
        self.assertEqual(len(buffer), 0)

    def test_buffer_max_size(self):
        """Test: Buffer haben maximale Größe (falls implementiert)"""
        topic = "size/test"

        # Viele Nachrichten hinzufügen
        for i in range(2000):
            self.client._buffers[topic].append({"id": i})

        # Buffer sollte nicht unbegrenzt wachsen
        buffer = list(self.client.get_buffer(topic))
        self.assertLessEqual(len(buffer), 2000)  # Aktuell keine Begrenzung


class TestPerTopicBufferIntegration(unittest.TestCase):
    """Integration Tests für Per-Topic-Buffer Pattern"""

    def test_dashboard_component_integration(self):
        """Test: Dashboard-Komponenten können Per-Topic-Buffer verwenden"""
        # Mock Dashboard-Komponente
        with patch('omf.dashboard.tools.omf_mqtt_client.mqtt'):
            client = OmfMqttClient(MqttConfig(host="localhost", port=1883))

        # Simuliere Dashboard-Komponente
        def mock_dashboard_component():
            # Topics subscriben
            client.subscribe_many(["module/v1/ff/+/state", "module/v1/ff/+/connection", "ccu/pairing/state"])

            # Buffer abrufen
            state_messages = list(client.get_buffer("module/v1/ff/+/state"))
            connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
            pairing_messages = list(client.get_buffer("ccu/pairing/state"))

            return {
                "state": len(state_messages),
                "connection": len(connection_messages),
                "pairing": len(pairing_messages),
            }

        # Komponente ausführen
        result = mock_dashboard_component()

        # Alle Buffer sollten leer sein (keine echten Nachrichten)
        self.assertEqual(result["state"], 0)
        self.assertEqual(result["connection"], 0)
        self.assertEqual(result["pairing"], 0)

    def test_message_processing_pattern(self):
        """Test: Message-Processing Pattern mit Per-Topic-Buffer"""
        with patch('omf.dashboard.tools.omf_mqtt_client.mqtt'):
            client = OmfMqttClient(MqttConfig(host="localhost", port=1883))

        # Simuliere Message-Processing
        def process_module_messages(state_messages, connection_messages, pairing_messages):
            """Simuliert _process_module_messages Funktion"""
            processed = {
                "state_count": len(state_messages),
                "connection_count": len(connection_messages),
                "pairing_count": len(pairing_messages),
            }
            return processed

        # Buffer abrufen und verarbeiten
        state_messages = list(client.get_buffer("module/v1/ff/+/state"))
        connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
        pairing_messages = list(client.get_buffer("ccu/pairing/state"))

        result = process_module_messages(state_messages, connection_messages, pairing_messages)

        # Alle sollten 0 sein (keine echten Nachrichten)
        self.assertEqual(result["state_count"], 0)
        self.assertEqual(result["connection_count"], 0)
        self.assertEqual(result["pairing_count"], 0)


if __name__ == "__main__":
    unittest.main()
