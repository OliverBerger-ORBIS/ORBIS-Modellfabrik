#!/usr/bin/env python3
"""
Session Manager - Streamlit Dashboard
Verwaltung und Analyse von MQTT-Sessions für die ORBIS Smart-Factory
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
from session_manager.components.replay_station import show_replay_station
from session_manager.components.session_recorder import show_session_recorder
from session_manager.components.settings_manager import SettingsManager
from session_manager.components.settings_ui import SettingsUI

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
    st.markdown("Verwaltung und Analyse von MQTT-Sessions für die ORBIS Smart-Factory")

    # Settings Manager initialisieren
    if "settings_manager" not in st.session_state:
        st.session_state.settings_manager = SettingsManager()

    if "settings_ui" not in st.session_state:
        st.session_state.settings_ui = SettingsUI(st.session_state.settings_manager)

    # Sidebar Navigation
    st.sidebar.title("Navigation")

    # Tab selection — `key` erlaubt Sprung aus z. B. Session Recorder (Einstellungen-Button)
    tab_options = [
        "📡 Replay Station",
        "🎙️ Session Recorder",
        "⚙️ Einstellungen",
    ]
    tab = st.sidebar.selectbox(
        "Wähle einen Tab:",
        tab_options,
        key="main_sidebar_tab",
    )

    if tab == "📡 Replay Station":
        show_replay_station()
    elif tab == "🎙️ Session Recorder":
        show_session_recorder()
    elif tab == "⚙️ Einstellungen":
        st.session_state.settings_ui.render_settings_page()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Session Manager v1.3.0**")
    st.sidebar.markdown("ORBIS Smart-Factory")


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
