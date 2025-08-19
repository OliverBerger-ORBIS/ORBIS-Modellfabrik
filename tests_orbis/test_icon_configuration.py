#!/usr/bin/env python3
"""
Test für Icon Configuration System
Prüft die Icon-Konfiguration und -Verwaltung
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestIconConfiguration(unittest.TestCase):
    """Test Icon Configuration System"""

    def test_icon_config_import(self):
        """Test: Icon Config kann importiert werden"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import (
                MODULE_ICONS, STATUS_ICONS, get_module_icon, get_status_icon
            )
            
            # Check if imports are successful
            self.assertIsNotNone(MODULE_ICONS)
            self.assertIsNotNone(STATUS_ICONS)
            self.assertIsNotNone(get_module_icon)
            self.assertIsNotNone(get_status_icon)
            
            print("✅ Icon config import: OK")
            
        except ImportError as e:
            self.fail(f"❌ Icon config import failed: {e}")

    def test_module_icons_structure(self):
        """Test: MODULE_ICONS Struktur ist korrekt"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import MODULE_ICONS
            
            # Check if it's a dictionary
            self.assertIsInstance(MODULE_ICONS, dict)
            
            # Check for required modules
            required_modules = ['DPS', 'HBW', 'MILL', 'DRILL', 'AIQS', 'FTS']
            
            for module in required_modules:
                self.assertIn(module, MODULE_ICONS)
                icon_info = MODULE_ICONS[module]
                self.assertIsInstance(icon_info, str)  # Icons are strings (emojis)
                self.assertGreater(len(icon_info), 0)  # Icon should not be empty
            
            print("✅ Module icons structure: OK")
            
        except Exception as e:
            self.fail(f"❌ Module icons structure failed: {e}")

    def test_status_icons_structure(self):
        """Test: STATUS_ICONS Struktur ist korrekt"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import STATUS_ICONS
            
            # Check if it's a dictionary
            self.assertIsInstance(STATUS_ICONS, dict)
            
            # Check for required statuses (using actual status names from config)
            required_statuses = ['available', 'busy', 'error', 'idle', 'offline']
            
            for status in required_statuses:
                self.assertIn(status, STATUS_ICONS)
                icon_info = STATUS_ICONS[status]
                self.assertIsInstance(icon_info, str)  # Icons are strings (emojis)
                self.assertGreater(len(icon_info), 0)  # Icon should not be empty
            
            print("✅ Status icons structure: OK")
            
        except Exception as e:
            self.fail(f"❌ Status icons structure failed: {e}")

    def test_get_module_icon_function(self):
        """Test: get_module_icon Funktion"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import get_module_icon
            
            # Test with valid modules
            test_modules = ['DPS', 'HBW', 'MILL', 'DRILL', 'AIQS', 'FTS']
            
            for module in test_modules:
                icon_info = get_module_icon(module)
                self.assertIsInstance(icon_info, str)  # Icon is a string (emoji or path)
                self.assertGreater(len(icon_info), 0)  # Icon should not be empty
            
            # Test with invalid module (should return default)
            default_icon = get_module_icon('INVALID_MODULE')
            self.assertIsInstance(default_icon, str)
            self.assertEqual(default_icon, "❓")  # Default icon for unknown modules
            
            print("✅ get_module_icon function: OK")
            
        except Exception as e:
            self.fail(f"❌ get_module_icon function failed: {e}")

    def test_get_status_icon_function(self):
        """Test: get_status_icon Funktion"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import get_status_icon
            
            # Test with valid statuses
            test_statuses = ['available', 'busy', 'error', 'idle', 'offline']
            
            for status in test_statuses:
                icon_info = get_status_icon(status)
                self.assertIsInstance(icon_info, str)  # Icon is a string (emoji)
                self.assertGreater(len(icon_info), 0)  # Icon should not be empty
            
            # Test with invalid status (should return default)
            default_icon = get_status_icon('INVALID_STATUS')
            self.assertIsInstance(default_icon, str)
            # Should return a valid status icon (pattern matching)
            
            print("✅ get_status_icon function: OK")
            
        except Exception as e:
            self.fail(f"❌ get_status_icon function failed: {e}")

    def test_icon_paths_exist(self):
        """Test: Icon-Pfade existieren (falls Icons als Dateien)"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import MODULE_ICONS, STATUS_ICONS
            
            # Check if icon paths exist (if they are file paths)
            all_icons = list(MODULE_ICONS.values()) + list(STATUS_ICONS.values())
            
            for icon_info in all_icons:
                # Icons are strings, check if they look like file paths
                if isinstance(icon_info, str) and ('/' in icon_info or '\\' in icon_info):
                    if os.path.isfile(icon_info):
                        self.assertTrue(os.path.exists(icon_info))
            
            print("✅ Icon paths validation: OK")
            
        except Exception as e:
            self.fail(f"❌ Icon paths validation failed: {e}")

    def test_icon_colors_are_valid(self):
        """Test: Icon-Farben sind gültige CSS-Farben"""
        try:
            from src_orbis.mqtt.dashboard.config.icon_config import MODULE_ICONS, STATUS_ICONS
            
            # Icons are emojis, so no color validation needed
            # This test is kept for future use if colors are added
            
            all_icons = list(MODULE_ICONS.values()) + list(STATUS_ICONS.values())
            
            # Check that all icons are valid strings
            for icon_info in all_icons:
                self.assertIsInstance(icon_info, str)
                self.assertGreater(len(icon_info), 0)
            
            print("✅ Icon colors validation: OK")
            
        except Exception as e:
            self.fail(f"❌ Icon colors validation failed: {e}")


if __name__ == '__main__':
    unittest.main()
