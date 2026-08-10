"""Tests für Retained-Startup-Grace und quality_check ts/Dedupe."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from session_manager.utils.recording_retain_policy import (
    RETAINED_STARTUP_GRACE_SEC,
    parse_payload_ts,
    should_skip_retained_message,
    should_skip_stale_or_duplicate_payload,
)


class TestRecordingRetainPolicy(unittest.TestCase):
    def test_non_retain_never_skipped(self):
        self.assertFalse(
            should_skip_retained_message(
                False,
                recording_started_monotonic=100.0,
                now_monotonic=100.1,
            )
        )

    def test_retain_skipped_during_grace(self):
        start = 1000.0
        self.assertTrue(
            should_skip_retained_message(
                True,
                recording_started_monotonic=start,
                now_monotonic=start + 0.5,
                grace_sec=RETAINED_STARTUP_GRACE_SEC,
            )
        )

    def test_retain_kept_after_grace(self):
        start = 1000.0
        self.assertFalse(
            should_skip_retained_message(
                True,
                recording_started_monotonic=start,
                now_monotonic=start + RETAINED_STARTUP_GRACE_SEC,
            )
        )

    def test_quality_check_bypasses_grace(self):
        start = 1000.0
        self.assertFalse(
            should_skip_retained_message(
                True,
                recording_started_monotonic=start,
                now_monotonic=start + 0.1,
                topic="/j1/txt/1/i/quality_check",
            )
        )

    def test_stale_payload_ts_skipped(self):
        started = datetime(2026, 8, 7, 8, 7, 52, tzinfo=timezone.utc)
        seen: set[str] = set()
        payload = '{"ts":"2026-08-07T08:00:07.783778Z","result":"FAILED",' '"classification":"MIPO2","num":4}'
        self.assertTrue(
            should_skip_stale_or_duplicate_payload(
                "/j1/txt/1/i/quality_check",
                payload,
                recording_started_at_utc=started,
                seen_payload_ts=seen,
            )
        )

    def test_live_payload_ts_kept_once(self):
        started = datetime(2026, 8, 7, 8, 7, 52, tzinfo=timezone.utc)
        seen: set[str] = set()
        payload = '{"ts":"2026-08-07T08:12:13.697340Z","result":"FAILED",' '"classification":"CRACK","num":4}'
        self.assertFalse(
            should_skip_stale_or_duplicate_payload(
                "/j1/txt/1/i/quality_check",
                payload,
                recording_started_at_utc=started,
                seen_payload_ts=seen,
            )
        )
        self.assertTrue(
            should_skip_stale_or_duplicate_payload(
                "/j1/txt/1/i/quality_check",
                payload,
                recording_started_at_utc=started,
                seen_payload_ts=seen,
            )
        )

    def test_parse_payload_ts(self):
        ts = parse_payload_ts('{"ts":"2026-08-07T08:12:13.697340Z"}')
        self.assertIsNotNone(ts)
        assert ts is not None
        self.assertEqual(ts.year, 2026)


if __name__ == "__main__":
    unittest.main()
