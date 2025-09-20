"""
Logs Component für OMF Dashboard

Zeigt Live-Logs direkt im Dashboard an.
"""

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

def show_logs():
    """Hauptfunktion für Logs-Anzeige"""
    st.header("📋 Live Logs")
    st.markdown("**Echtzeit-Logs der OMF Dashboard-Anwendung**")

    # Log-Buffer aus Session State holen
    log_buffer = st.session_state.get("log_buffer")

    # Test-Debug-Log direkt hinzufügen (nur für Tests)
    if log_buffer is not None:
        from omf.tools.logging_config import get_logger
        
        # OMF-Logging für Tests (thread-sicher)
        test_logger = get_logger("omf.dashboard.logs_test")
        test_logger.info("ℹ️ INFO-TEST aus logs.py Komponente")

        # Teste auch MqttGateway Logger direkt
        mqtt_test_logger = get_logger("omf.tools.mqtt_gateway")
        mqtt_test_logger.info("ℹ️ INFO-TEST MqttGateway Logger")

    if not log_buffer:
        st.warning("❌ Log-Buffer nicht verfügbar")
        st.info("💡 **Hinweis:** Log-Buffer wird beim nächsten Dashboard-Start initialisiert")
        return

    # Refresh-Button
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("🔄 Aktualisieren", key="refresh_logs"):
            request_refresh()

    with col2:
        if st.button("🗑️ Löschen", key="clear_logs"):
            log_buffer.clear()
            request_refresh()

    with col3:
        st.info("💡 Logs werden automatisch aktualisiert")

    # Log-Level Filter (für zukünftige Implementierung)
    st.subheader("🔍 Filter")
    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("DEBUG", value=False, key="show_debug")
        st.checkbox("INFO", value=True, key="show_info")

    with col2:
        st.checkbox("WARNING", value=True, key="show_warning")
        st.checkbox("ERROR", value=True, key="show_error")

    # Logs anzeigen
    st.subheader("📊 Log-Nachrichten")

    # Logs rendern mit aktiven Filtern
    show_debug = st.session_state.get("show_debug", False)
    show_info = st.session_state.get("show_info", True)
    show_warning = st.session_state.get("show_warning", True)
    show_error = st.session_state.get("show_error", True)

    # Filter-Logik implementieren (korrigiert - alle Level können gleichzeitig angezeigt werden)
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

def _show_log_statistics(log_buffer):
    """Zeigt Log-Statistiken an"""
    if not log_buffer:
        st.info("Keine Logs verfügbar")
        return

    # Log-Level zählen
    level_counts = {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}

    for log_entry in log_buffer:
        for level in level_counts:
            if f"[{level}]" in log_entry:
                level_counts[level] += 1
                break

    # Statistiken anzeigen
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("DEBUG", level_counts["DEBUG"])

    with col2:
        st.metric("INFO", level_counts["INFO"])

    with col3:
        st.metric("WARNING", level_counts["WARNING"])

    with col4:
        st.metric("ERROR", level_counts["ERROR"])

    with col5:
        st.metric("CRITICAL", level_counts["CRITICAL"])

    # Gesamtanzahl
    total_logs = sum(level_counts.values())
    st.metric("Gesamt", total_logs)
