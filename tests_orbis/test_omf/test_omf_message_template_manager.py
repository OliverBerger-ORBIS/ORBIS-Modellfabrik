#!/usr/bin/env python3
"""
Unit Tests für OMF Message Template Manager
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

# Add src_orbis to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))

from omf.tools.message_template_manager import OmfMessageTemplateManager, get_omf_message_template_manager


class TestOMFMessageTemplateManager(unittest.TestCase):
    """Test cases for OMFMessageTemplateManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = Path(self.temp_dir) / "message_templates"
        self.templates_dir.mkdir()

        # Create test structure
        (self.templates_dir / "templates" / "ccu").mkdir(parents=True)
        (self.templates_dir / "templates" / "txt").mkdir(parents=True)

        # Create test metadata
        self._create_test_metadata()
        self._create_test_categories()
        self._create_test_templates()

        # Initialize manager
        self.manager = OmfMessageTemplateManager(str(self.templates_dir))

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _create_test_metadata(self):
        """Create test metadata file"""
        metadata = {
            "metadata": {
                "version": "3.0.0",
                "description": "Test Templates",
                "last_updated": "2025-08-29",
            },
            "categories": ["CCU", "TXT"],
        }

        with open(self.templates_dir / "metadata.yml", "w") as f:
            yaml.dump(metadata, f)

    def _create_test_categories(self):
        """Create test categories file"""
        categories = {
            "categories": {
                "CCU": {
                    "description": "Central Control Unit",
                    "icon": "🏭",
                    "sub_categories": {
                        "Control": {
                            "description": "Control Commands",
                            "icon": "🎮",
                            "template_file": "templates/ccu/control.yml",
                        }
                    },
                },
                "TXT": {
                    "description": "TXT Controller",
                    "icon": "🔧",
                    "sub_categories": {
                        "Control": {
                            "description": "TXT Control",
                            "icon": "🎮",
                            "template_file": "templates/txt/control.yml",
                        }
                    },
                },
            }
        }

        with open(self.templates_dir / "categories.yml", "w") as f:
            yaml.dump(categories, f)

    def _create_test_templates(self):
        """Create test template files"""
        # CCU Control templates
        ccu_templates = {
            "metadata": {
                "version": "3.0.0",
                "category": "CCU",
                "sub_category": "Control",
            },
            "templates": {
                "ccu/control": {
                    "description": "CCU Control Command",
                    "structure": {"command": "<string>", "timestamp": "<datetime>"},
                    "examples": [{"command": "start", "timestamp": "2025-08-29T10:00:00Z"}],
                    "validation_rules": ["command muss gültiger Befehl sein"],
                }
            },
        }

        with open(self.templates_dir / "templates" / "ccu" / "control.yml", "w") as f:
            yaml.dump(ccu_templates, f)

        # TXT Control templates
        txt_templates = {
            "metadata": {
                "version": "3.0.0",
                "category": "TXT",
                "sub_category": "Control",
            },
            "templates": {
                "/j1/txt/1/c/bme680": {
                    "description": "BME680 Sensor Control",
                    "structure": {"period": "<number>", "ts": "<datetime>"},
                    "examples": [{"period": 60, "ts": "2025-08-29T10:00:00Z"}],
                    "validation_rules": ["period muss positive Zahl sein"],
                }
            },
        }

        with open(self.templates_dir / "templates" / "txt" / "control.yml", "w") as f:
            yaml.dump(txt_templates, f)

    def test_singleton_pattern(self):
        """Test singleton pattern"""
        manager1 = get_omf_message_template_manager()
        manager2 = get_omf_message_template_manager()
        self.assertIs(manager1, manager2)

    def test_load_metadata(self):
        """Test metadata loading"""
        self.assertIsNotNone(self.manager.metadata)
        self.assertEqual(self.manager.metadata.get("metadata", {}).get("version"), "3.0.0")

    def test_load_categories(self):
        """Test categories loading"""
        self.assertIsNotNone(self.manager.categories)
        categories = self.manager.categories.get("categories", {})
        self.assertIn("CCU", categories)
        self.assertIn("TXT", categories)

    def test_load_templates(self):
        """Test template loading"""
        self.assertGreater(len(self.manager.templates), 0)
        self.assertIn("ccu/control", self.manager.templates)
        self.assertIn("/j1/txt/1/c/bme680", self.manager.templates)

    def test_get_topic_template(self):
        """Test getting specific template"""
        template = self.manager.get_topic_template("ccu/control")
        self.assertIsNotNone(template)
        self.assertEqual(template["description"], "CCU Control Command")

    def test_get_all_topics(self):
        """Test getting all topics"""
        topics = self.manager.get_all_topics()
        self.assertIn("ccu/control", topics)
        self.assertIn("/j1/txt/1/c/bme680", topics)

    def test_get_topics_by_category(self):
        """Test getting topics by category"""
        ccu_topics = self.manager.get_topics_by_category("CCU")
        self.assertIn("ccu/control", ccu_topics)

        txt_topics = self.manager.get_topics_by_category("TXT")
        self.assertIn("/j1/txt/1/c/bme680", txt_topics)

    def test_get_topics_by_sub_category(self):
        """Test getting topics by sub-category"""
        control_topics = self.manager.get_topics_by_sub_category("Control")
        self.assertIn("ccu/control", control_topics)
        self.assertIn("/j1/txt/1/c/bme680", control_topics)

    def test_get_categories(self):
        """Test getting categories"""
        categories = self.manager.get_categories()
        self.assertIn("CCU", categories)
        self.assertIn("TXT", categories)

    def test_get_sub_categories(self):
        """Test getting sub-categories"""
        ccu_sub_cats = self.manager.get_sub_categories("CCU")
        self.assertIn("Control", ccu_sub_cats)

    def test_get_template_structure(self):
        """Test getting template structure"""
        structure = self.manager.get_template_structure("ccu/control")
        self.assertIsNotNone(structure)
        self.assertIn("command", structure)
        self.assertIn("timestamp", structure)

    def test_get_template_examples(self):
        """Test getting template examples"""
        examples = self.manager.get_template_examples("ccu/control")
        self.assertIsNotNone(examples)
        self.assertGreater(len(examples), 0)
        self.assertEqual(examples[0]["command"], "start")

    def test_get_validation_rules(self):
        """Test getting validation rules"""
        rules = self.manager.get_validation_rules("ccu/control")
        self.assertIsNotNone(rules)
        self.assertGreater(len(rules), 0)
        self.assertIn("gültiger Befehl", rules[0])

    def test_get_statistics(self):
        """Test getting statistics"""
        stats = self.manager.get_statistics()
        self.assertIsNotNone(stats)
        self.assertIn("total_templates", stats)
        self.assertIn("total_categories", stats)
        self.assertIn("category_counts", stats)
        self.assertGreater(stats["total_templates"], 0)

    def test_validate_message(self):
        """Test message validation"""
        # Valid message
        valid_message = {"command": "start", "timestamp": "2025-08-29T10:00:00Z"}
        result = self.manager.validate_message("ccu/control", valid_message)
        self.assertTrue(result["valid"])

        # Invalid message (missing field)
        invalid_message = {
            "command": "start"
            # missing timestamp
        }
        result = self.manager.validate_message("ccu/control", invalid_message)
        self.assertFalse(result["valid"])
        self.assertIn("timestamp", result["errors"][0])

    def test_reload_templates(self):
        """Test template reloading"""
        initial_count = len(self.manager.templates)
        success = self.manager.reload_templates()
        self.assertTrue(success)
        self.assertEqual(len(self.manager.templates), initial_count)

    def test_get_template_file_path(self):
        """Test getting template file path"""
        file_path = self.manager.get_template_file_path("ccu/control")
        self.assertIsNotNone(file_path)
        self.assertIn("control.yml", file_path)


if __name__ == "__main__":
    unittest.main()
