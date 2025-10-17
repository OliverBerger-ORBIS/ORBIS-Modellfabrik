#!/usr/bin/env python3
"""
NICHT SICHTBAR für agent
Admin Logs Tab - System Log Viewer and Analysis
Gateway-Pattern konform: Nutzt AdminGateway für Log-Zugriff
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_system_logs_tab():
    """Render Admin Logs Tab with system log viewer"""
    logger.info(f"{UISymbols.get_functional_icon('logs')} Rendering Admin Logs Tab")

    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        st.header(f"{UISymbols.get_functional_icon('logs')} {i18n.translate('tabs.system_logs')}")
        st.markdown("**System log viewer and analysis tools**")

        # Display mode toggle
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Display Options:**")
        with col2:
            # Initialize display mode in session state if not exists
            if "log_display_mode" not in st.session_state:
                st.session_state["log_display_mode"] = "Console View"

            display_mode = st.selectbox(
                "📋 Log Display Mode",
                ["Table View", "Console View"],
                index=1 if st.session_state["log_display_mode"] == "Console View" else 0,
                key="log_display_mode",
                help="Table View: Structured tabular display | Console View: Classic one-line format",
            )

            # Update session state only if changed (avoid widget warning)
            if display_mode != st.session_state["log_display_mode"]:
                st.session_state["log_display_mode"] = display_mode
                request_refresh()

        # Connection status check
        from omf2.factory.gateway_factory import get_admin_gateway

        admin_gateway = get_admin_gateway()

        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
            return

        # Connection status shown in sidebar only

        # Log viewer tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                f"{UISymbols.get_functional_icon('history')} Log History",
                f"{UISymbols.get_functional_icon('search')} Log Search",
                f"{UISymbols.get_functional_icon('dashboard')} Log Analytics",
                f"{UISymbols.get_functional_icon('settings')} Log Management",
                "🚨 Error & Warnings",
            ]
        )

        with tab1:
            _render_log_history(admin_gateway)

        with tab2:
            _render_log_search(admin_gateway)

        with tab3:
            _render_log_analytics(admin_gateway)

        with tab4:
            _render_log_management(admin_gateway)

        with tab5:
            from omf2.ui.admin.system_logs.error_warning_tab import render_error_warning_tab

            render_error_warning_tab()

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Admin Logs Tab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Admin Logs Tab failed: {e}")


def _render_log_history(admin_gateway):
    """Render log history viewer"""
    st.subheader(f"{UISymbols.get_functional_icon('history')} Log History")
    st.markdown("**Recent system logs and messages**")

    # Log level filter
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        log_level = st.selectbox(
            f"{UISymbols.get_functional_icon('search')} Log Level",
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
            key="log_level_filter",
        )

    with col2:
        max_entries = st.number_input(
            f"{UISymbols.get_functional_icon('dashboard')} Max Entries",
            min_value=10,
            max_value=1000,
            value=100,
            key="max_log_entries",
        )

    with col3:
        if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh", key="refresh_logs"):
            request_refresh()

    # Get log entries from new multi-level buffer system
    log_handler = st.session_state.get("log_handler")
    if not log_handler:
        st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
        return

    # Get all logs from all levels and combine them
    all_logs = []
    for level in ["ERROR", "WARNING", "INFO", "DEBUG"]:
        all_logs.extend(log_handler.get_buffer(level))

    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.split("]")[0] if "]" in x else x, reverse=True)

    # Filter by log level
    if log_level != "ALL":
        filtered_logs = [log for log in all_logs if f"[{log_level}]" in log]
    else:
        filtered_logs = all_logs

    # Limit entries
    filtered_logs = filtered_logs[:max_entries]

    # Display log entries
    if not filtered_logs:
        st.info(f"{UISymbols.get_status_icon('info')} No logs found for level: {log_level}")
        return

    st.success(f"{UISymbols.get_status_icon('success')} Showing {len(filtered_logs)} log entries")

    # Display logs based on selected mode
    display_mode = st.session_state.get("log_display_mode", "Console View")
    if display_mode == "Table View":
        _render_log_table(filtered_logs)
    else:
        _render_log_console(filtered_logs)


def _render_log_table(log_entries):
    """Render log entries in tabular format for better readability"""
    if not log_entries:
        return

    # Parse log entries into structured data
    parsed_logs = []
    for log_entry in log_entries:
        parsed_log = _parse_log_entry(log_entry)
        parsed_logs.append(parsed_log)

    # Create table header
    st.markdown("### 📋 Log Entries (Sequential View)")

    # Display logs in a structured table format
    for i, log in enumerate(parsed_logs):
        # Create a container for each log entry
        with st.container():
            # Color-coded level indicator
            level_color = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵", "DEBUG": "🔵"}.get(log["level"], "⚪")

            # Compact log entry display - all in one line
            col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 2, 1])

            with col1:
                st.markdown(f"**{level_color} {log['level']}**")

            with col2:
                st.text(log["timestamp"])

            with col3:
                st.text(log["logger_name"])

            with col4:
                # Message content inline
                st.text(log["message"][:50] + "..." if len(log["message"]) > 50 else log["message"])

            with col5:
                # Copy button inline
                if st.button("📋", key=f"copy_log_{i}", help="Copy log entry"):
                    # Display the log entry in a code block for copying
                    st.code(log["full_message"], language="text")
                    # Don't trigger refresh - just show the content

            # Full log entry in collapsible section
            with st.expander(f"🔍 Full Log Entry #{i+1}", expanded=False):
                st.code(log["full_message"], language="text")

            # Separator between entries
            st.markdown("---")


def _render_log_console(log_entries):
    """Render log entries in classic console format (one line per entry)"""
    if not log_entries:
        return

    st.markdown("### 📋 Log Entries (Console View)")
    st.caption("Classic one-line format - one log entry per line")

    # Display logs in classic console format with inline copy button
    for i, log_entry in enumerate(log_entries):
        # Parse log entry to extract level for color coding
        parsed_log = _parse_log_entry(log_entry)

        # Color coding for log levels
        level_color = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵", "DEBUG": "🔵"}.get(parsed_log["level"], "⚪")

        # Compact display with inline copy button
        col1, col2 = st.columns([10, 1])

        with col1:
            # Display as single line with color indicator
            st.text(f"{level_color} {log_entry}")

        with col2:
            # Copy button inline
            if st.button("📋", key=f"copy_console_{i}", help="Copy log entry"):
                st.code(log_entry, language="text")


def _parse_log_entry(log_entry):
    """Parse a log entry into structured components"""
    # Default values
    timestamp = "Unknown"
    level = "INFO"
    logger_name = "unknown"
    message = log_entry

    try:
        # Parse log format: "timestamp [LEVEL] logger_name: message"
        if "[DEBUG]" in log_entry:
            level = "DEBUG"
            parts = log_entry.split("[DEBUG] ")
            if len(parts) > 1:
                timestamp = parts[0].strip()
                remaining = parts[1]
                if ":" in remaining:
                    logger_name = remaining.split(":")[0].strip()
                    message = ":".join(remaining.split(":")[1:]).strip()
                else:
                    logger_name = remaining.strip()
                    message = ""
        elif "[INFO]" in log_entry:
            level = "INFO"
            parts = log_entry.split("[INFO] ")
            if len(parts) > 1:
                timestamp = parts[0].strip()
                remaining = parts[1]
                if ":" in remaining:
                    logger_name = remaining.split(":")[0].strip()
                    message = ":".join(remaining.split(":")[1:]).strip()
                else:
                    logger_name = remaining.strip()
                    message = ""
        elif "[WARNING]" in log_entry:
            level = "WARNING"
            parts = log_entry.split("[WARNING] ")
            if len(parts) > 1:
                timestamp = parts[0].strip()
                remaining = parts[1]
                if ":" in remaining:
                    logger_name = remaining.split(":")[0].strip()
                    message = ":".join(remaining.split(":")[1:]).strip()
                else:
                    logger_name = remaining.strip()
                    message = ""
        elif "[ERROR]" in log_entry:
            level = "ERROR"
            parts = log_entry.split("[ERROR] ")
            if len(parts) > 1:
                timestamp = parts[0].strip()
                remaining = parts[1]
                if ":" in remaining:
                    logger_name = remaining.split(":")[0].strip()
                    message = ":".join(remaining.split(":")[1:]).strip()
                else:
                    logger_name = remaining.strip()
                    message = ""
    except Exception as e:
        # Fallback for malformed log entries
        logger.warning(f"Failed to parse log entry: {e}")

    return {
        "timestamp": timestamp,
        "level": level,
        "logger_name": logger_name,
        "message": message,
        "full_message": log_entry,
    }


def _render_search_results_table(search_results, search_query):
    """Render search results in tabular format with highlighted search terms"""
    if not search_results:
        return

    st.markdown("### 🔍 Search Results (Sequential View)")

    # Display search results in tabular format
    for i, log_entry in enumerate(search_results):
        # Parse log entry
        parsed_log = _parse_log_entry(log_entry)

        # Highlight search term in message
        highlighted_message = parsed_log["message"].replace(search_query, f"**{search_query}**")

        # Create a container for each log entry
        with st.container():
            # Color-coded level indicator
            level_color = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵", "DEBUG": "🔵"}.get(parsed_log["level"], "⚪")

            # Compact search result display - all in one line
            col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 2, 1])

            with col1:
                st.markdown(f"**{level_color} {parsed_log['level']}**")

            with col2:
                st.text(parsed_log["timestamp"])

            with col3:
                st.text(parsed_log["logger_name"])

            with col4:
                # Message content with highlighted search term (truncated)
                truncated_message = (
                    highlighted_message[:50] + "..." if len(highlighted_message) > 50 else highlighted_message
                )
                st.markdown(truncated_message)

            with col5:
                # Copy button inline
                if st.button("📋", key=f"copy_search_{i}", help="Copy log entry"):
                    st.code(parsed_log["full_message"], language="text")

            # Full log entry in collapsible section
            with st.expander(f"🔍 Full Log Entry #{i+1}", expanded=(i < 3)):
                # Highlight search term in full message
                highlighted_full = parsed_log["full_message"].replace(search_query, f"**{search_query}**")
                st.code(highlighted_full, language="text")

            # Separator between entries
            st.markdown("---")


def _render_search_results_console(search_results, search_query):
    """Render search results in classic console format with highlighted search terms"""
    if not search_results:
        return

    st.markdown("### 🔍 Search Results (Console View)")
    st.caption("Classic one-line format with highlighted search terms")

    # Display search results in console format with inline copy button
    for i, log_entry in enumerate(search_results):
        # Parse log entry
        parsed_log = _parse_log_entry(log_entry)

        # Color coding for log levels
        level_color = {"ERROR": "🔴", "WARNING": "🟡", "INFO": "🔵", "DEBUG": "🔵"}.get(parsed_log["level"], "⚪")

        # Highlight search term in log entry
        highlighted_log = log_entry.replace(search_query, f"**{search_query}**")

        # Compact display with inline copy button
        col1, col2 = st.columns([10, 1])

        with col1:
            # Display as single line with color indicator and highlighting
            st.markdown(f"{level_color} {highlighted_log}")

        with col2:
            # Copy button inline
            if st.button("📋", key=f"copy_search_console_{i}", help="Copy log entry"):
                st.code(log_entry, language="text")


def _render_log_search(admin_gateway):
    """Render log search functionality"""
    st.subheader(f"{UISymbols.get_functional_icon('search')} Log Search")
    st.markdown("**Search through system logs**")

    # Search form
    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input(
            f"{UISymbols.get_functional_icon('search')} Search Query",
            placeholder="Enter search term...",
            key="log_search_query",
        )

    with col2:
        search_clicked = st.button(f"{UISymbols.get_functional_icon('search')} Search", key="search_logs")

    # Get log entries from new multi-level buffer system
    log_handler = st.session_state.get("log_handler")
    if not log_handler:
        st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
        return

    # Get all logs from all levels and combine them
    all_logs = []
    for level in ["ERROR", "WARNING", "INFO", "DEBUG"]:
        all_logs.extend(log_handler.get_buffer(level))

    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.split("]")[0] if "]" in x else x, reverse=True)

    # Perform search if query provided
    if search_query and search_clicked:
        # Case-insensitive search
        search_results = [log for log in all_logs if search_query.lower() in log.lower()]

        if search_results:
            st.success(
                f"{UISymbols.get_status_icon('success')} Found {len(search_results)} results for: '{search_query}'"
            )

            # Display search results based on selected mode
            display_mode = st.session_state.get("log_display_mode", "Console View")
            if display_mode == "Table View":
                _render_search_results_table(search_results[:50], search_query)  # Limit to 50 results
            else:
                _render_search_results_console(search_results[:50], search_query)  # Limit to 50 results
        else:
            st.warning(f"{UISymbols.get_status_icon('warning')} No results found for: '{search_query}'")

    elif search_clicked and not search_query:
        st.warning(f"{UISymbols.get_status_icon('warning')} Please enter a search query")

    # Show recent logs if no search performed
    if not search_query:
        st.info(
            f"{UISymbols.get_status_icon('info')} Enter a search term to search through {len(all_logs)} log entries"
        )


def _render_log_analytics(admin_gateway):
    """Render log analytics dashboard"""
    st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Log Analytics")
    st.markdown("**System log statistics and trends**")

    # Get log entries from new multi-level buffer system
    log_handler = st.session_state.get("log_handler")
    if not log_handler:
        st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
        return

    # Get all logs from all levels and combine them
    all_logs = []
    for level in ["ERROR", "WARNING", "INFO", "DEBUG"]:
        all_logs.extend(log_handler.get_buffer(level))

    # Count log levels
    total_logs = len(all_logs)
    debug_count = sum(1 for log in all_logs if "[DEBUG]" in log)
    info_count = sum(1 for log in all_logs if "[INFO]" in log)
    warning_count = sum(1 for log in all_logs if "[WARNING]" in log)
    error_count = sum(1 for log in all_logs if "[ERROR]" in log)

    # Analytics metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(f"{UISymbols.get_status_icon('success')} Total Logs", f"{total_logs:,}")

    with col2:
        st.metric(f"{UISymbols.get_status_icon('error')} Errors", f"{error_count:,}")

    with col3:
        st.metric(f"{UISymbols.get_status_icon('warning')} Warnings", f"{warning_count:,}")

    with col4:
        st.metric(f"{UISymbols.get_status_icon('info')} Info", f"{info_count:,}")

    # Additional metrics
    col5, col6 = st.columns(2)

    with col5:
        st.metric(f"{UISymbols.get_functional_icon('search')} Debug", f"{debug_count:,}")

    with col6:
        # Calculate error rate
        error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
        st.metric(f"{UISymbols.get_status_icon('error')} Error Rate", f"{error_rate:.1f}%")

    # Log level distribution chart
    if total_logs > 0:
        st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Log Level Distribution")

        # Create simple bar chart using columns
        chart_col1, chart_col2, chart_col3, chart_col4, chart_col5 = st.columns(5)

        with chart_col1:
            st.metric("DEBUG", debug_count, delta=None)
            debug_percent = (debug_count / total_logs * 100) if total_logs > 0 else 0
            st.progress(debug_percent / 100)

        with chart_col2:
            st.metric("INFO", info_count, delta=None)
            info_percent = (info_count / total_logs * 100) if total_logs > 0 else 0
            st.progress(info_percent / 100)

        with chart_col3:
            st.metric("WARNING", warning_count, delta=None)
            warning_percent = (warning_count / total_logs * 100) if total_logs > 0 else 0
            st.progress(warning_percent / 100)

        with chart_col4:
            st.metric("ERROR", error_count, delta=None)
            error_percent = (error_count / total_logs * 100) if total_logs > 0 else 0
            st.progress(error_percent / 100)

        with chart_col5:
            st.metric("TOTAL", total_logs, delta=None)
            st.progress(1.0)

    # Recent activity
    st.subheader(f"{UISymbols.get_functional_icon('history')} Recent Activity")

    # Show last 10 log entries with timestamps
    recent_logs = all_logs[-10:] if len(all_logs) >= 10 else all_logs
    recent_logs.reverse()  # Show newest first

    for log_entry in recent_logs:
        # Extract timestamp and level
        timestamp = log_entry.split("]")[0].split("[")[0].strip() if "]" in log_entry else "Unknown"
        level = "INFO"
        if "[DEBUG]" in log_entry:
            level = "DEBUG"
        elif "[INFO]" in log_entry:
            level = "INFO"
        elif "[WARNING]" in log_entry:
            level = "WARNING"
        elif "[ERROR]" in log_entry:
            level = "ERROR"

        # Color coding
        if level == "ERROR":
            color = "🔴"
        elif level == "WARNING":
            color = "🟡"
        elif level == "DEBUG":
            color = "🔵"
        else:
            color = "🔵"

        # Show recent activity
        st.text(f"{color} {timestamp} - {level}")

    if not recent_logs:
        st.info(f"{UISymbols.get_status_icon('info')} No recent activity")


def _render_log_management(admin_gateway):
    """Render log management and configuration"""
    st.subheader(f"{UISymbols.get_functional_icon('settings')} Log Management")
    st.markdown("**Configure logging levels and settings**")

    # Import logging configuration functions
    from omf2.common.logging_config import (
        get_current_log_levels,
        update_logging_config,
    )

    # Current log levels display
    st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Current Log Levels")
    current_levels = get_current_log_levels()

    # Architecture-based log levels display
    st.markdown("**Current Log Levels**")

    # Domain-based architecture: MQTT → Gateway → Manager → UI
    col1, col2 = st.columns(2)

    with col1:
        st.text("🔌 **ADMIN Domain:**")
        st.text(f"• admin_mqtt_client: {current_levels.get('omf2.admin.admin_mqtt_client', 'Unknown')}")
        st.text(f"• admin_gateway: {current_levels.get('omf2.admin.admin_gateway', 'Unknown')}")
        st.text("• (admin_managers: TBD)")
        st.text(f"• omf2.ui: {current_levels.get('omf2.ui', 'Unknown')}")

    with col2:
        st.text("🏭 **CCU Domain:**")
        st.text(f"• ccu_mqtt_client: {current_levels.get('omf2.ccu.ccu_mqtt_client', 'Unknown')}")
        st.text(f"• ccu_gateway: {current_levels.get('omf2.ccu.ccu_gateway', 'Unknown')}")
        st.text(f"• sensor_manager: {current_levels.get('omf2.ccu.sensor_manager', 'Unknown')}")
        st.text(f"• module_manager: {current_levels.get('omf2.ccu.module_manager', 'Unknown')}")

    # Common components
    st.text("🔧 **Common Components:**")
    st.text(f"• omf2.common: {current_levels.get('omf2.common', 'Unknown')}")
    st.text(f"• omf2.nodered: {current_levels.get('omf2.nodered', 'Unknown')}")

    # Quick debug controls
    st.subheader(f"{UISymbols.get_functional_icon('settings')} Quick Debug Controls")
    st.markdown("**Enable/disable debug logging for specific components**")

    # Domain-based debug controls
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔌 ADMIN Domain**")
        if st.button("🔍 Admin MQTT", key="enable_admin_mqtt_debug"):
            success = update_logging_config("omf2.admin.admin_mqtt_client", "DEBUG")
            if success:
                st.success("✅ Admin MQTT debug enabled")
            else:
                st.error("❌ Failed to enable Admin MQTT debug")
            request_refresh()
        if st.button("🔍 Admin Gateway", key="enable_admin_gateway_debug"):
            success = update_logging_config("omf2.admin.admin_gateway", "DEBUG")
            if success:
                st.success("✅ Admin Gateway debug enabled")
            else:
                st.error("❌ Failed to enable Admin Gateway debug")
            request_refresh()
        if st.button("ℹ️ Disable Admin", key="disable_admin_debug"):
            success1 = update_logging_config("omf2.admin.admin_mqtt_client", "INFO")
            success2 = update_logging_config("omf2.admin.admin_gateway", "INFO")
            if success1 and success2:
                st.info("ℹ️ Admin debug disabled")
            else:
                st.error("❌ Failed to disable Admin debug")
            request_refresh()

    with col2:
        st.markdown("**🏭 CCU Domain**")
        if st.button("🔍 CCU MQTT", key="enable_ccu_mqtt_debug"):
            success = update_logging_config("omf2.ccu.ccu_mqtt_client", "DEBUG")
            if success:
                st.success("✅ CCU MQTT debug enabled")
            else:
                st.error("❌ Failed to enable CCU MQTT debug")
            request_refresh()
        if st.button("🔍 CCU Gateway", key="enable_ccu_gateway_debug"):
            success = update_logging_config("omf2.ccu.ccu_gateway", "DEBUG")
            if success:
                st.success("✅ CCU Gateway debug enabled")
            else:
                st.error("❌ Failed to enable CCU Gateway debug")
            request_refresh()
        if st.button("🔍 Managers", key="enable_ccu_managers_debug"):
            success1 = update_logging_config("omf2.ccu.sensor_manager", "DEBUG")
            success2 = update_logging_config("omf2.ccu.module_manager", "DEBUG")
            if success1 and success2:
                st.success("✅ CCU Managers debug enabled")
            else:
                st.error("❌ Failed to enable CCU Managers debug")
            request_refresh()
        if st.button("ℹ️ Disable CCU", key="disable_ccu_debug"):
            success1 = update_logging_config("omf2.ccu.ccu_mqtt_client", "INFO")
            success2 = update_logging_config("omf2.ccu.ccu_gateway", "INFO")
            success3 = update_logging_config("omf2.ccu.sensor_manager", "INFO")
            success4 = update_logging_config("omf2.ccu.module_manager", "INFO")
            if success1 and success2 and success3 and success4:
                st.info("ℹ️ CCU debug disabled")
            else:
                st.error("❌ Failed to disable CCU debug")
            request_refresh()

    # Global controls
    st.subheader(f"{UISymbols.get_functional_icon('settings')} Global Controls")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"{UISymbols.get_functional_icon('search')} Enable All Debug", key="enable_all_debug"):
            # Enable debug for all major components
            success1 = update_logging_config("omf2", "DEBUG")
            success2 = update_logging_config("omf2.ccu", "DEBUG")
            success3 = update_logging_config("omf2.admin", "DEBUG")
            success4 = update_logging_config("omf2.common", "DEBUG")
            success5 = update_logging_config("omf2.ui", "DEBUG")
            if success1 and success2 and success3 and success4 and success5:
                st.success(f"{UISymbols.get_status_icon('success')} All debug logging enabled")
            else:
                st.error("❌ Failed to enable all debug logging")
            request_refresh()

    with col2:
        if st.button(f"{UISymbols.get_status_icon('info')} Disable All Debug", key="disable_all_debug"):
            # Disable debug for all major components
            success1 = update_logging_config("omf2", "INFO")
            success2 = update_logging_config("omf2.ccu", "INFO")
            success3 = update_logging_config("omf2.admin", "INFO")
            success4 = update_logging_config("omf2.common", "INFO")
            success5 = update_logging_config("omf2.ui", "INFO")
            if success1 and success2 and success3 and success4 and success5:
                st.info(f"{UISymbols.get_status_icon('info')} All debug logging disabled")
            else:
                st.error("❌ Failed to disable all debug logging")
            request_refresh()

    # Manual log level configuration
    st.subheader(f"{UISymbols.get_functional_icon('settings')} Manual Log Level Configuration")
    st.markdown("**Set specific log levels for modules**")

    # Module selection
    module_options = {
        "omf2": "OMF2 Core",
        "omf2.ccu": "CCU Domain",
        "omf2.admin": "Admin Domain",
        "omf2.common": "Common Components",
        "omf2.ui": "UI Components",
        "omf2.nodered": "NodeRED Integration",
    }

    selected_module = st.selectbox(
        f"{UISymbols.get_functional_icon('search')} Select Module",
        options=list(module_options.keys()),
        format_func=lambda x: module_options[x],
        key="log_level_module",
    )

    # Log level selection
    level_options = ["DEBUG", "INFO", "WARNING", "ERROR"]
    current_level = current_levels.get(selected_module, "INFO")

    selected_level = st.selectbox(
        f"{UISymbols.get_functional_icon('settings')} Log Level",
        options=level_options,
        index=level_options.index(current_level) if current_level in level_options else 1,
        key="log_level_selection",
    )

    # Apply button
    if st.button(f"{UISymbols.get_functional_icon('settings')} Apply Log Level", key="apply_log_level"):
        success = update_logging_config(selected_module, selected_level)
        if success:
            st.success(
                f"{UISymbols.get_status_icon('success')} Log level for {module_options[selected_module]} set to {selected_level}"
            )
        else:
            st.error(f"❌ Failed to set log level for {module_options[selected_module]} to {selected_level}")
        request_refresh()

    # Configuration file info
    st.subheader(f"{UISymbols.get_functional_icon('info')} Configuration File")
    st.markdown("**Persistent configuration via YAML file**")

    st.info(
        f"""
    **Configuration File:** `omf2/config/logging_config.yml`

    **Manual Configuration:**
    ```yaml
    modules:
      {selected_module}:
        level: {selected_level}

    business_managers:
      sensor_manager:
        level: DEBUG  # Enable sensor debugging
      module_manager:
        level: DEBUG  # Enable module debugging
      stock_manager:
        level: DEBUG  # Enable order management debugging
    ```

    **Note:** Changes to the YAML file require a dashboard restart to take effect.
    """
    )

    # Restart information
    st.subheader(f"{UISymbols.get_functional_icon('warning')} Application Restart")
    st.markdown("**When restart is required**")

    st.warning(
        """
    **Restart Required For:**
    - Changes to `omf2/config/logging_config.yml`
    - Changes to global logging configuration
    - Changes to buffer size or file logging settings

    **No Restart Required For:**
    - Quick debug controls (above)
    - Manual log level changes (above)
    - Runtime log level adjustments
    """
    )

    # Test logging
    st.subheader(f"{UISymbols.get_functional_icon('search')} Test Logging")
    st.markdown("**Generate test log entries to verify configuration**")

    if st.button(f"{UISymbols.get_functional_icon('search')} Generate Test Logs", key="generate_test_logs"):
        test_logger = logger.getChild("test")
        test_logger.debug("Test DEBUG message")
        test_logger.info("Test INFO message")
        test_logger.warning("Test WARNING message")
        test_logger.error("Test ERROR message")
        st.success(f"{UISymbols.get_status_icon('success')} Test log entries generated")
        st.info(f"{UISymbols.get_status_icon('info')} Check the Log History tab to see the test entries")
