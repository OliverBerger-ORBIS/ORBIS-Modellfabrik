#!/usr/bin/env python3
"""
MQTT Subscriber Streamlit Component

A custom Streamlit component that connects to an MQTT broker via WebSocket,
subscribes to topics, and pushes received messages to Streamlit.

This component is opt-in and only activated when configured via environment
variables or Streamlit secrets.
"""

import os
from pathlib import Path
from typing import Optional

import streamlit.components.v1 as components

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Determine component path
_component_path = Path(__file__).parent / "frontend"

# Declare the component
_mqtt_subscriber_component = components.declare_component(
    "mqtt_subscriber",
    path=str(_component_path),
)


def mqtt_subscriber_component(
    broker_url: str,
    topic: str,
    client_id: Optional[str] = None,
    key: Optional[str] = None,
) -> Optional[dict]:
    """
    MQTT Subscriber Component

    Connects to an MQTT broker via WebSocket, subscribes to a topic,
    and returns received messages to Streamlit.

    Args:
        broker_url: WebSocket URL of the MQTT broker (e.g., 'ws://localhost:9001')
        topic: MQTT topic to subscribe to (e.g., 'omf2/ui/refresh/order_updates')
        client_id: Optional client ID for MQTT connection (auto-generated if None)
        key: Optional unique key for the component instance

    Returns:
        Dict containing the received message payload, or None if no message yet

    Example:
        >>> message = mqtt_subscriber_component(
        ...     broker_url='ws://localhost:9001',
        ...     topic='omf2/ui/refresh/order_updates',
        ...     key='ui_mqtt_orders'
        ... )
        >>> if message:
        ...     print(f"Received: {message}")
    """
    if not broker_url:
        logger.debug("⚠️ No broker URL provided to mqtt_subscriber_component")
        return None

    try:
        # Generate client_id if not provided
        if client_id is None:
            import random
            import string

            random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
            client_id = f"streamlit_ui_{random_suffix}"

        # Call the component
        result = _mqtt_subscriber_component(
            broker_url=broker_url,
            topic=topic,
            client_id=client_id,
            key=key,
        )

        return result

    except Exception as e:
        logger.error(f"❌ Error in mqtt_subscriber_component: {e}")
        return None


def get_mqtt_ws_url() -> Optional[str]:
    """
    Get MQTT WebSocket URL from configuration

    Tries in order:
    1. st.secrets['mqtt']['ws_url']
    2. Environment variable OMF2_UI_MQTT_WS_URL
    3. None (disabled)

    Returns:
        MQTT WebSocket URL if configured, None otherwise
    """
    try:
        import streamlit as st

        # Try Streamlit secrets first
        if hasattr(st, "secrets") and "mqtt" in st.secrets:
            mqtt_config = st.secrets.get("mqtt")
            if mqtt_config and "ws_url" in mqtt_config:
                url = mqtt_config["ws_url"]
                if url:
                    logger.debug(f"✅ Using MQTT WebSocket URL from secrets: {url}")
                    return url

    except Exception as e:
        logger.debug(f"Could not read MQTT config from st.secrets: {e}")

    # Try environment variable
    env_url = os.environ.get("OMF2_UI_MQTT_WS_URL")
    if env_url:
        logger.debug(f"✅ Using MQTT WebSocket URL from env: {env_url}")
        return env_url

    logger.debug("⚠️ MQTT WebSocket URL not configured")
    return None


def is_mqtt_ui_enabled() -> bool:
    """
    Check if MQTT UI refresh is enabled

    Returns:
        True if MQTT WebSocket URL is configured, False otherwise
    """
    return get_mqtt_ws_url() is not None
