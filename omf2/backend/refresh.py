#!/usr/bin/env python3
"""
In-Process UI Refresh Management

This module provides functions to trigger and check UI refresh events
using an in-memory, thread-safe store for refresh timestamps.

Features:
- Global throttle (minimum 1 second between refreshes)
- Group-based refresh management (e.g., 'orders', 'modules', 'sensors')
- Thread-safe operations
- No external dependencies (Redis not required)
"""

import threading
import time
from typing import Dict, Optional

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Global lock for thread safety
_refresh_lock = threading.Lock()

# In-memory store for refresh timestamps
_memory_store: Dict[str, float] = {}


def request_refresh(group: str, min_interval: float = 1.0) -> bool:
    """
    Request a UI refresh for the specified group

    This function writes a timestamp to the in-memory store for the specified group,
    but only if enough time has passed since the last refresh (throttle).

    Args:
        group: Refresh group name (e.g., 'order_updates', 'module_updates', 'sensor_updates')
        min_interval: Minimum interval in seconds between refreshes (default: 1.0)

    Returns:
        True if refresh was requested, False if throttled
    """
    with _refresh_lock:
        try:
            # Get current timestamp
            current_time = time.time()

            # Key for this group
            key = f"ui:last_refresh:{group}"

            # Get last refresh time
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
            _memory_store[key] = current_time
            logger.debug(f"✅ Refresh requested for group '{group}' at {current_time}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to request refresh for group '{group}': {e}")
            return False


def get_last_refresh_ts(group: str) -> Optional[float]:
    """
    Get the last refresh timestamp for the specified group

    Args:
        group: Refresh group name (e.g., 'order_updates', 'module_updates', 'sensor_updates')

    Returns:
        Last refresh timestamp as float, or None if not found
    """
    try:
        key = f"ui:last_refresh:{group}"
        return _memory_store.get(key)

    except Exception as e:
        logger.error(f"❌ Failed to get last refresh for group '{group}': {e}")
        return None


def clear_last_refresh(group: str) -> bool:
    """
    Clear the refresh timestamp for the specified group

    This is useful for testing or manual reset.

    Args:
        group: Refresh group name

    Returns:
        True if cleared successfully, False otherwise
    """
    try:
        key = f"ui:last_refresh:{group}"
        _memory_store.pop(key, None)
        logger.debug(f"🗑️ Cleared refresh for group '{group}'")
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
    try:
        prefix = "ui:last_refresh:"
        groups = [key.replace(prefix, "") for key in _memory_store.keys() if key.startswith(prefix)]
        return groups

    except Exception as e:
        logger.error(f"❌ Failed to get refresh groups: {e}")
        return []


# Alias for backward compatibility
def get_last_refresh(group: str) -> Optional[float]:
    """
    Alias for get_last_refresh_ts for backward compatibility

    Args:
        group: Refresh group name

    Returns:
        Last refresh timestamp as float, or None if not found
    """
    return get_last_refresh_ts(group)


def clear_refresh(group: str) -> bool:
    """
    Alias for clear_last_refresh for backward compatibility

    Args:
        group: Refresh group name

    Returns:
        True if cleared successfully, False otherwise
    """
    return clear_last_refresh(group)
