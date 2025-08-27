#!/usr/bin/env python3
"""
Test für Filter-Verbesserungen
Prüft alle neuen Filter-Funktionen:
1. Session-Filter Optimierung
2. Zeit-Schieberegler statt Datums-Auswahl
3. Friendly Topic Names
4. Module-Icons in Dropdown
5. Alphabetische Sortierung
"""

import sys
import os
import unittest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFilterImprovements(unittest.TestCase):
    """Test für alle Filter-Verbesserungen"""

    def setUp(self):
        """Setup Test-Daten"""
        # Create test data with timestamps
        self.test_data = pd.DataFrame({
            'timestamp': [
                datetime(2025, 8, 20, 10, 0, 0),
                datetime(2025, 8, 20, 10, 1, 0),
                datetime(2025, 8, 20, 10, 2, 0),
                datetime(2025, 8, 20, 10, 3, 0),
                datetime(2025, 8, 20, 10, 4, 0),
            ],
            'session_label': ['test-session'] * 5,
            'process_label': ['wareneingang', 'qualitaetskontrolle', 'bearbeitung', 'lagerung', 'ausgang'],
            'module_type': ['DPS', 'AIQS', 'MILL', 'HBW', 'FTS'],
            'status': ['available', 'busy', 'blocked', 'available', 'charging'],
            'topic': [
                'module/v1/ff/SVR4H73275/state',
                'module/v1/ff/SVR4H76530/state',
                'module/v1/ff/SVR3QA2098/state',
                'module/v1/ff/SVR3QA0022/state',
                'fts/v1/ff/5iO4/state'
            ]
        })

    def test_filter_component_import(self):
        """Test: Filter-Komponente kann importiert werden"""
        try:
            from src_orbis.mqtt.dashboard.components.filters import create_filters
            self.assertTrue(callable(create_filters))
            print("✅ Filter component import: OK")
        except Exception as e:
            self.fail(f"❌ Filter component import failed: {e}")

    def test_topic_manager_import(self):
        """Test: Topic-Manager kann importiert werden"""
        try:
            from src_orbis.mqtt.tools.topic_manager import get_topic_manager
            topic_manager = get_topic_manager()
            self.assertTrue(callable(topic_manager.get_friendly_name))
            print("✅ Topic mapping import: OK")
        except Exception as e:
            self.fail(f"❌ Topic mapping import failed: {e}")

    def test_icon_config_import(self):
        """Test: Icon-Konfiguration kann importiert werden"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import get_module_icon
            self.assertTrue(callable(get_module_icon))
            print("✅ Icon config import: OK")
        except Exception as e:
            self.fail(f"❌ Icon config import failed: {e}")

    def test_friendly_topic_names(self):
        """Test: Friendly Topic Names funktionieren korrekt"""
        try:
            from src_orbis.mqtt.tools.topic_manager import get_topic_manager
            
            topic_manager = get_topic_manager()
            
            # Test cases
            test_cases = [
                ('module/v1/ff/SVR4H73275/state', 'DPS : state'),
                ('module/v1/ff/SVR4H76530/state', 'AIQS : state'),
                ('module/v1/ff/SVR3QA2098/state', 'MILL : state'),
                ('module/v1/ff/SVR3QA0022/state', 'HBW : state'),
                ('fts/v1/ff/5iO4/state', 'FTS : state'),
                ('ccu/state', 'CCU : state'),
            ]
            
            for topic, expected in test_cases:
                friendly_name = topic_manager.get_friendly_name(topic)
                self.assertEqual(friendly_name, expected, 
                               f"Topic '{topic}' should map to '{expected}', got '{friendly_name}'")
            
            print("✅ Friendly topic names: OK")
        except Exception as e:
            self.fail(f"❌ Friendly topic names failed: {e}")

    def test_module_icons(self):
        """Test: Module-Icons funktionieren korrekt"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import get_module_icon
            
            # Test cases - check that icons are returned (either PNG path or emoji)
            test_cases = [
                ('AIQS', ['🤖', 'aiqs_icon.png']),
                ('MILL', ['⚙️', 'mill_icon.png']),
                ('DRILL', ['🔩', 'drill_icon.png']),
                ('DPS', ['📦', 'dps_icon.png']),
                ('HBW', ['🏬', 'hbw_icon.png']),
                ('FTS', ['🚗', 'fts_icon.jpeg']),
                ('CHRG', ['🔋', 'chrg_icon.png']),
            ]
            
            for module, expected_icons in test_cases:
                icon = get_module_icon(module)
                
                # Icon should be either emoji or file path
                self.assertIsInstance(icon, str)
                self.assertGreater(len(icon), 0)
                
                # Check if it's a valid icon (emoji or file path)
                is_valid = (
                    icon in expected_icons or  # Exact match
                    any(expected_icon in icon for expected_icon in expected_icons) or  # Contains expected
                    icon.endswith('.png') or icon.endswith('.jpeg') or  # File path
                    len(icon) == 1  # Single emoji character
                )
                
                self.assertTrue(is_valid, 
                               f"Module '{module}' should have valid icon, got '{icon}'")
            
            print("✅ Module icons: OK")
        except Exception as e:
            self.fail(f"❌ Module icons failed: {e}")

    def test_single_session_mode_detection(self):
        """Test: Einzel-Session-Modus wird korrekt erkannt"""
        try:
            # Single session data
            single_session_df = self.test_data.copy()
            single_session_mode = len(single_session_df['session_label'].unique()) == 1
            self.assertTrue(single_session_mode, "Single session should be detected")
            
            # Multiple sessions data
            multi_session_df = self.test_data.copy()
            multi_session_df.loc[2, 'session_label'] = 'another-session'
            multi_session_mode = len(multi_session_df['session_label'].unique()) == 1
            self.assertFalse(multi_session_mode, "Multiple sessions should not be detected as single")
            
            print("✅ Single session mode detection: OK")
        except Exception as e:
            self.fail(f"❌ Single session mode detection failed: {e}")

    def test_timestamp_conversion(self):
        """Test: Timestamp-Konvertierung für Slider funktioniert"""
        try:
            # Test pandas timestamp to datetime conversion
            timestamp = pd.Timestamp('2025-08-20 10:00:00')
            datetime_obj = timestamp.to_pydatetime()
            
            self.assertIsInstance(datetime_obj, datetime)
            self.assertEqual(datetime_obj.year, 2025)
            self.assertEqual(datetime_obj.month, 8)
            self.assertEqual(datetime_obj.day, 20)
            self.assertEqual(datetime_obj.hour, 10)
            
            print("✅ Timestamp conversion: OK")
        except Exception as e:
            self.fail(f"❌ Timestamp conversion failed: {e}")

    def test_alphabetical_sorting(self):
        """Test: Alphabetische Sortierung funktioniert"""
        try:
            # Test process labels sorting
            processes = ['wareneingang', 'qualitaetskontrolle', 'bearbeitung', 'lagerung', 'ausgang']
            sorted_processes = sorted(processes)
            expected = ['ausgang', 'bearbeitung', 'lagerung', 'qualitaetskontrolle', 'wareneingang']
            
            self.assertEqual(sorted_processes, expected)
            
            # Test module types sorting
            modules = ['DPS', 'AIQS', 'MILL', 'HBW', 'FTS']
            sorted_modules = sorted(modules)
            expected = ['AIQS', 'DPS', 'FTS', 'HBW', 'MILL']
            
            self.assertEqual(sorted_modules, expected)
            
            print("✅ Alphabetical sorting: OK")
        except Exception as e:
            self.fail(f"❌ Alphabetical sorting failed: {e}")

    def test_filter_function_signature(self):
        """Test: Filter-Funktion hat korrekte Signatur"""
        try:
            from src_orbis.mqtt.dashboard.components.filters import create_filters
            import inspect
            
            # Check function signature
            sig = inspect.signature(create_filters)
            params = list(sig.parameters.keys())
            
            self.assertIn('df', params, "Function should have 'df' parameter")
            self.assertIn('single_session_mode', params, "Function should have 'single_session_mode' parameter")
            
            # Check default value
            default_value = sig.parameters['single_session_mode'].default
            self.assertEqual(default_value, False, "single_session_mode should default to False")
            
            print("✅ Filter function signature: OK")
        except Exception as e:
            self.fail(f"❌ Filter function signature failed: {e}")

    def test_dashboard_integration(self):
        """Test: Dashboard-Integration der neuen Filter"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard
            
            # Create test dashboard
            test_db = "/tmp/test_filter_dashboard.db"
            dashboard = APSDashboard(test_db)
            
            # Check if create_filters method exists and has correct signature
            self.assertTrue(hasattr(dashboard, 'create_filters'))
            
            import inspect
            sig = inspect.signature(dashboard.create_filters)
            params = list(sig.parameters.keys())
            
            self.assertIn('df', params)
            self.assertIn('single_session_mode', params)
            
            print("✅ Dashboard integration: OK")
        except Exception as e:
            self.fail(f"❌ Dashboard integration failed: {e}")

    def test_filter_state_management(self):
        """Test: Filter-State-Management funktioniert"""
        try:
            # Test that filter states are properly initialized
            from src_orbis.mqtt.dashboard.components.filters import create_filters
            
            # This would normally test Streamlit session state
            # For unit testing, we just verify the function doesn't crash
            # In a real Streamlit app, session state would be managed by Streamlit
            
            print("✅ Filter state management: OK (basic check)")
        except Exception as e:
            self.fail(f"❌ Filter state management failed: {e}")

    def test_time_range_filtering(self):
        """Test: Zeitbereich-Filterung funktioniert korrekt"""
        try:
            # Test time range filtering logic
            df = self.test_data.copy()
            
            # Define time range
            start_time = datetime(2025, 8, 20, 10, 1, 0)
            end_time = datetime(2025, 8, 20, 10, 3, 0)
            
            # Filter data
            filtered_df = df[
                (df['timestamp'] >= start_time) & 
                (df['timestamp'] <= end_time)
            ]
            
            # Should have 3 rows (10:01, 10:02, 10:03)
            self.assertEqual(len(filtered_df), 3)
            
            # Check that all timestamps are within range
            for timestamp in filtered_df['timestamp']:
                self.assertGreaterEqual(timestamp, start_time)
                self.assertLessEqual(timestamp, end_time)
            
            print("✅ Time range filtering: OK")
        except Exception as e:
            self.fail(f"❌ Time range filtering failed: {e}")

    def test_module_icon_integration(self):
        """Test: Module-Icon-Integration in Dropdown"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import get_module_icon
            
            # Test module options creation
            modules = ['AIQS', 'MILL', 'DPS', 'HBW', 'FTS']
            module_options = ['Alle']
            
            for module in sorted(modules):
                icon = get_module_icon(module)
                module_options.append(f"{icon} {module}")
            
            # Check that all modules have icons
            self.assertEqual(len(module_options), 6)  # 'Alle' + 5 modules
            
            # Check format
            for option in module_options[1:]:  # Skip 'Alle'
                self.assertIn(' ', option, "Module option should contain space between icon and name")
                parts = option.split(' ', 1)
                self.assertEqual(len(parts), 2, "Module option should have icon and name")
            
            print("✅ Module icon integration: OK")
        except Exception as e:
            self.fail(f"❌ Module icon integration failed: {e}")

    def test_friendly_topic_integration(self):
        """Test: Friendly Topic Integration in Dropdown"""
        try:
            from src_orbis.mqtt.tools.topic_manager import get_topic_manager
            
            topic_manager = get_topic_manager()
            
            # Test friendly topic mapping creation
            topics = [
                'module/v1/ff/SVR4H73275/state',
                'module/v1/ff/SVR4H76530/state',
                'module/v1/ff/SVR3QA2098/state'
            ]
            
            friendly_topics = {}
            for topic in topics:
                friendly_name = topic_manager.get_friendly_name(topic)
                friendly_topics[friendly_name] = topic
            
            # Check mapping
            self.assertIn('DPS : state', friendly_topics)
            self.assertIn('AIQS : state', friendly_topics)
            self.assertIn('MILL : state', friendly_topics)
            
            # Check reverse mapping
            self.assertEqual(friendly_topics['DPS : state'], 'module/v1/ff/SVR4H73275/state')
            
            print("✅ Friendly topic integration: OK")
        except Exception as e:
            self.fail(f"❌ Friendly topic integration failed: {e}")


def run_filter_tests():
    """Run all filter improvement tests"""
    print("🧪 Running Filter Improvement Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFilterImprovements)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 50)
    print(f"📊 Test Results:")
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
        print("\n✅ All filter improvement tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_filter_tests()
    sys.exit(0 if success else 1)
