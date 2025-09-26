from omf.dashboard.tools.path_constants import CONFIG_DIR, PROJECT_ROOT

"""
OMF Dashboard Konfiguration
Version: 3.0.0
"""


import yaml

# Basis-Pfade
BASE_DIR = PROJECT_ROOT
OMF_DATA_DIR = BASE_DIR / "omf-data"
# CONFIG_DIR aus path_constants verwenden - behebt das omf/omf/config Problem
# CONFIG_DIR = BASE_DIR / "omf" / "config"  # Korrigierte Pfad-Struktur

def _load_existing_mqtt_config():
    """Lädt die bestehende MQTT-Konfiguration aus mqtt_config.yml"""
    try:
        mqtt_config_path = CONFIG_DIR / "mqtt_config.yml"
        if mqtt_config_path.exists():
            with open(mqtt_config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                # Mappiere die YAML-Struktur auf Dashboard-Format
                return {
                    "broker": config.get("host", "localhost"),
                    "port": config.get("port", 1883),
                    "username": config.get("username", ""),
                    "password": config.get("password", ""),
                    "client_id": config.get("client_id", "omf_dashboard"),
                    "keepalive": config.get("keepalive", 60),
                    "tls": config.get("tls", False),
                }
    except Exception as e:
        print(f"⚠️ Konnte bestehende MQTT-Konfiguration nicht laden: {e}")
    
    # Fallback zur existierenden config.py
    try:
        from omf.config.config import LIVE_CFG
        return {
            "broker": LIVE_CFG.get("host", "localhost"),
            "port": LIVE_CFG.get("port", 1883),
            "username": LIVE_CFG.get("username", ""),
            "password": LIVE_CFG.get("password", ""),
            "client_id": LIVE_CFG.get("client_id", "omf_dashboard"),
            "keepalive": LIVE_CFG.get("keepalive", 60),
            "tls": LIVE_CFG.get("tls", False),
        }
    except ImportError:
        return {
            "broker": "localhost",
            "port": 1883,
            "username": "",
            "password": "",
            "client_id": "omf_dashboard",
            "keepalive": 60,
            "tls": False,
        }

def _load_existing_modules_config():
    """Lädt die bestehende Modul-Konfiguration aus registry/model/v0/modules.yml"""
    try:
        from omf.tools.module_manager import OmfModuleManager
        module_manager = OmfModuleManager()
        modules_data = module_manager.config.get("modules", [])
        
        # Konvertiere zu Dashboard-kompatiblem Format
        dashboard_modules = {}
        for module in modules_data:
            module_id = module.get("name", "").lower()
            if module_id:
                dashboard_modules[module_id] = {
                    "name": module.get("name_lang_de", module.get("name", module_id)),
                    "enabled": module.get("enabled", True)
                }
        return dashboard_modules
    except Exception as e:
        print(f"⚠️ Konnte bestehende Modul-Konfiguration nicht laden: {e}")
        # Minimaler Fallback
        return {}

def _get_default_config():
    """Lädt die bestehende MQTT-Konfiguration aus mqtt_config.yml"""
    try:
        mqtt_config_path = CONFIG_DIR / "mqtt_config.yml"
        if mqtt_config_path.exists():
            with open(mqtt_config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️ Konnte bestehende MQTT-Konfiguration nicht laden: {e}")
    
    # Fallback zur existierenden config.py
    try:
        from omf.config.config import LIVE_CFG
        return {
            "broker": LIVE_CFG.get("host", "localhost"),
            "port": LIVE_CFG.get("port", 1883),
            "username": LIVE_CFG.get("username", ""),
            "password": LIVE_CFG.get("password", ""),
        }
    except ImportError:
        return {
            "broker": "localhost",
            "port": 1883,
            "username": "",
            "password": "",
        }

def _load_existing_modules_config():
    """Lädt die bestehende Modul-Konfiguration aus registry/model/v0/modules.yml"""
    try:
        from omf.tools.module_manager import OmfModuleManager
        module_manager = OmfModuleManager()
        modules_data = module_manager.config.get("modules", [])
        
        # Konvertiere zu Dashboard-kompatiblem Format
        dashboard_modules = {}
        for module in modules_data:
            module_id = module.get("name", "").lower()
            if module_id:
                dashboard_modules[module_id] = {
                    "name": module.get("name_lang_de", module.get("name", module_id)),
                    "enabled": module.get("enabled", True)
                }
        return dashboard_modules
    except Exception as e:
        print(f"⚠️ Konnte bestehende Modul-Konfiguration nicht laden: {e}")
        # Minimaler Fallback
        return {}

def _get_default_config():
    """Erstellt Standard-Konfiguration - lazy loaded zur Laufzeit"""
    return {
        "dashboard": {
            "language": "de",
            "theme": "light",
            # auto_refresh auf False setzen um Konflikte mit Streamlit st.rerun zu vermeiden
            "auto_refresh": False,  # GEÄNDERT: Verhindert Konflikte mit UI-Refresh-Mechanismus
            "refresh_interval": 5,
        },
        # MQTT-Konfiguration aus bestehender mqtt_config.yml laden
        "mqtt": _load_existing_mqtt_config(),
        # Modul-Konfiguration aus bestehender registry/model/v0/modules.yml laden  
        "modules": _load_existing_modules_config(),
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
                return _get_default_config()  # Verwende lazy-loaded Konfiguration
        except Exception as e:
            print(f"⚠️ Konfiguration konnte nicht geladen werden: {e}")
            return _get_default_config()  # Verwende lazy-loaded Konfiguration

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
