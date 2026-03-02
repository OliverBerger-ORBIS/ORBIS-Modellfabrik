"""
Session Recorder Komponente
Einfache 1:1 Aufnahme von MQTT-Nachrichten
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from ..utils.logging_config import get_logger
from ..utils.path_constants import PROJECT_ROOT
from ..utils.ui_refresh import RerunController

logger = get_logger("omf.helper_apps.session_manager.components.session_recorder")

# Session Manager Logging-System verwenden (wie ursprünglich)
# logger = logging.getLogger("session_manager.session_recorder")  # Duplikat entfernt


# Thread-sichere Nachrichten-Sammlung
class ThreadSafeMessageBuffer:
    def __init__(self):
        self._messages = []
        self._lock = threading.Lock()

    def add_message(self, message: Dict[str, Any]):
        with self._lock:
            self._messages.append(message)

    def get_messages(self) -> List[Dict[str, Any]]:
        with self._lock:
            return self._messages.copy()

    def clear(self):
        with self._lock:
            self._messages.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._messages)


# Globale Nachrichten-Sammlung (thread-sicher)
message_buffer = ThreadSafeMessageBuffer()


def show_session_recorder():
    """Session Recorder Tab - KISS Design"""

    logger.info("🔴 Session Recorder Tab geladen")

    # RerunController initialisieren
    rerun_controller = RerunController()

    st.header("🔴 Session Recorder")
    st.markdown("Einfache 1:1 Aufnahme von MQTT-Nachrichten - **Konfiguration in ⚙️ Einstellungen**")

    # Konfiguration aus Settings laden
    from .settings_manager import SettingsManager

    settings_manager = SettingsManager()
    mqtt_settings = settings_manager.get_session_recorder_mqtt_settings()
    session_directory = settings_manager.get_session_recorder_directory()

    # Tab-spezifische Session State initialisieren (vollständig unabhängig)
    if "session_recorder" not in st.session_state:
        st.session_state.session_recorder = {
            "connected": False,
            "recording": False,
            "session_name": "",
            "start_time": None,
            "mqtt_client": None,
        }

    # Status anzeigen
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔌 MQTT Verbindung")
        st.info(f"**Broker:** {mqtt_settings['host']}:{mqtt_settings['port']}")
        st.info(f"**QoS:** {mqtt_settings['qos']} | **Timeout:** {mqtt_settings['timeout']}s")

        # Authentifizierung anzeigen
        if mqtt_settings.get("username"):
            st.info(f"**Auth:** {mqtt_settings['username']} (authentifiziert)")
        else:
            st.info("**Auth:** Keine Authentifizierung")

        if st.session_state.session_recorder["connected"]:
            st.success("✅ Verbunden")
        else:
            st.error("❌ Nicht verbunden")

    with col2:
        st.subheader("📁 Konfiguration")
        st.info(f"**Session-Verzeichnis:** `{session_directory}`")
        st.info("**Format:** log (JSON-Zeilen)")
        st.markdown("**Einstellungen** können hier konfiguriert werden")
        st.info("💡 Recording-Einstellungen werden automatisch geladen")

    st.markdown("---")

    # Session-Name eingeben
    st.subheader("📝 Session-Name")
    session_name = st.text_input(
        "Session-Name eingeben",
        value=st.session_state.session_recorder["session_name"],
        placeholder="z.B. auftrag-rot-R1",
        help="Name für die aufzunehmende Session",
    )

    if session_name:
        st.session_state.session_recorder["session_name"] = session_name
        st.success(f"✅ Session-Name gesetzt: {session_name}")

    st.markdown("---")

    # Verbindungs-Controls
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔌 Broker Verbinden", disabled=st.session_state.session_recorder["connected"]):
            if connect_to_broker(mqtt_settings):
                st.session_state.session_recorder["connected"] = True
                st.success("✅ MQTT verbunden!")
                rerun_controller.request_rerun()
            else:
                st.error("❌ Verbindung fehlgeschlagen!")

    with col2:
        if st.button("🔌 Broker Trennen", disabled=not st.session_state.session_recorder["connected"]):
            disconnect_from_broker()
            st.session_state.session_recorder["connected"] = False
            st.success("✅ MQTT getrennt!")
            rerun_controller.request_rerun()

    st.markdown("---")

    # Recording-Controls
    st.subheader("🔴 Aufnahme")

    if not st.session_state.session_recorder["connected"]:
        st.warning("⚠️ Bitte zuerst MQTT Broker verbinden")
    elif not st.session_state.session_recorder["session_name"]:
        st.warning("⚠️ Bitte Session-Name eingeben")
    else:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("▶️ Aufnahme Starten", disabled=st.session_state.session_recorder["recording"], type="primary"):
                start_recording()
                st.session_state.session_recorder["recording"] = True
                st.session_state.session_recorder["start_time"] = datetime.now()
                st.success("🔴 Aufnahme gestartet!")
                rerun_controller.request_rerun()

        with col2:
            if st.button(
                "⏹️ Aufnahme Beenden", disabled=not st.session_state.session_recorder["recording"], type="secondary"
            ):
                stop_recording()
                st.session_state.session_recorder["recording"] = False
                st.session_state.session_recorder["start_time"] = None
                st.success("⏹️ Aufnahme beendet und gespeichert!")
                rerun_controller.request_rerun()

    # Status anzeigen
    if st.session_state.session_recorder["recording"]:
        st.markdown("---")
        st.subheader("📊 Aufnahme-Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            message_count = message_buffer.count()
            st.metric("Nachrichten", message_count, delta=None)

        with col2:
            if st.session_state.session_recorder["start_time"]:
                duration = datetime.now() - st.session_state.session_recorder["start_time"]
                minutes, seconds = divmod(duration.seconds, 60)
                duration_str = f"{minutes:02d}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                st.metric("Dauer", duration_str)

        with col3:
            st.metric("Status", "🔴 Aufnahme läuft")

        # Letzte Nachrichten anzeigen
        messages = message_buffer.get_messages()
        if messages:
            st.markdown("**Letzte Nachrichten:**")
            for msg in messages[-5:]:  # Letzte 5 Nachrichten
                st.code(f"{msg['topic']}: {msg['payload'][:100]}...")

        # Manueller Refresh-Button
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("🔄 Aktualisieren", key="refresh_status"):
                rerun_controller.request_rerun()

        with col2:
            if st.button("📊 Status prüfen", key="check_status"):
                st.info(f"📨 Aktuelle Nachrichten: {message_buffer.count()}")
                st.info(f"⏱️ Aufnahme läuft seit: {st.session_state.session_recorder['start_time']}")

        with col3:
            st.info("💡 **Tipp:** Klicke 'Aktualisieren' um den Status zu aktualisieren")


def connect_to_broker(mqtt_settings: Dict[str, Any]) -> bool:
    """Verbindet zum MQTT Broker"""
    try:
        import paho.mqtt.client as mqtt

        # MQTT Client erstellen
        mqtt_client = mqtt.Client(client_id="session_manager_session_recorder")

        # Callback-Funktionen setzen
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message_received

        # Username/Password setzen falls vorhanden
        if mqtt_settings.get("username") and mqtt_settings.get("password"):
            mqtt_client.username_pw_set(mqtt_settings["username"], mqtt_settings["password"])
            logger.info(f"🔐 MQTT Authentifizierung: {mqtt_settings['username']}")

        # Verbinden
        mqtt_client.connect(mqtt_settings["host"], mqtt_settings["port"], mqtt_settings["timeout"])
        mqtt_client.loop_start()

        # Kurz warten, damit Verbindung etabliert wird
        import time

        time.sleep(0.5)

        # MQTT Client in Session State speichern
        st.session_state.session_recorder["mqtt_client"] = mqtt_client

        logger.debug(f"✅ MQTT verbunden: {mqtt_settings['host']}:{mqtt_settings['port']}")
        return True

    except Exception as e:
        logger.error(f"❌ MQTT Verbindungsfehler: {e}")
        return False


def disconnect_from_broker():
    """Trennt MQTT Verbindung"""
    try:
        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            st.session_state.session_recorder["mqtt_client"] = None
            logger.debug("✅ MQTT getrennt")
    except Exception as e:
        logger.error(f"❌ MQTT Trennung Fehler: {e}")


def on_connect(client, userdata, flags, rc):
    """Callback für MQTT Verbindung"""
    if rc == 0:
        logger.debug("✅ MQTT Broker verbunden")
        # Automatisch alle Topics abonnieren
        client.subscribe("#")
    else:
        logger.error(f"❌ MQTT Verbindung fehlgeschlagen: {rc}")


def start_recording():
    """Startet die Aufnahme"""
    try:
        logger.info("🔴 Session-Aufnahme wird gestartet...")

        # MQTT Client für Aufnahme konfigurieren
        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            # Topics abonnieren (falls sie deabonniert waren)
            mqtt_client.subscribe("#")

            # Session State aktualisieren
            st.session_state.session_recorder["recording"] = True
            st.session_state.session_recorder["message_buffer"].clear()

            logger.info("✅ Session-Aufnahme gestartet - alle Topics abonniert")
        else:
            logger.error("❌ Kein MQTT Client verfügbar für Aufnahme")

    except Exception as e:
        logger.error(f"❌ Fehler beim Starten der Aufnahme: {e}")


def pause_recording():
    """Pausiert die Aufnahme"""
    try:
        logger.info("⏸️ Session-Aufnahme wird pausiert...")

        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            mqtt_client.unsubscribe("#")

            # Session State aktualisieren
            st.session_state.session_recorder["recording"] = False

            logger.info("✅ Session-Aufnahme pausiert - Topics deabonniert")
        else:
            logger.error("❌ Kein MQTT Client verfügbar für Pause")
    except Exception as e:
        logger.error(f"❌ Fehler beim Pausieren der Aufnahme: {e}")


def stop_recording():
    """Beendet die Aufnahme und speichert"""
    try:
        logger.info("⏹️ Session-Aufnahme wird gestoppt...")

        # Aufnahme stoppen
        if st.session_state.session_recorder["mqtt_client"]:
            mqtt_client = st.session_state.session_recorder["mqtt_client"]
            mqtt_client.unsubscribe("#")
            logger.info("📡 MQTT Topics deabonniert")

        # Session speichern
        message_count = message_buffer.count()
        if message_count > 0:
            logger.info(f"💾 Session wird gespeichert ({message_count} Messages)...")
            save_session()
            message_buffer.clear()
            st.session_state.session_recorder["session_name"] = ""
            st.session_state.session_recorder["start_time"] = None
            logger.info("✅ Session erfolgreich gespeichert")
        else:
            logger.warning("⚠️ Keine Messages zum Speichern vorhanden")

        # Session State aktualisieren
        st.session_state.session_recorder["recording"] = False
        logger.info("✅ Session-Aufnahme beendet")

    except Exception as e:
        logger.error(f"❌ Fehler beim Stoppen der Aufnahme: {e}")


def on_message_received(client, userdata, msg):
    """Callback für empfangene MQTT-Nachrichten (thread-sicher)"""
    try:
        message = {"topic": msg.topic, "payload": msg.payload.decode("utf-8"), "timestamp": datetime.now().isoformat()}

        # Thread-sichere Nachrichten-Sammlung
        message_buffer.add_message(message)
        logger.debug(f"📨 Nachricht empfangen: {msg.topic} ({len(msg.payload)} bytes)")

    except Exception as e:
        logger.error(f"❌ Nachricht Verarbeitung Fehler: {e}")


def save_session():
    """Speichert die Session-Daten"""
    try:
        logger.info("💾 Session-Datei wird erstellt...")

        from .settings_manager import SettingsManager

        settings_manager = SettingsManager()
        session_directory = settings_manager.get_session_recorder_directory()
        # recording_settings = settings_manager.get_setting("session_recorder", "recording", {})  # Unused for now

        # Session-Verzeichnis erstellen (moderne Paket-Struktur)
        if not Path(session_directory).is_absolute():
            # Paket-relative Pfade verwenden
            # Projekt-Root-relative Pfade für Nutz-Daten verwenden
            project_root = PROJECT_ROOT
            session_dir = project_root / session_directory
        else:
            session_dir = Path(session_directory)
        session_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📁 Session-Verzeichnis: {session_dir}")

        # Dateiname generieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = st.session_state.session_recorder["session_name"]

        # Log-Format speichern (JSON-Zeilen)
        messages = message_buffer.get_messages()
        message_count = len(messages)
        logger.info(f"📊 {message_count} Messages werden gespeichert...")

        log_filename = f"{session_name}_{timestamp}.log"
        log_filepath = session_dir / log_filename
        logger.info(f"📝 Log-Datei wird erstellt: {log_filename}")
        save_log_session(log_filepath, messages)
        logger.info(f"✅ Log Session gespeichert: {log_filepath}")

        st.success(f"💾 Session gespeichert: {log_filename}")
        logger.info(f"🎉 Session erfolgreich gespeichert: {message_count} Messages")

    except Exception as e:
        logger.error(f"❌ Session Speichern Fehler: {e}")
        st.error(f"❌ Fehler beim Speichern: {e}")


def save_log_session(filepath: Path, messages: List[Dict[str, Any]]):
    """Speichert Session als Log-Datei"""
    try:
        logger.debug(f"📝 Log-Datei wird erstellt: {filepath}")

        with open(filepath, "w", encoding="utf-8") as f:
            for msg in messages:
                log_entry = {"topic": msg["topic"], "payload": msg["payload"], "timestamp": msg["timestamp"]}
                f.write(json.dumps(log_entry) + "\n")

        logger.debug(f"✅ Log Session gespeichert: {len(messages)} Messages in {filepath}")

    except Exception as e:
        logger.error(f"❌ Log Speichern Fehler: {e}")
        raise
