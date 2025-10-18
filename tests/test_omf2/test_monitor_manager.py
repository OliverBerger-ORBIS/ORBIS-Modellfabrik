#!/usr/bin/env python3
"""
Unit Tests für Monitor Manager
"""

import unittest
from unittest.mock import patch

from omf2.ccu.monitor_manager import MonitorManager, get_monitor_manager


class TestMonitorManager(unittest.TestCase):
    """Unit Tests für MonitorManager"""

    def setUp(self):
        """Test Setup"""
        self.monitor_manager = MonitorManager()

    def test_classify_topic_fts(self):
        """Test FTS Topic Classification"""
        result = self.monitor_manager.classify_topic("fts/v1/ff/5iO4/state")
        self.assertEqual(result, "FTS")

    def test_classify_topic_module(self):
        """Test Module Topic Classification"""
        result = self.monitor_manager.classify_topic("module/v1/ff/SVR3QA0022/connection")
        self.assertEqual(result, "Module")

    def test_classify_topic_ccu(self):
        """Test CCU Topic Classification"""
        result = self.monitor_manager.classify_topic("ccu/order/active")
        self.assertEqual(result, "CCU")

    def test_classify_topic_txt(self):
        """Test TXT Topic Classification"""
        result = self.monitor_manager.classify_topic("/j1/txt/1/f/i/stock")
        self.assertEqual(result, "TXT")

    def test_classify_topic_other(self):
        """Test Other Topic Classification"""
        result = self.monitor_manager.classify_topic("unknown/topic")
        self.assertEqual(result, "Other")

    def test_process_message_fts(self):
        """Test FTS Message Processing"""
        self.monitor_manager.process_message("fts/v1/ff/5iO4/state", {"test": "data"})

        self.assertIn("fts/v1/ff/5iO4/state", self.monitor_manager.all_topics)
        self.assertIn("fts/v1/ff/5iO4/state", self.monitor_manager.module_fts_topics)

    def test_process_message_module(self):
        """Test Module Message Processing"""
        self.monitor_manager.process_message("module/v1/ff/SVR3QA0022/connection", {"test": "data"})

        self.assertIn("module/v1/ff/SVR3QA0022/connection", self.monitor_manager.all_topics)
        self.assertIn("module/v1/ff/SVR3QA0022/connection", self.monitor_manager.module_fts_topics)

    def test_process_message_ccu(self):
        """Test CCU Message Processing"""
        self.monitor_manager.process_message("ccu/order/active", {"test": "data"})

        self.assertIn("ccu/order/active", self.monitor_manager.all_topics)
        self.assertIn("ccu/order/active", self.monitor_manager.ccu_topics)

    def test_process_message_txt(self):
        """Test TXT Message Processing"""
        self.monitor_manager.process_message("/j1/txt/1/f/i/stock", {"test": "data"})

        self.assertIn("/j1/txt/1/f/i/stock", self.monitor_manager.all_topics)
        self.assertIn("/j1/txt/1/f/i/stock", self.monitor_manager.txt_topics)

    def test_get_filter_lists(self):
        """Test Filter Lists Retrieval"""
        # Add some test topics
        self.monitor_manager.process_message("fts/v1/ff/5iO4/state", {})
        self.monitor_manager.process_message("module/v1/ff/SVR3QA0022/connection", {})
        self.monitor_manager.process_message("ccu/order/active", {})
        self.monitor_manager.process_message("/j1/txt/1/f/i/stock", {})

        filter_lists = self.monitor_manager.get_filter_lists()

        self.assertIn("all_topics", filter_lists)
        self.assertIn("module_fts_topics", filter_lists)
        self.assertIn("ccu_topics", filter_lists)
        self.assertIn("txt_topics", filter_lists)

        self.assertEqual(len(filter_lists["all_topics"]), 4)
        self.assertEqual(len(filter_lists["module_fts_topics"]), 2)
        self.assertEqual(len(filter_lists["ccu_topics"]), 1)
        self.assertEqual(len(filter_lists["txt_topics"]), 1)

    def test_get_topic_count(self):
        """Test Topic Count Retrieval"""
        # Add some test topics
        self.monitor_manager.process_message("fts/v1/ff/5iO4/state", {})
        self.monitor_manager.process_message("module/v1/ff/SVR3QA0022/connection", {})
        self.monitor_manager.process_message("ccu/order/active", {})
        self.monitor_manager.process_message("/j1/txt/1/f/i/stock", {})

        counts = self.monitor_manager.get_topic_count()

        self.assertEqual(counts["all"], 4)
        self.assertEqual(counts["module_fts"], 2)
        self.assertEqual(counts["ccu"], 1)
        self.assertEqual(counts["txt"], 1)
        self.assertEqual(counts["other"], 0)

    def test_clear_topics(self):
        """Test Topic Lists Clearing"""
        # Add some test topics
        self.monitor_manager.process_message("fts/v1/ff/5iO4/state", {})
        self.monitor_manager.process_message("module/v1/ff/SVR3QA0022/connection", {})

        # Clear topics
        self.monitor_manager.clear_topics()

        self.assertEqual(len(self.monitor_manager.all_topics), 0)
        self.assertEqual(len(self.monitor_manager.module_fts_topics), 0)
        self.assertEqual(len(self.monitor_manager.ccu_topics), 0)
        self.assertEqual(len(self.monitor_manager.txt_topics), 0)

    def test_singleton_pattern(self):
        """Test Singleton Pattern"""
        manager1 = get_monitor_manager()
        manager2 = get_monitor_manager()

        self.assertIs(manager1, manager2)

    def test_process_message_error_handling(self):
        """Test Error Handling in Process Message"""
        with patch.object(self.monitor_manager, "classify_topic", side_effect=Exception("Test error")):
            # Should not raise exception
            self.monitor_manager.process_message("test/topic", {"test": "data"})

    def test_classify_topic_error_handling(self):
        """Test Error Handling in Classify Topic"""
        # Test with None topic
        result = self.monitor_manager.classify_topic(None)
        self.assertEqual(result, "Other")


if __name__ == "__main__":
    unittest.main()
