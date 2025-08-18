#!/usr/bin/env python3
"""
Test für Dashboard-Imports
Prüft, ob alle Module korrekt importiert werden können
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDashboardImports(unittest.TestCase):
    """Test Dashboard Import-Funktionalität"""

    def test_dashboard_config_import(self):
        """Test: Dashboard config settings import"""
        try:
            from src_orbis.mqtt.dashboard.config.settings import APS_MODULES_EXTENDED
            self.assertIsNotNone(APS_MODULES_EXTENDED)
            print("✅ Dashboard config import: OK")
        except ImportError as e:
            self.fail(f"❌ Dashboard config import failed: {e}")

    def test_dashboard_utils_import(self):
        """Test: Dashboard utils import"""
        try:
            from src_orbis.mqtt.dashboard.utils.data_handling import extract_module_info
            self.assertTrue(callable(extract_module_info))
            print("✅ Dashboard utils import: OK")
        except ImportError as e:
            self.fail(f"❌ Dashboard utils import failed: {e}")

    def test_dashboard_components_import(self):
        """Test: Dashboard components import"""
        try:
            from src_orbis.mqtt.dashboard.components.filters import create_filters
            self.assertTrue(callable(create_filters))
            print("✅ Dashboard components import: OK")
        except ImportError as e:
            self.fail(f"❌ Dashboard components import failed: {e}")

    def test_mqtt_message_library_import(self):
        """Test: MQTT message library import"""
        try:
            from src_orbis.mqtt.tools.mqtt_message_library import (
                MQTTMessageLibrary,
                create_message_from_template,
                list_available_templates,
                get_template_info,
            )
            self.assertTrue(callable(MQTTMessageLibrary))
            self.assertTrue(callable(create_message_from_template))
            self.assertTrue(callable(list_available_templates))
            self.assertTrue(callable(get_template_info))
            print("✅ MQTT message library import: OK")
        except ImportError as e:
            self.fail(f"❌ MQTT message library import failed: {e}")

    def test_dashboard_main_import(self):
        """Test: Dashboard main file import"""
        try:
            # Test if we can import the main dashboard file
            dashboard_path = project_root / "src_orbis" / "mqtt" / "dashboard" / "aps_dashboard.py"
            self.assertTrue(dashboard_path.exists(), f"Dashboard file not found: {dashboard_path}")
            print("✅ Dashboard file exists: OK")
        except Exception as e:
            self.fail(f"❌ Dashboard file check failed: {e}")


class TestDashboardStartup(unittest.TestCase):
    """Test Dashboard Startup-Funktionalität"""

    def test_dashboard_can_start(self):
        """Test: Dashboard kann gestartet werden (ohne Streamlit)"""
        try:
            # Import without running Streamlit
            import src_orbis.mqtt.dashboard.aps_dashboard
            print("✅ Dashboard can be imported: OK")
        except Exception as e:
            self.fail(f"❌ Dashboard import failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing Dashboard Imports...")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 50)
    print("�� Test completed!")
