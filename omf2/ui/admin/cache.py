"""
Lightweight TTL cache for Admin tab manager/config loader calls.

This module provides a simple time-to-live (TTL) cache to reduce latency
and repeated I/O operations for admin dashboard config/manager loading.

The cache is opt-in via the OMF2_ADMIN_CACHE_TTL environment variable.
If unset or 0, caching is disabled.
"""

import os
import time
from functools import wraps
from threading import Lock
from typing import Any, Callable, Dict, Optional, Tuple


class TTLCache:
    """Thread-safe TTL cache implementation."""

    def __init__(self, default_ttl: float = 60.0):
        """
        Initialize the TTL cache.

        Args:
            default_ttl: Default time-to-live in seconds (default: 60.0)
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()
        self._default_ttl = default_ttl
        self._enabled = self._get_cache_enabled()

    def _get_cache_enabled(self) -> bool:
        """
        Check if caching is enabled via environment variable.

        Returns:
            True if caching is enabled, False otherwise
        """
        try:
            ttl_str = os.environ.get("OMF2_ADMIN_CACHE_TTL", "")
            if ttl_str:
                ttl_value = float(ttl_str)
                if ttl_value > 0:
                    self._default_ttl = ttl_value
                    return True
        except (ValueError, TypeError):
            pass
        return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if not self._enabled:
            return None

        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    # Expired, remove from cache
                    del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        if not self._enabled:
            return

        ttl_seconds = ttl if ttl is not None else self._default_ttl
        expiry = time.time() + ttl_seconds

        with self._lock:
            self._cache[key] = (value, expiry)

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[float] = None) -> Any:
        """
        Get a value from cache, or compute and cache it if not present.

        Args:
            key: Cache key
            factory: Function to call to generate the value if not cached
            ttl: Time-to-live in seconds (uses default if None)

        Returns:
            Cached or newly computed value
        """
        # Try to get from cache first
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value

        # Not in cache or disabled, compute value
        value = factory()

        # Store in cache if enabled
        self.set(key, value, ttl)

        return value

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def is_enabled(self) -> bool:
        """Check if the cache is enabled."""
        return self._enabled


# Global cache instance
_cache_instance: Optional[TTLCache] = None


def get_cache() -> TTLCache:
    """
    Get the global cache instance.

    Returns:
        Global TTLCache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = TTLCache()
    return _cache_instance


def cached(ttl: Optional[float] = None, key_prefix: str = ""):
    """
    Decorator to cache function results with TTL.

    Args:
        ttl: Time-to-live in seconds (uses cache default if None)
        key_prefix: Prefix for cache keys (default: empty string)

    Returns:
        Decorated function that caches results

    Example:
        @cached(ttl=60, key_prefix="mqtt_settings")
        def load_mqtt_settings():
            # expensive operation
            return settings
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()

            # Generate cache key from function name and arguments
            func_name = func.__name__
            args_key = str(args) + str(sorted(kwargs.items()))
            cache_key = f"{key_prefix}:{func_name}:{args_key}" if key_prefix else f"{func_name}:{args_key}"

            # Use get_or_set pattern
            return cache.get_or_set(cache_key, lambda: func(*args, **kwargs), ttl)

        return wrapper

    return decorator
