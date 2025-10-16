#!/usr/bin/env python3
"""
Tests for Admin Message Manager
"""

import unittest
from unittest.mock import Mock, patch

from omf2.admin.admin_message_manager import AdminMessageManager, get_admin_message_manager


class TestAdminMessageManager(unittest.TestCase):
    """Test cases for Admin Message Manager"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_registry_manager = Mock()
        self.mock_mqtt_client = Mock()

        # Mock registry manager methods
        self.mock_registry_manager.get_topic_config.return_value = {"qos": 1, "retain": False}
        self.mock_registry_manager.get_topic_schema.return_value = {
            "type": "object",
            "properties": {"message": {"type": "string"}, "timestamp": {"type": "string"}},
        }

        # Mock MQTT client methods
        self.mock_mqtt_client.get_all_buffers.return_value = {
            "test/topic": [
                {"message": "test1", "timestamp": "2025-01-01T00:00:00Z"},
                {"message": "test2", "timestamp": "2025-01-01T00:01:00Z"},
            ]
        }
        self.mock_mqtt_client.clear_buffers.return_value = True

        self.manager = AdminMessageManager(
            registry_manager=self.mock_registry_manager, mqtt_client=self.mock_mqtt_client
        )

    def test_init(self):
        """Test AdminMessageManager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.registry_manager, self.mock_registry_manager)
        self.assertEqual(self.manager.mqtt_client, self.mock_mqtt_client)

    def test_generate_message_with_params(self):
        """Test message generation with parameters"""
        topic = "test/topic"
        params = {"message": "Hello World", "timestamp": "2025-01-01T00:00:00Z"}

        result = self.manager.generate_message(topic, params)

        self.assertIsNotNone(result)
        self.assertEqual(result["message"], "Hello World")
        self.assertEqual(result["timestamp"], "2025-01-01T00:00:00Z")

        # Verify registry manager was called
        self.mock_registry_manager.get_topic_config.assert_called_with(topic)
        self.mock_registry_manager.get_topic_schema.assert_called_with(topic)

    def test_generate_message_without_params(self):
        """Test message generation without parameters"""
        topic = "test/topic"

        result = self.manager.generate_message(topic)

        self.assertIsNotNone(result)
        self.assertIn("type", result)
        self.assertIn("properties", result)

    def test_generate_message_no_topic_config(self):
        """Test message generation when no topic config exists"""
        self.mock_registry_manager.get_topic_config.return_value = None

        result = self.manager.generate_message("unknown/topic")

        self.assertIsNone(result)

    def test_generate_message_no_schema(self):
        """Test message generation when no schema exists"""
        self.mock_registry_manager.get_topic_schema.return_value = None

        result = self.manager.generate_message("test/topic")

        self.assertIsNone(result)

    @patch("jsonschema.validate")
    def test_validate_message_success(self, mock_validate):
        """Test successful message validation"""
        topic = "test/topic"
        message = {"message": "Hello World", "timestamp": "2025-01-01T00:00:00Z"}

        result = self.manager.validate_message(topic, message)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["warnings"], [])
        mock_validate.assert_called_once()

    @patch("jsonschema.validate")
    def test_validate_message_validation_error(self, mock_validate):
        """Test message validation with validation error"""
        from jsonschema import ValidationError

        mock_validate.side_effect = ValidationError("Invalid message")

        topic = "test/topic"
        message = {"invalid": "message"}

        result = self.manager.validate_message(topic, message)

        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("Schema validation failed", result["errors"][0])

    def test_validate_message_no_schema(self):
        """Test message validation when no schema exists"""
        self.mock_registry_manager.get_topic_schema.return_value = None

        result = self.manager.validate_message("unknown/topic", {"test": "message"})

        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("No schema found", result["errors"][0])

    @patch("jsonschema.validate", side_effect=ImportError)
    def test_validate_message_no_jsonschema(self, mock_validate):
        """Test message validation when jsonschema library is not available"""
        topic = "test/topic"
        message = {"message": "Hello World"}

        result = self.manager.validate_message(topic, message)

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("jsonschema library not available", result["warnings"][0])

    def test_get_all_message_buffers(self):
        """Test getting all message buffers"""
        result = self.manager.get_all_message_buffers()

        self.assertIsInstance(result, dict)
        self.assertIn("test/topic", result)
        self.assertEqual(len(result["test/topic"]), 2)

        self.mock_mqtt_client.get_all_buffers.assert_called_once()

    def test_get_all_message_buffers_no_client(self):
        """Test getting message buffers when no MQTT client"""
        manager_no_client = AdminMessageManager(registry_manager=self.mock_registry_manager)

        result = manager_no_client.get_all_message_buffers()

        self.assertEqual(result, {})

    def test_clear_message_history(self):
        """Test clearing message history"""
        result = self.manager.clear_message_history()

        self.assertTrue(result)
        self.mock_mqtt_client.clear_buffers.assert_called_once()

    def test_clear_message_history_no_client(self):
        """Test clearing message history when no MQTT client"""
        manager_no_client = AdminMessageManager(registry_manager=self.mock_registry_manager)

        result = manager_no_client.clear_message_history()

        self.assertFalse(result)

    def test_get_message_count_by_topic(self):
        """Test getting message count by topic"""
        result = self.manager.get_message_count_by_topic()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["test/topic"], 2)

    def test_get_latest_message_by_topic(self):
        """Test getting latest message by topic"""
        result = self.manager.get_latest_message_by_topic()

        self.assertIsInstance(result, dict)
        self.assertIn("test/topic", result)
        self.assertEqual(result["test/topic"]["message"], "test2")  # Latest message

    def test_deep_merge(self):
        """Test deep merge functionality"""
        base = {"level1": {"level2": "original", "level2_new": "new"}, "level1_new": "new_value"}
        update = {"level1": {"level2": "updated"}, "level1_new": "updated_value"}

        result = self.manager.message_manager._deep_merge(base, update)

        self.assertEqual(result["level1"]["level2"], "updated")
        self.assertEqual(result["level1"]["level2_new"], "new")
        self.assertEqual(result["level1_new"], "updated_value")


class TestAdminMessageManagerFactory(unittest.TestCase):
    """Test cases for Admin Message Manager Factory"""

    def test_get_admin_message_manager_singleton(self):
        """Test singleton pattern for factory function"""
        # Clear any existing instance
        if hasattr(get_admin_message_manager, "_instance"):
            delattr(get_admin_message_manager, "_instance")

        manager1 = get_admin_message_manager()
        manager2 = get_admin_message_manager()

        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, AdminMessageManager)


if __name__ == "__main__":
    unittest.main()
