#!/usr/bin/env python3
"""
Admin System Logs Tab - System Log Viewer and Analysis
Uses LogManager to display logs from central buffer
"""

import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.admin.log_manager import get_log_manager, LogLevel

logger = get_logger(__name__)


def render_system_logs_tab():
    """Render Admin System Logs Tab with central log buffer viewer"""
    logger.info(f"{UISymbols.get_functional_icon('logs')} Rendering Admin System Logs Tab")
    
    try:
        st.header(f"{UISymbols.get_functional_icon('logs')} System Logs")
        st.markdown("**System log viewer powered by central log buffer**")
        
        # Get LogManager instance with central buffer
        log_buffer = st.session_state.get('log_buffer')
        if not log_buffer:
            st.warning(f"{UISymbols.get_status_icon('warning')} Log buffer not initialized. Please restart the application.")
            return
        
        # Initialize LogManager with central buffer
        log_manager = get_log_manager(log_buffer=log_buffer)
        
        # Log viewer tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            f"{UISymbols.get_functional_icon('history')} Recent Logs",
            f"{UISymbols.get_functional_icon('search')} Search Logs", 
            f"{UISymbols.get_functional_icon('dashboard')} Statistics",
            f"{UISymbols.get_functional_icon('settings')} Management"
        ])
        
        with tab1:
            _render_recent_logs(log_manager)
        
        with tab2:
            _render_search_logs(log_manager)
        
        with tab3:
            _render_log_statistics(log_manager)
        
        with tab4:
            _render_log_management(log_manager)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} System Logs Tab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} System Logs Tab failed: {e}")


def _render_recent_logs(log_manager):
    """Render recent logs viewer"""
    st.subheader(f"{UISymbols.get_functional_icon('history')} Recent Logs")
    
    # Filter controls
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        log_level = st.selectbox(
            f"{UISymbols.get_functional_icon('filter')} Log Level",
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            key="log_level_filter",
            index=0
        )
    
    with col2:
        component_filter = st.text_input(
            f"{UISymbols.get_functional_icon('search')} Component Filter",
            placeholder="e.g., omf2.admin, omf2.ui...",
            key="component_filter"
        )
    
    with col3:
        max_entries = st.number_input(
            "Max Entries",
            min_value=10,
            max_value=500,
            value=100,
            key="max_log_entries"
        )
    
    with col4:
        if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh", key="refresh_logs"):
            st.rerun()
    
    # Get filtered logs
    level_filter = None if log_level == "ALL" else LogLevel(log_level)
    component = component_filter if component_filter else None
    
    logs = log_manager.get_logs(limit=max_entries, level=level_filter, component=component)
    
    # Display logs
    st.markdown(f"**Showing {len(logs)} log entries**")
    
    if logs:
        # Display in reverse order (newest first)
        for log_entry in reversed(logs):
            # Color code by level
            level_colors = {
                "DEBUG": "🔍",
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "CRITICAL": "🚨"
            }
            icon = level_colors.get(log_entry.level.value, "📝")
            
            with st.expander(
                f"{icon} [{log_entry.timestamp.strftime('%H:%M:%S')}] {log_entry.component}: {log_entry.message[:80]}...",
                expanded=False
            ):
                st.text(f"Timestamp: {log_entry.timestamp.isoformat()}")
                st.text(f"Level: {log_entry.level.value}")
                st.text(f"Component: {log_entry.component}")
                st.text(f"Message:\n{log_entry.message}")
    else:
        st.info(f"{UISymbols.get_status_icon('info')} No logs found matching the filters")


def _render_search_logs(log_manager):
    """Render log search functionality"""
    st.subheader(f"{UISymbols.get_functional_icon('search')} Log Search")
    
    # Search form
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            f"{UISymbols.get_functional_icon('search')} Search Query",
            placeholder="Enter search term...",
            key="log_search_query"
        )
    
    with col2:
        max_results = st.number_input(
            "Max Results",
            min_value=10,
            max_value=500,
            value=50,
            key="search_max_results"
        )
    
    if st.button(f"{UISymbols.get_functional_icon('search')} Search", key="search_logs_btn"):
        if search_query:
            results = log_manager.search_logs(search_query, limit=max_results)
            
            st.markdown(f"**Found {len(results)} matching entries**")
            
            if results:
                for log_entry in results:
                    level_colors = {
                        "DEBUG": "🔍",
                        "INFO": "ℹ️",
                        "WARNING": "⚠️",
                        "ERROR": "❌",
                        "CRITICAL": "🚨"
                    }
                    icon = level_colors.get(log_entry.level.value, "📝")
                    
                    with st.expander(
                        f"{icon} [{log_entry.timestamp.strftime('%H:%M:%S')}] {log_entry.component}: {log_entry.message[:80]}...",
                        expanded=False
                    ):
                        st.text(f"Timestamp: {log_entry.timestamp.isoformat()}")
                        st.text(f"Level: {log_entry.level.value}")
                        st.text(f"Component: {log_entry.component}")
                        st.text(f"Message:\n{log_entry.message}")
            else:
                st.info(f"{UISymbols.get_status_icon('info')} No logs found matching: {search_query}")
        else:
            st.warning(f"{UISymbols.get_status_icon('warning')} Please enter a search query")


def _render_log_statistics(log_manager):
    """Render log statistics dashboard"""
    st.subheader(f"{UISymbols.get_functional_icon('dashboard')} Log Statistics")
    
    # Get statistics
    stats = log_manager.get_log_statistics()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(f"{UISymbols.get_functional_icon('logs')} Total Logs", stats.get('total_entries', 0))
    
    with col2:
        errors = stats.get('level_distribution', {}).get('ERROR', 0)
        st.metric(f"{UISymbols.get_status_icon('error')} Errors", errors)
    
    with col3:
        warnings = stats.get('level_distribution', {}).get('WARNING', 0)
        st.metric(f"{UISymbols.get_status_icon('warning')} Warnings", warnings)
    
    with col4:
        st.metric(f"{UISymbols.get_functional_icon('dashboard')} Buffer Usage", stats.get('buffer_usage', '0/0'))
    
    # Level distribution
    st.markdown("**Log Level Distribution**")
    level_dist = stats.get('level_distribution', {})
    if level_dist:
        for level, count in level_dist.items():
            st.text(f"{level}: {count}")
    else:
        st.info("No log level data available")
    
    st.divider()
    
    # Component distribution
    st.markdown("**Component Distribution (Top 10)**")
    component_dist = stats.get('component_distribution', {})
    if component_dist:
        # Sort by count and show top 10
        sorted_components = sorted(component_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        for component, count in sorted_components:
            st.text(f"{component}: {count}")
    else:
        st.info("No component data available")


def _render_log_management(log_manager):
    """Render log management interface"""
    st.subheader(f"{UISymbols.get_functional_icon('settings')} Log Management")
    
    # Clear logs
    st.markdown("**Clear Logs**")
    st.warning(f"{UISymbols.get_status_icon('warning')} This will clear all logs from the buffer!")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button(f"{UISymbols.get_functional_icon('delete')} Clear All Logs", key="clear_logs_btn", type="secondary"):
            log_manager.clear_logs()
            st.success(f"{UISymbols.get_status_icon('success')} All logs cleared")
            st.rerun()
    
    st.divider()
    
    # Export logs
    st.markdown("**Export Logs**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        export_level = st.selectbox(
            "Log Level",
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            key="export_level"
        )
    
    with col2:
        export_component = st.text_input(
            "Component (optional)",
            placeholder="Leave empty for all",
            key="export_component"
        )
    
    with col3:
        export_hours = st.number_input(
            "Hours back",
            min_value=1,
            max_value=168,
            value=24,
            key="export_hours"
        )
    
    if st.button(f"{UISymbols.get_functional_icon('export')} Export Logs", key="export_logs_btn"):
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"omf2_logs_{timestamp}.json"
            filepath = Path.cwd() / "logs" / filename
            filepath.parent.mkdir(exist_ok=True)
            
            # Prepare filters
            level_filter = None if export_level == "ALL" else LogLevel(export_level)
            component_filter = export_component if export_component else None
            since_filter = datetime.now() - timedelta(hours=export_hours)
            
            # Export
            success = log_manager.export_logs(
                filepath,
                level=level_filter,
                component=component_filter,
                since=since_filter
            )
            
            if success:
                st.success(f"{UISymbols.get_status_icon('success')} Logs exported to: {filepath}")
            else:
                st.error(f"{UISymbols.get_status_icon('error')} Failed to export logs")
        except Exception as e:
            logger.error(f"Export error: {e}")
            st.error(f"{UISymbols.get_status_icon('error')} Export error: {e}")
