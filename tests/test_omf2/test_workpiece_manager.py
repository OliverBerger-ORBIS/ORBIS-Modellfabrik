#!/usr/bin/env python3
"""
Tests for Workpiece Manager
"""

# Set up path for imports
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from omf2.ccu.workpiece_manager import WorkpieceManager, get_workpiece_manager


class TestWorkpieceManager(unittest.TestCase):
    """Test cases for Workpiece Manager"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test files
        self.temp_dir = Path(tempfile.mkdtemp())
        self.registry_dir = self.temp_dir / "registry"
        self.registry_dir.mkdir(parents=True, exist_ok=True)

        # Create test directories
        (self.registry_dir / "model" / "v2").mkdir(parents=True, exist_ok=True)
        (self.registry_dir / "schemas").mkdir(parents=True, exist_ok=True)

        # Create test workpieces config
        self.test_workpieces = {
            "metadata": {
                "version": "2.0.0",
                "description": "Test Workpieces Registry",
                "schema_version": "workpieces.schema.json",
            },
            "workpieces": {
                "R1": {
                    "id": "R1",
                    "name": "Red Workpiece 1",
                    "color": "red",
                    "type": "cylinder",
                    "nfc_codes": ["040a8dca341291", "041b2fda452382"],
                },
                "B1": {
                    "id": "B1",
                    "name": "Blue Workpiece 1",
                    "color": "blue",
                    "type": "cylinder",
                    "nfc_codes": ["042c3eeb563473"],
                },
            },
            "colors": [
                {"id": "red", "name": "Red", "hex": "#FF0000"},
                {"id": "blue", "name": "Blue", "hex": "#0000FF"},
            ],
        }

        # Write test config
        workpieces_file = self.registry_dir / "model" / "v2" / "workpieces.yml"
        with open(workpieces_file, "w") as f:
            yaml.safe_dump(self.test_workpieces, f)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_initialization(self):
        """Test workpiece manager initialization"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        self.assertEqual(manager.registry_dir, self.registry_dir)
        self.assertIsInstance(manager.workpieces_config, dict)
        self.assertIn("workpieces", manager.workpieces_config)

    def test_get_workpiece_by_id(self):
        """Test getting workpiece by ID"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        workpiece = manager.get_workpiece_by_id("R1")
        self.assertIsNotNone(workpiece)
        self.assertEqual(workpiece["name"], "Red Workpiece 1")
        self.assertEqual(workpiece["color"], "red")

        # Test non-existent workpiece
        workpiece = manager.get_workpiece_by_id("NONEXISTENT")
        self.assertIsNone(workpiece)

    def test_get_workpiece_by_nfc_code(self):
        """Test getting workpiece by NFC code"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        workpiece = manager.get_workpiece_by_nfc_code("040a8dca341291")
        self.assertIsNotNone(workpiece)
        self.assertEqual(workpiece["id"], "R1")

        workpiece = manager.get_workpiece_by_nfc_code("042c3eeb563473")
        self.assertIsNotNone(workpiece)
        self.assertEqual(workpiece["id"], "B1")

        # Test non-existent NFC code
        workpiece = manager.get_workpiece_by_nfc_code("nonexistent")
        self.assertIsNone(workpiece)

    def test_validate_nfc_code(self):
        """Test NFC code validation"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        # Valid existing codes
        self.assertTrue(manager.validate_nfc_code("040a8dca341291"))
        self.assertTrue(manager.validate_nfc_code("042c3eeb563473"))

        # Invalid format
        self.assertFalse(manager.validate_nfc_code("invalid"))
        self.assertFalse(manager.validate_nfc_code("12345"))  # Too short
        self.assertFalse(manager.validate_nfc_code("ghijk67890123"))  # Not hex

        # Valid format but non-existent
        self.assertFalse(manager.validate_nfc_code("123456789012"))

    def test_get_statistics(self):
        """Test getting workpiece statistics"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        stats = manager.get_statistics()

        self.assertEqual(stats["total_workpieces"], 2)
        self.assertEqual(stats["colors"]["red"], 1)
        self.assertEqual(stats["colors"]["blue"], 1)
        self.assertEqual(stats["types"]["cylinder"], 2)
        self.assertEqual(stats["total_nfc_codes"], 3)

    def test_get_workpiece_display_name(self):
        """Test getting formatted display names"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        # With ID
        name = manager.get_workpiece_display_name("R1", include_id=True)
        self.assertEqual(name, "Red Workpiece 1 (R1)")

        # Without ID
        name = manager.get_workpiece_display_name("R1", include_id=False)
        self.assertEqual(name, "Red Workpiece 1")

        # Non-existent workpiece
        name = manager.get_workpiece_display_name("NONEXISTENT")
        self.assertEqual(name, "NONEXISTENT")

    def test_reload_config(self):
        """Test configuration reloading"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        # Modify the config file
        new_workpieces = self.test_workpieces.copy()
        new_workpieces["workpieces"]["G1"] = {"id": "G1", "name": "Green Workpiece 1", "color": "green", "type": "cube"}

        workpieces_file = self.registry_dir / "model" / "v2" / "workpieces.yml"
        with open(workpieces_file, "w") as f:
            yaml.safe_dump(new_workpieces, f)

        # Reload config
        result = manager.reload_config()
        self.assertTrue(result)

        # Check new workpiece is loaded
        workpiece = manager.get_workpiece_by_id("G1")
        self.assertIsNotNone(workpiece)
        self.assertEqual(workpiece["name"], "Green Workpiece 1")

    def test_get_workpieces_by_color(self):
        """Test getting workpieces by color"""
        manager = WorkpieceManager(registry_dir=self.registry_dir)

        red_workpieces = manager.get_workpieces_by_color("red")
        self.assertEqual(len(red_workpieces), 1)
        self.assertEqual(red_workpieces[0]["id"], "R1")

        blue_workpieces = manager.get_workpieces_by_color("blue")
        self.assertEqual(len(blue_workpieces), 1)
        self.assertEqual(blue_workpieces[0]["id"], "B1")

        # Non-existent color
        green_workpieces = manager.get_workpieces_by_color("green")
        self.assertEqual(len(green_workpieces), 0)

    def test_singleton_pattern(self):
        """Test workpiece manager singleton pattern"""
        manager1 = get_workpiece_manager(registry_dir=self.registry_dir)
        manager2 = get_workpiece_manager(registry_dir=Path("/different/path"))  # Should ignore new path

        self.assertIs(manager1, manager2)
        self.assertEqual(manager1.registry_dir, self.registry_dir)  # Should keep original path


if __name__ == "__main__":
    unittest.main()
