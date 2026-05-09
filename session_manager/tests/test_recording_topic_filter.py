"""Tests für DR-25 Topic-Ausschluss im Session-Recorder-Schreibpfad."""

import unittest

from session_manager.utils.recording_topic_filter import (
    CUSTOM_FILTER_MODE_EXCLUDE,
    CUSTOM_FILTER_MODE_INCLUDE,
    EXCLUSION_PRESET_ANALYSIS,
    EXCLUSION_PRESET_NO_CAM,
    EXCLUSION_PRESET_NONE,
    normalize_custom_filter_mode,
    normalize_exclusion_preset,
    should_write_message_to_session_log,
    topic_excluded_for_analysis_preset,
    topic_excluded_for_no_cam_preset,
)


class TestRecordingTopicFilter(unittest.TestCase):
    def test_none_preset_records_all(self):
        self.assertTrue(should_write_message_to_session_log("/j1/txt/1/i/cam", EXCLUSION_PRESET_NONE))
        self.assertTrue(
            should_write_message_to_session_log("osf/arduino/vibration/sw420-1/state", EXCLUSION_PRESET_NONE)
        )
        self.assertTrue(should_write_message_to_session_log("/j1/txt/1/i/ldr", EXCLUSION_PRESET_NONE))

    def test_analysis_excludes_dr25_topics(self):
        self.assertTrue(topic_excluded_for_analysis_preset("osf/arduino/station/telemetry"))
        self.assertTrue(topic_excluded_for_analysis_preset("/j1/txt/1/i/cam"))
        self.assertTrue(topic_excluded_for_analysis_preset("/j1/txt/1/i/bme680"))
        self.assertTrue(topic_excluded_for_analysis_preset("/j1/txt/1/i/ldr"))
        self.assertTrue(topic_excluded_for_analysis_preset("/j1/txt/1/c/ldr"))
        self.assertFalse(topic_excluded_for_analysis_preset("ccu/pairing/state"))
        self.assertFalse(topic_excluded_for_analysis_preset("fts/v1/ff/5iO4/state"))

    def test_analysis_preset_skips_excluded(self):
        self.assertFalse(
            should_write_message_to_session_log("osf/arduino/vibration/sw420-1/state", EXCLUSION_PRESET_ANALYSIS)
        )
        self.assertFalse(should_write_message_to_session_log("/j1/txt/1/i/cam", EXCLUSION_PRESET_ANALYSIS))
        self.assertFalse(should_write_message_to_session_log("/j1/txt/1/i/ldr", EXCLUSION_PRESET_ANALYSIS))
        self.assertTrue(should_write_message_to_session_log("ccu/order/active", EXCLUSION_PRESET_ANALYSIS))

    def test_normalize_invalid_preset(self):
        self.assertEqual(normalize_exclusion_preset(None), EXCLUSION_PRESET_NONE)
        self.assertEqual(normalize_exclusion_preset("bogus"), EXCLUSION_PRESET_NONE)
        self.assertEqual(normalize_exclusion_preset("analysis"), EXCLUSION_PRESET_ANALYSIS)

    def test_no_cam_preset(self):
        self.assertTrue(topic_excluded_for_no_cam_preset("/j1/txt/1/i/cam"))
        self.assertTrue(topic_excluded_for_no_cam_preset("/j1/txt/1/i/cam/frame"))
        self.assertFalse(topic_excluded_for_no_cam_preset("/j1/txt/1/i/ldr"))
        self.assertFalse(topic_excluded_for_no_cam_preset("ccu/order/active"))
        self.assertFalse(should_write_message_to_session_log("/j1/txt/1/i/cam", EXCLUSION_PRESET_NO_CAM))
        self.assertTrue(should_write_message_to_session_log("/j1/txt/1/i/ldr", EXCLUSION_PRESET_NO_CAM))

    def test_custom_exclude_filter(self):
        self.assertFalse(
            should_write_message_to_session_log(
                "/j1/txt/1/i/cam/frame",
                EXCLUSION_PRESET_NONE,
                custom_filter_mode=CUSTOM_FILTER_MODE_EXCLUDE,
                custom_filter_topics=["/j1/txt/1/i/cam/#"],
            )
        )
        self.assertTrue(
            should_write_message_to_session_log(
                "/j1/txt/1/i/ldr",
                EXCLUSION_PRESET_NONE,
                custom_filter_mode=CUSTOM_FILTER_MODE_EXCLUDE,
                custom_filter_topics=["/j1/txt/1/i/cam/#"],
            )
        )

    def test_custom_include_filter(self):
        self.assertTrue(
            should_write_message_to_session_log(
                "ccu/order/active",
                EXCLUSION_PRESET_NONE,
                custom_filter_mode=CUSTOM_FILTER_MODE_INCLUDE,
                custom_filter_topics=["ccu/order/active"],
            )
        )
        self.assertFalse(
            should_write_message_to_session_log(
                "fts/v1/ff/5iO4/state",
                EXCLUSION_PRESET_NONE,
                custom_filter_mode=CUSTOM_FILTER_MODE_INCLUDE,
                custom_filter_topics=["ccu/order/active"],
            )
        )

    def test_normalize_custom_mode(self):
        self.assertEqual(normalize_custom_filter_mode(None), "none")
        self.assertEqual(normalize_custom_filter_mode("bogus"), "none")
        self.assertEqual(normalize_custom_filter_mode("include"), "include")
