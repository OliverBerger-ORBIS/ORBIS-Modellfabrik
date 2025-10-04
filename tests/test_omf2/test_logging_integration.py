#!/usr/bin/env python3
"""
Integration test for central logging system
Verifies that logger.info() calls appear in the System Logs
"""

import unittest
import logging
from collections import deque

from omf2.common.logger import setup_central_log_buffer, get_logger
from omf2.admin.log_manager import get_log_manager, LogLevel


class TestLoggingIntegration(unittest.TestCase):
    """Integration tests for central logging system"""
    
    def setUp(self):
        """Setup test environment"""
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Reset log manager singleton
        import omf2.admin.log_manager as log_manager_module
        log_manager_module._log_manager = None
    
    def tearDown(self):
        """Cleanup after tests"""
        # Clear all handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    def test_logger_info_appears_in_buffer(self):
        """Test: logger.info() calls appear in central buffer"""
        # Setup central log buffer
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Get logger and log messages
        logger = get_logger("omf2.test")
        logger.info("Test info message 1")
        logger.warning("Test warning message 2")
        logger.error("Test error message 3")
        
        # Verify messages are in buffer
        buffer_content = "\n".join(log_buffer)
        self.assertIn("Test info message 1", buffer_content)
        self.assertIn("Test warning message 2", buffer_content)
        self.assertIn("Test error message 3", buffer_content)
        self.assertIn("omf2.test", buffer_content)
    
    def test_log_manager_receives_logger_calls(self):
        """Test: LogManager can access logs from logger.info() calls"""
        # Setup central log buffer
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Initialize LogManager with buffer
        log_manager = get_log_manager(log_buffer=log_buffer)
        
        # Log messages through standard logger
        logger1 = get_logger("omf2.admin")
        logger1.info("Admin info message")
        
        logger2 = get_logger("omf2.ui")
        logger2.warning("UI warning message")
        
        logger3 = get_logger("omf2.ccu")
        logger3.error("CCU error message")
        
        # Get logs from LogManager
        logs = log_manager.get_logs(limit=100)
        
        # Verify logs are accessible
        self.assertGreater(len(logs), 0)
        
        # Verify specific messages are found
        messages = [log.message for log in logs]
        self.assertTrue(any("Admin info message" in msg for msg in messages))
        self.assertTrue(any("UI warning message" in msg for msg in messages))
        self.assertTrue(any("CCU error message" in msg for msg in messages))
    
    def test_log_level_filtering_works(self):
        """Test: Log level filtering works correctly"""
        # Setup central log buffer
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Initialize LogManager
        log_manager = get_log_manager(log_buffer=log_buffer)
        
        # Log messages at different levels
        logger = get_logger("omf2.test")
        logger.debug("Debug message")  # Should not appear (below INFO)
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Get all logs
        all_logs = log_manager.get_logs(limit=100)
        messages = [log.message for log in all_logs]
        
        # Debug should not appear (log level is INFO)
        self.assertFalse(any("Debug message" in msg for msg in messages))
        
        # Others should appear
        self.assertTrue(any("Info message" in msg for msg in messages))
        self.assertTrue(any("Warning message" in msg for msg in messages))
        self.assertTrue(any("Error message" in msg for msg in messages))
    
    def test_component_filtering_works(self):
        """Test: Component filtering works correctly"""
        # Setup central log buffer
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Initialize LogManager
        log_manager = get_log_manager(log_buffer=log_buffer)
        
        # Log messages from different components
        logger1 = get_logger("omf2.admin")
        logger1.info("Admin message")
        
        logger2 = get_logger("omf2.ui")
        logger2.info("UI message")
        
        logger3 = get_logger("omf2.ccu")
        logger3.info("CCU message")
        
        # Filter by component
        admin_logs = log_manager.get_logs(component="omf2.admin", limit=100)
        
        # Verify filtering
        for log in admin_logs:
            self.assertIn("omf2.admin", log.component)
    
    def test_search_functionality_works(self):
        """Test: Search functionality works correctly"""
        # Setup central log buffer
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Initialize LogManager
        log_manager = get_log_manager(log_buffer=log_buffer)
        
        # Log messages with searchable content
        logger = get_logger("omf2.test")
        logger.info("Message about MQTT connection")
        logger.info("Message about database query")
        logger.info("Another MQTT related message")
        
        # Search for "MQTT"
        mqtt_logs = log_manager.search_logs("MQTT", limit=100)
        
        # Verify search results
        self.assertEqual(len(mqtt_logs), 2)
        for log in mqtt_logs:
            self.assertIn("MQTT", log.message)
    
    def test_multiple_omf2_loggers_propagate(self):
        """Test: All omf2 loggers propagate to central buffer"""
        # Setup central log buffer
        log_buffer, ring_handler = setup_central_log_buffer(
            buffer_size=100,
            log_level=logging.INFO
        )
        
        # Test all expected omf2 loggers
        logger_names = [
            "omf2.dashboard",
            "omf2.admin",
            "omf2.ui",
            "omf2.common",
            "omf2.ccu",
            "omf2.nodered",
            "omf2.factory",
            "omf2.registry"
        ]
        
        # Log from each logger
        for logger_name in logger_names:
            logger = get_logger(logger_name)
            logger.info(f"Test from {logger_name}")
        
        # Verify all messages are in buffer
        buffer_content = "\n".join(log_buffer)
        for logger_name in logger_names:
            self.assertIn(logger_name, buffer_content)


if __name__ == "__main__":
    unittest.main()
