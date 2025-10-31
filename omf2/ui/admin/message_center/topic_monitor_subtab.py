#!/usr/bin/env python3
"""
Topic Monitor Subtab - Live MQTT Topic Monitoring with Category Filtering
Gateway-Pattern konform: Nutzt AdminGateway statt direkten MQTT-Client
"""

import time

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.message_utils import MessageRow
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_topic_monitor_subtab(admin_gateway):
    """Render Topic Monitor Subtab with live MQTT topic monitoring

    Args:
        admin_gateway: AdminGateway Instanz (Gateway-Pattern)
    """
    logger.info(f"{UISymbols.get_functional_icon('topic_driven')} Rendering Topic Monitor Subtab")

    try:
        # Ensure i18n manager present (no assignment to avoid linter warnings)
        st.session_state.get("i18n_manager")

        st.subheader(f"{UISymbols.get_functional_icon('topic_driven')} Live MQTT Topic Monitor")
        st.markdown("**Real-time monitoring of MQTT topics with category filtering**")

        # Connection status shown in sidebar only

        # Topic filter and category filter
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            topic_filter = st.text_input(
                "Filter topics (supports wildcards like test/*):",
                key="topic_filter",
                placeholder="Leave empty to show all topics",
            )

        with col2:
            # Topic Category Filter
            topic_categories = ["Alle", "ccu", "module", "txt", "nodered", "fts"]
            category_filter = st.selectbox(
                "🏷️ Topic-Kategorie", options=topic_categories, index=0, key="monitor_category_filter"
            )

        with col3:
            # Manual refresh only
            if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh Now", key="manual_refresh_monitor"):
                request_refresh()

        # Get all topic buffers via Gateway
        all_buffers = admin_gateway.get_all_message_buffers()
        if not all_buffers:
            st.info("📋 No topics available yet. Topics will appear as messages are received.")
            return

        # Filter topics based on input
        filtered_topics = []
        if topic_filter:
            import fnmatch

            filtered_topics = [topic for topic in all_buffers.keys() if fnmatch.fnmatch(topic, topic_filter)]
        else:
            filtered_topics = list(all_buffers.keys())

        # Apply category filter
        if category_filter != "Alle":
            filtered_topics = [
                topic for topic in filtered_topics if MessageRow.get_category_for_topic(topic) == category_filter
            ]

        # Sort topics by most recent activity
        def get_latest_timestamp(topic):
            buffer = all_buffers[topic]
            if buffer and len(buffer) > 0:
                return buffer[-1].get("mqtt_timestamp", 0)
            return 0

        filtered_topics.sort(key=get_latest_timestamp, reverse=True)

        # Display filtered topics
        if not filtered_topics:
            st.info(f"{UISymbols.get_functional_icon('search')} No topics match your current filters.")
            return

        st.info(f"📄 Showing first 20 of {len(filtered_topics)} topics. Use topic filter to narrow down results.")

        # Display topics with their latest messages
        for i, topic in enumerate(filtered_topics[:20]):
            buffer = all_buffers[topic]
            with st.expander(f"📨 {topic}", expanded=(i < 3)):
                if buffer and len(buffer) > 0:
                    latest_message = buffer[-1]
                    if "mqtt_timestamp" in latest_message:
                        timestamp_str = time.strftime(
                            "%Y-%m-%d %H:%M:%S", time.localtime(latest_message["mqtt_timestamp"])
                        )
                        st.caption(f"⏰ Last updated: {timestamp_str}")
                    if "raw_payload" in latest_message:
                        st.text(f"Raw payload: {latest_message['raw_payload']}")
                    else:
                        # Entferne mqtt_timestamp für saubere Anzeige
                        display_dict = {k: v for k, v in latest_message.items() if k != "mqtt_timestamp"}
                        st.json(display_dict)
                else:
                    st.text("No messages in buffer")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Topic Monitor Subtab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Topic Monitor failed: {e}")
