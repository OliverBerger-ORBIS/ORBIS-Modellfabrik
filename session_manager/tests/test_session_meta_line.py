"""Tests für erste .log-Zeile session_meta (ohne MQTT-Pflichtfelder)."""

import json
import unittest
from datetime import datetime
from unittest.mock import patch

from session_manager.utils.session_meta_line import (
    SESSION_META_KIND,
    build_session_meta_line,
    detect_ccu_version_via_runtime_image,
    extract_ccu_version_from_messages,
    is_session_meta_line,
    read_osf_workspace_version,
    read_session_recorder_version,
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
            ccu_version="1.3.0-osf.3",
            ccu_version_source="ccu/state/version-mismatch",
        )
        data = json.loads(line)
        self.assertEqual(data.get("_kind"), SESSION_META_KIND)
        self.assertNotIn("topic", data)
        self.assertNotIn("payload", data)
        self.assertNotIn("timestamp", data)
        self.assertEqual(data.get("ccuOrderOutcome"), "ok")
        self.assertEqual(data.get("ccuVersion"), "1.3.0-osf.3")
        self.assertEqual(data.get("ccuVersionSource"), "ccu/state/version-mismatch")
        self.assertIn("sessionRecorderVersion", data)
        self.assertEqual(data.get("durationSec"), 210.0)
        self.assertTrue(is_session_meta_line(data))

    def test_read_osf_workspace_version_returns_string(self):
        v = read_osf_workspace_version()
        self.assertIsInstance(v, str)
        self.assertTrue(len(v) > 0)

    def test_read_session_recorder_version_returns_string(self):
        v = read_session_recorder_version()
        self.assertIsInstance(v, str)
        self.assertTrue(len(v) > 0)

    def test_extract_ccu_version_from_messages_prefers_version_mismatch(self):
        messages = [
            {
                "topic": "ccu/state/version-mismatch",
                "payload": '{"ccuVersion":"1.3.0-osf.3","mismatchedModules":[]}',
            },
            {
                "topic": "ccu/pairing/state",
                "payload": '{"ccuVersion":"1.3.0-osf.2"}',
            },
        ]
        version, source = extract_ccu_version_from_messages(messages)
        self.assertEqual(version, "1.3.0-osf.3")
        self.assertEqual(source, "ccu/state/version-mismatch")

    def test_extract_ccu_version_from_messages_unknown_when_absent(self):
        messages = [
            {"topic": "ccu/pairing/state", "payload": '{"modules":[]}'},
            {"topic": "module/v1/ff/demo/state", "payload": '{"state":"READY"}'},
        ]
        version, source = extract_ccu_version_from_messages(messages)
        self.assertEqual(version, "unknown")
        self.assertEqual(source, "unavailable")

    @patch("session_manager.utils.session_meta_line.subprocess.run")
    def test_detect_ccu_version_via_runtime_image_parses_tag(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "ghcr.io/ommsolutions/ff-ccu-armv7:v1.3.0-osf.4\n"
        version, source = detect_ccu_version_via_runtime_image("192.168.0.100")
        self.assertEqual(version, "1.3.0-osf.4")
        self.assertEqual(source, "rpi-docker-inspect")

    @patch("session_manager.utils.session_meta_line.subprocess.run")
    def test_detect_ccu_version_via_runtime_image_unknown_on_error(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        version, source = detect_ccu_version_via_runtime_image("192.168.0.100")
        self.assertEqual(version, "unknown")
        self.assertEqual(source, "unavailable")
