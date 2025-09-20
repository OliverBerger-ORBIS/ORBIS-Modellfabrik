"""
Session Manager Logs Component - Duplikat der OMF Dashboard Logs

Zeigt Live-Logs für den Session Manager an.
"""

import json

import streamlit as st

from omf.tools.logging_config import get_logger
from omf.tools.streamlit_log_buffer import RingBufferHandler, create_log_buffer
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("omf.helper_apps.session_manager.components.logs")


def show_logs():
    """Zeigt Live-Logs für den Session Manager an"""
    logger.info("📋 Session Manager Logs geladen")

    st.header("📋 Session Manager Logs")
    st.markdown("**Live-Logs für den Session Manager**")

    # Log-Buffer initialisieren
    if "session_manager_log_buffer" not in st.session_state:
        st.session_state.session_manager_log_buffer = create_log_buffer(maxlen=1000)

        # Ring-Buffer-Handler hinzufügen
        rb = RingBufferHandler(st.session_state.session_manager_log_buffer)
        rb.setLevel(logging.DEBUG)

        # Handler zu Session Manager Loggern hinzufügen
        session_logger = logging.getLogger("session_manager")
        session_logger.addHandler(rb)
        session_logger.propagate = False

        # Weitere Session Manager Logger
        for logger_name in [
            "session_manager.main",
            "session_manager.order_analyzer",
            "session_manager.auftrag_rot_analyzer",
            "session_manager.ui_components",
        ]:
            logger_obj = logging.getLogger(logger_name)
            logger_obj.addHandler(rb)
            logger_obj.propagate = False

    # Log-Level Filter
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        level_filter = st.selectbox(
            "Log-Level Filter:",
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
            index=1,
            key="session_manager_log_level_filter",
        )

    with col2:
        if st.button("🔄 Refresh", key="session_manager_logs_refresh"):
            request_refresh()

    with col3:
        if st.button("🗑️ Clear Logs", key="session_manager_logs_clear"):
            st.session_state.session_manager_log_buffer.clear()
            request_refresh()

    # Logs anzeigen
    logs = list(st.session_state.session_manager_log_buffer)

    if not logs:
        st.info("📝 Keine Logs verfügbar")
        return

    # Filter anwenden
    if level_filter != "ALL":
        level_mapping = {"DEBUG": "DEBUG", "INFO": "INFO", "WARNING": "WARNING", "ERROR": "ERROR"}
        target_level = level_mapping.get(level_filter, "INFO")
        filtered_logs = []

        for log_entry in logs:
            try:
                # Versuche JSON zu parsen
                log_data = json.loads(log_entry)
                if log_data.get("level") == target_level:
                    filtered_logs.append(log_entry)
            except json.JSONDecodeError:
                # Fallback für nicht-JSON Logs
                if target_level in log_entry:
                    filtered_logs.append(log_entry)

        logs = filtered_logs

    # Logs in umgekehrter Reihenfolge anzeigen (neueste zuerst)
    logs.reverse()

    # Logs-Container
    st.markdown(f"**{len(logs)} Log-Einträge** (Level: {level_filter})")

    # Logs anzeigen
    for _i, log_entry in enumerate(logs[:100]):  # Max 100 Einträge
        try:
            # Versuche JSON zu parsen
            log_data = json.loads(log_entry)

            # Log-Level bestimmen
            level = log_data.get("level", "INFO")
            message = log_data.get("msg", log_entry)
            logger_name = log_data.get("logger", "unknown")
            # timestamp = log_data.get("timestamp", "")  # Unused variable

            # Farben basierend auf Level
            if level == "ERROR":
                st.error(f"🔴 **{level}** | {logger_name} | {message}")
            elif level == "WARNING":
                st.warning(f"🟡 **{level}** | {logger_name} | {message}")
            elif level == "INFO":
                st.info(f"🔵 **{level}** | {logger_name} | {message}")
            elif level == "DEBUG":
                st.text(f"⚪ **{level}** | {logger_name} | {message}")
            else:
                st.text(f"📝 **{level}** | {logger_name} | {message}")

        except json.JSONDecodeError:
            # Fallback für nicht-JSON Logs
            st.text(f"📝 {log_entry}")

    if len(logs) > 100:
        st.info(f"📄 Zeige die letzten 100 von {len(logs)} Log-Einträgen")
