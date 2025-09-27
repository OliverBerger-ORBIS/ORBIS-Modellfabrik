"""
Settings Tab Component
Provides settings interface with workpiece subtab
"""

import streamlit as st
import logging
from omf2.common.i18n import translate, get_current_language
from omf2.ui.system.workpiece_subtab import show_workpiece_subtab


def show_settings_tab(logger: logging.Logger):
    """
    Zeigt den Settings Tab mit Subtabs
    
    Args:
        logger: Logger instance für diese Komponente
    """
    logger.info("Settings Tab geöffnet")
    
    current_lang = get_current_language()
    
    st.header(f"⚙️ {translate('settings_title', current_lang)}")
    
    # Subtabs für Settings
    subtab_configs = [
        {
            "key": "workpiece",
            "title": translate("workpiece", current_lang),
            "icon": "🔧",
            "component": show_workpiece_subtab
        },
        {
            "key": "general", 
            "title": translate("general", current_lang),
            "icon": "🔧",
            "component": _show_general_subtab
        },
        {
            "key": "system",
            "title": translate("system", current_lang), 
            "icon": "🖥️",
            "component": _show_system_subtab
        }
    ]
    
    # Subtabs erstellen
    subtab_labels = [f"{config['icon']} {config['title']}" for config in subtab_configs]
    subtabs = st.tabs(subtab_labels)
    
    # Subtab-Inhalte rendern
    for i, subtab_config in enumerate(subtab_configs):
        with subtabs[i]:
            try:
                logger.info(f"Settings Subtab '{subtab_config['key']}' geöffnet")
                subtab_config["component"](logger)
            except Exception as e:
                logger.error(f"Fehler in Settings Subtab '{subtab_config['key']}': {e}")
                st.error(f"❌ Fehler beim Laden des {subtab_config['title']} Subtabs")


def _show_general_subtab(logger: logging.Logger):
    """Allgemeine Einstellungen"""
    current_lang = get_current_language()
    
    st.subheader(f"🔧 {translate('general', current_lang)}")
    
    st.info("💡 Allgemeine Einstellungen werden hier angezeigt")
    
    # Placeholder für allgemeine Einstellungen
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Feature A aktivieren", value=True)
        st.selectbox("Theme", ["Dark", "Light", "Auto"])
        
    with col2:
        st.number_input("Timeout (s)", min_value=1, max_value=300, value=30)
        st.slider("Refresh Rate (s)", 1, 60, 5)


def _show_system_subtab(logger: logging.Logger):
    """System-Einstellungen"""
    current_lang = get_current_language()
    
    st.subheader(f"🖥️ {translate('system', current_lang)}")
    
    st.info("💡 System-Einstellungen werden hier angezeigt")
    
    # Placeholder für System-Einstellungen
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
        st.checkbox("Debug Mode", value=False)
        
    with col2:
        st.number_input("Max Log Files", min_value=1, max_value=100, value=10)
        st.text_input("Log Directory", value="logs/")
        
    if st.button("System Diagnostics"):
        st.success("✅ System läuft ordnungsgemäß")
        logger.info("System Diagnostics ausgeführt")