#!/usr/bin/env python3
"""
Production Orders Refresh Helper

Provides a reusable pattern for integrating auto-refresh polling into CCU UI components.
This helper wraps the existing refresh_polling functionality with a convenient reload pattern.
"""

from omf2.common.logger import get_logger
from omf2.ui.common.refresh_polling import get_last_refresh_timestamp
import streamlit as st

logger = get_logger(__name__)


def check_and_reload(api_base: str, group: str, reload_callable, session_state_key: str = None):
    """
    Check for refresh triggers and reload data if needed.
    
    This function integrates with the existing refresh_polling infrastructure
    by checking the API for refresh timestamps and calling a reload function
    when data needs to be refreshed.
    
    Args:
        api_base: Base URL for the refresh API (e.g., "http://localhost:5001")
        group: Refresh group name (e.g., 'order_updates', 'module_updates')
        reload_callable: Function to call when reload is needed. Should return data.
        session_state_key: Optional key to store the last refresh timestamp in session state.
                          If None, uses f"{group}_last_refresh_timestamp"
    
    Returns:
        True if reload was triggered, False otherwise
    """
    # Determine session state key
    if session_state_key is None:
        session_state_key = f"{group}_last_refresh_timestamp"
    
    try:
        # Get current timestamp from API
        current_timestamp = get_last_refresh_timestamp(group)
        
        if current_timestamp is None:
            # API unavailable or no refresh yet
            return False
        
        # Get last known timestamp from session_state
        last_timestamp = st.session_state.get(session_state_key, None)
        
        # Check if refresh is needed
        if last_timestamp is None or current_timestamp > last_timestamp:
            logger.debug(f"🔄 Refresh detected for group '{group}' (new: {current_timestamp}, old: {last_timestamp})")
            
            # Update session_state with new timestamp
            st.session_state[session_state_key] = current_timestamp
            
            # Call reload function
            try:
                reload_callable()
                logger.info(f"✅ Successfully reloaded data for group '{group}'")
                return True
            except Exception as e:
                logger.error(f"❌ Error reloading data for group '{group}': {e}")
                raise
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in check_and_reload for group '{group}': {e}")
        return False
