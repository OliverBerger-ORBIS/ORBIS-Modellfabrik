#!/usr/bin/env python3
"""
Unit Tests für OMF Dashboard - Nachrichtenzentrale Component
Version: 3.0.0
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))

from omf.dashboard.components.message_center import (
    MessageMonitorService,
    format_payload,
    format_timestamp,
    get_topic_friendly_name,
)


class TestMessageMonitorService(unittest.TestCase):
    """Test-Klasse für MessageMonitorService"""

    def setUp(self):
        """Setup für jeden Test"""
        self.monitor = MessageMonitorService()

    def test_add_sent_message(self):
        """Test: Gesendete Nachricht hinzufügen"""
        topic = "test/topic"
        payload = '{"test": "data"}'

        self.monitor.add_sent_message(topic, payload)

        self.assertEqual(len(self.monitor.sent_messages), 1)
        self.assertEqual(self.monitor.sent_messages[0]["topic"], topic)
        self.assertEqual(self.monitor.sent_messages[0]["payload"], payload)
        self.assertEqual(self.monitor.sent_messages[0]["direction"], "sent")

    def test_add_received_message(self):
        """Test: Empfangene Nachricht hinzufügen"""
        topic = "test/topic"
        payload = '{"test": "data"}'

        self.monitor.add_received_message(topic, payload)

        self.assertEqual(len(self.monitor.received_messages), 1)
        self.assertEqual(self.monitor.received_messages[0]["topic"], topic)
        self.assertEqual(self.monitor.received_messages[0]["payload"], payload)
        self.assertEqual(self.monitor.received_messages[0]["direction"], "received")

    def test_message_ordering(self):
        """Test: Nachrichten werden neueste zuerst sortiert"""
        # Erste Nachricht
        self.monitor.add_sent_message("topic1", "payload1")

        # Zweite Nachricht (sollte zuerst erscheinen)
        self.monitor.add_sent_message("topic2", "payload2")

        self.assertEqual(self.monitor.sent_messages[0]["topic"], "topic2")
        self.assertEqual(self.monitor.sent_messages[1]["topic"], "topic1")

    def test_message_limit(self):
        """Test: Maximale Anzahl Nachrichten wird eingehalten"""
        # Mehr als max_messages hinzufügen
        for i in range(self.monitor.max_messages + 10):
            self.monitor.add_sent_message(f"topic{i}", f"payload{i}")

        self.assertEqual(len(self.monitor.sent_messages), self.monitor.max_messages)
        # Neueste Nachricht sollte zuerst sein
        self.assertEqual(
            self.monitor.sent_messages[0]["topic"],
            f"topic{self.monitor.max_messages + 9}",
        )

    def test_filter_by_modules(self):
        """Test: Filterung nach Modulen"""
        # Test-Nachrichten hinzufügen
        self.monitor.add_sent_message("hbw/status", "payload1")
        self.monitor.add_sent_message("fts/status", "payload2")
        self.monitor.add_sent_message("other/topic", "payload3")

        filters = {"modules": ["HBW"]}
        filtered = self.monitor.get_filtered_messages(self.monitor.sent_messages, filters)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["topic"], "hbw/status")

    def test_filter_by_categories(self):
        """Test: Filterung nach Kategorien"""
        # Test-Nachrichten hinzufügen
        self.monitor.add_sent_message("ccu/status", "payload1")
        self.monitor.add_sent_message("txt/status", "payload2")
        self.monitor.add_sent_message("other/topic", "payload3")

        filters = {"categories": ["CCU"]}
        filtered = self.monitor.get_filtered_messages(self.monitor.sent_messages, filters)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["topic"], "ccu/status")

    def test_filter_by_time_range(self):
        """Test: Filterung nach Zeitraum"""
        # Alte Nachricht (vor 2 Stunden)
        old_time = datetime.now() - timedelta(hours=2)
        self.monitor.add_sent_message("topic1", "payload1", old_time)

        # Neue Nachricht (jetzt)
        self.monitor.add_sent_message("topic2", "payload2")

        filters = {"time_range": "1h"}
        filtered = self.monitor.get_filtered_messages(self.monitor.sent_messages, filters)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["topic"], "topic2")

    def test_filter_by_topic_pattern(self):
        """Test: Filterung nach Topic-Pattern"""
        # Test-Nachrichten hinzufügen
        self.monitor.add_sent_message("hbw/status", "payload1")
        self.monitor.add_sent_message("hbw/order", "payload2")
        self.monitor.add_sent_message("fts/status", "payload3")

        filters = {"topic_pattern": "hbw"}
        filtered = self.monitor.get_filtered_messages(self.monitor.sent_messages, filters)

        self.assertEqual(len(filtered), 2)
        self.assertTrue(all("hbw" in msg["topic"] for msg in filtered))


class TestUtilityFunctions(unittest.TestCase):
    """Test-Klasse für Utility-Funktionen"""

    def test_format_timestamp(self):
        """Test: Timestamp-Formatierung"""
        timestamp = datetime(2024, 1, 1, 12, 30, 45)
        formatted = format_timestamp(timestamp)

        self.assertEqual(formatted, "12:30:45")

    def test_format_payload_json(self):
        """Test: JSON-Payload-Formatierung"""
        payload = '{"test": "data", "number": 123}'
        formatted = format_payload(payload)

        # Sollte JSON-formatierte Ausgabe sein
        self.assertIn("test", formatted)
        self.assertIn("data", formatted)
        self.assertIn("123", formatted)

    def test_format_payload_non_json(self):
        """Test: Non-JSON-Payload-Formatierung"""
        payload = "plain text payload"
        formatted = format_payload(payload)

        self.assertEqual(formatted, "plain text payload")

    def test_format_payload_long_text(self):
        """Test: Lange Payload-Formatierung"""
        long_payload = "a" * 300  # 300 Zeichen
        formatted = format_payload(long_payload)

        self.assertTrue(len(formatted) <= 203)  # 200 + "..."
        self.assertTrue(formatted.endswith("..."))

    def test_get_topic_friendly_name_hbw(self):
        """Test: Friendly Name für HBW Topic"""
        friendly = get_topic_friendly_name("hbw/status")
        self.assertEqual(friendly, "HBW: hbw/status")

    def test_get_topic_friendly_name_fts(self):
        """Test: Friendly Name für FTS Topic"""
        friendly = get_topic_friendly_name("fts/order")
        self.assertEqual(friendly, "FTS: fts/order")

    def test_get_topic_friendly_name_unknown(self):
        """Test: Friendly Name für unbekanntes Topic"""
        friendly = get_topic_friendly_name("unknown/topic")
        self.assertEqual(friendly, "unknown/topic")

    def test_get_topic_friendly_name_case_insensitive(self):
        """Test: Case-insensitive Topic-Mapping"""
        friendly = get_topic_friendly_name("HBW/STATUS")
        self.assertEqual(friendly, "HBW: HBW/STATUS")


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
