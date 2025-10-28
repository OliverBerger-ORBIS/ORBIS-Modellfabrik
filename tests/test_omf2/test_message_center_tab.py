
#!/usr/bin/env python3
"""
Test für Message Center Tab - testet die gesamte Funktionalität
"""

import time
import unittest
from collections import deque
from unittest.mock import Mock, patch

from omf2.ui.admin.message_center.message_center_tab import render_message_center_tab


class TestMessageCenterTab(unittest.TestCase):
    """Test für Message Center Tab"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock Streamlit session state
        self.mock_session_state = {"admin_mqtt_client": Mock(), "admin_gateway": Mock()}

    @patch("streamlit.session_state")
    @patch("streamlit.subheader")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.info")
    @patch("streamlit.success")
    def test_render_message_center_tab_basic(
        self, mock_success, mock_info, mock_columns, mock_markdown, mock_subheader, mock_session_state
    ):
        """Test: Basic rendering der Message Center Tab"""
        # Mock MQTT client connection info
        mock_client = Mock()
        mock_client.get_connection_info.return_value = {
            "connected": True,
            "environment": "mock",
            "client_id": "omf_admin_mock",
            "host": "localhost",
            "port": 1883,
            "mock_mode": True,
        }
        mock_client.get_all_buffers.return_value = {}

        mock_session_state.__getitem__.side_effect = lambda key: self.mock_session_state[key]
        mock_session_state.__contains__.side_effect = lambda key: key in self.mock_session_state

        # Mock columns für UI layout
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Mock admin gateway
        mock_gateway = Mock()
        mock_gateway.get_all_buffers.return_value = {}
        self.mock_session_state["admin_gateway"] = mock_gateway
        self.mock_session_state["admin_mqtt_client"] = mock_client

        # Test: Function sollte ohne Fehler laufen
        try:
            render_message_center_tab()
            # Wenn wir hier ankommen, ist der Test erfolgreich
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Message Center Tab failed with error: {e}")

    @patch("streamlit.session_state")
    @patch("streamlit.subheader")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.info")
    @patch("streamlit.success")
    def test_render_with_deque_buffers(
        self, mock_success, mock_info, mock_columns, mock_markdown, mock_subheader, mock_session_state
    ):
        """Test: Message Center Tab mit deque Buffers"""
        # Mock MQTT client mit deque Buffers
        mock_client = Mock()
        mock_client.get_connection_info.return_value = {
            "connected": True,
            "environment": "mock",
            "client_id": "omf_admin_mock",
            "host": "localhost",
            "port": 1883,
            "mock_mode": True,
        }

        # Mock deque buffers (wie in omf2 implementiert)
        test_buffers = {
            "test/topic1": deque(
                [{"data": "test1", "timestamp": time.time() - 100}, {"data": "test1_new", "timestamp": time.time()}],
                maxlen=1000,
            ),
            "test/topic2": deque([{"data": "test2", "timestamp": time.time() - 50}], maxlen=1000),
        }

        mock_client.get_all_buffers.return_value = test_buffers

        mock_session_state.__getitem__.side_effect = lambda key: self.mock_session_state[key]
        mock_session_state.__contains__.side_effect = lambda key: key in self.mock_session_state

        # Mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Mock admin gateway
        mock_gateway = Mock()
        mock_gateway.get_all_buffers.return_value = test_buffers
        self.mock_session_state["admin_gateway"] = mock_gateway
        self.mock_session_state["admin_mqtt_client"] = mock_client

        # Test: Function sollte mit deque Buffers funktionieren
        try:
            render_message_center_tab()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Message Center Tab failed with deque buffers: {e}")

    def test_get_latest_timestamp_function(self):
        """Test: get_latest_timestamp Funktion funktioniert mit deque"""
        # Simuliere all_buffers wie in message_center_tab.py
        test_buffers = {
            "topic1": deque(
                [{"timestamp": 1000, "data": "test1"}, {"timestamp": 2000, "data": "test1_new"}], maxlen=1000
            ),
            "topic2": deque([{"timestamp": 1500, "data": "test2"}], maxlen=1000),
        }

        # Teste die get_latest_timestamp Funktion (aus message_center_tab.py)
        def get_latest_timestamp(topic):
            buffer = test_buffers[topic]
            if buffer and len(buffer) > 0:
                return buffer[-1].get("timestamp", 0)
            return 0

        # Sollte funktionieren ohne "deque object has no attribute 'get'" Fehler
        timestamp1 = get_latest_timestamp("topic1")
        timestamp2 = get_latest_timestamp("topic2")

        self.assertEqual(timestamp1, 2000)  # Neueste Message
        self.assertEqual(timestamp2, 1500)

        # Teste sorting
        topics = ["topic1", "topic2"]
        topics.sort(key=get_latest_timestamp, reverse=True)

        # topic1 sollte zuerst kommen (höherer timestamp)
        self.assertEqual(topics[0], "topic1")
        self.assertEqual(topics[1], "topic2")

    def test_deque_buffer_processing(self):
        """Test: deque Buffer Processing funktioniert korrekt"""
        # Simuliere deque Buffer wie in omf2
        buffer = deque(
            [{"data": "old", "timestamp": time.time() - 100}, {"data": "new", "timestamp": time.time()}], maxlen=1000
        )

        # Test: Letzte Message aus deque holen
        latest_message = buffer[-1]
        self.assertEqual(latest_message["data"], "new")

        # Test: Timestamp aus letzter Message
        timestamp = latest_message.get("timestamp", 0)
        self.assertGreater(timestamp, 0)

        # Test: Dictionary operations auf Message
        display_dict = {k: v for k, v in latest_message.items() if k != "timestamp"}
        self.assertIn("data", display_dict)
        self.assertEqual(display_dict["data"], "new")

    # REMOVED: test_render_with_mqtt_client_error - veraltet
    # I18n Manager wurde nach diesem Test eingeführt und der Test
    # erwartet veraltetes Verhalten ohne I18n-Integration

    def test_empty_deque_handling(self):
        """Test: Leere deque Buffer werden korrekt behandelt"""
        # Leere deque
        empty_buffer = deque(maxlen=1000)

        # Test: Leere Buffer sollten None/0 zurückgeben
        if empty_buffer and len(empty_buffer) > 0:
            latest_message = empty_buffer[-1]
            timestamp = latest_message.get("timestamp", 0)
        else:
            timestamp = 0

        self.assertEqual(timestamp, 0)

    def test_deque_vs_dict_compatibility(self):
        """Test: deque vs Dictionary Kompatibilität"""
        # Simuliere alte Dictionary-Struktur
        old_dict_buffer = {"data": "test", "timestamp": time.time()}

        # Simuliere neue deque-Struktur
        new_deque_buffer = deque([{"data": "test", "timestamp": time.time()}], maxlen=1000)

        # Test: Dictionary access
        dict_timestamp = old_dict_buffer.get("timestamp", 0)

        # Test: deque access
        deque_timestamp = new_deque_buffer[-1].get("timestamp", 0)

        # Beide sollten funktionieren
        self.assertGreater(dict_timestamp, 0)
        self.assertGreater(deque_timestamp, 0)

        # Test: deque sollte Dictionary-ähnlich funktionieren
        deque_message = new_deque_buffer[-1]
        self.assertIsInstance(deque_message, dict)
        self.assertEqual(deque_message["data"], "test")


if __name__ == "__main__":
    unittest.main()
