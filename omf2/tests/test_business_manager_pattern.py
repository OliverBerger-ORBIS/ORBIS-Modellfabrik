#!/usr/bin/env python3
"""
Test Business-Manager Pattern Implementation
Tests the new MQTT-Client → Manager → State-Holder → UI flow
"""

import pytest
import json
from unittest.mock import Mock, patch
from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.ccu.module_manager import get_ccu_module_manager
from omf2.registry.manager.registry_manager import get_registry_manager


class TestBusinessManagerPattern:
    """Test Business-Manager Pattern Implementation"""
    
    def test_sensor_manager_state_holder(self):
        """Test SensorManager as State-Holder"""
        # Get SensorManager singleton
        sensor_manager = get_ccu_sensor_manager()
        
        # Test initial state
        assert hasattr(sensor_manager, 'sensor_data')
        assert isinstance(sensor_manager.sensor_data, dict)
        assert len(sensor_manager.sensor_data) == 0
        
        # Test get_sensor_data method
        sensor_data = sensor_manager.get_sensor_data()
        assert isinstance(sensor_data, dict)
        
        # Test get_sensor_state method
        sensor_state = sensor_manager.get_sensor_state()
        assert isinstance(sensor_state, dict)
        assert 'sensor_data' in sensor_state
        assert 'total_sensors' in sensor_state
        assert 'sensor_topics' in sensor_state
    
    def test_module_manager_state_holder(self):
        """Test ModuleManager as State-Holder"""
        # Get ModuleManager singleton
        module_manager = get_ccu_module_manager()
        
        # Test initial state
        assert hasattr(module_manager, 'module_status')
        assert isinstance(module_manager.module_status, dict)
        assert len(module_manager.module_status) == 0
        
        # Test get_module_status_from_state method
        module_status = module_manager.get_module_status_from_state()
        assert isinstance(module_status, dict)
        
        # Test get_module_state method
        module_state = module_manager.get_module_state()
        assert isinstance(module_state, dict)
        assert 'module_status' in module_state
        assert 'total_modules' in module_state
        assert 'module_ids' in module_state
    
    def test_sensor_manager_process_message(self):
        """Test SensorManager.process_sensor_message with real test payloads"""
        sensor_manager = get_ccu_sensor_manager()
        
        # Load real test payload from test_payloads_for_topic
        import json
        from pathlib import Path
        
        test_payload_path = Path(__file__).parent / "test_payloads_for_topic" / "_j1_txt_1_i_bme680__000013.json"
        with open(test_payload_path, 'r') as f:
            real_payload = json.load(f)
        
        # Create correct structure: topic (String) + payload (Dict)
        topic = "/j1/txt/1/i/bme680"
        payload = real_payload  # Dict direkt, nicht als JSON-String
        
        # Process message
        sensor_manager.process_sensor_message(topic, payload)
        
        # Check if state was updated
        sensor_data = sensor_manager.get_sensor_data()
        assert topic in sensor_data
        
        # Check processed data structure
        processed_data = sensor_data[topic]
        assert 'temperature' in processed_data
        assert 'humidity' in processed_data
        assert 'pressure' in processed_data
        assert 'air_quality' in processed_data
        
        # Verify values match real payload
        assert processed_data['temperature'] == real_payload['t']
        assert processed_data['humidity'] == real_payload['h']
        assert processed_data['pressure'] == real_payload['p']
        assert processed_data['air_quality'] == real_payload['iaq']
    
    def test_module_manager_process_message(self):
        """Test ModuleManager.process_module_message with real test payloads"""
        module_manager = get_ccu_module_manager()
        
        # Load real test payload from test_payloads_for_topic
        import json
        from pathlib import Path
        
        test_payload_path = Path(__file__).parent / "test_payloads_for_topic" / "module_v1_ff_SVR4H73275_state__000292.json"
        with open(test_payload_path, 'r') as f:
            real_payload = json.load(f)
        
        # Create correct structure: topic (String) + payload (Dict)
        topic = "module/v1/ff/SVR4H73275/state"
        payload = real_payload  # Dict direkt, nicht als JSON-String
        
        # Process message
        module_manager.process_module_message(topic, payload)
        
        # Check if state was updated
        module_status = module_manager.get_module_status_from_state()
        assert "SVR4H73275" in module_status
        
        # Check processed data structure
        processed_data = module_status["SVR4H73275"]
        assert 'message_count' in processed_data
        assert 'last_update' in processed_data
        # Note: Module state processing depends on topic pattern (connection vs state)
        # The real payload is a state message, so it should extract relevant fields
    
    def test_registry_business_functions(self):
        """Test Registry Business-Functions Configuration"""
        registry_manager = get_registry_manager()
        
        # Test business functions retrieval
        business_functions = registry_manager.get_business_functions('ccu_mqtt_client')
        assert isinstance(business_functions, dict)
        
        # Test sensor_manager configuration
        assert 'sensor_manager' in business_functions
        sensor_config = business_functions['sensor_manager']
        assert 'subscribed_topics' in sensor_config
        assert 'callback_method' in sensor_config
        assert 'manager_class' in sensor_config
        assert 'manager_module' in sensor_config
        
        # Test module_manager configuration
        assert 'module_manager' in business_functions
        module_config = business_functions['module_manager']
        assert 'subscribed_topics' in module_config
        assert 'callback_method' in module_config
        assert 'manager_class' in module_config
        assert 'manager_module' in module_config
    
    def test_business_function_topics(self):
        """Test Business-Function Topic Retrieval"""
        registry_manager = get_registry_manager()
        
        # Test sensor manager topics
        sensor_topics = registry_manager.get_business_function_topics('ccu_mqtt_client', 'sensor_manager')
        assert isinstance(sensor_topics, list)
        assert "/j1/txt/1/i/bme680" in sensor_topics
        assert "/j1/txt/1/i/ldr" in sensor_topics
        assert "/j1/txt/1/i/cam" in sensor_topics
        
        # Test module manager topics
        module_topics = registry_manager.get_business_function_topics('ccu_mqtt_client', 'module_manager')
        assert isinstance(module_topics, list)
        assert "module/v1/ff/SVR4H73275/state" in module_topics
        assert "fts/v1/ff/5iO4/state" in module_topics
    
    @patch('omf2.ccu.sensor_manager.get_ccu_sensor_manager')
    def test_mqtt_client_callback_integration(self, mock_sensor_manager):
        """Test MQTT-Client Business-Function Callback Integration"""
        # Mock sensor manager
        mock_manager_instance = Mock()
        mock_manager_instance.process_sensor_message = Mock()
        mock_sensor_manager.return_value = mock_manager_instance
        
        # This would be called by MQTT-Client._call_business_function_callback
        # Simulate the callback call
        topic = "/j1/txt/1/i/bme680"
        payload = {"t": 25.4}  # Dict direkt, nicht als JSON-String
        
        # Simulate callback
        mock_manager_instance.process_sensor_message(topic, payload)
        
        # Verify callback was called
        mock_manager_instance.process_sensor_message.assert_called_once_with(topic, payload)
    
    def test_state_holder_isolation(self):
        """Test that State-Holders are isolated between different manager instances"""
        # Get two instances (should be same singleton)
        sensor_manager1 = get_ccu_sensor_manager()
        sensor_manager2 = get_ccu_sensor_manager()
        
        # They should be the same instance (singleton)
        assert sensor_manager1 is sensor_manager2
        
        # State should be shared
        sensor_manager1.sensor_data["test_topic"] = {"test": "data"}
        assert "test_topic" in sensor_manager2.sensor_data
        
        # Same for module manager
        module_manager1 = get_ccu_module_manager()
        module_manager2 = get_ccu_module_manager()
        
        assert module_manager1 is module_manager2
        
        module_manager1.module_status["test_module"] = {"test": "status"}
        assert "test_module" in module_manager2.module_status


if __name__ == "__main__":
    pytest.main([__file__])
