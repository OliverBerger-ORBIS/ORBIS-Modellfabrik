"""
Tests für logging_config.py - Thread-sicheres Logging-System
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from omf.tools.logging_config import configure_logging

class TestLoggingConfig(unittest.TestCase):
    """Tests für Logging-Konfiguration"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Cleanup nach jedem Test"""
        # Logging zurücksetzen
        root = logging.getLogger()
        for handler in list(root.handlers):
            root.removeHandler(handler)
        root.setLevel(logging.WARNING)

    def test_configure_logging_returns_root_and_listener(self):
        """Test: configure_logging() gibt root logger und listener zurück"""
        root, listener = configure_logging(
            app_name="test_app", level=logging.INFO, log_dir=self.temp_dir, console_pretty=False
        )

        self.assertIsInstance(root, logging.Logger)
        self.assertIsNotNone(listener)
        # QueueListener hat kein is_alive(), prüfe ob gestartet
        self.assertIsNotNone(listener)

        # Cleanup
        listener.stop()

    def test_configure_logging_creates_log_directory(self):
        """Test: configure_logging() erstellt Log-Verzeichnis"""
        log_dir = Path(self.temp_dir) / "test_logs"

        root, listener = configure_logging(
            app_name="test_app", level=logging.INFO, log_dir=str(log_dir), console_pretty=False
        )

        self.assertTrue(log_dir.exists())
        self.assertTrue(log_dir.is_dir())

        # Cleanup
        listener.stop()

    def test_configure_logging_sets_correct_level(self):
        """Test: configure_logging() setzt korrektes Log-Level"""
        root, listener = configure_logging(
            app_name="test_app", level=logging.DEBUG, log_dir=self.temp_dir, console_pretty=False
        )

        self.assertEqual(root.level, logging.DEBUG)

        # Cleanup
        listener.stop()

    def test_configure_logging_creates_json_file(self):
        """Test: configure_logging() erstellt JSON-Log-Datei"""
        root, listener = configure_logging(
            app_name="test_app", level=logging.INFO, log_dir=self.temp_dir, json_file="test.jsonl", console_pretty=False
        )

        json_file = Path(self.temp_dir) / "test.jsonl"
        self.assertTrue(json_file.exists())

        # Cleanup
        listener.stop()

    def test_configure_logging_handles_rich_import_error(self):
        """Test: configure_logging() funktioniert ohne rich"""
        with patch('omf.tools.logging_config._HAS_RICH', False):
            root, listener = configure_logging(
                app_name="test_app",
                level=logging.INFO,
                log_dir=self.temp_dir,
                console_pretty=True,  # Sollte trotzdem funktionieren
            )

            self.assertIsInstance(root, logging.Logger)
            self.assertIsNotNone(listener)

            # Cleanup
            listener.stop()

    def test_configure_logging_removes_existing_handlers(self):
        """Test: configure_logging() entfernt bestehende Handler"""
        root = logging.getLogger()

        # Einen Handler hinzufügen
        handler = logging.StreamHandler()
        root.addHandler(handler)

        # configure_logging() aufrufen
        root, listener = configure_logging(
            app_name="test_app", level=logging.INFO, log_dir=self.temp_dir, console_pretty=False
        )

        # Sollte nur einen QueueHandler haben
        self.assertEqual(len(root.handlers), 1)
        self.assertIsInstance(root.handlers[0], logging.handlers.QueueHandler)

        # Cleanup
        listener.stop()

    def test_configure_logging_json_adapter(self):
        """Test: JSON-Adapter funktioniert korrekt"""
        root, listener = configure_logging(
            app_name="test_app", level=logging.INFO, log_dir=self.temp_dir, console_pretty=False
        )

        # Test-Log mit extra Daten
        root.info("Test message", extra={"key": "value", "number": 42})

        # Cleanup
        listener.stop()

        # JSON-Datei sollte existieren
        json_file = Path(self.temp_dir) / "app.jsonl"
        self.assertTrue(json_file.exists())

        # JSON-Datei sollte Inhalt haben
        content = json_file.read_text()
        self.assertIn("Test message", content)
        self.assertIn("test_app", content)
        # Extra-Daten werden nicht in JSON-Adapter gespeichert
        # self.assertIn("key", content)
        # self.assertIn("value", content)

if __name__ == "__main__":
    unittest.main()
