"""
Internationalization (i18n) Module for OMF Dashboard
Provides multi-language support for the application
"""

import streamlit as st
from typing import Dict, Any

# Translation dictionaries
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "de": {
        # Main tabs
        "settings": "Einstellungen",
        "logs": "Protokolle", 
        "message_center": "Nachrichten-Zentrale",
        
        # Settings subtabs
        "workpiece": "Werkstück",
        "general": "Allgemein",
        "system": "System",
        
        # Common UI elements
        "language": "Sprache",
        "save": "Speichern",
        "cancel": "Abbrechen",
        "loading": "Lädt...",
        "error": "Fehler",
        "success": "Erfolgreich",
        "warning": "Warnung",
        "info": "Information",
        
        # Settings tab specific
        "settings_title": "Dashboard Einstellungen",
        "workpiece_config": "Werkstück-Konfiguration",
        "workpiece_settings": "Werkstück-Einstellungen",
        
        # Logs tab specific
        "logs_title": "System-Protokolle",
        "log_level": "Log-Level",
        "clear_logs": "Protokolle löschen",
        "refresh_logs": "Aktualisieren",
        
        # Message center specific
        "message_center_title": "Nachrichten-Zentrale",
        "messages": "Nachrichten",
        "send_message": "Nachricht senden",
        "clear_messages": "Nachrichten löschen",
    },
    "en": {
        # Main tabs
        "settings": "Settings",
        "logs": "Logs",
        "message_center": "Message Center",
        
        # Settings subtabs
        "workpiece": "Workpiece",
        "general": "General", 
        "system": "System",
        
        # Common UI elements
        "language": "Language",
        "save": "Save",
        "cancel": "Cancel",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Information",
        
        # Settings tab specific
        "settings_title": "Dashboard Settings",
        "workpiece_config": "Workpiece Configuration",
        "workpiece_settings": "Workpiece Settings",
        
        # Logs tab specific
        "logs_title": "System Logs",
        "log_level": "Log Level",
        "clear_logs": "Clear Logs",
        "refresh_logs": "Refresh",
        
        # Message center specific
        "message_center_title": "Message Center",
        "messages": "Messages",
        "send_message": "Send Message",
        "clear_messages": "Clear Messages",
    }
}


def get_current_language() -> str:
    """Get the current language from session state"""
    return st.session_state.get("language", "de")


def set_language(language: str) -> None:
    """Set the current language in session state"""
    if language in TRANSLATIONS:
        st.session_state.language = language
    else:
        st.session_state.language = "de"  # Default fallback


def translate(key: str, language: str = None) -> str:
    """
    Translate a key to the specified language
    
    Args:
        key: Translation key
        language: Target language (defaults to current language)
        
    Returns:
        Translated string or the key itself if no translation found
    """
    if language is None:
        language = get_current_language()
    
    return TRANSLATIONS.get(language, {}).get(key, key)


def get_available_languages() -> Dict[str, str]:
    """Get available languages with their display names"""
    return {
        "de": "🇩🇪 Deutsch",
        "en": "🇺🇸 English"
    }