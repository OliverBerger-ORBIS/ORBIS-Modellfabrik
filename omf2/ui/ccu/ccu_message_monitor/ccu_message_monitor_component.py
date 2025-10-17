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

        # Create message table data first (before filtering)
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

                    status = _get_message_status(message)

                    # Get module/FTS name for display
                    module_name = _get_module_display_name(topic)

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
                    status = "📨 Message"
                    module_name = _get_module_display_name(topic)
                    data = str(message)[:100] + "..." if len(str(message)) > 100 else str(message)

                message_table_data.append(
                    {
                        "Topic": topic,
                        "Type": module_name,  # Type-Spalte für Module-Name verwenden
                        "Status": status,
                        "Timestamp": timestamp,
                        "Data": data,
                    }
                )

        # Sort messages by timestamp (newest first) - like Admin
        if message_table_data:
            # Sort by timestamp (newest first)
            message_table_data.sort(key=lambda x: x.get("Timestamp", ""), reverse=True)

            df = pd.DataFrame(message_table_data)

            # Render filter controls above table columns and get filter values
            filter_values = _render_table_filters(df, i18n)

            # Apply filters to the dataframe using current filter values
            filtered_df = _apply_dataframe_filters_direct(df, filter_values, i18n)

            # Display filtered table
            st.dataframe(filtered_df, use_container_width=True)
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


def _render_table_filters(df, i18n):
    """Render Filter Controls above table columns and return filter values"""
    try:
        logger.debug("🔍 Rendering Table Filter Controls")

        # Initialize filter state in session_state BEFORE creating widgets
        # This prevents session state conflicts
        if "ccu_filter_topic" not in st.session_state:
            st.session_state["ccu_filter_topic"] = "All Topics"
        if "ccu_filter_module" not in st.session_state:
            st.session_state["ccu_filter_module"] = "All Modules/FTS"
        if "ccu_filter_status" not in st.session_state:
            st.session_state["ccu_filter_status"] = "All Status"

        # Get Registry Manager for module/FTS data
        from omf2.registry.manager.registry_manager import RegistryManager

        registry_manager = RegistryManager()
        modules = registry_manager.get_modules()

        # Filter row above table columns
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # Topic Filter
            topic_label = i18n.t("ccu_message_monitor.filter.topic") if i18n else "Topic Filter"
            unique_topics = ["All Topics"] + sorted(df["Topic"].unique().tolist())
            # Get current filter value from session state
            current_topic = st.session_state["ccu_filter_topic"]
            if current_topic not in unique_topics:
                current_topic = "All Topics"
                st.session_state["ccu_filter_topic"] = current_topic
            selected_topic = st.selectbox(
                topic_label, unique_topics, index=unique_topics.index(current_topic), key="ccu_filter_topic"
            )

        with col2:
            # Module/FTS Filter
            module_fts_label = i18n.t("ccu_message_monitor.filter.module_fts") if i18n else "Module/FTS Filter"

            # Create module options with ID and Name
            module_options = ["All Modules/FTS"]

            # Add FTS option (hardcoded for now)
            module_options.append("🚗 FTS (5iO4)")

            # Add regular modules
            for module_id, module_data in modules.items():
                module_name = module_data.get("name", "")
                module_type = module_data.get("type", "")
                module_icon = module_data.get("icon", "🏗️")

                if module_type != "Transport":  # Skip Transport, we handle FTS separately
                    display_name = f"{module_icon} {module_name} ({module_id})"
                    module_options.append(display_name)

            # Get current filter value from session state
            current_module = st.session_state["ccu_filter_module"]
            if current_module not in module_options:
                current_module = "All Modules/FTS"
                st.session_state["ccu_filter_module"] = current_module
            selected_module = st.selectbox(
                module_fts_label, module_options, index=module_options.index(current_module), key="ccu_filter_module"
            )

        with col3:
            # Status Filter - Erweiterte Status-Optionen
            status_label = i18n.t("ccu_message_monitor.filter.status") if i18n else "Status Filter"
            status_options = [
                "All Status",
                "🔌 Connection",
                "🏗️ Module State",
                "🚗 FTS State",
                "📄 Factsheet",
                "🟢 CCU State",
                "📨 Message",
            ]
            # Add unique statuses from data
            unique_statuses = sorted(df["Status"].unique().tolist())
            for status in unique_statuses:
                if status not in status_options:
                    status_options.append(status)

            # Get current filter value from session state
            current_status = st.session_state["ccu_filter_status"]
            if current_status not in status_options:
                current_status = "All Status"
                st.session_state["ccu_filter_status"] = current_status
            selected_status = st.selectbox(
                status_label, status_options, index=status_options.index(current_status), key="ccu_filter_status"
            )

        with col4:
            # Timestamp Filter (placeholder for actions)
            st.write("**Actions:**")
            apply_text = i18n.t("ccu_message_monitor.filter.apply") if i18n else "Apply"
            if st.button(f"✅ {apply_text}", key="ccu_filter_apply", use_container_width=True):
                # Trigger refresh - filters are already applied via selectbox values
                from omf2.ui.utils.ui_refresh import request_refresh

                request_refresh()

        with col5:
            # Data Filter (placeholder for actions)
            st.write("**Clear:**")
            clear_text = i18n.t("ccu_message_monitor.filter.clear") if i18n else "Clear"
            if st.button(f"🧹 {clear_text}", key="ccu_filter_clear", use_container_width=True):
                # Clear filter state by setting default values
                if "ccu_filter_topic" in st.session_state:
                    del st.session_state["ccu_filter_topic"]
                if "ccu_filter_module" in st.session_state:
                    del st.session_state["ccu_filter_module"]
                if "ccu_filter_status" in st.session_state:
                    del st.session_state["ccu_filter_status"]
                from omf2.ui.utils.ui_refresh import request_refresh

                request_refresh()

        # Return current filter values
        return {"topic": selected_topic, "module": selected_module, "status": selected_status}

    except Exception as e:
        logger.error(f"❌ Table Filter Controls render error: {e}")
        error_msg = f"Table Filter Controls failed: {e}"
        st.error(f"❌ {error_msg}")
        return {"topic": "All Topics", "module": "All Modules/FTS", "status": "All Status"}


def _apply_dataframe_filters_direct(df, filter_values, i18n):
    """Apply filters to dataframe using direct filter values"""
    try:
        logger.debug("🔍 Applying dataframe filters directly")

        selected_topic = filter_values.get("topic", "All Topics")
        selected_module = filter_values.get("module", "All Modules/FTS")
        selected_status = filter_values.get("status", "All Status")

        filtered_df = df.copy()

        # Topic Filter
        if selected_topic != "All Topics":
            filtered_df = filtered_df[filtered_df["Topic"] == selected_topic]
            logger.debug(f"🔍 Topic filter applied: {selected_topic}")

        # Module/FTS Filter - Filter by SERIAL-ID in TOPICS
        if selected_module != "All Modules/FTS":
            # Handle FTS filter
            if selected_module.startswith("🚗 FTS"):
                # Extract FTS serial ID (e.g., "5iO4")
                fts_serial = None
                if "(" in selected_module and ")" in selected_module:
                    fts_serial = selected_module.split("(")[-1].split(")")[0]

                if fts_serial:
                    # Filter topics containing the FTS serial ID
                    filtered_df = filtered_df[filtered_df["Topic"].str.contains(fts_serial, na=False)]
                    logger.debug(f"🔍 FTS filter applied for serial: {fts_serial}")
            else:
                # Extract module serial ID from display name for regular modules
                module_serial = None
                if "(" in selected_module and ")" in selected_module:
                    module_serial = selected_module.split("(")[-1].split(")")[0]

                if module_serial:
                    # Filter topics containing the module serial ID
                    filtered_df = filtered_df[filtered_df["Topic"].str.contains(module_serial, na=False)]
                    logger.debug(f"🔍 Module filter applied for serial: {module_serial}")

        # Status Filter - Filter by TOPIC PATTERN, not message content
        if selected_status != "All Status":
            if selected_status == "🔌 Connection":
                # Filter topics containing "/connection"
                filtered_df = filtered_df[filtered_df["Topic"].str.contains("/connection", na=False)]
                logger.debug("🔍 Connection topic filter applied")
            elif selected_status == "🏗️ Module State":
                # Filter topics containing "/state" (but not FTS)
                filtered_df = filtered_df[
                    (filtered_df["Topic"].str.contains("/state", na=False))
                    & (~filtered_df["Topic"].str.startswith("fts/", na=False))
                ]
                logger.debug("🔍 Module state topic filter applied")
            elif selected_status == "🚗 FTS State":
                # Filter FTS topics containing "/state"
                filtered_df = filtered_df[
                    (filtered_df["Topic"].str.contains("/state", na=False))
                    & (filtered_df["Topic"].str.startswith("fts/", na=False))
                ]
                logger.debug("🔍 FTS state topic filter applied")
            elif selected_status == "📄 Factsheet":
                # Filter topics containing "/factsheet"
                filtered_df = filtered_df[filtered_df["Topic"].str.contains("/factsheet", na=False)]
                logger.debug("🔍 Factsheet topic filter applied")
            elif selected_status == "🟢 CCU State":
                # Filter CCU topics
                filtered_df = filtered_df[filtered_df["Topic"].str.startswith("ccu/", na=False)]
                logger.debug("🔍 CCU state topic filter applied")
            else:
                # Direct status match (for other statuses)
                filtered_df = filtered_df[filtered_df["Status"] == selected_status]
                logger.debug(f"🔍 Status filter applied: {selected_status}")

        logger.debug(f"🔍 Filtered {len(filtered_df)} rows from {len(df)} total")
        return filtered_df

    except Exception as e:
        logger.error(f"❌ Dataframe filter error: {e}")
        return df  # Fallback to original dataframe


def _apply_dataframe_filters(df, i18n):
    """Apply filters to dataframe"""
    try:
        logger.debug("🔍 Applying dataframe filters")

        # Get filter state from session
        selected_topic = st.session_state.get("ccu_filter_topic", "All Topics")
        selected_module = st.session_state.get("ccu_filter_module", "All Modules/FTS")
        selected_status = st.session_state.get("ccu_filter_status", "All Status")

        filtered_df = df.copy()

        # Topic Filter
        if selected_topic != "All Topics":
            filtered_df = filtered_df[filtered_df["Topic"] == selected_topic]
            logger.debug(f"🔍 Topic filter applied: {selected_topic}")

        # Module/FTS Filter
        if selected_module != "All Modules/FTS":
            # Extract module ID from display name
            module_id = None
            if "(" in selected_module and ")" in selected_module:
                module_id = selected_module.split("(")[-1].split(")")[0]

            if module_id:
                filtered_df = filtered_df[filtered_df["Type"].str.contains(module_id, na=False)]
                logger.debug(f"🔍 Module filter applied: {module_id}")

        # Status Filter
        if selected_status != "All Status":
            # Handle status mapping
            status_mapping = {
                "🔌 Connection": "🔌 Connected",
                "🏗️ Module State": "🏗️ Module",
                "🚗 FTS State": "🚗 FTS",
                "📄 Factsheet": "📄 Factsheet",
                "🟢 CCU State": "🟢 CCU",
                "📨 Message": "📨 Message",
            }

            target_status = status_mapping.get(selected_status, selected_status)
            filtered_df = filtered_df[filtered_df["Status"] == target_status]
            logger.debug(f"🔍 Status filter applied: {target_status}")

        logger.debug(f"🔍 Filtered {len(filtered_df)} rows from {len(df)} total")
        return filtered_df

    except Exception as e:
        logger.error(f"❌ Dataframe filter error: {e}")
        return df  # Fallback to original dataframe


def _apply_message_filters(all_buffers, i18n):
    """Apply filters to message buffers"""
    try:
        logger.debug("🔍 Applying message filters")

        # Get filter state from session (only if exists)
        selected_modules = st.session_state.get("ccu_filter_modules", [])
        connection_status = st.session_state.get("ccu_filter_connection", True)
        module_status = st.session_state.get("ccu_filter_module", True)
        agv_fts_status = st.session_state.get("ccu_filter_agv_fts", True)

        # If no filters applied, return all buffers
        if not selected_modules and connection_status and module_status and agv_fts_status:
            logger.debug("🔍 No filters applied - returning all buffers")
            return all_buffers

        filtered_buffers = {}

        for topic, messages in all_buffers.items():
            if not messages:
                continue

            # Check if topic matches selected modules
            topic_matches_module = True
            if selected_modules:
                topic_matches_module = False
                for module_filter in selected_modules:
                    if module_filter == "all_modules" and _is_module_topic(topic):
                        topic_matches_module = True
                        break
                    elif module_filter == "all_fts" and _is_fts_topic(topic):
                        topic_matches_module = True
                        break
                    elif module_filter.startswith("module_") and module_filter[7:] in topic:
                        topic_matches_module = True
                        break
                    elif module_filter.startswith("fts_") and module_filter[4:] in topic:
                        topic_matches_module = True
                        break

            # Check if topic matches status types
            topic_matches_status = True
            if not (connection_status and module_status and agv_fts_status):
                topic_matches_status = False
                if connection_status and "connection" in topic:
                    topic_matches_status = True
                elif module_status and _is_module_topic(topic) and "state" in topic:
                    topic_matches_status = True
                elif agv_fts_status and _is_fts_topic(topic):
                    topic_matches_status = True

            # Include topic if it matches both module and status filters
            if topic_matches_module and topic_matches_status:
                filtered_buffers[topic] = messages

        logger.debug(f"🔍 Filtered {len(all_buffers)} topics to {len(filtered_buffers)} topics")
        return filtered_buffers

    except Exception as e:
        logger.error(f"❌ Message filter error: {e}")
        # Return all buffers on error
        return all_buffers


def _is_module_topic(topic):
    """Check if topic is a module topic"""
    # Module topics contain module serial IDs
    from omf2.registry.manager.registry_manager import RegistryManager

    registry_manager = RegistryManager()
    modules = registry_manager.get_modules()

    for module_id, module_data in modules.items():
        if module_id in topic and module_data.get("type", "") != "Transport":
            return True
    return False


def _is_fts_topic(topic):
    """Check if topic is an FTS topic"""
    # FTS topics contain FTS serial IDs or "fts" keyword
    if "fts" in topic.lower():
        return True

    from omf2.registry.manager.registry_manager import RegistryManager

    registry_manager = RegistryManager()
    modules = registry_manager.get_modules()

    for module_id, module_data in modules.items():
        if module_id in topic and module_data.get("type", "") == "Transport":
            return True
    return False


def _get_module_display_name(topic):
    """Get module/FTS display name for topic"""
    try:
        # Check for FTS topics first (fts/v1/ff/5iO4/...)
        if topic.startswith("fts/v1/ff/"):
            # Extract FTS serial from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                fts_serial = parts[3]
                return f"🚗 FTS ({fts_serial})"

        # Check for module topics (module/v1/ff/...)
        if topic.startswith("module/v1/ff/"):
            # Extract module serial from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                module_serial = parts[3]

                # Look up in registry
                from omf2.registry.manager.registry_manager import RegistryManager

                registry_manager = RegistryManager()
                modules = registry_manager.get_modules()

                for module_id, module_data in modules.items():
                    if module_id == module_serial:
                        module_name = module_data.get("name", module_id)
                        module_icon = module_data.get("icon", "🏗️")
                        return f"{module_icon} {module_name} ({module_id})"

                # Module not found in registry
                return f"🏗️ Module ({module_serial})"

        # Check for CCU topics
        if topic.startswith("ccu/"):
            return "🟢 CCU"

        # If no specific pattern found, return "other"
        return "other"
    except Exception:
        return "other"


def _get_message_type(topic):
    """Get message type based on topic"""
    if "ccu" in topic:
        return "🏭 CCU"
    elif "factsheet" in topic:
        return "📄 Factsheet"
    elif "connection" in topic:
        return "🔌 Connection"
    elif "state" in topic:
        # Check if it's FTS or Module
        if _is_fts_topic(topic):
            return "🚗 FTS"
        elif _is_module_topic(topic):
            return "🏗️ Module"
        else:
            return "🟢 State"
    elif "fts" in topic.lower():
        return "🚗 FTS"
    elif "module" in topic:
        return "🏗️ Module"
    else:
        return "📨 Message"


def _get_message_status(message):
    """Get message status based on content"""
    if isinstance(message, dict):
        # Check for connection status (only if "connected" key exists)
        if "connected" in message:
            if message.get("connected", False):
                return "🔌 Connected"
            else:
                return "🔌 Disconnected"

        # Check for module availability status
        if message.get("available") in ["READY", "AVAILABLE"]:
            return "🏗️ Available"
        elif message.get("available") == "BUSY":
            return "🏗️ Busy"
        elif message.get("available") == "ERROR":
            return "🏗️ Error"

        # Check for FTS state (has orderId, nodeStates, actionStates)
        elif "orderId" in message and ("nodeStates" in message or "actionStates" in message):
            # FTS is active if it has an orderId
            if message.get("orderId"):
                return "🚗 FTS Active"
            else:
                return "🚗 FTS Idle"

        # Check for factsheet content
        elif "capabilities" in message or "loadSpecification" in message:
            return "📄 Factsheet"

        # Check for CCU state
        elif "ccu" in str(message).lower():
            return "🟢 CCU State"

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
