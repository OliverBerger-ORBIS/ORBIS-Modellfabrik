#!/usr/bin/env python3
"""
Tests für Generic Topic Manager
"""

import unittest
from unittest.mock import Mock

from omf2.common.topic_manager import (
    TopicManager,
    get_admin_topic_manager,
    get_ccu_topic_manager,
    get_nodered_topic_manager,
    get_topic_manager,
)


class TestTopicManager(unittest.TestCase):
    """Test Generic Topic Manager"""

    def setUp(self):
        """Setup Test Environment"""
        self.mock_registry_manager = Mock()

        # Mock Registry Manager responses
        self.mock_registry_manager.get_topics.return_value = {
            "test/topic1": {"qos": 1, "retain": False},
            "test/topic2": {"qos": 0, "retain": True},
            "ccu/command": {"qos": 2, "retain": False},
            "admin/log": {"qos": 1, "retain": False},
        }

        self.mock_registry_manager.get_topic_config.return_value = {"qos": 1, "retain": False, "domain": "test"}

        self.mock_registry_manager.get_topic_schema.return_value = {
            "type": "object",
            "properties": {"message": {"type": "string"}, "timestamp": {"type": "string"}},
        }

        self.mock_registry_manager.get_mqtt_clients.return_value = {
            "mqtt_clients": {
                "test_mqtt_client": {
                    "subscribed_topics": [{"topic": "test/subscribe1"}, {"topic": "test/subscribe2"}],
                    "published_topics": [{"topic": "test/publish1"}, {"topic": "test/publish2"}],
                }
            }
        }

        self.manager = TopicManager("test", self.mock_registry_manager)

    def test_init(self):
        """Test TopicManager initialization"""
        self.assertEqual(self.manager.domain, "test")
        self.assertEqual(self.manager.registry_manager, self.mock_registry_manager)

    def test_get_all_topics(self):
        """Test getting all topics"""
        result = self.manager.get_all_topics()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        self.assertIn("test/topic1", result)
        self.assertIn("ccu/command", result)

    def test_get_topic_schemas(self):
        """Test getting topic schemas"""
        result = self.manager.get_topic_schemas()

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 4)  # All topics should have schemas
        self.assertIn("test/topic1", result)
        self.assertIsInstance(result["test/topic1"], dict)

    def test_get_topic_config(self):
        """Test getting topic configuration"""
        topic = "test/topic1"

        result = self.manager.get_topic_config(topic)

        self.assertIsNotNone(result)
        self.assertEqual(result["qos"], 1)
        self.assertEqual(result["retain"], False)

    def test_get_topic_schema(self):
        """Test getting topic schema"""
        topic = "test/topic1"

        result = self.manager.get_topic_schema(topic)

        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "object")
        self.assertIn("properties", result)

    def test_get_domain_topics(self):
        """Test getting domain-specific topics"""
        result = self.manager.get_domain_topics("test")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)  # 2 subscribed + 2 published
        self.assertIn("test/subscribe1", result)
        self.assertIn("test/publish1", result)

    def test_get_published_topics(self):
        """Test getting published topics"""
        result = self.manager.get_published_topics("test")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("test/publish1", result)
        self.assertIn("test/publish2", result)

    def test_get_subscribed_topics(self):
        """Test getting subscribed topics"""
        result = self.manager.get_subscribed_topics("test")

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("test/subscribe1", result)
        self.assertIn("test/subscribe2", result)

    def test_analyze_topic(self):
        """Test topic analysis"""
        topic = "test/topic1"

        result = self.manager.analyze_topic(topic)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["topic"], topic)
        self.assertTrue(result["exists"])
        self.assertTrue(result["has_schema"])
        self.assertTrue(result["has_config"])
        self.assertIsInstance(result["domains"], list)

    def test_get_topics_by_pattern(self):
        """Test getting topics by pattern"""
        pattern = "test/*"

        result = self.manager.get_topics_by_pattern(pattern)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # test/topic1, test/topic2
        self.assertIn("test/topic1", result)
        self.assertIn("test/topic2", result)

    def test_get_topics_by_pattern_exact(self):
        """Test getting topics by exact pattern"""
        pattern = "test/topic1"

        result = self.manager.get_topics_by_pattern(pattern)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn("test/topic1", result)

    def test_validate_topic_structure_valid(self):
        """Test validating valid topic structure"""
        topic = "test/valid/topic"

        result = self.manager.validate_topic_structure(topic)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["topic"], topic)
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_validate_topic_structure_invalid_wildcards(self):
        """Test validating topic with invalid wildcards"""
        topic = "test/+/invalid/#/topic"

        result = self.manager.validate_topic_structure(topic)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["topic"], topic)
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)

    def test_validate_topic_structure_multi_level_wildcard(self):
        """Test validating topic with multi-level wildcard not at end"""
        topic = "test/#/invalid"

        result = self.manager.validate_topic_structure(topic)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["topic"], topic)
        self.assertFalse(result["valid"])
        self.assertIn("Multi-level wildcard # must be at the end", result["errors"])

    def test_validate_topic_structure_empty(self):
        """Test validating empty topic"""
        topic = ""

        result = self.manager.validate_topic_structure(topic)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["topic"], topic)
        self.assertFalse(result["valid"])
        self.assertIn("Topic is empty", result["errors"])

    def test_get_topic_config_nonexistent(self):
        """Test getting config for nonexistent topic"""
        self.mock_registry_manager.get_topic_config.return_value = None
        topic = "nonexistent/topic"

        result = self.manager.get_topic_config(topic)

        self.assertIsNone(result)

    def test_get_topic_schema_nonexistent(self):
        """Test getting schema for nonexistent topic"""
        self.mock_registry_manager.get_topic_schema.return_value = None
        topic = "nonexistent/topic"

        result = self.manager.get_topic_schema(topic)

        self.assertIsNone(result)

    def test_analyze_topic_nonexistent(self):
        """Test analyzing nonexistent topic"""
        self.mock_registry_manager.get_topics.return_value = {}
        self.mock_registry_manager.get_topic_schema.return_value = None
        self.mock_registry_manager.get_topic_config.return_value = None
        topic = "nonexistent/topic"

        result = self.manager.analyze_topic(topic)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["topic"], topic)
        self.assertFalse(result["exists"])
        self.assertFalse(result["has_schema"])
        self.assertFalse(result["has_config"])


class TestTopicManagerFactory(unittest.TestCase):
    """Test Topic Manager Factory Functions"""

    def test_get_admin_topic_manager(self):
        """Test Admin Topic Manager factory"""
        manager = get_admin_topic_manager()

        self.assertIsInstance(manager, TopicManager)
        self.assertEqual(manager.domain, "admin")

    def test_get_ccu_topic_manager(self):
        """Test CCU Topic Manager factory"""
        manager = get_ccu_topic_manager()

        self.assertIsInstance(manager, TopicManager)
        self.assertEqual(manager.domain, "ccu")

    def test_get_nodered_topic_manager(self):
        """Test Node-RED Topic Manager factory"""
        manager = get_nodered_topic_manager()

        self.assertIsInstance(manager, TopicManager)
        self.assertEqual(manager.domain, "nodered")

    def test_get_topic_manager(self):
        """Test generic Topic Manager factory"""
        manager = get_topic_manager("custom_domain")

        self.assertIsInstance(manager, TopicManager)
        self.assertEqual(manager.domain, "custom_domain")


if __name__ == "__main__":
    unittest.main()
