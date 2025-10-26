#!/usr/bin/env python3
"""
Unit tests for Streamlit polling helpers

Tests the helper functions without requiring a browser or Streamlit server.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
import requests


def test_get_api_url_default():
    """Test getting default API URL"""
    from omf2.ui.common.refresh_polling import get_api_url
    
    # Should return default when no config is set
    with patch.dict('os.environ', {}, clear=True):
        url = get_api_url()
        assert url == "http://localhost:5001"


def test_get_api_url_from_env():
    """Test getting API URL from environment variable"""
    from omf2.ui.common.refresh_polling import get_api_url
    
    test_url = "http://custom-host:8080"
    with patch.dict('os.environ', {'REFRESH_API_URL': test_url}):
        url = get_api_url()
        assert url == test_url


def test_get_last_refresh_timestamp_success():
    """Test successful API call to get refresh timestamp"""
    from omf2.ui.common.refresh_polling import get_last_refresh_timestamp
    
    # Mock requests.get
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'success': True,
        'group': 'test_group',
        'timestamp': 1234567890.123
    }
    
    with patch('requests.get', return_value=mock_response):
        timestamp = get_last_refresh_timestamp('test_group')
        assert timestamp == 1234567890.123


def test_get_last_refresh_timestamp_no_timestamp():
    """Test API call when no timestamp is available"""
    from omf2.ui.common.refresh_polling import get_last_refresh_timestamp
    
    # Mock requests.get - success but no timestamp
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'success': True,
        'group': 'test_group',
        'timestamp': None
    }
    
    with patch('requests.get', return_value=mock_response):
        timestamp = get_last_refresh_timestamp('test_group')
        assert timestamp is None


def test_get_last_refresh_timestamp_api_error():
    """Test API call when server returns error"""
    from omf2.ui.common.refresh_polling import get_last_refresh_timestamp
    
    # Mock requests.get - error response
    mock_response = Mock()
    mock_response.status_code = 500
    
    with patch('requests.get', return_value=mock_response):
        timestamp = get_last_refresh_timestamp('test_group')
        assert timestamp is None


def test_get_last_refresh_timestamp_network_error():
    """Test API call when network error occurs"""
    from omf2.ui.common.refresh_polling import get_last_refresh_timestamp
    
    # Mock requests.get - network error
    with patch('requests.get', side_effect=requests.RequestException("Network error")):
        timestamp = get_last_refresh_timestamp('test_group')
        assert timestamp is None


def test_get_last_refresh_timestamp_timeout():
    """Test API call timeout"""
    from omf2.ui.common.refresh_polling import get_last_refresh_timestamp
    
    # Mock requests.get - timeout
    with patch('requests.get', side_effect=requests.Timeout("Request timeout")):
        timestamp = get_last_refresh_timestamp('test_group', timeout=0.1)
        assert timestamp is None


def test_should_reload_data_no_previous_timestamp():
    """Test should_reload_data when no previous timestamp exists"""
    from omf2.ui.common.refresh_polling import should_reload_data
    
    # Mock session_state
    mock_st = MagicMock()
    mock_st.session_state = {}
    
    # Mock get_last_refresh_timestamp
    with patch('omf2.ui.common.refresh_polling.st', mock_st), \
         patch('omf2.ui.common.refresh_polling.get_last_refresh_timestamp', return_value=1234567890.0):
        
        result = should_reload_data('test_group')
        assert result is True
        # Should have updated session_state
        assert mock_st.session_state['test_group_last_refresh_timestamp'] == 1234567890.0


def test_should_reload_data_with_newer_timestamp():
    """Test should_reload_data when a newer timestamp is available"""
    from omf2.ui.common.refresh_polling import should_reload_data
    
    # Mock session_state with old timestamp
    mock_st = MagicMock()
    mock_st.session_state = {'test_group_last_refresh_timestamp': 1000.0}
    
    # Mock get_last_refresh_timestamp with newer timestamp
    with patch('omf2.ui.common.refresh_polling.st', mock_st), \
         patch('omf2.ui.common.refresh_polling.get_last_refresh_timestamp', return_value=2000.0):
        
        result = should_reload_data('test_group')
        assert result is True
        # Should have updated session_state
        assert mock_st.session_state['test_group_last_refresh_timestamp'] == 2000.0


def test_should_reload_data_with_same_timestamp():
    """Test should_reload_data when timestamp hasn't changed"""
    from omf2.ui.common.refresh_polling import should_reload_data
    
    # Mock session_state with current timestamp
    mock_st = MagicMock()
    mock_st.session_state = {'test_group_last_refresh_timestamp': 1234567890.0}
    
    # Mock get_last_refresh_timestamp with same timestamp
    with patch('omf2.ui.common.refresh_polling.st', mock_st), \
         patch('omf2.ui.common.refresh_polling.get_last_refresh_timestamp', return_value=1234567890.0):
        
        result = should_reload_data('test_group')
        assert result is False


def test_should_reload_data_force():
    """Test should_reload_data with force=True"""
    from omf2.ui.common.refresh_polling import should_reload_data
    
    # Force should always return True regardless of timestamp
    result = should_reload_data('test_group', force=True)
    assert result is True


def test_should_reload_data_api_unavailable():
    """Test should_reload_data when API is unavailable"""
    from omf2.ui.common.refresh_polling import should_reload_data
    
    mock_st = MagicMock()
    mock_st.session_state = {}
    
    # Mock get_last_refresh_timestamp returning None (API unavailable)
    with patch('omf2.ui.common.refresh_polling.st', mock_st), \
         patch('omf2.ui.common.refresh_polling.get_last_refresh_timestamp', return_value=None):
        
        result = should_reload_data('test_group')
        assert result is False


def test_check_and_handle_refresh_with_callback():
    """Test check_and_handle_refresh with callback function"""
    from omf2.ui.common.refresh_polling import check_and_handle_refresh
    
    # Mock session_state
    mock_st = MagicMock()
    mock_st.session_state = {}
    
    # Mock callback
    callback = MagicMock()
    
    # Mock get_last_refresh_timestamp
    with patch('omf2.ui.common.refresh_polling.st', mock_st), \
         patch('omf2.ui.common.refresh_polling.get_last_refresh_timestamp', return_value=1234567890.0):
        
        result = check_and_handle_refresh('test_group', on_refresh_callback=callback)
        
        assert result is True
        callback.assert_called_once()


def test_check_and_handle_refresh_no_callback():
    """Test check_and_handle_refresh without callback function"""
    from omf2.ui.common.refresh_polling import check_and_handle_refresh
    
    # Mock session_state
    mock_st = MagicMock()
    mock_st.session_state = {}
    
    # Mock get_last_refresh_timestamp
    with patch('omf2.ui.common.refresh_polling.st', mock_st), \
         patch('omf2.ui.common.refresh_polling.get_last_refresh_timestamp', return_value=1234567890.0):
        
        result = check_and_handle_refresh('test_group')
        
        assert result is True
        # Should have updated session_state
        assert 'test_group_last_refresh_timestamp' in mock_st.session_state
