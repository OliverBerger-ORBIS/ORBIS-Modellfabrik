"""
Replay Station Komponente
Funktionalität wie alte Replay Station - MQTT-Nachrichten für Tests senden
Isolierte Version ohne OMF-Dependencies
"""

import json
import logging
import re
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Protocol, Tuple

import streamlit as st

from ..mqtt.mqtt_client import SessionManagerMQTTClient
from ..utils.logging_config import get_logger
from ..utils.path_constants import PROJECT_ROOT
from ..utils.ui_refresh import RerunController

# Logging konfigurieren - Verzeichnis sicherstellen
log_dir = Path("logs/session_manager")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_dir / "session_manager.log"), logging.StreamHandler()],
)
logger = get_logger(__name__)


# =========================
# Replay-Controller (neu)
# =========================
class _Publisher(Protocol):
    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> None: ...


@dataclass(frozen=True)
class _ReplayItem:
    ts_rel: float
    topic: str
    payload: bytes
    qos: int = 0
    retain: bool = False


class ReplayController:
    """
    Thread-sicherer MQTT-Replay-Controller mit persistentem MQTT-Client.
    - Keine Connection-Loops durch persistente Verbindung
    - Thread-sichere Publishing ohne mosquitto_pub
    - Sauberes Cleanup alter Controller-Instanzen
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = int(port)
        self._seq: List[_ReplayItem] = []
        self._idx = 0
        self._speed = 1.0
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._pause = threading.Event()  # gesetzt = pausiert
        self._worker: Optional[threading.Thread] = None
        self.started_at_mono: float = 0.0
        self._mqtt_client: Optional[SessionManagerMQTTClient] = None

    # ---------- öffentlich ----------
    def load(self, items: List[Tuple[float, str, bytes, int, bool]]) -> None:
        """items: Liste (ts_rel, topic, payload_bytes, qos, retain)"""
        with self._lock:
            self._seq = [_ReplayItem(*it) for it in items]
            self._idx = 0
            self._stop.clear()
            self._pause.clear()

    def play(self, speed: float = 1.0) -> None:
        with self._lock:
            self._speed = max(0.1, float(speed))
            if self._worker and self._worker.is_alive():
                self._pause.clear()
                return

            # MQTT-Client initialisieren falls nötig
            if not self._mqtt_client:
                self._mqtt_client = SessionManagerMQTTClient(self.host, self.port, "session_manager_replay")
                if not self._mqtt_client.connect():
                    logger.error("❌ MQTT-Client konnte nicht verbinden")
                    return

            self._stop.clear()
            self._pause.clear()
            self.started_at_mono = time.monotonic() - (self._seq[self._idx].ts_rel / self._speed if self._seq else 0.0)
            self._worker = threading.Thread(target=self._run, name="replay-worker", daemon=True)
            self._worker.start()

    def pause(self) -> None:
        self._pause.set()

    def resume(self) -> None:
        with self._lock:
            if not (self._worker and self._worker.is_alive()):
                return
            # Startzeit für aktuelle Position neu ausrichten
            now = time.monotonic()
            current_rel = self._seq[self._idx].ts_rel if self._idx < len(self._seq) else 0.0
            self.started_at_mono = now - current_rel / self._speed
            self._pause.clear()

    def stop(self) -> None:
        self._stop.set()
        self._pause.clear()
        with self._lock:
            self._idx = 0
            # Worker-Thread sauber beenden
            if self._worker and self._worker.is_alive():
                self._worker.join(timeout=2.0)  # Max 2 Sekunden warten

    def set_speed(self, speed: float) -> None:
        with self._lock:
            self._speed = max(0.1, float(speed))
            if self._seq and self._idx < len(self._seq):
                # Startzeit an neue Geschwindigkeit anpassen
                now = time.monotonic()
                current_rel = self._seq[self._idx].ts_rel
                self.started_at_mono = now - current_rel / self._speed

    def progress(self) -> tuple[int, int]:
        with self._lock:
            return self._idx, len(self._seq)

    def is_running(self) -> bool:
        w = self._worker
        return bool(w and w.is_alive() and not self._pause.is_set() and not self._stop.is_set())

    # ---------- intern ----------
    def _run(self) -> None:
        while not self._stop.is_set():
            with self._lock:
                if self._idx >= len(self._seq):
                    break
                item = self._seq[self._idx]
                speed = self._speed
                start = self.started_at_mono
            # Pause blockierend abwarten
            while self._pause.is_set() and not self._stop.is_set():
                time.sleep(0.05)
            if self._stop.is_set():
                break
            # Zeitpunkt (mit Speed) abwarten
            due = start + (item.ts_rel / speed)
            now = time.monotonic()
            if due > now:
                time.sleep(min(0.1, due - now))
                continue
            # Publish mit persistentem MQTT-Client
            if self._mqtt_client and self._mqtt_client.is_connected():
                try:
                    payload_str = (
                        item.payload
                        if isinstance(item.payload, (bytes, bytearray))
                        else str(item.payload).encode("utf-8")
                    )
                    success = self._mqtt_client.publish(
                        topic=item.topic, payload=payload_str, qos=item.qos, retain=item.retain
                    )
                    if not success:
                        logger.warning(f"⚠️ MQTT-Publish fehlgeschlagen: {item.topic}")
                except Exception as e:
                    logger.error(f"❌ MQTT-Publish Exception: {e}")
            else:
                logger.error("❌ MQTT-Client nicht verbunden")
            # Index vorrücken
            with self._lock:
                self._idx += 1

    def cleanup(self):
        """Sauberes Cleanup des Controllers"""
        self.stop()
        if self._mqtt_client:
            self._mqtt_client.disconnect()
            self._mqtt_client = None


# Einfache Factory, die genau EINE Controller-Instanz je Broker hält
def _get_replay_controller(mqtt_host: str, mqtt_port: int) -> ReplayController:
    key = "_replay_controller"
    rc: Optional[ReplayController] = st.session_state.get(key)

    # Alten Controller sauber stoppen falls Host/Port geändert
    if rc and (rc.host != mqtt_host or int(rc.port) != int(mqtt_port)):
        logger.info("🔄 Alten ReplayController stoppen (Host/Port geändert)")
        rc.cleanup()
        rc = None
        del st.session_state[key]

    # Neuen Controller erstellen falls nötig
    if rc is None:
        logger.info(f"🆕 Neuen ReplayController erstellen: {mqtt_host}:{mqtt_port}")
        rc = ReplayController(mqtt_host, int(mqtt_port))
        st.session_state[key] = rc

    return rc


def show_replay_station():
    """Replay Station Tab - Fokussiert auf wesentliche Funktionen"""

    logger.info("📡 Replay Station Tab geladen")

    # RerunController initialisieren
    rerun_controller = RerunController()

    st.header("📡 Replay Station")
    st.markdown("MQTT-Nachrichten für Tests senden - **MQTT-Konfiguration in ⚙️ Einstellungen**")

    # Konfiguration aus Settings laden
    from .settings_manager import SettingsManager

    settings_manager = SettingsManager()
    mqtt_settings = settings_manager.get_mqtt_broker_settings()
    session_directory = settings_manager.get_session_directory()

    # Verbindungsstatus anzeigen
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔌 MQTT Verbindung")
        st.info(f"**Broker:** {mqtt_settings['host']}:{mqtt_settings['port']}")
        st.info(f"**QoS:** {mqtt_settings['qos']} | **Timeout:** {mqtt_settings['timeout']}s")

        if "mqtt_connected" not in st.session_state:
            st.session_state.mqtt_connected = False

        if st.session_state.mqtt_connected:
            st.success("✅ Verbunden")
        else:
            st.error("❌ Nicht verbunden")

    with col2:
        st.subheader("⚙️ Konfiguration")
        st.info(f"**Session-Verzeichnis:** `{session_directory}`")
        st.markdown("**MQTT-Einstellungen** können hier konfiguriert werden")
        st.info("💡 MQTT-Konfiguration wird automatisch aus den Session-Daten geladen")

    # Connection controls
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔌 Verbindung testen", key="test_mqtt"):
            logger.debug("🔌 User klickt: Verbindung testen")
            test_mqtt_connection(mqtt_settings["host"], mqtt_settings["port"], rerun_controller)

    with col2:
        if st.button("🔌 Verbindung trennen", key="disconnect_mqtt"):
            logger.debug("🔌 User klickt: Verbindung trennen")
            disconnect_mqtt(rerun_controller)

    # Session State für MQTT Parameter speichern
    st.session_state.mqtt_host = mqtt_settings["host"]
    st.session_state.mqtt_port = mqtt_settings["port"]
    replay_ctrl = _get_replay_controller(st.session_state.mqtt_host, st.session_state.mqtt_port)

    st.markdown("---")

    # Sektion 1: Session Replay
    st.subheader("📁 Session Replay")

    # Session-Verzeichnis analysieren
    logger.debug(f"🔍 Replay Station: Suche Sessions in: {session_directory}")
    session_files = get_session_files(session_directory)
    logger.debug(f"📁 Gefundene Session-Dateien: {len(session_files)}")

    if not session_files:
        st.warning("❌ Keine Session-Dateien gefunden")
        st.info(f"💡 Legen Sie Log-Dateien (.log) in `{session_directory}/` ab")
        st.info("ℹ️ **Hinweis:** Nur .log Dateien (JSON-Zeilen-Format) werden für Replay unterstützt")
    else:
        # Regex-Filter
        col1, col2 = st.columns([2, 1])
        with col1:
            regex_filter = st.text_input("🔍 Regex-Filter", placeholder="z.B. 'Waren' für Wareneingang-Sessions")
        with col2:
            if st.button("🔍 Filtern"):
                logger.debug(f"🔍 User klickt: Filtern mit '{regex_filter}'")
                st.session_state.session_filter = regex_filter
                rerun_controller.request_rerun()

        # Session-Liste filtern
        filtered_sessions = filter_sessions(session_files, st.session_state.get("session_filter", ""))

        if filtered_sessions:
            # Session-Auswahl
            selected_session = st.selectbox("📂 Session auswählen:", filtered_sessions, format_func=lambda x: x.name)

            if selected_session:
                # Session-Info
                st.info(f"📁 Ausgewählte Session: {selected_session.name}")

                # Test-Topic Preload & Individuelle Auswahl
                st.markdown("#### 📋 Test-Topic Management")

                # Sektion 1: Individuelles Senden
                st.markdown("##### 🎯 Individuelle Test-Topics")
                test_topic_files = get_test_topic_files()

                if test_topic_files:
                    # Multiselect für individuelle Auswahl
                    selected_test_topics = st.multiselect(
                        "Wähle Test-Topics zum Senden:",
                        options=test_topic_files,
                        format_func=lambda x: x.name,
                        help="Wähle eine oder mehrere JSON-Dateien aus data/osf-data/test_topics/",
                    )

                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if selected_test_topics:
                            st.info(f"✅ {len(selected_test_topics)} Test-Topic(s) ausgewählt")
                    with col2:
                        if st.button(
                            "📤 Ausgewählte jetzt senden", key="send_selected_topics", disabled=not selected_test_topics
                        ):
                            logger.debug(
                                f"📤 User klickt: Ausgewählte Test-Topics senden ({len(selected_test_topics)} Dateien)"
                            )
                            send_selected_test_topics(selected_test_topics, replay_ctrl)
                else:
                    st.warning("❌ Keine Test-Topic-Dateien in data/osf-data/test_topics/ gefunden")

                st.markdown("---")

                # Sektion 2: Automatischer Preload
                st.markdown("##### 🚀 Automatischer Preload")
                col1, col2 = st.columns([2, 1])

                with col1:
                    send_preloads = st.checkbox(
                        "🚀 Test-Topics vor Session-Replay senden",
                        value=True,
                        help="Sendet automatisch alle Test-Topics aus data/osf-data/test_topics/preloads/ vor dem Session-Replay",
                    )

                with col2:
                    if st.button("🚀 Preloads jetzt senden", key="send_preloads_now"):
                        logger.debug("🚀 User klickt: Preloads jetzt senden")
                        send_preload_test_topics(replay_ctrl)

                # Verfügbare Preload-Topics anzeigen
                preload_files = get_preload_test_topic_files()
                if preload_files:
                    st.info(f"🚀 {len(preload_files)} Preload-Test-Topic(s) verfügbar")
                    with st.expander("📋 Verfügbare Preload-Topics anzeigen"):
                        for preload_file in preload_files[:10]:  # Erste 10 anzeigen
                            st.text(f"• {preload_file.name}")
                        if len(preload_files) > 10:
                            st.text(f"... und {len(preload_files) - 10} weitere")
                else:
                    st.info("ℹ️ Keine Preload-Test-Topics in data/osf-data/test_topics/preloads/ gefunden")

                # Session laden
                if st.button("📂 Session laden"):
                    logger.debug(f"📂 User klickt: Session laden - {selected_session.name}")
                    if send_preloads:
                        logger.info("🚀 Test-Topic Preload vor Session-Load")
                        send_preload_test_topics(replay_ctrl)
                    load_session(selected_session, replay_ctrl)

                # Replay-Kontrollen (wenn Session geladen)
                if "loaded_session" in st.session_state and st.session_state.loaded_session:
                    show_replay_controls(rerun_controller)
        else:
            st.warning("❌ Keine Sessions gefunden (Regex-Filter)")

    st.markdown("---")

    # Sektion 2: Test Messages (sofort testbar)
    st.subheader("🧪 Test Messages")
    st.markdown("Sofort testbare MQTT-Nachrichten senden")

    # Test Message 1
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Topic", value="test/session_manager", key="test_topic_1")
    with col2:
        if st.button("📤 Senden", key="send_test_1"):
            send_test_message(
                "test/session_manager",
                {"message": "Hello from Session Manager!", "timestamp": datetime.now().isoformat()},
            )

    # Test Message 2
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Topic", value="module/v1/ff/SVR3QA0022/order", key="test_topic_2")
    with col2:
        if st.button("📤 Senden", key="send_test_2"):
            send_test_message("module/v1/ff/SVR3QA0022/order", {"command": "PICK", "workpiece": "RED"})

    # Schnelltest-Buttons
    st.markdown("#### 🚀 Schnelltest-Nachrichten")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📡 Test 1", key="quick_test_1"):
            send_test_message("test/quick/1", {"id": 1, "status": "active"})

    with col2:
        if st.button("📡 Test 2", key="quick_test_2"):
            send_test_message("test/quick/2", {"id": 2, "value": 123.45})

    with col3:
        if st.button("📡 Test 3", key="quick_test_3"):
            send_test_message("test/quick/3", {"id": 3, "data": "Hello World"})


def test_mqtt_connection(host, port, rerun_controller: RerunController):
    """MQTT Verbindung testen mit persistentem MQTT-Client"""
    try:
        # Temporären MQTT-Client für Test erstellen
        test_client = SessionManagerMQTTClient(host, port, "session_manager_test")

        if test_client.connect():
            # Test-Nachricht senden
            success = test_client.publish("test/connection", "test", qos=1)
            test_client.disconnect()

            if success:
                st.session_state.mqtt_connected = True
                st.success(f"✅ MQTT Broker erreichbar: {host}:{port}")
                rerun_controller.request_rerun()
                return True
            else:
                st.error("❌ MQTT Test-Nachricht konnte nicht gesendet werden")
                st.session_state.mqtt_connected = False
                rerun_controller.request_rerun()
                return False
        else:
            st.error(f"❌ MQTT Broker nicht erreichbar: {host}:{port}")
            st.session_state.mqtt_connected = False
            rerun_controller.request_rerun()
            return False
    except Exception as e:
        st.error(f"❌ Verbindung fehlgeschlagen: {e}")
        st.session_state.mqtt_connected = False
        rerun_controller.request_rerun()
        return False


def disconnect_mqtt(rerun_controller: RerunController):
    """MQTT Verbindung trennen"""
    st.session_state.mqtt_connected = False
    st.success("✅ Verbindung getrennt")
    rerun_controller.request_rerun()  # UI sofort aktualisieren


def send_test_message(topic, payload):
    """Test-Nachricht mit persistentem MQTT-Client senden"""
    try:
        # Temporären MQTT-Client für Test erstellen
        test_client = SessionManagerMQTTClient(
            st.session_state.mqtt_host, st.session_state.mqtt_port, "session_manager_test"
        )

        if test_client.connect():
            # Payload-Aufbereitung wie normale Session-Daten (konsistent)
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            payload_b = (payload if isinstance(payload, (bytes, bytearray)) else str(payload)).encode("utf-8")

            # Nachricht senden
            success = test_client.publish(topic, payload_b, qos=1)
            test_client.disconnect()

            if success:
                st.session_state.mqtt_connected = True
                st.success(f"📤 Nachricht gesendet: {topic}")
            else:
                st.session_state.mqtt_connected = False
                st.error("❌ Fehler beim Senden der Nachricht")
        else:
            st.session_state.mqtt_connected = False
            st.error("❌ MQTT-Client konnte nicht verbinden")
    except Exception as e:
        st.session_state.mqtt_connected = False
        st.error(f"❌ Fehler beim Senden: {e}")


def send_selected_test_topics(selected_files: List[Path], replay_ctrl: ReplayController):
    """Ausgewählte Test-Topic-Messages aus JSON-Dateien laden und an Broker senden"""
    try:
        if not selected_files:
            st.warning("❌ Keine Test-Topics ausgewählt")
            return False

        logger.info(f"📤 Sende {len(selected_files)} ausgewählte Test-Topic(s)...")

        # Temporären MQTT-Client für Test-Topics erstellen
        test_client = SessionManagerMQTTClient(
            st.session_state.mqtt_host, st.session_state.mqtt_port, "session_manager_test_topics"
        )

        if not test_client.connect():
            st.error("❌ MQTT-Client konnte nicht für Test-Topics verbinden")
            return False

        success_count = 0
        error_count = 0

        # Test-Topics laden und senden
        for test_file in selected_files:
            try:
                with open(test_file, encoding="utf-8") as f:
                    test_data = json.load(f)

                topic = test_data.get("topic")
                payload = test_data.get("payload")
                qos = test_data.get("qos", 0)
                retain = test_data.get("retain", False)

                if topic and payload:
                    # Payload-Aufbereitung wie normale Session-Daten
                    if isinstance(payload, (dict, list)):
                        payload = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
                    payload_b = (payload if isinstance(payload, (bytes, bytearray)) else str(payload)).encode("utf-8")

                    success = test_client.publish(topic, payload_b, qos=qos, retain=retain)

                    if success:
                        success_count += 1
                        logger.debug(f"✅ Test-Topic gesendet: {topic} ({test_file.name})")
                    else:
                        error_count += 1
                        logger.warning(f"⚠️ Test-Topic fehlgeschlagen: {topic} ({test_file.name})")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ Ungültige Test-Topic-Daten: {test_file.name}")

            except Exception as e:
                error_count += 1
                logger.error(f"❌ Fehler beim Laden von {test_file.name}: {e}")

        test_client.disconnect()

        # Ergebnis anzeigen
        if success_count > 0:
            st.success(f"✅ {success_count} Test-Topic(s) erfolgreich gesendet")
            if error_count > 0:
                st.warning(f"⚠️ {error_count} Test-Topic(s) fehlgeschlagen")
        else:
            st.error("❌ Keine Test-Topics konnten gesendet werden")

        logger.info(f"📤 Test-Topic-Versand abgeschlossen: {success_count} erfolgreich, {error_count} fehlgeschlagen")
        return success_count > 0

    except Exception as e:
        st.error(f"❌ Fehler beim Test-Topic-Versand: {e}")
        logger.error(f"❌ Test-Topic-Versand Exception: {e}")
        return False


def send_preload_test_topics(replay_ctrl: ReplayController):
    """Preload Test-Topic-Messages aus JSON-Dateien laden und an Broker senden (alle aus preloads/)"""
    try:
        # Preload-Verzeichnis
        preload_dir = PROJECT_ROOT / "data/osf-data/test_topics/preloads"

        if not preload_dir.exists():
            st.warning(f"❌ Preload-Verzeichnis nicht gefunden: {preload_dir}")
            return False

        # JSON-Preload-Dateien finden
        preload_files = list(preload_dir.glob("*.json"))

        if not preload_files:
            st.warning("❌ Keine Preload-JSON-Dateien in data/osf-data/test_topics/preloads/ gefunden")
            return False

        logger.info(f"🚀 Lade {len(preload_files)} Preload-Test-Topic(s)...")

        # Temporären MQTT-Client für Preloads erstellen
        preload_client = SessionManagerMQTTClient(
            st.session_state.mqtt_host, st.session_state.mqtt_port, "session_manager_preloads"
        )

        if not preload_client.connect():
            st.error("❌ MQTT-Client konnte nicht für Preloads verbinden")
            return False

        success_count = 0
        error_count = 0

        # Preloads laden und senden
        for preload_file in preload_files:
            try:
                with open(preload_file, encoding="utf-8") as f:
                    preload_data = json.load(f)

                topic = preload_data.get("topic")
                payload = preload_data.get("payload")
                qos = preload_data.get("qos", 0)
                retain = preload_data.get("retain", False)

                if topic and payload:
                    # Payload-Aufbereitung wie normale Session-Daten
                    if isinstance(payload, (dict, list)):
                        payload = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
                    payload_b = (payload if isinstance(payload, (bytes, bytearray)) else str(payload)).encode("utf-8")

                    success = preload_client.publish(topic, payload_b, qos=qos, retain=retain)

                    if success:
                        success_count += 1
                        logger.debug(f"✅ Preload gesendet: {topic}")
                    else:
                        error_count += 1
                        logger.warning(f"⚠️ Preload fehlgeschlagen: {topic}")
                else:
                    error_count += 1
                    logger.warning(f"⚠️ Ungültige Preload-Daten: {preload_file.name}")

            except Exception as e:
                error_count += 1
                logger.error(f"❌ Fehler beim Laden von {preload_file.name}: {e}")

        preload_client.disconnect()

        # Ergebnis anzeigen
        if success_count > 0:
            st.success(f"✅ {success_count} Preload-Test-Topic(s) erfolgreich gesendet")
            if error_count > 0:
                st.warning(f"⚠️ {error_count} Preload-Test-Topic(s) fehlgeschlagen")
        else:
            st.error("❌ Keine Preload-Test-Topics konnten gesendet werden")

        logger.info(f"🚀 Preload abgeschlossen: {success_count} erfolgreich, {error_count} fehlgeschlagen")
        return success_count > 0

    except Exception as e:
        st.error(f"❌ Fehler beim Preload: {e}")
        logger.error(f"❌ Preload Exception: {e}")
        return False


# Session Replay Funktionen
def get_test_topic_files(test_topic_directory: str = "data/osf-data/test_topics"):
    """Test-Topic-Dateien aus konfiguriertem Verzeichnis laden - nur .json Dateien"""
    logger.debug(f"🔍 get_test_topic_files: Suche in {test_topic_directory}")

    # Moderne Paket-Struktur - State of the Art
    if not Path(test_topic_directory).is_absolute():
        # Projekt-Root-relative Pfade für Nutz-Daten verwenden
        project_root = PROJECT_ROOT
        test_topic_dir = project_root / test_topic_directory
    else:
        test_topic_dir = Path(test_topic_directory)

    logger.debug(f"📁 Test-Topic-Verzeichnis existiert: {test_topic_dir.exists()}")
    logger.debug(f"📁 Absoluter Pfad: {test_topic_dir.absolute()}")

    if not test_topic_dir.exists():
        logger.warning(f"❌ Test-Topic-Verzeichnis existiert nicht: {test_topic_dir.absolute()}")
        return []

    # Nur JSON-Dateien im Hauptverzeichnis finden (nicht in preloads/)
    test_topic_files = [f for f in test_topic_dir.glob("*.json") if f.is_file()]

    logger.debug(f"📊 Gefundene .json Test-Topic-Dateien: {len(test_topic_files)}")

    logger.debug(f"📁 Gesamt Test-Topic-Dateien: {len(test_topic_files)}")
    for f in test_topic_files:
        logger.debug(f"  - {f.name}")

    return sorted(test_topic_files, key=lambda x: x.name)


def get_preload_test_topic_files(preload_directory: str = "data/osf-data/test_topics/preloads"):
    """Preload-Test-Topic-Dateien aus konfiguriertem Verzeichnis laden - nur .json Dateien"""
    logger.debug(f"🔍 get_preload_test_topic_files: Suche in {preload_directory}")

    # Moderne Paket-Struktur - State of the Art
    if not Path(preload_directory).is_absolute():
        # Projekt-Root-relative Pfade für Nutz-Daten verwenden
        project_root = PROJECT_ROOT
        preload_dir = project_root / preload_directory
    else:
        preload_dir = Path(preload_directory)

    logger.debug(f"📁 Preload-Verzeichnis existiert: {preload_dir.exists()}")
    logger.debug(f"📁 Absoluter Pfad: {preload_dir.absolute()}")

    if not preload_dir.exists():
        logger.warning(f"❌ Preload-Verzeichnis existiert nicht: {preload_dir.absolute()}")
        return []

    # Nur JSON-Dateien finden (Preload kann nur .json Dateien verarbeiten)
    preload_files = list(preload_dir.glob("*.json"))

    logger.debug(f"📊 Gefundene .json Preload-Dateien: {len(preload_files)}")

    logger.debug(f"📁 Gesamt Preload-Dateien: {len(preload_files)}")
    for f in preload_files:
        logger.debug(f"  - {f.name}")

    return sorted(preload_files, key=lambda x: x.name)


def get_session_files(session_directory: str = "data/osf-data/sessions"):
    """Session-Dateien aus konfiguriertem Verzeichnis laden - nur .log Dateien (JSON-Zeilen-Format)"""
    logger.debug(f"🔍 get_session_files: Suche in {session_directory}")

    # Moderne Paket-Struktur - State of the Art
    if not Path(session_directory).is_absolute():
        # Projekt-Root-relative Pfade für Nutz-Daten verwenden
        project_root = PROJECT_ROOT
        session_dir = project_root / session_directory
    else:
        session_dir = Path(session_directory)

    logger.debug(f"📁 Verzeichnis existiert: {session_dir.exists()}")
    logger.debug(f"📁 Absoluter Pfad: {session_dir.absolute()}")

    if not session_dir.exists():
        logger.warning(f"❌ Verzeichnis existiert nicht: {session_dir.absolute()}")
        return []

    # Nur Log-Dateien finden (Replay Station nutzt JSON-Zeilen-Format)
    session_files = list(session_dir.glob("*.log"))

    logger.debug(f"📊 Gefundene .log Dateien: {len(session_files)}")

    logger.debug(f"📁 Gesamt Session-Dateien: {len(session_files)}")
    for f in session_files:
        logger.debug(f"  - {f.name}")

    return sorted(session_files, key=lambda x: x.name)


def filter_sessions(session_files, regex_filter):
    """Sessions nach Regex-Filter filtern"""
    if not regex_filter:
        return session_files

    try:
        pattern = re.compile(regex_filter, re.IGNORECASE)
        return [f for f in session_files if pattern.search(f.name)]
    except re.error:
        return session_files


def load_session(session_file, replay_ctrl: ReplayController):
    """Session laden und in Session State speichern (nur .log mit JSON-Zeilen-Format)"""
    try:
        messages = load_log_session(session_file)

        if messages:
            # Sequenz vorbereiten: (ts_rel, topic, payload_bytes, qos, retain)
            items: List[Tuple[float, str, bytes, int, bool]] = []

            # Timestamps auf Sekunden float normalisieren
            def _to_epoch_s(ts_val):
                # int/float Epoch
                if isinstance(ts_val, (int, float)):
                    return float(ts_val)
                s = str(ts_val).strip()
                # ISO 8601
                try:
                    if s.endswith("Z"):
                        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                    else:
                        dt = datetime.fromisoformat(s)
                    return dt.timestamp()
                except Exception:
                    # Fallback: try float
                    try:
                        return float(s)
                    except Exception:
                        return 0.0

            if messages:
                t0 = _to_epoch_s(messages[0].get("timestamp", 0))
                for m in messages:
                    topic = m["topic"]
                    payload = m["payload"]
                    ts = _to_epoch_s(m.get("timestamp", 0))
                    ts_rel = max(0.0, ts - t0)
                    if isinstance(payload, (dict, list)):
                        payload = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
                    payload_b = (payload if isinstance(payload, (bytes, bytearray)) else str(payload)).encode("utf-8")
                    items.append((ts_rel, topic, payload_b, 1, False))  # qos=1, retain=False als Default

            # in Controller laden
            replay_ctrl.load(items)
            st.session_state.loaded_session = {
                "file": session_file,
                "messages": messages,
                "current_index": 0,
                "is_playing": False,  # UI-Flag; Controller ist maßgeblich
                "speed": 1.0,
                "loop": False,
            }
            st.success(f"✅ Session '{session_file.name}' geladen ({len(messages)} Nachrichten)")
        else:
            st.error(f"❌ Session '{session_file.name}' konnte nicht geladen werden")
    except Exception as e:
        st.error(f"❌ Fehler beim Laden: {e}")


def load_log_session(session_file):
    """Log Session laden (JSON-Zeilen-Format: eine JSON-Nachricht pro Zeile)"""
    try:
        messages = []
        with open(session_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if "topic" in data and "payload" in data and "timestamp" in data:
                        messages.append(
                            {
                                "topic": data["topic"],
                                "payload": data["payload"],
                                "timestamp": data["timestamp"],
                            }
                        )
                except json.JSONDecodeError:
                    continue
        return messages
    except Exception:
        return []


def show_replay_controls(rerun_controller: RerunController):
    """Replay-Kontrollen anzeigen"""
    session = st.session_state.loaded_session
    replay_ctrl = _get_replay_controller(st.session_state.mqtt_host, st.session_state.mqtt_port)

    st.markdown("#### 🎮 Replay-Kontrollen")

    # Status-Anzeige
    col1, col2, col3 = st.columns(3)
    with col1:
        total_msgs = len(session["messages"])
        st.metric("Nachrichten", total_msgs)
    with col2:
        idx, total = replay_ctrl.progress()
        st.metric("Aktuell", f"{min(idx, total)}/{total}")
    with col3:
        status = "▶️ Aktiv" if replay_ctrl.is_running() else ("⏸️ Pausiert" if session.get("is_playing") else "⏹️ Stopp")
        st.metric("Status", status)

    # Kontroll-Buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Play / Resume
        if st.button("▶️ Play / Resume", key="play_resume_btn"):
            session_name = (
                session.get("file", {}).get("name", "Unknown")
                if isinstance(session.get("file"), dict)
                else str(session.get("file", "Unknown"))
            )
            logger.debug(f"▶️ User klickt: Play/Resume - Session: {session_name}")
            # Controller starten (mit aktueller Geschwindigkeit)
            replay_ctrl.play(speed=session.get("speed", 1.0))
            session["is_playing"] = True
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col2:
        if st.button("⏸️ Pause", key="pause_btn"):
            session_name = (
                session.get("file", {}).get("name", "Unknown")
                if isinstance(session.get("file"), dict)
                else str(session.get("file", "Unknown"))
            )
            logger.debug(f"⏸️ User klickt: Pause - Session: {session_name}")
            replay_ctrl.pause()
            session["is_playing"] = False
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col3:
        if st.button("⏹️ Stop", key="stop_btn"):
            session_name = (
                session.get("file", {}).get("name", "Unknown")
                if isinstance(session.get("file"), dict)
                else str(session.get("file", "Unknown"))
            )
            logger.debug(f"⏹️ User klickt: Stop - Session: {session_name}")
            replay_ctrl.stop()
            session["is_playing"] = False
            session["current_index"] = 0
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col4:
        if st.button("🔄 Reset", key="reset_btn"):
            session_name = (
                session.get("file", {}).get("name", "Unknown")
                if isinstance(session.get("file"), dict)
                else str(session.get("file", "Unknown"))
            )
            logger.debug(f"🔄 User klickt: Reset - Session: {session_name}")
            replay_ctrl.stop()
            session["is_playing"] = False
            session["current_index"] = 0
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    # Einstellungen
    col1, col2 = st.columns(2)

    with col1:
        speed = st.selectbox(
            "🏃 Geschwindigkeit",
            [0.2, 0.33, 0.5, 1.0, 2.0, 3.0, 5.0],
            index=3,
            format_func=lambda x: f"{x}x" if x >= 1 else f"1/{int(1/x)}x",
        )
        session["speed"] = speed
        # Speed ggf. im Controller aktualisieren
        replay_ctrl.set_speed(speed)

    with col2:
        loop = st.checkbox("🔄 Loop", value=False)
        session["loop"] = loop

    # Fortschritt visualisieren
    idx, total = replay_ctrl.progress()
    if total > 0:
        st.progress(idx / total)
        st.text(f"📊 Fortschritt: {idx}/{total}")
    else:
        st.progress(0.0)
        st.text("📊 Fortschritt: 0/0")

    # UI-Polling statt Re-Run pro Nachricht
    if replay_ctrl.is_running():
        # Einfacher manueller Refresh-Button
        if st.button("🔄 Status", key="refresh_status"):
            st.rerun()

    # (alte Replay-Logik entfernt - wird jetzt vom ReplayController gehandhabt)


def start_replay():
    """Replay starten"""
    if "loaded_session" not in st.session_state:
        logger.error("❌ Start Replay: Keine Session geladen")
        st.error("❌ Keine Session geladen")
        return

    session = st.session_state.loaded_session
    session["is_playing"] = True
    session_name = (
        session.get("file", {}).get("name", "Unknown")
        if isinstance(session.get("file"), dict)
        else str(session.get("file", "Unknown"))
    )
    logger.debug(
        f"▶️ Start Replay: Session={session_name}, Index={session['current_index']}, Messages={len(session['messages'])}"
    )

    # Einfache Lösung: Replay direkt starten (ohne Threading)
    st.success("▶️ Replay gestartet")
    logger.debug("▶️ Replay gestartet")


def pause_replay():
    """Replay pausieren"""
    if "loaded_session" in st.session_state:
        st.session_state.loaded_session["is_playing"] = False
        logger.debug("⏸️ Replay pausiert")
        st.info("⏸️ Replay pausiert")


def stop_replay():
    """Replay stoppen"""
    if "loaded_session" in st.session_state:
        session = st.session_state.loaded_session
        session["is_playing"] = False
        session["current_index"] = 0
        logger.debug("⏹️ Replay gestoppt")
        st.info("⏹️ Replay gestoppt")


def reset_replay():
    """Replay zurücksetzen"""
    if "loaded_session" in st.session_state:
        session = st.session_state.loaded_session
        session["is_playing"] = False
        session["current_index"] = 0
        logger.debug("🔄 Replay zurückgesetzt")
        st.info("🔄 Replay zurückgesetzt")


def replay_worker(session_data):
    """Replay Worker Thread"""
    # Session-Daten als Parameter übergeben (Thread-sicher)
    messages = session_data["messages"]
    current_index = session_data["current_index"]
    speed = session_data["speed"]
    loop = session_data["loop"]

    logger.debug(f"🚀 Replay Worker gestartet: {len(messages)} Nachrichten, Index: {current_index}, Speed: {speed}x")

    while current_index < len(messages):
        msg = messages[current_index]
        logger.debug(f"📤 Sende Nachricht {current_index + 1}/{len(messages)}: {msg['topic']}")

        # Nachricht senden
        if send_replay_message(msg["topic"], msg["payload"]):
            current_index += 1
            logger.debug(f"✅ Nachricht {current_index}/{len(messages)} gesendet")
        else:
            logger.error(f"❌ Fehler beim Senden von Nachricht {current_index + 1}")
            break

        # Warten bis zur nächsten Nachricht
        if current_index < len(messages):
            try:
                current_time = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
                next_msg = messages[current_index]
                next_time = datetime.fromisoformat(next_msg["timestamp"].replace("Z", "+00:00"))
                time_diff = (next_time - current_time).total_seconds()

                sleep_time = time_diff / speed
                if sleep_time > 0:
                    logger.debug(f"⏳ Warte {sleep_time:.2f}s bis zur nächsten Nachricht")
                    time.sleep(sleep_time)
            except Exception as e:
                logger.warning(f"⏳ Fallback Wartezeit: {e}")
                time.sleep(1.0 / speed)

    logger.debug(f"🏁 Replay Worker beendet: {current_index}/{len(messages)} Nachrichten gesendet")

    # Loop oder beenden
    try:
        if "loaded_session" in st.session_state:
            if loop and st.session_state.loaded_session.get("is_playing", False):
                logger.debug("🔄 Loop: Starte von vorne")
                st.session_state.loaded_session["current_index"] = 0
                replay_worker()
            else:
                logger.debug("⏹️ Replay beendet")
                st.session_state.loaded_session["is_playing"] = False
    except Exception as e:
        logger.error(f"❌ Loop/Ende Fehler: {e}")
        pass


def send_replay_message(topic, payload):
    """Replay-Nachricht senden - wird jetzt vom ReplayController gehandhabt"""
    # Diese Funktion wird nicht mehr verwendet, da der ReplayController
    # jetzt direkt mit dem persistenten MQTT-Client arbeitet
    logger.debug(f"📤 Replay-Nachricht: {topic} → {payload[:50]}...")
    return True
