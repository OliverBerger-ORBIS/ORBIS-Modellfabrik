#!/usr/bin/env python3
"""
Error & Warning Logs Tab - Dedicated display for ERROR and WARNING level logs
Shows only critical logs that need immediate attention
"""

import streamlit as st
from typing import Dict, Deque
from collections import deque

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_error_warning_tab():
    """Render dedicated Error & Warning Logs tab"""
    logger.info(f"{UISymbols.get_functional_icon('error')} Rendering Error & Warning Logs Tab")
    
    try:
        # Best Practice: Zugriff über Handler statt direkte Buffers
        log_handler = st.session_state.get('log_handler')
        if not log_handler:
            st.error(f"{UISymbols.get_status_icon('error')} No log handler available")
            return
        
        # Thread-sicherer Zugriff auf Level-spezifische Buffer
        error_logs = log_handler.get_buffer('ERROR')
        warning_logs = log_handler.get_buffer('WARNING')
        
        error_count = len(error_logs)
        warning_count = len(warning_logs)
        
        st.subheader(f"🚨 Critical Logs")
        st.caption(f"🔴 {error_count} Errors | 🟡 {warning_count} Warnings")
        
        # Create tabs for ERROR and WARNING
        error_tab, warning_tab = st.tabs(["🔴 Errors", "🟡 Warnings"])
        
        with error_tab:
            _render_log_level(error_logs, "ERROR", "🔴")
        
        with warning_tab:
            _render_log_level(warning_logs, "WARNING", "🟡")
            
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Error & Warning Logs Tab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Error displaying logs: {e}")


def _render_log_level(logs: list, level: str, icon: str):
    """Render logs for a specific level based on display mode"""
    
    if not logs:
        st.info(f"{icon} No {level} logs available")
        return
    
    # Show latest logs first (most recent at top)
    logs = list(logs)
    logs.reverse()  # Show newest first
    
    # Get display mode from session state
    display_mode = st.session_state.get('log_display_mode', 'Console View')
    
    if display_mode == 'Table View':
        _render_log_level_table(logs, level, icon)
    else:
        _render_log_level_console(logs, level, icon)


def _render_log_level_table(logs: list, level: str, icon: str):
    """Render logs for a specific level in tabular format"""
    st.markdown(f"### {icon} {level} Logs (Table View)")
    
    # Display logs in tabular format
    for i, log_entry in enumerate(logs):
        # Parse log entry to extract components
        parsed_log = _parse_log_entry_structured(log_entry)
        
        # Create a container for each log entry
        with st.container():
            # Compact log entry display - all in one line
            col1, col2, col3, col4, col5 = st.columns([1, 2, 3, 2, 1])
            
            with col1:
                st.markdown(f"**{icon} {parsed_log['level']}**")
            
            with col2:
                st.text(parsed_log["timestamp"])
            
            with col3:
                st.text(parsed_log["logger_name"])
            
            with col4:
                # Message content inline (truncated)
                truncated_message = parsed_log["message"][:50] + "..." if len(parsed_log["message"]) > 50 else parsed_log["message"]
                st.text(truncated_message)
            
            with col5:
                # Copy button inline
                if st.button("📋", key=f"copy_{level}_{i}", help="Copy log entry"):
                    st.code(parsed_log["full_message"], language="text")
            
            # Full log entry in collapsible section
            with st.expander(f"🔍 Full Log Entry #{i+1}", expanded=(i < 3)):
                st.code(parsed_log["full_message"], language="text")
            
            # Separator between entries
            st.markdown("---")
    
    # Summary
    st.caption(f"{icon} Showing {len(logs)} {level} log entries")


def _render_log_level_console(logs: list, level: str, icon: str):
    """Render logs for a specific level in classic console format"""
    st.markdown(f"### {icon} {level} Logs (Console View)")
    st.caption("Classic one-line format - one log entry per line")
    
    # Display logs in console format with inline copy button
    for i, log_entry in enumerate(logs):
        # Parse log entry to extract level for color coding
        parsed_log = _parse_log_entry_structured(log_entry)
        
        # Color coding for log levels
        level_color = {
            "ERROR": "🔴",
            "WARNING": "🟡", 
            "INFO": "🔵",
            "DEBUG": "🔵"
        }.get(parsed_log["level"], "⚪")
        
        # Compact display with inline copy button
        col1, col2 = st.columns([10, 1])
        
        with col1:
            # Display as single line with color indicator
            st.text(f"{level_color} {log_entry}")
        
        with col2:
            # Copy button inline
            if st.button("📋", key=f"copy_console_{level}_{i}", help="Copy log entry"):
                st.code(log_entry, language="text")
    
    # Summary
    st.caption(f"{icon} Showing {len(logs)} {level} log entries")


def _parse_log_entry_structured(log_entry):
    """Parse a log entry into structured components for Error & Warning tab"""
    # Default values
    timestamp = "Unknown"
    level = "INFO"
    logger_name = "unknown"
    message = log_entry
    
    try:
        # Try different parsing approaches
        if " - " in log_entry:
            # Format: "timestamp - logger_name - level - message"
            parts = log_entry.split(' - ', 3)
            if len(parts) >= 4:
                timestamp = parts[0]
                logger_name = parts[1]
                level = parts[2]
                message = parts[3]
        else:
            # Fallback to standard format parsing
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
        "full_message": log_entry
    }
