#!/usr/bin/env python3
"""
Tests für CCU Manager State-Holder Pattern
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import threading
import time


class TestSensorManager(unittest.TestCase):
    """Test CCU Sensor Manager State-Holder Pattern"""
    
    def setUp(self):
        """Setup Test Environment"""
        # Mock dependencies
        self.mock_registry_manager = Mock()
        self.mock_message_manager = Mock()
        
        # Mock Registry Manager responses
        self.mock_registry_manager.validate_topic_payload.return_value = {
            'valid': True
        }
        
        # Patch get functions
        with patch('omf2.ccu.sensor_manager.get_registry_manager', return_value=self.mock_registry_manager):
            with patch('omf2.ccu.sensor_manager.get_ccu_message_manager', return_value=self.mock_message_manager):
                from omf2.ccu.sensor_manager import SensorManager
                self.manager = SensorManager()
    
    def test_init(self):
        """Test SensorManager initialization"""
        self.assertIsNotNone(self.manager._state_lock)
        self.assertIsInstance(self.manager._sensor_state, dict)
        self.assertEqual(len(self.manager._sensor_state), 0)
    
    def test_process_sensor_message_bme680(self):
        """Test processing BME680 sensor message"""
        topic = "/j1/txt/1/i/bme680"
        payload = {
            "t": 25.5,
            "h": 45.2,
            "p": 1013.25,
            "iaq": 50.0,
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        self.manager.process_sensor_message(topic, payload)
        
        # Verify state was updated
        sensor_data = self.manager.get_sensor_data(topic)
        self.assertIsNotNone(sensor_data)
        self.assertEqual(sensor_data.get("temperature"), 25.5)
        self.assertEqual(sensor_data.get("humidity"), 45.2)
        self.assertEqual(sensor_data.get("pressure"), 1013.25)
        self.assertEqual(sensor_data.get("air_quality"), 50.0)
    
    def test_process_sensor_message_ldr(self):
        """Test processing LDR sensor message"""
        topic = "/j1/txt/1/i/ldr"
        payload = {
            "ldr": 250.0,
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        self.manager.process_sensor_message(topic, payload)
        
        # Verify state was updated
        sensor_data = self.manager.get_sensor_data(topic)
        self.assertIsNotNone(sensor_data)
        self.assertEqual(sensor_data.get("light"), 250.0)
    
    def test_get_all_sensor_data(self):
        """Test getting all sensor data"""
        # Add multiple sensor data
        topic1 = "/j1/txt/1/i/bme680"
        payload1 = {"t": 25.5, "h": 45.2, "p": 1013.25, "iaq": 50.0}
        
        topic2 = "/j1/txt/1/i/ldr"
        payload2 = {"ldr": 250.0}
        
        self.manager.process_sensor_message(topic1, payload1)
        self.manager.process_sensor_message(topic2, payload2)
        
        # Get all data
        all_data = self.manager.get_all_sensor_data()
        self.assertEqual(len(all_data), 2)
        self.assertIn(topic1, all_data)
        self.assertIn(topic2, all_data)
    
    def test_thread_safety(self):
        """Test thread-safe access to sensor data"""
        topic = "/j1/txt/1/i/bme680"
        
        def update_sensor():
            for i in range(100):
                payload = {"t": float(i), "h": 50.0, "p": 1000.0, "iaq": 40.0}
                self.manager.process_sensor_message(topic, payload)
        
        def read_sensor():
            for i in range(100):
                data = self.manager.get_sensor_data(topic)
                # Should never fail due to race condition
                self.assertIsInstance(data, dict)
        
        # Create threads
        threads = []
        threads.append(threading.Thread(target=update_sensor))
        threads.append(threading.Thread(target=read_sensor))
        
        # Start threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify final state exists
        data = self.manager.get_sensor_data(topic)
        self.assertIsNotNone(data)


class TestModuleManager(unittest.TestCase):
    """Test CCU Module Manager State-Holder Pattern"""
    
    def setUp(self):
        """Setup Test Environment"""
        # Mock dependencies
        self.mock_registry_manager = Mock()
        
        # Mock Registry Manager responses
        self.mock_registry_manager.get_modules.return_value = {
            'HBW': {'name': 'Hochregallager', 'icon': '🏭'},
            'MILL': {'name': 'Fräsen', 'icon': '⚙️'}
        }
        
        self.mock_registry_manager.get_mqtt_clients.return_value = {
            'ccu_mqtt_client': {
                'subscribed_topics': [
                    {'topic': 'module/v1/ff/+/state'},
                    {'topic': 'module/v1/ff/+/connection'}
                ]
            }
        }
        
        # Patch get functions
        with patch('omf2.ccu.module_manager.get_registry_manager', return_value=self.mock_registry_manager):
            from omf2.ccu.module_manager import CcuModuleManager
            self.manager = CcuModuleManager(registry_manager=self.mock_registry_manager)
    
    def test_init(self):
        """Test ModuleManager initialization"""
        self.assertIsNotNone(self.manager._state_lock)
        self.assertIsInstance(self.manager._module_state, dict)
        self.assertEqual(len(self.manager._module_state), 0)
    
    def test_process_module_message_connection(self):
        """Test processing module connection message"""
        topic = "module/v1/ff/HBW/connection"
        payload = {
            "connectionState": "connected",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        self.manager.process_module_message(topic, payload)
        
        # Verify state was updated
        status = self.manager.get_module_status("HBW")
        self.assertIsNotNone(status)
        self.assertTrue(status.get("connected"))
    
    def test_process_module_message_state(self):
        """Test processing module state message"""
        topic = "module/v1/ff/MILL/state"
        payload = {
            "available": "READY",
            "timestamp": "2025-01-01T00:00:00Z"
        }
        
        self.manager.process_module_message(topic, payload)
        
        # Verify state was updated
        status = self.manager.get_module_status("MILL")
        self.assertIsNotNone(status)
        self.assertEqual(status.get("available"), "READY")
    
    def test_get_all_module_status(self):
        """Test getting all module status"""
        # Add multiple module status
        topic1 = "module/v1/ff/HBW/connection"
        payload1 = {"connectionState": "connected"}
        
        topic2 = "module/v1/ff/MILL/state"
        payload2 = {"available": "READY"}
        
        self.manager.process_module_message(topic1, payload1)
        self.manager.process_module_message(topic2, payload2)
        
        # Get all status
        all_status = self.manager.get_all_module_status()
        self.assertEqual(len(all_status), 2)
        self.assertIn("HBW", all_status)
        self.assertIn("MILL", all_status)
    
    def test_thread_safety(self):
        """Test thread-safe access to module status"""
        topic = "module/v1/ff/HBW/connection"
        
        def update_module():
            for i in range(100):
                state = "connected" if i % 2 == 0 else "disconnected"
                payload = {"connectionState": state}
                self.manager.process_module_message(topic, payload)
        
        def read_module():
            for i in range(100):
                status = self.manager.get_module_status("HBW")
                # Should never fail due to race condition
                self.assertIsInstance(status, dict)
        
        # Create threads
        threads = []
        threads.append(threading.Thread(target=update_module))
        threads.append(threading.Thread(target=read_module))
        
        # Start threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Verify final state exists
        status = self.manager.get_module_status("HBW")
        self.assertIsNotNone(status)


class TestCcuMqttClientCallbacks(unittest.TestCase):
    """Test CCU MQTT Client Callback Registration"""
    
    def setUp(self):
        """Setup Test Environment"""
        # Mock paho-mqtt
        self.mock_mqtt = Mock()
        
        # Patch dependencies
        with patch('omf2.ccu.ccu_mqtt_client.mqtt', self.mock_mqtt):
            with patch('omf2.ccu.ccu_mqtt_client.get_registry_manager'):
                from omf2.ccu.ccu_mqtt_client import CcuMqttClient
                # Reset singleton for testing
                CcuMqttClient._instance = None
                CcuMqttClient._initialized = False
                self.client = CcuMqttClient()
    
    def test_register_callback(self):
        """Test registering message callback"""
        callback = Mock()
        
        self.client.register_message_callback(callback)
        
        self.assertIn(callback, self.client._message_callbacks)
    
    def test_unregister_callback(self):
        """Test unregistering message callback"""
        callback = Mock()
        
        self.client.register_message_callback(callback)
        self.assertIn(callback, self.client._message_callbacks)
        
        self.client.unregister_message_callback(callback)
        self.assertNotIn(callback, self.client._message_callbacks)
    
    def test_callback_execution(self):
        """Test callback execution on message"""
        callback1 = Mock()
        callback2 = Mock()
        
        self.client.register_message_callback(callback1)
        self.client.register_message_callback(callback2)
        
        # Simulate message reception
        topic = "test/topic"
        payload = {"test": "data"}
        
        # Call callbacks directly (simulating _on_message)
        with self.client._callbacks_lock:
            for callback in self.client._message_callbacks:
                callback(topic, payload)
        
        # Verify callbacks were called
        callback1.assert_called_once_with(topic, payload)
        callback2.assert_called_once_with(topic, payload)


if __name__ == '__main__':
    unittest.main()
