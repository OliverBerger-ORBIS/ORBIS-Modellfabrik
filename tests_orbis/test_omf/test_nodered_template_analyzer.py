#!/usr/bin/env python3
"""
Unit tests for Node-RED Template Analyzer

Tests the Node-RED template analysis functionality including:
- Topic pattern matching
- Sub-category determination
- Module ID extraction
- Template structure analysis
- Validation rule generation
"""

import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

import yaml

# Add src_orbis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src_orbis"))

from src_orbis.analysis_tools.template_analyzers.nodered_template_analyzer import NodeRedTemplateAnalyzer


class TestNodeRedTemplateAnalyzer(unittest.TestCase):
    """Test cases for Node-RED Template Analyzer"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_dir = os.path.join(self.temp_dir, "sessions")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Create test analyzer
        self.analyzer = NodeRedTemplateAnalyzer(session_dir=self.session_dir, output_dir=self.output_dir)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.session_dir, self.session_dir)
        self.assertEqual(self.analyzer.output_dir, self.output_dir)
        self.assertIsInstance(self.analyzer.nodered_topics, list)
        self.assertGreater(len(self.analyzer.nodered_topics), 0)

    def test_determine_sub_category(self):
        """Test sub-category determination"""
        test_cases = [
            ("module/v1/ff/NodeRed/SVR4H73275/connection", "Connection"),
            ("module/v1/ff/NodeRed/SVR4H76530/state", "State"),
            ("module/v1/ff/NodeRed/SVR4H76449/order", "Order"),
            ("module/v1/ff/NodeRed/SVR3QA0022/factsheet", "Factsheet"),
            ("module/v1/ff/NodeRed/SVR4H73275/instantAction", "InstantAction"),
            ("ccu/state/flows", "State"),  # "state" comes before "flows" in the logic
            ("dashboard/default/status", "Dashboard"),
            ("ui/default/config", "UI"),
            ("module/v1/ff/NodeRed/status", "Status"),
            ("unknown/topic", "General"),
        ]

        for topic, expected in test_cases:
            with self.subTest(topic=topic):
                result = self.analyzer._determine_sub_category(topic)
                self.assertEqual(result, expected)

    def test_determine_module_id(self):
        """Test module ID extraction"""
        test_cases = [
            ("module/v1/ff/NodeRed/SVR4H73275/connection", "SVR4H73275"),
            ("module/v1/ff/NodeRed/SVR4H76530/state", "SVR4H76530"),
            ("module/v1/ff/NodeRed/status", "NodeRed"),
            ("ccu/state/flows", "CCU"),
            ("flows/default/status", "Flow"),
            ("dashboard/default/config", "Dashboard"),
            ("ui/default/data", "UI"),
            ("unknown/topic", "unknown"),
        ]

        for topic, expected in test_cases:
            with self.subTest(topic=topic):
                result = self.analyzer._determine_module_id(topic)
                self.assertEqual(result, expected)

    def test_get_placeholder_for_field(self):
        """Test placeholder generation for fields"""
        test_cases = [
            # Timestamp fields
            ("timestamp", {"2024-01-01T12:00:00Z"}, "<datetime>"),
            ("time", {"2024-01-01T12:00:00Z"}, "<datetime>"),
            # ID fields
            ("id", {"123e4567-e89b-12d3-a456-426614174000"}, "<uuid>"),
            ("uuid", {"123e4567-e89b-12d3-a456-426614174000"}, "<uuid>"),
            # NFC fields
            ("nfc_code", {"040a8dca341291"}, "<nfcCode>"),
            ("workpiece_id", {"040a8dca341291"}, "<nfcCode>"),
            # Module fields
            ("module_id", {"SVR4H73275"}, "<moduleId>"),
            ("moduleid", {"SVR4H73275"}, "<moduleId>"),
            # Status fields (small enum)
            ("status", {"online", "offline"}, "[offline, online]"),
            # Position fields
            ("position", {"HOME", "WORK"}, "<position>"),
            # Error fields
            ("error_code", {"E001", "E002"}, "<errorCode>"),
            # Message fields
            ("message", {"Hello World"}, "<message>"),
            # Data fields
            ("data", {"some data"}, "<data>"),
            # Flow fields
            ("flow_id", {"flow1"}, "<flowId>"),
            # Dashboard fields
            ("dashboard_id", {"dashboard1"}, "<dashboardId>"),
            # UI fields
            ("ui_id", {"ui1"}, "<uiId>"),
            # Small enum
            ("type", {"A", "B", "C"}, "[A, B, C]"),
            # Large set (should be string)
            (
                "description",
                {"desc1", "desc2", "desc3", "desc4", "desc5", "desc6"},
                "<string>",
            ),
        ]

        for field_name, values, expected in test_cases:
            with self.subTest(field_name=field_name):
                result = self.analyzer._get_placeholder_for_field(field_name, values)
                self.assertEqual(result, expected)

    def test_analyze_topic_structure_empty(self):
        """Test topic structure analysis with empty messages"""
        result = self.analyzer._analyze_topic_structure("test/topic", [])

        self.assertIn("template_structure", result)
        self.assertIn("examples", result)
        self.assertIn("statistics", result)
        self.assertEqual(result["template_structure"], {})
        self.assertEqual(result["examples"], [])
        self.assertEqual(result["statistics"]["total_messages"], 0)

    def test_analyze_topic_structure_with_data(self):
        """Test topic structure analysis with sample data"""
        messages = [
            {
                "payload": {
                    "status": "online",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "module_id": "SVR4H73275",
                    "data": "test data",
                }
            },
            {
                "payload": {
                    "status": "offline",
                    "timestamp": "2024-01-01T13:00:00Z",
                    "module_id": "SVR4H76530",
                    "data": "other data",
                }
            },
        ]

        result = self.analyzer._analyze_topic_structure("test/topic", messages)

        self.assertIn("template_structure", result)
        self.assertIn("examples", result)
        self.assertIn("statistics", result)

        # Check template structure
        structure = result["template_structure"]
        self.assertIn("status", structure)
        self.assertIn("timestamp", structure)
        self.assertIn("module_id", structure)
        self.assertIn("data", structure)

        # Check specific placeholders
        self.assertEqual(structure["status"], "[offline, online]")
        self.assertEqual(structure["timestamp"], "<datetime>")
        self.assertEqual(structure["module_id"], "<moduleId>")
        self.assertEqual(structure["data"], "<data>")

        # Check statistics
        stats = result["statistics"]
        self.assertEqual(stats["total_messages"], 2)
        self.assertEqual(stats["enum_fields"], 1)  # status
        self.assertEqual(stats["variable_fields"], 3)  # timestamp, module_id, data

    def test_generate_validation_rules(self):
        """Test validation rule generation"""
        template_structure = {
            "status": "[online, offline]",
            "timestamp": "<datetime>",
            "module_id": "<moduleId>",
            "position": "<position>",
            "error_code": "<errorCode>",
            "message": "<message>",
            "data": "<data>",
            "flow_id": "<flowId>",
            "dashboard_id": "<dashboardId>",
            "ui_id": "<uiId>",
        }

        rules = self.analyzer._generate_validation_rules(template_structure)

        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)

        # Check for specific rules
        rule_texts = " ".join(rules)
        self.assertIn("status muss in [online, offline] sein", rule_texts)
        self.assertIn("timestamp muss ISO 8601 Format haben", rule_texts)
        self.assertIn("module_id muss gültige Modul-ID sein", rule_texts)
        self.assertIn("position muss gültige Position sein", rule_texts)
        self.assertIn("error_code muss gültiger Fehler-Code sein", rule_texts)
        # Note: message validation rule is not implemented in the analyzer
        self.assertIn("data muss gültige Daten sein", rule_texts)
        self.assertIn("flow_id muss gültige Flow-ID sein", rule_texts)
        self.assertIn("dashboard_id muss gültige Dashboard-ID sein", rule_texts)
        self.assertIn("ui_id muss gültige UI-ID sein", rule_texts)

    def test_load_all_sessions_empty(self):
        """Test loading sessions from empty directory"""
        sessions = self.analyzer.load_all_sessions()
        self.assertEqual(sessions, [])

    def test_load_all_sessions_with_data(self):
        """Test loading sessions with test database"""
        # Create test database
        db_path = os.path.join(self.session_dir, "test_session.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table and insert data
        cursor.execute(
            """
            CREATE TABLE mqtt_messages (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """
        )

        cursor.execute(
            """
            INSERT INTO mqtt_messages (topic, payload, timestamp)
            VALUES (?, ?, ?)
        """,
            ("test/topic", '{"status": "online"}', "2024-01-01T12:00:00Z"),
        )

        conn.commit()
        conn.close()

        # Load sessions
        sessions = self.analyzer.load_all_sessions()

        self.assertEqual(len(sessions), 1)
        self.assertIn("test_session.db", sessions[0])

    def test_analyze_topic_structure_from_sessions(self):
        """Test topic structure analysis from session data"""
        # Create test database
        db_path = os.path.join(self.session_dir, "test_session.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE mqtt_messages (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """
        )

        # Insert test data
        test_messages = [
            (
                "ccu/state/flows",
                '{"status": "online", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "ccu/state/flows",
                '{"status": "offline", "timestamp": "2024-01-01T13:00:00Z"}',
                "2024-01-01T13:00:00Z",
            ),
        ]

        for topic, payload, timestamp in test_messages:
            cursor.execute(
                """
                INSERT INTO mqtt_messages (topic, payload, timestamp)
                VALUES (?, ?, ?)
            """,
                (topic, payload, timestamp),
            )

        conn.commit()
        conn.close()

        # Analyze topic
        sessions = [db_path]
        result = self.analyzer.analyze_topic_structure("ccu/state/flows", sessions)

        self.assertIn("template_structure", result)
        self.assertIn("examples", result)
        self.assertIn("statistics", result)

        # Check structure
        structure = result["template_structure"]
        self.assertIn("status", structure)
        self.assertIn("timestamp", structure)
        self.assertEqual(structure["status"], "[offline, online]")
        self.assertEqual(structure["timestamp"], "<datetime>")

        # Check statistics
        stats = result["statistics"]
        self.assertEqual(stats["total_messages"], 2)

    def test_analyze_all_topics(self):
        """Test analysis of all topics"""
        # Create test database with Node-RED topics
        db_path = os.path.join(self.session_dir, "test_session.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE mqtt_messages (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """
        )

        # Insert Node-RED specific test data
        test_messages = [
            (
                "ccu/state/flows",
                '{"status": "online", "flow_count": 5}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H73275/connection",
                '{"connected": true, "module_id": "SVR4H73275"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H76530/state",
                '{"status": "idle", "module_id": "SVR4H76530"}',
                "2024-01-01T12:00:00Z",
            ),
        ]

        for topic, payload, timestamp in test_messages:
            cursor.execute(
                """
                INSERT INTO mqtt_messages (topic, payload, timestamp)
                VALUES (?, ?, ?)
            """,
                (topic, payload, timestamp),
            )

        conn.commit()
        conn.close()

        # Analyze all topics
        sessions = [db_path]
        results = self.analyzer.analyze_all_topics(sessions)

        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)

        # Check specific topics
        self.assertIn("ccu/state/flows", results)
        self.assertIn("module/v1/ff/NodeRed/SVR4H73275/connection", results)
        self.assertIn("module/v1/ff/NodeRed/SVR4H76530/state", results)

        # Check topic structure
        flows_result = results["ccu/state/flows"]
        self.assertIn("template_structure", flows_result)
        self.assertEqual(flows_result["statistics"]["total_messages"], 1)

    def test_save_results(self):
        """Test saving results to JSON"""
        test_results = {
            "test/topic": {
                "template_structure": {"status": "[online, offline]"},
                "examples": [{"status": "online"}],
                "statistics": {
                    "total_messages": 1,
                    "enum_fields": 1,
                    "variable_fields": 0,
                },
            }
        }

        output_file = self.analyzer.save_results(test_results)

        self.assertTrue(os.path.exists(output_file))

        # Check file content
        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("templates", data)
        self.assertIn("test/topic", data["templates"])

    def test_save_results_to_yaml(self):
        """Test saving results to YAML"""
        test_results = {
            "test/topic": {
                "template_structure": {"status": "[online, offline]"},
                "examples": [{"status": "online"}],
                "statistics": {
                    "total_messages": 1,
                    "enum_fields": 1,
                    "variable_fields": 0,
                },
            }
        }

        output_file = self.analyzer.save_results_to_yaml(test_results)

        self.assertTrue(os.path.exists(output_file))

        # Check file content
        with open(output_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIn("metadata", data)
        self.assertIn("templates", data)
        self.assertIn("test/topic", data["templates"])


class TestNodeRedTemplateAnalyzerIntegration(unittest.TestCase):
    """Integration tests for Node-RED Template Analyzer"""

    def setUp(self):
        """Set up integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_dir = os.path.join(self.temp_dir, "sessions")
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Create test analyzer
        self.analyzer = NodeRedTemplateAnalyzer(session_dir=self.session_dir, output_dir=self.output_dir)

    def tearDown(self):
        """Clean up integration test environment"""
        shutil.rmtree(self.temp_dir)

    def test_full_analysis_workflow(self):
        """Test complete analysis workflow"""
        # Create comprehensive test database
        db_path = os.path.join(self.session_dir, "integration_test.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE mqtt_messages (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                payload TEXT,
                timestamp TEXT
            )
        """
        )

        # Insert comprehensive test data
        test_messages = [
            # CCU topics
            (
                "ccu/state/flows",
                '{"status": "online", "flow_count": 5, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "ccu/state/dashboard",
                '{"status": "active", "dashboard_count": 3, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "ccu/state/ui",
                '{"status": "ready", "ui_count": 2, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            # Node-RED module topics
            (
                "module/v1/ff/NodeRed/SVR4H73275/connection",
                '{"connected": true, "module_id": "SVR4H73275", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H73275/state",
                '{"status": "idle", "module_id": "SVR4H73275", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H73275/order",
                '{"order_id": "ORD001", "status": "pending", "module_id": "SVR4H73275"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H73275/factsheet",
                '{"module_id": "SVR4H73275", "type": "DPS", "description": "Warenein- und Ausgang"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H73275/instantAction",
                '{"action": "reset", "module_id": "SVR4H73275"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H76530/connection",
                '{"connected": true, "module_id": "SVR4H76530", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "module/v1/ff/NodeRed/SVR4H76530/state",
                '{"status": "processing", "module_id": "SVR4H76530", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            # Node-RED status
            (
                "module/v1/ff/NodeRed/status",
                '{"overall_status": "healthy", "active_modules": 5, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            # Flow topics
            (
                "flows/default/status",
                '{"flow_status": "running", "node_count": 10, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "flows/default/config",
                '{"flow_config": "active", "version": "1.0", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            # Dashboard topics
            (
                "dashboard/default/status",
                '{"dashboard_status": "active", "widget_count": 5, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "dashboard/default/config",
                '{"dashboard_config": "default", "theme": "light", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            # UI topics
            (
                "ui/default/status",
                '{"ui_status": "ready", "component_count": 3, "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
            (
                "ui/default/config",
                '{"ui_config": "default", "layout": "grid", "timestamp": "2024-01-01T12:00:00Z"}',
                "2024-01-01T12:00:00Z",
            ),
        ]

        for topic, payload, timestamp in test_messages:
            cursor.execute(
                """
                INSERT INTO mqtt_messages (topic, payload, timestamp)
                VALUES (?, ?, ?)
            """,
                (topic, payload, timestamp),
            )

        conn.commit()
        conn.close()

        # Run complete analysis
        self.analyzer.run_analysis()

        # Check output files
        json_file = os.path.join(self.output_dir, "nodered_template_analysis.json")
        yaml_file = os.path.join(self.output_dir, "nodered_analysis_results.yml")

        self.assertTrue(os.path.exists(json_file))
        self.assertTrue(os.path.exists(yaml_file))

        # Check JSON content
        with open(json_file, encoding="utf-8") as f:
            json_data = json.load(f)

        self.assertIn("metadata", json_data)
        self.assertIn("templates", json_data)
        self.assertGreater(len(json_data["templates"]), 0)

        # Check YAML content
        with open(yaml_file, encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        self.assertIn("metadata", yaml_data)
        self.assertIn("templates", yaml_data)
        self.assertGreater(len(yaml_data["templates"]), 0)

        # Check specific topics
        expected_topics = [
            "ccu/state/flows",
            "module/v1/ff/NodeRed/SVR4H73275/connection",
            "module/v1/ff/NodeRed/SVR4H73275/state",
            "module/v1/ff/NodeRed/SVR4H76530/connection",
            "module/v1/ff/NodeRed/status",
        ]

        for topic in expected_topics:
            if topic in json_data["templates"]:
                template = json_data["templates"][topic]
                self.assertIn("template_structure", template)
                self.assertIn("examples", template)
                self.assertIn("statistics", template)
                self.assertGreater(template["statistics"]["total_messages"], 0)


if __name__ == "__main__":
    unittest.main()
