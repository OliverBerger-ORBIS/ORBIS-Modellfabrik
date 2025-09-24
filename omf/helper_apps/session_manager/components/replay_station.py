from omf.dashboard.tools.path_constants import PROJECT_ROOT

"""
Replay Station Komponente
Funktionalität wie alte Replay Station - MQTT-Nachrichten für Tests senden
"""

import json
import logging
import re
import sqlite3
import subprocess
import time
import threading
from dataclasses import dataclass
from typing import List, Tuple, Optional, Protocol
from datetime import datetime
from pathlib import Path

import streamlit as st

from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.utils.ui_refresh import RerunController

# Logging konfigurieren - Verzeichnis sicherstellen
# Log-Verzeichnis erstellen falls nicht vorhanden
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_dir / 'session_manager.log'), logging.StreamHandler()],
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
    Thread-sicherer MQTT-Replay-Controller.
    - Keinerlei Streamlit-Aufrufe im Thread!
    - Versendet Nachrichten per mosquitto_pub.
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
            # Publish (ohne Streamlit!)
            try:
                payload_str = item.payload if isinstance(item.payload, (bytes, bytearray)) else str(item.payload).encode("utf-8")
                subprocess.run(
                    [
                        "mosquitto_pub",
                        "-h", self.host,
                        "-p", str(self.port),
                        "-t", item.topic,
                        "-m", payload_str,
                        "-q", str(item.qos),
                        "-i", "session_manager_replay_station",
                    ],
                    capture_output=True,
                    text=False,
                    timeout=5,
                )
            except Exception:
                pass  # Logging optional extern
            # Index vorrücken
            with self._lock:
                self._idx += 1

# Einfache Factory, die genau EINE Controller-Instanz je Broker hält
def _get_replay_controller(mqtt_host: str, mqtt_port: int) -> ReplayController:
    key = "_replay_controller"
    rc: Optional[ReplayController] = st.session_state.get(key)
    if rc is None or rc.host != mqtt_host or int(rc.port) != int(mqtt_port):
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
    from omf.helper_apps.session_manager.components.settings_manager import SettingsManager

    settings_manager = SettingsManager()
    mqtt_settings = settings_manager.get_mqtt_broker_settings()
    session_directory = settings_manager.get_session_directory()

    # Verbindungsstatus anzeigen
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔌 MQTT Verbindung")
        st.info(f"**Broker:** {mqtt_settings['host']}:{mqtt_settings['port']}")
        st.info(f"**QoS:** {mqtt_settings['qos']} | **Timeout:** {mqtt_settings['timeout']}s")

        if 'mqtt_connected' not in st.session_state:
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
            test_mqtt_connection(mqtt_settings['host'], mqtt_settings['port'], rerun_controller)

    with col2:
        if st.button("🔌 Verbindung trennen", key="disconnect_mqtt"):
            logger.debug("🔌 User klickt: Verbindung trennen")
            disconnect_mqtt(rerun_controller)

    # Session State für MQTT Parameter speichern
    st.session_state.mqtt_host = mqtt_settings['host']
    st.session_state.mqtt_port = mqtt_settings['port']
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
        st.info(f"💡 Legen Sie SQLite-Dateien (.db) in `{session_directory}/` ab")
        st.info("ℹ️ **Hinweis:** Nur .db Dateien werden für Replay unterstützt")
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

                # Session laden
                if st.button("📂 Session laden"):
                    logger.debug(f"📂 User klickt: Session laden - {selected_session.name}")
                    load_session(selected_session, replay_ctrl)

                # Replay-Kontrollen (wenn Session geladen)
                if 'loaded_session' in st.session_state and st.session_state.loaded_session:
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
    """MQTT Verbindung testen mit mosquitto_pub"""
    try:
        result = subprocess.run(
            ["mosquitto_pub", "-h", host, "-p", str(port), "-t", "test/connection", "-m", "test", "-q", "1", "-i", "session_manager_replay_station"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            st.session_state.mqtt_connected = True
            st.success(f"✅ MQTT Broker erreichbar: {host}:{port}")
            rerun_controller.request_rerun()  # UI sofort aktualisieren
            return True
        else:
            st.error(f"❌ MQTT Broker nicht erreichbar: {result.stderr}")
            st.session_state.mqtt_connected = False
            rerun_controller.request_rerun()  # UI sofort aktualisieren
            return False
    except Exception as e:
        st.error(f"❌ Verbindung fehlgeschlagen: {e}")
        st.session_state.mqtt_connected = False
        rerun_controller.request_rerun()  # UI sofort aktualisieren
        return False


def disconnect_mqtt(rerun_controller: RerunController):
    """MQTT Verbindung trennen"""
    st.session_state.mqtt_connected = False
    st.success("✅ Verbindung getrennt")
    rerun_controller.request_rerun()  # UI sofort aktualisieren


def send_test_message(topic, payload):
    """Test-Nachricht mit mosquitto_pub senden"""
    try:
        result = subprocess.run(
            [
                "mosquitto_pub",
                "-h",
                st.session_state.mqtt_host,
                "-p",
                str(st.session_state.mqtt_port),
                "-t",
                topic,
                "-m",
                json.dumps(payload),
                "-q",
                "1",
                "-i",
                "session_manager_replay_station",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            st.session_state.mqtt_connected = True  # Verbindung bestätigen
            st.success(f"📤 Nachricht gesendet: {topic}")
        else:
            st.session_state.mqtt_connected = False
            st.error(f"❌ Fehler beim Senden: {result.stderr}")
    except Exception as e:
        st.session_state.mqtt_connected = False
        st.error(f"❌ Fehler beim Senden: {e}")


# Session Replay Funktionen
def get_session_files(session_directory: str = "data/omf-data/sessions"):
    """Session-Dateien aus konfiguriertem Verzeichnis laden - nur .db Dateien"""
    logger.debug(f"🔍 get_session_files: Suche in {session_directory}")

    # Moderne Paket-Struktur - State of the Art
    if not Path(session_directory).is_absolute():
        # Projekt-Root-relative Pfade für Nutz-Daten verwenden
        # Von omf/helper_apps/session_manager/components/ -> Projekt-Root
        project_root = PROJECT_ROOT
        session_dir = project_root / session_directory
    else:
        session_dir = Path(session_directory)

    logger.debug(f"📁 Verzeichnis existiert: {session_dir.exists()}")
    logger.debug(f"📁 Absoluter Pfad: {session_dir.absolute()}")

    if not session_dir.exists():
        logger.warning(f"❌ Verzeichnis existiert nicht: {session_dir.absolute()}")
        return []

    # Nur SQLite-Dateien finden (Replay Station kann nur .db Dateien verarbeiten)
    session_files = list(session_dir.glob("*.db"))

    logger.debug(f"📊 Gefundene .db Dateien: {len(session_files)}")

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
    """Session laden und in Session State speichern"""
    try:
        if session_file.suffix == ".db":
            messages = load_sqlite_session(session_file)
        else:
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
                "is_playing": False,   # UI-Flag; Controller ist maßgeblich
                "speed": 1.0,
                "loop": False,
            }
            st.success(f"✅ Session '{session_file.name}' geladen ({len(messages)} Nachrichten)")
        else:
            st.error(f"❌ Session '{session_file.name}' konnte nicht geladen werden")
    except Exception as e:
        st.error(f"❌ Fehler beim Laden: {e}")


def load_sqlite_session(session_file):
    """SQLite Session laden"""
    try:
        conn = sqlite3.connect(session_file)
        cursor = conn.cursor()

        cursor.execute("SELECT topic, payload, timestamp FROM mqtt_messages ORDER BY timestamp")
        rows = cursor.fetchall()

        messages = []
        for row in rows:
            topic, payload, timestamp = row
            if topic and payload:
                messages.append({"topic": topic, "payload": payload, "timestamp": timestamp})

        conn.close()
        return messages
    except Exception:
        return []


def load_log_session(session_file):
    """Log Session laden"""
    try:
        messages = []
        with open(session_file) as f:
            for line in f:
                line = line.strip()
                if line and "|" in line:
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        timestamp, topic, payload = parts
                        if topic.strip() and payload.strip():
                            messages.append(
                                {"topic": topic.strip(), "payload": payload.strip(), "timestamp": timestamp.strip()}
                            )
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
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"▶️ User klickt: Play/Resume - Session: {session_name}")
            # Controller starten (mit aktueller Geschwindigkeit)
            replay_ctrl.play(speed=session.get("speed", 1.0))
            session["is_playing"] = True
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col2:
        if st.button("⏸️ Pause", key="pause_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"⏸️ User klickt: Pause - Session: {session_name}")
            replay_ctrl.pause()
            session["is_playing"] = False
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col3:
        if st.button("⏹️ Stop", key="stop_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"⏹️ User klickt: Stop - Session: {session_name}")
            replay_ctrl.stop()
            session["is_playing"] = False
            session["current_index"] = 0
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col4:
        if st.button("🔄 Reset", key="reset_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
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
    if 'loaded_session' not in st.session_state:
        logger.error("❌ Start Replay: Keine Session geladen")
        st.error("❌ Keine Session geladen")
        return

    session = st.session_state.loaded_session
    session["is_playing"] = True
    session_name = (
        session.get('file', {}).get('name', 'Unknown')
        if isinstance(session.get('file'), dict)
        else str(session.get('file', 'Unknown'))
    )
    logger.debug(
        f"▶️ Start Replay: Session={session_name}, Index={session['current_index']}, Messages={len(session['messages'])}"
    )

    # Einfache Lösung: Replay direkt starten (ohne Threading)
    st.success("▶️ Replay gestartet")
    logger.debug("▶️ Replay gestartet")


def pause_replay():
    """Replay pausieren"""
    if 'loaded_session' in st.session_state:
        st.session_state.loaded_session["is_playing"] = False
        logger.debug("⏸️ Replay pausiert")
        st.info("⏸️ Replay pausiert")


def stop_replay():
    """Replay stoppen"""
    if 'loaded_session' in st.session_state:
        session = st.session_state.loaded_session
        session["is_playing"] = False
        session["current_index"] = 0
        logger.debug("⏹️ Replay gestoppt")
        st.info("⏹️ Replay gestoppt")


def reset_replay():
    """Replay zurücksetzen"""
    if 'loaded_session' in st.session_state:
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
        if 'loaded_session' in st.session_state:
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
    """Replay-Nachricht senden"""
    try:
        # MQTT-Parameter aus Session State holen
        mqtt_host = st.session_state.get('mqtt_host', 'localhost')
        mqtt_port = st.session_state.get('mqtt_port', 1883)

        result = subprocess.run(
            ["mosquitto_pub", "-h", mqtt_host, "-p", str(mqtt_port), "-t", topic, "-m", payload, "-q", "1", "-i", "session_manager_replay_station"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            logger.debug(f"✅ Replay: {topic} → {payload[:50]}...")
            return True
        else:
            logger.error(f"❌ Replay Fehler: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Replay Exception: {e}")
        return False
