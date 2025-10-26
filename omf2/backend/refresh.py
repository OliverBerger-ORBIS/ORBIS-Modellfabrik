#!/usr/bin/env python3
"""
Redis-based UI Refresh Management with In-Memory Fallback

This module provides functions to trigger and check UI refresh events
using Redis as a shared store for refresh timestamps.

Features:
- Global throttle (minimum 1 second between refreshes)
- Group-based refresh management (e.g., 'orders', 'modules', 'sensors')
- Thread-safe operations
- In-memory fallback when Redis is unavailable
"""

import os
import threading
import time
from typing import Dict, Optional

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Global lock for thread safety
_refresh_lock = threading.Lock()

# Redis client (lazy initialization)
_redis_client = None
_redis_available = None

# In-memory fallback store for when Redis is unavailable
_memory_store: Dict[str, float] = {}


def _get_redis_client():
    """
    Get or create Redis client (lazy initialization)

    Returns:
        Redis client or None if Redis is not available
    """
    global _redis_client, _redis_available

    # Return cached result if already checked
    if _redis_available is False:
        return None

    if _redis_client is not None:
        return _redis_client

    # Try to import redis module
    try:
        import redis
    except ImportError:
        logger.warning("⚠️ Redis module not available. " "Install it with: pip install redis>=7.0.0")
        _redis_available = False
        return None

    try:
        # Try to get Redis URL from environment or streamlit secrets
        redis_url = os.environ.get("REDIS_URL")

        if not redis_url:
            try:
                import streamlit as st

                redis_url = st.secrets.get("REDIS_URL")
            except (ImportError, FileNotFoundError, KeyError):
                pass

        if not redis_url:
            # Default to localhost
            redis_url = "redis://localhost:6379/0"
            logger.info(f"ℹ️ REDIS_URL not set, using default: {redis_url}")
        else:
            logger.info(f"ℹ️ Using REDIS_URL: {redis_url}")

        # Create Redis client
        _redis_client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)

        # Test connection
        _redis_client.ping()
        _redis_available = True
        logger.info("✅ Redis client initialized successfully")

        return _redis_client

    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}. " "Using in-memory fallback for refresh management.")
        _redis_available = False
        return None


def request_refresh(group: str, min_interval: float = 1.0) -> bool:
    """
    Request a UI refresh for the specified group

    This function writes a timestamp to Redis (or in-memory fallback) for the specified group,
    but only if enough time has passed since the last refresh (throttle).

    Args:
        group: Refresh group name (e.g., 'orders', 'modules', 'sensors')
        min_interval: Minimum interval in seconds between refreshes (default: 1.0)

    Returns:
        True if refresh was requested, False if throttled
    """
    redis_client = _get_redis_client()

    with _refresh_lock:
        try:
            # Get current timestamp
            current_time = time.time()

            # Key for this group
            key = f"ui:last_refresh:{group}"

            # Get last refresh time
            if redis_client is not None:
                # Use Redis
                last_refresh_str = redis_client.get(key)
                last_refresh = float(last_refresh_str) if last_refresh_str else None
            else:
                # Use in-memory fallback
                last_refresh = _memory_store.get(key)

            # Check throttle
            if last_refresh is not None:
                time_since_last = current_time - last_refresh

                # Throttle: skip if too soon
                if time_since_last < min_interval:
                    logger.debug(
                        f"🚫 Refresh throttled for group '{group}' " f"({time_since_last:.2f}s < {min_interval}s)"
                    )
                    return False

            # Write new timestamp
            if redis_client is not None:
                # Use Redis
                redis_client.set(key, str(current_time))
                logger.debug(f"✅ Refresh requested for group '{group}' at {current_time} (Redis)")
            else:
                # Use in-memory fallback
                _memory_store[key] = current_time
                logger.debug(f"✅ Refresh requested for group '{group}' at {current_time} (memory)")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to request refresh for group '{group}': {e}")
            return False


def get_last_refresh(group: str) -> Optional[float]:
    """
    Get the last refresh timestamp for the specified group

    Args:
        group: Refresh group name (e.g., 'orders', 'modules', 'sensors')

    Returns:
        Last refresh timestamp as float, or None if not found
    """
    redis_client = _get_redis_client()

    try:
        key = f"ui:last_refresh:{group}"

        if redis_client is not None:
            # Use Redis
            last_refresh_str = redis_client.get(key)
            return float(last_refresh_str) if last_refresh_str else None
        else:
            # Use in-memory fallback
            return _memory_store.get(key)

    except Exception as e:
        logger.error(f"❌ Failed to get last refresh for group '{group}': {e}")
        return None


def clear_refresh(group: str) -> bool:
    """
    Clear the refresh timestamp for the specified group

    This is useful for testing or manual reset.

    Args:
        group: Refresh group name

    Returns:
        True if cleared successfully, False otherwise
    """
    redis_client = _get_redis_client()

    try:
        key = f"ui:last_refresh:{group}"

        if redis_client is not None:
            # Use Redis
            redis_client.delete(key)
            logger.debug(f"🗑️ Cleared refresh for group '{group}' (Redis)")
        else:
            # Use in-memory fallback
            _memory_store.pop(key, None)
            logger.debug(f"🗑️ Cleared refresh for group '{group}' (memory)")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to clear refresh for group '{group}': {e}")
        return False


def get_all_refresh_groups() -> list:
    """
    Get all refresh groups currently tracked

    Returns:
        List of group names
    """
    redis_client = _get_redis_client()

    try:
        if redis_client is not None:
            # Use Redis
            pattern = "ui:last_refresh:*"
            keys = redis_client.keys(pattern)

            # Extract group names from keys
            groups = [key.replace("ui:last_refresh:", "") for key in keys]
            return groups
        else:
            # Use in-memory fallback
            prefix = "ui:last_refresh:"
            groups = [key.replace(prefix, "") for key in _memory_store.keys() if key.startswith(prefix)]
            return groups

    except Exception as e:
        logger.error(f"❌ Failed to get refresh groups: {e}")
        return []
