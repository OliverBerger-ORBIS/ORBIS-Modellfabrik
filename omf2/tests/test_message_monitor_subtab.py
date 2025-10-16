#!/usr/bin/env python3
"""
Test für Enhanced View Subtab - testet die gesamte Funktionalität
"""

import time
import unittest
from unittest.mock import Mock, patch

from omf2.ui.utils.message_utils import MessageRow, flatten_messages_for_df


class TestMessageMonitorSubtab(unittest.TestCase):
    """Test für Message Monitor Subtab"""

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
    def test_render_message_monitor_subtab_basic(
        self, mock_success, mock_info, mock_columns, mock_markdown, mock_subheader, mock_session_state
    ):
        """Test: Basic rendering der Message Monitor Subtab"""
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

        mock_session_state["admin_mqtt_client"] = mock_client

        # Mock columns für UI layout
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Mock admin gateway
        mock_gateway = Mock()
        mock_gateway.get_all_buffers.return_value = {}
        mock_session_state["admin_gateway"] = mock_gateway

        # Test: Function sollte ohne Fehler laufen
        try:
            from omf2.ui.admin.message_center.message_monitor_subtab import render_message_monitor_subtab

            render_message_monitor_subtab(mock_client)
            # Wenn wir hier ankommen, ist der Test erfolgreich
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Message Monitor Subtab failed with error: {e}")

    def test_message_row_creation(self):
        """Test: MessageRow Dataclass funktioniert korrekt"""
        # Test MessageRow creation
        msg = MessageRow(
            topic="test/topic",
            payload={"test": "data"},
            message_type="received",
            timestamp=time.time(),
            qos=1,
            retain=False,
        )

        self.assertEqual(msg.topic, "test/topic")
        self.assertEqual(msg.payload, {"test": "data"})
        self.assertEqual(msg.message_type, "received")
        self.assertEqual(msg.qos, 1)
        self.assertFalse(msg.retain)

    def test_message_row_get_category(self):
        """Test: MessageRow.get_category() funktioniert korrekt"""
        # Test verschiedene Topic-Kategorien
        test_cases = [
            ("ccu/state", "ccu"),
            ("module/v1/ff/SVR3QA0022/state", "module"),
            ("txt/input", "txt"),
            ("nodered/flow", "nodered"),
            ("fts/transport", "fts"),
            ("unknown/topic", "Sonstige"),
        ]

        for topic, expected_category in test_cases:
            msg = MessageRow(
                topic=topic, payload={}, message_type="received", timestamp=time.time(), qos=0, retain=False
            )
            self.assertEqual(msg.get_category(), expected_category)

    def test_flatten_messages_for_df(self):
        """Test: flatten_messages_for_df() funktioniert korrekt"""
        # Test mit leeren Messages
        empty_df = flatten_messages_for_df([])
        self.assertTrue(empty_df.empty)

        # Test mit echten Messages
        messages = [
            MessageRow(
                topic="test/topic1",
                payload={"data": "test1"},
                message_type="received",
                timestamp=time.time(),
                qos=1,
                retain=False,
            ),
            MessageRow(
                topic="test/topic2",
                payload={"data": "test2"},
                message_type="sent",
                timestamp=time.time() + 1,
                qos=0,
                retain=True,
            ),
        ]

        df = flatten_messages_for_df(messages)

        # Prüfe DataFrame Struktur
        self.assertEqual(len(df), 2)
        self.assertIn("⏰", df.columns)
        self.assertIn("📨", df.columns)
        self.assertIn("🏷️", df.columns)
        self.assertIn("📡", df.columns)
        self.assertIn("📄", df.columns)
        self.assertIn("🔢", df.columns)
        self.assertIn("💾", df.columns)

        # Prüfe, dass keine "Sub-Kat" Spalte existiert
        self.assertNotIn("📋", df.columns)

    def test_message_filtering_by_category(self):
        """Test: Message filtering nach Kategorie"""
        from omf2.ui.utils.message_utils import filter_messages_by_category

        messages = [
            MessageRow("ccu/state", {}, "received", time.time(), 0, False),
            MessageRow("module/v1/ff/SVR3QA0022/state", {}, "received", time.time(), 0, False),
            MessageRow("txt/input", {}, "received", time.time(), 0, False),
        ]

        # Test CCU filtering
        ccu_messages = filter_messages_by_category(messages, "ccu")
        self.assertEqual(len(ccu_messages), 1)
        self.assertEqual(ccu_messages[0].topic, "ccu/state")

        # Test Module filtering
        module_messages = filter_messages_by_category(messages, "module")
        self.assertEqual(len(module_messages), 1)
        self.assertEqual(module_messages[0].topic, "module/v1/ff/SVR3QA0022/state")

    def test_message_filtering_by_type(self):
        """Test: Message filtering nach Typ"""
        from omf2.ui.utils.message_utils import filter_messages_by_type

        messages = [
            MessageRow("test/topic1", {}, "received", time.time(), 0, False),
            MessageRow("test/topic2", {}, "sent", time.time(), 0, False),
            MessageRow("test/topic3", {}, "received", time.time(), 0, False),
        ]

        # Test received filtering
        received_messages = filter_messages_by_type(messages, "received")
        self.assertEqual(len(received_messages), 2)

        # Test sent filtering
        sent_messages = filter_messages_by_type(messages, "sent")
        self.assertEqual(len(sent_messages), 1)

    def test_available_categories(self):
        """Test: get_available_categories() funktioniert"""
        from omf2.ui.utils.message_utils import get_available_categories

        categories = get_available_categories()

        # Prüfe, dass erwartete Kategorien vorhanden sind
        expected_categories = ["ccu", "module", "txt", "nodered", "fts", "Sonstige"]
        for category in expected_categories:
            self.assertIn(category, categories)

    @patch("streamlit.session_state")
    @patch("streamlit.subheader")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.info")
    @patch("streamlit.success")
    @patch("streamlit.error")
    def test_render_with_mqtt_client_error(
        self, mock_error, mock_success, mock_info, mock_columns, mock_markdown, mock_subheader, mock_session_state
    ):
        """Test: Message Monitor Subtab mit MQTT Client Fehler"""
        # Mock MQTT client mit Fehler
        mock_client = Mock()
        mock_client.get_connection_info.side_effect = Exception("Connection failed")

        mock_session_state["admin_mqtt_client"] = mock_client

        # Mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Test: Function sollte Fehler abfangen und error anzeigen
        try:
            # Mock conn_info direkt, da get_connection_info() eine Exception wirft
            from omf2.ui.admin.message_center.message_monitor_subtab import render_message_monitor_subtab

            render_message_monitor_subtab(mock_client)
            # Sollte error() aufgerufen haben
            mock_error.assert_called()
        except Exception as e:
            self.fail(f"Message Monitor Subtab should handle MQTT client errors gracefully: {e}")

    @patch("streamlit.session_state")
    @patch("streamlit.subheader")
    @patch("streamlit.markdown")
    @patch("streamlit.columns")
    @patch("streamlit.info")
    @patch("streamlit.success")
    def test_render_with_messages(
        self, mock_success, mock_info, mock_columns, mock_markdown, mock_subheader, mock_session_state
    ):
        """Test: Message Monitor Subtab mit echten Messages"""
        # Mock MQTT client mit Messages
        mock_client = Mock()
        mock_client.get_connection_info.return_value = {
            "connected": True,
            "environment": "mock",
            "client_id": "omf_admin_mock",
            "host": "localhost",
            "port": 1883,
            "mock_mode": True,
        }

        # Mock admin gateway mit Messages
        mock_gateway = Mock()
        mock_gateway.get_all_buffers.return_value = {
            "test/topic1": {"data": "test1", "timestamp": time.time()},
            "test/topic2": {"data": "test2", "timestamp": time.time()},
        }

        mock_session_state["admin_mqtt_client"] = mock_client
        mock_session_state["admin_gateway"] = mock_gateway

        # Mock columns
        mock_col1, mock_col2, mock_col3 = Mock(), Mock(), Mock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]

        # Test: Function sollte mit Messages funktionieren
        try:
            from omf2.ui.admin.message_center.message_monitor_subtab import render_message_monitor_subtab

            render_message_monitor_subtab(mock_client)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Message Monitor Subtab failed with messages: {e}")


if __name__ == "__main__":
    unittest.main()
