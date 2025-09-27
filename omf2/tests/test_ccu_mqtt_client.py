#!/usr/bin/env python3
"""
Tests for CCU MQTT Client
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
from collections import deque

# Set up path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from omf2.ccu.ccu_mqtt_client import CCUMqttClient, get_ccu_mqtt_client, cleanup_ccu_mqtt_client


class TestCCUMqttClient(unittest.TestCase):
    """Test cases for CCU MQTT Client"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clean up any existing singleton
        cleanup_ccu_mqtt_client()
        
        # Mock MQTT client
        self.mock_mqtt = Mock()
        self.mock_client_instance = Mock()
        self.mock_mqtt.Client.return_value = self.mock_client_instance
        
        self.patcher = patch('omf2.ccu.ccu_mqtt_client.mqtt', self.mock_mqtt)
        self.patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.patcher.stop()
        cleanup_ccu_mqtt_client()
    
    def test_client_initialization(self):
        """Test CCU MQTT client initialization"""
        client = CCUMqttClient(
            host="test.broker.com",
            port=1883,
            username="testuser",
            password="testpass",
            client_id="test_ccu_client"
        )
        
        # Check attributes
        self.assertEqual(client.host, "test.broker.com")
        self.assertEqual(client.port, 1883)
        self.assertEqual(client.username, "testuser")
        self.assertEqual(client.password, "testpass")
        self.assertEqual(client.client_id, "test_ccu_client")
        
        # Check MQTT client setup
        self.mock_mqtt.Client.assert_called_once()
        self.mock_client_instance.username_pw_set.assert_called_once_with("testuser", "testpass")
        
        # Check callbacks are set
        self.assertIsNotNone(self.mock_client_instance.on_connect)
        self.assertIsNotNone(self.mock_client_instance.on_disconnect)
        self.assertIsNotNone(self.mock_client_instance.on_message)
    
    def test_singleton_pattern(self):
        """Test singleton pattern works correctly"""
        client1 = get_ccu_mqtt_client(host="test1")
        client2 = get_ccu_mqtt_client(host="test2")  # Should ignore new params
        
        self.assertIs(client1, client2)
        self.assertEqual(client1.host, "test1")  # Should keep original params
    
    def test_cleanup_singleton(self):
        """Test singleton cleanup"""
        client = get_ccu_mqtt_client()
        
        cleanup_ccu_mqtt_client()
        
        # Get new client after cleanup
        new_client = get_ccu_mqtt_client()
        
        self.assertIsNot(client, new_client)


if __name__ == '__main__':
    unittest.main()