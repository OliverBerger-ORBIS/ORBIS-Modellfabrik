"""
Language Management für OMF Dashboard
Verwaltet Sprachwechsel und i18n
"""

import streamlit as st
from omf.config.omf_config import OmfConfig, TRANSLATIONS
from typing import Dict, List


class LanguageManager:
    """Manager für Sprachwechsel und Internationalisierung"""
    
    SUPPORTED_LANGUAGES = {
        "de": {"name": "Deutsch", "flag": "🇩🇪"},
        "en": {"name": "English", "flag": "🇺🇸"},
        "fr": {"name": "Français", "flag": "🇫🇷"}
    }
    
    @staticmethod
    def get_current_language() -> str:
        """Holt die aktuelle Sprache aus Config oder Session State"""
        # Prüfe Session State zuerst
        if "language" in st.session_state:
            return st.session_state["language"]
        
        # Fallback auf Config
        config = OmfConfig()
        language = config.get("dashboard.language", "de")
        st.session_state["language"] = language
        return language
    
    @staticmethod
    def set_language(language: str):
        """Setzt die Sprache in Session State und Config"""
        st.session_state["language"] = language
        
        # Config auch aktualisieren
        config = OmfConfig()
        config.set("dashboard.language", language)
        config.save_config()
    
    @staticmethod
    def get_translation(key: str, language: str = None) -> str:
        """Holt eine Übersetzung für einen Schlüssel"""
        if language is None:
            language = LanguageManager.get_current_language()
        
        return TRANSLATIONS.get(language, {}).get(key, key)
    
    @staticmethod
    def get_tab_name(tab_key: str, language: str = None) -> str:
        """Holt den übersetzten Tab-Namen"""
        if language is None:
            language = LanguageManager.get_current_language()
        
        return TRANSLATIONS.get(language, {}).get(tab_key, tab_key.replace("_", " ").title())
    
    @staticmethod
    def show_language_selector():
        """Zeigt einen Sprachen-Wähler in der Sidebar"""
        current_language = LanguageManager.get_current_language()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"🌐 {LanguageManager.get_translation('language')}")
        
        # Sprach-Optionen mit Flaggen
        language_options = []
        language_keys = []
        
        for lang_code, lang_info in LanguageManager.SUPPORTED_LANGUAGES.items():
            display_name = f"{lang_info['flag']} {lang_info['name']}"
            language_options.append(display_name)
            language_keys.append(lang_code)
        
        # Aktueller Index finden
        current_index = language_keys.index(current_language) if current_language in language_keys else 0
        
        selected_display = st.sidebar.selectbox(
            LanguageManager.get_translation("select_language"),
            options=language_options,
            index=current_index
        )
        
        # Neue Sprache ermitteln und setzen
        selected_index = language_options.index(selected_display)
        selected_language = language_keys[selected_index]
        
        if selected_language != current_language:
            LanguageManager.set_language(selected_language)
            st.rerun()
        
        # Info über aktuelle Sprache
        st.sidebar.info(f"Aktuelle Sprache: {LanguageManager.SUPPORTED_LANGUAGES[current_language]['name']}")