#!/usr/bin/env python3
"""
Tests für Session Manager Logging-Features
Basierend auf PR2 Tests, angepasst für unsere Implementierung
"""

import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import streamlit as st


class TestSessionManagerLogging(unittest.TestCase):
    """Test-Klasse für Session Manager Logging-Features"""

    def setUp(self):
        """Test-Setup"""
        # Session State zurücksetzen
        if hasattr(st, 'session_state'):
            st.session_state.clear()

    def test_setup_logging_default_level(self):
        """Test Default Logging-Level (INFO)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporäres Verzeichnis für Logs
            with patch('pathlib.Path') as mock_path:
                mock_log_dir = Path(temp_dir) / "logs"
                mock_log_dir.mkdir(exist_ok=True)
                mock_path.return_value = mock_log_dir / "session_manager.log"

                from src_orbis.helper_apps.session_manager.session_manager import setup_logging

                logger = setup_logging()

                # Logger sollte erstellt werden
                self.assertIsNotNone(logger)
                self.assertEqual(logger.name, "session_manager")
                self.assertEqual(logger.level, logging.INFO)

    def test_setup_logging_debug_level(self):
        """Test DEBUG Logging-Level aus Session State"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # DEBUG Level in Session State setzen
            with patch.object(st, 'session_state', {'logging_level': 'DEBUG'}):
                with patch('pathlib.Path') as mock_path:
                    mock_log_dir = Path(temp_dir) / "logs"
                    mock_log_dir.mkdir(exist_ok=True)
                    mock_path.return_value = mock_log_dir / "session_manager.log"

                    from src_orbis.helper_apps.session_manager.session_manager import setup_logging

                    logger = setup_logging()

                    # Logger sollte DEBUG Level haben
                    self.assertEqual(logger.level, logging.DEBUG)

    def test_setup_logging_warning_level(self):
        """Test WARNING Logging-Level aus Session State"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # WARNING Level in Session State setzen
            with patch.object(st, 'session_state', {'logging_level': 'WARNING'}):
                with patch('pathlib.Path') as mock_path:
                    mock_log_dir = Path(temp_dir) / "logs"
                    mock_log_dir.mkdir(exist_ok=True)
                    mock_path.return_value = mock_log_dir / "session_manager.log"

                    from src_orbis.helper_apps.session_manager.session_manager import setup_logging

                    logger = setup_logging()

                    # Logger sollte WARNING Level haben
                    self.assertEqual(logger.level, logging.WARNING)

    def test_setup_logging_error_level(self):
        """Test ERROR Logging-Level aus Session State"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # ERROR Level in Session State setzen
            with patch.object(st, 'session_state', {'logging_level': 'ERROR'}):
                with patch('pathlib.Path') as mock_path:
                    mock_log_dir = Path(temp_dir) / "logs"
                    mock_log_dir.mkdir(exist_ok=True)
                    mock_path.return_value = mock_log_dir / "session_manager.log"

                    from src_orbis.helper_apps.session_manager.session_manager import setup_logging

                    logger = setup_logging()

                    # Logger sollte ERROR Level haben
                    self.assertEqual(logger.level, logging.ERROR)

    def test_logging_levels_available(self):
        """Test dass alle gewünschten Logging-Level verfügbar sind"""
        expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]

        for level in expected_levels:
            with patch.object(st, 'session_state', {'logging_level': level}):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with patch('pathlib.Path') as mock_path:
                        mock_log_dir = Path(temp_dir) / "logs"
                        mock_log_dir.mkdir(exist_ok=True)
                        mock_path.return_value = mock_log_dir / "session_manager.log"

                        from src_orbis.helper_apps.session_manager.session_manager import setup_logging

                        logger = setup_logging()

                        # Logger sollte korrekt konfiguriert sein
                        self.assertIsNotNone(logger)
                        self.assertEqual(logger.name, "session_manager")


class TestSessionManagerIntegration(unittest.TestCase):
    """Integration Tests für Session Manager"""

    def test_log_directory_creation(self):
        """Test dass Log-Verzeichnis automatisch erstellt wird"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Patch Path um temporäres Verzeichnis zu verwenden
            test_log_dir = Path(temp_dir) / "data" / "logs"

            with patch('src_orbis.helper_apps.session_manager.session_manager.Path') as mock_path_class:
                mock_path_class.return_value = test_log_dir

                # setup_logging sollte Verzeichnis erstellen
                from src_orbis.helper_apps.session_manager.session_manager import setup_logging

                setup_logging()

                # Verzeichnis sollte existieren
                self.assertTrue(test_log_dir.exists())


if __name__ == '__main__':
    unittest.main()
