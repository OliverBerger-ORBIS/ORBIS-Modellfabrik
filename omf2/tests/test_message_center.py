"""
Test Message Center Components
"""

import pytest
import logging
import time
from unittest.mock import MagicMock, patch, Mock
from datetime import datetime

# Import the components to test
from omf2.message_center.mqtt_config import MqttConfig, get_config_for_env
from omf2.message_center.mqtt_client import MqttClient
from omf2.message_center.mqtt_gateway import MqttGateway
from omf2.message_center.message_handler import MessageHandler, MessageRow


class TestMqttConfig:
    """Test MQTT Configuration"""
    
    def test_mqtt_config_creation(self):
        """Test: MQTT config can be created"""
        config = MqttConfig(host="localhost", port=1883)
        
        assert config.host == "localhost"
        assert config.port == 1883
        assert config.client_id == "omf2_message_center"
        assert config.keepalive == 60
    
    def test_get_config_for_env_live(self):
        """Test: Live environment config"""
        config = get_config_for_env("live")
        
        assert config.host == "192.168.0.100"
        assert config.port == 1883
        assert config.client_id == "omf2_live_client"
    
    def test_get_config_for_env_mock(self):
        """Test: Mock environment config"""
        config = get_config_for_env("mock")
        
        assert config.host == "localhost"
        assert config.port == 1883
        assert config.client_id == "omf2_mock_client"
    
    def test_get_config_for_env_invalid(self):
        """Test: Invalid environment raises error"""
        with pytest.raises(ValueError):
            get_config_for_env("invalid")


class TestMessageRow:
    """Test MessageRow data class"""
    
    def test_message_row_creation(self):
        """Test: MessageRow can be created"""
        row = MessageRow(
            topic="test/topic",
            payload={"test": "data"},
            message_type="received",
            timestamp=time.time()
        )
        
        assert row.topic == "test/topic"
        assert row.payload == {"test": "data"}
        assert row.message_type == "received"
        assert row.qos == 0
        assert row.retain == False
    
    def test_formatted_timestamp(self):
        """Test: Timestamp formatting works"""
        test_time = 1609459200.0  # 2021-01-01 00:00:00
        row = MessageRow(
            topic="test", payload={}, message_type="received", timestamp=test_time
        )
        
        formatted = row.get_formatted_timestamp()
        assert "2021-01-01" in formatted
    
    def test_formatted_payload_dict(self):
        """Test: Dict payload formatting"""
        row = MessageRow(
            topic="test", 
            payload={"key": "value", "number": 42}, 
            message_type="received", 
            timestamp=time.time()
        )
        
        formatted = row.get_formatted_payload()
        assert "key" in formatted
        assert "value" in formatted
        assert "42" in formatted
    
    def test_formatted_payload_string(self):
        """Test: String payload formatting"""
        row = MessageRow(
            topic="test", 
            payload="Simple string", 
            message_type="received", 
            timestamp=time.time()
        )
        
        formatted = row.get_formatted_payload()
        assert formatted == "Simple string"
    
    def test_topic_display_name(self):
        """Test: Topic display name mapping"""
        # Test exact match
        row = MessageRow(
            topic="f/i/order", 
            payload={}, 
            message_type="received", 
            timestamp=time.time()
        )
        display_name = row.get_topic_display_name()
        assert "📋 Orders" == display_name
        
        # Test partial match
        row = MessageRow(
            topic="omf/hbw/status", 
            payload={}, 
            message_type="received", 
            timestamp=time.time()
        )
        display_name = row.get_topic_display_name()
        assert "🏭 HBW" in display_name
        
        # Test no match
        row = MessageRow(
            topic="custom/topic", 
            payload={}, 
            message_type="received", 
            timestamp=time.time()
        )
        display_name = row.get_topic_display_name()
        assert display_name == "custom/topic"


class TestMessageHandler:
    """Test Message Handler"""
    
    def setup_method(self):
        """Setup for each test"""
        self.handler = MessageHandler()
    
    def test_message_handler_creation(self):
        """Test: MessageHandler can be created"""
        assert self.handler is not None
        assert hasattr(self.handler, 'logger')
    
    def test_convert_messages_to_rows(self):
        """Test: Message conversion to rows"""
        raw_messages = [
            {
                "topic": "test/topic",
                "payload": {"data": "test"},
                "type": "received",
                "timestamp": time.time(),
                "qos": 1,
                "retain": True
            }
        ]
        
        rows = self.handler.convert_messages_to_rows(raw_messages)
        
        assert len(rows) == 1
        assert isinstance(rows[0], MessageRow)
        assert rows[0].topic == "test/topic"
        assert rows[0].payload == {"data": "test"}
    
    def test_filter_messages_by_topic(self):
        """Test: Topic filtering"""
        messages = [
            MessageRow("hbw/status", {}, "received", time.time()),
            MessageRow("fts/position", {}, "received", time.time()),
            MessageRow("mill/speed", {}, "received", time.time())
        ]
        
        filtered = self.handler.filter_messages_by_topic(messages, "hbw")
        assert len(filtered) == 1
        assert filtered[0].topic == "hbw/status"
        
        # Test case insensitive
        filtered = self.handler.filter_messages_by_topic(messages, "HBW")
        assert len(filtered) == 1
    
    def test_filter_messages_by_type(self):
        """Test: Type filtering"""
        messages = [
            MessageRow("topic1", {}, "sent", time.time()),
            MessageRow("topic2", {}, "received", time.time()),
            MessageRow("topic3", {}, "sent", time.time())
        ]
        
        sent_messages = self.handler.filter_messages_by_type(messages, "sent")
        assert len(sent_messages) == 2
        
        received_messages = self.handler.filter_messages_by_type(messages, "received")
        assert len(received_messages) == 1
        
        all_messages = self.handler.filter_messages_by_type(messages, "all")
        assert len(all_messages) == 3
    
    def test_filter_messages_by_module(self):
        """Test: Module filtering"""
        messages = [
            MessageRow("omf/hbw/status", {}, "received", time.time()),
            MessageRow("omf/fts/position", {}, "received", time.time()),
            MessageRow("other/topic", {}, "received", time.time())
        ]
        
        hbw_messages = self.handler.filter_messages_by_module(messages, "HBW")
        assert len(hbw_messages) == 1
        
        fts_messages = self.handler.filter_messages_by_module(messages, "FTS")
        assert len(fts_messages) == 1
        
        all_messages = self.handler.filter_messages_by_module(messages, "all")
        assert len(all_messages) == 3
    
    def test_sort_messages(self):
        """Test: Message sorting"""
        messages = [
            MessageRow("topic1", {}, "received", 1.0),
            MessageRow("topic2", {}, "received", 3.0),
            MessageRow("topic3", {}, "received", 2.0)
        ]
        
        # Sort by timestamp ascending
        sorted_asc = self.handler.sort_messages(messages, "timestamp", ascending=True)
        assert sorted_asc[0].timestamp == 1.0
        assert sorted_asc[1].timestamp == 2.0
        assert sorted_asc[2].timestamp == 3.0
        
        # Sort by timestamp descending (default)
        sorted_desc = self.handler.sort_messages(messages, "timestamp", ascending=False)
        assert sorted_desc[0].timestamp == 3.0
        assert sorted_desc[1].timestamp == 2.0
        assert sorted_desc[2].timestamp == 1.0
    
    def test_get_message_statistics(self):
        """Test: Message statistics calculation"""
        messages = [
            MessageRow("hbw/status", {}, "sent", time.time()),
            MessageRow("fts/position", {}, "received", time.time()),
            MessageRow("hbw/control", {}, "received", time.time())
        ]
        
        stats = self.handler.get_message_statistics(messages)
        
        assert stats["total"] == 3
        assert stats["sent"] == 1
        assert stats["received"] == 2
        assert stats["unique_topics"] == 3
        assert "HBW" in stats["modules"]
        assert "FTS" in stats["modules"]
    
    def test_create_table_data(self):
        """Test: Table data creation"""
        messages = [
            MessageRow("test/topic", {"data": "test"}, "received", time.time())
        ]
        
        headers, rows = self.handler.create_table_data(messages)
        
        assert len(headers) == 6
        assert "Zeit" in headers
        assert "Topic" in headers
        assert "Payload" in headers
        
        assert len(rows) == 1
        assert len(rows[0]) == 6


class TestMqttClient:
    """Test MQTT Client (with mocking)"""
    
    def setup_method(self):
        """Setup for each test"""
        # Reset singleton before each test
        MqttClient.reset_singleton()
    
    def teardown_method(self):
        """Teardown after each test"""
        # Reset singleton after each test
        MqttClient.reset_singleton()
    
    @patch('paho.mqtt.client.Client')
    def test_mqtt_client_singleton(self, mock_mqtt_client):
        """Test: MQTT Client follows singleton pattern"""
        config = MqttConfig(host="localhost")
        
        client1 = MqttClient(config)
        client2 = MqttClient(config)
        
        assert client1 is client2
    
    @patch('paho.mqtt.client.Client')
    def test_mqtt_client_initialization(self, mock_mqtt_client):
        """Test: MQTT Client initializes correctly"""
        config = MqttConfig(host="localhost", port=1883, client_id="test_client")
        
        client = MqttClient(config)
        
        assert client.config == config
        assert client.connected == False
        assert len(client._history) == 0
    
    @patch('paho.mqtt.client.Client')
    def test_mqtt_client_message_history(self, mock_mqtt_client):
        """Test: Message history management"""
        config = MqttConfig(host="localhost")
        client = MqttClient(config)
        
        # Test adding messages to history
        test_message = {
            "type": "received",
            "topic": "test/topic",
            "payload": {"data": "test"},
            "timestamp": time.time()
        }
        
        client._add_to_history(test_message)
        messages = client.get_messages()
        
        assert len(messages) == 1
        assert messages[0]["topic"] == "test/topic"
        
        # Test clearing history
        client.clear_history()
        messages = client.get_messages()
        assert len(messages) == 0
    
    @patch('paho.mqtt.client.Client')
    def test_mqtt_client_connection_status(self, mock_mqtt_client):
        """Test: Connection status reporting"""
        config = MqttConfig(host="localhost", port=1883, client_id="test")
        client = MqttClient(config)
        
        status = client.get_connection_status()
        
        assert status["connected"] == False
        assert status["broker"] == "localhost:1883"
        assert status["client_id"] == "test"
        assert "messages" in status


class TestMqttGateway:
    """Test MQTT Gateway (with mocking)"""
    
    def setup_method(self):
        """Setup for each test"""
        # Reset singleton before each test
        MqttClient.reset_singleton()
    
    def teardown_method(self):
        """Teardown after each test"""
        # Reset singleton after each test
        MqttClient.reset_singleton()
    
    def test_mqtt_gateway_creation(self):
        """Test: MQTT Gateway can be created"""
        gateway = MqttGateway("mock")
        
        assert gateway.environment == "mock"
        assert gateway._connected == False
    
    @patch.object(MqttClient, 'connect')
    @patch.object(MqttClient, '__init__', return_value=None)
    def test_mqtt_gateway_connect(self, mock_init, mock_connect):
        """Test: Gateway connection"""
        mock_connect.return_value = True
        
        gateway = MqttGateway("mock")
        # Mock the client
        gateway._client = Mock()
        gateway._client.connect.return_value = True
        gateway._client.add_on_connect_callback = Mock()
        gateway._client.add_on_disconnect_callback = Mock()
        
        result = gateway.connect()
        
        # Since we're mocking, we can't test the actual connection
        # but we can test that the method exists and returns a boolean
        assert isinstance(result, bool)
    
    def test_mqtt_gateway_is_connected(self):
        """Test: Connection status check"""
        gateway = MqttGateway("mock")
        
        assert gateway.is_connected() == False
        
        # Simulate connection
        gateway._connected = True
        gateway._client = Mock()
        
        assert gateway.is_connected() == True
    
    def test_mqtt_gateway_environment_switch(self):
        """Test: Environment switching"""
        gateway = MqttGateway("mock")
        
        # Test switching to same environment
        result = gateway.switch_environment("mock")
        assert result == True
        
        # Test switching to different environment
        original_env = gateway.environment
        gateway.switch_environment("live")
        
        # Environment should be updated
        assert gateway.environment == "live"
        assert gateway.config.client_id == "omf2_live_client"
    
    def test_mqtt_gateway_message_operations(self):
        """Test: Message operations without client"""
        gateway = MqttGateway("mock")
        
        # Test getting messages when no client
        messages = gateway.get_all_messages()
        assert messages == []
        
        # Test getting recent messages
        recent = gateway.get_recent_messages(10)
        assert recent == []
        
        # Test publishing without client
        result = gateway.publish_message("test/topic", {"data": "test"})
        assert result == False
    
    def test_mqtt_gateway_statistics(self):
        """Test: Message statistics"""
        gateway = MqttGateway("mock")
        
        stats = gateway.get_message_statistics()
        
        assert stats["total"] == 0
        assert stats["sent"] == 0
        assert stats["received"] == 0
        assert stats["topics"] == []


# Integration tests would require actual MQTT broker
class TestMessageCenterIntegration:
    """Integration tests for message center components"""
    
    def test_message_center_workflow(self):
        """Test: Complete message center workflow (mocked)"""
        from omf2.common.env_manager import EnvironmentManager
        
        # Test environment manager
        env_manager = EnvironmentManager()
        env = env_manager.get_current_environment()
        assert env in ["live", "replay", "mock"]
        
        # Test gateway creation
        gateway = MqttGateway(env)
        assert gateway.environment == env
        
        # Test message handler
        handler = MessageHandler()
        assert handler is not None
        
        # Test complete workflow without actual MQTT
        status = gateway.get_connection_status()
        assert "connected" in status
        assert "environment" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])