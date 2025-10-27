#!/usr/bin/env python3
"""
Admin Status Subtab - System Configuration Status Display

Displays system configuration and feature status for administrators.
"""

import importlib.util
import os

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
        if hasattr(st, 'secrets') and 'ui' in st.secrets:
            ui_config = st.secrets.get('ui')
            if ui_config and 'autorefresh' in ui_config:
                return bool(ui_config['autorefresh'])
    except Exception as e:
        logger.debug(f"Could not read autorefresh from st.secrets: {e}")

    # Try environment variable
    env_value = os.environ.get('OMF2_UI_AUTOREFRESH', '').lower()
    if env_value in ('1', 'true', 'yes'):
        return True

    # Default to False
    return False


def _is_streamlit_autorefresh_installed() -> bool:
    """
    Check if streamlit_autorefresh package is installed

    Returns:
        True if package is installed, False otherwise
    """
    return importlib.util.find_spec("streamlit_autorefresh") is not None


def render_admin_subtab():
    """
    Render Admin Status Subtab

    Displays system configuration status including autorefresh settings.
    Safe to import and call - provides minimal status display.
    """
    logger.info("Rendering Admin Status Subtab")

    st.subheader("🔧 System Configuration Status")
    st.markdown("**Feature and dependency status for administrators**")

    # AutoRefresh Status Section
    st.markdown("---")
    st.markdown("### AutoRefresh Feature Status")

    col1, col2 = st.columns(2)

    with col1:
        autorefresh_enabled = _get_autorefresh_enabled()
        status_icon = "✅" if autorefresh_enabled else "❌"
        st.metric(
            label="AutoRefresh Configured",
            value=f"{status_icon} {'Enabled' if autorefresh_enabled else 'Disabled'}"
        )

        if autorefresh_enabled:
            # Show configuration source
            if os.environ.get('OMF2_UI_AUTOREFRESH', '').lower() in ('1', 'true', 'yes'):
                st.caption("📝 Source: Environment variable `OMF2_UI_AUTOREFRESH`")
            else:
                st.caption("📝 Source: Streamlit secrets `[ui].autorefresh`")
        else:
            st.caption("💡 To enable: Set `OMF2_UI_AUTOREFRESH=1` or add `[ui].autorefresh = true` to secrets")

    with col2:
        autorefresh_installed = _is_streamlit_autorefresh_installed()
        status_icon = "✅" if autorefresh_installed else "❌"
        st.metric(
            label="streamlit_autorefresh Installed",
            value=f"{status_icon} {'Yes' if autorefresh_installed else 'No'}"
        )

        if not autorefresh_installed:
            st.caption("💡 Install with: `pip install streamlit-autorefresh`")
        else:
            st.caption("✅ Package is available for use")

    # Combined status message
    st.markdown("---")
    if autorefresh_enabled and autorefresh_installed:
        st.success("✅ AutoRefresh feature is fully operational")
    elif autorefresh_enabled and not autorefresh_installed:
        st.warning("⚠️ AutoRefresh is enabled but `streamlit-autorefresh` is not installed. Install it to use this feature.")
    elif not autorefresh_enabled and autorefresh_installed:
        st.info("ℹ️ AutoRefresh is disabled. The package is installed and ready to use when enabled.")
    else:
        st.info("ℹ️ AutoRefresh is disabled and package is not installed.")
