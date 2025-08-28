#!/usr/bin/env python3
"""
Test für Datenbankstruktur und Daten
Prüft ob Datenbanken die richtige Struktur und Daten haben
"""

import sys
import unittest
import sqlite3
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDatabaseStructure(unittest.TestCase):
    """Test Datenbankstruktur und Daten"""

    def test_default_database_structure(self):
        """Test: Default-Datenbank hat die richtige Struktur"""
        try:
            default_db = project_root / "mqtt-data/sessions/default_test_session.db"

            if not default_db.exists():
                self.skipTest("Default-Datenbank nicht verfügbar")

            # Connect to database
            conn = sqlite3.connect(default_db)
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'"
            )
            table_exists = cursor.fetchone() is not None
            self.assertTrue(table_exists, "Tabelle 'mqtt_messages' fehlt")

            # Check required columns
            cursor.execute("PRAGMA table_info(mqtt_messages)")
            columns = {row[1] for row in cursor.fetchall()}

            required_columns = {
                "timestamp",
                "topic",
                "payload",
                "qos",
                "retain",
                "message_type",
                "module_type",
                "serial_number",
                "status",
                "session_label",
                "process_label",
            }

            missing_columns = required_columns - columns
            self.assertEqual(
                len(missing_columns), 0, f"Fehlende Spalten: {missing_columns}"
            )

            # Check if data exists
            cursor.execute("SELECT COUNT(*) FROM mqtt_messages")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, "Datenbank ist leer")

            # Check sample data
            cursor.execute("SELECT topic, session_label FROM mqtt_messages LIMIT 1")
            sample = cursor.fetchone()
            self.assertIsNotNone(sample, "Keine Beispieldaten gefunden")

            conn.close()
            print(f"✅ Default-Datenbank Struktur: OK ({count} Nachrichten)")

        except Exception as e:
            self.fail(f"❌ Default-Datenbank Struktur failed: {e}")

    def test_database_loading_in_dashboard(self):
        """Test: Dashboard kann Datenbank korrekt laden"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            default_db = project_root / "mqtt-data/sessions/default_test_session.db"

            if not default_db.exists():
                self.skipTest("Default-Datenbank nicht verfügbar")

            # Test dashboard with default database
            dashboard = APSDashboard(str(default_db))

            # Test connect
            result = dashboard.connect()
            self.assertTrue(result, "Dashboard sollte mit Default-DB verbinden können")

            # Test load_data
            df = dashboard.load_data()
            self.assertIsNotNone(df, "load_data sollte DataFrame zurückgeben")
            self.assertFalse(df.empty, "DataFrame sollte nicht leer sein")

            # Check required columns in DataFrame
            required_columns = {
                "timestamp",
                "topic",
                "payload",
                "qos",
                "retain",
                "message_type",
                "module_type",
                "serial_number",
                "status",
                "session_label",
                "process_label",
            }

            missing_columns = required_columns - set(df.columns)
            self.assertEqual(
                len(missing_columns),
                0,
                f"Fehlende Spalten im DataFrame: {missing_columns}",
            )

            # Check if data is loaded
            self.assertGreater(len(df), 0, "DataFrame sollte Daten enthalten")

            print(f"✅ Dashboard Datenbank-Laden: OK ({len(df)} Nachrichten)")

        except Exception as e:
            self.fail(f"❌ Dashboard Datenbank-Laden failed: {e}")

    def test_session_label_extraction(self):
        """Test: Session-Labels werden korrekt extrahiert"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            default_db = project_root / "mqtt-data/sessions/default_test_session.db"

            if not default_db.exists():
                self.skipTest("Default-Datenbank nicht verfügbar")

            # Test dashboard with default database
            dashboard = APSDashboard(str(default_db))
            dashboard.connect()
            df = dashboard.load_data()

            # Check if session_label column has data
            self.assertIn("session_label", df.columns, "session_label Spalte fehlt")
            self.assertFalse(
                df["session_label"].isna().all(), "session_label ist komplett leer"
            )

            # Check unique session labels
            unique_sessions = df["session_label"].unique()
            self.assertGreater(len(unique_sessions), 0, "Keine Session-Labels gefunden")

            print(f"✅ Session-Label Extraktion: OK ({len(unique_sessions)} Sessions)")

        except Exception as e:
            self.fail(f"❌ Session-Label Extraktion failed: {e}")

    def test_topic_extraction(self):
        """Test: Topics werden korrekt extrahiert"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            default_db = project_root / "mqtt-data/sessions/default_test_session.db"

            if not default_db.exists():
                self.skipTest("Default-Datenbank nicht verfügbar")

            # Test dashboard with default database
            dashboard = APSDashboard(str(default_db))
            dashboard.connect()
            df = dashboard.load_data()

            # Check if topic column has data
            self.assertIn("topic", df.columns, "topic Spalte fehlt")
            self.assertFalse(df["topic"].isna().all(), "topic ist komplett leer")

            # Check unique topics
            unique_topics = df["topic"].unique()
            self.assertGreater(len(unique_topics), 0, "Keine Topics gefunden")

            print(f"✅ Topic Extraktion: OK ({len(unique_topics)} Topics)")

        except Exception as e:
            self.fail(f"❌ Topic Extraktion failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing Database Structure...")
    print("=" * 50)

    # Run tests
    unittest.main(verbosity=2, exit=False)

    print("=" * 50)
    print("🎯 Database Structure test completed!")
