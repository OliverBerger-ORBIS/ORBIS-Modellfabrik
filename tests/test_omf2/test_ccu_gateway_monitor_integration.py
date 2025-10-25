#!/usr/bin/env python3
"""
End-to-End Test für CCU Gateway Monitor Manager Integration
"""

import unittest
from unittest.mock import Mock, patch

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.monitor_manager import MonitorManager


class TestCCUGatewayMonitorIntegration(unittest.TestCase):
    """End-to-End Test für CCU Gateway Monitor Manager Integration"""

    def setUp(self):
        """Test Setup"""
        # Mock MQTT Client
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client._get_subscribed_topics.return_value = [
            "fts/v1/ff/5iO4/state",
            "fts/v1/ff/5iO4/connection",
            "module/v1/ff/SVR3QA0022/state",
            "module/v1/ff/SVR3QA0022/connection",
            "ccu/order/active",
            "/j1/txt/1/f/o/order",
            "/j1/txt/1/f/i/stock",
        ]

        # Mock Message Manager
        self.mock_message_manager = Mock()
        self.mock_message_manager.get_all_buffers.return_value = {
            "fts/v1/ff/5iO4/state": ["message1"],
            "module/v1/ff/SVR3QA0022/state": ["message2"],
            "ccu/order/active": ["message3"],
        }

        # Mock Registry Manager
        self.mock_registry_manager = Mock()
        self.mock_registry_manager.get_gateway_config.return_value = {
            "routing_hints": {},
            "refresh_triggers": {}
        }

    def test_ccu_gateway_monitor_manager_initialization(self):
        """Test CCU Gateway Monitor Manager Initialization"""
        with patch("omf2.ccu.ccu_gateway.get_ccu_message_manager", return_value=self.mock_message_manager), patch(
            "omf2.ccu.ccu_gateway.get_registry_manager", return_value=self.mock_registry_manager
        ), patch("omf2.ccu.ccu_gateway.get_monitor_manager") as mock_get_monitor_manager:

            # Create Monitor Manager mock
            mock_monitor_manager = Mock(spec=MonitorManager)
            mock_get_monitor_manager.return_value = mock_monitor_manager

            # Initialize CCU Gateway
            gateway = CcuGateway(mqtt_client=self.mock_mqtt_client)

            # Verify Monitor Manager was initialized
            self.assertIsNotNone(gateway.monitor_manager)
            mock_get_monitor_manager.assert_called_once_with(registry_manager=self.mock_registry_manager)

    def test_ccu_gateway_message_routing_to_monitor_manager(self):
        """Test Message Routing to Monitor Manager"""
        with patch("omf2.ccu.ccu_gateway.get_ccu_message_manager", return_value=self.mock_message_manager), patch(
            "omf2.ccu.ccu_gateway.get_registry_manager", return_value=self.mock_registry_manager
        ), patch("omf2.ccu.ccu_gateway.get_monitor_manager") as mock_get_monitor_manager:

            # Create Monitor Manager mock
            mock_monitor_manager = Mock(spec=MonitorManager)
            mock_get_monitor_manager.return_value = mock_monitor_manager

            # Initialize CCU Gateway
            gateway = CcuGateway(mqtt_client=self.mock_mqtt_client)

            # Test message routing
            test_topic = "fts/v1/ff/5iO4/state"
            test_message = {"test": "data"}
            test_meta = {"timestamp": "2025-01-01T10:00:00"}

            # Route message
            result = gateway._route_ccu_message(test_topic, test_message, test_meta)

            # Verify Monitor Manager received the message
            mock_monitor_manager.process_message.assert_called_with(test_topic, test_message, test_meta)
            self.assertTrue(result)

    def test_ccu_gateway_get_subscribed_topics(self):
        """Test CCU Gateway get_subscribed_topics"""
        with patch("omf2.ccu.ccu_gateway.get_ccu_message_manager", return_value=self.mock_message_manager), patch(
            "omf2.ccu.ccu_gateway.get_registry_manager", return_value=self.mock_registry_manager
        ), patch("omf2.ccu.ccu_gateway.get_monitor_manager") as mock_get_monitor_manager:

            # Create Monitor Manager mock with filter lists
            mock_monitor_manager = Mock(spec=MonitorManager)
            mock_monitor_manager.get_filter_lists.return_value = {
                "all_topics": [
                    "fts/v1/ff/5iO4/state",
                    "fts/v1/ff/5iO4/connection",
                    "module/v1/ff/SVR3QA0022/state",
                    "module/v1/ff/SVR3QA0022/connection",
                    "ccu/order/active",
                    "/j1/txt/1/f/o/order",
                    "/j1/txt/1/f/i/stock",
                ],
                "module_fts_topics": [
                    "fts/v1/ff/5iO4/state",
                    "fts/v1/ff/5iO4/connection",
                    "module/v1/ff/SVR3QA0022/state",
                    "module/v1/ff/SVR3QA0022/connection",
                ],
            }
            mock_get_monitor_manager.return_value = mock_monitor_manager

            # Initialize CCU Gateway
            gateway = CcuGateway(mqtt_client=self.mock_mqtt_client)

            # Test get_subscribed_topics
            topics = gateway.get_subscribed_topics()

            # Verify topics are returned
            self.assertEqual(len(topics), 7)
            self.assertIn("fts/v1/ff/5iO4/state", topics)
            self.assertIn("ccu/order/active", topics)

    def test_ccu_gateway_get_module_fts_topics(self):
        """Test CCU Gateway get_module_fts_topics"""
        with patch("omf2.ccu.ccu_gateway.get_ccu_message_manager", return_value=self.mock_message_manager), patch(
            "omf2.ccu.ccu_gateway.get_registry_manager", return_value=self.mock_registry_manager
        ), patch("omf2.ccu.ccu_gateway.get_monitor_manager") as mock_get_monitor_manager:

            # Create Monitor Manager mock with filter lists
            mock_monitor_manager = Mock(spec=MonitorManager)
            mock_monitor_manager.get_filter_lists.return_value = {
                "module_fts_topics": [
                    "fts/v1/ff/5iO4/state",
                    "fts/v1/ff/5iO4/connection",
                    "module/v1/ff/SVR3QA0022/state",
                    "module/v1/ff/SVR3QA0022/connection",
                ]
            }
            mock_get_monitor_manager.return_value = mock_monitor_manager

            # Initialize CCU Gateway
            gateway = CcuGateway(mqtt_client=self.mock_mqtt_client)

            # Test get_module_fts_topics
            topics = gateway.get_module_fts_topics()

            # Verify only module/FTS topics are returned
            self.assertEqual(len(topics), 4)
            self.assertIn("fts/v1/ff/5iO4/state", topics)
            self.assertIn("module/v1/ff/SVR3QA0022/state", topics)

    def test_ccu_gateway_get_all_message_buffers(self):
        """Test CCU Gateway get_all_message_buffers in the presence of MessageManager"""
        with patch("omf2.ccu.ccu_gateway.get_ccu_message_manager", return_value=self.mock_message_manager), patch(
            "omf2.ccu.ccu_gateway.get_registry_manager", return_value=self.mock_registry_manager
        ), patch("omf2.ccu.ccu_gateway.get_monitor_manager") as mock_get_monitor_manager:

            # Create Monitor Manager mock
            mock_monitor_manager = Mock(spec=MonitorManager)
            mock_get_monitor_manager.return_value = mock_monitor_manager

            # Initialize CCU Gateway
            gateway = CcuGateway(mqtt_client=self.mock_mqtt_client)

            # Test get_all_message_buffers
            buffers = gateway.get_all_message_buffers()

            # Verify buffers are returned
            self.assertIsNotNone(buffers)
            self.mock_message_manager.get_all_message_buffers.assert_called_once()

    def test_monitor_manager_processes_all_message_types(self):
        """Test Monitor Manager processes all message types"""
        with patch("omf2.ccu.ccu_gateway.get_ccu_message_manager", return_value=self.mock_message_manager), patch(
            "omf2.ccu.ccu_gateway.get_registry_manager", return_value=self.mock_registry_manager
        ), patch("omf2.ccu.ccu_gateway.get_monitor_manager") as mock_get_monitor_manager:

            # Create Monitor Manager mock
            mock_monitor_manager = Mock(spec=MonitorManager)
            mock_get_monitor_manager.return_value = mock_monitor_manager

            # Initialize CCU Gateway
            gateway = CcuGateway(mqtt_client=self.mock_mqtt_client)

            # Test different message types
            test_messages = [
                ("fts/v1/ff/5iO4/state", {"state": "active"}),
                ("module/v1/ff/SVR3QA0022/connection", {"connected": True}),
                ("ccu/order/active", {"orderId": "123"}),
                ("/j1/txt/1/f/o/order", {"order": "test"}),
            ]

            for topic, message in test_messages:
                result = gateway._route_ccu_message(topic, message)
                self.assertTrue(result)
                mock_monitor_manager.process_message.assert_called_with(topic, message, None)


if __name__ == "__main__":
    unittest.main()
