"""Tests für erste .log-Zeile session_meta (ohne MQTT-Pflichtfelder)."""

import json
import unittest
from datetime import datetime

from session_manager.utils.session_meta_line import (
    SESSION_META_KIND,
    build_session_meta_line,
    is_session_meta_line,
    read_osf_workspace_version,
)


class TestSessionMetaLine(unittest.TestCase):
    def test_meta_line_is_valid_json_without_mqtt_fields(self):
        line = build_session_meta_line(
            session_name="test-mixed",
            log_filename="test-mixed_20260409_120000.log",
            recording_started_at=datetime(2026, 4, 9, 12, 0, 0),
            recording_ended_at=datetime(2026, 4, 9, 12, 3, 30),
            recording_exclusion_preset="analysis",
            broker_host="192.168.0.100",
            broker_port=1883,
            ccu_orders_description="two parallel storage",
            ccu_order_outcome="ok",
            note="demo",
        )
        data = json.loads(line)
        self.assertEqual(data.get("_kind"), SESSION_META_KIND)
        self.assertNotIn("topic", data)
        self.assertNotIn("payload", data)
        self.assertNotIn("timestamp", data)
        self.assertEqual(data.get("ccuOrderOutcome"), "ok")
        self.assertEqual(data.get("durationSec"), 210.0)
        self.assertTrue(is_session_meta_line(data))

    def test_read_osf_workspace_version_returns_string(self):
        v = read_osf_workspace_version()
        self.assertIsInstance(v, str)
        self.assertTrue(len(v) > 0)
