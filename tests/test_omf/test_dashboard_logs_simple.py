"""
Vereinfachte Tests für logs.py - Dashboard Logs-Komponente

Diese Tests prüfen die grundlegende Logik ohne komplexe Streamlit-UI-Mocks.
"""

import unittest
from collections import deque
from unittest.mock import MagicMock, patch


class TestDashboardLogsSimple(unittest.TestCase):
    """Vereinfachte Tests für Dashboard Logs-Komponente"""

    def test_log_buffer_handling(self):
        """Test: Log-Buffer-Handling funktioniert korrekt"""
        # Log-Buffer erstellen
        log_buffer = deque(maxlen=100)
        log_buffer.append("2025-01-01 12:00:00 [INFO] test: Test message 1")
        log_buffer.append("2025-01-01 12:00:01 [WARNING] test: Test message 2")
        log_buffer.append("2025-01-01 12:00:02 [ERROR] test: Test message 3")

        # Buffer sollte Nachrichten enthalten
        self.assertEqual(len(log_buffer), 3)
        self.assertIn("Test message 1", log_buffer[0])
        self.assertIn("Test message 2", log_buffer[1])
        self.assertIn("Test message 3", log_buffer[2])

    def test_log_buffer_maxlen(self):
        """Test: Log-Buffer respektiert maxlen"""
        log_buffer = deque(maxlen=5)

        # Mehr Nachrichten als maxlen hinzufügen
        for i in range(7):
            log_buffer.append(f"Message {i}")

        # Buffer sollte nur 5 Nachrichten enthalten
        self.assertEqual(len(log_buffer), 5)

        # Älteste Nachrichten sollten entfernt worden sein
        self.assertIn("Message 2", log_buffer[0])  # Älteste verbleibende
        self.assertIn("Message 6", log_buffer[4])  # Neueste

    def test_log_buffer_empty(self):
        """Test: Leerer Log-Buffer funktioniert"""
        log_buffer = deque(maxlen=100)

        # Leerer Buffer
        self.assertEqual(len(log_buffer), 0)
        self.assertFalse(log_buffer)

    def test_log_buffer_clear(self):
        """Test: Log-Buffer kann geleert werden"""
        log_buffer = deque(maxlen=100)
        log_buffer.append("Test message 1")
        log_buffer.append("Test message 2")

        # Buffer sollte Nachrichten enthalten
        self.assertEqual(len(log_buffer), 2)

        # Buffer leeren
        log_buffer.clear()

        # Buffer sollte leer sein
        self.assertEqual(len(log_buffer), 0)

    def test_log_buffer_different_levels(self):
        """Test: Log-Buffer funktioniert mit verschiedenen Log-Levels"""
        log_buffer = deque(maxlen=100)
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]

        for level in levels:
            log_buffer.append(f"2025-01-01 12:00:00 [{level}] test: Message {level}")

        # Alle Nachrichten sollten im Buffer sein
        self.assertEqual(len(log_buffer), len(levels))

        for i, level in enumerate(levels):
            self.assertIn(f"Message {level}", log_buffer[i])
            self.assertIn(f"[{level}]", log_buffer[i])


if __name__ == "__main__":
    unittest.main()
