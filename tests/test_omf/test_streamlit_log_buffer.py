"""
Tests für streamlit_log_buffer.py - RingBufferHandler für Streamlit
"""

import logging
import unittest
from collections import deque

from omf.tools.streamlit_log_buffer import RingBufferHandler

class TestStreamlitLogBuffer(unittest.TestCase):
    """Tests für Streamlit Log Buffer"""

    def setUp(self):
        """Setup für jeden Test"""
        self.buffer = deque(maxlen=5)
        self.handler = RingBufferHandler(self.buffer)

    def test_ring_buffer_handler_initialization(self):
        """Test: RingBufferHandler initialisiert korrekt"""
        self.assertEqual(self.handler.buf, self.buffer)
        self.assertEqual(self.handler.level, logging.INFO)

    def test_ring_buffer_handler_emit(self):
        """Test: RingBufferHandler fügt Nachrichten zum Buffer hinzu"""
        # LogRecord erstellen
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Handler emit aufrufen
        self.handler.emit(record)

        # Buffer sollte Nachricht enthalten
        self.assertEqual(len(self.buffer), 1)
        self.assertIn("Test message", self.buffer[0])

    def test_ring_buffer_handler_maxlen(self):
        """Test: RingBufferHandler respektiert maxlen"""
        # Mehr Nachrichten als maxlen hinzufügen
        for i in range(7):  # maxlen ist 5
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=1,
                msg=f"Message {i}",
                args=(),
                exc_info=None,
            )
            self.handler.emit(record)

        # Buffer sollte nur 5 Nachrichten enthalten
        self.assertEqual(len(self.buffer), 5)

        # Älteste Nachrichten sollten entfernt worden sein
        self.assertIn("Message 2", self.buffer[0])  # Älteste verbleibende
        self.assertIn("Message 6", self.buffer[4])  # Neueste

    def test_ring_buffer_handler_emit_exception(self):
        """Test: RingBufferHandler behandelt Exceptions beim emit"""
        # Handler mit defektem Buffer
        broken_buffer = None
        handler = RingBufferHandler(broken_buffer)

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Sollte keine Exception werfen
        handler.emit(record)

    def test_ring_buffer_handler_different_levels(self):
        """Test: RingBufferHandler funktioniert mit verschiedenen Log-Levels"""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]

        for level in levels:
            record = logging.LogRecord(
                name="test_logger",
                level=level,
                pathname="test.py",
                lineno=1,
                msg=f"Message level {level}",
                args=(),
                exc_info=None,
            )
            self.handler.emit(record)

        # Alle Nachrichten sollten im Buffer sein
        self.assertEqual(len(self.buffer), len(levels))

        for i, level in enumerate(levels):
            self.assertIn(f"Message level {level}", self.buffer[i])

if __name__ == "__main__":
    unittest.main()
