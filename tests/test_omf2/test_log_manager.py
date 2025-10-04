#!/usr/bin/env python3
"""
Tests for LogManager in omf2.admin.log_manager
"""

import unittest
import logging
from datetime import datetime, timedelta
from collections import deque
from pathlib import Path
import tempfile
import json

from omf2.admin.log_manager import LogManager, LogEntry, LogLevel


class TestLogManager(unittest.TestCase):
    """Tests for LogManager business logic"""
    
    def setUp(self):
        """Setup test environment"""
        # Create temporary log directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test log buffer
        self.log_buffer = deque(maxlen=100)
        
        # Add some test log entries
        self.log_buffer.append("2025-01-01 12:00:00 [INFO] omf2.admin: Test info message")
        self.log_buffer.append("2025-01-01 12:00:01 [WARNING] omf2.ui: Test warning message")
        self.log_buffer.append("2025-01-01 12:00:02 [ERROR] omf2.ccu: Test error message")
        self.log_buffer.append("2025-01-01 12:00:03 [DEBUG] omf2.common: Test debug message")
        
        # Create LogManager with test buffer
        self.log_manager = LogManager(
            log_buffer=self.log_buffer,
            logs_dir=Path(self.temp_dir)
        )
    
    def tearDown(self):
        """Cleanup after tests"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_manager_initialization(self):
        """Test: LogManager initializes correctly"""
        self.assertIsNotNone(self.log_manager)
        self.assertEqual(self.log_manager.log_buffer, self.log_buffer)
        self.assertTrue(self.log_manager.logs_dir.exists())
    
    def test_set_log_buffer(self):
        """Test: set_log_buffer updates buffer"""
        new_buffer = deque(maxlen=50)
        self.log_manager.set_log_buffer(new_buffer)
        self.assertEqual(self.log_manager.log_buffer, new_buffer)
    
    def test_get_logs_all(self):
        """Test: get_logs returns all logs"""
        logs = self.log_manager.get_logs(limit=100)
        self.assertEqual(len(logs), 4)
    
    def test_get_logs_with_level_filter(self):
        """Test: get_logs filters by log level"""
        logs = self.log_manager.get_logs(level=LogLevel.INFO)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].level, LogLevel.INFO)
    
    def test_get_logs_with_component_filter(self):
        """Test: get_logs filters by component"""
        logs = self.log_manager.get_logs(component="omf2.ui")
        self.assertEqual(len(logs), 1)
        self.assertIn("omf2.ui", logs[0].component)
    
    def test_get_logs_with_limit(self):
        """Test: get_logs respects limit"""
        logs = self.log_manager.get_logs(limit=2)
        self.assertEqual(len(logs), 2)
    
    def test_get_error_logs(self):
        """Test: get_error_logs returns only errors and critical"""
        logs = self.log_manager.get_error_logs()
        self.assertGreater(len(logs), 0)
        for log in logs:
            self.assertIn(log.level, [LogLevel.ERROR, LogLevel.CRITICAL])
    
    def test_search_logs(self):
        """Test: search_logs finds matching entries"""
        results = self.log_manager.search_logs("warning")
        self.assertEqual(len(results), 1)
        self.assertIn("warning", results[0].message.lower())
    
    def test_search_logs_no_match(self):
        """Test: search_logs returns empty for no match"""
        results = self.log_manager.search_logs("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_get_log_statistics(self):
        """Test: get_log_statistics returns correct stats"""
        stats = self.log_manager.get_log_statistics()
        
        self.assertIn('total_entries', stats)
        self.assertIn('level_distribution', stats)
        self.assertIn('component_distribution', stats)
        self.assertEqual(stats['total_entries'], 4)
    
    def test_export_logs(self):
        """Test: export_logs creates JSON file"""
        export_path = Path(self.temp_dir) / "test_export.json"
        
        success = self.log_manager.export_logs(export_path)
        self.assertTrue(success)
        self.assertTrue(export_path.exists())
        
        # Verify exported content
        with open(export_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('entries', data)
        self.assertIn('exported_at', data)
        self.assertGreater(len(data['entries']), 0)
    
    def test_clear_logs(self):
        """Test: clear_logs removes all entries"""
        self.assertEqual(len(self.log_buffer), 4)
        
        self.log_manager.clear_logs()
        
        self.assertEqual(len(self.log_buffer), 0)
    
    def test_log_entry_from_log_line(self):
        """Test: LogEntry.from_log_line parses correctly"""
        log_line = "2025-01-01 12:00:00 [INFO] omf2.test: Test message"
        entry = LogEntry.from_log_line(log_line)
        
        self.assertIsNotNone(entry)
        self.assertEqual(entry.level, LogLevel.INFO)
        self.assertEqual(entry.component, "omf2.test")
        self.assertEqual(entry.message, "Test message")
    
    def test_log_entry_from_invalid_log_line(self):
        """Test: LogEntry.from_log_line handles invalid format"""
        log_line = "Invalid log format"
        entry = LogEntry.from_log_line(log_line)
        
        self.assertIsNone(entry)
    
    def test_log_entry_to_dict(self):
        """Test: LogEntry.to_dict converts correctly"""
        timestamp = datetime.now()
        entry = LogEntry(
            timestamp=timestamp,
            level=LogLevel.INFO,
            component="test",
            message="Test message"
        )
        
        entry_dict = entry.to_dict()
        
        self.assertEqual(entry_dict['level'], 'INFO')
        self.assertEqual(entry_dict['component'], 'test')
        self.assertEqual(entry_dict['message'], 'Test message')
        self.assertIn('timestamp', entry_dict)


if __name__ == "__main__":
    unittest.main()
