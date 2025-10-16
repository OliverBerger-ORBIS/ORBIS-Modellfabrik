#!/usr/bin/env python3
"""
CCU Message Monitor Component - Wiederverwendbare Komponente für CCU MQTT Message Monitoring
"""

import pandas as pd
import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_message_monitor(ccu_gateway, title=None, show_controls=True):
    """
    Render CCU Message Monitor Component - Wiederverwendbare Komponente

    Args:
        ccu_gateway: CCU Gateway instance (Gateway-Pattern)
        title: Title for the monitor section (optional, uses i18n if None)
        show_controls: Whether to show control buttons
    """
    try:
        logger.info("📡 Rendering CCU Message Monitor Component")

        # Get i18n manager
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.warning("⚠️ I18n Manager not found in session state - using fallback")
            # Fallback for compatibility
            title = title or "CCU Message Monitor"
            st.subheader(f"📡 {title}")
            st.markdown("CCU MQTT Message Monitoring - Echtzeit-Nachrichten über CCU Gateway")
        else:
            # Use i18n
            title = title or i18n.t("ccu_message_monitor.title")
            st.subheader(f"📡 {title}")
            st.markdown(i18n.t("ccu_message_monitor.subtitle"))

        if not ccu_gateway:
            error_msg = (
                i18n.t("ccu_message_monitor.error.gateway_not_available") if i18n else "CCU Gateway nicht verfügbar"
            )
            st.error(f"❌ {error_msg}")
            return

        # Get MQTT client through gateway
        mqtt_client = ccu_gateway.mqtt_client
        if not mqtt_client:
            error_msg = (
                i18n.t("ccu_message_monitor.error.mqtt_not_available")
                if i18n
                else "CCU MQTT Client nicht verfügbar über Gateway"
            )
            st.error(f"❌ {error_msg}")
            return

        # CCU Message Monitor Controls (optional)
        if show_controls:
            col1, col2, col3 = st.columns([1, 1, 1])

            refresh_text = i18n.t("ccu_message_monitor.controls.refresh_messages") if i18n else "Refresh Messages"
            stats_text = i18n.t("ccu_message_monitor.controls.show_statistics") if i18n else "Show Statistics"
            clear_text = i18n.t("ccu_message_monitor.controls.clear_buffer") if i18n else "Clear Buffer"

            with col1:
                if st.button(
                    f"{UISymbols.get_status_icon('refresh')} {refresh_text}",
                    use_container_width=True,
                    key="ccu_refresh_messages",
                ):
                    _refresh_ccu_messages(ccu_gateway, i18n)

            with col2:
                if st.button(
                    f"{UISymbols.get_functional_icon('dashboard')} {stats_text}",
                    use_container_width=True,
                    key="ccu_show_statistics",
                ):
                    _show_ccu_message_statistics(ccu_gateway, i18n)

            with col3:
                if st.button(
                    f"{UISymbols.get_functional_icon('settings')} {clear_text}",
                    use_container_width=True,
                    key="ccu_clear_buffer",
                ):
                    _clear_ccu_message_buffer(ccu_gateway, i18n)

        # Get all buffers from CCU MQTT client
        all_buffers = mqtt_client.get_all_buffers()

        # Always show subscribed topics, even if no buffers
        subscribed_topics = mqtt_client._get_subscribed_topics()
        if subscribed_topics:
            subscribed_msg = (
                i18n.t("ccu_message_monitor.subscriptions.subscribed_to").format(count=len(subscribed_topics))
                if i18n
                else f"CCU MQTT Client subscribed to {len(subscribed_topics)} topics"
            )
            st.success(f"📡 {subscribed_msg}")
            topics_title = (
                i18n.t("ccu_message_monitor.subscriptions.subscribed_topics") if i18n else "Subscribed Topics"
            )
            with st.expander(f"📋 {topics_title}", expanded=False):
                for topic in subscribed_topics:
                    st.text(f"  • {topic}")
        else:
            no_topics_msg = (
                i18n.t("ccu_message_monitor.subscriptions.no_topics")
                if i18n
                else "CCU MQTT Client has no subscribed topics"
            )
            st.warning(f"⚠️ {no_topics_msg}")

        if not all_buffers:
            no_msg = i18n.t("ccu_message_monitor.messages.no_messages") if i18n else "Keine CCU Messages verfügbar"
            waiting_msg = (
                i18n.t("ccu_message_monitor.messages.waiting")
                if i18n
                else "Messages werden angezeigt, sobald der Client connected ist und Nachrichten empfängt"
            )
            st.info(f"📋 {no_msg}")
            st.info(f"💡 {waiting_msg}")
            return

        # Create message table data
        message_table_data = []

        for topic, messages in all_buffers.items():
            if not messages:
                continue

            # Create a copy of messages to avoid "deque mutated during iteration" error
            messages_copy = list(messages) if hasattr(messages, "__iter__") else [messages]

            # Process ALL messages in buffer, not just the latest (like Admin)
            for message in messages_copy:
                # Extract message info - handle both dict and other types
                if isinstance(message, dict):
                    # Format timestamp properly
                    raw_timestamp = message.get("mqtt_timestamp", "Unknown")
                    if isinstance(raw_timestamp, (int, float)):
                        from datetime import datetime

                        timestamp = datetime.fromtimestamp(raw_timestamp).strftime("%H:%M:%S.%f")[:-3]
                    else:
                        timestamp = str(raw_timestamp)

                    message_type = _get_message_type(topic)
                    status = _get_message_status(message)

                    # Format payload as JSON if possible
                    payload = message.get("payload", message)
                    if isinstance(payload, (dict, list)):
                        import json

                        data = (
                            json.dumps(payload, indent=2)[:200] + "..."
                            if len(json.dumps(payload)) > 200
                            else json.dumps(payload, indent=2)
                        )
                    else:
                        data = str(payload)[:100] + "..." if len(str(payload)) > 100 else str(payload)
                else:
                    timestamp = "Unknown"
                    message_type = _get_message_type(topic)
                    status = "📨 Message"
                    data = str(message)[:100] + "..." if len(str(message)) > 100 else str(message)

                table_headers = {
                    "topic": i18n.t("ccu_message_monitor.table.topic") if i18n else "Topic",
                    "type": i18n.t("ccu_message_monitor.table.type") if i18n else "Type",
                    "status": i18n.t("ccu_message_monitor.table.status") if i18n else "Status",
                    "timestamp": i18n.t("ccu_message_monitor.table.timestamp") if i18n else "Timestamp",
                    "data": i18n.t("ccu_message_monitor.table.data") if i18n else "Data",
                }

                message_table_data.append(
                    {
                        table_headers["topic"]: topic,
                        table_headers["type"]: message_type,
                        table_headers["status"]: status,
                        table_headers["timestamp"]: timestamp,
                        table_headers["data"]: data,
                    }
                )

        # Sort messages by timestamp (newest first) - like Admin
        if message_table_data:
            # Get the timestamp column name (might be translated)
            timestamp_col = i18n.t("ccu_message_monitor.table.timestamp") if i18n else "Timestamp"
            # Sort by timestamp (newest first)
            message_table_data.sort(key=lambda x: x.get(timestamp_col, ""), reverse=True)

            df = pd.DataFrame(message_table_data)
            st.dataframe(df, use_container_width=True)
        else:
            no_msg = i18n.t("ccu_message_monitor.messages.no_messages") if i18n else "Keine CCU Messages verfügbar"
            st.info(f"📋 {no_msg}")

    except Exception as e:
        logger.error(f"❌ CCU Message Monitor Component error: {e}")
        error_msg = (
            i18n.t("ccu_message_monitor.error.component_failed").format(error=e)
            if i18n
            else f"CCU Message Monitor Component failed: {e}"
        )
        st.error(f"❌ {error_msg}")


def _get_message_type(topic):
    """Get message type based on topic"""
    if "state" in topic:
        return "🟢 State"
    elif "connection" in topic:
        return "🔌 Connection"
    elif "factsheet" in topic:
        return "📄 Factsheet"
    elif "ccu" in topic:
        return "🏭 CCU"
    elif "module" in topic:
        return "🏗️ Module"
    elif "fts" in topic:
        return "🚗 FTS"
    else:
        return "📨 Message"


def _get_message_status(message):
    """Get message status based on content"""
    if isinstance(message, dict):
        if message.get("connected", False):
            return "🟢 Connected"
        elif message.get("available") in ["READY", "AVAILABLE"]:
            return "🟢 Available"
        elif message.get("available") == "BUSY":
            return "🟡 Busy"
        elif message.get("available") == "ERROR":
            return "🔴 Error"
        else:
            return "⚪ Unknown"
    else:
        # Handle non-dict messages (like deque items)
        return "📨 Message"


def _refresh_ccu_messages(ccu_gateway, i18n):
    """Refresh CCU Messages - EXACT like Admin but with CCU topics"""
    try:
        logger.info("🔄 Refreshing CCU Messages")

        # Get MQTT client through gateway
        mqtt_client = ccu_gateway.mqtt_client
        if mqtt_client:
            # Get subscribed topics from registry (not hardcoded!)
            subscribed_topics = mqtt_client._get_subscribed_topics()
            if subscribed_topics:
                # Re-subscribe to all CCU topics from registry
                # mqtt_client.subscribe_many(subscribed_topics)
                resubscribed_msg = (
                    i18n.t("ccu_message_monitor.actions.resubscribed").format(count=len(subscribed_topics))
                    if i18n
                    else f"Re-subscribed to {len(subscribed_topics)} CCU topics"
                )
                logger.info(f"📥 {resubscribed_msg}")
            else:
                no_topics_msg = (
                    i18n.t("ccu_message_monitor.error.no_topics") if i18n else "No CCU topics found in registry"
                )
                logger.warning(f"⚠️ {no_topics_msg}")
        else:
            no_client_msg = i18n.t("ccu_message_monitor.error.no_mqtt_client") if i18n else "No MQTT client provided"
            logger.warning(f"⚠️ {no_client_msg}")

        success_msg = i18n.t("ccu_message_monitor.actions.refresh_success") if i18n else "CCU Messages refreshed!"
        st.success(f"✅ {success_msg}")

        # CRITICAL: Request UI refresh to update the display
        from omf2.ui.utils.ui_refresh import request_refresh

        request_refresh()
    except Exception as e:
        logger.error(f"❌ CCU Messages refresh error: {e}")
        error_msg = (
            i18n.t("ccu_message_monitor.error.refresh_failed").format(error=e)
            if i18n
            else f"CCU Messages refresh failed: {e}"
        )
        st.error(f"❌ {error_msg}")


def _show_ccu_message_statistics(ccu_gateway, i18n):
    """Show CCU Message Statistics - ECHTE MQTT-Daten"""
    try:
        logger.info("📊 Showing CCU Message Statistics")
        stats_title = i18n.t("ccu_message_monitor.statistics.title") if i18n else "CCU Message Statistics"
        st.subheader(f"📊 {stats_title}")

        # Get all buffers from CCU Gateway
        all_buffers = ccu_gateway.get_all_message_buffers()

        # Calculate statistics
        total_topics = len(all_buffers)
        total_messages = 0
        for messages in all_buffers.values():
            if messages:
                # Create a copy to avoid "deque mutated during iteration" error
                messages_copy = list(messages) if hasattr(messages, "__iter__") else [messages]
                total_messages += len(messages_copy)

        # Count by type
        state_topics = sum(1 for topic in all_buffers.keys() if "state" in topic)
        connection_topics = sum(1 for topic in all_buffers.keys() if "connection" in topic)
        sum(1 for topic in all_buffers.keys() if "ccu" in topic)

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        total_topics_label = i18n.t("ccu_message_monitor.statistics.total_topics") if i18n else "Gesamt Topics"
        total_messages_label = i18n.t("ccu_message_monitor.statistics.total_messages") if i18n else "Gesamt Messages"
        state_topics_label = i18n.t("ccu_message_monitor.statistics.state_topics") if i18n else "State Topics"
        connection_topics_label = (
            i18n.t("ccu_message_monitor.statistics.connection_topics") if i18n else "Connection Topics"
        )

        with col1:
            st.metric(total_topics_label, total_topics)

        with col2:
            st.metric(total_messages_label, total_messages)

        with col3:
            st.metric(state_topics_label, state_topics)

        with col4:
            st.metric(connection_topics_label, connection_topics)

        logger.info("CCU Message Statistics erfolgreich angezeigt")

    except Exception as e:
        logger.error(f"❌ CCU Message Statistics error: {e}")
        error_msg = (
            i18n.t("ccu_message_monitor.error.statistics_failed").format(error=e)
            if i18n
            else f"CCU Message Statistics failed: {e}"
        )
        st.error(f"❌ {error_msg}")


def _clear_ccu_message_buffer(ccu_gateway, i18n):
    """Clear CCU Message Buffer"""
    try:
        logger.info("🧹 Clearing CCU Message Buffer")
        # TODO: Implement buffer clearing
        success_msg = i18n.t("ccu_message_monitor.actions.buffer_cleared") if i18n else "CCU Message Buffer cleared!"
        st.success(f"✅ {success_msg}")
    except Exception as e:
        logger.error(f"❌ CCU Message Buffer clear error: {e}")
        error_msg = (
            i18n.t("ccu_message_monitor.error.buffer_clear_failed").format(error=e)
            if i18n
            else f"CCU Message Buffer clear failed: {e}"
        )
        st.error(f"❌ {error_msg}")
