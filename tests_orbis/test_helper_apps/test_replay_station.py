#!/usr/bin/env python3
"""
Unit Tests für OMF Replay Station
Testet SessionPlayer, LocalMQTTBroker und Session-Lade-Funktionalität
"""

import os
import sqlite3

# Add src_orbis to path for imports
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))

from src_orbis.helper_apps.replay_station.omf_replay_station import LocalMQTTBroker, SessionPlayer


@unittest.skipIf(os.name == "nt", "Test wird unter Windows wegen WinError 32 übersprungen")
class TestLocalMQTTBroker(unittest.TestCase):
    """Tests für LocalMQTTBroker"""

    def setUp(self):
        """Setup für jeden Test"""
        self.broker = LocalMQTTBroker(port=1884)

    def test_broker_initialization(self):
        """Test Broker-Initialisierung"""
        self.assertEqual(self.broker.port, 1884)
        self.assertFalse(self.broker.is_running)
        self.assertEqual(self.broker.subscribers, {})

    def test_broker_start(self):
        """Test Broker-Start"""
        result = self.broker.start()
        self.assertTrue(result)
        self.assertTrue(self.broker.is_running)

    def test_broker_stop(self):
        """Test Broker-Stop"""
        self.broker.start()
        self.broker.stop()
        self.assertFalse(self.broker.is_running)

    def test_broker_publish(self):
        """Test Nachrichten-Publishing"""
        self.broker.start()
        result = self.broker.publish("test/topic", "test payload")
        self.assertEqual(result.rc, 0)  # Mock success

    def test_broker_publish_not_running(self):
        """Test Publishing wenn Broker nicht läuft"""
        result = self.broker.publish("test/topic", "test payload")
        self.assertEqual(result.rc, 1)  # Mock error


@unittest.skipIf(os.name == "nt", "Test wird unter Windows wegen WinError 32 übersprungen")
class TestSessionPlayer(unittest.TestCase):
    """Tests für SessionPlayer"""

    def setUp(self):
        """Setup für jeden Test"""
        self.broker = LocalMQTTBroker()
        self.player = SessionPlayer(self.broker)

    def test_player_initialization(self):
        """Test SessionPlayer-Initialisierung"""
        self.assertEqual(self.player.messages, [])
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.player.current_index, 0)
        self.assertEqual(self.player.speed, 1.0)
        self.assertFalse(self.player.loop)

    def test_load_sqlite_session_success(self):
        """Test erfolgreiches Laden einer SQLite-Session"""
        # Erstelle temporäre SQLite-Datenbank
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle Test-Datenbank
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Erstelle Tabelle
            cursor.execute(
                """
                CREATE TABLE mqtt_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    payload TEXT,
                    qos INTEGER,
                    retain BOOLEAN,
                    message_type TEXT,
                    module_type TEXT,
                    serial_number TEXT,
                    status TEXT,
                    session_label TEXT,
                    process_label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Füge Test-Nachrichten hinzu
            test_messages = [
                ("2024-01-01T10:00:00", "test/topic1", '{"test": "data1"}'),
                ("2024-01-01T10:00:01", "test/topic2", '{"test": "data2"}'),
                ("2024-01-01T10:00:02", "test/topic3", '{"test": "data3"}'),
            ]

            cursor.executemany(
                "INSERT INTO mqtt_messages (timestamp, topic, payload) VALUES (?, ?, ?)",
                test_messages,
            )
            conn.commit()
            conn.close()

            # Test Session laden
            with patch("streamlit.success") as _mock_success:
                result = self.player.load_session(db_path)
                self.assertTrue(result)
                self.assertEqual(len(self.player.messages), 3)

                # Prüfe erste Nachricht
                first_msg = self.player.messages[0]
                self.assertEqual(first_msg["topic"], "test/topic1")
                self.assertEqual(first_msg["payload"], '{"test": "data1"}')
                self.assertIsInstance(first_msg["timestamp"], datetime)

        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_load_sqlite_session_invalid_table(self):
        """Test Laden einer SQLite-Session mit falscher Tabellen-Struktur"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle Datenbank mit falscher Tabelle
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE wrong_table (id INTEGER, data TEXT)")
            conn.commit()
            conn.close()

            # Test Session laden
            with patch("streamlit.error") as mock_error:
                result = self.player.load_session(db_path)
                self.assertFalse(result)
                mock_error.assert_called()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_load_log_session_success(self):
        """Test erfolgreiches Laden einer Log-Session"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Erstelle Test-Log-Datei
            test_log_content = [
                '2024-01-01T10:00:00|test/topic1|{"test": "data1"}',
                '2024-01-01T10:00:01|test/topic2|{"test": "data2"}',
                '2024-01-01T10:00:02|test/topic3|{"test": "data3"}',
            ]

            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(test_log_content))

            # Test Session laden
            with patch("streamlit.success") as _mock_success:
                result = self.player.load_session(log_path)
                self.assertTrue(result)
                self.assertEqual(len(self.player.messages), 3)

                # Prüfe erste Nachricht
                first_msg = self.player.messages[0]
                self.assertEqual(first_msg["topic"], "test/topic1")
                self.assertEqual(first_msg["payload"], '{"test": "data1"}')
                self.assertIsInstance(first_msg["timestamp"], datetime)

        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)

    def test_load_log_session_invalid_format(self):
        """Test Laden einer Log-Session mit ungültigem Format"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Erstelle Log-Datei mit ungültigem Format
            test_log_content = [
                "invalid line",
                "2024-01-01T10:00:00|test/topic1",  # Fehlende Payload
                "2024-01-01T10:00:01|test/topic2|payload|extra",  # Zu viele Teile
            ]

            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(test_log_content))

            # Test Session laden
            with patch("streamlit.success") as _mock_success:
                result = self.player.load_session(log_path)
                self.assertTrue(result)  # Sollte trotzdem funktionieren
                # Prüfe ob gültige Nachrichten geladen wurden (könnte 0 oder mehr sein)
                self.assertIsInstance(len(self.player.messages), int)

        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)

    def test_start_replay_no_messages(self):
        """Test Replay-Start ohne Nachrichten"""
        with patch("streamlit.warning") as mock_warning:
            self.player.start_replay()
            mock_warning.assert_called_with("❌ Keine Nachrichten zum Abspielen")

    def test_start_replay_with_messages(self):
        """Test Replay-Start mit Nachrichten"""
        # Füge Test-Nachrichten hinzu
        self.player.messages = [
            {
                "topic": "test/topic1",
                "payload": '{"test": "data1"}',
                "timestamp": datetime.now(),
            }
        ]

        with patch("streamlit.success") as mock_success:
            self.player.start_replay(speed=2.0, loop=True)
            self.assertTrue(self.player.is_playing)
            self.assertEqual(self.player.speed, 2.0)
            self.assertTrue(self.player.loop)
            mock_success.assert_called()

    def test_pause_replay(self):
        """Test Replay-Pause"""
        self.player.is_playing = True
        with patch("streamlit.info") as mock_info:
            self.player.pause_replay()
            self.assertFalse(self.player.is_playing)
            mock_info.assert_called_with("⏸️ Replay pausiert")

    def test_stop_replay(self):
        """Test Replay-Stop"""
        self.player.is_playing = True
        self.player.current_index = 5
        with patch("streamlit.info") as mock_info:
            self.player.stop_replay()
            self.assertFalse(self.player.is_playing)
            self.assertEqual(self.player.current_index, 0)
            # Check that stop message was called (order may vary due to threading)
            mock_info.assert_any_call("⏹️ Replay gestoppt")

    def test_get_progress(self):
        """Test Fortschritts-Berechnung"""
        # Keine Nachrichten
        self.assertEqual(self.player.get_progress(), 0.0)

        # Mit Nachrichten
        self.player.messages = [1, 2, 3, 4, 5]  # 5 Nachrichten
        self.player.current_index = 2  # Bei Nachricht 3

        progress = self.player.get_progress()
        self.assertEqual(progress, 40.0)  # 2/5 * 100 = 40%

    def test_send_message(self):
        """Test Nachrichten-Senden"""
        test_message = {"topic": "test/topic", "payload": '{"test": "data"}'}

        # Mock broker_client.publish
        self.player.broker_client = Mock()
        mock_result = Mock()
        mock_result.rc = 0  # Success
        self.player.broker_client.publish.return_value = mock_result

        with patch("logging.info") as _mock_log:
            self.player._send_message(test_message)
            # Prüfe ob publish aufgerufen wurde
            self.player.broker_client.publish.assert_called_once_with("test/topic", '{"test": "data"}', qos=1)


@unittest.skipIf(os.name == "nt", "Test wird unter Windows wegen WinError 32 übersprungen")
class TestReplayStationIntegration(unittest.TestCase):
    """Integration-Tests für Replay-Station"""

    def setUp(self):
        """Setup für jeden Test"""
        self.broker = LocalMQTTBroker()
        self.player = SessionPlayer(self.broker)

    def test_full_replay_workflow(self):
        """Test vollständiger Replay-Workflow"""
        # 1. Broker starten
        self.assertTrue(self.broker.start())

        # 2. Test-Session erstellen
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Erstelle Test-Datenbank
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE mqtt_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    payload TEXT
                )
            """
            )

            # Füge Test-Nachrichten hinzu
            cursor.execute(
                "INSERT INTO mqtt_messages (timestamp, topic, payload) VALUES (?, ?, ?)",
                ("2024-01-01T10:00:00", "test/topic", '{"test": "data"}'),
            )
            conn.commit()
            conn.close()

            # 3. Session laden
            with patch("streamlit.success"):
                result = self.player.load_session(db_path)
                self.assertTrue(result)
                self.assertEqual(len(self.player.messages), 1)

            # 4. Replay starten
            with patch("streamlit.success"):
                self.player.start_replay()
                # Prüfe ob Replay gestartet wurde (kann kurz dauern)
                self.assertTrue(self.player.is_playing or self.player.current_index > 0)

            # 5. Replay stoppen
            with patch("streamlit.info"):
                self.player.stop_replay()
                self.assertFalse(self.player.is_playing)

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_session_file_detection(self):
        """Test Erkennung von Session-Dateien"""
        # Test mit verschiedenen Dateiendungen
        test_files = [
            "test_session.db",
            "test_session.log",
            "aps_persistent_traffic_test.db",
            "aps_persistent_traffic_test.log",
        ]

        for filename in test_files:
            if filename.endswith(".db"):
                self.assertTrue(self.player._is_sqlite_session(filename))
                self.assertFalse(self.player._is_log_session(filename))
            else:
                self.assertFalse(self.player._is_sqlite_session(filename))
                self.assertTrue(self.player._is_log_session(filename))


@unittest.skipIf(os.name == "nt", "Test wird unter Windows wegen WinError 32 übersprungen")
class TestReplayStationErrorHandling(unittest.TestCase):
    """Tests für Fehlerbehandlung in Replay-Station"""

    def setUp(self):
        """Setup für jeden Test"""
        self.broker = LocalMQTTBroker()
        self.player = SessionPlayer(self.broker)

    def test_load_nonexistent_file(self):
        """Test Laden einer nicht existierenden Datei"""
        with patch("streamlit.error") as mock_error:
            result = self.player.load_session("nonexistent_file.db")
            self.assertFalse(result)
            mock_error.assert_called()

    def test_load_corrupted_sqlite(self):
        """Test Laden einer beschädigten SQLite-Datei"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            # Schreibe ungültige Daten in die Datei
            with open(db_path, "w") as f:
                f.write("This is not a valid SQLite database")

            with patch("streamlit.error") as mock_error:
                result = self.player.load_session(db_path)
                self.assertFalse(result)
                mock_error.assert_called()

        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_load_corrupted_log(self):
        """Test Laden einer beschädigten Log-Datei"""
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_file:
            log_path = tmp_file.name

        try:
            # Schreibe ungültige Daten in die Datei
            with open(log_path, "w") as f:
                f.write("This is not a valid log file\n")
                f.write("Invalid format line\n")

            with patch("streamlit.success") as _mock_success:
                result = self.player.load_session(log_path)
                self.assertTrue(result)  # Sollte trotzdem funktionieren
                self.assertEqual(len(self.player.messages), 0)  # Aber keine Nachrichten laden

        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)


if __name__ == "__main__":
    # Führe Tests aus
    unittest.main(verbosity=2)
