"""
Settings Manager für Session Manager
Zentrale Verwaltung aller Einstellungen für die verschiedenen Tabs
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """Zentrale Verwaltung aller Session Manager Einstellungen"""

    def __init__(self, settings_file: str = "session_manager_settings.json"):
        # Moderne Paket-Struktur - State of the Art
        if not Path(settings_file).is_absolute():
            # Paket-relative Pfade verwenden
            package_dir = Path(__file__).parent.parent
            self.settings_file = package_dir / settings_file
        else:
            self.settings_file = Path(settings_file)
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Lädt die Einstellungen aus der JSON-Datei"""
        logger.debug(f"Lade Einstellungen aus: {self.settings_file}")
        if self.settings_file.exists():
            try:
                with open(self.settings_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Einstellungen: {e}")
                return self._get_default_settings()
        else:
            return self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Gibt die Standard-Einstellungen zurück"""
        return {
            "session_analysis": {
                "session_directory": "data/osf-data/sessions",
                "prefilter_topics": [
                    "/j1/txt/1/i/cam",  # Kamera-Daten
                    "/j1/txt/1/i/bme",  # BME680-Sensor-Daten
                    "/j1/txt/1/c/bme680",  # BME680-Sensor-Daten (andere Schreibweise)
                    "/j1/txt/1/c/cam",  # Kamera-Daten (andere Schreibweise)
                    "/j1/txt/1/c/ldr",  # LDR-Sensor-Daten
                ],
                "show_all_topics_by_default": False,
                "timeline_height": 600,
                "max_topics_display": 50,
            },
            "replay_station": {
                "session_directory": "data/osf-data/sessions",
                "mqtt_broker": {"host": "localhost", "port": 1883, "qos": 1, "timeout": 5},
                "replay": {"default_speed": 1.0, "auto_play": False, "loop_playback": False},
            },
            "session_recorder": {
                "session_directory": "data/osf-data/sessions",
                "mqtt_broker": {"host": "localhost", "port": 1883, "qos": 1, "timeout": 5},
                "recording": {
                    "auto_save": True,
                    "save_interval": 300,  # 5 Minuten
                    "max_file_size": 100,  # MB
                    # DR-25: "none" = alle Topics; "analysis" = ohne Arduino/BME680/Kamera/LDR (TXT)
                    "recording_exclusion_preset": "none",
                },
            },
            "topic_recorder": {
                "topics_directory": "data/osf-data/topics",
                "mqtt_broker": {"host": "localhost", "port": 1883, "qos": 1, "timeout": 5},
                "periodic_topics": [
                    "ccu/pairing/state",
                    "/j1/txt/1/i/cam",
                    "module/v1/ff/SVR4H73275/instantAction",
                ],
            },
            "template_analysis": {"show_payload_preview": True, "max_payload_length": 200},
        }

    def save_settings(self):
        """Speichert die Einstellungen in die JSON-Datei"""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.debug(f"Einstellungen gespeichert: {self.settings_file}")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Einstellungen: {e}")

    def get_setting(self, section: str, key: str, default=None):
        """Holt eine spezifische Einstellung"""
        return self.settings.get(section, {}).get(key, default)

    def set_setting(self, section: str, key: str, value: Any):
        """Setzt eine spezifische Einstellung"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save_settings()

    def get_section(self, section: str) -> Dict[str, Any]:
        """Holt eine komplette Sektion"""
        return self.settings.get(section, {})

    def set_section(self, section: str, settings: Dict[str, Any]):
        """Setzt eine komplette Sektion"""
        self.settings[section] = settings
        self.save_settings()

    def get_prefilter_topics(self) -> List[str]:
        """Holt die Vorfilter-Topics für Session Analysis"""
        return self.get_setting("session_analysis", "prefilter_topics", [])

    def set_prefilter_topics(self, topics: List[str]):
        """Setzt die Vorfilter-Topics für Session Analysis"""
        self.set_setting("session_analysis", "prefilter_topics", topics)

    def add_prefilter_topic(self, topic: str):
        """Fügt ein Topic zum Vorfilter hinzu"""
        topics = self.get_prefilter_topics()
        if topic not in topics:
            topics.append(topic)
            self.set_prefilter_topics(topics)

    def remove_prefilter_topic(self, topic: str):
        """Entfernt ein Topic vom Vorfilter"""
        topics = self.get_prefilter_topics()
        if topic in topics:
            topics.remove(topic)
            self.set_prefilter_topics(topics)

    def toggle_prefilter_topic(self, topic: str):
        """Schaltet ein Topic im Vorfilter ein/aus"""
        topics = self.get_prefilter_topics()
        if topic in topics:
            self.remove_prefilter_topic(topic)
        else:
            self.add_prefilter_topic(topic)

    def is_prefilter_topic_active(self, topic: str) -> bool:
        """Prüft ob ein Topic im Vorfilter aktiv ist"""
        return topic in self.get_prefilter_topics()

    def get_mqtt_broker_settings(self) -> Dict[str, Any]:
        """Gibt die MQTT Broker Einstellungen zurück"""
        return self.settings.get("replay_station", {}).get(
            "mqtt_broker", {"host": "localhost", "port": 1883, "qos": 1, "timeout": 5}
        )

    def update_mqtt_broker_settings(self, host: str, port: int, qos: int, timeout: int):
        """Aktualisiert die MQTT Broker Einstellungen"""
        if "replay_station" not in self.settings:
            self.settings["replay_station"] = {}

        self.settings["replay_station"]["mqtt_broker"] = {"host": host, "port": port, "qos": qos, "timeout": timeout}
        self.save_settings()

    def get_session_directory(self, section: str = "replay_station") -> str:
        """Gibt das Session-Verzeichnis zurück"""
        if section == "session_analysis":
            directory = self.settings.get("session_analysis", {}).get("session_directory", "data/osf-data/sessions")
        else:
            directory = self.settings.get("replay_station", {}).get("session_directory", "data/osf-data/sessions")
        logger.debug(f"🔍 Settings: get_session_directory({section}) = {directory}")
        return directory

    def update_session_directory(self, directory: str):
        """Aktualisiert das Session-Verzeichnis"""
        if "replay_station" not in self.settings:
            self.settings["replay_station"] = {}

        self.settings["replay_station"]["session_directory"] = directory
        self.save_settings()

    def get_session_recorder_settings(self) -> Dict[str, Any]:
        """Gibt die Session Recorder Einstellungen zurück"""
        return self.settings.get("session_recorder", {})

    def get_session_recorder_directory(self) -> str:
        """Gibt das Session-Verzeichnis für Recorder zurück"""
        return self.settings.get("session_recorder", {}).get("session_directory", "data/osf-data/sessions")

    def get_session_recorder_mqtt_settings(self) -> Dict[str, Any]:
        """Gibt die MQTT Broker Einstellungen für Recorder zurück"""
        return self.settings.get("session_recorder", {}).get(
            "mqtt_broker", {"host": "localhost", "port": 1883, "qos": 1, "timeout": 5, "username": "", "password": ""}
        )

    def update_session_recorder_directory(self, directory: str):
        """Aktualisiert das Session-Verzeichnis für Recorder"""
        if "session_recorder" not in self.settings:
            self.settings["session_recorder"] = {}

        self.settings["session_recorder"]["session_directory"] = directory
        self.save_settings()

    def get_session_recorder_recording_exclusion_preset(self) -> str:
        """Preset für Topic-Ausschluss beim Record (DR-25): none | analysis."""
        rec = self.get_setting("session_recorder", "recording", {})
        preset = rec.get("recording_exclusion_preset", "none")
        return preset if preset in ("none", "analysis") else "none"

    def set_session_recorder_recording_exclusion_preset(self, preset: str) -> None:
        """Persistiert recording_exclusion_preset unter session_recorder.recording."""
        if preset not in ("none", "analysis"):
            preset = "none"
        rec = dict(self.get_setting("session_recorder", "recording", {}))
        rec["recording_exclusion_preset"] = preset
        self.set_setting("session_recorder", "recording", rec)

    def update_session_recorder_mqtt_settings(
        self, host: str, port: int, qos: int, timeout: int, username: str = "", password: str = ""
    ):
        """Aktualisiert die MQTT Broker Einstellungen für Recorder"""
        if "session_recorder" not in self.settings:
            self.settings["session_recorder"] = {}

        self.settings["session_recorder"]["mqtt_broker"] = {
            "host": host,
            "port": port,
            "qos": qos,
            "timeout": timeout,
            "username": username,
            "password": password,
        }
        self.save_settings()

    def get_topic_recorder_mqtt_settings(self) -> Dict[str, Any]:
        """Gibt die MQTT Broker Einstellungen für Topic Recorder zurück"""
        return self.settings.get("topic_recorder", {}).get(
            "mqtt_broker", {"host": "localhost", "port": 1883, "qos": 1, "timeout": 5, "username": "", "password": ""}
        )

    def get_topic_recorder_directory(self) -> str:
        """Gibt das Topics-Verzeichnis für Topic Recorder zurück"""
        return self.settings.get("topic_recorder", {}).get("topics_directory", "data/osf-data/topics")

    def update_topic_recorder_mqtt_settings(
        self, host: str, port: int, qos: int, timeout: int, username: str = "", password: str = ""
    ):
        """Aktualisiert die MQTT Broker Einstellungen für Topic Recorder"""
        if "topic_recorder" not in self.settings:
            self.settings["topic_recorder"] = {}

        self.settings["topic_recorder"]["mqtt_broker"] = {
            "host": host,
            "port": port,
            "qos": qos,
            "timeout": timeout,
            "username": username,
            "password": password,
        }
        self.save_settings()

    def update_topic_recorder_directory(self, directory: str):
        """Aktualisiert das Topics-Verzeichnis für Topic Recorder"""
        if "topic_recorder" not in self.settings:
            self.settings["topic_recorder"] = {}

        self.settings["topic_recorder"]["topics_directory"] = directory
        self.save_settings()

    def get_topic_recorder_periodic_topics(self) -> list:
        """Gibt die Liste der manuell konfigurierten periodischen Topics zurück"""
        return self.settings.get("topic_recorder", {}).get("periodic_topics", [])

    def update_topic_recorder_periodic_topics(self, topics: list):
        """Aktualisiert die Liste der periodischen Topics"""
        if "topic_recorder" not in self.settings:
            self.settings["topic_recorder"] = {}

        self.settings["topic_recorder"]["periodic_topics"] = topics
        self.save_settings()

    def add_topic_recorder_periodic_topic(self, topic: str):
        """Fügt ein Topic zur Liste der periodischen Topics hinzu"""
        topics = self.get_topic_recorder_periodic_topics()
        if topic not in topics:
            topics.append(topic)
            self.update_topic_recorder_periodic_topics(topics)

    def remove_topic_recorder_periodic_topic(self, topic: str):
        """Entfernt ein Topic aus der Liste der periodischen Topics"""
        topics = self.get_topic_recorder_periodic_topics()
        if topic in topics:
            topics.remove(topic)
            self.update_topic_recorder_periodic_topics(topics)

    def reset_to_defaults(self):
        """Setzt alle Einstellungen auf Standard zurück"""
        self.settings = self._get_default_settings()
        self.save_settings()
