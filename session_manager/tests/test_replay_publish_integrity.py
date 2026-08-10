"""Replay publish acceptance gate and abort helpers."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from session_manager.components.replay_station import (
    REPLAY_ABORT_AFTER_CONSECUTIVE_FAILS,
    ReplayController,
    replay_acceptance_message,
    replay_run_valid_for_acceptance,
)
from session_manager.mqtt.mqtt_client import paho_rc_name


class TestReplayAcceptanceGate(unittest.TestCase):
    def test_valid_only_when_all_ok(self):
        stats = {
            "finished": True,
            "aborted": False,
            "pub_ok": 100,
            "pub_fail": 0,
            "total": 100,
        }
        self.assertTrue(replay_run_valid_for_acceptance(stats))
        self.assertIn("valid for Track & Trace", replay_acceptance_message(stats))

    def test_invalid_when_any_fail(self):
        stats = {
            "finished": True,
            "aborted": False,
            "pub_ok": 401,
            "pub_fail": 1082,
            "total": 1483,
            "last_rc_name": "NOT_CONNECTED",
        }
        self.assertFalse(replay_run_valid_for_acceptance(stats))
        msg = replay_acceptance_message(stats)
        self.assertIn("INVALID", msg)
        self.assertIn("NOT_CONNECTED", msg)

    def test_invalid_when_aborted(self):
        stats = {
            "finished": True,
            "aborted": True,
            "pub_ok": 0,
            "pub_fail": 1,
            "total": 1483,
            "abort_reason": "MQTT not connected after reconnect",
        }
        self.assertFalse(replay_run_valid_for_acceptance(stats))
        self.assertIn("abort=", replay_acceptance_message(stats))

    def test_paho_rc_name_known(self):
        self.assertEqual(paho_rc_name(-1), "NOT_CONNECTED")
        self.assertEqual(paho_rc_name(0), "SUCCESS")


class TestReplayControllerAbort(unittest.TestCase):
    def test_aborts_after_consecutive_not_connected(self):
        ctrl = ReplayController("127.0.0.1", 1883)
        mock_client = MagicMock()
        mock_client.is_connected.return_value = False
        mock_client.ensure_connected.return_value = False
        mock_client.last_connect_rc = 5
        mock_client.last_disconnect_rc = 7
        ctrl._mqtt_client = mock_client

        items = [(float(i), f"t/{i}", b"{}", 0, False) for i in range(100)]
        ctrl.load(items)

        # Drive publish path directly (no worker/timing)
        ok = ctrl._publish_item(ctrl._seq[0], 1.0)
        self.assertFalse(ok)
        stats = ctrl.get_publish_stats()
        self.assertTrue(stats["aborted"])
        self.assertGreaterEqual(stats["pub_fail"], 1)
        self.assertIn("MQTT not connected", str(stats["abort_reason"]))
        self.assertFalse(stats["valid_for_acceptance"])

    def test_aborts_after_consecutive_publish_fails(self):
        ctrl = ReplayController("127.0.0.1", 1883)
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.ensure_connected.return_value = True
        mock_client.publish_with_status.return_value = (False, 15)  # QUEUE_SIZE
        ctrl._mqtt_client = mock_client

        items = [(float(i), f"t/{i}", b"{}", 1, False) for i in range(REPLAY_ABORT_AFTER_CONSECUTIVE_FAILS + 5)]
        ctrl.load(items)

        with unittest.mock.patch("session_manager.components.replay_station.time.sleep", return_value=None):
            continued = True
            for i in range(REPLAY_ABORT_AFTER_CONSECUTIVE_FAILS):
                continued = ctrl._publish_item(ctrl._seq[i], 1.0)
                if not continued:
                    break
        self.assertFalse(continued)
        stats = ctrl.get_publish_stats()
        self.assertTrue(stats["aborted"])
        self.assertEqual(stats["last_rc_name"], "QUEUE_SIZE")
        self.assertGreaterEqual(stats["pub_fail"], REPLAY_ABORT_AFTER_CONSECUTIVE_FAILS)


if __name__ == "__main__":
    unittest.main()
