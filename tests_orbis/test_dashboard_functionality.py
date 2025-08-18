#!/usr/bin/env python3
"""
Test für Dashboard-Funktionalität
Prüft die tatsächliche Funktionalität des Dashboards
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDashboardFunctionality(unittest.TestCase):
    """Test Dashboard-Funktionalität"""

    def test_aps_modules_extended_structure(self):
        """Test: APS_MODULES_EXTENDED Struktur ist korrekt"""
        try:
            from src_orbis.mqtt.dashboard.config.settings import APS_MODULES_EXTENDED
            
            # Check if it exists
            self.assertIsNotNone(APS_MODULES_EXTENDED)
            self.assertIsInstance(APS_MODULES_EXTENDED, dict)
            
            # Check structure for each module
            for module_name, module_info in APS_MODULES_EXTENDED.items():
                self.assertIsInstance(module_info, dict)
                self.assertIn('id', module_info, f"Module {module_name} missing 'id'")
                self.assertIn('name', module_info, f"Module {module_name} missing 'name'")
                self.assertIn('icon', module_info, f"Module {module_name} missing 'icon'")
                self.assertIn('type', module_info, f"Module {module_name} missing 'type'")
                self.assertIn('commands', module_info, f"Module {module_name} missing 'commands'")
                self.assertIn('ip', module_info, f"Module {module_name} missing 'ip'")
            
            print("✅ APS_MODULES_EXTENDED structure: OK")
            
        except Exception as e:
            self.fail(f"❌ APS_MODULES_EXTENDED structure failed: {e}")

    def test_dashboard_initialization(self):
        """Test: Dashboard kann initialisiert werden"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard
            
            # Create a dummy database file for testing
            test_db = "/tmp/test_dashboard.db"
            
            # Initialize dashboard
            dashboard = APSDashboard(test_db)
            
            # Check required attributes
            self.assertIsNotNone(dashboard.aps_modules_extended)
            self.assertIsNotNone(dashboard.message_library)
            self.assertIsNotNone(dashboard.mqtt_broker)
            self.assertIsNotNone(dashboard.mqtt_port)
            
            print("✅ Dashboard initialization: OK")
            
        except Exception as e:
            self.fail(f"❌ Dashboard initialization failed: {e}")

    def test_mqtt_message_library_integration(self):
        """Test: MQTT Message Library Integration"""
        try:
            from src_orbis.mqtt.tools.mqtt_message_library import MQTTMessageLibrary
            from src_orbis.mqtt.dashboard.config.settings import APS_MODULES_EXTENDED
            
            # Initialize library
            library = MQTTMessageLibrary()
            
            # Test with each module
            for module_name in APS_MODULES_EXTENDED.keys():
                # Test get_working_commands
                commands = library.get_working_commands(module_name)
                self.assertIsInstance(commands, list)
                
                # Test get_module_info
                module_info = library.get_module_info(module_name)
                self.assertIsInstance(module_info, dict)
            
            print("✅ MQTT Message Library integration: OK")
            
        except Exception as e:
            self.fail(f"❌ MQTT Message Library integration failed: {e}")

    def test_dashboard_methods_exist(self):
        """Test: Dashboard-Methoden existieren"""
        try:
            from src_orbis.mqtt.dashboard.aps_dashboard import APSDashboard
            
            test_db = "/tmp/test_dashboard.db"
            dashboard = APSDashboard(test_db)
            
            # Check if required methods exist
            required_methods = [
                'show_mqtt_control',
                'show_module_overview_dashboard',
                'show_aps_analysis',
                'show_settings',
                'connect_mqtt',
                'disconnect_mqtt',
                'send_mqtt_message_direct'
            ]
            
            for method_name in required_methods:
                self.assertTrue(hasattr(dashboard, method_name), 
                              f"Method {method_name} not found")
            
            print("✅ Dashboard methods exist: OK")
            
        except Exception as e:
            self.fail(f"❌ Dashboard methods check failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing Dashboard Functionality...")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("=" * 50)
    print("🎯 Functionality test completed!")
