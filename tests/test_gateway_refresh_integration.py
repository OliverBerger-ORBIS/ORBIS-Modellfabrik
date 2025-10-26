#!/usr/bin/env python3
"""
Integration tests for Gateway → Redis refresh flow

Tests that the gateway correctly triggers UI refresh events
when processing MQTT messages.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock


@pytest.fixture
def mock_redis():
    """Create a fake Redis client for testing"""
    try:
        import fakeredis
        return fakeredis.FakeRedis(decode_responses=True)
    except ImportError:
        pytest.skip("fakeredis not available")


@pytest.fixture
def mock_gateway():
    """Create a mock CCU Gateway for testing"""
    from omf2.ccu.ccu_gateway import CcuGateway
    
    # Mock dependencies
    mock_mqtt_client = MagicMock()
    
    with patch('omf2.ccu.ccu_gateway.get_registry_manager') as mock_reg_mgr, \
         patch('omf2.ccu.ccu_gateway.get_ccu_message_manager') as mock_msg_mgr, \
         patch('omf2.ccu.ccu_gateway.get_ccu_topic_manager') as mock_topic_mgr, \
         patch('omf2.ccu.ccu_gateway.get_monitor_manager') as mock_mon_mgr:
        
        # Configure mock registry manager to return test config
        mock_registry = MagicMock()
        mock_registry.get_gateway_config.return_value = {
            'routing_hints': {},
            'refresh_triggers': {
                'order_updates': [
                    'ccu/order/active',
                    'ccu/order/completed',
                ],
                'module_updates': [
                    'module/v1/ff/*/state',
                ],
                'sensor_updates': [
                    '/j1/txt/1/i/bme680',
                ],
            }
        }
        mock_reg_mgr.return_value = mock_registry
        
        # Create gateway
        gateway = CcuGateway(mqtt_client=mock_mqtt_client)
        
        yield gateway


def test_gateway_triggers_refresh_on_order_message(mock_gateway, mock_redis):
    """Test that gateway triggers refresh when order message is processed"""
    with patch('omf2.backend.refresh._get_redis_client', return_value=mock_redis):
        # Simulate order message
        topic = 'ccu/order/active'
        message = {'orderId': '12345', 'status': 'ACTIVE'}
        
        # Process message (will trigger routing and refresh)
        with patch.object(mock_gateway, '_get_order_manager') as mock_order_mgr:
            mock_order_mgr.return_value = MagicMock()
            
            result = mock_gateway._route_ccu_message(topic, message)
            assert result is True
        
        # Check that refresh was triggered
        import omf2.backend.refresh as refresh
        timestamp = refresh.get_last_refresh('order_updates')
        assert timestamp is not None


def test_gateway_triggers_refresh_on_module_message(mock_gateway, mock_redis):
    """Test that gateway triggers refresh when module message is processed"""
    with patch('omf2.backend.refresh._get_redis_client', return_value=mock_redis):
        # Simulate module message with wildcard pattern
        topic = 'module/v1/ff/SVR3QA0022/state'
        message = {'moduleId': 'SVR3QA0022', 'state': 'IDLE'}
        
        # Process message
        with patch.object(mock_gateway, '_get_module_manager') as mock_module_mgr:
            mock_module_mgr.return_value = MagicMock()
            
            result = mock_gateway._route_ccu_message(topic, message)
            assert result is True
        
        # Check that refresh was triggered
        import omf2.backend.refresh as refresh
        timestamp = refresh.get_last_refresh('module_updates')
        assert timestamp is not None


def test_gateway_wildcard_pattern_matching(mock_gateway):
    """Test that gateway correctly matches wildcard patterns"""
    # Test exact match
    assert mock_gateway._topic_matches_pattern('ccu/order/active', 'ccu/order/active')
    
    # Test wildcard at end
    assert mock_gateway._topic_matches_pattern('module/v1/ff/SVR3QA0022/state', 'module/v1/ff/*/state')
    assert mock_gateway._topic_matches_pattern('module/v1/ff/ABC123/state', 'module/v1/ff/*/state')
    
    # Test wildcard in middle
    assert mock_gateway._topic_matches_pattern('module/v1/ff/test/data', 'module/*/data')
    
    # Test no match
    assert not mock_gateway._topic_matches_pattern('ccu/order/active', 'ccu/order/completed')
    assert not mock_gateway._topic_matches_pattern('module/v1/ff/test/connection', 'module/v1/ff/*/state')


def test_gateway_no_refresh_when_redis_unavailable(mock_gateway):
    """Test that gateway handles Redis unavailability gracefully"""
    with patch('omf2.backend.refresh._get_redis_client', return_value=None):
        # Simulate order message
        topic = 'ccu/order/active'
        message = {'orderId': '12345', 'status': 'ACTIVE'}
        
        # Process message (should succeed even if Redis is unavailable)
        with patch.object(mock_gateway, '_get_order_manager') as mock_order_mgr:
            mock_order_mgr.return_value = MagicMock()
            
            result = mock_gateway._route_ccu_message(topic, message)
            assert result is True  # Should not fail


def test_gateway_refresh_throttling(mock_gateway, mock_redis):
    """Test that refresh throttling works through the gateway"""
    import time
    
    with patch('omf2.backend.refresh._get_redis_client', return_value=mock_redis):
        topic = 'ccu/order/active'
        message = {'orderId': '12345', 'status': 'ACTIVE'}
        
        # First message should trigger refresh
        with patch.object(mock_gateway, '_get_order_manager') as mock_order_mgr:
            mock_order_mgr.return_value = MagicMock()
            mock_gateway._route_ccu_message(topic, message)
        
        import omf2.backend.refresh as refresh
        timestamp1 = refresh.get_last_refresh('order_updates')
        
        # Immediate second message should be throttled (timestamp unchanged)
        with patch.object(mock_gateway, '_get_order_manager') as mock_order_mgr:
            mock_order_mgr.return_value = MagicMock()
            mock_gateway._route_ccu_message(topic, message)
        
        timestamp2 = refresh.get_last_refresh('order_updates')
        assert timestamp1 == timestamp2  # Should be same (throttled)
        
        # After waiting, should trigger refresh
        time.sleep(1.1)
        with patch.object(mock_gateway, '_get_order_manager') as mock_order_mgr:
            mock_order_mgr.return_value = MagicMock()
            mock_gateway._route_ccu_message(topic, message)
        
        timestamp3 = refresh.get_last_refresh('order_updates')
        assert timestamp3 > timestamp2  # Should be newer


def test_gateway_multiple_groups(mock_gateway, mock_redis):
    """Test that different message types trigger different refresh groups"""
    with patch('omf2.backend.refresh._get_redis_client', return_value=mock_redis):
        # Order message
        with patch.object(mock_gateway, '_get_order_manager') as mock_order_mgr:
            mock_order_mgr.return_value = MagicMock()
            mock_gateway._route_ccu_message('ccu/order/active', {'orderId': '123'})
        
        # Sensor message
        with patch.object(mock_gateway, '_get_sensor_manager') as mock_sensor_mgr:
            mock_sensor_mgr.return_value = MagicMock()
            mock_gateway._route_ccu_message('/j1/txt/1/i/bme680', {'temp': 25})
        
        # Check that both groups were triggered
        import omf2.backend.refresh as refresh
        order_timestamp = refresh.get_last_refresh('order_updates')
        sensor_timestamp = refresh.get_last_refresh('sensor_updates')
        
        assert order_timestamp is not None
        assert sensor_timestamp is not None
