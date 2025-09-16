"""
Tests für Session Manager Logging
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import streamlit as st


class TestSessionManagerLogging(unittest.TestCase):
    """Tests für Session Manager Logging-Funktionalität"""

    def setUp(self):
        """Test-Setup"""
        # Session State zurücksetzen
        if hasattr(st, 'session_state'):
            st.session_state.clear()

    def test_init_logging_function_exists(self):
        """Test dass _init_logging_once Funktion existiert"""
        from src_orbis.helper_apps.session_manager.session_manager import _init_logging_once

        self.assertIsNotNone(_init_logging_once)
        self.assertTrue(callable(_init_logging_once))

    def test_logging_levels_available(self):
        """Test dass alle gewünschten Logging-Level verfügbar sind"""
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]

        # Test dass alle Level in logging verfügbar sind
        for level in expected_levels:
            self.assertTrue(hasattr(logging, level), f"Logging level {level} sollte verfügbar sein")
            self.assertIsInstance(getattr(logging, level), int, f"Logging level {level} sollte Integer sein")

    def test_session_logger_import(self):
        """Test dass Session Logger importiert werden kann"""
        from src_orbis.helper_apps.session_manager.utils.session_logger import SessionManagerLogger

        self.assertIsNotNone(SessionManagerLogger)
        self.assertTrue(callable(SessionManagerLogger))

    def test_session_logger_creation(self):
        """Test dass Session Logger erstellt werden kann"""
        from src_orbis.helper_apps.session_manager.utils.session_logger import SessionManagerLogger

        with tempfile.TemporaryDirectory() as temp_dir:
            logger = SessionManagerLogger("test_session", str(Path(temp_dir) / "logs"))

            self.assertIsNotNone(logger)
            self.assertIsInstance(logger, SessionManagerLogger)

    def test_log_directory_creation(self):
        """Test mit temporärem Verzeichnis"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test dass Verzeichnis erstellt werden kann
            log_dir = Path(temp_dir) / "logs"
            log_dir.mkdir(exist_ok=True)

            self.assertTrue(log_dir.exists())
            self.assertTrue(log_dir.is_dir())

    def test_empty_session_name(self):
        """Test mit leerem Session-Namen"""
        from src_orbis.helper_apps.session_manager.utils.session_logger import SessionManagerLogger

        with tempfile.TemporaryDirectory() as temp_dir:
            # Sollte funktionieren auch mit leerem Namen
            logger = SessionManagerLogger("", str(Path(temp_dir) / "logs"))

            self.assertIsNotNone(logger)
            self.assertIsInstance(logger, SessionManagerLogger)

    def test_nonexistent_log_directory(self):
        """Test mit nicht existierendem Log-Verzeichnis"""
        from src_orbis.helper_apps.session_manager.utils.session_logger import SessionManagerLogger

        with tempfile.TemporaryDirectory() as temp_base:
            # Erstelle Unterverzeichnis das nicht existiert
            nonexistent_dir = Path(temp_base) / "nonexistent" / "path" / "for" / "logs"

            # Sollte Verzeichnis erstellen
            logger = SessionManagerLogger("test", str(nonexistent_dir))

            # Prüfen dass Verzeichnis erstellt wurde
            self.assertTrue(nonexistent_dir.exists())
            self.assertIsNotNone(logger)


if __name__ == '__main__':
    unittest.main()
