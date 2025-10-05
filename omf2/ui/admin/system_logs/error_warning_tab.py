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
    """Render logs for a specific level"""
    
    if not logs:
        st.info(f"{icon} No {level} logs available")
        return
    
    # Show latest logs first (most recent at top)
    logs = list(logs)
    logs.reverse()  # Show newest first
    
    # Display logs
    for i, log_entry in enumerate(logs):
        # Parse log entry to extract components
        try:
            parts = log_entry.split(' - ', 3)
            if len(parts) >= 4:
                timestamp = parts[0]
                logger_name = parts[1]
                log_level = parts[2]
                message = parts[3]
                
                # Create expandable section for each log entry
                with st.expander(f"{icon} [{i+1}] {timestamp} - {logger_name}", expanded=(i < 3)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Message:** {message}")
                        st.write(f"**Logger:** {logger_name}")
                    
                    with col2:
                        st.write(f"**Level:** {log_level}")
                        st.write(f"**Time:** {timestamp}")
                        
                        # Copy button for the log entry
                        if st.button("📋 Copy", key=f"copy_{level}_{i}"):
                            st.write("```")
                            st.code(log_entry)
                            st.write("```")
            else:
                # Fallback for malformed log entries
                st.text(log_entry)
                
        except Exception as e:
            # Fallback for any parsing errors
            st.text(log_entry)
    
    # Summary
    st.caption(f"{icon} Showing {len(logs)} {level} log entries")
