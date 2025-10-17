#!/usr/bin/env python3
"""
Unit Tests für CCU Message Monitor Filter Funktionalität

Test-First Development für:
- Filter-Funktionen: _apply_message_filters(), _is_module_topic(), _is_fts_topic()
- Registry Manager Integration: Module-Definitionen, Serial-ID Mapping
- Filter-Logik: Module-Filter, Status-Type Filter, kombinierte Filter
- Session State Management: Filter-Persistenz
"""

import unittest
from unittest.mock import patch, MagicMock
from collections import deque
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the component to test
from omf2.ui.ccu.ccu_message_monitor.ccu_message_monitor_component import (
    _apply_message_filters,
    _is_module_topic,
    _is_fts_topic,
    _get_message_type,
    _get_message_status
)


class TestCCUMessageMonitorFilter(unittest.TestCase):
    """Test-Klasse für CCU Message Monitor Filter-Funktionalität"""

    def setUp(self):
        """Setup vor jedem Test"""
        # Mock message buffers for testing
        self.sample_buffers = {
            "module/v1/ff/SVR3QA0022/state": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"state": "AVAILABLE"}}
            ]),
            "module/v1/ff/SVR3QA0022/connection": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"connected": True}}
            ]),
            "module/v1/ff/SVR4H76449/state": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"state": "BUSY"}}
            ]),
            "module/v1/ff/5iO4/state": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"state": "READY"}}
            ]),
            "ccu/pairing/state": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"modules": []}}
            ])
        }

    def test_is_module_topic_hbw(self):
        """Test: HBW Module Topic Erkennung"""
        topic = "module/v1/ff/SVR3QA0022/state"
        result = _is_module_topic(topic)
        self.assertTrue(result, "HBW Topic sollte als Module Topic erkannt werden")

    def test_is_module_topic_drill(self):
        """Test: DRILL Module Topic Erkennung"""
        topic = "module/v1/ff/SVR4H76449/connection"
        result = _is_module_topic(topic)
        self.assertTrue(result, "DRILL Topic sollte als Module Topic erkannt werden")

    def test_is_module_topic_fts(self):
        """Test: FTS Topic sollte NICHT als Module Topic erkannt werden"""
        topic = "module/v1/ff/5iO4/state"
        result = _is_module_topic(topic)
        self.assertFalse(result, "FTS Topic sollte NICHT als Module Topic erkannt werden")

    def test_is_module_topic_ccu(self):
        """Test: CCU Topic sollte NICHT als Module Topic erkannt werden"""
        topic = "ccu/pairing/state"
        result = _is_module_topic(topic)
        self.assertFalse(result, "CCU Topic sollte NICHT als Module Topic erkannt werden")

    def test_is_fts_topic_fts_serial(self):
        """Test: FTS Topic mit Serial-ID Erkennung"""
        topic = "module/v1/ff/5iO4/state"
        result = _is_fts_topic(topic)
        self.assertTrue(result, "FTS Topic mit Serial-ID sollte als FTS Topic erkannt werden")

    def test_is_fts_topic_fts_keyword(self):
        """Test: FTS Topic mit 'fts' Keyword Erkennung"""
        topic = "fts/v1/status"
        result = _is_fts_topic(topic)
        self.assertTrue(result, "FTS Topic mit 'fts' Keyword sollte als FTS Topic erkannt werden")

    def test_is_fts_topic_module(self):
        """Test: Module Topic sollte NICHT als FTS Topic erkannt werden"""
        topic = "module/v1/ff/SVR3QA0022/state"
        result = _is_fts_topic(topic)
        self.assertFalse(result, "Module Topic sollte NICHT als FTS Topic erkannt werden")

    def test_apply_message_filters_no_filters(self):
        """Test: Keine Filter angewendet - alle Messages zurückgeben"""
        with patch('streamlit.session_state', {}):
            result = _apply_message_filters(self.sample_buffers, None)
            self.assertEqual(len(result), len(self.sample_buffers), "Alle Buffers sollten zurückgegeben werden")
            self.assertEqual(result, self.sample_buffers, "Result sollte identisch mit Input sein")

    def test_apply_message_filters_all_modules(self):
        """Test: 'All Modules' Filter"""
        with patch('streamlit.session_state', {
            'ccu_filter_modules': ['all_modules'],
            'ccu_filter_connection': True,
            'ccu_filter_module': True,
            'ccu_filter_agv_fts': True
        }):
            result = _apply_message_filters(self.sample_buffers, None)
            
            # Should include HBW and DRILL topics, but not FTS or CCU
            expected_topics = [
                "module/v1/ff/SVR3QA0022/state",
                "module/v1/ff/SVR3QA0022/connection", 
                "module/v1/ff/SVR4H76449/state"
            ]
            
            for topic in expected_topics:
                self.assertIn(topic, result, f"Module Topic {topic} sollte im Filter-Result sein")
            
            # FTS and CCU topics should not be included
            self.assertNotIn("module/v1/ff/5iO4/state", result, "FTS Topic sollte nicht im Filter-Result sein")
            self.assertNotIn("ccu/pairing/state", result, "CCU Topic sollte nicht im Filter-Result sein")

    def test_apply_message_filters_all_fts(self):
        """Test: 'All FTS' Filter"""
        with patch('streamlit.session_state', {
            'ccu_filter_modules': ['all_fts'],
            'ccu_filter_connection': True,
            'ccu_filter_module': True,
            'ccu_filter_agv_fts': True
        }):
            result = _apply_message_filters(self.sample_buffers, None)
            
            # Should include FTS topic, but not module or CCU topics
            self.assertIn("module/v1/ff/5iO4/state", result, "FTS Topic sollte im Filter-Result sein")
            
            # Module and CCU topics should not be included
            self.assertNotIn("module/v1/ff/SVR3QA0022/state", result, "Module Topic sollte nicht im Filter-Result sein")
            self.assertNotIn("ccu/pairing/state", result, "CCU Topic sollte nicht im Filter-Result sein")

    def test_apply_message_filters_specific_module(self):
        """Test: Spezifischer Module Filter (HBW)"""
        with patch('streamlit.session_state', {
            'ccu_filter_modules': ['module_SVR3QA0022'],
            'ccu_filter_connection': True,
            'ccu_filter_module': True,
            'ccu_filter_agv_fts': True
        }):
            result = _apply_message_filters(self.sample_buffers, None)
            
            # Should include only HBW topics
            hbw_topics = [
                "module/v1/ff/SVR3QA0022/state",
                "module/v1/ff/SVR3QA0022/connection"
            ]
            
            for topic in hbw_topics:
                self.assertIn(topic, result, f"HBW Topic {topic} sollte im Filter-Result sein")
            
            # Other topics should not be included
            self.assertNotIn("module/v1/ff/SVR4H76449/state", result, "DRILL Topic sollte nicht im Filter-Result sein")
            self.assertNotIn("module/v1/ff/5iO4/state", result, "FTS Topic sollte nicht im Filter-Result sein")

    def test_apply_message_filters_connection_status_only(self):
        """Test: Nur Connection Status Filter"""
        with patch('streamlit.session_state', {
            'ccu_filter_modules': [],
            'ccu_filter_connection': True,
            'ccu_filter_module': False,
            'ccu_filter_agv_fts': False
        }):
            result = _apply_message_filters(self.sample_buffers, None)
            
            # Should include only connection topics
            self.assertIn("module/v1/ff/SVR3QA0022/connection", result, "Connection Topic sollte im Filter-Result sein")
            
            # Other topics should not be included
            self.assertNotIn("module/v1/ff/SVR3QA0022/state", result, "State Topic sollte nicht im Filter-Result sein")
            self.assertNotIn("module/v1/ff/SVR4H76449/state", result, "State Topic sollte nicht im Filter-Result sein")

    def test_apply_message_filters_combined_filters(self):
        """Test: Kombinierte Filter (Module + Status-Type)"""
        with patch('streamlit.session_state', {
            'ccu_filter_modules': ['module_SVR3QA0022'],
            'ccu_filter_connection': False,
            'ccu_filter_module': True,
            'ccu_filter_agv_fts': False
        }):
            result = _apply_message_filters(self.sample_buffers, None)
            
            # Should include only HBW state topic (module filter + module status filter)
            self.assertIn("module/v1/ff/SVR3QA0022/state", result, "HBW State Topic sollte im Filter-Result sein")
            
            # Connection topic should not be included (connection status filter is False)
            self.assertNotIn("module/v1/ff/SVR3QA0022/connection", result, "Connection Topic sollte nicht im Filter-Result sein")

    def test_get_message_type_state(self):
        """Test: Message Type Erkennung - State"""
        topic = "module/v1/ff/SVR3QA0022/state"
        result = _get_message_type(topic)
        self.assertEqual(result, "🏗️ Module", "Module State Topic sollte als '🏗️ Module' erkannt werden")

    def test_get_message_type_connection(self):
        """Test: Message Type Erkennung - Connection"""
        topic = "module/v1/ff/SVR3QA0022/connection"
        result = _get_message_type(topic)
        self.assertEqual(result, "🔌 Connection", "Connection Topic sollte als '🔌 Connection' erkannt werden")

    def test_get_message_type_factsheet(self):
        """Test: Message Type Erkennung - Factsheet"""
        topic = "module/v1/ff/SVR3QA0022/factsheet"
        result = _get_message_type(topic)
        self.assertEqual(result, "📄 Factsheet", "Factsheet Topic sollte als '📄 Factsheet' erkannt werden")

    def test_get_message_type_ccu(self):
        """Test: Message Type Erkennung - CCU"""
        topic = "ccu/pairing/state"
        result = _get_message_type(topic)
        self.assertEqual(result, "🏭 CCU", "CCU Topic sollte als '🏭 CCU' erkannt werden")

    def test_get_message_type_fts(self):
        """Test: Message Type Erkennung - FTS"""
        topic = "module/v1/ff/5iO4/state"
        result = _get_message_type(topic)
        self.assertEqual(result, "🚗 FTS", "FTS Topic sollte als '🚗 FTS' erkannt werden")

    def test_get_message_status_connected(self):
        """Test: Message Status Erkennung - Connected"""
        message = {"connected": True}
        result = _get_message_status(message)
        self.assertEqual(result, "🔌 Connected", "Connected Message sollte als '🔌 Connected' erkannt werden")

    def test_get_message_status_available(self):
        """Test: Message Status Erkennung - Available"""
        message = {"available": "AVAILABLE"}
        result = _get_message_status(message)
        self.assertEqual(result, "🏗️ Available", "Available Message sollte als '🏗️ Available' erkannt werden")

    def test_get_message_status_busy(self):
        """Test: Message Status Erkennung - Busy"""
        message = {"available": "BUSY"}
        result = _get_message_status(message)
        self.assertEqual(result, "🏗️ Busy", "Busy Message sollte als '🏗️ Busy' erkannt werden")

    def test_get_message_status_error(self):
        """Test: Message Status Erkennung - Error"""
        message = {"available": "ERROR"}
        result = _get_message_status(message)
        self.assertEqual(result, "🏗️ Error", "Error Message sollte als '🏗️ Error' erkannt werden")
    
    def test_get_message_status_fts_active(self):
        """Test: Message Status Erkennung - FTS Active"""
        message = {"orderId": "test-order", "nodeStates": [], "actionStates": []}
        result = _get_message_status(message)
        self.assertEqual(result, "🚗 FTS Active", "FTS Active Message sollte als '🚗 FTS Active' erkannt werden")
    
    def test_get_message_status_fts_idle(self):
        """Test: Message Status Erkennung - FTS Idle"""
        message = {"orderId": None, "nodeStates": [], "actionStates": []}
        result = _get_message_status(message)
        self.assertEqual(result, "🚗 FTS Idle", "FTS Idle Message sollte als '🚗 FTS Idle' erkannt werden")

    def test_apply_message_filters_error_handling(self):
        """Test: Error Handling in Filter-Funktion"""
        with patch('streamlit.session_state', {}):
            # Test with invalid input
            result = _apply_message_filters(None, None)
            self.assertEqual(result, None, "Bei None Input sollte None zurückgegeben werden")
            
            # Test with empty dict
            result = _apply_message_filters({}, None)
            self.assertEqual(result, {}, "Bei leerem Dict sollte leeres Dict zurückgegeben werden")


class TestCCUMessageMonitorFilterIntegration(unittest.TestCase):
    """Integration Tests für CCU Message Monitor Filter mit Registry Manager"""

    def setUp(self):
        """Setup vor jedem Test"""
        self.sample_buffers = {
            "module/v1/ff/SVR3QA0022/state": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"state": "AVAILABLE"}}
            ]),
            "module/v1/ff/5iO4/state": deque([
                {"mqtt_timestamp": 1234567890, "payload": {"state": "READY"}}
            ])
        }

    @patch('omf2.registry.manager.registry_manager.RegistryManager')
    def test_registry_manager_integration(self, mock_registry_manager):
        """Test: Registry Manager Integration für Module-Definitionen"""
        # Mock Registry Manager - return dict format
        mock_modules = {
            "SVR3QA0022": {"id": "SVR3QA0022", "name": "HBW", "type": "Storage", "icon": "🏬"},
            "5iO4": {"id": "5iO4", "name": "FTS", "type": "Transport", "icon": "🚗"}
        }
        mock_registry_manager.return_value.get_modules.return_value = mock_modules
        
        # Test module topic detection
        hbw_topic = "module/v1/ff/SVR3QA0022/state"
        fts_topic = "module/v1/ff/5iO4/state"
        
        hbw_result = _is_module_topic(hbw_topic)
        fts_result = _is_module_topic(fts_topic)
        
        self.assertTrue(hbw_result, "HBW Topic sollte als Module Topic erkannt werden")
        self.assertFalse(fts_result, "FTS Topic sollte NICHT als Module Topic erkannt werden")

    def test_filter_performance(self):
        """Test: Filter Performance mit vielen Messages"""
        # Create large buffer for performance testing with real module IDs
        large_buffers = {}
        for i in range(100):
            topic = f"module/v1/ff/SVR{i:06d}/state"
            large_buffers[topic] = deque([
                {"mqtt_timestamp": 1234567890, "payload": {"state": "AVAILABLE"}}
            ])
        
        with patch('streamlit.session_state', {
            'ccu_filter_modules': [],  # No specific module filter
            'ccu_filter_connection': True,
            'ccu_filter_module': True,
            'ccu_filter_agv_fts': True
        }):
            import time
            start_time = time.time()
            result = _apply_message_filters(large_buffers, None)
            end_time = time.time()
            
            # Performance should be reasonable (less than 1 second for 100 topics)
            self.assertLess(end_time - start_time, 1.0, "Filter sollte in weniger als 1 Sekunde ausgeführt werden")
            # With no filters, all buffers should be returned
            self.assertEqual(len(result), len(large_buffers), "Alle Buffers sollten zurückgegeben werden")


if __name__ == '__main__':
    unittest.main()
