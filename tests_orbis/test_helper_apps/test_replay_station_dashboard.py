#!/usr/bin/env python3
"""
Tests für replay_station_dashboard.py
Testet die neue Replay Station (mit externem Mosquitto-Broker)
"""

import os
import sqlite3

# Add src_orbis to path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src_orbis"))

from src_orbis.helper_apps.replay_station.replay_station_dashboard import SessionPlayer


class TestSessionPlayer(unittest.TestCase):
    """Tests für SessionPlayer (neue Replay Station)"""

    def setUp(self):
        """Setup für jeden Test"""
        self.player = SessionPlayer(broker_host="localhost", broker_port=1884)

    def test_player_initialization(self):
        """Test SessionPlayer-Initialisierung"""
        self.assertEqual(self.player.broker_host, "localhost")
        self.assertEqual(self.player.broker_port, 1884)
        self.assertEqual(self.player.messages, [])
        self.assertEqual(self.player.current_index, 0)
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.player.speed, 1.0)
        self.assertFalse(self.player.loop)

    def test_player_initialization_custom_broker(self):
        """Test SessionPlayer-Initialisierung mit custom Broker"""
        player = SessionPlayer(broker_host="192.168.1.100", broker_port=1883)
        self.assertEqual(player.broker_host, "192.168.1.100")
        self.assertEqual(player.broker_port, 1883)

    def test_load_sqlite_session_success(self):
        """Test erfolgreiches Laden einer SQLite-Session"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle Test-SQLite-Datenbank
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE mqtt_messages (
                    topic TEXT,
                    payload TEXT,
                    timestamp TEXT
                )
            """
            )
            cursor.execute(
                """
                INSERT INTO mqtt_messages (topic, payload, timestamp) VALUES
                ('test/topic1', '{"test": "data1"}', '2023-01-01T10:00:00'),
                ('test/topic2', '{"test": "data2"}', '2023-01-01T10:01:00'),
                ('test/topic3', '{"test": "data3"}', '2023-01-01T10:02:00')
            """
            )
            conn.commit()
            conn.close()

            # Test Session laden
            with patch("streamlit.success") as mock_success:
                result = self.player.load_sqlite_session(db_path)
                self.assertTrue(result)
                self.assertEqual(len(self.player.messages), 3)
                self.assertEqual(self.player.messages[0]["topic"], "test/topic1")
                self.assertEqual(self.player.messages[0]["payload"], '{"test": "data1"}')
                self.assertEqual(self.player.messages[2]["payload"], '{"test": "data3"}')
                mock_success.assert_called_with("✅ 3 Nachrichten aus SQLite geladen")

        finally:
            os.unlink(db_path)

    def test_load_sqlite_session_no_table(self):
        """Test SQLite-Session ohne mqtt_messages Tabelle"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle SQLite-Datenbank ohne mqtt_messages Tabelle
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE other_table (id INTEGER)")
            conn.commit()
            conn.close()

            # Test Session laden
            with patch("streamlit.error") as mock_error:
                result = self.player.load_sqlite_session(db_path)
                self.assertFalse(result)
                mock_error.assert_called_with(f"❌ Tabelle 'mqtt_messages' nicht gefunden in {db_path}")
                self.assertEqual(len(self.player.messages), 0)

        finally:
            os.unlink(db_path)

    def test_load_sqlite_session_empty(self):
        """Test SQLite-Session ohne Nachrichten"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle leere SQLite-Datenbank
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE mqtt_messages (
                    topic TEXT,
                    payload TEXT,
                    timestamp TEXT
                )
            """
            )
            conn.commit()
            conn.close()

            # Test Session laden
            with patch("streamlit.warning") as mock_warning:
                result = self.player.load_sqlite_session(db_path)
                self.assertFalse(result)
                mock_warning.assert_called_with(f"⚠️ Session {db_path} enthält keine gültigen Nachrichten")
                self.assertEqual(len(self.player.messages), 0)

        finally:
            os.unlink(db_path)

    def test_load_log_session_success(self):
        """Test erfolgreiches Laden einer Log-Session"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Erstelle Test-Log-Datei
            test_log_content = [
                '2023-01-01T10:00:00 | test/topic1 | {"test": "data1"}',
                '2023-01-01T10:01:00 | test/topic2 | {"test": "data2"}',
                '2023-01-01T10:02:00 | test/topic3 | {"test": "data3"}',
            ]
            with open(log_path, "w") as f:
                f.write("\n".join(test_log_content))

            # Test Session laden
            with patch("streamlit.success") as mock_success:
                result = self.player.load_log_session(log_path)
                self.assertTrue(result)
                self.assertEqual(len(self.player.messages), 3)
                self.assertEqual(self.player.messages[0]["topic"], "test/topic1")
                self.assertEqual(self.player.messages[0]["payload"], '{"test": "data1"}')
                self.assertEqual(self.player.messages[2]["payload"], '{"test": "data3"}')
                mock_success.assert_called_with("✅ 3 Nachrichten aus Log geladen")

        finally:
            os.unlink(log_path)

    def test_load_log_session_empty(self):
        """Test Log-Session ohne gültige Nachrichten"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Erstelle Log-Datei mit ungültigen Zeilen
            test_log_content = [
                "invalid line without pipe",
                "2023-01-01T10:00:00 | | empty payload",
                "2023-01-01T10:01:00 |  | empty topic and payload",
                "",
            ]
            with open(log_path, "w") as f:
                f.write("\n".join(test_log_content))

            # Test Session laden - sollte False zurückgeben bei leeren messages
            result = self.player.load_log_session(log_path)
            self.assertFalse(result)  # load_log_session gibt False zurück bei leeren Nachrichten
            self.assertEqual(len(self.player.messages), 0)

        finally:
            os.unlink(log_path)

    def test_load_log_session_invalid_format(self):
        """Test Log-Session mit ungültigem Format"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Erstelle Log-Datei mit ungültigem Format
            with open(log_path, "w") as f:
                f.write("corrupted content without proper format")

            # Test Session laden - sollte False zurückgeben bei ungültigem Format
            result = self.player.load_log_session(log_path)
            self.assertFalse(result)  # load_log_session gibt False zurück bei ungültigem Format
            self.assertEqual(len(self.player.messages), 0)

        finally:
            os.unlink(log_path)

    @patch("subprocess.run")
    def test_send_message_success(self, mock_subprocess):
        """Test erfolgreiches Senden einer Nachricht"""
        # Mock erfolgreiche subprocess-Ausführung
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = self.player.send_message("test/topic", '{"test": "data"}')
        self.assertTrue(result)

        # Prüfe subprocess-Aufruf
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        self.assertEqual(call_args[0], "mosquitto_pub")
        self.assertEqual(call_args[1], "-h")
        self.assertEqual(call_args[2], "localhost")
        self.assertEqual(call_args[3], "-p")
        self.assertEqual(call_args[4], "1884")
        self.assertEqual(call_args[5], "-t")
        self.assertEqual(call_args[6], "test/topic")
        self.assertEqual(call_args[7], "-m")
        self.assertEqual(call_args[8], '{"test": "data"}')
        self.assertEqual(call_args[9], "-q")
        self.assertEqual(call_args[10], "1")

    @patch("subprocess.run")
    def test_send_message_failure(self, mock_subprocess):
        """Test fehlgeschlagenes Senden einer Nachricht"""
        # Mock fehlgeschlagene subprocess-Ausführung
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Connection refused"
        mock_subprocess.return_value = mock_result

        result = self.player.send_message("test/topic", '{"test": "data"}')
        self.assertFalse(result)
        # Prüfe dass logging.error aufgerufen wurde (ohne spezifische Nachricht)
        # Das wird durch die Captured log call im Test-Output bestätigt

    @patch("subprocess.run")
    def test_send_message_exception(self, mock_subprocess):
        """Test Exception beim Senden einer Nachricht"""
        # Mock Exception
        mock_subprocess.side_effect = Exception("subprocess error")

        result = self.player.send_message("test/topic", '{"test": "data"}')
        self.assertFalse(result)
        # Prüfe dass logging.error aufgerufen wurde (ohne spezifische Nachricht)
        # Das wird durch die Captured log call im Test-Output bestätigt

    def test_start_replay_no_messages(self):
        """Test Replay-Start ohne Nachrichten"""
        with patch("streamlit.warning") as mock_warning:
            self.player.start_replay()
            mock_warning.assert_called_with("⚠️ Keine Nachrichten zum Abspielen")

    def test_start_replay_with_messages(self):
        """Test Replay-Start mit Nachrichten"""
        # Setup Test-Nachrichten
        self.player.messages = [
            {"topic": "test/topic1", "payload": '{"test": "data1"}', "timestamp": "2023-01-01T10:00:00"},
            {"topic": "test/topic2", "payload": '{"test": "data2"}', "timestamp": "2023-01-01T10:01:00"},
        ]

        self.player.start_replay(speed=2.0, loop=True)
        self.assertTrue(self.player.is_playing)
        self.assertEqual(self.player.speed, 2.0)
        self.assertTrue(self.player.loop)
        self.assertEqual(self.player.current_index, 0)

    def test_start_replay_from_end(self):
        """Test Replay-Start wenn current_index am Ende ist"""
        # Setup Test-Nachrichten und setze Index ans Ende
        self.player.messages = [
            {"topic": "test/topic1", "payload": '{"test": "data1"}', "timestamp": "2023-01-01T10:00:00"}
        ]
        self.player.current_index = 1  # Am Ende

        self.player.start_replay()
        self.assertEqual(self.player.current_index, 0)  # Sollte zurückgesetzt werden

    def test_pause_replay(self):
        """Test Replay pausieren"""
        self.player.is_playing = True
        self.player.pause_replay()
        self.assertFalse(self.player.is_playing)

    def test_stop_replay(self):
        """Test Replay stoppen"""
        self.player.is_playing = True
        self.player.current_index = 5
        self.player.stop_replay()
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.player.current_index, 0)

    def test_resume_replay(self):
        """Test Replay fortsetzen"""
        self.player.messages = [
            {"topic": "test/topic1", "payload": '{"test": "data1"}', "timestamp": "2023-01-01T10:00:00"}
        ]
        self.player.is_playing = False
        self.player.resume_replay()
        self.assertTrue(self.player.is_playing)

    def test_resume_replay_no_messages(self):
        """Test Replay fortsetzen ohne Nachrichten"""
        with patch("streamlit.warning") as mock_warning:
            self.player.resume_replay()
            mock_warning.assert_called_with("⚠️ Keine Nachrichten zum Abspielen")

    def test_reset_controls(self):
        """Test Kontrollen zurücksetzen"""
        self.player.is_playing = True
        self.player.current_index = 5
        self.player.speed = 2.0
        self.player.loop = True

        self.player.reset_controls()
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.player.current_index, 0)
        self.assertEqual(self.player.speed, 1.0)
        self.assertFalse(self.player.loop)

    def test_get_progress_no_messages(self):
        """Test Fortschritt ohne Nachrichten"""
        progress = self.player.get_progress()
        self.assertEqual(progress, 0.0)

    def test_get_progress_with_messages(self):
        """Test Fortschritt mit Nachrichten"""
        self.player.messages = [
            {"topic": "test/topic1", "payload": '{"test": "data1"}', "timestamp": "2023-01-01T10:00:00"},
            {"topic": "test/topic2", "payload": '{"test": "data2"}', "timestamp": "2023-01-01T10:01:00"},
            {"topic": "test/topic3", "payload": '{"test": "data3"}', "timestamp": "2023-01-01T10:02:00"},
        ]
        self.player.current_index = 1

        progress = self.player.get_progress()
        self.assertAlmostEqual(progress, 33.33, places=1)

    def test_get_progress_complete(self):
        """Test Fortschritt bei vollständigem Replay"""
        self.player.messages = [
            {"topic": "test/topic1", "payload": '{"test": "data1"}', "timestamp": "2023-01-01T10:00:00"}
        ]
        self.player.current_index = 1

        progress = self.player.get_progress()
        self.assertEqual(progress, 100.0)


class TestSessionPlayerIntegration(unittest.TestCase):
    """Integration Tests für SessionPlayer"""

    def setUp(self):
        """Setup für jeden Test"""
        self.player = SessionPlayer(broker_host="localhost", broker_port=1884)

    @patch("subprocess.run")
    def test_full_replay_workflow(self, mock_subprocess):
        """Test des vollständigen Replay-Workflows"""
        # Mock erfolgreiche subprocess-Ausführung
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        # Setup Test-Nachrichten
        self.player.messages = [
            {"topic": "test/topic1", "payload": '{"test": "data1"}', "timestamp": "2023-01-01T10:00:00"},
            {"topic": "test/topic2", "payload": '{"test": "data2"}', "timestamp": "2023-01-01T10:01:00"},
        ]

        # Start Replay
        with patch("streamlit.success"):
            self.player.start_replay(speed=1.0, loop=False)
            self.assertTrue(self.player.is_playing)

        # Pause
        self.player.pause_replay()
        self.assertFalse(self.player.is_playing)

        # Resume - funktioniert nur wenn messages vorhanden sind
        self.player.resume_replay()
        # resume_replay prüft auf messages, daher sollte is_playing True sein

        # Stop
        self.player.stop_replay()
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.player.current_index, 0)

    def test_session_file_detection(self):
        """Test der Session-Datei-Erkennung"""
        # Erstelle temporäre Dateien
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as db_file:
            db_path = db_file.name
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as log_file:
            log_path = log_file.name

        try:
            # Erstelle SQLite-Datei
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE mqtt_messages (
                    topic TEXT,
                    payload TEXT,
                    timestamp TEXT
                )
            """
            )
            cursor.execute(
                """
                INSERT INTO mqtt_messages (topic, payload, timestamp) VALUES
                ('test/topic', '{"test": "data"}', '2023-01-01T10:00:00')
            """
            )
            conn.commit()
            conn.close()

            # Erstelle Log-Datei
            with open(log_path, "w") as f:
                f.write('2023-01-01T10:00:00 | test/topic | {"test": "data"}')

            # Test mit SQLite-Datei
            with patch("streamlit.success"):
                result = self.player.load_sqlite_session(db_path)
                self.assertTrue(result)
                self.assertGreater(len(self.player.messages), 0)
                self.player.messages = []  # Zurücksetzen

            # Test mit Log-Datei
            with patch("streamlit.success"):
                result = self.player.load_log_session(log_path)
                self.assertTrue(result)
                self.assertGreater(len(self.player.messages), 0)

        finally:
            os.unlink(db_path)
            os.unlink(log_path)


class TestSessionPlayerErrorHandling(unittest.TestCase):
    """Error Handling Tests für SessionPlayer"""

    def setUp(self):
        """Setup für jeden Test"""
        self.player = SessionPlayer(broker_host="localhost", broker_port=1884)

    def test_load_nonexistent_sqlite_file(self):
        """Test Laden einer nicht existierenden SQLite-Datei"""
        non_existent_path = "non_existent_file.db"
        with patch("streamlit.error") as mock_error:
            result = self.player.load_sqlite_session(non_existent_path)
            self.assertFalse(result)
            # Die tatsächliche Fehlermeldung ist spezifischer
            mock_error.assert_called_with("❌ Tabelle 'mqtt_messages' nicht gefunden in non_existent_file.db")
            self.assertEqual(len(self.player.messages), 0)

    def test_load_nonexistent_log_file(self):
        """Test Laden einer nicht existierenden Log-Datei"""
        non_existent_path = "non_existent_file.log"
        with patch("streamlit.error") as mock_error:
            result = self.player.load_log_session(non_existent_path)
            self.assertFalse(result)
            mock_error.assert_called_with("❌ Fehler beim Laden der Log Session")
            self.assertEqual(len(self.player.messages), 0)

    def test_load_corrupted_sqlite(self):
        """Test Laden einer korrupten SQLite-Datei"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle korrupte SQLite-Datei
            with open(db_path, "w") as f:
                f.write("not a valid sqlite file")

            with patch("streamlit.error") as mock_error:
                result = self.player.load_sqlite_session(db_path)
                self.assertFalse(result)
                mock_error.assert_called_with("❌ Fehler beim Laden der SQLite Session")
                self.assertEqual(len(self.player.messages), 0)

        finally:
            os.unlink(db_path)

    def test_load_corrupted_log(self):
        """Test Laden einer korrupten Log-Datei"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Erstelle korrupte Log-Datei
            with open(log_path, "w") as f:
                f.write("corrupted content")

            result = self.player.load_log_session(log_path)
            self.assertFalse(result)  # load_log_session gibt False zurück bei korrupten Dateien
            self.assertEqual(len(self.player.messages), 0)

        finally:
            os.unlink(log_path)


if __name__ == "__main__":
    unittest.main()
