#!/usr/bin/env python3
"""
Test für Dashboard Runtime-Fehler
Prüft auch Runtime-Fehler wie Datenbankverbindungen
"""

import sys
import unittest
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDashboardRuntime(unittest.TestCase):
    """Test Dashboard Runtime-Fehler"""

    def test_dashboard_without_database(self):
        """Test: Dashboard kann ohne Datenbank gestartet werden"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            # Test with None database file
            dashboard = APSDashboard(None)

            # Test connect method
            result = dashboard.connect()
            self.assertTrue(result, "Dashboard sollte ohne Datenbank verbinden können")

            # Test load_data method
            df = dashboard.load_data()
            self.assertIsNotNone(df, "load_data sollte DataFrame zurückgeben")
            self.assertTrue(df.empty, "DataFrame sollte leer sein ohne Datenbank")

            print("✅ Dashboard ohne Datenbank: OK")

        except Exception as e:
            self.fail(f"❌ Dashboard ohne Datenbank failed: {e}")

    def test_dashboard_with_invalid_database(self):
        """Test: Dashboard mit ungültiger Datenbank"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            # Test with non-existent database file
            dashboard = APSDashboard("/path/to/nonexistent.db")

            # Test connect method should handle gracefully
            result = dashboard.connect()
            self.assertFalse(
                result, "Dashboard sollte bei ungültiger DB False zurückgeben"
            )

            print("✅ Dashboard mit ungültiger DB: OK")

        except Exception as e:
            self.fail(f"❌ Dashboard mit ungültiger DB failed: {e}")

    def test_dashboard_with_valid_database(self):
        """Test: Dashboard mit gültiger Datenbank"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            # Create a temporary database file
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
                tmp_db_path = tmp_file.name

            try:
                # Test with valid database file
                dashboard = APSDashboard(tmp_db_path)

                # Test connect method
                result = dashboard.connect()
                self.assertTrue(
                    result, "Dashboard sollte mit gültiger DB verbinden können"
                )

                # Test load_data method
                df = dashboard.load_data()
                self.assertIsNotNone(df, "load_data sollte DataFrame zurückgeben")

                print("✅ Dashboard mit gültiger DB: OK")

            finally:
                # Clean up
                if os.path.exists(tmp_db_path):
                    os.unlink(tmp_db_path)

        except Exception as e:
            self.fail(f"❌ Dashboard mit gültiger DB failed: {e}")

    def test_session_recorder_methods(self):
        """Test: Session-Recorder Methoden existieren"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            dashboard = APSDashboard(None)

            # Check if methods exist
            self.assertTrue(
                hasattr(dashboard, "start_session_recorder"),
                "start_session_recorder Methode fehlt",
            )
            self.assertTrue(
                hasattr(dashboard, "stop_session_recorder"),
                "stop_session_recorder Methode fehlt",
            )

            print("✅ Session-Recorder Methoden: OK")

        except Exception as e:
            self.fail(f"❌ Session-Recorder Methoden failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing Dashboard Runtime...")
    print("=" * 50)

    # Run tests
    unittest.main(verbosity=2, exit=False)

    print("=" * 50)
    print("🎯 Runtime test completed!")
