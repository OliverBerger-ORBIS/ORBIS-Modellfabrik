#!/usr/bin/env python3
"""
Tests für Generic Message Manager
"""

import unittest
from unittest.mock import Mock, patch

from omf2.common.message_manager import (
    MessageManager,
    get_admin_message_manager,
    get_ccu_message_manager,
    get_message_manager,
    get_nodered_message_manager,
)


class TestMessageManager(unittest.TestCase):
    """Test Generic Message Manager"""

    def setUp(self):
        """Setup Test Environment"""
        self.mock_registry_manager = Mock()
        self.mock_mqtt_client = Mock()

        # Mock Registry Manager responses
        self.mock_registry_manager.get_topic_config.return_value = {"qos": 1, "retain": False, "domain": "test"}

        self.mock_registry_manager.get_topic_schema.return_value = {
            "type": "object",
            "properties": {"message": {"type": "string"}, "timestamp": {"type": "string"}},
        }

        # Mock MQTT Client responses
        self.mock_mqtt_client.get_all_buffers.return_value = {
            "test/topic": [
                {"message": "test1", "timestamp": "2025-01-01T00:00:00Z"},
                {"message": "test2", "timestamp": "2025-01-01T00:01:00Z"},
            ]
        }

        self.manager = MessageManager("test", self.mock_registry_manager, self.mock_mqtt_client)

    def test_init(self):
        """Test MessageManager initialization"""
        self.assertEqual(self.manager.domain, "test")
        self.assertEqual(self.manager.registry_manager, self.mock_registry_manager)
        self.assertEqual(self.manager.mqtt_client, self.mock_mqtt_client)

    def test_generate_message_without_params(self):
        """Test message generation without parameters"""
        topic = "test/topic"

        result = self.manager.generate_message(topic)

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "object")
        self.assertIn("properties", result)

    def test_generate_message_with_params(self):
        """Test message generation with parameters"""
        topic = "test/topic"
        params = {"message": "Hello World", "timestamp": "2025-01-01T00:00:00Z"}

        result = self.manager.generate_message(topic, params)

        self.assertIsNotNone(result)
        self.assertEqual(result["message"], "Hello World")
        self.assertEqual(result["timestamp"], "2025-01-01T00:00:00Z")

    def test_generate_message_no_topic_config(self):
        """Test message generation when no topic config exists"""
        self.mock_registry_manager.get_topic_config.return_value = None
        topic = "test/topic"

        result = self.manager.generate_message(topic)

        self.assertIsNone(result)

    def test_generate_message_no_schema(self):
        """Test message generation when no schema exists"""
        self.mock_registry_manager.get_topic_schema.return_value = None
        topic = "test/topic"

        result = self.manager.generate_message(topic)

        self.assertIsNone(result)

    def test_validate_message_success(self):
        """Test successful message validation"""
        topic = "test/topic"
        message = {"message": "Hello World", "timestamp": "2025-01-01T00:00:00Z"}

        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: __import__(name, *args) if name != "jsonschema" else Mock(validate=Mock()),
        ):
            result = self.manager.validate_message(topic, message)

            self.assertEqual(len(result["errors"]), 0)

    def test_validate_message_validation_error(self):
        """Test message validation with validation error"""
        topic = "test/topic"
        message = {"invalid": "message"}

        # Mock jsonschema to raise ValidationError
        mock_jsonschema = Mock()
        validation_error = Exception("Invalid message")
        validation_error.message = "Invalid message"  # Add message attribute
        mock_jsonschema.ValidationError = Exception
        mock_jsonschema.validate.side_effect = validation_error

        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: mock_jsonschema if name == "jsonschema" else __import__(name, *args),
        ):
            result = self.manager.validate_message(topic, message)

            self.assertEqual(len(result["errors"]), 1)
            self.assertIn("Schema validation failed", result["errors"][0])

    def test_validate_message_no_jsonschema(self):
        """Test message validation when jsonschema library is not available"""
        topic = "test/topic"
        message = {"message": "Hello World"}

        with patch("builtins.__import__", side_effect=ImportError("No module named 'jsonschema'")):
            result = self.manager.validate_message(topic, message)

            self.assertEqual(len(result["errors"]), 0)
            self.assertEqual(len(result["warnings"]), 1)
            self.assertIn("jsonschema library not available", result["warnings"][0])

    def test_validate_message_no_schema(self):
        """Test message validation when no schema exists"""
        self.mock_registry_manager.get_topic_schema.return_value = None
        topic = "test/topic"
        message = {"message": "Hello World"}

        result = self.manager.validate_message(topic, message)

        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("No schema found for topic", result["errors"][0])

    def test_get_all_message_buffers(self):
        """Test getting all message buffers"""
        result = self.manager.get_all_message_buffers()

        self.assertIsInstance(result, dict)
        self.assertIn("test/topic", result)
        self.assertEqual(len(result["test/topic"]), 2)

    def test_get_all_message_buffers_no_client(self):
        """Test getting message buffers when no MQTT client is available"""
        manager = MessageManager("test", self.mock_registry_manager, None)

        result = manager.get_all_message_buffers()

        self.assertEqual(result, {})

    def test_clear_message_history(self):
        """Test clearing message history"""
        result = self.manager.clear_message_history()

        self.assertTrue(result)
        self.mock_mqtt_client.clear_buffers.assert_called_once()

    def test_clear_message_history_no_client(self):
        """Test clearing message history when no MQTT client is available"""
        manager = MessageManager("test", self.mock_registry_manager, None)

        result = manager.clear_message_history()

        self.assertFalse(result)

    def test_get_message_count_by_topic(self):
        """Test getting message count by topic"""
        result = self.manager.get_message_count_by_topic()

        self.assertIsInstance(result, dict)
        self.assertIn("test/topic", result)
        self.assertEqual(result["test/topic"], 2)

    def test_get_latest_message_by_topic(self):
        """Test getting latest message by topic"""
        result = self.manager.get_latest_message_by_topic()

        self.assertIsInstance(result, dict)
        self.assertIn("test/topic", result)
        self.assertEqual(result["test/topic"]["message"], "test2")  # Latest message

    def test_deep_merge(self):
        """Test deep merge functionality"""
        base = {"level1": {"level2": "original", "level3": "keep"}, "top_level": "original"}

        update = {"level1": {"level2": "updated", "level4": "new"}, "top_level": "updated", "new_top_level": "new"}

        result = self.manager._deep_merge(base, update)

        self.assertEqual(result["level1"]["level2"], "updated")
        self.assertEqual(result["level1"]["level3"], "keep")
        self.assertEqual(result["level1"]["level4"], "new")
        self.assertEqual(result["top_level"], "updated")
        self.assertEqual(result["new_top_level"], "new")


class TestMessageManagerFactory(unittest.TestCase):
    """Test Message Manager Factory Functions"""

    def test_get_admin_message_manager(self):
        """Test Admin Message Manager factory"""
        manager = get_admin_message_manager()

        self.assertIsInstance(manager, MessageManager)
        self.assertEqual(manager.domain, "admin")

    def test_get_ccu_message_manager(self):
        """Test CCU Message Manager factory"""
        manager = get_ccu_message_manager()

        self.assertIsInstance(manager, MessageManager)
        self.assertEqual(manager.domain, "ccu")

    def test_get_nodered_message_manager(self):
        """Test Node-RED Message Manager factory"""
        manager = get_nodered_message_manager()

        self.assertIsInstance(manager, MessageManager)
        self.assertEqual(manager.domain, "nodered")

    def test_get_message_manager(self):
        """Test generic Message Manager factory"""
        manager = get_message_manager("custom_domain")

        self.assertIsInstance(manager, MessageManager)
        self.assertEqual(manager.domain, "custom_domain")


if __name__ == "__main__":
    unittest.main()
