#!/usr/bin/env python3
"""
System Logs Tab - System Logs UI Component
Einfache Logs-Funktionalität aus dem alten Dashboard
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_logs_tab():
    """Render System Logs Tab - Einfache Logs-Funktionalität"""
    logger.info("📋 Rendering System Logs Tab")
    try:
        st.header("📋 Live Logs")
        st.markdown("**Echtzeit-Logs der OMF2 Dashboard-Anwendung**")
        
        # Log-Buffer aus Session State holen
        log_buffer = st.session_state.get("log_buffer")
        
        if not log_buffer:
            st.warning("❌ Log-Buffer nicht verfügbar")
            st.info("💡 **Hinweis:** Log-Buffer wird beim nächsten Dashboard-Start initialisiert")
            return
        
        # Refresh/Löschen Buttons
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("🔄 Aktualisieren", key="logs_refresh_btn"):
                request_refresh()
        
        with col2:
            if st.button("🗑️ Löschen", key="logs_clear_btn"):
                log_buffer.clear()
                request_refresh()
        
        with col3:
            st.info("💡 Logs werden automatisch aktualisiert")
        
        # Log-Level Filter
        st.subheader("🔍 Filter")
        col1, col2 = st.columns(2)
        
        with col1:
            show_debug = st.checkbox("DEBUG", value=False, key="logs_show_debug")
            show_info = st.checkbox("INFO", value=True, key="logs_show_info")
        
        with col2:
            show_warning = st.checkbox("WARNING", value=True, key="logs_show_warning")
            show_error = st.checkbox("ERROR", value=True, key="logs_show_error")
        
        # Logs anzeigen
        st.subheader("📊 Log-Nachrichten")
        
        # Filter-Logik
        filtered_logs = []
        for log_entry in log_buffer:
            should_show = False
            
            if show_debug and "[DEBUG]" in log_entry:
                should_show = True
            if show_info and "[INFO]" in log_entry:
                should_show = True
            if show_warning and "[WARNING]" in log_entry:
                should_show = True
            if show_error and "[ERROR]" in log_entry:
                should_show = True
            
            if should_show:
                filtered_logs.append(log_entry)
        
        # Logs als Text rendern
        log_text = "\n".join(filtered_logs) if filtered_logs else "—"
        
        if log_text == "—":
            st.info("ℹ️ Keine Logs verfügbar")
            return
        
        # Logs in Code-Block anzeigen
        st.code(log_text, language="text")
        
        # Log-Statistiken
        with st.expander("📈 Log-Statistiken", expanded=False):
            _show_log_statistics(log_buffer)
        
    except Exception as e:
        logger.error(f"❌ System Logs Tab rendering error: {e}")
        st.error(f"❌ System Logs Tab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_log_statistics(log_buffer):
    """Zeigt Log-Statistiken an"""
    try:
        total_logs = len(log_buffer)
        
        # Log-Level zählen
        debug_count = sum(1 for log in log_buffer if "[DEBUG]" in log)
        info_count = sum(1 for log in log_buffer if "[INFO]" in log)
        warning_count = sum(1 for log in log_buffer if "[WARNING]" in log)
        error_count = sum(1 for log in log_buffer if "[ERROR]" in log)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("DEBUG", debug_count)
        
        with col2:
            st.metric("INFO", info_count)
        
        with col3:
            st.metric("WARNING", warning_count)
        
        with col4:
            st.metric("ERROR", error_count)
        
        st.caption(f"📊 Gesamt: {total_logs} Log-Einträge")
        
    except Exception as e:
        logger.error(f"❌ Log statistics error: {e}")
        st.error("❌ Fehler beim Laden der Statistiken")
