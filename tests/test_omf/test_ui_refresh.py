"""
Tests für ui_refresh.py - Zentraler UI-Refresh-Mechanismus
"""

import time
import unittest
from unittest.mock import MagicMock, patch

from omf.dashboard.utils.ui_refresh import consume_refresh, request_refresh

class TestUIRefresh(unittest.TestCase):
    """Tests für UI-Refresh-Mechanismus"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock Streamlit session_state
        self.mock_session_state = {}

    @patch('omf.dashboard.utils.ui_refresh.st')
    def test_request_refresh_sets_flag(self, mock_st):
        """Test: request_refresh() setzt Flag in session_state"""
        mock_st.session_state = self.mock_session_state

        # Flag sollte nicht existieren
        self.assertNotIn("_ui_refresh_requested_at", mock_st.session_state)

        # request_refresh() aufrufen
        request_refresh()

        # Flag sollte gesetzt sein
        self.assertIn("_ui_refresh_requested_at", mock_st.session_state)
        self.assertIsInstance(mock_st.session_state["_ui_refresh_requested_at"], (int, float))

    @patch('omf.dashboard.utils.ui_refresh.st')
    def test_consume_refresh_returns_true_once(self, mock_st):
        """Test: consume_refresh() gibt genau einmal True zurück"""
        mock_st.session_state = self.mock_session_state

        # Flag setzen
        mock_st.session_state["_ui_refresh_requested_at"] = time.time()

        # Erster Aufruf sollte True zurückgeben
        result1 = consume_refresh()
        self.assertTrue(result1)

        # Flag sollte gelöscht sein
        self.assertEqual(mock_st.session_state.get("_ui_refresh_requested_at", 0), 0)

        # Zweiter Aufruf sollte False zurückgeben
        result2 = consume_refresh()
        self.assertFalse(result2)

    @patch('omf.dashboard.utils.ui_refresh.st')
    def test_consume_refresh_no_flag_returns_false(self, mock_st):
        """Test: consume_refresh() ohne Flag gibt False zurück"""
        mock_st.session_state = self.mock_session_state

        # Kein Flag gesetzt
        result = consume_refresh()
        self.assertFalse(result)

    @patch('omf.dashboard.utils.ui_refresh.st')
    def test_consume_refresh_zero_flag_returns_false(self, mock_st):
        """Test: consume_refresh() mit Flag=0 gibt False zurück"""
        mock_st.session_state = self.mock_session_state

        # Flag auf 0 setzen
        mock_st.session_state["_ui_refresh_requested_at"] = 0

        result = consume_refresh()
        self.assertFalse(result)

    @patch('omf.dashboard.utils.ui_refresh.st')
    def test_request_refresh_updates_timestamp(self, mock_st):
        """Test: request_refresh() aktualisiert Timestamp bei wiederholten Aufrufen"""
        mock_st.session_state = self.mock_session_state

        # Ersten Timestamp setzen
        request_refresh()
        timestamp1 = mock_st.session_state["_ui_refresh_requested_at"]

        # Kurz warten
        time.sleep(0.001)

        # Zweiten Timestamp setzen
        request_refresh()
        timestamp2 = mock_st.session_state["_ui_refresh_requested_at"]

        # Timestamp sollte aktualisiert worden sein
        self.assertGreater(timestamp2, timestamp1)

if __name__ == "__main__":
    unittest.main()
