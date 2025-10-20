#!/usr/bin/env python3
"""
Tests for Admin Settings
"""

# Set up path for imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from omf2.admin.admin_settings import AdminSettings


class TestAdminSettings(unittest.TestCase):
    """Test cases for Admin Settings"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test files
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_dir = self.temp_dir / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_admin_settings_initialization(self):
        """Test admin settings initialization"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        self.assertEqual(admin_settings.config_dir, self.config_dir)
        self.assertTrue(admin_settings.config_dir.exists())

    def test_load_default_mqtt_settings(self):
        """Test loading default MQTT settings when file doesn't exist"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        mqtt_settings = admin_settings.load_mqtt_settings()

        self.assertIsInstance(mqtt_settings, dict)
        self.assertIn("environments", mqtt_settings)
        self.assertIn("live", mqtt_settings["environments"])
        self.assertIn("replay", mqtt_settings["environments"])
        self.assertIn("mock", mqtt_settings["environments"])
        self.assertEqual(mqtt_settings["default_environment"], "replay")

    def test_save_and_load_mqtt_settings(self):
        """Test saving and loading MQTT settings"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        test_settings = {
            "environments": {"test": {"host": "test.broker.com", "port": 1883, "enabled": True}},
            "default_environment": "test",
        }

        # Save settings
        result = admin_settings.save_mqtt_settings(test_settings)
        self.assertTrue(result)

        # Load settings
        loaded_settings = admin_settings.load_mqtt_settings()
        self.assertEqual(loaded_settings["default_environment"], "test")
        self.assertEqual(loaded_settings["environments"]["test"]["host"], "test.broker.com")

    def test_load_default_user_roles(self):
        """Test loading default user roles when file doesn't exist"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        user_roles = admin_settings.load_user_roles()

        self.assertIsInstance(user_roles, dict)
        self.assertIn("roles", user_roles)
        self.assertIn("users", user_roles)
        self.assertIn("admin", user_roles["roles"])
        self.assertIn("operator", user_roles["roles"])
        self.assertIn("operator", user_roles["roles"])
        self.assertEqual(user_roles["default_role"], "operator")

    def test_get_environment_settings(self):
        """Test getting settings for specific environment"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        # Test default environments
        live_settings = admin_settings.get_environment_settings("live")
        self.assertIsNotNone(live_settings)
        self.assertEqual(live_settings["host"], "localhost")
        self.assertEqual(live_settings["port"], 1883)

        # Test non-existent environment
        fake_settings = admin_settings.get_environment_settings("nonexistent")
        self.assertIsNone(fake_settings)

    def test_get_available_environments(self):
        """Test getting list of available environments"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        environments = admin_settings.get_available_environments()

        self.assertIsInstance(environments, list)
        self.assertIn("live", environments)
        self.assertIn("replay", environments)
        self.assertIn("mock", environments)

    def test_user_permissions(self):
        """Test user permission management"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        # Test admin permissions
        admin_permissions = admin_settings.get_user_permissions("admin")
        self.assertIn("*", admin_permissions)

        # Test admin has all permissions
        self.assertTrue(admin_settings.has_permission("admin", "read"))
        self.assertTrue(admin_settings.has_permission("admin", "write"))
        self.assertTrue(admin_settings.has_permission("admin", "control"))

        # Test non-existent user (should get default role permissions)
        nonexistent_permissions = admin_settings.get_user_permissions("nonexistent")
        self.assertEqual(nonexistent_permissions, [])  # Inactive user

    def test_get_enabled_apps(self):
        """Test getting enabled apps"""
        admin_settings = AdminSettings(config_dir=self.config_dir)

        # Test without user (should return all enabled apps)
        apps = admin_settings.get_enabled_apps()
        self.assertIsInstance(apps, dict)
        self.assertIn("ccu_dashboard", apps)

        # Test with admin user (should return all apps including admin-only)
        admin_apps = admin_settings.get_enabled_apps("admin")
        self.assertIsInstance(admin_apps, dict)
        self.assertIn("ccu_dashboard", admin_apps)
        self.assertIn("admin_settings", admin_apps)  # Admin-only app


if __name__ == "__main__":
    unittest.main()
