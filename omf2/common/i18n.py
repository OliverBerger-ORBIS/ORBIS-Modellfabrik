"""
Internationalization (i18n) support for OMF2 Dashboard
Provides multi-language support for German, English, and French

NON-BLOCKING ARCHITECTURE:
- Lazy Loading: Translations werden beim ersten Zugriff geladen (kein File I/O im __init__)
- Session State: Aktuelle Sprache wird in Streamlit Session State gespeichert
- YAML-basiert: Translations in config/translations/ (Fallback zu inline)
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from omf2.common.logger import get_logger

logger = get_logger(__name__)


class I18nManager:
    """
    Manages internationalization for the OMF2 Dashboard

    NON-BLOCKING: Kein File I/O im __init__ - Lazy Loading Pattern
    SESSION STATE: Verwendet st.session_state für aktuelle Sprache
    """

    def __init__(self, session_state=None):
        """
        Initialize I18nManager - KEIN File I/O hier!

        Args:
            session_state: Optional Streamlit session_state für Sprach-Persistenz
        """
        self.session_state = session_state
        self.translations = None  # Lazy Loading - wird beim ersten Zugriff geladen
        self.supported_languages = ["de", "en", "fr"]
        self.translations_path = Path(__file__).parent.parent / "config" / "translations"
        # Kein _load_translations() mehr beim Init - Lazy Loading!

    def _get_translations(self):
        """Lazy Loading für Translations - wird beim ersten Zugriff geladen"""
        if self.translations is None:
            self._load_translations()
        return self.translations

    def _load_translations(self):
        """
        Load translation files - Lazy Loading beim ersten Zugriff

        Strategie:
        1. Versuche YAML-Files aus config/translations/ zu laden
        2. Fallback zu inline translations (für Entwicklung/Tests)

        NON-BLOCKING: Diese Methode wird nur beim ersten translate() Aufruf aufgerufen
        """
        try:
            # Versuche YAML-Files zu laden (wenn vorhanden)
            if self.translations_path.exists():
                logger.debug(f"📁 Loading translations from: {self.translations_path}")
                loaded_translations = self._load_yaml_translations()
                if loaded_translations:
                    self.translations = loaded_translations
                    logger.info(f"✅ Translations loaded from YAML files: {list(self.translations.keys())}")
                    return

            # Fallback: Inline translations (wie bisher)
            logger.info("📋 Using inline translations (YAML files not found)")
            self.translations = {
                "de": {
                    "dashboard": {
                        "title": "Modellfabrik Dashboard",
                        "subtitle": "ORBIS Modellfabrik (OMF)",
                        "welcome": "Willkommen im OMF2 Dashboard",
                    },
                    "roles": {
                        "admin": "Administrator",
                        "supervisor": "Supervisor",
                        "operator": "Operator",
                    },
                    "tabs": {
                        "ccu_dashboard": "Übersicht",
                        "ccu_overview": "Übersicht",
                        "ccu_orders": "Aufträge",
                        "ccu_process": "Prozess",
                        "production_plan": "Produktionsplan",
                        "production_monitoring": "Produktionsüberwachung",
                        "ccu_configuration": "CCU Konfiguration",
                        "factory_configuration": "Fabrik-Konfiguration",
                        "parameter_configuration": "Parameter-Konfiguration",
                        "ccu_modules": "CCU Module",
                        "nodered_overview": "Node-RED Übersicht",
                        "nodered_processes": "Node-RED Prozesse",
                        "message_center": "Nachrichten-Zentrum",
                        "generic_steering": "Fabrik-Steuerung",
                        "system_logs": "System-Logs",
                        "admin_settings": "Admin-Einstellungen",
                    },
                    "common": {
                        "connect": "Verbinden",
                        "disconnect": "Trennen",
                        "start": "Starten",
                        "stop": "Stoppen",
                        "status": "Status",
                        "error": "Fehler",
                        "success": "Erfolgreich",
                        "loading": "Wird geladen...",
                        "refresh": "Aktualisieren",
                    },
                    "ccu_overview": {
                        "labels": {
                            "unprocessed_svg": "UNPROCESSED SVG",
                            "missing_workpieces": "Fehlende Werkstücke",
                        },
                        "status": {
                            "stock_complete": "Bestand vollständig",
                        },
                        "errors": {
                            "palett_not_found": "palett.svg nicht gefunden!",
                        },
                    },
                    "ccu_orders": {
                        "labels": {
                            "step": "Schritt {index}:",
                        },
                        "info": {
                            "active_module": "Aktives Modul:",
                            "order_completed_no_shopfloor": "Auftrag abgeschlossen – kein aktiver Shopfloor",
                            "fts_navigation_active": "FTS Navigation aktiv:",
                        },
                        "status": {
                            "all_production_steps_completed": "Alle Produktionsschritte abgeschlossen",
                            "all_storage_steps_completed": "Alle Lager-Schritte abgeschlossen",
                            "completed": "Abgeschlossen",
                        },
                    },
                },
                "en": {
                    "dashboard": {
                        "title": "Model Factory Dashboard",
                        "subtitle": "ORBIS Model Factory (OMF)",
                        "welcome": "Welcome to OMF2 Dashboard",
                    },
                    "roles": {
                        "admin": "Administrator",
                        "supervisor": "Supervisor",
                        "operator": "Operator",
                    },
                    "tabs": {
                        "ccu_dashboard": "Overview",
                        "ccu_overview": "Overview",
                        "ccu_orders": "Orders",
                        "ccu_process": "Process",
                        "production_plan": "Production Plan",
                        "production_monitoring": "Production Monitoring",
                        "ccu_configuration": "CCU Configuration",
                        "factory_configuration": "Factory Configuration",
                        "parameter_configuration": "Parameter Configuration",
                        "ccu_modules": "CCU Modules",
                        "nodered_overview": "Node-RED Overview",
                        "nodered_processes": "Node-RED Processes",
                        "message_center": "Message Center",
                        "generic_steering": "Generic Steering",
                        "system_logs": "System Logs",
                        "admin_settings": "Admin Settings",
                    },
                    "common": {
                        "connect": "Connect",
                        "disconnect": "Disconnect",
                        "start": "Start",
                        "stop": "Stop",
                        "status": "Status",
                        "error": "Error",
                        "success": "Success",
                        "loading": "Loading...",
                        "refresh": "Refresh",
                    },
                    "ccu_overview": {
                        "labels": {
                            "unprocessed_svg": "Unprocessed SVG",
                            "missing_workpieces": "Missing workpieces",
                        },
                        "status": {
                            "stock_complete": "Stock complete",
                        },
                        "errors": {
                            "palett_not_found": "palett.svg not found!",
                        },
                    },
                    "ccu_orders": {
                        "labels": {
                            "step": "Step {index}:",
                        },
                        "info": {
                            "active_module": "Active Module:",
                            "order_completed_no_shopfloor": "Order completed - no active shopfloor",
                            "fts_navigation_active": "FTS navigation active:",
                        },
                        "status": {
                            "all_production_steps_completed": "All production steps completed",
                            "all_storage_steps_completed": "All storage steps completed",
                            "completed": "Completed",
                        },
                    },
                },
                "fr": {
                    "dashboard": {
                        "title": "Tableau de bord de l’usine modèle",
                        "subtitle": "Usine Modèle ORBIS (OMF)",
                        "welcome": "Bienvenue au tableau de bord OMF2",
                    },
                    "roles": {
                        "admin": "Administrateur",
                        "supervisor": "Superviseur",
                        "operator": "Opérateur",
                    },
                    "tabs": {
                        "ccu_dashboard": "Aperçu",
                        "ccu_overview": "Aperçu",
                        "ccu_orders": "Commandes",
                        "ccu_process": "Processus",
                        "production_plan": "Plan de Production",
                        "production_monitoring": "Surveillance de Production",
                        "ccu_configuration": "Configuration CCU",
                        "factory_configuration": "Configuration Usine",
                        "parameter_configuration": "Configuration Paramètres",
                        "ccu_modules": "Modules CCU",
                        "nodered_overview": "Aperçu Node-RED",
                        "nodered_processes": "Processus Node-RED",
                        "message_center": "Centre de Messages",
                        "generic_steering": "Contrôle Usine",
                        "system_logs": "Journaux Système",
                        "admin_settings": "Paramètres Admin",
                    },
                    "common": {
                        "connect": "Connecter",
                        "disconnect": "Déconnecter",
                        "start": "Démarrer",
                        "stop": "Arrêter",
                        "status": "Statut",
                        "error": "Erreur",
                        "success": "Succès",
                        "loading": "Chargement...",
                        "refresh": "Actualiser",
                    },
                    "ccu_overview": {
                        "labels": {
                            "unprocessed_svg": "SVG non traité",
                            "missing_workpieces": "Pièces manquantes",
                        },
                        "status": {
                            "stock_complete": "Stock complet",
                        },
                        "errors": {
                            "palett_not_found": "palett.svg introuvable !",
                        },
                    },
                    "ccu_orders": {
                        "labels": {
                            "step": "Étape {index} :",
                        },
                        "info": {
                            "active_module": "Module actif :",
                            "order_completed_no_shopfloor": "Commande terminée - aucun shopfloor actif",
                            "fts_navigation_active": "Navigation FTS active :",
                        },
                        "status": {
                            "all_production_steps_completed": "Toutes les étapes de production terminées",
                            "all_storage_steps_completed": "Toutes les étapes de stockage terminées",
                            "completed": "Terminé",
                        },
                    },
                },
            }
            logger.info(f"✅ Translations loaded for languages: {list(self.translations.keys())}")
        except Exception as e:
            logger.error(f"❌ Failed to load translations: {e}")
            # Fallback to English-only
            self.translations = {
                "en": {"dashboard": {"title": "OMF2 Dashboard"}, "common": {"error": "Error", "loading": "Loading..."}}
            }

    def set_language(self, language: str):
        """
        Set the current language

        Args:
            language: Language code (de, en, fr)

        NOTE: Verwendet Session State wenn verfügbar für Persistenz
        """
        if language in self.supported_languages:
            if self.session_state is not None:
                # Session State verfügbar - speichere dort
                self.session_state["i18n_current_language"] = language
                logger.info(f"🌐 Language set to: {language} (Session State)")
            else:
                # Fallback: Nur lokal speichern
                self.current_language = language
                logger.info(f"🌐 Language set to: {language} (Local)")
            # Invalidate cached translations to pick up new/updated YAML and ensure correct language
            self.translations = None
        else:
            logger.warning(f"⚠️ Unsupported language: {language}")

    def get_current_language(self) -> str:
        """
        Get the current language

        Returns:
            Current language code (de, en, fr)

        NOTE: Liest aus Session State wenn verfügbar, sonst Fallback zu 'de'
        """
        if self.session_state is not None and "i18n_current_language" in self.session_state:
            return self.session_state["i18n_current_language"]
        elif hasattr(self, "current_language"):
            return self.current_language
        else:
            return "de"  # Default

    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return self.supported_languages

    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Get translated string for the given key with optional string interpolation

        Args:
            key: Translation key in dot notation (e.g., 'dashboard.title')
            language: Language code (uses current language if not specified)
            **kwargs: Optional variables for string interpolation (e.g., workpiece_type="BLUE")

        Returns:
            Translated string or the key if translation not found

        Examples:
            i18n.translate('ccu.overview.stock', count=5)
            → "Bestand: 5" (if translation is "Bestand: {count}")
        """
        if language is None:
            language = self.get_current_language()

        # Handle fallback to English if language not available
        if language not in self._get_translations():
            language = "en"

        # Direct key lookup (FLAT STRUCTURE: common.buttons.order)
        try:
            translations = self._get_translations()[language]
            value = translations[key]

            # String interpolation if kwargs provided
            if kwargs:
                return str(value).format(**kwargs)

            return str(value)
        except (KeyError, TypeError):
            logger.warning(f"⚠️ Translation not found for key: {key} (language: {language})")
            return key  # Return key as fallback
        except ValueError as e:
            logger.error(f"❌ String interpolation error for key: {key} - {e}")
            return key  # Return key as fallback

    def t(self, key: str, **kwargs) -> str:
        """
        Shorthand for translate() - for better developer experience

        Args:
            key: Translation key in dot notation
            **kwargs: Optional variables for string interpolation

        Returns:
            Translated string

        Examples:
            i18n.t('common.buttons.send')
            i18n.t('ccu.overview.order_sent', workpiece_type='BLUE')
        """
        return self.translate(key, **kwargs)

    def get_language_display_name(self, language: str) -> str:
        """Get display name for language"""
        display_names = {"de": "Deutsch", "en": "English", "fr": "Français"}
        return display_names.get(language, language)

    def _load_yaml_translations(self) -> Optional[Dict[str, Any]]:
        """
        Load translations from YAML files (NEW STRUCTURE: de/, en/, fr/ folders)

        Struktur:
        config/translations/
        ├── de/
        │   ├── common.yml
        │   └── ccu_overview.yml
        ├── en/
        │   ├── common.yml
        │   └── ccu_overview.yml
        └── fr/
            ├── common.yml
            └── ccu_overview.yml

        Returns:
            Dict mit allen Translations oder None bei Fehler
        """
        try:
            translations = {"de": {}, "en": {}, "fr": {}}

            # Für jede Sprache: Lade alle YAML-Files im Sprach-Ordner
            for lang in ["de", "en", "fr"]:
                lang_path = self.translations_path / lang

                if not lang_path.exists():
                    logger.warning(f"⚠️ Language folder not found: {lang_path}")
                    continue

                # Alle YAML-Files im Sprach-Ordner
                yaml_files = list(lang_path.glob("*.yml"))

                if not yaml_files:
                    logger.debug(f"No YAML files found in {lang_path}")
                    continue

                # Jedes YAML-File laden und mergen
                for yaml_file in yaml_files:
                    try:
                        with open(yaml_file, encoding="utf-8") as f:
                            content = yaml.safe_load(f)

                        if not content:
                            continue

                        # Deep merge in language dict
                        self._deep_merge(translations[lang], content)

                        logger.debug(f"✅ Loaded: {lang}/{yaml_file.name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load {yaml_file}: {e}")

            # Prüfe ob mindestens eine Sprache Daten hat
            if any(translations.values()):
                logger.info(f"✅ Translations loaded from YAML files: {list(translations.keys())}")
                return translations
            else:
                logger.warning("⚠️ No translations loaded from YAML files")
                return None

        except Exception as e:
            logger.error(f"❌ Failed to load YAML translations: {e}")
            return None

    def _deep_merge(self, target: Dict, source: Dict) -> None:
        """
        Deep merge source dict into target dict (mutates target)

        Args:
            target: Target dictionary (will be modified)
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Rekursiv mergen für nested dicts
                self._deep_merge(target[key], value)
            else:
                # Einfach überschreiben
                target[key] = value

    def get_role_name(self, role: str, language: Optional[str] = None) -> str:
        """Get translated role name"""
        return self.translate(f"roles.{role}", language)

    def get_tab_name(self, tab: str, language: Optional[str] = None) -> str:
        """Get translated tab name"""
        return self.translate(f"tabs.{tab}", language)
