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
                    load_session(selected_session)

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


def load_session(session_file):
    """Session laden und in Session State speichern"""
    try:
        if session_file.suffix == ".db":
            messages = load_sqlite_session(session_file)
        else:
            messages = load_log_session(session_file)

        if messages:
            st.session_state.loaded_session = {
                "file": session_file,
                "messages": messages,
                "current_index": 0,
                "is_playing": False,
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

    st.markdown("#### 🎮 Replay-Kontrollen")

    # Status-Anzeige
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nachrichten", len(session["messages"]))
    with col2:
        st.metric("Aktuell", f"{session['current_index']}/{len(session['messages'])}")
    with col3:
        status = "▶️ Aktiv" if session["is_playing"] else "⏸️ Pausiert"
        st.metric("Status", status)

    # Kontroll-Buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Play/Resume Button - je nach Status
        if session["is_playing"]:
            button_text = "▶️ Playing..."
            button_disabled = True
        elif session["current_index"] > 0 and session["current_index"] < len(session["messages"]):
            button_text = "▶️ Resume"
            button_disabled = False
        else:
            button_text = "▶️ Play"
            button_disabled = False

        if st.button(button_text, disabled=button_disabled, key="play_resume_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"▶️ User klickt: {button_text} - Session: {session_name}")
            start_replay()
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col2:
        if st.button("⏸️ Pause", disabled=not session["is_playing"], key="pause_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"⏸️ User klickt: Pause - Session: {session_name}")
            pause_replay()
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col3:
        if st.button("⏹️ Stop", key="stop_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"⏹️ User klickt: Stop - Session: {session_name}")
            stop_replay()
            rerun_controller.request_rerun()  # Sofortige UI-Aktualisierung

    with col4:
        if st.button("🔄 Reset", key="reset_btn"):
            session_name = (
                session.get('file', {}).get('name', 'Unknown')
                if isinstance(session.get('file'), dict)
                else str(session.get('file', 'Unknown'))
            )
            logger.debug(f"🔄 User klickt: Reset - Session: {session_name}")
            reset_replay()
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

    with col2:
        loop = st.checkbox("🔄 Loop", value=False)
        session["loop"] = loop

    # Fortschrittsbalken
    if len(session["messages"]) > 0:
        progress = (session["current_index"] / len(session["messages"])) * 100
        st.progress(progress / 100.0)
        st.text(f"📊 Fortschritt: {progress:.1f}% ({session['current_index']}/{len(session['messages'])})")
    else:
        st.progress(0.0)
        st.text("📊 Fortschritt: 0.0% (0/0)")

    # Replay Logic (ohne Threading)
    if session["is_playing"] and session["current_index"] < len(session["messages"]):
        # Nächste Nachricht senden
        msg = session["messages"][session["current_index"]]
        logger.debug(f"📤 Sende Nachricht {session['current_index'] + 1}/{len(session['messages'])}: {msg['topic']}")

        if send_replay_message(msg["topic"], msg["payload"]):
            session["current_index"] += 1
            logger.debug(f"✅ Nachricht {session['current_index']}/{len(session['messages'])} gesendet")

            # Original Timing basierend auf Geschwindigkeit
            if session["current_index"] < len(session["messages"]):
                current_msg = session["messages"][session["current_index"]]
                prev_msg = session["messages"][session["current_index"] - 1]

                # Zeitdifferenz zwischen Nachrichten berechnen
                if "timestamp" in current_msg and "timestamp" in prev_msg:
                    try:
                        # Verschiedene Timestamp-Formate unterstützen
                        current_ts_str = current_msg["timestamp"]
                        prev_ts_str = prev_msg["timestamp"]

                        # ISO Format mit Z
                        if current_ts_str.endswith('Z'):
                            current_ts = datetime.fromisoformat(current_ts_str.replace('Z', '+00:00'))
                            prev_ts = datetime.fromisoformat(prev_ts_str.replace('Z', '+00:00'))
                        else:
                            # Standard ISO Format
                            current_ts = datetime.fromisoformat(current_ts_str)
                            prev_ts = datetime.fromisoformat(prev_ts_str)

                        time_diff = (current_ts - prev_ts).total_seconds()

                        # Geschwindigkeit anwenden
                        speed = session.get("speed", 1.0)
                        wait_time = time_diff / speed

                        if wait_time > 0:
                            logger.debug(f"⏳ Warte {wait_time:.3f}s bis zur nächsten Nachricht")
                            time.sleep(wait_time)
                        else:
                            # Negative Zeitdifferenz = Nachrichten zur gleichen Zeit
                            time.sleep(0.01)  # Minimale Wartezeit
                    except Exception as e:
                        logger.warning(f"⚠️ Zeitberechnung fehlgeschlagen: {e}")
                        time.sleep(0.1)  # Fallback
                else:
                    time.sleep(0.1)  # Fallback wenn keine Timestamps
        else:
            logger.error(f"❌ Fehler beim Senden von Nachricht {session['current_index'] + 1}")
            session["is_playing"] = False

    # Auto-Refresh für Live-Updates
    if session["is_playing"]:
        time.sleep(0.1)  # Kürzere Wartezeit für bessere Responsivität
        rerun_controller.request_rerun()


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
