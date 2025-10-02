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

from omf2.ccu.ccu_mqtt_client import CcuMqttClient, get_ccu_mqtt_client


class TestCcuMqttClient(unittest.TestCase):
    """Test cases for CCU MQTT Client"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clean up any existing singleton
        from omf2.ccu.ccu_mqtt_client import CcuMqttClient
        CcuMqttClient._instance = None
        CcuMqttClient._initialized = False
    
    def test_client_initialization(self):
        """Test CCU MQTT client initialization"""
        client = get_ccu_mqtt_client()
        
        self.assertIsNotNone(client.registry_manager)
        self.assertEqual(client.client_id, "omf_ccu")
        # TODO: Add connected attribute to CcuMqttClient
        # self.assertFalse(client.connected)
        # self.assertIsNone(client.client)
    
    def test_singleton_pattern(self):
        """Test singleton pattern works correctly"""
        client1 = get_ccu_mqtt_client()
        client2 = get_ccu_mqtt_client()  # Should return same instance
        
        self.assertIs(client1, client2)
        self.assertIsNotNone(client1)
    
    def test_cleanup_singleton(self):
        """Test singleton cleanup"""
        client = get_ccu_mqtt_client()
        
        # Clean up singleton
        from omf2.ccu.ccu_mqtt_client import CcuMqttClient
        CcuMqttClient._instance = None
        CcuMqttClient._initialized = False
        
        # Get new client after cleanup
        new_client = get_ccu_mqtt_client()
        
        self.assertIsNot(client, new_client)


if __name__ == '__main__':
    unittest.main()