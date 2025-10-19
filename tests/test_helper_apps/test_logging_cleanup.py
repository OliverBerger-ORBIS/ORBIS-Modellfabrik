"""
Tests für Logging Cleanup und RingBuffer Integration

Testet:
- Cleanup alter Log-Dateien beim Start
- RingBuffer Integration ins Logging-System
- Thread-sichere Log-Ausgabe in File und RingBuffer
"""

import logging
import tempfile
import unittest
from collections import deque
from pathlib import Path

from session_manager.utils.logging_config import cleanup_old_logs, configure_logging
from session_manager.utils.streamlit_log_buffer import create_log_buffer


class TestLoggingCleanup(unittest.TestCase):
    """Tests für Log-Cleanup Funktionalität"""

    def setUp(self):
        """Test-Setup mit temporärem Verzeichnis"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Test-Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cleanup_old_logs_deletes_files(self):
        """Test dass cleanup_old_logs alte Log-Dateien löscht"""
        # Erstelle Test-Log-Dateien
        log_file1 = self.temp_dir / "session_manager.jsonl"
        log_file2 = self.temp_dir / "session_manager.jsonl.1"
        log_file3 = self.temp_dir / "session_manager.jsonl.2"
        
        log_file1.write_text("log content 1")
        log_file2.write_text("log content 2")
        log_file3.write_text("log content 3")
        
        # Cleanup ausführen
        cleanup_old_logs(self.temp_dir, "session_manager.jsonl*")
        
        # Alle Dateien sollten gelöscht sein
        self.assertFalse(log_file1.exists())
        self.assertFalse(log_file2.exists())
        self.assertFalse(log_file3.exists())

    def test_cleanup_old_logs_with_nonexistent_directory(self):
        """Test dass cleanup mit nicht-existierendem Verzeichnis nicht fehlschlägt"""
        nonexistent_dir = self.temp_dir / "does_not_exist"
        
        # Sollte nicht fehlschlagen
        cleanup_old_logs(nonexistent_dir)
        
        # Verzeichnis sollte nicht erstellt worden sein
        self.assertFalse(nonexistent_dir.exists())

    def test_cleanup_old_logs_with_different_pattern(self):
        """Test dass cleanup nur Dateien mit passendem Pattern löscht"""
        # Erstelle verschiedene Log-Dateien
        log_file1 = self.temp_dir / "session_manager.jsonl"
        log_file2 = self.temp_dir / "other_app.log"
        
        log_file1.write_text("log content 1")
        log_file2.write_text("log content 2")
        
        # Cleanup nur für session_manager Logs
        cleanup_old_logs(self.temp_dir, "session_manager.jsonl*")
        
        # Nur session_manager.jsonl sollte gelöscht sein
        self.assertFalse(log_file1.exists())
        self.assertTrue(log_file2.exists())


class TestRingBufferIntegration(unittest.TestCase):
    """Tests für RingBuffer Integration"""

    def setUp(self):
        """Test-Setup"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.ring_buffer = create_log_buffer(maxlen=100)

    def tearDown(self):
        """Test-Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Logging-Handler aufräumen
        root_logger = logging.getLogger()
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

    def test_configure_logging_with_ring_buffer(self):
        """Test dass configure_logging mit RingBuffer funktioniert"""
        # Logging mit RingBuffer konfigurieren
        root, listener = configure_logging(
            app_name="test_app",
            level=logging.INFO,
            log_dir=self.temp_dir,
            json_file="test.jsonl",
            ring_buffer=self.ring_buffer,
            cleanup_on_start=False,
            console_pretty=False,
        )
        
        self.assertIsNotNone(root)
        self.assertIsNotNone(listener)
        
        # Listener stoppen
        listener.stop()

    def test_ring_buffer_receives_log_messages(self):
        """Test dass RingBuffer Log-Nachrichten empfängt"""
        # Logging mit RingBuffer konfigurieren
        root, listener = configure_logging(
            app_name="test_app",
            level=logging.INFO,
            log_dir=self.temp_dir,
            json_file="test.jsonl",
            ring_buffer=self.ring_buffer,
            cleanup_on_start=False,
            console_pretty=False,
        )
        
        # Test-Logger erstellen
        logger = logging.getLogger("test_logger")
        
        # Log-Nachricht senden
        test_message = "Test-Nachricht für RingBuffer"
        logger.info(test_message)
        
        # Warten bis Queue geleert ist
        import time
        time.sleep(0.1)
        
        # Prüfen dass Nachricht im RingBuffer ist
        buffer_content = "\n".join(self.ring_buffer)
        self.assertIn(test_message, buffer_content)
        
        # Listener stoppen
        listener.stop()

    def test_ring_buffer_max_size(self):
        """Test dass RingBuffer maximale Größe respektiert"""
        small_buffer = create_log_buffer(maxlen=5)
        
        # Logging mit kleinem RingBuffer konfigurieren
        root, listener = configure_logging(
            app_name="test_app",
            level=logging.INFO,
            log_dir=self.temp_dir,
            json_file="test.jsonl",
            ring_buffer=small_buffer,
            cleanup_on_start=False,
            console_pretty=False,
        )
        
        # Test-Logger erstellen
        logger = logging.getLogger("test_logger")
        
        # Mehr Nachrichten senden als Buffer groß ist
        for i in range(10):
            logger.info(f"Nachricht {i}")
        
        # Warten bis Queue geleert ist
        import time
        time.sleep(0.1)
        
        # Buffer sollte maximal 5 Einträge haben
        self.assertLessEqual(len(small_buffer), 5)
        
        # Listener stoppen
        listener.stop()

    def test_file_and_ring_buffer_both_receive_logs(self):
        """Test dass beide Handler (File und RingBuffer) Logs erhalten"""
        # Logging mit RingBuffer konfigurieren
        root, listener = configure_logging(
            app_name="test_app",
            level=logging.INFO,
            log_dir=self.temp_dir,
            json_file="test.jsonl",
            ring_buffer=self.ring_buffer,
            cleanup_on_start=False,
            console_pretty=False,
        )
        
        # Test-Logger erstellen
        logger = logging.getLogger("test_logger")
        
        # Log-Nachricht senden
        test_message = "Test für File und RingBuffer"
        logger.info(test_message)
        
        # Warten bis Queue geleert ist
        import time
        time.sleep(0.1)
        
        # Listener stoppen um File zu flushen
        listener.stop()
        
        # Prüfen dass Nachricht im RingBuffer ist
        buffer_content = "\n".join(self.ring_buffer)
        self.assertIn(test_message, buffer_content)
        
        # Prüfen dass Nachricht in Log-Datei ist
        log_file = self.temp_dir / "test.jsonl"
        self.assertTrue(log_file.exists())
        
        log_content = log_file.read_text()
        self.assertIn(test_message, log_content)


class TestLoggingCleanupIntegration(unittest.TestCase):
    """Integration Tests für Cleanup und Logging"""

    def setUp(self):
        """Test-Setup"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Test-Cleanup"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Logging-Handler aufräumen
        root_logger = logging.getLogger()
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

    def test_cleanup_on_start_deletes_old_logs(self):
        """Test dass cleanup_on_start alte Logs beim Start löscht"""
        # Erstelle alte Log-Dateien
        old_log1 = self.temp_dir / "test.jsonl.1"
        old_log2 = self.temp_dir / "test.jsonl.2"
        old_log1.write_text("old content 1")
        old_log2.write_text("old content 2")
        
        # Logging mit cleanup_on_start konfigurieren
        root, listener = configure_logging(
            app_name="test_app",
            level=logging.INFO,
            log_dir=self.temp_dir,
            json_file="test.jsonl",
            cleanup_on_start=True,
            console_pretty=False,
        )
        
        # Alte Backup-Log-Dateien sollten gelöscht sein
        self.assertFalse(old_log1.exists())
        self.assertFalse(old_log2.exists())
        
        # Neue Log-Datei sollte existieren (wird von RotatingFileHandler erstellt)
        new_log = self.temp_dir / "test.jsonl"
        self.assertTrue(new_log.exists())
        
        # Listener stoppen
        listener.stop()

    def test_no_cleanup_when_disabled(self):
        """Test dass Logs nicht gelöscht werden wenn cleanup_on_start=False"""
        # Erstelle alte Log-Datei
        old_log = self.temp_dir / "test.jsonl.1"
        old_log.write_text("old content")
        
        # Logging ohne cleanup_on_start konfigurieren
        root, listener = configure_logging(
            app_name="test_app",
            level=logging.INFO,
            log_dir=self.temp_dir,
            json_file="test.jsonl",
            cleanup_on_start=False,
            console_pretty=False,
        )
        
        # Alte Log-Datei sollte noch existieren
        self.assertTrue(old_log.exists())
        
        # Listener stoppen
        listener.stop()


if __name__ == '__main__':
    unittest.main()
