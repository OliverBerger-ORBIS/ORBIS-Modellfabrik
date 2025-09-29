#!/usr/bin/env python3
"""
Tests für MessageTemplates Singleton
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from omf2.common.message_templates import MessageTemplates, get_message_templates


class TestMessageTemplates(unittest.TestCase):
    """Test-Klasse für MessageTemplates Singleton"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Temporäres Registry-Verzeichnis erstellen
        self.temp_dir = tempfile.mkdtemp()
        self.registry_path = Path(self.temp_dir) / "registry" / "model" / "v2"
        self.registry_path.mkdir(parents=True, exist_ok=True)
        
        # Test-Templates erstellen
        self._create_test_templates()
        self._create_test_mappings()
        self._create_test_topics()
        
        # Singleton zurücksetzen
        MessageTemplates._instance = None
        MessageTemplates._initialized = False
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        shutil.rmtree(self.temp_dir)
        MessageTemplates._instance = None
        MessageTemplates._initialized = False
    
    def _create_test_templates(self):
        """Erstellt Test-Templates"""
        templates_dir = self.registry_path / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Module State Template
        module_state_template = {
            "metadata": {
                "version": "2.0.0",
                "description": "Test Module State Template"
            },
            "template": {
                "name": "module.state",
                "category": "MODULE",
                "sub_category": "State",
                "schema": {
                    "type": "object",
                    "properties": {
                        "module_id": {"type": "string"},
                        "state": {"type": "string", "enum": ["idle", "processing", "error"]},
                        "timestamp": {"type": "string", "format": "date-time"}
                    },
                    "required": ["module_id", "state", "timestamp"]
                },
                "example": {
                    "module_id": "SVR3QA0022",
                    "state": "idle",
                    "timestamp": "2025-09-28T16:24:55Z"
                }
            }
        }
        
        with open(templates_dir / "module.state.yml", 'w') as f:
            import yaml
            yaml.dump(module_state_template, f)
    
    def _create_test_mappings(self):
        """Erstellt Test-Mappings"""
        mappings_dir = self.registry_path / "mappings"
        mappings_dir.mkdir(exist_ok=True)
        
        mappings = {
            "metadata": {
                "version": "2.0.0",
                "description": "Test Topic-Template Mappings"
            },
            "mappings": [
                {
                    "topic": "module/v1/ff/SVR3QA0022/state",
                    "template": "module.state",
                    "direction": "inbound"
                },
                {
                    "pattern": "module/v1/ff/{module_id}/state",
                    "template": "module.state",
                    "direction": "inbound",
                    "vars": {"module_id": "<serial>"}
                }
            ]
        }
        
        with open(mappings_dir / "topic_templates.yml", 'w') as f:
            import yaml
            yaml.dump(mappings, f)
    
    def _create_test_topics(self):
        """Erstellt Test-Topics"""
        topics_dir = self.registry_path / "topics"
        topics_dir.mkdir(exist_ok=True)
        
        module_topics = {
            "metadata": {
                "version": "2.0.0",
                "description": "Test Module Topics"
            },
            "module_topics": [
                {
                    "topic": "module/v1/ff/SVR3QA0022/state",
                    "qos": 2,
                    "retain": True
                }
            ]
        }
        
        with open(topics_dir / "module.yml", 'w') as f:
            import yaml
            yaml.dump(module_topics, f)
    
    def test_singleton_pattern(self):
        """Test: Singleton Pattern funktioniert"""
        # Erste Instanz
        instance1 = MessageTemplates(str(self.registry_path))
        
        # Zweite Instanz (sollte dieselbe sein)
        instance2 = MessageTemplates(str(self.registry_path))
        
        self.assertIs(instance1, instance2)
        self.assertTrue(MessageTemplates._initialized)
    
    def test_factory_function(self):
        """Test: Factory-Funktion funktioniert"""
        instance1 = get_message_templates(str(self.registry_path))
        instance2 = get_message_templates(str(self.registry_path))
        
        self.assertIs(instance1, instance2)
        self.assertIsInstance(instance1, MessageTemplates)
    
    def test_registry_loading(self):
        """Test: Registry wird korrekt geladen"""
        templates = MessageTemplates(str(self.registry_path))
        
        # Templates geladen
        self.assertIn("module.state", templates.templates)
        
        # Mappings geladen
        self.assertIn("mappings", templates.mappings)
        self.assertEqual(len(templates.mappings["mappings"]), 2)
        
        # Topics geladen
        self.assertIn("module", templates.topics)
    
    def test_get_template_for_topic_exact_match(self):
        """Test: Exact Match für Topic"""
        templates = MessageTemplates(str(self.registry_path))
        
        template_key = templates.get_template_for_topic("module/v1/ff/SVR3QA0022/state")
        self.assertEqual(template_key, "module.state")
    
    def test_get_template_for_topic_pattern_match(self):
        """Test: Pattern Match für Topic"""
        templates = MessageTemplates(str(self.registry_path))
        
        template_key = templates.get_template_for_topic("module/v1/ff/SVR4H73275/state")
        self.assertEqual(template_key, "module.state")
    
    def test_get_template_for_topic_not_found(self):
        """Test: Topic nicht gefunden"""
        templates = MessageTemplates(str(self.registry_path))
        
        template_key = templates.get_template_for_topic("unknown/topic")
        self.assertIsNone(template_key)
    
    def test_get_template(self):
        """Test: Template nach Key laden"""
        templates = MessageTemplates(str(self.registry_path))
        
        template = templates.get_template("module.state")
        self.assertIsNotNone(template)
        self.assertEqual(template["template"]["name"], "module.state")
        
        # Nicht existierendes Template
        template = templates.get_template("nonexistent")
        self.assertIsNone(template)
    
    def test_render_message(self):
        """Test: Message rendern"""
        templates = MessageTemplates(str(self.registry_path))
        
        params = {
            "module_id": "SVR3QA0022",
            "state": "idle",
            "timestamp": "2025-09-28T16:24:55Z"
        }
        
        message = templates.render_message("module/v1/ff/SVR3QA0022/state", params)
        
        self.assertIsNotNone(message)
        self.assertEqual(message["module_id"], "SVR3QA0022")
        self.assertEqual(message["state"], "idle")
        self.assertEqual(message["timestamp"], "2025-09-28T16:24:55Z")
    
    def test_render_message_invalid_topic(self):
        """Test: Message rendern mit ungültigem Topic"""
        templates = MessageTemplates(str(self.registry_path))
        
        message = templates.render_message("invalid/topic", {})
        self.assertIsNone(message)
    
    def test_validate_message_valid(self):
        """Test: Gültige Message validieren"""
        templates = MessageTemplates(str(self.registry_path))
        
        message = {
            "module_id": "SVR3QA0022",
            "state": "idle",
            "timestamp": "2025-09-28T16:24:55Z"
        }
        
        result = templates.validate_message("module/v1/ff/SVR3QA0022/state", message)
        self.assertEqual(len(result["errors"]), 0)
    
    def test_validate_message_invalid(self):
        """Test: Ungültige Message validieren"""
        templates = MessageTemplates(str(self.registry_path))
        
        message = {
            "module_id": "SVR3QA0022",
            "state": "invalid_state",  # Nicht in enum
            "timestamp": "invalid_timestamp"  # Falsches Format
        }
        
        result = templates.validate_message("module/v1/ff/SVR3QA0022/state", message)
        self.assertGreater(len(result["errors"]), 0)
    
    def test_validate_message_missing_required(self):
        """Test: Message mit fehlenden required Fields"""
        templates = MessageTemplates(str(self.registry_path))
        
        message = {
            "module_id": "SVR3QA0022"
            # state und timestamp fehlen
        }
        
        result = templates.validate_message("module/v1/ff/SVR3QA0022/state", message)
        self.assertGreater(len(result["errors"]), 0)
    
    def test_log_message(self):
        """Test: Message loggen"""
        templates = MessageTemplates(str(self.registry_path))
        
        with patch('omf2.common.message_templates.logger') as mock_logger:
            templates.log_message("test/topic", {"test": "data"}, "SEND")
            mock_logger.info.assert_called_once()
    
    def test_get_topic_config(self):
        """Test: QoS/Retain für Topic abrufen"""
        templates = MessageTemplates(str(self.registry_path))
        
        qos, retain = templates.get_topic_config("module/v1/ff/SVR3QA0022/state")
        self.assertEqual(qos, 2)
        self.assertEqual(retain, True)
    
    def test_get_topic_config_not_found(self):
        """Test: QoS/Retain für unbekanntes Topic"""
        templates = MessageTemplates(str(self.registry_path))
        
        qos, retain = templates.get_topic_config("unknown/topic")
        self.assertEqual(qos, 1)  # Default
        self.assertEqual(retain, False)  # Default
    
    def test_get_all_templates(self):
        """Test: Alle Templates abrufen"""
        templates = MessageTemplates(str(self.registry_path))
        
        all_templates = templates.get_all_templates()
        self.assertIn("module.state", all_templates)
    
    def test_get_all_mappings(self):
        """Test: Alle Mappings abrufen"""
        templates = MessageTemplates(str(self.registry_path))
        
        all_mappings = templates.get_all_mappings()
        self.assertIn("mappings", all_mappings)


if __name__ == '__main__':
    unittest.main()
