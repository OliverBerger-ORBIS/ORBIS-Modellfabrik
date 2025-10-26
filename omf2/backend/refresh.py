#!/usr/bin/env python3
"""
Redis-based UI Refresh Management

This module provides functions to trigger and check UI refresh events
using Redis as a shared store for refresh timestamps.

Features:
- Global throttle (minimum 1 second between refreshes)
- Group-based refresh management (e.g., 'orders', 'modules', 'sensors')
- Thread-safe operations
"""

import os
import time
import threading
from typing import Optional

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Global lock for thread safety
_refresh_lock = threading.Lock()

# Redis client (lazy initialization)
_redis_client = None
_redis_available = None


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
    
    try:
        import redis
        
        # Try to get Redis URL from environment or streamlit secrets
        redis_url = os.environ.get('REDIS_URL')
        
        if not redis_url:
            try:
                import streamlit as st
                redis_url = st.secrets.get('REDIS_URL')
            except (ImportError, FileNotFoundError, KeyError):
                pass
        
        if not redis_url:
            # Default to localhost
            redis_url = 'redis://localhost:6379/0'
            logger.warning(f"⚠️ REDIS_URL not set, using default: {redis_url}")
        
        # Create Redis client
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Test connection
        _redis_client.ping()
        _redis_available = True
        logger.info(f"✅ Redis client initialized: {redis_url}")
        
        return _redis_client
        
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}")
        _redis_available = False
        return None


def request_refresh(group: str, min_interval: float = 1.0) -> bool:
    """
    Request a UI refresh for the specified group
    
    This function writes a timestamp to Redis for the specified group,
    but only if enough time has passed since the last refresh (throttle).
    
    Args:
        group: Refresh group name (e.g., 'orders', 'modules', 'sensors')
        min_interval: Minimum interval in seconds between refreshes (default: 1.0)
    
    Returns:
        True if refresh was requested, False if throttled or Redis unavailable
    """
    redis_client = _get_redis_client()
    
    if redis_client is None:
        logger.debug(f"⚠️ Redis not available, cannot request refresh for group: {group}")
        return False
    
    with _refresh_lock:
        try:
            # Get current timestamp
            current_time = time.time()
            
            # Redis key for this group
            redis_key = f"omf2:ui:refresh:{group}"
            
            # Check last refresh time (if any)
            last_refresh_str = redis_client.get(redis_key)
            
            if last_refresh_str:
                last_refresh = float(last_refresh_str)
                time_since_last = current_time - last_refresh
                
                # Throttle: skip if too soon
                if time_since_last < min_interval:
                    logger.debug(
                        f"🚫 Refresh throttled for group '{group}' "
                        f"({time_since_last:.2f}s < {min_interval}s)"
                    )
                    return False
            
            # Write new timestamp
            redis_client.set(redis_key, str(current_time))
            logger.debug(f"✅ Refresh requested for group '{group}' at {current_time}")
            
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
        Last refresh timestamp as float, or None if not found or Redis unavailable
    """
    redis_client = _get_redis_client()
    
    if redis_client is None:
        logger.debug(f"⚠️ Redis not available, cannot get last refresh for group: {group}")
        return None
    
    try:
        redis_key = f"omf2:ui:refresh:{group}"
        last_refresh_str = redis_client.get(redis_key)
        
        if last_refresh_str:
            return float(last_refresh_str)
        else:
            return None
            
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
    
    if redis_client is None:
        logger.debug(f"⚠️ Redis not available, cannot clear refresh for group: {group}")
        return False
    
    try:
        redis_key = f"omf2:ui:refresh:{group}"
        redis_client.delete(redis_key)
        logger.debug(f"🗑️ Cleared refresh for group '{group}'")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to clear refresh for group '{group}': {e}")
        return False


def get_all_refresh_groups() -> list:
    """
    Get all refresh groups currently tracked in Redis
    
    Returns:
        List of group names
    """
    redis_client = _get_redis_client()
    
    if redis_client is None:
        logger.debug("⚠️ Redis not available, cannot get refresh groups")
        return []
    
    try:
        pattern = "omf2:ui:refresh:*"
        keys = redis_client.keys(pattern)
        
        # Extract group names from keys
        groups = [key.replace("omf2:ui:refresh:", "") for key in keys]
        return groups
        
    except Exception as e:
        logger.error(f"❌ Failed to get refresh groups: {e}")
        return []
