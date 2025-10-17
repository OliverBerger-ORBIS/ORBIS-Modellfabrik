#!/usr/bin/env python3
"""
Example integration of CCU Message Monitor with CCU Gateway.

This shows how to use the message monitor component with live MQTT data
from the CCU Gateway.
"""

from typing import Any, Dict, List

import streamlit as st

try:
    from omf2.ccu import CCUGateway, ccu_mqtt_client
    from omf2.ui.ccu.ccu_message_monitor import render_ccu_message_monitor

    CCU_AVAILABLE = True
except ImportError:
    CCU_AVAILABLE = False


def get_ccu_messages(ccu_gateway: "CCUGateway", limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get messages from CCU Gateway message buffers.

    Args:
        ccu_gateway: CCU Gateway instance
        limit: Maximum number of messages to retrieve

    Returns:
        List of messages in the format expected by render_ccu_message_monitor
    """
    messages = []

    # Get messages from various CCU topics
    topics = [
        "ccu/state",
        "ccu/status",
        "ccu/control",
        "ccu/connection",
    ]

    for topic in topics:
        buffer = ccu_gateway.client.get_buffer(topic)
        messages.extend(buffer)

    # Also get workflow messages (with wildcard pattern)
    workflow_topics = [k for k in ccu_gateway.client._message_buffers.keys() if k.startswith("ccu/workflow/")]
    for topic in workflow_topics:
        buffer = ccu_gateway.client.get_buffer(topic)
        messages.extend(buffer)

    # Sort by timestamp and limit
    messages.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return messages[:limit]


def render_ccu_dashboard_with_monitor():
    """
    Example: Render CCU Dashboard with integrated Message Monitor.

    This function demonstrates how to integrate the message monitor
    into a larger dashboard.
    """
    if not CCU_AVAILABLE:
        st.error("❌ CCU components not available")
        return

    st.title("🏭 CCU Dashboard with Message Monitor")

    # Initialize CCU Gateway
    if "ccu_gateway" not in st.session_state:
        st.session_state.ccu_gateway = CCUGateway(ccu_mqtt_client)

    ccu_gateway = st.session_state.ccu_gateway

    # Connection status
    if ccu_gateway.is_connected():
        st.success("🟢 CCU MQTT Connected")
    else:
        st.error("🔴 CCU MQTT Disconnected")

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📡 Message Monitor", "⚙️ Settings"])

    with tab1:
        st.subheader("System Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Connection Status", "Connected" if ccu_gateway.is_connected() else "Disconnected")

        with col2:
            status_history = ccu_gateway.get_status_history(limit=10)
            st.metric("Recent Messages", len(status_history))

        with col3:
            latest_state = ccu_gateway.get_latest_state()
            state_status = latest_state.get("status", "unknown") if latest_state else "unknown"
            st.metric("System State", state_status.title())

    with tab2:
        st.subheader("CCU Message Monitor")

        # Get messages from CCU Gateway
        messages = get_ccu_messages(ccu_gateway, limit=100)

        if messages:
            # Render the message monitor with live data
            render_ccu_message_monitor(messages=messages)
        else:
            st.info("No messages available. Waiting for CCU messages...")
            st.markdown("**Tip:** Send some test messages to the CCU MQTT broker to see them here.")

            # Option to use sample data for testing
            if st.button("📝 Load Sample Data for Testing"):
                render_ccu_message_monitor(messages=None)

    with tab3:
        st.subheader("Settings")
        st.markdown(
            """
        **MQTT Configuration**

        Configure MQTT connection settings for the CCU Gateway.
        """
        )

        # Settings would go here
        st.info("Settings interface coming soon")


if __name__ == "__main__":
    st.set_page_config(
        page_title="CCU Dashboard with Monitor",
        page_icon="🏭",
        layout="wide",
    )

    render_ccu_dashboard_with_monitor()
