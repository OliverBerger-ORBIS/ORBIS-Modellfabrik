#!/usr/bin/env python3
"""
Unit tests for omf2.backend.refresh module

Tests the Redis-based refresh throttle logic using fakeredis
"""

import time
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_redis():
    """Create a fake Redis client for testing"""
    try:
        import fakeredis

        return fakeredis.FakeRedis(decode_responses=True)
    except ImportError:
        pytest.skip("fakeredis not available")


@pytest.fixture
def refresh_module(mock_redis):
    """Set up refresh module with mocked Redis"""
    import omf2.backend.refresh as refresh

    # Reset module state
    refresh._redis_client = None
    refresh._redis_available = None

    # Patch _get_redis_client to return our mock
    with patch.object(refresh, "_get_redis_client", return_value=mock_redis):
        yield refresh


def test_request_refresh_basic(refresh_module, mock_redis):
    """Test basic refresh request"""
    # Patch _get_redis_client for the duration of this test
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        result = refresh_module.request_refresh("test_group")
        assert result is True

        # Check that timestamp was written to Redis with new key naming
        timestamp = mock_redis.get("ui:last_refresh:test_group")
        assert timestamp is not None
        assert float(timestamp) > 0


def test_request_refresh_throttle(refresh_module, mock_redis):
    """Test that refresh is throttled when called too quickly"""
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        # First request should succeed
        result1 = refresh_module.request_refresh("test_group", min_interval=1.0)
        assert result1 is True

        # Immediate second request should be throttled
        result2 = refresh_module.request_refresh("test_group", min_interval=1.0)
        assert result2 is False

        # Wait and try again
        time.sleep(1.1)
        result3 = refresh_module.request_refresh("test_group", min_interval=1.0)
        assert result3 is True


def test_get_last_refresh(refresh_module, mock_redis):
    """Test getting last refresh timestamp"""
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        # Initially should return None
        timestamp = refresh_module.get_last_refresh("test_group")
        assert timestamp is None

        # Request refresh
        refresh_module.request_refresh("test_group")

        # Now should return a timestamp
        timestamp = refresh_module.get_last_refresh("test_group")
        assert timestamp is not None
        assert isinstance(timestamp, float)
        assert timestamp > 0


def test_clear_refresh(refresh_module, mock_redis):
    """Test clearing refresh timestamp"""
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        # Request refresh
        refresh_module.request_refresh("test_group")

        # Verify it exists
        timestamp = refresh_module.get_last_refresh("test_group")
        assert timestamp is not None

        # Clear it
        result = refresh_module.clear_refresh("test_group")
        assert result is True

        # Verify it's gone
        timestamp = refresh_module.get_last_refresh("test_group")
        assert timestamp is None


def test_get_all_refresh_groups(refresh_module, mock_redis):
    """Test getting all refresh groups"""
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        # Request refresh for multiple groups
        refresh_module.request_refresh("orders")
        refresh_module.request_refresh("modules")
        refresh_module.request_refresh("sensors")

        # Get all groups
        groups = refresh_module.get_all_refresh_groups()
        assert "orders" in groups
        assert "modules" in groups
        assert "sensors" in groups


def test_request_refresh_different_groups(refresh_module, mock_redis):
    """Test that different groups don't interfere with each other"""
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        # Request refresh for group1
        result1 = refresh_module.request_refresh("group1", min_interval=1.0)
        assert result1 is True

        # Immediately request refresh for group2 (should succeed, different group)
        result2 = refresh_module.request_refresh("group2", min_interval=1.0)
        assert result2 is True

        # Immediately request refresh for group1 again (should be throttled)
        result3 = refresh_module.request_refresh("group1", min_interval=1.0)
        assert result3 is False


def test_request_refresh_custom_interval(refresh_module, mock_redis):
    """Test custom throttle intervals"""
    with patch("omf2.backend.refresh._get_redis_client", return_value=mock_redis):
        # Request with 0.5s interval
        result1 = refresh_module.request_refresh("test_group", min_interval=0.5)
        assert result1 is True

        # Immediate request should be throttled
        result2 = refresh_module.request_refresh("test_group", min_interval=0.5)
        assert result2 is False

        # Wait 0.6s and try again
        time.sleep(0.6)
        result3 = refresh_module.request_refresh("test_group", min_interval=0.5)
        assert result3 is True


def test_redis_unavailable():
    """Test in-memory implementation (Redis removed)"""
    import omf2.backend.refresh as refresh

    # Reset module state
    refresh._memory_store = {}

    # request_refresh should return True (using in-memory store)
    result = refresh.request_refresh("test_group")
    assert result is True

    # get_last_refresh should return the timestamp from memory
    timestamp = refresh.get_last_refresh("test_group")
    assert timestamp is not None
    assert isinstance(timestamp, float)
    assert timestamp > 0

    # clear_refresh should return True (using in-memory store)
    result = refresh.clear_refresh("test_group")
    assert result is True

    # After clearing, get_last_refresh should return None
    timestamp = refresh.get_last_refresh("test_group")
    assert timestamp is None

    # Test get_all_refresh_groups with in-memory store
    refresh.request_refresh("orders")
    refresh.request_refresh("modules")
    groups = refresh.get_all_refresh_groups()
    assert "orders" in groups
    assert "modules" in groups


def test_memory_fallback_throttle():
    """Test that in-memory store properly throttles requests"""
    import omf2.backend.refresh as refresh

    # Reset module state
    refresh._memory_store = {}

    # First request should succeed
    result1 = refresh.request_refresh("test_group", min_interval=1.0)
    assert result1 is True

    # Immediate second request should be throttled
    result2 = refresh.request_refresh("test_group", min_interval=1.0)
    assert result2 is False

    # Wait and try again
    time.sleep(1.1)
    result3 = refresh.request_refresh("test_group", min_interval=1.0)
    assert result3 is True
