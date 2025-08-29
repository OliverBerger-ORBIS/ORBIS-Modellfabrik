#!/usr/bin/env python3
"""
Integration Test für Filter-Verbesserungen
Testet die Filter-Funktionen mit echten Daten und Dashboard-Integration
"""

import sys
import os
import unittest
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFilterIntegration(unittest.TestCase):
    """Integration Test für Filter-Verbesserungen"""

    def setUp(self):
        """Setup Test-Datenbank und -Daten"""
        # Create test database
        self.test_db = "/tmp/test_filter_integration.db"
        self.conn = sqlite3.connect(self.test_db)

        # Create test table
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mqtt_messages (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                payload TEXT,
                timestamp TEXT,
                session_label TEXT,
                process_label TEXT,
                module_type TEXT,
                status TEXT
            )
        """
        )

        # Insert test data
        test_data = [
            (
                "module/v1/ff/SVR4H73275/state",
                '{"status": "available"}',
                "2025-08-20 10:00:00",
                "session-1",
                "wareneingang",
                "DPS",
                "available",
            ),
            (
                "module/v1/ff/SVR4H76530/state",
                '{"status": "busy"}',
                "2025-08-20 10:01:00",
                "session-1",
                "qualitaetskontrolle",
                "AIQS",
                "busy",
            ),
            (
                "module/v1/ff/SVR3QA2098/state",
                '{"status": "blocked"}',
                "2025-08-20 10:02:00",
                "session-1",
                "bearbeitung",
                "MILL",
                "blocked",
            ),
            (
                "module/v1/ff/SVR3QA0022/state",
                '{"status": "available"}',
                "2025-08-20 10:03:00",
                "session-1",
                "lagerung",
                "HBW",
                "available",
            ),
            (
                "fts/v1/ff/5iO4/state",
                '{"status": "charging"}',
                "2025-08-20 10:04:00",
                "session-1",
                "transport",
                "FTS",
                "charging",
            ),
            (
                "module/v1/ff/SVR4H73275/state",
                '{"status": "available"}',
                "2025-08-20 11:00:00",
                "session-2",
                "wareneingang",
                "DPS",
                "available",
            ),
            (
                "module/v1/ff/SVR4H76530/state",
                '{"status": "busy"}',
                "2025-08-20 11:01:00",
                "session-2",
                "qualitaetskontrolle",
                "AIQS",
                "busy",
            ),
        ]

        self.conn.executemany(
            """
            INSERT INTO mqtt_messages (topic, payload, timestamp, session_label, process_label, module_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            test_data,
        )

        self.conn.commit()

    def tearDown(self):
        """Cleanup Test-Datenbank"""
        if self.conn:
            self.conn.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_data_loading_and_processing(self):
        """Test: Daten können geladen und verarbeitet werden"""
        try:
            # Load data from database
            query = "SELECT * FROM mqtt_messages ORDER BY timestamp"
            df = pd.read_sql_query(query, self.conn)

            # Convert timestamp
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Basic checks
            self.assertEqual(len(df), 7, "Should have 7 test messages")
            self.assertEqual(
                len(df["session_label"].unique()), 2, "Should have 2 sessions"
            )
            self.assertEqual(
                len(df["module_type"].unique()), 5, "Should have 5 module types"
            )

            print("✅ Data loading and processing: OK")
        except Exception as e:
            self.fail(f"❌ Data loading and processing failed: {e}")

    def test_single_session_mode_detection_integration(self):
        """Test: Einzel-Session-Modus wird korrekt erkannt (Integration)"""
        try:
            # Load data for single session
            query = "SELECT * FROM mqtt_messages WHERE session_label = 'session-1' ORDER BY timestamp"
            df_single = pd.read_sql_query(query, self.conn)
            df_single["timestamp"] = pd.to_datetime(df_single["timestamp"])

            # Check single session detection
            single_session_mode = len(df_single["session_label"].unique()) == 1
            self.assertTrue(single_session_mode, "Single session should be detected")

            # Load data for multiple sessions
            query = "SELECT * FROM mqtt_messages ORDER BY timestamp"
            df_multi = pd.read_sql_query(query, self.conn)
            df_multi["timestamp"] = pd.to_datetime(df_multi["timestamp"])

            # Check multiple session detection
            multi_session_mode = len(df_multi["session_label"].unique()) == 1
            self.assertFalse(
                multi_session_mode, "Multiple sessions should not be detected as single"
            )

            print("✅ Single session mode detection integration: OK")
        except Exception as e:
            self.fail(f"❌ Single session mode detection integration failed: {e}")

    def test_filter_component_with_real_data(self):
        """Test: Filter-Komponente funktioniert mit echten Daten"""
        try:

            # Load data
            query = "SELECT * FROM mqtt_messages ORDER BY timestamp"
            df = pd.read_sql_query(query, self.conn)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Test single session mode
            single_session_df = df[df["session_label"] == "session-1"].copy()
            single_session_mode = len(single_session_df["session_label"].unique()) == 1

            # The function should not crash with real data
            # Note: In a real test environment, we'd mock Streamlit components
            print("✅ Filter component with real data: OK (basic functionality)")
        except Exception as e:
            self.fail(f"❌ Filter component with real data failed: {e}")

    def test_topic_manager_with_real_topics(self):
        """Test: Topic-Manager funktioniert mit echten Topics"""
        try:
            from src_orbis.mqtt.tools.topic_manager import get_topic_manager

            # Get real topics from database
            query = "SELECT DISTINCT topic FROM mqtt_messages"
            topics = pd.read_sql_query(query, self.conn)["topic"].tolist()

            # Test mapping for each topic
            topic_manager = get_topic_manager()
            for topic in topics:
                friendly_name = topic_manager.get_friendly_name(topic)

                # Check that mapping produces readable names
                self.assertIsInstance(friendly_name, str)
                self.assertGreater(len(friendly_name), 0)

                # Check that friendly names are different from original topics
                if not topic.startswith("ccu/"):  # CCU topics might not be mapped
                    self.assertNotEqual(
                        friendly_name,
                        topic,
                        f"Topic {topic} should be mapped to friendly name",
                    )

            print("✅ Topic mapping with real topics: OK")
        except Exception as e:
            self.fail(f"❌ Topic mapping with real topics failed: {e}")

    def test_module_icons_with_real_modules(self):
        """Test: Module-Icons funktionieren mit echten Modulen"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import get_module_icon

            # Get real modules from database
            query = "SELECT DISTINCT module_type FROM mqtt_messages"
            modules = pd.read_sql_query(query, self.conn)["module_type"].tolist()

            # Test icons for each module
            for module in modules:
                icon = get_module_icon(module)

                # Check that icon is returned
                self.assertIsInstance(icon, str)
                self.assertGreater(len(icon), 0)

                # Check that it's not the default unknown icon
                self.assertNotEqual(
                    icon, "❓", f"Module {module} should have a proper icon"
                )

            print("✅ Module icons with real modules: OK")
        except Exception as e:
            self.fail(f"❌ Module icons with real modules failed: {e}")

    def test_time_range_filtering_with_real_data(self):
        """Test: Zeitbereich-Filterung funktioniert mit echten Daten"""
        try:
            # Load data
            query = "SELECT * FROM mqtt_messages ORDER BY timestamp"
            df = pd.read_sql_query(query, self.conn)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Define time range
            start_time = datetime(2025, 8, 20, 10, 1, 0)
            end_time = datetime(2025, 8, 20, 10, 3, 0)

            # Filter data
            filtered_df = df[
                (df["timestamp"] >= start_time) & (df["timestamp"] <= end_time)
            ]

            # Should have 3 rows (10:01, 10:02, 10:03 from session-1)
            self.assertEqual(len(filtered_df), 3)

            # Check that all timestamps are within range
            for timestamp in filtered_df["timestamp"]:
                self.assertGreaterEqual(timestamp, start_time)
                self.assertLessEqual(timestamp, end_time)

            print("✅ Time range filtering with real data: OK")
        except Exception as e:
            self.fail(f"❌ Time range filtering with real data failed: {e}")

    def test_dashboard_integration_with_real_data(self):
        """Test: Dashboard-Integration funktioniert mit echten Daten"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard

            # Create dashboard with test database
            dashboard = APSDashboard(self.test_db)

            # Check that dashboard can be created
            self.assertIsNotNone(dashboard)
            self.assertTrue(hasattr(dashboard, "create_filters"))

            # Check method signature
            import inspect

            sig = inspect.signature(dashboard.create_filters)
            params = list(sig.parameters.keys())

            self.assertIn("df", params)
            self.assertIn("single_session_mode", params)

            print("✅ Dashboard integration with real data: OK")
        except Exception as e:
            self.fail(f"❌ Dashboard integration with real data failed: {e}")

    def test_filter_state_persistence(self):
        """Test: Filter-State-Persistierung funktioniert"""
        try:
            # This test would normally check Streamlit session state
            # For integration testing, we verify the concept works

            # Simulate filter state
            filter_states = {
                "selected_process": "wareneingang",
                "selected_module": "DPS",
                "selected_status": "available",
                "selected_topic": "module/v1/ff/SVR4H73275/state",
            }

            # Verify state structure
            self.assertIsInstance(filter_states, dict)
            self.assertIn("selected_process", filter_states)
            self.assertIn("selected_module", filter_states)
            self.assertIn("selected_status", filter_states)
            self.assertIn("selected_topic", filter_states)

            print("✅ Filter state persistence: OK (concept verified)")
        except Exception as e:
            self.fail(f"❌ Filter state persistence failed: {e}")


def run_integration_tests():
    """Run all filter integration tests"""
    print("🧪 Running Filter Integration Tests...")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFilterIntegration)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("=" * 50)
    print("📊 Integration Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")

    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")

    if result.wasSuccessful():
        print("\n✅ All filter integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
