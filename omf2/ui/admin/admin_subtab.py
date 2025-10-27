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


def _is_streamlit_autorefresh_installed() -> bool:
    """
    Check if streamlit_autorefresh package is installed

    Returns:
        True if package is installed, False otherwise
    """
    return importlib.util.find_spec("streamlit_autorefresh") is not None


def _get_mqtt_ws_url() -> str:
    """
    Get MQTT WebSocket URL from configuration

    Tries in order:
    1. st.secrets['mqtt']['ws_url']
    2. Environment variable OMF2_UI_MQTT_WS_URL
    3. Empty string (not configured)

    Returns:
        MQTT WebSocket URL if configured, empty string otherwise
    """
    # Try Streamlit secrets first
    try:
        if hasattr(st, "secrets") and "mqtt" in st.secrets:
            mqtt_config = st.secrets.get("mqtt")
            if mqtt_config and "ws_url" in mqtt_config:
                url = mqtt_config["ws_url"]
                if url:
                    return str(url)
    except Exception as e:
        logger.debug(f"Could not read MQTT config from st.secrets: {e}")

    # Try environment variable
    env_url = os.environ.get("OMF2_UI_MQTT_WS_URL", "")
    if env_url:
        return env_url

    return ""


def _get_refresh_trigger_groups() -> dict:
    """
    Get configured refresh trigger groups from secrets

    Returns:
        Dict of refresh trigger groups or empty dict if not configured
    """
    try:
        if hasattr(st, "secrets") and "ui" in st.secrets:
            ui_config = st.secrets.get("ui")
            if ui_config and "refresh_triggers" in ui_config:
                return dict(ui_config["refresh_triggers"])
    except Exception as e:
        logger.debug(f"Could not read refresh_triggers from st.secrets: {e}")

    return {}


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
            label="AutoRefresh Configured", value=f"{status_icon} {'Enabled' if autorefresh_enabled else 'Disabled'}"
        )

        if autorefresh_enabled:
            # Show configuration source
            if os.environ.get("OMF2_UI_AUTOREFRESH", "").lower() in ("1", "true", "yes"):
                st.caption("📝 Source: Environment variable `OMF2_UI_AUTOREFRESH`")
            else:
                st.caption("📝 Source: Streamlit secrets `[ui].autorefresh`")
        else:
            st.caption("💡 To enable: Set `OMF2_UI_AUTOREFRESH=1` or add `[ui].autorefresh = true` to secrets")

    with col2:
        autorefresh_installed = _is_streamlit_autorefresh_installed()
        status_icon = "✅" if autorefresh_installed else "❌"
        st.metric(
            label="streamlit_autorefresh Installed", value=f"{status_icon} {'Yes' if autorefresh_installed else 'No'}"
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
        st.warning(
            "⚠️ AutoRefresh is enabled but `streamlit-autorefresh` is not installed. Install it to use this feature."
        )
    elif not autorefresh_enabled and autorefresh_installed:
        st.info("ℹ️ AutoRefresh is disabled. The package is installed and ready to use when enabled.")
    else:
        st.info("ℹ️ AutoRefresh is disabled and package is not installed.")

    # MQTT UI Refresh Status Section
    st.markdown("---")
    st.markdown("### MQTT UI Refresh Feature Status")

    mqtt_ws_url = _get_mqtt_ws_url()
    mqtt_enabled = bool(mqtt_ws_url)

    col1, col2 = st.columns(2)

    with col1:
        status_icon = "✅" if mqtt_enabled else "❌"
        st.metric(
            label="MQTT WebSocket Configured",
            value=f"{status_icon} {'Enabled' if mqtt_enabled else 'Disabled'}",
        )

        if mqtt_enabled:
            st.caption(f"🔌 Broker: `{mqtt_ws_url}`")
            # Show configuration source
            if os.environ.get("OMF2_UI_MQTT_WS_URL"):
                st.caption("📝 Source: Environment variable `OMF2_UI_MQTT_WS_URL`")
            else:
                st.caption("📝 Source: Streamlit secrets `[mqtt].ws_url`")
        else:
            st.caption(
                "💡 To enable: Set `OMF2_UI_MQTT_WS_URL=ws://broker:9001` or add `[mqtt].ws_url` to secrets"
            )

    with col2:
        refresh_triggers = _get_refresh_trigger_groups()
        trigger_count = len(refresh_triggers)

        st.metric(
            label="Configured Refresh Groups",
            value=f"{trigger_count} group{'s' if trigger_count != 1 else ''}",
        )

        if refresh_triggers:
            st.caption(f"📋 Groups: {', '.join(refresh_triggers.keys())}")
        else:
            st.caption("💡 Default groups: order_updates, sensor_data")

    # MQTT feature status
    st.markdown("---")
    
    # Check if MQTT publish refresh is enabled (gateway-side)
    mqtt_publish_enabled = bool(os.environ.get("OMF2_UI_REFRESH_VIA_MQTT"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="MQTT Publish (Gateway)",
            value=f"{'✅ Enabled' if mqtt_publish_enabled else '❌ Disabled'}",
        )
        if mqtt_publish_enabled:
            st.caption("📝 Business functions publish to `omf2/ui/refresh/{group}`")
        else:
            st.caption("💡 To enable: Set `OMF2_UI_REFRESH_VIA_MQTT=1`")
    
    with col2:
        st.metric(
            label="MQTT Subscribe (UI)",
            value=f"{'✅ Enabled' if mqtt_enabled else '❌ Disabled'}",
        )
        if mqtt_enabled:
            st.caption("🔌 UI components subscribe via WebSocket")
        else:
            st.caption("💡 Configure WebSocket URL to enable")
    
    st.markdown("---")
    if mqtt_publish_enabled and mqtt_enabled:
        st.success("✅ Full MQTT UI Refresh pipeline is active (Gateway → MQTT → UI)")
        st.info(
            "📨 Test with: `mosquitto_pub -t omf2/ui/refresh/order_updates -m '{\"ts\": 12345, \"source\":\"test\"}'`"
        )
    elif mqtt_publish_enabled and not mqtt_enabled:
        st.warning("⚠️ Gateway publishes MQTT refresh events but UI is not configured to receive them")
    elif not mqtt_publish_enabled and mqtt_enabled:
        st.warning("⚠️ UI is configured to receive MQTT events but Gateway is not publishing them")
    else:
        st.info(
            "ℹ️ MQTT UI Refresh is disabled. Enable both Gateway publish and UI subscribe for real-time updates."
        )
