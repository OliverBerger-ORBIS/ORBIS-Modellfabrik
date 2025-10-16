#!/usr/bin/env python3
"""
Test for Streamlit startup errors and warnings
"""

import os
import sys
import unittest
import warnings
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestStreamlitStartup(unittest.TestCase):
    """Test Streamlit startup for errors and warnings"""

    def setUp(self):
        """Set up test environment"""
        # Capture warnings
        self.warning_catcher = warnings.catch_warnings(record=True)
        self.warning_catcher.__enter__()

    def tearDown(self):
        """Clean up test environment"""
        self.warning_catcher.__exit__(None, None, None)

    def test_import_all_ui_components(self):
        """Test that all UI components can be imported without errors"""
        import_errors = []
        import_warnings = []

        # List of all UI components that should be importable
        ui_components = [
            # CCU Components
            ("omf2.ui.ccu.ccu_overview.ccu_overview_tab", "render_ccu_overview_tab"),
            ("omf2.ui.ccu.ccu_orders.ccu_orders_tab", "render_ccu_orders_tab"),
            ("omf2.ui.ccu.ccu_process.ccu_process_tab", "render_ccu_process_tab"),
            ("omf2.ui.ccu.ccu_configuration.ccu_configuration_tab", "render_ccu_configuration_tab"),
            ("omf2.ui.ccu.ccu_modules.ccu_modules_tab", "render_ccu_modules_tab"),
            # Node-RED Components
            ("omf2.ui.nodered.nodered_overview.nodered_overview_tab", "render_nodered_overview_tab"),
            ("omf2.ui.nodered.nodered_processes.nodered_processes_tab", "render_nodered_processes_tab"),
            # Admin Components
            ("omf2.ui.admin.system_logs.system_logs_tab", "render_system_logs_tab"),
            ("omf2.ui.admin.admin_settings.admin_settings_tab", "render_admin_settings_tab"),
        ]

        for module_path, function_name in ui_components:
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")

                    # Import the module
                    module = __import__(module_path, fromlist=[function_name])
                    function = getattr(module, function_name)

                    # Check for warnings during import
                    if w:
                        for warning in w:
                            import_warnings.append(f"{module_path}: {warning.message}")

                    # Verify function is callable
                    self.assertTrue(callable(function), f"{function_name} is not callable")

            except ImportError as e:
                import_errors.append(f"{module_path}: {str(e)}")
            except AttributeError as e:
                import_errors.append(f"{module_path}.{function_name}: {str(e)}")
            except Exception as e:
                import_errors.append(f"{module_path}: Unexpected error: {str(e)}")

        # Report results
        if import_errors:
            print("\n❌ IMPORT ERRORS FOUND:")
            for error in import_errors:
                print(f"  • {error}")

        if import_warnings:
            print("\n⚠️ IMPORT WARNINGS FOUND:")
            for warning in import_warnings:
                print(f"  • {warning}")

        # Assert no import errors
        self.assertEqual(len(import_errors), 0, f"Found {len(import_errors)} import errors")

        # Log warnings but don't fail test
        if import_warnings:
            print(f"\n⚠️ Found {len(import_warnings)} import warnings (non-critical)")

    def test_user_manager_tab_config(self):
        """Test that user manager can generate tab config without errors"""
        try:
            from omf2.ui.user_manager import UserManager

            user_manager = UserManager()

            # Test all roles
            roles = ["administrator", "supervisor", "operator"]

            for role in roles:
                with self.subTest(role=role):
                    # Set role
                    user_manager.set_user_role(role)

                    # Get tab config
                    tab_config = user_manager.get_tab_config()

                    # Verify tab config is not empty
                    self.assertIsNotNone(tab_config, f"Tab config is None for role {role}")
                    self.assertGreater(len(tab_config), 0, f"No tabs available for role {role}")

                    # Verify each tab has required fields
                    for tab_key, tab_info in tab_config.items():
                        self.assertIn("module", tab_info, f"Missing 'module' in {tab_key}")
                        self.assertIn("function", tab_info, f"Missing 'function' in {tab_key}")
                        self.assertIn("icon", tab_info, f"Missing 'icon' in {tab_key}")
                        self.assertIn("name", tab_info, f"Missing 'name' in {tab_key}")

                        # Verify module path is valid
                        module_path = tab_info["module"]
                        self.assertTrue(module_path.startswith("omf2.ui."), f"Invalid module path: {module_path}")

        except Exception as e:
            self.fail(f"UserManager tab config test failed: {str(e)}")

    def test_main_dashboard_initialization(self):
        """Test that main dashboard can be initialized without errors"""
        try:
            from omf2.ui.main_dashboard import MainDashboard

            # Mock streamlit session state
            with patch("streamlit.session_state", {}):
                dashboard = MainDashboard()
                self.assertIsNotNone(dashboard)

        except Exception as e:
            self.fail(f"MainDashboard initialization failed: {str(e)}")

    def test_all_module_paths_exist(self):
        """Test that all module paths referenced in user_manager actually exist"""
        from omf2.ui.user_manager import UserManager

        user_manager = UserManager()
        tab_config = user_manager.get_tab_config()

        missing_modules = []

        for _tab_key, tab_info in tab_config.items():
            module_path = tab_info["module"]
            function_name = tab_info["function"]

            try:
                # Try to import the module
                module = __import__(module_path, fromlist=[function_name])

                # Check if function exists
                if not hasattr(module, function_name):
                    missing_modules.append(f"{module_path}.{function_name} - function not found")

            except ImportError as e:
                missing_modules.append(f"{module_path} - {str(e)}")
            except Exception as e:
                missing_modules.append(f"{module_path} - unexpected error: {str(e)}")

        if missing_modules:
            print("\n❌ MISSING MODULES:")
            for missing in missing_modules:
                print(f"  • {missing}")

        self.assertEqual(len(missing_modules), 0, f"Found {len(missing_modules)} missing modules")


if __name__ == "__main__":
    # Run the test
    unittest.main(verbosity=2)
