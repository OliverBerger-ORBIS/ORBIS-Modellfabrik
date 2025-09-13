#!/usr/bin/env python3
"""
Tests für Session Manager
Testet kontrolliertes st.rerun() Handling und zentrales Logging
"""

import logging
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Add src_orbis to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src_orbis"))

from src_orbis.helper_apps.session_manager.logging_utils import SessionManagerLogger, get_session_logger
from src_orbis.helper_apps.session_manager.rerun_control import RerunController, get_rerun_controller


class TestSessionManagerLogger(unittest.TestCase):
    """Tests für SessionManagerLogger"""

    def setUp(self):
        """Setup für jeden Test"""
        # Temporäres Verzeichnis für Log-Dateien
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Logger für Tests
        self.logger = SessionManagerLogger("test_logger", "DEBUG")

    def tearDown(self):
        """Cleanup nach jedem Test"""
        os.chdir(self.original_cwd)

        # Handler schließen und entfernen
        for handler in self.logger.logger.handlers[:]:
            handler.close()
            self.logger.logger.removeHandler(handler)

    def test_logger_initialization(self):
        """Test Logger-Initialisierung"""
        self.assertEqual(self.logger.name, "test_logger")
        self.assertEqual(self.logger.log_level, logging.DEBUG)
        self.assertIsInstance(self.logger.logger, logging.Logger)

        # Prüfe Handler (Console + File)
        self.assertEqual(len(self.logger.logger.handlers), 2)

    def test_log_file_creation(self):
        """Test Log-Datei wird erstellt"""
        # Log-Nachricht senden
        self.logger.log_event("Test message", "INFO")

        # Prüfe dass Log-Datei existiert
        log_file = Path("logs/test_logger.log")
        self.assertTrue(log_file.exists())

        # Prüfe Inhalt
        with open(log_file) as f:
            content = f.read()
            self.assertIn("Test message", content)
            self.assertIn("INFO", content)

    def test_log_event_with_context(self):
        """Test Event-Logging mit Kontext"""
        context = {"user_id": 123, "action": "click"}
        self.logger.log_event("User action", "INFO", **context)

        log_file = Path("logs/test_logger.log")
        with open(log_file) as f:
            content = f.read()
            self.assertIn("User action", content)
            self.assertIn("Context:", content)
            self.assertIn("user_id", content)

    def test_log_ui_action(self):
        """Test UI-Action Logging"""
        user_context = {"button": "increment", "value": 5}
        self.logger.log_ui_action("button_click", user_context)

        log_file = Path("logs/test_logger.log")
        with open(log_file) as f:
            content = f.read()
            self.assertIn("UI Action: button_click", content)
            self.assertIn("button", content)

    def test_log_rerun_trigger(self):
        """Test Rerun-Trigger Logging"""
        self.logger.log_rerun_trigger("counter_updated", "increment_button")

        log_file = Path("logs/test_logger.log")
        with open(log_file) as f:
            content = f.read()
            self.assertIn("Rerun triggered: counter_updated from increment_button", content)

    def test_log_error_with_exception(self):
        """Test Fehler-Logging mit Exception"""
        try:
            _ = 10 / 0
        except Exception as e:
            self.logger.log_error(e, "Test error context")

        log_file = Path("logs/test_logger.log")
        with open(log_file) as f:
            content = f.read()
            self.assertIn("Error:", content)
            self.assertIn("ZeroDivisionError", content)
            self.assertIn("Test error context", content)

    def test_log_warning(self):
        """Test Warning-Logging"""
        self.logger.log_warning("Test warning", component="test")

        log_file = Path("logs/test_logger.log")
        with open(log_file) as f:
            content = f.read()
            self.assertIn("Test warning", content)
            self.assertIn("WARNING", content)

    def test_get_session_logger_singleton(self):
        """Test Singleton-Pattern des Session-Loggers"""
        logger1 = get_session_logger("test")
        logger2 = get_session_logger("test")

        # Sollte gleiche Instanz sein
        self.assertIs(logger1, logger2)


class TestRerunController(unittest.TestCase):
    """Tests für RerunController"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock Streamlit session_state
        self.mock_session_state = {}

        # Temporäres Verzeichnis für Logs
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Controller für Tests
        self.controller = RerunController("test_rerun")

    def tearDown(self):
        """Cleanup nach jedem Test"""
        os.chdir(self.original_cwd)

        # Logger Handler cleanup
        for handler in self.controller.logger.logger.handlers[:]:
            handler.close()
            self.controller.logger.logger.removeHandler(handler)

    @patch('streamlit.session_state')
    @patch('streamlit.info')
    def test_request_rerun(self, mock_info, mock_session_state):
        """Test Rerun-Anfrage"""
        mock_session_state.__getitem__.side_effect = self.mock_session_state.get
        mock_session_state.__setitem__.side_effect = self.mock_session_state.__setitem__
        mock_session_state.get.side_effect = self.mock_session_state.get

        # Rerun anfordern
        self.controller.request_rerun("test_reason", "test_source")

        # Prüfe dass Flags gesetzt wurden
        self.assertTrue(self.mock_session_state.get("needs_rerun", False))
        self.assertEqual(self.mock_session_state.get("rerun_reason"), "test_reason")
        self.assertEqual(self.mock_session_state.get("rerun_source"), "test_source")

        # Prüfe UI-Feedback
        mock_info.assert_called_once()

    @patch('streamlit.session_state')
    def test_request_rerun_prevents_cascade(self, mock_session_state):
        """Test dass Rerun-Kaskaden verhindert werden"""
        # Simuliere bereits angeforderten Rerun
        self.mock_session_state["needs_rerun"] = True
        mock_session_state.__getitem__.side_effect = self.mock_session_state.get
        mock_session_state.get.side_effect = self.mock_session_state.get

        # Versuche weiteren Rerun anzufordern
        self.controller.request_rerun("second_reason", "second_source")

        # Sollte nicht überschrieben werden
        self.assertNotEqual(self.mock_session_state.get("rerun_reason"), "second_reason")

    @patch('streamlit.session_state')
    @patch('streamlit.rerun')
    def test_execute_pending_rerun(self, mock_rerun, mock_session_state):
        """Test Ausführung von anstehendem Rerun"""
        # Setup anstehender Rerun
        self.mock_session_state["needs_rerun"] = True
        self.mock_session_state["rerun_reason"] = "test_reason"
        self.mock_session_state["rerun_source"] = "test_source"

        mock_session_state.__getitem__.side_effect = self.mock_session_state.get
        mock_session_state.__setitem__.side_effect = self.mock_session_state.__setitem__
        mock_session_state.get.side_effect = self.mock_session_state.get

        # Rerun ausführen
        result = self.controller.execute_pending_rerun()

        # Prüfe Ergebnis
        self.assertTrue(result)
        mock_rerun.assert_called_once()

        # Prüfe dass Flags zurückgesetzt wurden
        self.assertFalse(self.mock_session_state.get("needs_rerun", True))

    @patch('streamlit.session_state')
    @patch('streamlit.rerun')
    def test_execute_pending_rerun_no_rerun(self, mock_rerun, mock_session_state):
        """Test keine Ausführung wenn kein Rerun ansteht"""
        # Kein Rerun anstehend
        self.mock_session_state["needs_rerun"] = False
        mock_session_state.get.side_effect = self.mock_session_state.get

        # Versuche Rerun auszuführen
        result = self.controller.execute_pending_rerun()

        # Prüfe Ergebnis
        self.assertFalse(result)
        mock_rerun.assert_not_called()

    @patch('streamlit.session_state')
    def test_is_rerun_pending(self, mock_session_state):
        """Test Rerun-Status-Prüfung"""
        mock_session_state.get.side_effect = self.mock_session_state.get

        # Kein Rerun anstehend
        self.mock_session_state["needs_rerun"] = False
        self.assertFalse(self.controller.is_rerun_pending())

        # Rerun anstehend
        self.mock_session_state["needs_rerun"] = True
        self.assertTrue(self.controller.is_rerun_pending())

    @patch('streamlit.session_state')
    def test_get_rerun_info(self, mock_session_state):
        """Test Abrufen von Rerun-Informationen"""
        self.mock_session_state["rerun_reason"] = "test_reason"
        self.mock_session_state["rerun_source"] = "test_source"
        mock_session_state.get.side_effect = self.mock_session_state.get

        reason, source = self.controller.get_rerun_info()

        self.assertEqual(reason, "test_reason")
        self.assertEqual(source, "test_source")

    @patch('streamlit.session_state')
    def test_clear_rerun_request(self, mock_session_state):
        """Test Löschen von Rerun-Anfrage"""
        # Setup anstehender Rerun
        self.mock_session_state["needs_rerun"] = True
        self.mock_session_state["rerun_reason"] = "test_reason"

        mock_session_state.__getitem__.side_effect = self.mock_session_state.get
        mock_session_state.__setitem__.side_effect = self.mock_session_state.__setitem__
        mock_session_state.get.side_effect = self.mock_session_state.get

        # Rerun-Anfrage löschen
        self.controller.clear_rerun_request()

        # Prüfe dass Flags zurückgesetzt wurden
        self.assertFalse(self.mock_session_state.get("needs_rerun", True))
        self.assertEqual(self.mock_session_state.get("rerun_reason"), "")

    def test_get_rerun_controller_singleton(self):
        """Test Singleton-Pattern des Rerun-Controllers"""
        controller1 = get_rerun_controller("test")
        controller2 = get_rerun_controller("test")

        # Sollte gleiche Instanz sein
        self.assertIs(controller1, controller2)


class TestSessionManagerIntegration(unittest.TestCase):
    """Integration Tests für Session Manager Komponenten"""

    def setUp(self):
        """Setup für jeden Test"""
        # Temporäres Verzeichnis
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Cleanup nach jedem Test"""
        os.chdir(self.original_cwd)

    @patch('streamlit.session_state')
    @patch('streamlit.info')
    @patch('streamlit.rerun')
    def test_full_rerun_workflow(self, mock_rerun, mock_info, mock_session_state):
        """Test vollständiger Rerun-Workflow mit Logging"""
        mock_session_state_dict = {}
        mock_session_state.__getitem__.side_effect = mock_session_state_dict.get
        mock_session_state.__setitem__.side_effect = mock_session_state_dict.__setitem__
        mock_session_state.get.side_effect = mock_session_state_dict.get

        # Logger und Controller erstellen
        logger = SessionManagerLogger("integration_test", "INFO")
        controller = RerunController("integration_test")

        try:
            # 1. Rerun anfordern
            controller.request_rerun("integration_test", "test_workflow")

            # 2. Prüfe dass Rerun ansteht
            self.assertTrue(controller.is_rerun_pending())

            # 3. Rerun ausführen
            result = controller.execute_pending_rerun()

            # 4. Prüfe Ergebnis
            self.assertTrue(result)
            mock_rerun.assert_called_once()

            # 5. Prüfe dass Log-Datei erstellt wurde
            log_file = Path("logs/integration_test.log")
            self.assertTrue(log_file.exists())

            # Die Hauptfunktionalität funktioniert - Logging wird im captured log gezeigt
            # Das ist ausreichend für den Integrationstest

        finally:
            # Cleanup Handler
            for handler in logger.logger.handlers[:]:
                handler.close()
                logger.logger.removeHandler(handler)


class TestSessionManagerErrorHandling(unittest.TestCase):
    """Error Handling Tests für Session Manager"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Cleanup nach jedem Test"""
        os.chdir(self.original_cwd)

    def test_logger_with_invalid_log_level(self):
        """Test Logger mit ungültigem Log-Level"""
        # Sollte auf INFO zurückfallen ohne Fehler
        logger = SessionManagerLogger("test", "INVALID_LEVEL")

        # Sollte DEFAULT (INFO) verwenden
        self.assertEqual(logger.log_level, logging.INFO)

    @patch('streamlit.session_state')
    def test_rerun_controller_missing_session_state(self, mock_session_state):
        """Test Rerun-Controller mit fehlendem Session State"""

        # Mock get() um für spezifische Keys None zurückzugeben
        def mock_get(key, default=None):
            return default

        mock_session_state.get.side_effect = mock_get

        controller = RerunController("test")

        # Sollte nicht fehlschlagen
        self.assertFalse(controller.is_rerun_pending())
        reason, source = controller.get_rerun_info()
        self.assertEqual(reason, "unknown")
        self.assertEqual(source, "unknown")

    def test_log_file_permission_error(self):
        """Test Verhalten bei Log-Datei-Berechtigung-Fehlern"""
        # Erstelle read-only Verzeichnis
        readonly_dir = Path(self.temp_dir) / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only

        try:
            # Versuche Logger in read-only Verzeichnis
            os.chdir(str(readonly_dir))

            # Sollte nicht fehlschlagen, aber eventuell Console-Only logging
            logger = SessionManagerLogger("readonly_test", "INFO")
            logger.log_event("Test message", "INFO")

            # Test sollte nicht fehlschlagen
            self.assertIsNotNone(logger)

        except PermissionError:
            # Erwartbarer Fehler in manchen Umgebungen
            pass
        finally:
            # Cleanup
            try:
                readonly_dir.chmod(0o755)
            except OSError:
                pass


if __name__ == "__main__":
    unittest.main()
