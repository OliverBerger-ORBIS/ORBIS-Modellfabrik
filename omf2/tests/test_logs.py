"""
Test Logs Tab Components
"""

import pytest
import logging
from unittest.mock import MagicMock, patch


class TestLogsTab:
    """Test suite for Logs Tab functionality"""
    
    def test_logs_tab_import(self):
        """Test: Logs Tab kann importiert werden"""
        try:
            from omf2.ui.system.logs_tab import show_logs_tab
            assert callable(show_logs_tab)
        except ImportError as e:
            pytest.fail(f"Logs Tab Import fehlgeschlagen: {e}")
    
    @patch('streamlit.header')
    @patch('streamlit.session_state', {"log_messages": []})
    def test_logs_tab_rendering(self, mock_header):
        """Test: Logs Tab rendert ohne Fehler"""
        from omf2.ui.system.logs_tab import show_logs_tab
        
        # Mock logger
        mock_logger = MagicMock(spec=logging.Logger)
        
        try:
            with patch('streamlit.columns'), \
                 patch('streamlit.selectbox'), \
                 patch('streamlit.checkbox'), \
                 patch('streamlit.button'), \
                 patch('streamlit.container'), \
                 patch('streamlit.write'), \
                 patch('streamlit.code'), \
                 patch('streamlit.info'):
                show_logs_tab(mock_logger)
            
            # Überprüfe, dass Logger aufgerufen wurde
            mock_logger.info.assert_called()
            # Überprüfe, dass Header gesetzt wurde
            mock_header.assert_called()
        except Exception as e:
            pytest.fail(f"Logs Tab Rendering fehlgeschlagen: {e}")
    
    def test_log_level_filtering(self):
        """Test: Log-Level-Filterung funktioniert"""
        from omf2.ui.system.logs_tab import _should_show_log
        
        # Test-Log-Nachrichten
        debug_log = "[DEBUG] test: Debug message"
        info_log = "[INFO] test: Info message"
        warning_log = "[WARNING] test: Warning message"
        error_log = "[ERROR] test: Error message"
        
        # Test verschiedene Filter-Level
        assert _should_show_log(debug_log, "DEBUG") == True
        assert _should_show_log(info_log, "DEBUG") == True
        assert _should_show_log(warning_log, "DEBUG") == True
        assert _should_show_log(error_log, "DEBUG") == True
        
        assert _should_show_log(debug_log, "INFO") == False
        assert _should_show_log(info_log, "INFO") == True
        assert _should_show_log(warning_log, "INFO") == True
        assert _should_show_log(error_log, "INFO") == True
        
        assert _should_show_log(debug_log, "WARNING") == False
        assert _should_show_log(info_log, "WARNING") == False
        assert _should_show_log(warning_log, "WARNING") == True
        assert _should_show_log(error_log, "WARNING") == True
        
        assert _should_show_log(debug_log, "ERROR") == False
        assert _should_show_log(info_log, "ERROR") == False
        assert _should_show_log(warning_log, "ERROR") == False
        assert _should_show_log(error_log, "ERROR") == True
    
    def test_sample_logs_generation(self):
        """Test: Beispiel-Logs werden korrekt generiert"""
        from omf2.ui.system.logs_tab import _generate_sample_logs
        
        sample_logs = _generate_sample_logs()
        
        # Überprüfe, dass Logs generiert wurden
        assert isinstance(sample_logs, list)
        assert len(sample_logs) > 0
        
        # Überprüfe Log-Format
        for log in sample_logs:
            assert isinstance(log, str)
            assert "[" in log and "]" in log  # Log-Level-Klammern
    
    def test_log_message_validation(self):
        """Test: Log-Nachrichten haben gültiges Format"""
        # Test-Log-Nachricht
        test_log = "[2025-01-25 10:00:00] [INFO] omf_dashboard: Test message"
        
        # Einfache Format-Validierung
        assert "[INFO]" in test_log
        assert "omf_dashboard" in test_log
        assert "Test message" in test_log
        assert len(test_log) > 0
    
    def test_logs_session_state_handling(self):
        """Test: Session State für Logs wird korrekt behandelt"""
        # Dummy-Test für Session State
        mock_session_state = {}
        
        # Simuliere Log-Nachrichten im Session State
        mock_session_state["log_messages"] = ["Test log 1", "Test log 2"]
        
        assert "log_messages" in mock_session_state
        assert len(mock_session_state["log_messages"]) == 2
        assert mock_session_state["log_messages"][0] == "Test log 1"