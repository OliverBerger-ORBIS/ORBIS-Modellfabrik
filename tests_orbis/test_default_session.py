#!/usr/bin/env python3
"""
Test für Default-Session-Funktionalität
Prüft ob Default-Session korrekt geladen wird
"""

import sys
import unittest
import os
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDefaultSession(unittest.TestCase):
    """Test Default-Session-Funktionalität"""

    def test_default_session_exists(self):
        """Test: Default-Session-Dateien existieren"""
        try:
            default_db = project_root / "mqtt-data/sessions/default_test_session.db"
            default_log = project_root / "mqtt-data/sessions/default_test_session.log"
            
            self.assertTrue(default_db.exists(), f"Default DB nicht gefunden: {default_db}")
            self.assertTrue(default_log.exists(), f"Default Log nicht gefunden: {default_log}")
            
            # Check file sizes
            db_size = default_db.stat().st_size
            log_size = default_log.stat().st_size
            
            self.assertGreater(db_size, 0, "Default DB ist leer")
            self.assertGreater(log_size, 0, "Default Log ist leer")
            
            print(f"✅ Default-Session existiert: DB={db_size} bytes, Log={log_size} bytes")
            
        except Exception as e:
            self.fail(f"❌ Default-Session Test failed: {e}")

    def test_default_session_loading(self):
        """Test: Default-Session kann geladen werden"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard
            
            default_db = project_root / "mqtt-data/sessions/default_test_session.db"
            
            if not default_db.exists():
                self.skipTest("Default-Session nicht verfügbar")
            
            # Test dashboard with default session
            dashboard = APSDashboard(str(default_db))
            
            # Test connect
            result = dashboard.connect()
            self.assertTrue(result, "Dashboard sollte mit Default-Session verbinden können")
            
            # Test load_data
            df = dashboard.load_data()
            self.assertIsNotNone(df, "load_data sollte DataFrame zurückgeben")
            self.assertFalse(df.empty, "Default-Session sollte Daten enthalten")
            
            print(f"✅ Default-Session geladen: {len(df)} Nachrichten")
            
        except Exception as e:
            self.fail(f"❌ Default-Session Loading failed: {e}")

    def test_session_selection_logic(self):
        """Test: Session-Auswahl-Logik funktioniert"""
        try:
            # Create temporary sessions directory
            with tempfile.TemporaryDirectory() as temp_dir:
                sessions_dir = Path(temp_dir) / "sessions"
                sessions_dir.mkdir()
                
                # Create mock session files
                mock_session1 = sessions_dir / "aps_persistent_traffic_test1.db"
                mock_session2 = sessions_dir / "aps_persistent_traffic_test2.db"
                default_session = sessions_dir / "default_test_session.db"
                
                # Create empty files
                mock_session1.touch()
                mock_session2.touch()
                default_session.touch()
                
                # Test session file discovery
                db_files = list(sessions_dir.glob("aps_persistent_traffic_*.db"))
                self.assertEqual(len(db_files), 2, "Sollte 2 normale Sessions finden")
                
                # Test default session addition
                if default_session.exists():
                    db_files.insert(0, default_session)
                
                self.assertEqual(len(db_files), 3, "Sollte 3 Sessions haben (inkl. Default)")
                self.assertEqual(db_files[0], default_session, "Default sollte an erster Stelle sein")
                
                print("✅ Session-Auswahl-Logik funktioniert")
                
        except Exception as e:
            self.fail(f"❌ Session-Auswahl-Logik failed: {e}")

    def test_dashboard_without_session(self):
        """Test: Dashboard funktioniert ohne Session"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard
            
            # Test dashboard without database
            dashboard = APSDashboard(None)
            
            # Test connect
            result = dashboard.connect()
            self.assertTrue(result, "Dashboard sollte ohne Session verbinden können")
            
            # Test load_data
            df = dashboard.load_data()
            self.assertIsNotNone(df, "load_data sollte DataFrame zurückgeben")
            self.assertTrue(df.empty, "DataFrame sollte leer sein ohne Session")
            
            print("✅ Dashboard ohne Session funktioniert")
            
        except Exception as e:
            self.fail(f"❌ Dashboard ohne Session failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing Default Session...")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 50)
    print("🎯 Default Session test completed!")
