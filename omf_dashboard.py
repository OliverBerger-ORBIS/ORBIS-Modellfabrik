#!/usr/bin/env python3
"""
OMF Dashboard - Modulare Streamlit-App
Haupteinstiegspunkt für das ORBIS Modellfabrik Dashboard
"""

import logging
import streamlit as st
from pathlib import Path

# Import centralized logging configuration
from omf.dashboard.tools.logging_config import configure_logging, get_logger

# Import i18n module
from omf2.common.i18n import translate, get_current_language, set_language

# Import tab components
from omf2.ui.system.settings_tab import show_settings_tab
from omf2.ui.system.logs_tab import show_logs_tab
from omf2.ui.message_center.message_center_tab import show_message_center_tab


def setup_logging():
    """Zentrales Logging-Setup"""
    if not st.session_state.get("_logging_initialized"):
        root_logger, listener = configure_logging(
            app_name="omf_dashboard",
            level=logging.INFO,
            log_dir="logs",
            console_pretty=True
        )
        
        # Globaler Logger für das Dashboard
        dashboard_logger = get_logger("omf_dashboard")
        dashboard_logger.info("🚀 OMF Dashboard gestartet")
        
        st.session_state._logging_initialized = True
        st.session_state._root_logger = root_logger
        st.session_state._listener = listener
        
        return dashboard_logger
    else:
        return get_logger("omf_dashboard")


def setup_page_config():
    """Streamlit Seitenkonfiguration"""
    st.set_page_config(
        page_title="OMF Dashboard",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def setup_sidebar():
    """Sidebar mit Sprachauswahl"""
    with st.sidebar:
        st.title("🏭 OMF Dashboard")
        
        # Sprachauswahl
        current_lang = get_current_language()
        lang_options = {"de": "🇩🇪 Deutsch", "en": "🇺🇸 English"}
        
        selected_lang = st.selectbox(
            "Sprache / Language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(current_lang)
        )
        
        if selected_lang != current_lang:
            set_language(selected_lang)
            st.rerun()


def main():
    """Hauptfunktion des OMF Dashboards"""
    
    # 1. Seite konfigurieren
    setup_page_config()
    
    # 2. Logging initialisieren
    logger = setup_logging()
    
    # 3. Sidebar einrichten
    setup_sidebar()
    
    # 4. Hauptbereich mit Tabs
    current_lang = get_current_language()
    
    # Tab-Definitionen
    tab_configs = [
        {
            "key": "settings",
            "title": translate("settings", current_lang),
            "icon": "⚙️",
            "component": show_settings_tab
        },
        {
            "key": "logs", 
            "title": translate("logs", current_lang),
            "icon": "📋",
            "component": show_logs_tab
        },
        {
            "key": "message_center",
            "title": translate("message_center", current_lang), 
            "icon": "💬",
            "component": show_message_center_tab
        }
    ]
    
    # Tabs erstellen
    tab_labels = [f"{config['icon']} {config['title']}" for config in tab_configs]
    tabs = st.tabs(tab_labels)
    
    # Tab-Inhalte rendern
    for i, tab_config in enumerate(tab_configs):
        with tabs[i]:
            try:
                logger.info(f"🔧 {tab_config['key'].title()} Tab geöffnet")
                tab_config["component"](logger)
            except Exception as e:
                logger.error(f"Fehler in {tab_config['key']} Tab: {e}")
                st.error(f"❌ Fehler beim Laden des {tab_config['title']} Tabs")


if __name__ == "__main__":
    main()