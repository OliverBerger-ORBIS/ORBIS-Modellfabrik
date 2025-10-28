#!/usr/bin/env python3
"""
Tests for Admin Cache TTL implementation.
"""

import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from omf2.common.cache import TTLCache, cached, get_cache


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset the global cache instance before each test."""
    import omf2.common.cache as cache_module

    cache_module._cache_instance = None
    yield
    cache_module._cache_instance = None


class TestTTLCache:
    """Test cases for TTLCache"""

    def test_cache_disabled_by_default(self):
        """Test that cache is disabled when env var is not set"""
        with patch.dict(os.environ, {}, clear=False):
            if "OMF2_CACHE_TTL" in os.environ:
                del os.environ["OMF2_CACHE_TTL"]
            if "OMF2_ADMIN_CACHE_TTL" in os.environ:
                del os.environ["OMF2_ADMIN_CACHE_TTL"]
            cache = TTLCache()
            assert not cache.is_enabled()

    def test_cache_enabled_with_generic_env_var(self):
        """Test that cache is enabled with generic OMF2_CACHE_TTL env var"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "30"}):
            cache = TTLCache()
            assert cache.is_enabled()

    def test_cache_enabled_with_legacy_env_var(self):
        """Test that cache is enabled with legacy OMF2_ADMIN_CACHE_TTL env var"""
        with patch.dict(os.environ, {"OMF2_ADMIN_CACHE_TTL": "30"}):
            cache = TTLCache()
            assert cache.is_enabled()

    def test_cache_generic_env_var_takes_precedence(self):
        """Test that OMF2_CACHE_TTL takes precedence over legacy env var"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "30", "OMF2_ADMIN_CACHE_TTL": "60"}):
            cache = TTLCache()
            assert cache.is_enabled()
            # Should use the generic env var value (30)
            assert cache._default_ttl == 30.0

    def test_cache_disabled_with_zero_ttl(self):
        """Test that cache is disabled when TTL is 0"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "0"}):
            cache = TTLCache()
            assert not cache.is_enabled()

    def test_cache_disabled_with_invalid_ttl(self):
        """Test that cache is disabled with invalid TTL value"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "invalid"}):
            cache = TTLCache()
            assert not cache.is_enabled()

    def test_cache_stores_and_retrieves_values(self):
        """Test that cache can store and retrieve values"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            cache = TTLCache()
            cache.set("test_key", "test_value")
            assert cache.get("test_key") == "test_value"

    def test_cache_returns_none_for_missing_key(self):
        """Test that cache returns None for non-existent keys"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            cache = TTLCache()
            assert cache.get("nonexistent_key") is None

    def test_cache_expiration(self):
        """Test that cache entries expire after TTL"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "0.1"}):
            cache = TTLCache()
            cache.set("expire_key", "expire_value", ttl=0.1)

            # Should be available immediately
            assert cache.get("expire_key") == "expire_value"

            # Wait for expiration
            time.sleep(0.15)

            # Should be expired and return None
            assert cache.get("expire_key") is None

    def test_cache_custom_ttl(self):
        """Test that cache respects custom TTL per key"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            cache = TTLCache()
            cache.set("short_ttl", "value", ttl=0.1)
            cache.set("long_ttl", "value", ttl=60)

            # Wait for short TTL to expire
            time.sleep(0.15)

            assert cache.get("short_ttl") is None
            assert cache.get("long_ttl") == "value"

    def test_get_or_set_with_cache_hit(self):
        """Test get_or_set when value is in cache"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            cache = TTLCache()
            call_count = [0]

            def factory():
                call_count[0] += 1
                return "computed_value"

            # First call should compute
            result1 = cache.get_or_set("key1", factory)
            assert result1 == "computed_value"
            assert call_count[0] == 1

            # Second call should use cache
            result2 = cache.get_or_set("key1", factory)
            assert result2 == "computed_value"
            assert call_count[0] == 1  # Factory not called again

    def test_get_or_set_with_cache_miss(self):
        """Test get_or_set when value is not in cache"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            cache = TTLCache()
            call_count = [0]

            def factory():
                call_count[0] += 1
                return f"value_{call_count[0]}"

            result1 = cache.get_or_set("key1", factory)
            assert result1 == "value_1"

            result2 = cache.get_or_set("key2", factory)
            assert result2 == "value_2"

            # Different keys should call factory separately
            assert call_count[0] == 2

    def test_cache_clear(self):
        """Test that cache can be cleared"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            cache = TTLCache()
            cache.set("key1", "value1")
            cache.set("key2", "value2")

            assert cache.get("key1") == "value1"
            assert cache.get("key2") == "value2"

            cache.clear()

            assert cache.get("key1") is None
            assert cache.get("key2") is None

    def test_cache_disabled_get_returns_none(self):
        """Test that get returns None when cache is disabled"""
        with patch.dict(os.environ, {}, clear=False):
            if "OMF2_CACHE_TTL" in os.environ:
                del os.environ["OMF2_CACHE_TTL"]
            if "OMF2_ADMIN_CACHE_TTL" in os.environ:
                del os.environ["OMF2_ADMIN_CACHE_TTL"]
            cache = TTLCache()
            cache.set("key", "value")
            assert cache.get("key") is None

    def test_cache_disabled_get_or_set_always_calls_factory(self):
        """Test that get_or_set always calls factory when cache is disabled"""
        with patch.dict(os.environ, {}, clear=False):
            if "OMF2_CACHE_TTL" in os.environ:
                del os.environ["OMF2_CACHE_TTL"]
            if "OMF2_ADMIN_CACHE_TTL" in os.environ:
                del os.environ["OMF2_ADMIN_CACHE_TTL"]
            cache = TTLCache()
            call_count = [0]

            def factory():
                call_count[0] += 1
                return "value"

            # Should call factory each time when cache is disabled
            cache.get_or_set("key", factory)
            cache.get_or_set("key", factory)
            assert call_count[0] == 2


class TestCachedDecorator:
    """Test cases for @cached decorator"""

    def test_cached_decorator_with_enabled_cache(self):
        """Test that @cached decorator caches function results"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            call_count = [0]

            @cached(ttl=60)
            def expensive_function():
                call_count[0] += 1
                return "result"

            # First call
            result1 = expensive_function()
            assert result1 == "result"
            assert call_count[0] == 1

            # Second call should use cache
            result2 = expensive_function()
            assert result2 == "result"
            assert call_count[0] == 1

    def test_cached_decorator_with_disabled_cache(self):
        """Test that @cached decorator works when cache is disabled"""
        with patch.dict(os.environ, {}, clear=False):
            if "OMF2_CACHE_TTL" in os.environ:
                del os.environ["OMF2_CACHE_TTL"]
            if "OMF2_ADMIN_CACHE_TTL" in os.environ:
                del os.environ["OMF2_ADMIN_CACHE_TTL"]

            call_count = [0]

            @cached(ttl=60)
            def expensive_function():
                call_count[0] += 1
                return "result"

            # Should call function each time when cache is disabled
            expensive_function()
            expensive_function()
            assert call_count[0] == 2

    def test_cached_decorator_with_key_prefix(self):
        """Test @cached decorator with key prefix"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            call_count = [0]

            @cached(ttl=60, key_prefix="test_prefix")
            def function_with_prefix():
                call_count[0] += 1
                return "result"

            function_with_prefix()
            function_with_prefix()
            assert call_count[0] == 1

    def test_cached_decorator_with_arguments(self):
        """Test @cached decorator with function arguments"""
        with patch.dict(os.environ, {"OMF2_CACHE_TTL": "60"}):
            call_count = [0]

            @cached(ttl=60)
            def function_with_args(arg1, arg2):
                call_count[0] += 1
                return f"{arg1}_{arg2}"

            # Different arguments should create different cache entries
            result1 = function_with_args("a", "b")
            result2 = function_with_args("a", "b")
            result3 = function_with_args("c", "d")

            assert result1 == "a_b"
            assert result2 == "a_b"
            assert result3 == "c_d"
            assert call_count[0] == 2  # Two different arg combinations


class TestGlobalCache:
    """Test cases for global cache instance"""

    def test_get_cache_returns_singleton(self):
        """Test that get_cache returns a singleton instance"""
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
