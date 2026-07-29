"""Replay speed options: 10x/max, QoS override, stable labels."""

from __future__ import annotations

import unittest

from session_manager.components.replay_station import (
    REPLAY_SPEED_BY_LABEL,
    REPLAY_SPEED_LABELS,
    REPLAY_SPEED_OPTIONS,
    effective_publish_qos,
    format_replay_speed,
    label_for_replay_speed,
    normalize_replay_speed,
)


class TestReplaySpeedOptions(unittest.TestCase):
    def test_options_include_10x_and_max(self):
        self.assertIn(10.0, REPLAY_SPEED_OPTIONS)
        self.assertIn(float("inf"), REPLAY_SPEED_OPTIONS)
        self.assertIn("10x", REPLAY_SPEED_LABELS)
        self.assertIn("max", REPLAY_SPEED_LABELS)

    def test_label_map_roundtrip(self):
        self.assertEqual(REPLAY_SPEED_BY_LABEL["10x"], 10.0)
        self.assertEqual(REPLAY_SPEED_BY_LABEL["max"], float("inf"))
        self.assertEqual(label_for_replay_speed(10.0), "10x")
        self.assertEqual(label_for_replay_speed(float("inf")), "max")

    def test_format_labels(self):
        self.assertEqual(format_replay_speed(10.0), "10x")
        self.assertEqual(format_replay_speed(float("inf")), "max")
        self.assertEqual(format_replay_speed(1.0), "1x")
        self.assertEqual(format_replay_speed(0.5), "1/2x")

    def test_normalize_allows_inf_and_clamps_slow(self):
        self.assertEqual(normalize_replay_speed(float("inf")), float("inf"))
        self.assertEqual(normalize_replay_speed(10.0), 10.0)
        self.assertEqual(normalize_replay_speed(0.01), 0.1)

    def test_high_speed_forces_qos0(self):
        self.assertEqual(effective_publish_qos(1, 1.0), 1)
        self.assertEqual(effective_publish_qos(1, 5.0), 0)
        self.assertEqual(effective_publish_qos(1, 10.0), 0)
        self.assertEqual(effective_publish_qos(1, float("inf")), 0)
        self.assertEqual(effective_publish_qos(0, 1.0), 0)


if __name__ == "__main__":
    unittest.main()
