"""
Tests für Session Log-Format (JSON-Zeilen)

Testet:
- load_log_session parst JSON-Zeilen korrekt
- save_log_session schreibt JSON-Zeilen (Session Recorder Format)
- Kompatibilität zwischen Schreiben und Lesen
"""

import json
import tempfile
import unittest
from pathlib import Path

from session_manager.components.replay_station import load_log_session
from session_manager.components.session_recorder import save_log_session


class TestSessionLogFormat(unittest.TestCase):
    """Tests für .log Session-Format (JSON-Zeilen)"""

    def test_load_log_session_skips_session_meta_first_line(self):
        """Erste Zeile session_meta (ohne topic/payload/timestamp) wird nicht als Message geladen."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, encoding="utf-8") as f:
            f.write('{"_kind":"session_meta","schema":1,"note":"x"}\n')
            f.write('{"topic": "t1", "payload": "{}", "timestamp": "2025-01-15T10:00:00Z"}\n')
            log_path = Path(f.name)
        try:
            messages = load_log_session(log_path)
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["topic"], "t1")
        finally:
            log_path.unlink(missing_ok=True)

    def test_load_log_session_parses_json_lines(self):
        """Test dass load_log_session JSON-Zeilen korrekt parst"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, encoding="utf-8") as f:
            f.write('{"topic": "test/topic", "payload": "{}", "timestamp": "2025-01-15T10:00:00Z"}\n')
            f.write(
                '{"topic": "other/topic", "payload": "{\\"key\\": \\"value\\"}", "timestamp": "2025-01-15T10:00:01Z"}\n'
            )
            log_path = Path(f.name)

        try:
            messages = load_log_session(log_path)
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]["topic"], "test/topic")
            self.assertEqual(messages[0]["payload"], "{}")
            self.assertEqual(messages[0]["timestamp"], "2025-01-15T10:00:00Z")
            self.assertEqual(messages[1]["topic"], "other/topic")
        finally:
            log_path.unlink(missing_ok=True)

    def test_load_log_session_skips_invalid_lines(self):
        """Test dass ungültige Zeilen übersprungen werden"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, encoding="utf-8") as f:
            f.write('{"topic": "valid", "payload": "{}", "timestamp": "2025-01-15T10:00:00Z"}\n')
            f.write("invalid json\n")
            f.write("  \n")
            f.write('{"topic": "valid2", "payload": "{}", "timestamp": "2025-01-15T10:00:01Z"}\n')
            log_path = Path(f.name)

        try:
            messages = load_log_session(log_path)
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0]["topic"], "valid")
            self.assertEqual(messages[1]["topic"], "valid2")
        finally:
            log_path.unlink(missing_ok=True)

    def test_save_log_session_writes_json_lines(self):
        """Test dass save_log_session JSON-Zeilen schreibt"""
        messages = [
            {"topic": "a/b", "payload": "{}", "timestamp": "2025-01-15T10:00:00Z"},
            {"topic": "c/d", "payload": '{"x": 1}', "timestamp": "2025-01-15T10:00:01Z"},
        ]
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            log_path = Path(f.name)

        try:
            save_log_session(log_path, messages, meta_line='{"_kind":"session_meta","schema":1}')
            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            self.assertEqual(len(lines), 3)
            first = json.loads(lines[0])
            self.assertEqual(first.get("_kind"), "session_meta")
            for i, line in enumerate(lines[1:], start=0):
                data = json.loads(line)
                self.assertEqual(data["topic"], messages[i]["topic"])
                self.assertEqual(data["payload"], messages[i]["payload"])
                self.assertEqual(data["timestamp"], messages[i]["timestamp"])
        finally:
            log_path.unlink(missing_ok=True)

    def test_save_and_load_roundtrip(self):
        """Test Roundtrip: save_log_session -> load_log_session"""
        original = [
            {"topic": "module/v1/ff/test/state", "payload": '{"orderId": "abc"}', "timestamp": "2025-01-15T10:00:00Z"},
            {"topic": "ccu/state/layout", "payload": "{}", "timestamp": "2025-01-15T10:00:01Z"},
        ]
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            log_path = Path(f.name)

        try:
            save_log_session(log_path, original)
            loaded = load_log_session(log_path)
            self.assertEqual(len(loaded), len(original))
            for i, msg in enumerate(loaded):
                self.assertEqual(msg["topic"], original[i]["topic"])
                self.assertEqual(msg["payload"], original[i]["payload"])
                self.assertEqual(msg["timestamp"], original[i]["timestamp"])
        finally:
            log_path.unlink(missing_ok=True)

    def test_save_and_load_roundtrip_with_qos_retain(self):
        """Test Roundtrip mit qos/retain für retain-Verifizierung"""
        original = [
            {
                "topic": "module/v1/ff/SVR3QA0022/state",
                "payload": "{}",
                "timestamp": "2025-01-15T10:00:00Z",
                "qos": 1,
                "retain": True,
            },
        ]
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            log_path = Path(f.name)

        try:
            save_log_session(log_path, original)
            loaded = load_log_session(log_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["qos"], 1)
            self.assertEqual(loaded[0]["retain"], True)
        finally:
            log_path.unlink(missing_ok=True)
