"""
Logs Component für OMF Dashboard

Zeigt Live-Logs direkt im Dashboard an.
"""

import streamlit as st

from src_orbis.omf.tools.streamlit_log_buffer import render_logs_panel


def show_logs():
    """Hauptfunktion für Logs-Anzeige"""
    st.header("📋 Live Logs")
    st.markdown("**Echtzeit-Logs der OMF Dashboard-Anwendung**")

    # Log-Buffer aus Session State holen
    log_buffer = st.session_state.get("log_buffer")

    if not log_buffer:
        st.warning("❌ Log-Buffer nicht verfügbar")
        return

    # Refresh-Button
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("🔄 Aktualisieren", key="refresh_logs"):
            st.rerun()

    with col2:
        if st.button("🗑️ Löschen", key="clear_logs"):
            log_buffer.clear()
            st.rerun()

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

    # Logs rendern
    log_text = render_logs_panel(log_buffer, max_lines=500)

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
