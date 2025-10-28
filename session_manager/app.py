#!/usr/bin/env python3
"""
Session Manager - Streamlit Dashboard
Verwaltung und Analyse von MQTT-Sessions für die ORBIS Modellfabrik
"""

import sys
from pathlib import Path

# Add project root to Python path so session_manager package can be imported
_app_file = Path(__file__).resolve()
_project_root = _app_file.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import argparse

import streamlit as st

# Import components
from session_manager.components.logs import show_logs
from session_manager.components.replay_station import show_replay_station
from session_manager.components.session_analysis import show_session_analysis
from session_manager.components.session_recorder import show_session_recorder
from session_manager.components.settings_manager import SettingsManager
from session_manager.components.settings_ui import SettingsUI
from session_manager.components.topic_recorder import show_topic_recorder

# Absolute imports for main script (entry point)
from session_manager.utils.logging_config import configure_logging, get_logger

# from session_manager.utils.registry_manager import get_registry  # TODO: Optional feature - registry watch mode
from session_manager.utils.ui_refresh import consume_refresh, request_refresh

# Page configuration
st.set_page_config(page_title="Session Manager", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")


def _init_logging_once():
    """Initialisiert OMF Logging einmal pro Streamlit-Session"""
    if st.session_state.get("_log_init"):
        return

    # Ring-Buffer für UI-Logs erstellen wenn nicht vorhanden
    if "session_manager_log_buffer" not in st.session_state:
        from session_manager.utils.streamlit_log_buffer import create_log_buffer

        st.session_state.session_manager_log_buffer = create_log_buffer(maxlen=1000)

    # Aktuelles Logging-Level aus Session State holen, Default: INFO
    current_level = st.session_state.get("logging_level", "INFO")
    level_mapping = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
    level = level_mapping.get(current_level, 20)

    # OMF Logging konfigurieren mit RingBuffer
    root, listener = configure_logging(
        app_name="session_manager",
        level=level,
        log_dir="logs",
        json_file="session_manager.jsonl",
        ring_buffer=st.session_state.session_manager_log_buffer,
        cleanup_on_start=True,
        console_pretty=True,
    )

    # Listener in Session State speichern
    st.session_state["_log_listener"] = listener
    st.session_state["_log_init"] = True


def show_logging_settings(logger):
    """Logging-Konfiguration und Live-Logs Tab"""
    st.subheader("📝 Logging-Konfiguration")

    # UI-Refresh System initialisiert (wird in main() verwendet)

    # Aktuelles Level anzeigen
    current_level = st.session_state.get("logging_level", "INFO")
    st.info(f"🔍 Aktuelles Logging-Level: **{current_level}**")

    # Level-Auswahl
    level_options = ["DEBUG", "INFO", "WARNING", "ERROR"]
    selected_level = st.selectbox(
        "Logging-Level auswählen:",
        level_options,
        index=level_options.index(current_level),
        help=(
            "DEBUG: Detaillierte Debug-Informationen\n"
            "INFO: Allgemeine Informationen\n"
            "WARNING: Warnungen\n"
            "ERROR: Nur Fehler"
        ),
    )

    # Level-Änderung verarbeiten
    if selected_level != current_level:
        st.session_state["logging_level"] = selected_level
        st.success(f"✅ Logging-Level auf **{selected_level}** geändert")
        request_refresh()

    # Info über automatisches Log-Cleanup
    st.info("ℹ️ **Hinweis:** Alte Log-Dateien werden automatisch beim Neustart der Anwendung gelöscht.")

    # Log-Datei Info
    log_file = Path("logs/session_manager.jsonl")
    if log_file.exists():
        file_size = log_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        st.markdown(f"📄 **Log-Datei:** `{log_file}`")
        st.markdown(f"📊 **Dateigröße:** {file_size_mb:.2f} MB")

        # Log-Datei löschen Option
        if st.button("🗑️ Log-Datei löschen", help="Löscht die aktuelle Log-Datei"):
            try:
                log_file.unlink()
                st.success("✅ Log-Datei gelöscht")
                request_refresh()
            except Exception as e:
                st.error(f"❌ Fehler beim Löschen: {e}")
    else:
        st.warning("📄 Log-Datei existiert noch nicht")

    # Demo-Sektion
    st.markdown("### 🧪 Logging-Demo")
    st.markdown("Teste verschiedene Log-Level:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🐛 DEBUG"):
            logger.debug("Debug-Nachricht: Detaillierte Debug-Informationen")
            st.success("Debug-Nachricht gesendet")

    with col2:
        if st.button("ℹ️ INFO"):
            logger.info("Info-Nachricht: Allgemeine Informationen")
            st.success("Info-Nachricht gesendet")

    with col3:
        if st.button("⚠️ WARNING"):
            logger.warning("Warning-Nachricht: Warnung vor einem Problem")
            st.success("Warning-Nachricht gesendet")

    with col4:
        if st.button("❌ ERROR"):
            logger.error("Error-Nachricht: Ein Fehler ist aufgetreten")
            st.success("Error-Nachricht gesendet")

    # Log-Viewer
    st.markdown("### 📋 Live Log-Viewer")
    if log_file.exists():
        try:
            with open(log_file, encoding="utf-8") as f:
                log_lines = f.readlines()

            # Letzte 20 Zeilen anzeigen
            recent_lines = log_lines[-20:] if len(log_lines) > 20 else log_lines
            log_content = "".join(recent_lines)

            st.code(log_content, language="text")
        except Exception as e:
            st.error(f"❌ Fehler beim Lesen der Log-Datei: {e}")
    else:
        st.info("📄 Keine Log-Datei vorhanden")


def main():
    """Hauptfunktion des Session Managers"""

    # UI-Refresh prüfen (früh in main())
    if consume_refresh():
        request_refresh()
        return

    # OMF Logging initialisieren
    _init_logging_once()
    logger = get_logger("session_manager.main")
    logger.info("Session Manager gestartet")

    # Header
    st.title("🎙️ Session Manager")
    st.markdown("Verwaltung und Analyse von MQTT-Sessions für die ORBIS Modellfabrik")

    # Settings Manager initialisieren
    if "settings_manager" not in st.session_state:
        st.session_state.settings_manager = SettingsManager()

    if "settings_ui" not in st.session_state:
        st.session_state.settings_ui = SettingsUI(st.session_state.settings_manager)

    # Sidebar Navigation
    st.sidebar.title("Navigation")

    # Tab selection - Topic Recorder als Default
    tab = st.sidebar.selectbox(
        "Wähle einen Tab:",
        [
            "📂 Topic Recorder",
            "📡 Replay Station",
            "🎙️ Session Recorder",
            "📊 Session Analyse",
            "⚙️ Einstellungen",
            "📝 Logging",
        ],
    )

    # Tab content
    if tab == "📂 Topic Recorder":
        show_topic_recorder()
    elif tab == "📡 Replay Station":
        show_replay_station()
    elif tab == "🎙️ Session Recorder":
        show_session_recorder()
    elif tab == "📊 Session Analyse":
        show_session_analysis()
    elif tab == "⚙️ Einstellungen":
        st.session_state.settings_ui.render_settings_page()
    elif tab == "📝 Logging":
        show_logging_settings(logger)
        st.markdown("---")
        show_logs()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Session Manager v1.1.0**")
    st.sidebar.markdown("ORBIS Modellfabrik")


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Session Manager - MQTT Session Management")
    parser.add_argument("--registry-watch", action="store_true", help="Enable registry watch mode for live development")
    parser.add_argument("--model-version", default="v1.0.0", help="Expected model version (default: v1.0.0)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Initialize registry with watch mode if requested
    # TODO: Registry watch mode disabled during migration - needs registry_manager implementation
    # if args.registry_watch:
    #     registry = get_registry(watch_mode=True)
    #     print("🔄 Registry watch mode enabled - live reloading active")

    main()
