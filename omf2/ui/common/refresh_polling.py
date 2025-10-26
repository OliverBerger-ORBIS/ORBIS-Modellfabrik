#!/usr/bin/env python3
"""
Streamlit UI Polling Helpers

Provides helper functions for polling the refresh API and managing
auto-refresh in Streamlit pages.
"""

import time
import requests
from typing import Optional
import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Default API endpoint (can be configured via environment or secrets)
DEFAULT_API_URL = "http://localhost:5001"


def get_api_url() -> str:
    """
    Get the refresh API URL from configuration
    
    Returns:
        API base URL
    """
    # Try to get from Streamlit secrets first
    try:
        if hasattr(st, 'secrets') and 'REFRESH_API_URL' in st.secrets:
            return st.secrets['REFRESH_API_URL']
    except Exception:
        pass
    
    # Fall back to environment variable or default
    import os
    return os.environ.get('REFRESH_API_URL', DEFAULT_API_URL)


def get_last_refresh_timestamp(group: str, timeout: float = 1.0) -> Optional[float]:
    """
    Get the last refresh timestamp for a group from the API
    
    Args:
        group: Refresh group name (e.g., 'order_updates', 'module_updates')
        timeout: Request timeout in seconds (default: 1.0)
    
    Returns:
        Last refresh timestamp as float, or None if unavailable
    """
    try:
        api_url = get_api_url()
        url = f"{api_url}/api/last_refresh?group={group}"
        
        response = requests.get(url, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('timestamp') is not None:
                return float(data['timestamp'])
        
        return None
        
    except Exception as e:
        logger.debug(f"⚠️ Failed to get last refresh for group '{group}': {e}")
        return None


def check_and_handle_refresh(
    group: str,
    session_state_key: str = 'last_refresh_timestamp',
    on_refresh_callback=None
) -> bool:
    """
    Check if a refresh is needed and handle it
    
    This function checks the refresh API for a new timestamp and compares
    it with the last known timestamp in session_state. If a refresh is needed,
    it calls the optional callback and returns True.
    
    Args:
        group: Refresh group name
        session_state_key: Key in session_state to store last timestamp
        on_refresh_callback: Optional function to call when refresh is needed
    
    Returns:
        True if refresh was triggered, False otherwise
    """
    # Get current timestamp from API
    current_timestamp = get_last_refresh_timestamp(group)
    
    if current_timestamp is None:
        # API unavailable or no refresh yet
        return False
    
    # Get last known timestamp from session_state
    full_key = f"{group}_{session_state_key}"
    last_timestamp = st.session_state.get(full_key, None)
    
    # Check if refresh is needed
    if last_timestamp is None or current_timestamp > last_timestamp:
        logger.debug(f"🔄 Refresh detected for group '{group}' (new: {current_timestamp}, old: {last_timestamp})")
        
        # Update session_state
        st.session_state[full_key] = current_timestamp
        
        # Call callback if provided
        if on_refresh_callback:
            try:
                on_refresh_callback()
            except Exception as e:
                logger.error(f"❌ Error in refresh callback: {e}")
        
        return True
    
    return False


def init_auto_refresh_polling(group: str, interval_ms: int = 1000):
    """
    Initialize auto-refresh polling for a Streamlit page
    
    This function sets up the infrastructure for auto-refresh polling.
    Call this at the beginning of your Streamlit page.
    
    Args:
        group: Refresh group name
        interval_ms: Polling interval in milliseconds (default: 1000)
    
    Note:
        This uses streamlit_autorefresh if available, otherwise falls back
        to manual polling with st.empty()
    """
    try:
        from streamlit_autorefresh import st_autorefresh
        
        # Auto-refresh at the specified interval
        st_autorefresh(interval=interval_ms, key=f"autorefresh_{group}")
        
    except ImportError:
        logger.debug("⚠️ streamlit_autorefresh not available, using manual polling")
        # Manual polling fallback
        if f"refresh_counter_{group}" not in st.session_state:
            st.session_state[f"refresh_counter_{group}"] = 0


def should_reload_data(group: str, force: bool = False) -> bool:
    """
    Check if data should be reloaded based on refresh timestamp
    
    This is a simpler alternative to check_and_handle_refresh that just
    returns True/False without calling callbacks.
    
    Args:
        group: Refresh group name
        force: If True, always return True (force reload)
    
    Returns:
        True if data should be reloaded, False otherwise
    """
    if force:
        return True
    
    # Get current timestamp from API
    current_timestamp = get_last_refresh_timestamp(group)
    
    if current_timestamp is None:
        return False
    
    # Get last known timestamp from session_state
    key = f"{group}_last_refresh_timestamp"
    last_timestamp = st.session_state.get(key, None)
    
    # Check if refresh is needed
    if last_timestamp is None or current_timestamp > last_timestamp:
        # Update session_state
        st.session_state[key] = current_timestamp
        return True
    
    return False
