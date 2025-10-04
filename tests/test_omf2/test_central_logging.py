#!/usr/bin/env python3
"""
Tests for centralized logging in omf2.common.logger
"""

import unittest
import logging
from collections import deque

from omf2.common.logger import (
    RingBufferHandler,
    create_log_buffer,
    setup_central_log_buffer,
    get_log_buffer_entries
)


class TestCentralLogging(unittest.TestCase):
    """Tests for central logging functionality"""
    
    def setUp(self):
        """Setup test environment"""
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def tearDown(self):
        """Cleanup after tests"""
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def test_create_log_buffer(self):
        """Test: create_log_buffer creates a deque with correct size"""
        buffer = create_log_buffer(maxlen=100)
        
        self.assertIsInstance(buffer, deque)
        self.assertEqual(buffer.maxlen, 100)
        self.assertEqual(len(buffer), 0)
    
    def test_ring_buffer_handler_basic(self):
        """Test: RingBufferHandler adds log messages to buffer"""
        buffer = create_log_buffer(maxlen=10)
        handler = RingBufferHandler(buffer, level=logging.INFO)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        
        # Create logger and add handler
        test_logger = logging.getLogger("test_logger")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        
        # Log messages
        test_logger.info("Test message 1")
        test_logger.warning("Test message 2")
        
        # Check buffer
        self.assertEqual(len(buffer), 2)
        self.assertIn("INFO: Test message 1", buffer[0])
        self.assertIn("WARNING: Test message 2", buffer[1])
    
    def test_setup_central_log_buffer(self):
        """Test: setup_central_log_buffer initializes buffer and handlers"""
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Check buffer
        self.assertIsInstance(log_buffer, deque)
        self.assertEqual(log_buffer.maxlen, 100)
        
        # Check handler
        self.assertIsInstance(ring_handler, RingBufferHandler)
        
        # Check that handler is attached to root logger
        root_logger = logging.getLogger()
        self.assertIn(ring_handler, root_logger.handlers)
        
        # Test that logs are captured
        test_logger = logging.getLogger("omf2.test")
        test_logger.info("Test info message")
        
        # Give it a moment to propagate
        self.assertGreater(len(log_buffer), 0)
    
    def test_get_log_buffer_entries(self):
        """Test: get_log_buffer_entries returns formatted log entries"""
        buffer = create_log_buffer(maxlen=10)
        buffer.append("2025-01-01 12:00:00 [INFO] test: Message 1")
        buffer.append("2025-01-01 12:00:01 [WARNING] test: Message 2")
        buffer.append("2025-01-01 12:00:02 [ERROR] test: Message 3")
        
        # Get all entries
        entries = get_log_buffer_entries(buffer, max_lines=10)
        self.assertIn("Message 1", entries)
        self.assertIn("Message 2", entries)
        self.assertIn("Message 3", entries)
        
        # Get limited entries
        entries_limited = get_log_buffer_entries(buffer, max_lines=2)
        lines = entries_limited.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertIn("Message 2", entries_limited)
        self.assertIn("Message 3", entries_limited)
    
    def test_get_log_buffer_entries_empty(self):
        """Test: get_log_buffer_entries handles empty buffer"""
        buffer = create_log_buffer(maxlen=10)
        entries = get_log_buffer_entries(buffer)
        self.assertEqual(entries, "—")
    
    def test_omf2_logger_propagation(self):
        """Test: omf2 loggers propagate to central buffer"""
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Test various omf2 loggers
        loggers = [
            logging.getLogger("omf2.admin"),
            logging.getLogger("omf2.ui"),
            logging.getLogger("omf2.common")
        ]
        
        for logger in loggers:
            logger.info(f"Test message from {logger.name}")
        
        # Check that messages are in buffer
        self.assertGreaterEqual(len(log_buffer), 3)
        
        buffer_content = "\n".join(log_buffer)
        for logger in loggers:
            self.assertIn(logger.name, buffer_content)


if __name__ == "__main__":
    unittest.main()
