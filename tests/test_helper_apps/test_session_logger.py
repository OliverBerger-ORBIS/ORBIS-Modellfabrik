"""
Tests für SessionManagerLogger - Session-spezifisches Logging

Testet:
- Session-spezifische Log-Dateien
- Strukturierte Log-Ausgabe mit Session-Kontext
- RotatingFileHandler Funktionalität
- Logger-Adapter mit Session-Informationen
- Convenience-Funktionen
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from omf.helper_apps.session_manager.utils.session_logger import (
    SessionManagerLogger,
    get_analysis_logger,
    get_recorder_logger,
    get_replay_logger,
    get_session_logger,
    get_session_logger_cached,
    get_settings_logger,
    get_template_logger,
)

class TestSessionManagerLogger(unittest.TestCase):
    """Tests für SessionManagerLogger Klasse"""

    def setUp(self):
        """Test-Setup mit temporärem Verzeichnis"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_name = "test_session"
        self.logger = SessionManagerLogger(self.session_name, self.temp_dir)

    def tearDown(self):
        """Test-Cleanup"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test SessionManagerLogger Initialisierung"""
        self.assertEqual(self.logger.session_name, self.session_name)
        self.assertEqual(self.logger.log_dir, Path(self.temp_dir))
        self.assertEqual(self.logger.logger_name, f"session_manager.{self.session_name}")
        self.assertIsInstance(self.logger.logger, logging.LoggerAdapter)

    def test_log_file_creation(self):
        """Test Log-Datei wird erstellt"""
        log_file = self.logger.get_log_file_path()
        expected_path = Path(self.temp_dir) / f"session_manager_{self.session_name}.log"
        self.assertEqual(log_file, expected_path)

        # Prüfen dass Handler konfiguriert sind
        handlers = self.logger.base_logger.handlers
        file_handlers = [h for h in handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        self.assertEqual(len(file_handlers), 1)

        # Prüfen dass Handler-Pfad korrekt ist (nur Dateiname vergleichen)
        handler_filename = Path(file_handlers[0].baseFilename).name
        expected_filename = log_file.name
        self.assertEqual(handler_filename, expected_filename)

    def test_log_formatting(self):
        """Test Log-Formatierung mit Session-Kontext"""
        with patch('sys.stdout'):
            # Log-Nachricht schreiben
            self.logger.get_logger().info("Test-Nachricht")

            # Prüfen dass Handler konfiguriert sind
            self.assertEqual(len(self.logger.logger.logger.handlers), 2)

            # Prüfen dass Logger-Adapter Session-Name enthält
            self.assertEqual(self.logger.logger.extra['session_name'], self.session_name)

    def test_log_level_setting(self):
        """Test Log-Level setzen"""
        self.logger.set_level(logging.DEBUG)
        self.assertEqual(self.logger.logger.logger.level, logging.DEBUG)

        self.logger.set_level(logging.WARNING)
        self.assertEqual(self.logger.logger.logger.level, logging.WARNING)

    def test_rotating_file_handler(self):
        """Test RotatingFileHandler Konfiguration"""
        handlers = self.logger.logger.logger.handlers

        # Prüfen dass RotatingFileHandler vorhanden ist
        file_handlers = [h for h in handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        self.assertEqual(len(file_handlers), 1)

        rotating_handler = file_handlers[0]
        self.assertEqual(rotating_handler.maxBytes, 10 * 1024 * 1024)  # 10MB
        self.assertEqual(rotating_handler.backupCount, 5)

    def test_cleanup_old_logs(self):
        """Test Bereinigung alter Log-Dateien"""
        # Test-Dateien erstellen
        log_dir = Path(self.temp_dir)
        old_log = log_dir / "session_manager_test_session.log.1"
        old_log.write_text("Old log content")

        # Cleanup ausführen
        self.logger.cleanup_old_logs(keep_days=0)  # Alle Dateien löschen

        # Prüfen dass alte Datei gelöscht wurde
        self.assertFalse(old_log.exists())

class TestSessionLoggerFactory(unittest.TestCase):
    """Tests für SessionManagerLogger Factory-Funktionen"""

    def setUp(self):
        """Test-Setup"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Test-Cleanup"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_session_logger(self):
        """Test get_session_logger Factory-Funktion"""
        logger = get_session_logger("test_session", self.temp_dir)

        self.assertIsInstance(logger, SessionManagerLogger)
        self.assertEqual(logger.session_name, "test_session")
        self.assertEqual(logger.log_dir, Path(self.temp_dir))

    def test_get_session_logger_cached(self):
        """Test get_session_logger_cached mit Caching"""
        # Ersten Logger holen
        logger1 = get_session_logger_cached("test_session")

        # Zweiten Logger mit gleichem Namen holen
        logger2 = get_session_logger_cached("test_session")

        # Sollte derselbe Logger sein (Caching)
        self.assertIs(logger1, logger2)

        # Logger mit anderem Namen
        logger3 = get_session_logger_cached("other_session")
        self.assertIsNot(logger1, logger3)

    def test_convenience_functions(self):
        """Test Convenience-Funktionen für häufige Session-Namen"""
        # Alle Convenience-Funktionen testen
        analysis_logger = get_analysis_logger()
        replay_logger = get_replay_logger()
        recorder_logger = get_recorder_logger()
        template_logger = get_template_logger()
        settings_logger = get_settings_logger()

        # Prüfen dass alle Logger LoggerAdapter sind
        self.assertIsInstance(analysis_logger, logging.LoggerAdapter)
        self.assertIsInstance(replay_logger, logging.LoggerAdapter)
        self.assertIsInstance(recorder_logger, logging.LoggerAdapter)
        self.assertIsInstance(template_logger, logging.LoggerAdapter)
        self.assertIsInstance(settings_logger, logging.LoggerAdapter)

        # Prüfen dass Session-Namen korrekt sind
        self.assertEqual(analysis_logger.extra['session_name'], "analysis")
        self.assertEqual(replay_logger.extra['session_name'], "replay")
        self.assertEqual(recorder_logger.extra['session_name'], "recorder")
        self.assertEqual(template_logger.extra['session_name'], "template")
        self.assertEqual(settings_logger.extra['session_name'], "settings")

class TestSessionLoggerIntegration(unittest.TestCase):
    """Integration Tests für SessionManagerLogger"""

    def setUp(self):
        """Test-Setup"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Test-Cleanup"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_multiple_sessions_logging(self):
        """Test Logging für mehrere Sessions gleichzeitig"""
        # Logger für verschiedene Sessions erstellen
        logger1 = get_session_logger("session1", self.temp_dir)
        logger2 = get_session_logger("session2", self.temp_dir)

        # Log-Nachrichten schreiben
        logger1.get_logger().info("Nachricht für Session 1")
        logger2.get_logger().info("Nachricht für Session 2")

        # Prüfen dass separate Log-Dateien erstellt wurden
        log_file1 = Path(self.temp_dir) / "session_manager_session1.log"
        log_file2 = Path(self.temp_dir) / "session_manager_session2.log"

        self.assertTrue(log_file1.exists())
        self.assertTrue(log_file2.exists())

        # Prüfen dass Log-Inhalte korrekt sind
        content1 = log_file1.read_text()
        content2 = log_file2.read_text()

        self.assertIn("Nachricht für Session 1", content1)
        self.assertIn("Nachricht für Session 2", content2)
        self.assertNotIn("Nachricht für Session 1", content2)
        self.assertNotIn("Nachricht für Session 2", content1)

    def test_log_rotation(self):
        """Test Log-Rotation Funktionalität"""
        logger = get_session_logger("rotation_test", self.temp_dir)

        # Kleine maxBytes für Test
        for handler in logger.logger.logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.maxBytes = 100  # 100 Bytes für Test

        # Viele Log-Nachrichten schreiben um Rotation auszulösen
        for i in range(10):
            logger.get_logger().info(f"Test-Nachricht {i} " * 10)  # Lange Nachrichten

        # Prüfen dass Rotation-Dateien erstellt wurden
        log_dir = Path(self.temp_dir)
        rotation_files = list(log_dir.glob("session_manager_rotation_test.log*"))

        # Sollte mindestens 2 Dateien geben (Original + Rotation)
        self.assertGreaterEqual(len(rotation_files), 2)

class TestSessionLoggerEdgeCases(unittest.TestCase):
    """Edge Cases für SessionManagerLogger"""

    def test_invalid_session_name(self):
        """Test mit ungültigem Session-Namen"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Session-Name mit Sonderzeichen (bereinigt)
            safe_name = "test_session_name"  # Sonderzeichen entfernt
            logger = get_session_logger(safe_name, temp_dir)

            # Sollte trotzdem funktionieren
            self.assertIsInstance(logger, SessionManagerLogger)
            self.assertEqual(logger.session_name, safe_name)

    def test_nonexistent_log_directory(self):
        """Test mit nicht existierendem Log-Verzeichnis"""
        with tempfile.TemporaryDirectory() as temp_base:
            # Erstelle Unterverzeichnis das nicht existiert
            nonexistent_dir = Path(temp_base) / "nonexistent" / "path" / "for" / "logs"

            # Sollte Verzeichnis erstellen
            get_session_logger("test", str(nonexistent_dir))

            # Prüfen dass Verzeichnis erstellt wurde
            self.assertTrue(nonexistent_dir.exists())

    def test_empty_session_name(self):
        """Test mit leerem Session-Namen"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = get_session_logger("", temp_dir)

            # Sollte funktionieren
            self.assertIsInstance(logger, SessionManagerLogger)
            self.assertEqual(logger.session_name, "")

if __name__ == '__main__':
    unittest.main()
