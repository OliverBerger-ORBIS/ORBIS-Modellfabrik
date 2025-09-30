"""
System Logs Tab für OMF2 Dashboard

Zeigt Live-Logs direkt im Dashboard an - portiert von OMF Dashboard.
"""

import streamlit as st
from collections import deque
import logging
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

# Logger für Logs-Tab
logger = get_logger("omf2.ui.admin.logs.logs_tab")
def render_logs_tab():  # FIXED RINGBUFFER ERROR
    """Hauptfunktion für System Logs-Anzeige"""
    logger.info("📋 Rendering System Logs Tab")
    
    st.header("📋 System Logs")
    st.markdown("**Live-Logs der OMF2 Dashboard-Anwendung**")
    
    # Log-Buffer aus Session State holen oder initialisieren
    log_buffer = st.session_state.get("log_buffer")
    
    if not log_buffer:
        # Log-Buffer initialisieren falls nicht vorhanden
        from collections import deque
        from omf2.common.streamlit_log_buffer import RingBufferHandler, create_log_buffer
        import logging
        
        # Create ring buffer
        st.session_state['log_buffer'] = create_log_buffer(maxlen=1000)
        log_buffer = st.session_state['log_buffer']
        
        # Setup RingBufferHandler for all loggers
        ring_handler = RingBufferHandler(log_buffer)
        # Ensure all existing loggers use the ring buffer
        for logger_name in ["omf2", "omf2.dashboard", "omf2.admin", "omf2.ui", "omf2.common"]:
            existing_logger = logging.getLogger(logger_name)
            if not any(isinstance(h, RingBufferHandler) for h in existing_logger.handlers):
                existing_logger.addHandler(ring_handler)
        ring_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(ring_handler)
        st.session_state['ring_buffer_handler'] = ring_handler
        
        logger.info("📋 System logs tab ready - RINGBUFFER FIXED")
        
    # Refresh-Button
    col1, col2, col3 = st.columns([1, 1, 4])
    
    with col1:
        if st.button("🔄 Aktualisieren", key="refresh_logs"):
            request_refresh()
    
    with col2:
        if st.button("🗑️ Löschen", key="clear_logs"):
            log_buffer.clear()
            logger.info("🗑️ Log buffer cleared")
            logger.info("📋 New logs will appear here")
            request_refresh()
    
    with col3:
        if st.button("🧪 Test Log", key="test_log"):
            logger.info("🧪 Test log message - RingBuffer should work")
            request_refresh()
    
    with col3:
        st.info("💡 Logs werden automatisch aktualisiert")
    
    # Log-Level Filter
    st.subheader("🔍 Filter")
    col1, col2 = st.columns(2)
    
    with col1:
        show_debug = st.checkbox("DEBUG", value=False, key="show_debug")
        show_info = st.checkbox("INFO", value=True, key="show_info")
    
    with col2:
        show_warning = st.checkbox("WARNING", value=True, key="show_warning")
        show_error = st.checkbox("ERROR", value=True, key="show_error")
    
    # Logs anzeigen
    st.subheader("📋 Live Logs")
    
    if not log_buffer:
        st.info("Keine Logs verfügbar")
        return
    
    # Filter anwenden
    filtered_logs = []
    st.info(f"📊 Zeige {len(filtered_logs)} von {len(log_buffer)} verfügbaren Logs")
    for log_entry in log_buffer:
        if "[DEBUG]" in log_entry and not show_debug:
            continue
        if "[INFO]" in log_entry and not show_info:
            continue
        if "[WARNING]" in log_entry and not show_warning:
            continue
        if "[ERROR]" in log_entry and not show_error:
            continue
        filtered_logs.append(log_entry)
    
    # Logs in umgekehrter Reihenfolge anzeigen (neueste zuerst)
    for log_entry in reversed(filtered_logs):  # Nur die letzten 50 Einträge
        # Farbkodierung basierend auf Log-Level
        if "[ERROR]" in log_entry:
            st.error(log_entry)
        elif "[WARNING]" in log_entry:
            st.warning(log_entry)
        elif "[INFO]" in log_entry:
            st.info(log_entry)
        elif "[DEBUG]" in log_entry:
            st.text(log_entry)
        else:
            st.text(log_entry)
    
    # Statistiken
    st.subheader("📊 Statistiken")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        debug_count = sum(1 for log in log_buffer if "[DEBUG]" in log)
        st.metric("DEBUG", debug_count)
    
    with col2:
        info_count = sum(1 for log in log_buffer if "[INFO]" in log)
        st.metric("INFO", info_count)
       
    with col3:
        warning_count = sum(1 for log in log_buffer if "[WARNING]" in log)
        st.metric("WARNING", warning_count)
    
    with col4:
        error_count = sum(1 for log in log_buffer if "[ERROR]" in log)
        st.metric("ERROR", error_count)
