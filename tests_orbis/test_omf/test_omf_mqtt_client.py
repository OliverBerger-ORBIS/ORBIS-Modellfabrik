from src_orbis.omf.tools.omf_mqtt_factory import get_omf_mqtt_client

#!/usr/bin/env python3
"""Test für OMF MQTT Client."""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import unittest


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
