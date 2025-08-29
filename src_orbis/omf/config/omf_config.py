"""
OMF Dashboard Konfiguration
Version: 3.0.0
"""

from pathlib import Path

import yaml

# Basis-Pfade
BASE_DIR = Path(__file__).parent.parent.parent.parent
OMF_DATA_DIR = BASE_DIR / "omf-data"
CONFIG_DIR = BASE_DIR / "src_orbis" / "omf" / "config"

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
        "overview": "Übersicht",
        "orders": "Aufträge",
        "message_monitor": "Nachrichten-Monitor",
        "message_controls": "Nachrichten-Steuerung",
        "settings": "Einstellungen",
        "module_status": "Modul-Status",
        "order_management": "Auftragsverwaltung",
        "ongoing_orders": "Laufende Aufträge",
        "dashboard_settings": "Dashboard-Einstellungen",
        "module_config": "Modul-Konfiguration",
        "nfc_config": "NFC-Konfiguration",
        "topic_config": "Topic-Konfiguration",
        "messages_templates": "Nachrichten-Templates",
    },
    "en": {
        "overview": "Overview",
        "orders": "Orders",
        "message_monitor": "Message Monitor",
        "message_controls": "Message Controls",
        "settings": "Settings",
        "module_status": "Module Status",
        "order_management": "Order Management",
        "ongoing_orders": "Ongoing Orders",
        "dashboard_settings": "Dashboard Settings",
        "module_config": "Module Configuration",
        "nfc_config": "NFC Configuration",
        "topic_config": "Topic Configuration",
        "messages_templates": "Message Templates",
    },
}


class OMFConfig:
    """OMF Dashboard Konfigurationsklasse"""

    def __init__(self, config_file=None):
        self.config_file = config_file or CONFIG_DIR / "omf_config.yaml"
        self.config = self._load_config()

    def _load_config(self):
        """Lädt die Konfiguration aus Datei oder erstellt Standard"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
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
                yaml.dump(
                    self.config, f, default_flow_style=False, allow_unicode=True
                )
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
config = OMFConfig()
