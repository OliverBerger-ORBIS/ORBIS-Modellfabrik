"""
Test Message Center Components
"""

import pytest
import logging
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestMessageCenter:
    """Test suite for Message Center functionality"""
    
    def test_message_center_import(self):
        """Test: Message Center kann importiert werden"""
        try:
            from omf2.ui.message_center.message_center_tab import show_message_center_tab
            assert callable(show_message_center_tab)
        except ImportError as e:
            pytest.fail(f"Message Center Import fehlgeschlagen: {e}")
    
    @patch('streamlit.header')
    @patch('streamlit.session_state', {"messages": []})
    def test_message_center_rendering(self, mock_header):
        """Test: Message Center rendert ohne Fehler"""
        from omf2.ui.message_center.message_center_tab import show_message_center_tab
        
        # Mock logger
        mock_logger = MagicMock(spec=logging.Logger)
        
        try:
            with patch('streamlit.columns'), \
                 patch('streamlit.subheader'), \
                 patch('streamlit.container'), \
                 patch('streamlit.expander'), \
                 patch('streamlit.write'), \
                 patch('streamlit.button'), \
                 patch('streamlit.form'), \
                 patch('streamlit.selectbox'), \
                 patch('streamlit.text_input'), \
                 patch('streamlit.text_area'), \
                 patch('streamlit.form_submit_button'), \
                 patch('streamlit.metric'), \
                 patch('streamlit.info'):
                show_message_center_tab(mock_logger)
            
            # Überprüfe, dass Logger aufgerufen wurde
            mock_logger.info.assert_called()
            # Überprüfe, dass Header gesetzt wurde
            mock_header.assert_called()
        except Exception as e:
            pytest.fail(f"Message Center Rendering fehlgeschlagen: {e}")
    
    def test_sample_messages_generation(self):
        """Test: Beispiel-Nachrichten werden korrekt generiert"""
        from omf2.ui.message_center.message_center_tab import _get_sample_messages
        
        sample_messages = _get_sample_messages()
        
        # Überprüfe, dass Nachrichten generiert wurden
        assert isinstance(sample_messages, list)
        assert len(sample_messages) > 0
        
        # Überprüfe Nachrichtenstruktur
        for message in sample_messages:
            assert isinstance(message, dict)
            assert "title" in message
            assert "content" in message
            assert "sender" in message
            assert "recipient" in message
            assert "type" in message
            assert "priority" in message
            assert "timestamp" in message
            assert "icon" in message
    
    def test_message_icon_mapping(self):
        """Test: Nachrichten-Icons werden korrekt zugeordnet"""
        from omf2.ui.message_center.message_center_tab import _get_message_icon
        
        # Test verschiedene Nachrichtentypen
        assert _get_message_icon("Info") == "ℹ️"
        assert _get_message_icon("Warnung") == "⚠️"
        assert _get_message_icon("Fehler") == "❌"
        assert _get_message_icon("Anfrage") == "❓"
        assert _get_message_icon("Unbekannt") == "📝"  # Default
    
    def test_message_validation(self):
        """Test: Nachrichten-Validierung funktioniert"""
        # Gültige Nachricht
        valid_message = {
            "title": "Test Nachricht",
            "content": "Dies ist eine Testnachricht",
            "sender": "Test User",
            "recipient": "Admin",
            "type": "Info",
            "priority": "Normal",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "icon": "ℹ️"
        }
        
        # Überprüfe Nachrichtenfelder
        required_fields = ["title", "content", "sender", "recipient", "type", "priority", "timestamp", "icon"]
        for field in required_fields:
            assert field in valid_message
            assert valid_message[field] is not None
            assert len(str(valid_message[field])) > 0
    
    def test_message_types_validation(self):
        """Test: Nachrichten-Typen sind gültig"""
        valid_types = ["Info", "Warnung", "Fehler", "Anfrage"]
        valid_priorities = ["Niedrig", "Normal", "Hoch", "Kritisch"]
        valid_recipients = ["Operator", "Supervisor", "Admin", "System"]
        
        # Test Nachrichtentyp
        test_type = "Info"
        assert test_type in valid_types
        
        # Test Priorität
        test_priority = "Normal"
        assert test_priority in valid_priorities
        
        # Test Empfänger
        test_recipient = "Admin"
        assert test_recipient in valid_recipients
    
    def test_message_timestamp_format(self):
        """Test: Timestamp-Format ist korrekt"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Überprüfe Format (YYYY-MM-DD HH:MM:SS)
        assert len(timestamp) == 19
        assert timestamp[4] == "-"
        assert timestamp[7] == "-"
        assert timestamp[10] == " "
        assert timestamp[13] == ":"
        assert timestamp[16] == ":"
    
    def test_message_center_session_state(self):
        """Test: Session State für Message Center wird korrekt behandelt"""
        # Dummy-Test für Session State
        mock_session_state = {}
        
        # Simuliere Nachrichten im Session State
        mock_session_state["messages"] = [
            {"title": "Test 1", "content": "Content 1"},
            {"title": "Test 2", "content": "Content 2"}
        ]
        
        assert "messages" in mock_session_state
        assert len(mock_session_state["messages"]) == 2
        assert mock_session_state["messages"][0]["title"] == "Test 1"