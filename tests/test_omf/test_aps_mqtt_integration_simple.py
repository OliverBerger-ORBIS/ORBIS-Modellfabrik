#!/usr/bin/env python3
"""
Einfache Tests für APS MQTT Integration (ohne Registry-Abhängigkeit)
Version: 1.0.0
"""

import json
from unittest.mock import Mock, patch

import pytest
from omf.dashboard.tools.mqtt_config import MqttConfig
from omf.dashboard.tools.omf_mqtt_client import OmfMqttClient
from omf.tools.aps_mqtt_integration import APSMqttIntegration


class TestAPSMqttIntegrationSimple:
    """Einfache Test-Klasse für APS MQTT Integration"""

    @pytest.fixture
    def mock_mqtt_client(self):
        """Mock MQTT Client"""
        client = Mock(spec=OmfMqttClient)
        client.connected = True
        client.subscribe = Mock()
        client.publish = Mock(return_value=True)
        client._subscribed = set()
        return client

    @pytest.fixture
    def aps_integration(self, mock_mqtt_client):
        """APS Integration Instance mit Mock Managers"""
        with patch('omf.tools.aps_mqtt_integration.VDA5050OrderManager') as mock_vda5050, \
             patch('omf.tools.aps_mqtt_integration.APSTXTControllerManager') as mock_txt, \
             patch('omf.tools.aps_mqtt_integration.APSSystemControlManager') as mock_sys:

            # Mock VDA5050 Manager
            mock_vda5050_instance = Mock()
            mock_vda5050_instance.create_storage_order.return_value = {
                "orderId": "test_order_001",
                "nodes": [{
                    "actions": [{
                        "parameters": {"color": "RED", "workpieceId": "WP_001"}
                    }]
                }]
            }
            mock_vda5050_instance.create_retrieval_order.return_value = {
                "orderId": "test_order_002",
                "nodes": [{
                    "actions": [{
                        "parameters": {"color": "BLUE", "workpieceId": "WP_002"}
                    }]
                }]
            }
            mock_vda5050_instance.send_instant_action.return_value = {
                "instantActions": [{
                    "actionType": "camera_adjustment",
                    "parameters": {"direction": "up", "angle": 10}
                }]
            }
            mock_vda5050_instance.get_active_orders.return_value = {}
            mock_vda5050_instance.get_order_history.return_value = []
            mock_vda5050_instance.get_orders_by_color.return_value = []
            mock_vda5050_instance.get_orders_by_status.return_value = []
            mock_vda5050_instance.process_state_message.return_value = None
            mock_vda5050_instance.process_order_response.return_value = None
            mock_vda5050_instance.complete_order.return_value = True
            mock_vda5050_instance.cancel_order.return_value = True
            mock_vda5050_instance.get_order_statistics.return_value = {}
            mock_vda5050.return_value = mock_vda5050_instance

            # Mock TXT Controller Manager
            mock_txt_instance = Mock()
            mock_txt_instance.get_discovered_controllers.return_value = {
                "SVR4H73275": {
                    "serial_number": "SVR4H73275",
                    "moduleType": "DPS",
                    "ip_address": "192.168.0.102",
                    "online": True
                }
            }
            mock_txt_instance.get_controller_by_serial.return_value = {
                "serial_number": "SVR4H73275",
                "moduleType": "DPS",
                "ip_address": "192.168.0.102"
            }
            mock_txt_instance.get_controller_by_ip.return_value = {
                "serial_number": "SVR4H73275",
                "moduleType": "DPS",
                "ip_address": "192.168.0.102"
            }
            mock_txt_instance.get_online_controllers.return_value = {
                "SVR4H73275": {
                    "serial_number": "SVR4H73275",
                    "moduleType": "DPS",
                    "ip_address": "192.168.0.102",
                    "online": True
                }
            }
            mock_txt_instance.get_expected_topics.return_value = []
            mock_txt_instance.is_controller_online.return_value = True
            mock_txt_instance.get_controller_ip.return_value = "192.168.0.102"
            mock_txt_instance.process_factsheet_message.return_value = None
            mock_txt_instance.process_state_message.return_value = None
            mock_txt_instance.get_controller_status_summary.return_value = {}
            mock_txt_instance._controllers = {}
            mock_txt.return_value = mock_txt_instance

            # Mock System Control Manager
            mock_sys_instance = Mock()
            mock_sys_instance.send_system_command.return_value = {
                "topic": "ccu/set/reset",
                "parameters": {},
                "qos": 2,
                "retain": False
            }
            mock_sys_instance.get_command_statistics.return_value = {}
            mock_sys.return_value = mock_sys_instance

            return APSMqttIntegration(mock_mqtt_client)

    def test_initialization(self, aps_integration, mock_mqtt_client):
        """Test Initialisierung"""
        assert aps_integration.mqtt_client == mock_mqtt_client
        assert aps_integration.vda5050_manager is not None
        assert aps_integration.txt_controller_manager is not None
        assert aps_integration.system_control_manager is not None
        assert len(aps_integration.aps_topics) > 0

    def test_aps_topics_setup(self, aps_integration):
        """Test APS Topics Setup"""
        topics = aps_integration.aps_topics

        # VDA5050 Topics
        assert "factsheet_topics" in topics
        assert "state_topics" in topics
        assert "order_topics" in topics
        assert "instant_action_topics" in topics

        # System Control Topics
        assert "system_control_topics" in topics

        # FTS Topics
        assert "fts_topics" in topics

        # Prüfe Topic-Patterns
        assert any("module/v1/ff/+/factsheet" in topic for topic in topics["factsheet_topics"])
        assert any("ccu/set/+" in topic for topic in topics["system_control_topics"])

    def test_vda5050_order_creation(self, aps_integration):
        """Test VDA5050 Order Creation"""
        # Storage Order
        storage_order = aps_integration.create_storage_order("RED", "WP_001", "DPS")
        assert storage_order["orderId"] is not None
        assert storage_order["nodes"][0]["actions"][0]["parameters"]["color"] == "RED"
        assert storage_order["nodes"][0]["actions"][0]["parameters"]["workpieceId"] == "WP_001"

        # Retrieval Order
        retrieval_order = aps_integration.create_retrieval_order("BLUE", "WP_002", "HBW")
        assert retrieval_order["orderId"] is not None
        assert retrieval_order["nodes"][0]["actions"][0]["parameters"]["color"] == "BLUE"
        assert retrieval_order["nodes"][0]["actions"][0]["parameters"]["workpieceId"] == "WP_002"

    def test_instant_action_creation(self, aps_integration):
        """Test Instant Action Creation"""
        action = aps_integration.send_instant_action(
            "camera_adjustment",
            {"direction": "up", "angle": 10},
            "DPS"
        )
        assert action["instantActions"][0]["actionType"] == "camera_adjustment"
        assert action["instantActions"][0]["parameters"]["direction"] == "up"
        assert action["instantActions"][0]["parameters"]["angle"] == 10

    def test_system_commands(self, aps_integration, mock_mqtt_client):
        """Test System Commands"""
        # Factory Reset
        result = aps_integration.reset_factory()
        assert result is True
        mock_mqtt_client.publish.assert_called()

        # FTS Charge
        result = aps_integration.charge_fts()
        assert result is True

        # Park Factory
        result = aps_integration.park_factory()
        assert result is True

        # System Calibration
        result = aps_integration.calibrate_system()
        assert result is True

    def test_order_publishing(self, aps_integration, mock_mqtt_client):
        """Test Order Publishing"""
        order = aps_integration.create_storage_order("WHITE", "WP_003")

        # Publish Order
        result = aps_integration.publish_order(order, "DPS")
        assert result is True
        mock_mqtt_client.publish.assert_called()

        # Publish Instant Action
        action = aps_integration.send_instant_action("nfc_read", {}, "DPS")
        result = aps_integration.publish_instant_action(action, "DPS")
        assert result is True

    def test_controller_discovery(self, aps_integration):
        """Test Controller Discovery"""
        # Mock factsheet message
        factsheet_topic = "module/v1/ff/SVR4H73275/factsheet"
        factsheet_payload = json.dumps({
            "moduleId": "SVR4H73275",
            "moduleType": "DPS",
            "version": "1.0.0",
            "timestamp": "2025-09-19T10:30:00Z",
            "capabilities": ["warehouse", "nfc", "camera"]
        })

        # Process factsheet
        aps_integration._handle_factsheet_message(factsheet_topic, factsheet_payload.encode())

        # Check discovered controllers
        controllers = aps_integration.get_discovered_controllers()
        assert "SVR4H73275" in controllers
        assert controllers["SVR4H73275"]["moduleType"] == "DPS"

    def test_state_message_handling(self, aps_integration):
        """Test State Message Handling"""
        # Mock state message
        state_topic = "module/v1/ff/SVR4H73275/state"
        state_payload = json.dumps({
            "orderId": "order_001",
            "orderUpdateId": 0,
            "timestamp": "2025-09-19T10:30:00Z",
            "version": "2.0.0",
            "nodeStates": [],
            "edgeStates": []
        })

        # Process state message
        aps_integration._handle_state_message(state_topic, state_payload.encode())

        # Check if processed (no exception should be raised)
        assert True

    def test_aps_status(self, aps_integration):
        """Test APS Status"""
        status = aps_integration.get_aps_status()

        assert "controllers" in status
        assert "orders" in status
        assert "system_commands" in status
        assert "mqtt_connected" in status
        assert "subscribed_topics" in status

        assert status["mqtt_connected"] is True

    def test_utility_functions(self, aps_integration):
        """Test Utility Functions"""
        # Mock controller
        aps_integration.txt_controller_manager._controllers = {
            "SVR4H73275": {
                "serial_number": "SVR4H73275",
                "ip_address": "192.168.0.102",
                "online": True
            }
        }

        # Test utility functions
        assert aps_integration.is_controller_online("SVR4H73275") is True
        assert aps_integration.get_controller_ip("SVR4H73275") == "192.168.0.102"

        # Test order filtering
        orders = aps_integration.get_orders_by_color("RED")
        assert isinstance(orders, list)

        orders = aps_integration.get_orders_by_status("RUNNING")
        assert isinstance(orders, list)

    def test_error_handling(self, aps_integration):
        """Test Error Handling"""
        # Invalid JSON
        aps_integration._handle_factsheet_message("test/topic", b"invalid json")
        # Should not raise exception

        # Invalid topic
        aps_integration._handle_state_message("invalid/topic", b'{"test": "data"}')
        # Should not raise exception

        assert True  # If we get here, error handling worked


class TestOmfMqttClientAPSIntegrationSimple:
    """Einfache Tests für OmfMqttClient APS Integration"""

    @pytest.fixture
    def mqtt_config(self):
        """Mock MQTT Config"""
        config = Mock(spec=MqttConfig)
        config.host = "localhost"
        config.port = 1883
        config.username = "test"
        config.password = "test"
        config.client_id = "test_client"
        config.keepalive = 60
        config.clean_session = True
        config.protocol = 4
        return config

    @pytest.fixture
    def mock_mqtt_client(self, mqtt_config):
        """Mock MQTT Client mit APS Integration"""
        with patch('omf.dashboard.tools.omf_mqtt_client.mqtt.Client'):
            client = OmfMqttClient(mqtt_config)
            client.connected = True
            return client

    def test_aps_integration_enable(self, mock_mqtt_client):
        """Test APS Integration Enable"""
        with patch('omf.tools.aps_mqtt_integration.APSMqttIntegration') as mock_aps:
            mock_aps_instance = Mock()
            mock_aps.return_value = mock_aps_instance

            # Enable APS Integration
            aps_integration = mock_mqtt_client.enable_aps_integration()

            assert aps_integration is not None
            assert mock_mqtt_client.is_aps_enabled() is True
            assert mock_mqtt_client.get_aps_integration() == aps_integration

    def test_aps_integration_disable(self, mock_mqtt_client):
        """Test APS Integration Disable"""
        # Initially disabled
        assert mock_mqtt_client.is_aps_enabled() is False
        assert mock_mqtt_client.get_aps_integration() is None

        with patch('omf.tools.aps_mqtt_integration.APSMqttIntegration') as mock_aps:
            mock_aps_instance = Mock()
            mock_aps.return_value = mock_aps_instance

            # Enable and check
            aps_integration = mock_mqtt_client.enable_aps_integration()
            assert mock_mqtt_client.is_aps_enabled() is True

            # Get integration
            retrieved = mock_mqtt_client.get_aps_integration()
            assert retrieved == aps_integration


if __name__ == "__main__":
    pytest.main([__file__])
