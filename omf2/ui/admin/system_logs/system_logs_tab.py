#!/usr/bin/env python3
"""
NICHT SICHTBAR für agent
Admin Logs Tab - System Log Viewer and Analysis
Gateway-Pattern konform: Nutzt AdminGateway für Log-Zugriff
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_system_logs_tab():
    """Render Admin Logs Tab with system log viewer"""
    logger.info(f"{UISymbols.get_functional_icon('logs')} Rendering Admin Logs Tab")
    
    try:
        st.header(f"{UISymbols.get_functional_icon('logs')} System Logs")
        st.markdown("**System log viewer and analysis tools**")
        
        # Connection status check
        from omf2.factory.gateway_factory import get_admin_gateway
        admin_gateway = get_admin_gateway()
        
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} Admin Gateway not available")
            return
        
        # Connection status shown in sidebar only
        
        # Log viewer tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            f"{UISymbols.get_functional_icon('history')} Log History",
            f"{UISymbols.get_functional_icon('search')} Log Search", 
            f"{UISymbols.get_functional_icon('dashboard')} Log Analytics",
            f"{UISymbols.get_functional_icon('settings')} Log Management",
            f"🚨 Error & Warnings"
        ])
        
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
            key="log_level_filter"
        )
    
    with col2:
        max_entries = st.number_input(
            f"{UISymbols.get_functional_icon('dashboard')} Max Entries",
            min_value=10,
            max_value=1000,
            value=100,
            key="max_log_entries"
        )
    
    with col3:
        if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh", key="refresh_logs"):
            st.rerun()
    
    # Get log entries from new multi-level buffer system
    log_handler = st.session_state.get('log_handler')
    if not log_handler:
        st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
        return
    
    # Get all logs from all levels and combine them
    all_logs = []
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
        all_logs.extend(log_handler.get_buffer(level))
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.split(']')[0] if ']' in x else x, reverse=True)
    
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
    
    # Display logs in expandable sections
    for i, log_entry in enumerate(filtered_logs):
        # Extract level and logger name for display
        level = "INFO"
        logger_name = "unknown"
        
        # Parse log format: "timestamp [LEVEL] logger_name: message"
        if "[DEBUG]" in log_entry:
            level = "DEBUG"
            parts = log_entry.split("[DEBUG] ")
            if len(parts) > 1:
                logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                logger_name = logger_part.strip()
        elif "[INFO]" in log_entry:
            level = "INFO"
            parts = log_entry.split("[INFO] ")
            if len(parts) > 1:
                logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                logger_name = logger_part.strip()
        elif "[WARNING]" in log_entry:
            level = "WARNING"
            parts = log_entry.split("[WARNING] ")
            if len(parts) > 1:
                logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                logger_name = logger_part.strip()
        elif "[ERROR]" in log_entry:
            level = "ERROR"
            parts = log_entry.split("[ERROR] ")
            if len(parts) > 1:
                logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                logger_name = logger_part.strip()
        
        # Color coding for log levels
        if level == "ERROR":
            color = "🔴"
        elif level == "WARNING":
            color = "🟡"
        elif level == "DEBUG":
            color = "🔵"
        else:
            color = "🔵"
        
        # Create expandable section with new format: [LEVEL] logger_name
        with st.expander(f"{color} [{level}] {logger_name}", expanded=False):
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
            key="log_search_query"
        )
    
    with col2:
        search_clicked = st.button(f"{UISymbols.get_functional_icon('search')} Search", key="search_logs")
    
    # Get log entries from new multi-level buffer system
    log_handler = st.session_state.get('log_handler')
    if not log_handler:
        st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
        return
    
    # Get all logs from all levels and combine them
    all_logs = []
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
        all_logs.extend(log_handler.get_buffer(level))
    
    # Sort by timestamp (newest first)
    all_logs.sort(key=lambda x: x.split(']')[0] if ']' in x else x, reverse=True)
    
    # Perform search if query provided
    if search_query and search_clicked:
        # Case-insensitive search
        search_results = [log for log in all_logs if search_query.lower() in log.lower()]
        
        if search_results:
            st.success(f"{UISymbols.get_status_icon('success')} Found {len(search_results)} results for: '{search_query}'")
            
            # Display search results
            for i, log_entry in enumerate(search_results[:50]):  # Limit to 50 results
                # Extract level and logger name for display (same logic as Log History)
                level = "INFO"
                logger_name = "unknown"
                
                # Parse log format: "timestamp [LEVEL] logger_name: message"
                if "[DEBUG]" in log_entry:
                    level = "DEBUG"
                    parts = log_entry.split("[DEBUG] ")
                    if len(parts) > 1:
                        logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                        logger_name = logger_part.strip()
                elif "[INFO]" in log_entry:
                    level = "INFO"
                    parts = log_entry.split("[INFO] ")
                    if len(parts) > 1:
                        logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                        logger_name = logger_part.strip()
                elif "[WARNING]" in log_entry:
                    level = "WARNING"
                    parts = log_entry.split("[WARNING] ")
                    if len(parts) > 1:
                        logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                        logger_name = logger_part.strip()
                elif "[ERROR]" in log_entry:
                    level = "ERROR"
                    parts = log_entry.split("[ERROR] ")
                    if len(parts) > 1:
                        logger_part = parts[1].split(":")[0] if ":" in parts[1] else "unknown"
                        logger_name = logger_part.strip()
                
                # Color coding for log levels
                if level == "ERROR":
                    color = "🔴"
                elif level == "WARNING":
                    color = "🟡"
                elif level == "DEBUG":
                    color = "🔵"
                else:
                    color = "🔵"
                
                # Highlight search term in log entry
                highlighted_log = log_entry.replace(
                    search_query, f"**{search_query}**"
                )
                
                # Display directly without expandable section (expanded by default)
                st.markdown(f"**{color} [{level}] {logger_name}**")
                st.code(highlighted_log, language="text")
                st.markdown("---")  # Separator between entries
        else:
            st.warning(f"{UISymbols.get_status_icon('warning')} No results found for: '{search_query}'")
    
    elif search_clicked and not search_query:
        st.warning(f"{UISymbols.get_status_icon('warning')} Please enter a search query")
    
    # Show recent logs if no search performed
    if not search_query:
        st.info(f"{UISymbols.get_status_icon('info')} Enter a search term to search through {len(all_logs)} log entries")


def _render_log_analytics(admin_gateway):
    """Render log analytics dashboard"""
    st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Log Analytics")
    st.markdown("**System log statistics and trends**")
    
    # Get log entries from new multi-level buffer system
    log_handler = st.session_state.get('log_handler')
    if not log_handler:
        st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
        return
    
    # Get all logs from all levels and combine them
    all_logs = []
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
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
        timestamp = log_entry.split(']')[0].split('[')[0].strip() if ']' in log_entry else "Unknown"
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
        set_debug_mode,
        enable_sensor_debug,
        disable_debug_logging,
        enable_module_debug,
        enable_mqtt_debug
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
        st.text(f"• (admin_managers: TBD)")
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
            set_debug_mode("omf2.admin.admin_mqtt_client", True)
            st.success("✅ Admin MQTT debug enabled")
            st.rerun()
        if st.button("🔍 Admin Gateway", key="enable_admin_gateway_debug"):
            set_debug_mode("omf2.admin.admin_gateway", True)
            st.success("✅ Admin Gateway debug enabled")
            st.rerun()
        if st.button("ℹ️ Disable Admin", key="disable_admin_debug"):
            set_debug_mode("omf2.admin.admin_mqtt_client", False)
            set_debug_mode("omf2.admin.admin_gateway", False)
            st.info("ℹ️ Admin debug disabled")
            st.rerun()
    
    with col2:
        st.markdown("**🏭 CCU Domain**")
        if st.button("🔍 CCU MQTT", key="enable_ccu_mqtt_debug"):
            set_debug_mode("omf2.ccu.ccu_mqtt_client", True)
            st.success("✅ CCU MQTT debug enabled")
            st.rerun()
        if st.button("🔍 CCU Gateway", key="enable_ccu_gateway_debug"):
            set_debug_mode("omf2.ccu.ccu_gateway", True)
            st.success("✅ CCU Gateway debug enabled")
            st.rerun()
        if st.button("🔍 Managers", key="enable_ccu_managers_debug"):
            enable_sensor_debug()
            enable_module_debug()
            st.success("✅ CCU Managers debug enabled")
            st.rerun()
        if st.button("ℹ️ Disable CCU", key="disable_ccu_debug"):
            set_debug_mode("omf2.ccu.ccu_mqtt_client", False)
            set_debug_mode("omf2.ccu.ccu_gateway", False)
            set_debug_mode("omf2.ccu.sensor_manager", False)
            set_debug_mode("omf2.ccu.module_manager", False)
            st.info("ℹ️ CCU debug disabled")
            st.rerun()
    
    
    # Global controls
    st.subheader(f"{UISymbols.get_functional_icon('settings')} Global Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"{UISymbols.get_functional_icon('search')} Enable All Debug", key="enable_all_debug"):
            set_debug_mode(enabled=True)
            st.success(f"{UISymbols.get_status_icon('success')} All debug logging enabled")
            st.rerun()
    
    with col2:
        if st.button(f"{UISymbols.get_status_icon('info')} Disable All Debug", key="disable_all_debug"):
            disable_debug_logging()
            st.info(f"{UISymbols.get_status_icon('info')} All debug logging disabled")
            st.rerun()
    
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
        "omf2.nodered": "NodeRED Integration"
    }
    
    selected_module = st.selectbox(
        f"{UISymbols.get_functional_icon('search')} Select Module",
        options=list(module_options.keys()),
        format_func=lambda x: module_options[x],
        key="log_level_module"
    )
    
    # Log level selection
    level_options = ["DEBUG", "INFO", "WARNING", "ERROR"]
    current_level = current_levels.get(selected_module, "INFO")
    
    selected_level = st.selectbox(
        f"{UISymbols.get_functional_icon('settings')} Log Level",
        options=level_options,
        index=level_options.index(current_level) if current_level in level_options else 1,
        key="log_level_selection"
    )
    
    # Apply button
    if st.button(f"{UISymbols.get_functional_icon('settings')} Apply Log Level", key="apply_log_level"):
        set_debug_mode(selected_module, selected_level == "DEBUG")
        st.success(f"{UISymbols.get_status_icon('success')} Log level for {module_options[selected_module]} set to {selected_level}")
        st.rerun()
    
    # Configuration file info
    st.subheader(f"{UISymbols.get_functional_icon('info')} Configuration File")
    st.markdown("**Persistent configuration via YAML file**")
    
    st.info(f"""
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
    ```
    
    **Note:** Changes to the YAML file require a dashboard restart to take effect.
    """)
    
    # Restart information
    st.subheader(f"{UISymbols.get_functional_icon('warning')} Application Restart")
    st.markdown("**When restart is required**")
    
    st.warning(f"""
    **Restart Required For:**
    - Changes to `omf2/config/logging_config.yml`
    - Changes to global logging configuration
    - Changes to buffer size or file logging settings
    
    **No Restart Required For:**
    - Quick debug controls (above)
    - Manual log level changes (above)
    - Runtime log level adjustments
    """)
    
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
