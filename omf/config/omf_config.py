from omf.dashboard.tools.path_constants import CONFIG_DIR, PROJECT_ROOT

"""
OMF Dashboard Konfiguration
Version: 3.0.0
"""


import yaml

# Basis-Pfade
BASE_DIR = PROJECT_ROOT
OMF_DATA_DIR = BASE_DIR / "omf-data"
CONFIG_DIR = BASE_DIR / "omf" / "omf" / "config"

# Standard-Konfiguration
DEFAULT_CONFIG = {
    "dashboard": {
        "language": "de",
        "theme": "light",
        "auto_refresh": True,
        "refresh_interval": 5,
    },
    "mqtt": {
        "broker": "localhost",
        "port": 1883,
        "username": "",
        "password": "",
        "topics": {
            "hbw": "aps/hbw/#",
            "vgr": "aps/vgr/#",
            "mpo": "aps/mpo/#",
            "ssc": "aps/ssc/#",
            "dps": "aps/dps/#",
            "drill": "aps/drill/#",
            "mill": "aps/mill/#",
            "aiqs": "aps/aiqs/#",
            "oven": "aps/oven/#",
        },
    },
    "modules": {
        "hbw": {"name": "Hochregallager", "enabled": True},
        "vgr": {"name": "Vakuum Greifer Roboter", "enabled": True},
        "mpo": {"name": "Multi-Processing-Outlet", "enabled": True},
        "ssc": {"name": "Sorting Station Control", "enabled": True},
        "dps": {"name": "Drill Processing Station", "enabled": True},
        "drill": {"name": "Bohrstation", "enabled": True},
        "mill": {"name": "Frässtation", "enabled": True},
        "aiqs": {"name": "AI Quality Station", "enabled": True},
        "oven": {"name": "Ofen", "enabled": True},
    },
    "nfc": {"enabled": True, "reader_type": "default", "timeout": 30},
}

# Übersetzungen
TRANSLATIONS = {
    "de": {
        # Tab-Namen
        "aps_overview": "APS Übersicht",
        "aps_orders": "APS Aufträge", 
        "aps_processes": "APS Prozesse",
        "aps_configuration": "APS Konfiguration",
        "aps_modules": "APS Module",
        "wl_module_control": "WL Modul-Steuerung",
        "wl_system_control": "WL System Control",
        "steering": "Steuerung",
        "message_center": "Nachrichten-Zentrale",
        "logs": "Logs",
        "settings": "Einstellungen",
        
        # Bestehende Übersetzungen
        "overview": "Übersicht",
        "orders": "Aufträge",
        "message_monitor": "Nachrichten-Monitor",
        "message_controls": "Nachrichten-Steuerung",
        "module_status": "Modul-Status",
        "order_management": "Auftragsverwaltung",
        "ongoing_orders": "Laufende Aufträge",
        "dashboard_settings": "Dashboard-Einstellungen",
        "module_config": "Modul-Konfiguration",
        "nfc_config": "NFC-Konfiguration",
        "topic_config": "Topic-Konfiguration",
        "messages_templates": "Nachrichten-Templates",
        
        # UI-Elemente
        "language": "Sprache",
        "user_role": "Benutzerrolle",
        "select_language": "Sprache wählen:",
        "select_role": "Rolle wählen:",
        "tabs_available": "Tabs verfügbar"
    },
    "en": {
        # Tab-Namen
        "aps_overview": "APS Overview",
        "aps_orders": "APS Orders",
        "aps_processes": "APS Processes", 
        "aps_configuration": "APS Configuration",
        "aps_modules": "APS Modules",
        "wl_module_control": "WL Module Control",
        "wl_system_control": "WL System Control",
        "steering": "Steering",
        "message_center": "Message Center",
        "logs": "Logs",
        "settings": "Settings",
        
        # Bestehende Übersetzungen
        "overview": "Overview",
        "orders": "Orders",
        "message_monitor": "Message Monitor",
        "message_controls": "Message Controls",
        "module_status": "Module Status",
        "order_management": "Order Management",
        "ongoing_orders": "Ongoing Orders",
        "dashboard_settings": "Dashboard Settings",
        "module_config": "Module Configuration",
        "nfc_config": "NFC Configuration",
        "topic_config": "Topic Configuration",
        "messages_templates": "Message Templates",
        
        # UI-Elemente
        "language": "Language",
        "user_role": "User Role",
        "select_language": "Select Language:",
        "select_role": "Select Role:",
        "tabs_available": "tabs available"
    },
    "fr": {
        # Tab-Namen
        "aps_overview": "Vue d'ensemble APS",
        "aps_orders": "Commandes APS",
        "aps_processes": "Processus APS",
        "aps_configuration": "Configuration APS", 
        "aps_modules": "Modules APS",
        "wl_module_control": "Contrôle Module WL",
        "wl_system_control": "Contrôle Système WL",
        "steering": "Direction",
        "message_center": "Centre de Messages",
        "logs": "Journaux",
        "settings": "Paramètres",
        
        # Übersetzungen
        "overview": "Vue d'ensemble",
        "orders": "Commandes",
        "message_monitor": "Moniteur de Messages",
        "message_controls": "Contrôles de Messages",
        "module_status": "État des Modules",
        "order_management": "Gestion des Commandes",
        "ongoing_orders": "Commandes en Cours",
        "dashboard_settings": "Paramètres du Tableau de Bord",
        "module_config": "Configuration des Modules",
        "nfc_config": "Configuration NFC",
        "topic_config": "Configuration des Sujets",
        "messages_templates": "Modèles de Messages",
        
        # UI-Elemente
        "language": "Langue",
        "user_role": "Rôle Utilisateur",
        "select_language": "Choisir la langue:",
        "select_role": "Choisir le rôle:",
        "tabs_available": "onglets disponibles"
    },
}


class OmfConfig:
    """OMF Dashboard Konfigurationsklasse"""

    def __init__(self, config_file=None):
        self.config_file = config_file or CONFIG_DIR / "omf_config.yaml"
        self.config = self._load_config()

    def _load_config(self):
        """Lädt die Konfiguration aus Datei oder erstellt Standard"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"⚠️ Konfiguration konnte nicht geladen werden: {e}")
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        """Speichert die aktuelle Konfiguration"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"❌ Konfiguration konnte nicht gespeichert werden: {e}")
            return False

    def get(self, key, default=None):
        """Holt einen Konfigurationswert"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        """Setzt einen Konfigurationswert"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def get_translation(self, key, language=None):
        """Holt eine Übersetzung"""
        lang = language or self.get("dashboard.language", "de")
        return TRANSLATIONS.get(lang, {}).get(key, key)

    def get_module_name(self, module_id, language=None):
        """Holt den Namen eines Moduls"""
        module_config = self.get(f"modules.{module_id}", {})
        return module_config.get("name", module_id.upper())


# Globale Konfigurationsinstanz
config = OmfConfig()
