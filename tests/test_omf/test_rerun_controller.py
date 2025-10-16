"""
Tests für RerunController - Thread-sichere st.rerun() Kontrolle

Testet:
- Thread-Safety mit threading.Lock()
- Debouncing-Funktionalität
- Force-Rerun Option
- Zeit-Messung seit letztem Rerun
"""

import threading
import time
import unittest
from unittest.mock import patch

from omf.dashboard.utils.ui_refresh import RerunController, get_rerun_controller, request_rerun_safe


class TestRerunController(unittest.TestCase):
    """Tests für RerunController Klasse"""

    def setUp(self):
        """Test-Setup"""
        self.controller = RerunController(debounce_ms=50)  # 50ms Debounce für Tests

    def test_initialization(self):
        """Test RerunController Initialisierung"""
        self.assertEqual(self.controller._debounce_ms, 50)
        self.assertEqual(self.controller._last_rerun, 0)
        self.assertIsInstance(self.controller._lock, threading.Lock)

    def test_force_rerun(self):
        """Test Force-Rerun funktioniert immer"""
        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            # Erster Force-Rerun
            result1 = self.controller.request_rerun(force=True)
            self.assertTrue(result1)
            self.assertEqual(mock_rerun.call_count, 1)

            # Sofortiger zweiter Force-Rerun
            result2 = self.controller.request_rerun(force=True)
            self.assertTrue(result2)
            self.assertEqual(mock_rerun.call_count, 2)

    def test_debouncing(self):
        """Test Debouncing verhindert zu häufige Reruns"""
        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            # Erster Rerun
            result1 = self.controller.request_rerun()
            self.assertTrue(result1)
            self.assertEqual(mock_rerun.call_count, 1)

            # Sofortiger zweiter Rerun (sollte debounced werden)
            result2 = self.controller.request_rerun()
            self.assertFalse(result2)
            self.assertEqual(mock_rerun.call_count, 1)  # Kein zusätzlicher Rerun

    def test_debounce_timeout(self):
        """Test Debounce-Zeit wird respektiert"""
        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            # Erster Rerun
            result1 = self.controller.request_rerun()
            self.assertTrue(result1)
            self.assertEqual(mock_rerun.call_count, 1)

            # Warten bis Debounce-Zeit verstrichen ist
            time.sleep(0.06)  # 60ms > 50ms Debounce

            # Zweiter Rerun nach Debounce-Zeit
            result2 = self.controller.request_rerun()
            self.assertTrue(result2)
            self.assertEqual(mock_rerun.call_count, 2)

    def test_time_since_last_rerun(self):
        """Test Zeit-Messung seit letztem Rerun"""
        with patch('streamlit.rerun'):
            # Vor Rerun
            time_before = self.controller.get_time_since_last_rerun()
            self.assertGreaterEqual(time_before, 0)

            # Rerun ausführen
            self.controller.request_rerun(force=True)

            # Nach Rerun
            time_after = self.controller.get_time_since_last_rerun()
            self.assertLess(time_after, 10)  # Sollte sehr klein sein

    def test_thread_safety(self):
        """Test Thread-Safety mit mehreren Threads"""
        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            results = []
            errors = []

            def worker():
                try:
                    result = self.controller.request_rerun(force=True)
                    results.append(result)
                except Exception as e:
                    errors.append(e)

            # Mehrere Threads starten
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=worker)
                threads.append(thread)
                thread.start()

            # Alle Threads warten
            for thread in threads:
                thread.join()

            # Prüfen dass keine Fehler aufgetreten sind
            self.assertEqual(len(errors), 0, f"Thread-Safety Fehler: {errors}")

            # Prüfen dass alle Reruns ausgeführt wurden
            self.assertEqual(len(results), 10)
            self.assertTrue(all(results))
            self.assertEqual(mock_rerun.call_count, 10)


class TestRerunControllerIntegration(unittest.TestCase):
    """Integration Tests für RerunController"""

    def test_global_controller_singleton(self):
        """Test globale RerunController-Instanz ist Singleton"""
        controller1 = get_rerun_controller()
        controller2 = get_rerun_controller()

        self.assertIs(controller1, controller2)

    def test_request_rerun_safe_function(self):
        """Test request_rerun_safe Funktion"""
        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            # Test Force-Anfrage (normale Anfrage kann debounced werden)
            result = request_rerun_safe(force=True)
            self.assertTrue(result)
            self.assertEqual(mock_rerun.call_count, 1)

            # Test zweite Force-Anfrage
            result = request_rerun_safe(force=True)
            self.assertTrue(result)
            self.assertEqual(mock_rerun.call_count, 2)

    def test_debounce_with_global_controller(self):
        """Test Debouncing mit globalem Controller"""
        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            controller = get_rerun_controller()
            controller._debounce_ms = 50  # 50ms für Test

            # Erster Rerun
            result1 = request_rerun_safe()
            self.assertTrue(result1)
            self.assertEqual(mock_rerun.call_count, 1)

            # Sofortiger zweiter Rerun (sollte debounced werden)
            result2 = request_rerun_safe()
            self.assertFalse(result2)
            self.assertEqual(mock_rerun.call_count, 1)


class TestRerunControllerEdgeCases(unittest.TestCase):
    """Edge Cases für RerunController"""

    def test_zero_debounce_time(self):
        """Test mit 0ms Debounce-Zeit"""
        controller = RerunController(debounce_ms=0)

        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            # Beide Reruns sollten ausgeführt werden
            result1 = controller.request_rerun()
            result2 = controller.request_rerun()

            self.assertTrue(result1)
            self.assertTrue(result2)
            self.assertEqual(mock_rerun.call_count, 2)

    def test_very_high_debounce_time(self):
        """Test mit sehr hoher Debounce-Zeit"""
        controller = RerunController(debounce_ms=10000)  # 10 Sekunden

        with patch('omf.dashboard.utils.ui_refresh.st.rerun') as mock_rerun:
            # Erster Rerun
            result1 = controller.request_rerun()
            self.assertTrue(result1)
            self.assertEqual(mock_rerun.call_count, 1)

            # Zweiter Rerun sollte debounced werden
            result2 = controller.request_rerun()
            self.assertFalse(result2)
            self.assertEqual(mock_rerun.call_count, 1)

            # Force-Rerun sollte funktionieren
            result3 = controller.request_rerun(force=True)
            self.assertTrue(result3)
            self.assertEqual(mock_rerun.call_count, 2)


if __name__ == '__main__':
    unittest.main()
