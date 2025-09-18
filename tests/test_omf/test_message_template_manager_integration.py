from pathlib import Path
import os

import shutil
import tempfile
import unittest

import yaml

from omf.tools.message_template_manager import OmfMessageTemplateManager

class TestMessageTemplateManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.temp_dir, "templates", "test"))
        # metadata.yml
        with open(os.path.join(self.temp_dir, "metadata.yml"), "w") as f:
            yaml.dump({"version": "1.0"}, f)
        # categories.yml
        with open(os.path.join(self.temp_dir, "categories.yml"), "w") as f:
            yaml.dump({"categories": {"TEST": {"description": "Integration Test"}}}, f)
        # Topic-Template
        topic_yaml = {
            "metadata": {"category": "TEST", "sub_category": "Integration"},
            "templates": {
                "integration/test": {
                    "structure": {"field1": "<string>", "field2": "<number>"},
                    "examples": [{"field1": "abc", "field2": 123}],
                    "validation_rules": [],
                }
            },
        }
        with open(os.path.join(self.temp_dir, "templates", "test", "integration.yml"), "w") as f:
            yaml.dump(topic_yaml, f)
        self.manager = OmfMessageTemplateManager(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        template = self.manager.get_topic_template("integration/test")
        self.assertIsNotNone(template)
        message = {"field1": "abc", "field2": 123}
        result = self.manager.validate_message("integration/test", message)
        self.assertTrue(result.get("valid", False))
        stats = self.manager.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn("total_templates", stats)

    def test_error_handling(self):
        invalid_message = {"invalid_field": "value"}
        result = self.manager.validate_message("integration/test", invalid_message)
        self.assertFalse(result.get("valid", True))
