"""
Topic Recorder Komponente
Speichert jedes MQTT-Topic als einzelne Datei mit dem letzten Payload
"""

import re
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Set

import streamlit as st

from ..utils.logging_config import get_logger
from ..utils.path_constants import PROJECT_ROOT
from ..utils.ui_refresh import RerunController

logger = get_logger("omf.helper_apps.session_manager.components.topic_recorder")


class ThreadSafeTopicTracker:
    """Thread-sichere Verwaltung empfangener Topics mit Frequenz-Analyse"""

    def __init__(self):
        self._topics = set()
        self._topic_counts = {}  # Topic -> Anzahl Messages
        self._lock = threading.Lock()

    def add_topic(self, topic: str):
        with self._lock:
            self._topics.add(topic)
            self._topic_counts[topic] = self._topic_counts.get(topic, 0) + 1

    def get_topics(self) -> Set[str]:
        with self._lock:
            return self._topics.copy()

    def get_topic_counts(self) -> Dict[str, int]:
        with self._lock:
            return self._topic_counts.copy()

    def clear(self):
        with self._lock:
            self._topics.clear()
            self._topic_counts.clear()

    def count(self) -> int:
        with self._lock:
            return len(self._topics)


# Globale Topic-Sammlung (thread-sicher)
topic_tracker = ThreadSafeTopicTracker()

# Globale Recording-Konfiguration (thread-sicher, für MQTT-Callback)
class RecordingConfig:
    def __init__(self):
        self._lock = threading.Lock()
        self._mode = None  # None, "analyze", "record"
        self._topics_directory = None
        self._periodic_topics = set()  # Topics die als periodisch erkannt wurden
        self._global_sequence = 0  # Globaler Sequenz-Counter über alle Topics

    def start_analysis(self):
        """Startet Analyse-Phase (keine Speicherung)"""
        with self._lock:
            self._mode = "analyze"

    def start_recording(self, topics_directory: Path, periodic_topics: Set[str]):
        """Startet Recording-Phase mit globaler Sequenznummer"""
        with self._lock:
            self._mode = "record"
            self._topics_directory = topics_directory
            self._periodic_topics = periodic_topics.copy()
            self._global_sequence = 0  # Reset bei neuem Recording

    def stop(self):
        with self._lock:
            self._mode = None

    def get_mode(self) -> str:
        with self._lock:
            return self._mode

    def is_analyzing(self) -> bool:
        with self._lock:
            return self._mode == "analyze"

    def is_recording(self) -> bool:
        with self._lock:
            return self._mode == "record"

    def get_topics_directory(self) -> Path:
        with self._lock:
            return self._topics_directory

    def is_periodic(self, topic: str) -> bool:
        with self._lock:
            return topic in self._periodic_topics

    def get_next_sequence(self) -> int:
        """Gibt nächste globale Sequenznummer zurück (über alle Topics)"""
        with self._lock:
            self._global_sequence += 1
            return self._global_sequence

recording_config = RecordingConfig()


def sanitize_topic_name(topic: str) -> str:
    """
    Konvertiert Topic-Namen in gültige Dateinamen
    Beispiele:
      ccu/order/active -> ccu_order_active
      /j1/txt/1/i/bme680 -> _j1_txt_1_i_bme680
      j1/txt/1/i/bme680 -> j1_txt_1_i_bme680
    """
    # Trailing Slashes entfernen (aber führendes "/" behalten für die Konvertierung)
    topic = topic.rstrip('/')

    # Alle ungültigen Zeichen (inkl. /) durch Underscore ersetzen
    # Erlaubte Zeichen: a-z, A-Z, 0-9, _, -, .
    sanitized = re.sub(r'[^a-zA-Z0-9_\-.]', '_', topic)

    # Mehrfache Underscores durch einen ersetzen
    sanitized = re.sub(r'_+', '_', sanitized)

    return sanitized


def show_topic_recorder():
    """Topic Recorder Tab"""

    logger.info("📂 Topic Recorder Tab geladen")

    # RerunController initialisieren
    rerun_controller = RerunController()

    st.header("📂 Topic Recorder")
    st.markdown(
        "Speichert jedes MQTT-Topic als einzelne Datei - "
        "**Konfiguration in ⚙️ Einstellungen**"
    )

    # Konfiguration aus Settings laden
    from .settings_manager import SettingsManager

    settings_manager = SettingsManager()
    mqtt_settings = settings_manager.get_session_recorder_mqtt_settings()

    # Tab-spezifische Session State initialisieren
    if 'topic_recorder' not in st.session_state:
        st.session_state.topic_recorder = {
            'connected': False,
            'recording': False,
            'analyzing': False,
            'analysis_start_time': None,
            'start_time': None,
            'mqtt_client': None,
            'topics_directory': PROJECT_ROOT / "data/aps-data/topics",
            'recording_name': '',
            'current_recording_dir': None,
            'periodic_topics': set(),  # Erkannte periodische Topics
            'analysis_duration': 60,  # Sekunden für Analyse-Phase
            'frequency_threshold': 60,  # Messages pro MINUTE für "periodisch"
        }

    # Sicherstellen dass Analyse-Phase nicht hängt (falls App neugestartet wurde)
    if st.session_state.topic_recorder.get('analyzing', False):
        if st.session_state.topic_recorder.get('analysis_start_time'):
            elapsed = (datetime.now() - st.session_state.topic_recorder['analysis_start_time']).seconds
            # Wenn Analyse länger als 10 Minuten läuft, zurücksetzen
            if elapsed > 600:
                logger.warning("⚠️ Analyse-Phase hängt - wird zurückgesetzt")
                st.session_state.topic_recorder['analyzing'] = False
                st.session_state.topic_recorder['analysis_start_time'] = None
                recording_config.stop()

    # Prüfe MQTT-Verbindung nach Neustart
    if st.session_state.topic_recorder.get('connected', False):
        if st.session_state.topic_recorder.get('mqtt_client') is None:
            logger.warning("⚠️ MQTT als 'verbunden' markiert, aber Client fehlt - wird zurückgesetzt")
            st.session_state.topic_recorder['connected'] = False

    # Topics-Verzeichnis erstellen
    topics_dir = st.session_state.topic_recorder['topics_directory']
    topics_dir.mkdir(parents=True, exist_ok=True)

    # Status anzeigen
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔌 MQTT Verbindung")
        st.info(f"**Broker:** {mqtt_settings['host']}:{mqtt_settings['port']}")
        st.info(f"**QoS:** {mqtt_settings['qos']} | **Timeout:** {mqtt_settings['timeout']}s")

        # Authentifizierung anzeigen
        if mqtt_settings.get('username'):
            st.info(f"**Auth:** {mqtt_settings['username']} (authentifiziert)")
        else:
            st.info("**Auth:** Keine Authentifizierung")

        if st.session_state.topic_recorder['connected']:
            st.success("✅ Verbunden")
        else:
            st.error("❌ Nicht verbunden")

    with col2:
        st.subheader("📁 Konfiguration")
        st.info(f"**Topics-Verzeichnis:** `{topics_dir.relative_to(PROJECT_ROOT)}`")
        st.info("**Dateiformat:** JSON mit allen MQTT-Metadaten")
        st.info("💡 **Verhalten:** Speichert erste Nachricht pro Topic (valides Test-Beispiel)")

    st.markdown("---")

    # Recording-Name eingeben
    st.subheader("📝 Recording-Name")
    recording_name = st.text_input(
        "Name für dieses Recording:",
        value=st.session_state.topic_recorder['recording_name'],
        placeholder="z.B. rec1, test-session, auftrag-rot",
        help="Name für das Recording-Unterverzeichnis",
        disabled=st.session_state.topic_recorder['connected'] or st.session_state.topic_recorder['recording']
    )

    if recording_name:
        st.session_state.topic_recorder['recording_name'] = recording_name
        # Recording-Verzeichnis setzen
        recording_dir = topics_dir / recording_name
        st.session_state.topic_recorder['current_recording_dir'] = recording_dir
        st.success(f"✅ Recording-Name gesetzt: **{recording_name}**")
        st.info(f"📁 Ziel-Verzeichnis: `{recording_dir.relative_to(PROJECT_ROOT)}`")
    else:
        st.warning("⚠️ Bitte Recording-Name eingeben")

    st.markdown("---")

    # Verbindungs-Controls
    col1, col2, col3 = st.columns(3)

    with col1:
        can_connect = not st.session_state.topic_recorder['connected'] and recording_name
        if st.button("🔌 Broker Verbinden", disabled=not can_connect):
            if connect_to_broker(mqtt_settings):
                st.session_state.topic_recorder['connected'] = True
                # Recording-Verzeichnis erstellen
                recording_dir = st.session_state.topic_recorder['current_recording_dir']
                recording_dir.mkdir(parents=True, exist_ok=True)
                st.success("✅ MQTT verbunden!")
                rerun_controller.request_rerun()
            else:
                st.error("❌ Verbindung fehlgeschlagen!")

    with col2:
        if st.button("🔌 Broker Trennen", disabled=not st.session_state.topic_recorder['connected']):
            disconnect_from_broker()
            st.session_state.topic_recorder['connected'] = False
            st.success("✅ MQTT getrennt!")
            rerun_controller.request_rerun()

    with col3:
        # Neues Recording starten (Disconnect + Reset)
        can_new_recording = st.session_state.topic_recorder['connected'] and not st.session_state.topic_recorder['recording']
        if st.button("🆕 Neues Recording", disabled=not can_new_recording):
            # Disconnect vom Broker
            disconnect_from_broker()
            st.session_state.topic_recorder['connected'] = False
            # Recording-Name und Verzeichnis zurücksetzen
            st.session_state.topic_recorder['recording_name'] = ''
            st.session_state.topic_recorder['current_recording_dir'] = None
            # Topic-Liste leeren
            topic_tracker.clear()
            st.success("✅ Bereit für neues Recording! Bitte neuen Namen eingeben und erneut verbinden.")
            rerun_controller.request_rerun()

    st.markdown("---")

    # Recording Controls (ohne Analyse)
    st.subheader("📂 Topic Recording")

    if not recording_name:
        st.warning("⚠️ Bitte zuerst Recording-Name eingeben")
    elif not st.session_state.topic_recorder['connected']:
        st.warning("⚠️ Bitte zuerst MQTT Broker verbinden")
    elif st.session_state.topic_recorder['recording']:
        # Recording läuft
        st.success("📂 **Recording läuft** mit globalen Sequenznummern")

        if st.button("⏹️ Recording Beenden", type="secondary"):
            stop_recording()
            st.session_state.topic_recorder['recording'] = False
            st.session_state.topic_recorder['start_time'] = None
            st.success("⏹️ Recording beendet!")
            rerun_controller.request_rerun()
    else:
        # Bereit zum Starten
        from .settings_manager import SettingsManager
        settings_manager = SettingsManager()
        manual_periodic = settings_manager.get_topic_recorder_periodic_topics()

        st.info(f"✅ **{len(manual_periodic)} periodische Topics** in Settings konfiguriert")
        st.markdown("**Periodische Topics (nur erste Nachricht):**")
        for topic in manual_periodic:
            st.code(topic, language="text")

        st.markdown("---")
        st.markdown("💡 **Alle anderen Topics** werden mit **globaler Sequenznummer** gespeichert")

        if st.button("▶️ Recording Starten", type="primary", key="start_recording"):
            # Setze leere analyzed_periodic (keine Analyse)
            st.session_state.topic_recorder['periodic_topics'] = set()

            start_recording()
            st.session_state.topic_recorder['recording'] = True
            st.session_state.topic_recorder['start_time'] = datetime.now()
            st.success("📂 Recording gestartet!")
            rerun_controller.request_rerun()

    # Status anzeigen
    if st.session_state.topic_recorder['recording']:
        st.markdown("---")
        st.subheader("📊 Recording-Status")

        col1, col2, col3 = st.columns(3)

        with col1:
            topic_count = topic_tracker.count()
            st.metric("Empfangene Topics", topic_count)

        with col2:
            if st.session_state.topic_recorder['start_time']:
                duration = datetime.now() - st.session_state.topic_recorder['start_time']
                minutes, seconds = divmod(duration.seconds, 60)
                duration_str = f"{minutes:02d}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
                st.metric("Dauer", duration_str)

        with col3:
            st.metric("Status", "📂 Recording läuft")

        # Empfangene Topics anzeigen
        topics = sorted(topic_tracker.get_topics())
        if topics:
            st.markdown("**Empfangene Topics:**")

            # In Spalten anzeigen für bessere Übersicht
            cols = st.columns(3)
            for idx, topic in enumerate(topics[-30:]):  # Letzte 30 Topics
                with cols[idx % 3]:
                    st.code(topic, language="text")

        # Manueller Refresh-Button
        col1, col2 = st.columns([1, 3])

        with col1:
            if st.button("🔄 Aktualisieren", key="refresh_status"):
                rerun_controller.request_rerun()

        with col2:
            st.info("💡 **Tipp:** Klicke 'Aktualisieren' um den Status zu aktualisieren")

    # Gespeicherte Dateien anzeigen
    st.markdown("---")
    st.subheader("📋 Gespeicherte Topic-Dateien")

    # Dateien aus dem aktuellen Recording-Verzeichnis anzeigen
    current_recording_dir = st.session_state.topic_recorder.get('current_recording_dir')
    if current_recording_dir and current_recording_dir.exists():
        saved_files = list(current_recording_dir.glob("*.json"))
    else:
        saved_files = []
    if saved_files:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"**Anzahl Dateien:** {len(saved_files)}")

        with col2:
            sort_option = st.selectbox(
                "Sortierung:",
                ["Neueste zuerst", "Älteste zuerst", "Topic-Name A-Z", "Topic-Name Z-A"],
                key="topic_recorder_sort"
            )

        # Sortierung anwenden
        if sort_option == "Neueste zuerst":
            saved_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        elif sort_option == "Älteste zuerst":
            saved_files.sort(key=lambda f: f.stat().st_mtime, reverse=False)
        elif sort_option == "Topic-Name A-Z":
            saved_files.sort(key=lambda f: f.name)
        elif sort_option == "Topic-Name Z-A":
            saved_files.sort(key=lambda f: f.name, reverse=True)

        # In expandable sections zeigen
        with st.expander("📂 Gespeicherte Dateien anzeigen", expanded=False):
            for file in saved_files[:100]:  # Erste 100 Dateien
                file_size = file.stat().st_size
                file_mtime = datetime.fromtimestamp(file.stat().st_mtime)

                # JSON-Inhalt laden für Vorschau
                try:
                    import json
                    with open(file, encoding='utf-8') as f:
                        data = json.load(f)

                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.code(f"{file.name}", language="text")
                    with col2:
                        st.caption(f"QoS:{data.get('qos', '?')} Retain:{data.get('retain', '?')}")
                    with col3:
                        st.caption(f"📅 {file_mtime.strftime('%H:%M:%S')}")
                except Exception:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.code(f"{file.name} ({file_size} bytes)", language="text")
                    with col2:
                        st.caption(f"📅 {file_mtime.strftime('%H:%M:%S')}")
    else:
        st.info("📂 Noch keine Dateien gespeichert")


def connect_to_broker(mqtt_settings: Dict[str, Any]) -> bool:
    """Verbindet zum MQTT Broker"""
    try:
        import paho.mqtt.client as mqtt

        # MQTT Client erstellen
        mqtt_client = mqtt.Client(client_id="session_manager_topic_recorder")

        # Callback-Funktionen setzen
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message_received

        # Username/Password setzen falls vorhanden
        if mqtt_settings.get('username') and mqtt_settings.get('password'):
            mqtt_client.username_pw_set(mqtt_settings['username'], mqtt_settings['password'])
            logger.info(f"🔐 MQTT Authentifizierung: {mqtt_settings['username']}")

        # Verbinden
        mqtt_client.connect(mqtt_settings['host'], mqtt_settings['port'], mqtt_settings['timeout'])
        mqtt_client.loop_start()

        # Kurz warten, damit Verbindung etabliert wird
        import time
        time.sleep(0.5)

        # MQTT Client in Session State speichern
        st.session_state.topic_recorder['mqtt_client'] = mqtt_client

        logger.info(f"✅ MQTT verbunden: {mqtt_settings['host']}:{mqtt_settings['port']}")
        return True

    except Exception as e:
        logger.error(f"❌ MQTT Verbindungsfehler: {e}")
        return False


def disconnect_from_broker():
    """Trennt MQTT Verbindung"""
    try:
        if st.session_state.topic_recorder['mqtt_client']:
            mqtt_client = st.session_state.topic_recorder['mqtt_client']
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            st.session_state.topic_recorder['mqtt_client'] = None
            logger.info("✅ MQTT getrennt")
    except Exception as e:
        logger.error(f"❌ MQTT Trennung Fehler: {e}")


def on_connect(client, userdata, flags, rc):
    """Callback für MQTT Verbindung"""
    if rc == 0:
        logger.info("✅ MQTT Broker verbunden")
        # Automatisch alle Topics abonnieren
        client.subscribe("#")
        logger.info("📡 Alle Topics (#) abonniert")
    else:
        logger.error(f"❌ MQTT Verbindung fehlgeschlagen: {rc}")


def start_analysis():
    """Startet Analyse-Phase (keine Speicherung)"""
    try:
        logger.info("🔍 Topic-Analyse wird gestartet...")

        # Topics leeren für neue Analyse
        topic_tracker.clear()

        # MQTT Topics abonnieren (falls noch nicht geschehen)
        if st.session_state.topic_recorder['mqtt_client']:
            mqtt_client = st.session_state.topic_recorder['mqtt_client']
            mqtt_client.subscribe("#")
            logger.info("📡 MQTT Topics (#) abonniert für Analyse")
        else:
            logger.error("❌ Kein MQTT Client verfügbar")
            return

        # Globale Recording-Config auf Analyse setzen
        recording_config.start_analysis()

        logger.info("✅ Topic-Analyse gestartet")
    except Exception as e:
        logger.error(f"❌ Fehler beim Starten der Analyse: {e}")


def stop_analysis():
    """Beendet Analyse-Phase"""
    try:
        logger.info("⏹️ Topic-Analyse wird gestoppt...")
        recording_config.stop()
        logger.info("✅ Topic-Analyse beendet")
    except Exception as e:
        logger.error(f"❌ Fehler beim Stoppen der Analyse: {e}")


def analyze_topic_frequencies():
    """Analysiert gesammelte Topic-Frequenzen und identifiziert periodische Topics"""
    try:
        topic_counts = topic_tracker.get_topic_counts()
        analysis_duration = st.session_state.topic_recorder['analysis_duration']
        frequency_threshold = st.session_state.topic_recorder['frequency_threshold']

        logger.info(f"🔍 Analyse-Start: {len(topic_counts)} Topics, {analysis_duration}s, Schwellenwert: {frequency_threshold} msg/min")

        periodic_topics = set()

        for topic, count in topic_counts.items():
            # Frequenz in Messages pro MINUTE
            frequency_per_min = (count / analysis_duration) * 60

            if frequency_per_min >= frequency_threshold:
                periodic_topics.add(topic)
                logger.info(f"📊 Periodisch: {topic} ({count} msgs, {frequency_per_min:.1f} msg/min)")
            else:
                logger.debug(f"✨ Interessant: {topic} ({count} msgs, {frequency_per_min:.1f} msg/min)")

        st.session_state.topic_recorder['periodic_topics'] = periodic_topics

        logger.info(f"✅ Analyse abgeschlossen: {len(periodic_topics)} periodische, {len(topic_counts) - len(periodic_topics)} interessante Topics")

    except Exception as e:
        logger.error(f"❌ Fehler bei Frequenz-Analyse: {e}", exc_info=True)


def show_analysis_results():
    """Zeigt Analyse-Ergebnisse an"""
    st.subheader("📊 Analyse-Ergebnisse")

    topic_counts = topic_tracker.get_topic_counts()
    periodic_topics = st.session_state.topic_recorder['periodic_topics']
    analysis_duration = st.session_state.topic_recorder['analysis_duration']

    # Interessante vs. Periodische Topics
    interesting_topics = set(topic_counts.keys()) - periodic_topics

    col1, col2 = st.columns(2)

    with col1:
        st.metric("✨ Interessante Topics", len(interesting_topics))
        st.caption("(werden mit Sequenznummer gespeichert)")

    with col2:
        st.metric("🔄 Periodische Topics", len(periodic_topics))
        st.caption("(nur erste Nachricht)")

    # Details anzeigen
    with st.expander("📋 Topic-Details anzeigen"):
        # Interessante Topics
        st.markdown("### ✨ Interessante Topics (mit Sequenznummern)")
        for topic in sorted(interesting_topics):
            count = topic_counts[topic]
            freq_per_min = (count / analysis_duration) * 60
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(topic, language="text")
            with col2:
                st.caption(f"{count} msgs ({freq_per_min:.1f}/min)")

        st.markdown("---")

        # Periodische Topics
        st.markdown("### 🔄 Periodische Topics (nur erste Nachricht)")
        for topic in sorted(periodic_topics):
            count = topic_counts[topic]
            freq_per_min = (count / analysis_duration) * 60
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(topic, language="text")
            with col2:
                st.caption(f"{count} msgs ({freq_per_min:.1f}/min)")


def start_recording():
    """Startet die Aufnahme mit Sequenznummern"""
    try:
        logger.info("📂 Topic-Recording wird gestartet...")

        # MQTT Client für Aufnahme konfigurieren
        if st.session_state.topic_recorder['mqtt_client']:
            mqtt_client = st.session_state.topic_recorder['mqtt_client']
            # Topics abonnieren (falls sie deabonniert waren)
            mqtt_client.subscribe("#")

            # Session State aktualisieren
            st.session_state.topic_recorder['recording'] = True

            # Globale Recording-Config für MQTT-Callback setzen
            recording_dir = st.session_state.topic_recorder['current_recording_dir']
            if recording_dir is None:
                logger.error("❌ Kein Recording-Verzeichnis gesetzt")
                return

            # Periodische Topics: Kombination aus Analyse + manuell konfiguriert
            from .settings_manager import SettingsManager
            settings_manager = SettingsManager()
            manual_periodic = set(settings_manager.get_topic_recorder_periodic_topics())
            analyzed_periodic = st.session_state.topic_recorder['periodic_topics']

            # Vereinigung beider Sets
            all_periodic_topics = manual_periodic | analyzed_periodic

            recording_config.start_recording(recording_dir, all_periodic_topics)

            logger.info(f"✅ Topic-Recording gestartet - {len(all_periodic_topics)} periodische Topics ({len(analyzed_periodic)} analysiert, {len(manual_periodic)} manuell)")
        else:
            logger.error("❌ Kein MQTT Client verfügbar für Recording")

    except Exception as e:
        logger.error(f"❌ Fehler beim Starten des Recordings: {e}")


def stop_recording():
    """Beendet die Aufnahme"""
    try:
        logger.info("⏹️ Topic-Recording wird gestoppt...")

        # Globale Recording-Config stoppen (für MQTT-Callback)
        recording_config.stop()

        # Recording stoppen
        if st.session_state.topic_recorder['mqtt_client']:
            mqtt_client = st.session_state.topic_recorder['mqtt_client']
            mqtt_client.unsubscribe("#")
            logger.info("📡 MQTT Topics deabonniert")

        # Session State aktualisieren
        st.session_state.topic_recorder['recording'] = False

        topic_count = topic_tracker.count()
        logger.info(f"✅ Topic-Recording beendet - {topic_count} Topics empfangen")

    except Exception as e:
        logger.error(f"❌ Fehler beim Stoppen des Recordings: {e}")


def on_message_received(client, userdata, msg):
    """Callback für empfangene MQTT-Nachrichten (thread-sicher)"""
    try:
        import json

        topic = msg.topic
        payload = msg.payload.decode('utf-8', errors='replace')
        qos = msg.qos
        retain = msg.retain

        # Topic zur Sammlung hinzufügen (für Analyse & Recording)
        topic_tracker.add_topic(topic)

        # Analyse-Phase: Nur zählen, nichts speichern
        if recording_config.is_analyzing():
            logger.debug(f"🔍 Analyse: {topic}")
            return

        # Recording-Phase: Mit Sequenznummern speichern
        if not recording_config.is_recording():
            return

        # Dateinamen generieren
        sanitized_topic = sanitize_topic_name(topic)

        # Prüfen ob Topic periodisch ist
        is_periodic = recording_config.is_periodic(topic)

        # Dateipfad (thread-sicherer Zugriff)
        topics_dir = recording_config.get_topics_directory()
        if topics_dir is None:
            logger.error("❌ Topics-Verzeichnis nicht konfiguriert")
            return

        if is_periodic:
            # Periodisches Topic: Nur erste Nachricht ohne Sequenznummer
            filename = f"{sanitized_topic}.json"
            filepath = topics_dir / filename

            # NUR speichern wenn Datei NICHT existiert
            if not filepath.exists():
                topic_data = {
                    "topic": topic,
                    "payload": payload,
                    "qos": qos,
                    "retain": retain,
                    "timestamp": datetime.now().isoformat(),
                    "type": "periodic"
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(topic_data, f, indent=2, ensure_ascii=False)

                logger.debug(f"📂 Periodisch gespeichert: {filename}")
            else:
                logger.debug(f"⏭️ Periodisch ignoriert: {filename}")
        else:
            # Interessantes Topic: Mit globaler Sequenznummer
            sequence = recording_config.get_next_sequence()
            filename = f"{sanitized_topic}__{sequence:06d}.json"
            filepath = topics_dir / filename

            topic_data = {
                "topic": topic,
                "payload": payload,
                "qos": qos,
                "retain": retain,
                "timestamp": datetime.now().isoformat(),
                "sequence": sequence,
                "type": "interesting"
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(topic_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"📂 Sequenz gespeichert: {filename} (global seq: {sequence})")

    except Exception as e:
        logger.error(f"❌ Nachricht Verarbeitung Fehler: {e}")

