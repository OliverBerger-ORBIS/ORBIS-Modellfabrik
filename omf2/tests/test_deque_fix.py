#!/usr/bin/env python3
"""
Test für Deque-Fix - reproduziert den "collections.deque object has no attribute 'get'" Fehler
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from omf2.admin.admin_mqtt_client import get_admin_mqtt_client


class TestDequeFix(unittest.TestCase):
    """Test für Deque-Fix"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.client = get_admin_mqtt_client()
        
    def test_topic_buffers_structure(self):
        """Test: Topic buffers sollten defaultdict mit deque sein"""
        # Prüfe, dass topic_buffers ein defaultdict ist
        self.assertIsInstance(self.client.topic_buffers, dict)
        
        # Prüfe, dass neue Topics automatisch deque erstellen
        from collections import deque
        test_topic = "test/topic"
        buffer = self.client.topic_buffers[test_topic]
        self.assertIsInstance(buffer, deque)
        
    def test_get_buffer_returns_dict_not_deque(self):
        """Test: get_buffer() sollte Dictionary zurückgeben, nicht deque"""
        # Simuliere eine Message im Buffer
        test_message = {"test": "data", "timestamp": 1234567890}
        
        # Füge Message zum Buffer hinzu
        self.client.topic_buffers["test/topic"].append(test_message)
        
        # get_buffer() sollte Dictionary zurückgeben
        result = self.client.get_buffer("test/topic")
        self.assertIsInstance(result, dict)
        self.assertEqual(result, test_message)
        
    def test_get_buffer_empty_returns_none(self):
        """Test: get_buffer() für leeren Buffer sollte None zurückgeben"""
        result = self.client.get_buffer("nonexistent/topic")
        self.assertIsNone(result)
        
    def test_system_overview_with_deque(self):
        """Test: System overview sollte mit deque arbeiten"""
        # Füge Test-Messages hinzu
        self.client.topic_buffers["topic1"].append({"timestamp": 1000, "data": "test1"})
        self.client.topic_buffers["topic2"].append({"timestamp": 2000, "data": "test2"})
        
        # System overview sollte funktionieren
        overview = self.client.get_system_overview()
        
        self.assertIn("total_topics", overview)
        self.assertIn("active_topics", overview)
        self.assertIn("last_activity", overview)
        self.assertGreaterEqual(overview["total_topics"], 0)
        
    def test_message_center_tab_sorting(self):
        """Test: Message center tab sorting sollte mit deque arbeiten"""
        # Simuliere all_buffers wie in message_center_tab.py
        all_buffers = {
            "topic1": self.client.topic_buffers["topic1"],
            "topic2": self.client.topic_buffers["topic2"]
        }
        
        # Füge Test-Messages hinzu
        all_buffers["topic1"].append({"timestamp": 1000, "data": "test1"})
        all_buffers["topic2"].append({"timestamp": 2000, "data": "test2"})
        
        # Teste die get_latest_timestamp Funktion
        def get_latest_timestamp(topic):
            buffer = all_buffers[topic]
            if buffer and len(buffer) > 0:
                return buffer[-1].get('timestamp', 0)
            return 0
        
        # Sollte funktionieren ohne "deque object has no attribute 'get'" Fehler
        timestamp1 = get_latest_timestamp("topic1")
        timestamp2 = get_latest_timestamp("topic2")
        
        self.assertEqual(timestamp1, 1000)
        self.assertEqual(timestamp2, 2000)
        
        # Teste sorting
        topics = ["topic1", "topic2"]
        topics.sort(key=get_latest_timestamp, reverse=True)
        
        # topic2 sollte zuerst kommen (höherer timestamp)
        self.assertEqual(topics[0], "topic2")
        self.assertEqual(topics[1], "topic1")


if __name__ == '__main__':
    unittest.main()
