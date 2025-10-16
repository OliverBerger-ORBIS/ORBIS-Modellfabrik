#!/usr/bin/env python3
from omf.dashboard.tools.path_constants import PROJECT_ROOT

"""
Test für OMF Shopfloor-Komponenten - migriert zu aps_modules.py
Prüft alle Shopfloor-bezogenen Komponenten über aps_modules.py Factory Configuration
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

# Add project root to path
project_root = PROJECT_ROOT

# Mock Streamlit für Tests
import sys

sys.modules['streamlit'] = Mock()
sys.modules['yaml'] = Mock()


class TestShopfloorComponents(unittest.TestCase):
    """Test-Klasse für Shopfloor-Komponenten - migriert zu aps_modules.py"""

    def test_shopfloor_manager_import(self):
        """Test: Shopfloor Manager kann importiert werden"""
        try:
            # Mock der Dependencies - Path.exists() muss True zurückgeben
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.__truediv__ = lambda self, other: mock_path

            with patch('omf.tools.shopfloor_manager.REGISTRY_DIR', mock_path):
                with patch('builtins.open', MagicMock()):
                    with patch('yaml.safe_load', return_value={"grid": {}, "positions": []}):
                        from omf.tools.shopfloor_manager import get_omf_shopfloor_manager
                        manager = get_omf_shopfloor_manager()
                        self.assertIsNotNone(manager, "Shopfloor Manager sollte verfügbar sein")
                        print("✅ Shopfloor Manager Import: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor Manager Import failed: {e}")

    def test_shopfloor_manager_methods(self):
        """Test: Shopfloor Manager Methoden sind verfügbar"""
        try:
            # Mock der Dependencies - Path.exists() muss True zurückgeben
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.__truediv__ = lambda self, other: mock_path

            with patch('omf.tools.shopfloor_manager.REGISTRY_DIR', mock_path):
                with patch('builtins.open', MagicMock()):
                    with patch('yaml.safe_load', return_value={"grid": {}, "positions": [], "routes": {}}):
                        from omf.tools.shopfloor_manager import get_omf_shopfloor_manager
                        manager = get_omf_shopfloor_manager()

                        # Teste Methoden-Verfügbarkeit
                        self.assertTrue(hasattr(manager, 'get_all_positions'), "get_all_positions sollte verfügbar sein")
                        self.assertTrue(hasattr(manager, 'get_all_routes'), "get_all_routes sollte verfügbar sein")
                        self.assertTrue(hasattr(manager, 'get_layout_statistics'), "get_layout_statistics sollte verfügbar sein")
                        print("✅ Shopfloor Manager Methoden: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor Manager Methoden failed: {e}")

    def test_shopfloor_manager_singleton(self):
        """Test: Shopfloor Manager ist Singleton"""
        try:
            # Mock der Dependencies - Path.exists() muss True zurückgeben
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.__truediv__ = lambda self, other: mock_path

            with patch('omf.tools.shopfloor_manager.REGISTRY_DIR', mock_path):
                with patch('builtins.open', MagicMock()):
                    with patch('yaml.safe_load', return_value={"grid": {}, "positions": [], "routes": {}}):
                        from omf.tools.shopfloor_manager import get_omf_shopfloor_manager

                        manager1 = get_omf_shopfloor_manager()
                        manager2 = get_omf_shopfloor_manager()

                        self.assertIs(manager1, manager2, "Shopfloor Manager sollte Singleton sein")
                        print("✅ Shopfloor Manager Singleton: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor Manager Singleton failed: {e}")


if __name__ == "__main__":
    unittest.main()
