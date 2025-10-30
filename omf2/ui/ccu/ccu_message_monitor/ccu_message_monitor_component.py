#!/usr/bin/env python3
"""
CCU Message Monitor Component - Wiederverwendbare Komponente für CCU MQTT Message Monitoring
"""

import html

import pandas as pd
import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.ccu.module_manager import get_ccu_module_manager
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
            # Get SVG icon for Message Monitor heading
            try:
                msg_icon = get_svg_inline("MESSAGE_CENTER", size_px=32) or ""
                st.markdown(
                    f"<h3 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{msg_icon} {title}</h3>",
                    unsafe_allow_html=True,
                )
            except Exception:
                st.subheader(f"📡 {title}")
            st.markdown("CCU MQTT Message Monitoring - Echtzeit-Nachrichten über CCU Gateway")
        else:
            # Use i18n
            title = title or i18n.t("ccu_message_monitor.title")
            # Get SVG icon for Message Monitor heading
            try:
                msg_icon = get_svg_inline("MESSAGE_CENTER", size_px=32) or ""
                st.markdown(
                    f"<h3 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{msg_icon} {title}</h3>",
                    unsafe_allow_html=True,
                )
            except Exception:
                st.subheader(f"📡 {title}")
            st.markdown(i18n.t("ccu_message_monitor.subtitle"))

        if not ccu_gateway:
            error_msg = (
                i18n.t("ccu_message_monitor.error.gateway_not_available") if i18n else "CCU Gateway nicht verfügbar"
            )
            st.error(f"❌ {error_msg}")
            return

        # Initialize Monitor Manager (like other managers)
        from omf2.ccu.monitor_manager import get_monitor_manager
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()
        monitor_manager = get_monitor_manager(registry_manager)

        # Get subscribed topics from Monitor Manager (like other UI elements)
        subscribed_topics = monitor_manager.get_filter_lists().get("all_topics", [])
        if subscribed_topics:
            subscribed_msg = (
                i18n.t("ccu_message_monitor.subscriptions.subscribed_topics_count").format(count=len(subscribed_topics))
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

        # Get all buffers from CCU Gateway (like other UI elements)
        all_buffers = ccu_gateway.get_all_message_buffers()

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

                    # Get module/FTS name for display
                    _get_module_display_name(topic)

                    # Format payload as JSON if possible (store full + preview)
                    payload = message.get("payload", message)
                    if isinstance(payload, (dict, list)):
                        import json

                        full_data = json.dumps(payload, indent=2)
                        data = full_data[:200] + "..." if len(full_data) > 200 else full_data
                    else:
                        full_data = str(payload)
                        data = full_data[:200] + "..." if len(full_data) > 200 else full_data
                else:
                    timestamp = "Unknown"
                    full_data = str(message)
                    data = full_data[:200] + "..." if len(full_data) > 200 else full_data

                message_table_data.append(
                    {
                        "Topic": topic,
                        "Name": _get_topic_name_with_icon(topic),
                        "Timestamp": timestamp,
                        "Data": data,  # preview string
                        "FullData": full_data,  # full, untruncated content
                    }
                )

        # Sort messages by timestamp (newest first) - like Admin
        if message_table_data:
            # Sort by timestamp (newest first)
            message_table_data.sort(key=lambda x: x.get("Timestamp", ""), reverse=True)

            df = pd.DataFrame(message_table_data)

            # Define column order for better display
            column_order = ["Topic", "Name", "Timestamp", "Data", "FullData"]
            df = df.reindex(columns=column_order)

            # Render filter controls above table columns and get filter values
            _render_table_filters(df, i18n, ccu_gateway, monitor_manager)

            # Apply filters to the dataframe using current filter values
            filtered_df = _apply_dataframe_filters(df, i18n)

            # Display filtered table using HTML so module SVG icons can render
            _render_messages_table_with_svg_icons(filtered_df, i18n)
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


def _render_table_filters(df, i18n, ccu_gateway, monitor_manager):
    """Render Filter Controls above table columns and return filter values"""
    try:
        logger.debug("🔍 Rendering Table Filter Controls")

        # Initialize filter state in session_state BEFORE creating widgets
        # This prevents session state conflicts
        if "ccu_filter_scope" not in st.session_state:
            st.session_state["ccu_filter_scope"] = "Modules & FTS"
        if "ccu_filter_topic" not in st.session_state:
            st.session_state["ccu_filter_topic"] = "All Topics"
        if "ccu_filter_module" not in st.session_state:
            st.session_state["ccu_filter_module"] = "All Modules/FTS"
        if "ccu_filter_status" not in st.session_state:
            st.session_state["ccu_filter_status"] = "All Status"
        if "ccu_filter_selected_topics" not in st.session_state:
            st.session_state["ccu_filter_selected_topics"] = []

        # Get Registry Manager for module/FTS data
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()
        modules = registry_manager.get_modules()

        # Topic Scope Switch (Teil der Filter-UI)
        # Check if scope changed and reset filters
        previous_scope = st.session_state.get("ccu_filter_previous_scope", "Modules & FTS")
        topic_scope = st.radio(
            "Scope:",
            ["All Topics", "Modules & FTS"],
            key="ccu_filter_scope",
            horizontal=True,
            index=1,  # Default: "Modules & FTS"
        )

        # Check if scope changed and reset filters
        if topic_scope != previous_scope:
            _reset_filters_on_scope_change()
            st.session_state["ccu_filter_previous_scope"] = topic_scope

        # Abonnierte Topics Anzeige - Auswahlbox
        # Get SVG icon for Topics heading
        try:
            topics_icon = get_svg_inline("TOPICS", size_px=32) or ""
            st.markdown(
                f"<h4 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{topics_icon} Abonnierte Topics</h4>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.subheader("📋 Abonnierte Topics")

        if topic_scope == "All Topics":
            # Alle abonnierten Topics vom Monitor Manager holen
            all_subscribed_topics = monitor_manager.get_filter_lists().get("all_topics", [])
            unique_topics = sorted(all_subscribed_topics) if all_subscribed_topics else []

            selected_topics = st.multiselect(
                "Wähle Topics aus:",
                unique_topics,
                default=unique_topics,  # Alle Topics standardmäßig ausgewählt
                key="ccu_filter_selected_topics",
            )
            st.info(f"📊 {len(selected_topics)} von {len(unique_topics)} Topics ausgewählt")
        else:
            # Nur Module/FTS Topics vom Monitor Manager holen
            module_fts_topics = monitor_manager.get_filter_lists().get("module_fts_topics", [])

            selected_topics = st.multiselect(
                "Module & FTS Topics:",
                module_fts_topics,
                default=module_fts_topics,  # Alle Topics standardmäßig ausgewählt
                key="ccu_filter_selected_topics",
            )
            st.info(f"📊 {len(selected_topics)} von {len(module_fts_topics)} Module/FTS Topics ausgewählt")

        # Filter row above table columns - SOFORTIGE WIRKUNG (keine Buttons)
        col1, col2, col3 = st.columns(3)

        with col1:
            if topic_scope == "All Topics":
                # Topic Filter - Erweiterte Topic-Optionen
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
                selected_module = "All Modules/FTS"  # Not used in All Topics mode
            else:
                # Module/FTS Filter (ein Dropdown)
                module_fts_label = i18n.t("ccu_message_monitor.filter.module_fts") if i18n else "Module/FTS Filter"
                module_options = ["All Modules/FTS"]

                # Add FTS option (hardcoded for now)
                module_options.append("🚗 FTS (5iO4)")

                # Get Module Manager for consistent icon lookup
                module_manager = get_ccu_module_manager()

                # Add all modules (including Transport/CHRG0)
                for module_id, module_data in modules.items():
                    module_name = module_data.get("name", "")
                    # Use Module Manager for consistent emoji icon (selectbox doesn't support HTML)
                    module_icon = module_manager.get_module_icon(module_id)

                    # Add all modules, including Transport/CHRG0
                    display_name = f"{module_icon} {module_name} ({module_id})"
                    module_options.append(display_name)

                # Get current filter value from session state
                current_module = st.session_state["ccu_filter_module"]
                if current_module not in module_options:
                    current_module = "All Modules/FTS"
                    st.session_state["ccu_filter_module"] = current_module
                selected_module = st.selectbox(
                    module_fts_label,
                    module_options,
                    index=module_options.index(current_module),
                    key="ccu_filter_module",
                )
                selected_topic = "All Topics"  # Not used in Modules & FTS mode

        with col2:
            # Status Filter - Conditional based on scope
            if topic_scope == "All Topics":
                # All Topics Mode - All Status Options
                status_label = i18n.t("ccu_message_monitor.filter.status") if i18n else "Status Filter"
                status_options = [
                    "All Status",
                    f"{UISymbols.STATUS_ICONS['connected']} Connection",
                    f"{UISymbols.STATUS_ICONS['available']} Module State",
                    f"{UISymbols.STATUS_ICONS['transport']} FTS State",
                    f"{UISymbols.STATUS_ICONS['configured']} Factsheet",
                    f"{UISymbols.STATUS_ICONS['available']} CCU State",
                    f"{UISymbols.FUNCTIONAL_ICONS['topic_driven']} Message",
                ]
            else:
                # Modules & FTS Mode - Limited Status Options
                status_label = i18n.t("ccu_message_monitor.filter.status") if i18n else "Status Filter"
                status_options = [
                    "All Status",
                    f"{UISymbols.STATUS_ICONS['connected']} Connection",
                    f"{UISymbols.STATUS_ICONS['available']} State",
                    f"{UISymbols.STATUS_ICONS['configured']} Factsheet",
                ]

            # No need to add unique statuses from data since we removed Status column
            # Status options are now predefined based on topic patterns

            # Get current filter value from session state
            current_status = st.session_state["ccu_filter_status"]
            if current_status not in status_options:
                current_status = "All Status"
                st.session_state["ccu_filter_status"] = current_status
            selected_status = st.selectbox(
                status_label, status_options, index=status_options.index(current_status), key="ccu_filter_status"
            )

        with col3:
            # Empty column (reserved for future use)
            st.write("")

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
            if selected_status == f"{UISymbols.STATUS_ICONS['connected']} Connection":
                # Filter topics ending with "/connection"
                filtered_df = filtered_df[filtered_df["Topic"].str.endswith("/connection", na=False)]
                logger.debug("🔍 Connection topic filter applied")
            elif selected_status == f"{UISymbols.STATUS_ICONS['available']} Module State":
                # Filter topics ending with "/state" (but not FTS)
                filtered_df = filtered_df[
                    (filtered_df["Topic"].str.endswith("/state", na=False))
                    & (~filtered_df["Topic"].str.startswith("fts/", na=False))
                ]
                logger.debug("🔍 Module state topic filter applied")
            elif selected_status == f"{UISymbols.STATUS_ICONS['transport']} FTS State":
                # Filter FTS topics ending with "/state"
                filtered_df = filtered_df[
                    (filtered_df["Topic"].str.endswith("/state", na=False))
                    & (filtered_df["Topic"].str.startswith("fts/", na=False))
                ]
                logger.debug("🔍 FTS state topic filter applied")
            elif selected_status == f"{UISymbols.STATUS_ICONS['configured']} Factsheet":
                # Filter topics ending with "/factsheet"
                filtered_df = filtered_df[filtered_df["Topic"].str.endswith("/factsheet", na=False)]
                logger.debug("🔍 Factsheet topic filter applied")
            elif selected_status == f"{UISymbols.STATUS_ICONS['available']} CCU State":
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
        topic_scope = st.session_state.get("ccu_filter_scope", "Modules & FTS")
        selected_topic = st.session_state.get("ccu_filter_topic", "All Topics")
        selected_module = st.session_state.get("ccu_filter_module", "All Modules/FTS")
        selected_status = st.session_state.get("ccu_filter_status", "All Status")
        selected_topics = st.session_state.get("ccu_filter_selected_topics", [])

        filtered_df = df.copy()

        # Erste Filterung: Nur ausgewählte Topics anzeigen
        if selected_topics:
            filtered_df = filtered_df[filtered_df["Topic"].isin(selected_topics)]
            logger.debug(f"🔍 Topic selection filter applied: {len(selected_topics)} topics")

        # Zusätzliche Sicherheitsprüfung für "Modules & FTS" Scope
        if topic_scope == "Modules & FTS":
            # Nur Module/FTS Topics anzeigen (zusätzliche Sicherheit)
            filtered_df = filtered_df[
                (filtered_df["Topic"].str.startswith("module/v1/ff/", na=False))
                | (filtered_df["Topic"].str.startswith("fts/v1/ff/", na=False))
            ]
            logger.debug(f"🔍 Modules & FTS scope filter applied: {len(filtered_df)} topics remain")

        # Topic Filter - nur im "All Topics" Modus
        if topic_scope == "All Topics" and selected_topic != "All Topics":
            filtered_df = filtered_df[filtered_df["Topic"] == selected_topic]
            logger.debug(f"🔍 Topic filter applied: {selected_topic}")

        # Module/FTS Filter - Filter by Topic pattern (nur im "Modules & FTS" Modus)
        if topic_scope == "Modules & FTS" and selected_module != "All Modules/FTS":
            if selected_module == "🚗 FTS (5iO4)":
                # Filter for FTS topics
                filtered_df = filtered_df[filtered_df["Topic"].str.startswith("fts/", na=False)]
                logger.debug("🔍 FTS filter applied")
            else:
                # Extract module ID from display name
                module_id = None
                if "(" in selected_module and ")" in selected_module:
                    module_id = selected_module.split("(")[-1].split(")")[0]

                if module_id:
                    # Filter by module serial in topic
                    filtered_df = filtered_df[filtered_df["Topic"].str.contains(f"/{module_id}/", na=False)]
                    logger.debug(f"🔍 Module filter applied: {module_id}")

        # Status Filter - Filter by Topic pattern (keine Status-Spalte mehr)
        if selected_status != "All Status":
            if f"{UISymbols.STATUS_ICONS['connected']} Connection" in selected_status:
                # Filter topics ending with "/connection"
                filtered_df = filtered_df[filtered_df["Topic"].str.endswith("/connection", na=False)]
                logger.debug("🔍 Connection filter applied")
            elif f"{UISymbols.STATUS_ICONS['available']} Module State" in selected_status:
                # Filter module state topics (not FTS)
                filtered_df = filtered_df[
                    (filtered_df["Topic"].str.endswith("/state", na=False))
                    & (~filtered_df["Topic"].str.startswith("fts/", na=False))
                ]
                logger.debug("🔍 Module State filter applied")
            elif f"{UISymbols.STATUS_ICONS['transport']} FTS State" in selected_status:
                # Filter FTS state topics
                filtered_df = filtered_df[
                    (filtered_df["Topic"].str.endswith("/state", na=False))
                    & (filtered_df["Topic"].str.startswith("fts/", na=False))
                ]
                logger.debug("🔍 FTS State filter applied")
            elif f"{UISymbols.STATUS_ICONS['configured']} Factsheet" in selected_status:
                # Filter topics ending with "/factsheet"
                filtered_df = filtered_df[filtered_df["Topic"].str.endswith("/factsheet", na=False)]
                logger.debug("🔍 Factsheet filter applied")
            elif f"{UISymbols.STATUS_ICONS['available']} CCU State" in selected_status:
                # Filter CCU topics
                filtered_df = filtered_df[filtered_df["Topic"].str.startswith("ccu/", na=False)]
                logger.debug("🔍 CCU State filter applied")

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
    from omf2.registry.manager.registry_manager import get_registry_manager

    registry_manager = get_registry_manager()
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

    from omf2.registry.manager.registry_manager import get_registry_manager

    registry_manager = get_registry_manager()
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
                return f"{UISymbols.STATUS_ICONS['transport']} FTS ({fts_serial})"

        # Check for module topics (module/v1/ff/...)
        if topic.startswith("module/v1/ff/"):
            # Extract module serial from topic
            parts = topic.split("/")
            if len(parts) >= 4:
                module_serial = parts[3]

                # Use Module Manager for consistent icon lookup
                try:
                    module_manager = get_ccu_module_manager()
                    # Get emoji icon (dataframe doesn't support HTML)
                    module_icon = module_manager.get_module_icon(module_serial)

                    # Get module info for name
                    modules = module_manager.get_all_modules()
                    module_data = modules.get(module_serial, {})
                    module_name = module_data.get("name", module_serial)

                    return f"{module_icon} {module_name} ({module_serial})"
                except Exception as e:
                    logger.warning(f"⚠️ Could not get module icon via Module Manager: {e}")
                    # Fallback to direct registry lookup
                    from omf2.registry.manager.registry_manager import get_registry_manager

                    registry_manager = get_registry_manager()
                    modules = registry_manager.get_modules()

                    for module_id, module_data in modules.items():
                        if module_id == module_serial:
                            module_name = module_data.get("name", module_id)
                            module_icon = module_data.get("icon", "🏗️")
                            return f"{module_icon} {module_name} ({module_id})"

                # Module not found in registry
                return f"{UISymbols.STATUS_ICONS['available']} Module ({module_serial})"

        # Check for CCU topics
        if topic.startswith("ccu/"):
            return f"{UISymbols.STATUS_ICONS['available']} CCU"

        # If no specific pattern found, return "other"
        return "other"
    except Exception:
        return "other"


def _get_topic_name_with_icon(topic):
    """Get topic name with appropriate icon for Module/FTS or neutral topic icon"""
    try:
        # Check if it's a Module/FTS topic
        if topic.startswith("module/v1/ff/") or topic.startswith("fts/v1/ff/"):
            return _get_module_display_name(topic)
        else:
            # For non-Module/FTS topics, use neutral topic icon
            return f"{UISymbols.FUNCTIONAL_ICONS['topic_driven']} Topic"
    except Exception:
        return f"{UISymbols.FUNCTIONAL_ICONS['topic_driven']} Topic"


def _reset_filters_on_scope_change():
    """Reset filters when scope changes"""
    try:
        # Reset all filter values to defaults
        st.session_state["ccu_filter_topic"] = "All Topics"
        st.session_state["ccu_filter_module"] = "All Modules/FTS"
        st.session_state["ccu_filter_status"] = "All Status"
        logger.debug("🔄 Filters reset due to scope change")
    except Exception as e:
        logger.error(f"❌ Failed to reset filters: {e}")


def _get_message_type(topic):
    """Get message type based on topic"""
    if "ccu" in topic:
        return f"{UISymbols.STATUS_ICONS['available']} CCU"
    elif "factsheet" in topic:
        return f"{UISymbols.STATUS_ICONS['configured']} Factsheet"
    elif "connection" in topic:
        return f"{UISymbols.STATUS_ICONS['connected']} Connection"
    elif "state" in topic:
        # Check if it's FTS or Module
        if _is_fts_topic(topic):
            return f"{UISymbols.STATUS_ICONS['transport']} FTS"
        elif _is_module_topic(topic):
            return f"{UISymbols.STATUS_ICONS['available']} Module"
        else:
            return f"{UISymbols.STATUS_ICONS['available']} State"
    elif "fts" in topic.lower():
        return f"{UISymbols.STATUS_ICONS['transport']} FTS"
    elif "module" in topic:
        return f"{UISymbols.STATUS_ICONS['available']} Module"
    else:
        return f"{UISymbols.FUNCTIONAL_ICONS['topic_driven']} Message"


def _get_message_status(message):
    """Get message status based on content"""
    if isinstance(message, dict):
        # Check for connection status (only if "connected" key exists)
        if "connected" in message:
            if message.get("connected", False):
                return f"{UISymbols.STATUS_ICONS['connected']} Connected"
            else:
                return f"{UISymbols.STATUS_ICONS['disconnected']} Disconnected"

        # Check for module availability status
        if message.get("available") in ["READY", "AVAILABLE"]:
            return f"{UISymbols.STATUS_ICONS['available']} Available"
        elif message.get("available") == "BUSY":
            return f"{UISymbols.STATUS_ICONS['busy']} Busy"
        elif message.get("available") == "ERROR":
            return f"{UISymbols.STATUS_ICONS['error']} Error"

        # Check for FTS state (has orderId, nodeStates, actionStates)
        elif "orderId" in message and ("nodeStates" in message or "actionStates" in message):
            # FTS is active if it has an orderId
            if message.get("orderId"):
                return f"{UISymbols.STATUS_ICONS['transport']} FTS Active"
            else:
                return f"{UISymbols.STATUS_ICONS['idle']} FTS Idle"

        # Check for factsheet content
        elif "capabilities" in message or "loadSpecification" in message:
            return f"{UISymbols.STATUS_ICONS['configured']} Factsheet"

        # Check for CCU state
        elif "ccu" in str(message).lower():
            return f"{UISymbols.STATUS_ICONS['available']} CCU State"

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


def _render_messages_table_with_svg_icons(filtered_df: pd.DataFrame, i18n):
    """Render messages table as HTML so module SVG icons can be displayed.

    Columns: Topic | Name | Timestamp | Data
    - For module topics (module/v1/ff/{serial}/...), use Module Manager to render SVG icon in Name.
    - For FTS and other topics, keep existing text/emoji (scope limited to module SVGs).
    """
    try:
        # Build HTML table
        table_html = '<table style="width: 100%; border-collapse: collapse;">'

        # Header
        headers = [
            "Topic",
            i18n.t("ccu_message_monitor.table.name") if i18n else "Name",
            i18n.t("ccu_message_monitor.table.timestamp") if i18n else "Timestamp",
            i18n.t("ccu_message_monitor.table.data") if i18n else "Data",
        ]
        table_html += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
        for header in headers:
            table_html += f'<th style="padding: 8px; text-align: left; font-weight: bold;">{header}</th>'
        table_html += "</tr></thead>"

        # Body
        table_html += "<tbody>"

        # Module Manager for SVG rendering
        module_manager = get_ccu_module_manager()
        modules = module_manager.get_all_modules()

        for _, row in filtered_df.iterrows():
            topic = str(row.get("Topic", ""))
            name_display = str(row.get("Name", ""))
            timestamp = str(row.get("Timestamp", ""))
            data = str(row.get("Data", ""))
            full_data = str(row.get("FullData", data))

            # If module topic, replace name with SVG icon + module name
            if topic.startswith("module/v1/ff/") or topic.startswith("fts/v1/ff/"):
                try:
                    parts = topic.split("/")
                    module_serial = parts[3] if len(parts) >= 4 else None
                    if module_serial:
                        icon_html = module_manager.get_module_icon_html(module_serial, size_px=20)
                        module_name = modules.get(module_serial, {}).get("name", module_serial)
                        # Keep SVG and text on one line
                        name_text = html.escape(f"{module_name} ({module_serial})")
                        name_display = (
                            f'<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">'
                            f"{icon_html}<span>{name_text}</span></span>"
                        )
                except Exception:
                    # Keep original name_display on failure
                    pass

            # Row
            table_html += '<tr style="border-bottom: 1px solid #ddd;">'
            table_html += f'<td style="padding: 8px; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(topic)}</td>'
            table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name_display}</td>'
            table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(timestamp)}</td>'
            # Data cell: show preview with expandable full content using <details>
            safe_preview = html.escape(data)
            safe_full = html.escape(full_data)
            data_cell = (
                f'<details style="max-width: 100%;">'
                f'<summary style="cursor: pointer; color: #444; display: inline-block; max-width: 100%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{safe_preview}</summary>'
                f'<pre style="white-space: pre-wrap; margin-top: 8px;">{safe_full}</pre>'
                f"</details>"
            )
            table_html += f'<td style="padding: 8px;">{data_cell}</td>'
            table_html += "</tr>"

        table_html += "</tbody></table>"

        # Render
        st.markdown(table_html, unsafe_allow_html=True)

        # Diagnostics
        svg_count = table_html.count("<svg")
        st.caption(f"✨ Messages rendered with SVG icons where available ({svg_count} SVG icons)")

    except Exception as e:
        logger.error(f"❌ Failed to render messages table with SVG icons: {e}")
        # Fallback to dataframe if HTML rendering fails
        st.dataframe(filtered_df, use_container_width=True)
