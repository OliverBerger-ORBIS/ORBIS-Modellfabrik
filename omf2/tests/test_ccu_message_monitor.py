#!/usr/bin/env python3
"""
Tests for CCU Message Monitor Component
"""

import time
import unittest


class TestCCUMessageMonitor(unittest.TestCase):
    """Test CCU Message Monitor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        from omf2.ui.ccu.ccu_message_monitor.ccu_message_monitor_component import (
            _apply_filters,
            _detect_message_type,
            _detect_module_or_fts,
            _detect_status_category,
            _extract_serial_from_payload,
            _prepare_dataframe,
        )

        self._extract_serial = _extract_serial_from_payload
        self._detect_status = _detect_status_category
        self._detect_module = _detect_module_or_fts
        self._detect_type = _detect_message_type
        self._prepare_df = _prepare_dataframe
        self._apply_filters = _apply_filters

    def test_extract_serial_from_payload(self):
        """Test serial extraction from various payload formats"""
        # Direct serial field
        payload1 = {"serial": "BS-001"}
        self.assertEqual(self._extract_serial(payload1), "BS-001")

        # Serial in details
        payload2 = {"details": {"serial": "FS-002"}}
        self.assertEqual(self._extract_serial(payload2), "FS-002")

        # No serial
        payload3 = {"module": "Bohrstation"}
        self.assertEqual(self._extract_serial(payload3), "")

        # Non-dict payload
        self.assertEqual(self._extract_serial("string"), "")

    def test_detect_status_category(self):
        """Test status category detection"""
        # Connection status
        topic1 = "ccu/connection"
        payload1 = {"connected": True}
        self.assertEqual(self._detect_status(topic1, payload1), "Connection Status")

        # Module state
        topic2 = "ccu/status"
        payload2 = {"module": "Bohrstation", "state": "running"}
        self.assertEqual(self._detect_status(topic2, payload2), "Module State")

        # FTS state
        topic3 = "ccu/status"
        payload3 = {"module": "FTS-1", "state": "transporting"}
        self.assertEqual(self._detect_status(topic3, payload3), "FTS State")

        # CCU state
        topic4 = "ccu/state"
        payload4 = {"status": "running"}
        self.assertEqual(self._detect_status(topic4, payload4), "CCU State")

    def test_detect_module_or_fts(self):
        """Test module/FTS detection"""
        # Direct module field
        payload1 = {"module": "Bohrstation"}
        self.assertEqual(self._detect_module(payload1), "Bohrstation")

        # FTS pattern
        payload2 = {"module": "FTS-1"}
        self.assertEqual(self._detect_module(payload2), "FTS-1")

        # Component field
        payload3 = {"component": "Frässtation"}
        self.assertEqual(self._detect_module(payload3), "Frässtation")

        # No module
        payload4 = {"status": "running"}
        self.assertEqual(self._detect_module(payload4), "")

    def test_detect_message_type(self):
        """Test message type detection"""
        # Status update
        topic1 = "ccu/status"
        self.assertEqual(self._detect_type(topic1, {}), "Status Update")

        # Control command
        topic2 = "ccu/control"
        self.assertEqual(self._detect_type(topic2, {}), "Control Command")

        # Connection
        topic3 = "ccu/connection"
        self.assertEqual(self._detect_type(topic3, {}), "Connection")

        # Workflow
        topic4 = "ccu/workflow/WF001"
        self.assertEqual(self._detect_type(topic4, {}), "Workflow")

    def test_prepare_dataframe(self):
        """Test dataframe preparation"""
        messages = [
            {
                "timestamp": time.time(),
                "topic": "ccu/status",
                "payload": {"module": "Bohrstation", "state": "running", "details": {"serial": "BS-001"}},
            },
            {
                "timestamp": time.time() - 60,
                "topic": "ccu/connection",
                "payload": {"component": "FTS-1", "connected": True},
            },
        ]

        df = self._prepare_df(messages)

        # Check dataframe structure
        self.assertEqual(len(df), 2)
        self.assertIn("timestamp", df.columns)
        self.assertIn("topic", df.columns)
        self.assertIn("msg_type", df.columns)
        self.assertIn("serial", df.columns)
        self.assertIn("detected_status", df.columns)
        self.assertIn("module_fts", df.columns)

        # Check first row
        self.assertEqual(df.iloc[0]["topic"], "ccu/status")
        self.assertEqual(df.iloc[0]["module_fts"], "Bohrstation")
        self.assertEqual(df.iloc[0]["serial"], "BS-001")
        self.assertEqual(df.iloc[0]["msg_type"], "Status Update")

        # Check second row
        self.assertEqual(df.iloc[1]["topic"], "ccu/connection")
        self.assertEqual(df.iloc[1]["module_fts"], "FTS-1")
        self.assertEqual(df.iloc[1]["msg_type"], "Connection")

    def test_apply_filters(self):
        """Test filter application"""
        import pandas as pd

        # Create test dataframe
        df = pd.DataFrame(
            [
                {
                    "topic": "ccu/status",
                    "msg_type": "Status Update",
                    "serial": "BS-001",
                    "detected_status": "Module State",
                    "module_fts": "Bohrstation",
                    "type_display": "Status Update",
                },
                {
                    "topic": "ccu/connection",
                    "msg_type": "Connection",
                    "serial": "",
                    "detected_status": "Connection Status",
                    "module_fts": "FTS-1",
                    "type_display": "Connection",
                },
                {
                    "topic": "ccu/status",
                    "msg_type": "Status Update",
                    "serial": "FS-002",
                    "detected_status": "Module State",
                    "module_fts": "Frässtation",
                    "type_display": "Status Update",
                },
            ]
        )

        # Test topic filter
        filtered = self._apply_filters(df, "ccu/status", "All", "All", "All")
        self.assertEqual(len(filtered), 2)

        # Test module filter
        filtered = self._apply_filters(df, "All", "Bohrstation", "All", "All")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["module_fts"], "Bohrstation")

        # Test status filter
        filtered = self._apply_filters(df, "All", "All", "Connection Status", "All")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["detected_status"], "Connection Status")

        # Test type filter
        filtered = self._apply_filters(df, "All", "All", "All", "Connection")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["type_display"], "Connection")

        # Test combined filters
        filtered = self._apply_filters(df, "ccu/status", "All", "Module State", "Status Update")
        self.assertEqual(len(filtered), 2)

        # Test no matches
        filtered = self._apply_filters(df, "ccu/status", "FTS-1", "All", "All")
        self.assertEqual(len(filtered), 0)


if __name__ == "__main__":
    unittest.main()
