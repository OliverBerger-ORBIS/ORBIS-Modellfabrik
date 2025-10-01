"""
Internationalization (i18n) support for OMF2 Dashboard
Provides multi-language support for German, English, and French
"""

from typing import Dict, Any, Optional
from pathlib import Path
import yaml

from omf2.common.logger import get_logger

logger = get_logger(__name__)


class I18nManager:
    """Manages internationalization for the OMF2 Dashboard"""
    
    def __init__(self):
        self.current_language = 'de'  # Default to German
        self.translations = {}
        self.supported_languages = ['de', 'en', 'fr']
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files"""
        try:
            # Define default translations inline for now
            self.translations = {
                'de': {
                    'dashboard': {
                        'title': 'OMF2 Dashboard',
                        'subtitle': 'ORBIS Modellfabrik Steuerung',
                        'welcome': 'Willkommen im OMF2 Dashboard'
                    },
                    'roles': {
                        'admin': 'Administrator',
                        'supervisor': 'Supervisor', 
                        'operator': 'Operator',
                    },
                    'tabs': {
                        'ccu_dashboard': 'CCU Dashboard',
                        'system_logs': 'System-Logs',
                        'admin_settings': 'Admin-Einstellungen',
                        'steering_factory': 'Fabrik-Steuerung'
                    },
                    'common': {
                        'connect': 'Verbinden',
                        'disconnect': 'Trennen',
                        'start': 'Starten',
                        'stop': 'Stoppen',
                        'status': 'Status',
                        'error': 'Fehler',
                        'success': 'Erfolgreich',
                        'loading': 'Wird geladen...',
                        'refresh': 'Aktualisieren'
                    }
                },
                'en': {
                    'dashboard': {
                        'title': 'OMF2 Dashboard',
                        'subtitle': 'ORBIS Model Factory Control',
                        'welcome': 'Welcome to OMF2 Dashboard'
                    },
                    'roles': {
                        'admin': 'Administrator',
                        'supervisor': 'Supervisor',
                        'operator': 'Operator', 
                    },
                    'tabs': {
                        'ccu_dashboard': 'CCU Dashboard',
                        'system_logs': 'System Logs',
                        'admin_settings': 'Admin Settings',
                        'steering_factory': 'Generic Steering'
                    },
                    'common': {
                        'connect': 'Connect',
                        'disconnect': 'Disconnect',
                        'start': 'Start',
                        'stop': 'Stop',
                        'status': 'Status',
                        'error': 'Error',
                        'success': 'Success',
                        'loading': 'Loading...',
                        'refresh': 'Refresh'
                    }
                },
                'fr': {
                    'dashboard': {
                        'title': 'Tableau de bord OMF2',
                        'subtitle': 'Contrôle de la fabrique modèle ORBIS',
                        'welcome': 'Bienvenue au tableau de bord OMF2'
                    },
                    'roles': {
                        'admin': 'Administrateur',
                        'supervisor': 'Superviseur',
                        'operator': 'Opérateur',
                    },
                    'tabs': {
                        'ccu_dashboard': 'Tableau de bord CCU',
                        'system_logs': 'Journaux système',
                        'admin_settings': 'Paramètres admin',
                        'steering_factory': 'Contrôle usine'
                    },
                    'common': {
                        'connect': 'Connecter',
                        'disconnect': 'Déconnecter',
                        'start': 'Démarrer',
                        'stop': 'Arrêter',
                        'status': 'Statut',
                        'error': 'Erreur',
                        'success': 'Succès',
                        'loading': 'Chargement...',
                        'refresh': 'Actualiser'
                    }
                }
            }
            logger.info(f"✅ Translations loaded for languages: {list(self.translations.keys())}")
        except Exception as e:
            logger.error(f"❌ Failed to load translations: {e}")
            # Fallback to English-only
            self.translations = {
                'en': {
                    'dashboard': {'title': 'OMF2 Dashboard'},
                    'common': {'error': 'Error', 'loading': 'Loading...'}
                }
            }
    
    def set_language(self, language: str):
        """Set the current language"""
        if language in self.supported_languages:
            self.current_language = language
            logger.info(f"🌐 Language set to: {language}")
        else:
            logger.warning(f"⚠️ Unsupported language: {language}")
    
    def get_current_language(self) -> str:
        """Get the current language"""
        return self.current_language
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return self.supported_languages
    
    def translate(self, key: str, language: Optional[str] = None) -> str:
        """
        Get translated string for the given key
        
        Args:
            key: Translation key in dot notation (e.g., 'dashboard.title')
            language: Language code (uses current language if not specified)
        
        Returns:
            Translated string or the key if translation not found
        """
        if language is None:
            language = self.current_language
        
        # Handle fallback to English if language not available
        if language not in self.translations:
            language = 'en'
        
        # Navigate through the nested dictionary
        try:
            keys = key.split('.')
            value = self.translations[language]
            
            for k in keys:
                value = value[k]
            
            return str(value)
        except (KeyError, TypeError):
            logger.warning(f"⚠️ Translation not found for key: {key} (language: {language})")
            return key  # Return key as fallback
    
    def get_language_display_name(self, language: str) -> str:
        """Get display name for language"""
        display_names = {
            'de': 'Deutsch',
            'en': 'English', 
            'fr': 'Français'
        }
        return display_names.get(language, language)
    
    def get_role_name(self, role: str, language: Optional[str] = None) -> str:
        """Get translated role name"""
        return self.translate(f'roles.{role}', language)
    
    def get_tab_name(self, tab: str, language: Optional[str] = None) -> str:
        """Get translated tab name"""
        return self.translate(f'tabs.{tab}', language)