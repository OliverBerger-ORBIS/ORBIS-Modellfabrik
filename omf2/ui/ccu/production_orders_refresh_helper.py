#!/usr/bin/env python3
"""
Production Orders Refresh Helper

Provides robust polling + compare helper for production orders subtab.
Integrates with /api/last_refresh endpoint to trigger domain-data reloads
when the timestamp increases.
"""

import importlib.util
import os
from typing import Optional

import requests
import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def _get_autorefresh_enabled() -> bool:
    """
    Check if autorefresh is enabled

    Tries in order:
    1. st.secrets['ui']['autorefresh'] (truthy)
    2. Environment variable OMF2_UI_AUTOREFRESH ("1", "true", "yes")
    3. Default False

    Returns:
        True if autorefresh is enabled, False otherwise
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, "secrets") and "ui" in st.secrets:
            ui_config = st.secrets.get("ui")
            if ui_config and "autorefresh" in ui_config:
                return bool(ui_config["autorefresh"])
    except Exception as e:
        logger.debug(f"Could not read autorefresh from st.secrets: {e}")

    # Try environment variable
    env_value = os.environ.get("OMF2_UI_AUTOREFRESH", "").lower()
    if env_value in ("1", "true", "yes"):
        return True

    # Default to False
    return False


def _get_api_base() -> str:
    """
    Get API base URL from configuration

    Tries in order:
    1. st.secrets['api']['base']
    2. Environment variable OMF2_API_BASE
    3. Fallback to http://127.0.0.1:5001

    Returns:
        API base URL
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, "secrets") and "api" in st.secrets:
            api_config = st.secrets.get("api")
            if api_config and "base" in api_config:
                return api_config["base"]
    except Exception as e:
        logger.debug(f"Could not read from st.secrets: {e}")

    # Try environment variable
    api_base = os.environ.get("OMF2_API_BASE")
    if api_base:
        return api_base

    # Fallback
    return "http://127.0.0.1:5001"


def fetch_last_refresh(group: str = "order_updates", timeout: float = 1.0) -> Optional[float]:
    """
    Fetch last refresh timestamp from API

    Defensive about JSON keys - handles both 'timestamp' and 'last_refresh'.

    Args:
        group: Refresh group name (default: order_updates)
        timeout: Request timeout in seconds (default: 1.0)

    Returns:
        Last refresh timestamp as float, or None if unavailable
    """
    try:
        api_base = _get_api_base()
        url = f"{api_base}/api/last_refresh"
        params = {"group": group}

        response = requests.get(url, params=params, timeout=timeout)

        if response.status_code == 200:
            data = response.json()

            # Defensive: check for both 'timestamp' and 'last_refresh' keys
            timestamp = data.get("timestamp") or data.get("last_refresh")

            if timestamp is not None:
                return float(timestamp)

        return None

    except requests.exceptions.Timeout:
        logger.debug(f"⚠️ Timeout fetching refresh timestamp for group '{group}'")
        return None
    except requests.exceptions.RequestException as e:
        logger.debug(f"⚠️ Request error fetching refresh timestamp for group '{group}': {e}")
        return None
    except Exception as e:
        logger.debug(f"⚠️ Error fetching refresh timestamp for group '{group}': {e}")
        return None


def ensure_autorefresh_state(group: str = "order_updates", interval_ms: int = 1000) -> None:
    """
    Ensure auto-refresh state is initialized

    Only attempts to use st_autorefresh when autorefresh is enabled via configuration.
    Uses manual polling fallback otherwise.

    Args:
        group: Refresh group name (default: order_updates)
        interval_ms: Polling interval in milliseconds (default: 1000)
    """
    # Check if autorefresh is enabled
    autorefresh_enabled = _get_autorefresh_enabled()

    if not autorefresh_enabled:
        # Autorefresh disabled, use manual polling
        logger.debug("AutoRefresh disabled via configuration, using manual polling")
        counter_key = f"refresh_counter_{group}"
        if counter_key not in st.session_state:
            st.session_state[counter_key] = 0
        return

    # Autorefresh is enabled, try to use streamlit_autorefresh
    if importlib.util.find_spec("streamlit_autorefresh") is not None:
        try:
            from streamlit_autorefresh import st_autorefresh

            # Auto-refresh at the specified interval
            st_autorefresh(interval=interval_ms, key=f"autorefresh_{group}")

            # Optional debug indicator (to be removed later)
            logger.debug(f"✅ AutoRefresh active for group '{group}' (interval: {interval_ms}ms)")

        except Exception as e:
            logger.debug(f"⚠️ Error using streamlit_autorefresh: {e}, falling back to manual polling")
            # Initialize counter for manual polling
            counter_key = f"refresh_counter_{group}"
            if counter_key not in st.session_state:
                st.session_state[counter_key] = 0
    else:
        logger.debug("⚠️ streamlit_autorefresh not installed, using manual polling fallback")
        # Initialize counter for manual polling
        counter_key = f"refresh_counter_{group}"
        if counter_key not in st.session_state:
            st.session_state[counter_key] = 0


def check_and_reload(group: str = "order_updates", reload_callback=None, interval_ms: int = 1000) -> bool:
    """
    Check if refresh is needed and trigger reload

    This is the robust poll/compare snippet that:
    1. Ensures auto-refresh state is initialized
    2. Fetches current timestamp from API
    3. Compares with last known timestamp
    4. Calls reload_callback if timestamp increased

    Args:
        group: Refresh group name (default: order_updates)
        reload_callback: Optional function to call when reload is needed
        interval_ms: Polling interval in milliseconds (default: 1000)

    Returns:
        True if reload was triggered, False otherwise
    """
    # Ensure auto-refresh is initialized
    ensure_autorefresh_state(group=group, interval_ms=interval_ms)

    # Fetch current timestamp from API
    current_timestamp = fetch_last_refresh(group=group)

    if current_timestamp is None:
        # API unavailable or no timestamp yet
        logger.debug(f"No timestamp available for group '{group}'")
        return False

    # Get last known timestamp from session state
    session_key = f"{group}_last_refresh_timestamp"
    last_timestamp = st.session_state.get(session_key)

    # Check if reload is needed
    if last_timestamp is None or current_timestamp > last_timestamp:
        logger.debug(f"🔄 Refresh detected for group '{group}' (current: {current_timestamp}, last: {last_timestamp})")

        # Update session state
        st.session_state[session_key] = current_timestamp

        # Call reload callback if provided
        if reload_callback:
            try:
                reload_callback()
                logger.debug(f"✅ Reload callback executed for group '{group}'")
            except Exception as e:
                logger.error(f"❌ Error in reload callback for group '{group}': {e}")

        return True

    return False
