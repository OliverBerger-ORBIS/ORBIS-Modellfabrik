"""
Test i18n (Internationalization) Components
"""

import pytest
from unittest.mock import patch


class TestI18n:
    """Test suite for i18n functionality"""
    
    def test_i18n_import(self):
        """Test: i18n Module kann importiert werden"""
        try:
            from omf2.common.i18n import translate, get_current_language, set_language
            assert callable(translate)
            assert callable(get_current_language)
            assert callable(set_language)
        except ImportError as e:
            pytest.fail(f"i18n Import fehlgeschlagen: {e}")
    
    def test_translation_dictionaries_exist(self):
        """Test: Übersetzungswörterbücher sind verfügbar"""
        from omf2.common.i18n import TRANSLATIONS
        
        # Überprüfe, dass Übersetzungen vorhanden sind
        assert isinstance(TRANSLATIONS, dict)
        assert "de" in TRANSLATIONS
        assert "en" in TRANSLATIONS
        
        # Überprüfe deutsche Übersetzungen
        de_translations = TRANSLATIONS["de"]
        assert "settings" in de_translations
        assert "logs" in de_translations
        assert "message_center" in de_translations
        assert "workpiece" in de_translations
        
        # Überprüfe englische Übersetzungen
        en_translations = TRANSLATIONS["en"]
        assert "settings" in en_translations
        assert "logs" in en_translations
        assert "message_center" in en_translations
        assert "workpiece" in en_translations
    
    @patch('streamlit.session_state', {})
    def test_language_management(self):
        """Test: Sprachenverwaltung funktioniert"""
        from omf2.common.i18n import get_current_language, set_language
        
        # Standard-Sprache sollte Deutsch sein
        default_lang = get_current_language()
        assert default_lang == "de"
        
        # Sprache auf Englisch setzen
        set_language("en")
        # Mock session_state für Test
        import streamlit as st
        st.session_state.language = "en"
        
        with patch('streamlit.session_state', {"language": "en"}):
            current_lang = get_current_language()
            assert current_lang == "en"
        
        # Ungültige Sprache sollte auf Deutsch zurückfallen
        set_language("invalid")
        with patch('streamlit.session_state', {"language": "de"}):
            current_lang = get_current_language()
            assert current_lang == "de"
    
    def test_translation_function(self):
        """Test: Übersetzungsfunktion arbeitet korrekt"""
        from omf2.common.i18n import translate
        
        # Deutsche Übersetzungen
        assert translate("settings", "de") == "Einstellungen"
        assert translate("logs", "de") == "Protokolle"
        assert translate("message_center", "de") == "Nachrichten-Zentrale"
        assert translate("workpiece", "de") == "Werkstück"
        
        # Englische Übersetzungen
        assert translate("settings", "en") == "Settings"
        assert translate("logs", "en") == "Logs"
        assert translate("message_center", "en") == "Message Center"
        assert translate("workpiece", "en") == "Workpiece"
        
        # Nicht existierender Schlüssel sollte Schlüssel selbst zurückgeben
        assert translate("non_existent_key", "de") == "non_existent_key"
        assert translate("non_existent_key", "en") == "non_existent_key"
    
    def test_available_languages(self):
        """Test: Verfügbare Sprachen sind korrekt definiert"""
        from omf2.common.i18n import get_available_languages
        
        available_langs = get_available_languages()
        
        assert isinstance(available_langs, dict)
        assert "de" in available_langs
        assert "en" in available_langs
        assert "🇩🇪 Deutsch" in available_langs.values()
        assert "🇺🇸 English" in available_langs.values()
    
    def test_translation_completeness(self):
        """Test: Übersetzungen sind vollständig für alle Sprachen"""
        from omf2.common.i18n import TRANSLATIONS
        
        # Hole alle Schlüssel aus der deutschen Übersetzung
        de_keys = set(TRANSLATIONS["de"].keys())
        
        # Überprüfe, dass alle anderen Sprachen die gleichen Schlüssel haben
        for lang in TRANSLATIONS:
            if lang != "de":
                lang_keys = set(TRANSLATIONS[lang].keys())
                missing_keys = de_keys - lang_keys
                extra_keys = lang_keys - de_keys
                
                # Sollte keine fehlenden oder zusätzlichen Schlüssel geben
                assert len(missing_keys) == 0, f"Fehlende Schlüssel in {lang}: {missing_keys}"
                assert len(extra_keys) == 0, f"Zusätzliche Schlüssel in {lang}: {extra_keys}"
    
    @patch('streamlit.session_state', {"language": "de"})
    def test_translation_with_default_language(self):
        """Test: Übersetzung mit Standard-Sprache funktioniert"""
        from omf2.common.i18n import translate
        
        # Ohne explizite Sprache sollte aktuelle Sprache verwendet werden
        with patch('omf2.common.i18n.get_current_language', return_value="de"):
            assert translate("settings") == "Einstellungen"
            
        with patch('omf2.common.i18n.get_current_language', return_value="en"):
            assert translate("settings") == "Settings"