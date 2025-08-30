#!/usr/bin/env python3
"""
OMF Replay Station
Sendet Nachrichten an den MQTT Broker (ohne eigenen Broker zu starten)
"""


import logging
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionPlayer:
    """Session-Player der Nachrichten an den MQTT Broker sendet"""

    def __init__(self, broker_host="localhost", broker_port=1884):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.messages = []
        self.current_index = 0
        self.is_playing = False
        self.replay_thread = None
        self.speed = 1.0
        self.loop = False

    def load_sqlite_session(self, file_path: str) -> bool:
        """SQLite Session laden"""
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'")
            if not cursor.fetchone():
                st.error(f"❌ Tabelle 'mqtt_messages' nicht gefunden in {file_path}")
                return False

            # Nachrichten laden
            cursor.execute("SELECT topic, payload, timestamp FROM mqtt_messages ORDER BY timestamp")
            rows = cursor.fetchall()

            self.messages = []
            for row in rows:
                topic, payload, timestamp = row
                if topic and payload:  # Nur gültige Nachrichten
                    self.messages.append({"topic": topic, "payload": payload, "timestamp": timestamp})

            conn.close()

            if len(self.messages) == 0:
                st.warning(f"⚠️ Session {file_path} enthält keine gültigen Nachrichten")
                st.info("💡 Mögliche Ursachen:")
                st.info("   - Session wurde ohne MQTT-Traffic aufgenommen")
                st.info("   - Alle Nachrichten sind leer oder ungültig")
                st.info("   - Session-Datei ist beschädigt")
                return False
            else:
                st.success(f"✅ {len(self.messages)} Nachrichten aus SQLite geladen")
                return True

        except Exception:
            st.error("❌ Fehler beim Laden der SQLite Session")
            return False

    def load_log_session(self, file_path: str) -> bool:
        """Log Session laden"""
        try:
            self.messages = []
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if line and "|" in line:
                        try:
                            # Format: timestamp | topic | payload
                            parts = line.split("|", 2)
                            if len(parts) == 3:
                                timestamp, topic, payload = parts
                                if topic.strip() and payload.strip():  # Nur gültige Nachrichten
                                    self.messages.append(
                                        {
                                            "topic": topic.strip(),
                                            "payload": payload.strip(),
                                            "timestamp": timestamp.strip(),
                                        }
                                    )
                        except:
                            continue

            if len(self.messages) == 0:
                st.warning(f"⚠️ Session {file_path} enthält keine gültigen Nachrichten")
                st.info("💡 Mögliche Ursachen:")
                st.info("   - Session wurde ohne MQTT-Traffic aufgenommen")
                st.info("   - Alle Nachrichten sind leer oder ungültig")
                st.info("   - Log-Format ist nicht korrekt")
                return False
            else:
                st.success(f"✅ {len(self.messages)} Nachrichten aus Log geladen")
                return True

        except Exception:
            st.error("❌ Fehler beim Laden der Log Session")
            return False

    def send_message(self, topic: str, payload: str) -> bool:
        """Nachricht über mosquitto_pub senden"""
        try:
            result = subprocess.run(
                [
                    "mosquitto_pub",
                    "-h",
                    self.broker_host,
                    "-p",
                    str(self.broker_port),
                    "-t",
                    topic,
                    "-m",
                    payload,
                    "-q",
                    "1",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                logger.info(f"📤 Gesendet: {topic} → {payload[:50]}...")
                return True
            else:
                logger.error(f"❌ Fehler beim Senden: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Fehler beim Senden: {e}")
            return False

    def start_replay(self, speed: float = 1.0, loop: bool = False):
        """Replay starten"""
        if not self.messages:
            st.warning("⚠️ Keine Nachrichten zum Abspielen")
            return

        self.speed = speed
        self.loop = loop
        self.is_playing = True

        # Nur von vorne starten wenn current_index am Ende ist
        if self.current_index >= len(self.messages):
            self.current_index = 0

        # Replay in separatem Thread
        self.replay_thread = threading.Thread(target=self._replay_worker)
        self.replay_thread.daemon = True
        self.replay_thread.start()

        st.success("▶️ Replay gestartet")

    def resume_replay(self):
        """Replay fortsetzen"""
        if not self.messages:
            st.warning("⚠️ Keine Nachrichten zum Abspielen")
            return

        if self.current_index >= len(self.messages):
            st.warning("⚠️ Replay ist bereits beendet")
            return

        self.is_playing = True

        # Replay in separatem Thread
        self.replay_thread = threading.Thread(target=self._replay_worker)
        self.replay_thread.daemon = True
        self.replay_thread.start()

        st.success("▶️ Replay fortgesetzt")

    def _replay_worker(self):
        """Replay Worker Thread"""
        while self.is_playing and self.current_index < len(self.messages):
            msg = self.messages[self.current_index]

            # Nachricht senden
            if self.send_message(msg["topic"], msg["payload"]):
                self.current_index += 1
            else:
                logger.error(f"❌ Fehler beim Senden von Nachricht {self.current_index}")
                break

            # Warten bis zur nächsten Nachricht
            if self.current_index < len(self.messages):
                next_msg = self.messages[self.current_index]
                current_msg = self.messages[self.current_index - 1]

                try:
                    # Zeitdifferenz berechnen
                    current_time = datetime.fromisoformat(current_msg["timestamp"].replace("Z", "+00:00"))
                    next_time = datetime.fromisoformat(next_msg["timestamp"].replace("Z", "+00:00"))
                    time_diff = (next_time - current_time).total_seconds()

                    # Mit Speed-Faktor warten
                    sleep_time = time_diff / self.speed
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                except:
                    # Fallback: 1 Sekunde warten
                    time.sleep(1.0 / self.speed)

        # Loop oder beenden
        if self.loop and self.is_playing:
            self.current_index = 0
            self._replay_worker()
        else:
            self.is_playing = False

    def pause_replay(self):
        """Replay pausieren"""
        self.is_playing = False
        st.info("⏸️ Replay pausiert")

    def stop_replay(self):
        """Replay stoppen"""
        self.is_playing = False
        self.current_index = 0
        st.info("⏹️ Replay gestoppt")

    def reset_controls(self):
        """Kontrollen zurücksetzen (für neue Session)"""
        self.is_playing = False
        self.current_index = 0
        self.speed = 1.0
        self.loop = False

    def get_progress(self) -> float:
        """Fortschritt in Prozent"""
        if not self.messages:
            return 0.0
        return (self.current_index / len(self.messages)) * 100.0


def main():
    st.set_page_config(page_title="🎬 OMF Replay Station", page_icon="🎬", layout="wide")

    st.title("🎬 OMF Replay Station")
    st.markdown("Sendet Nachrichten an den MQTT Broker (Port 1884)")

    # Session-Player initialisieren
    if "session_player" not in st.session_state:
        st.session_state.session_player = SessionPlayer()

    session_player = st.session_state.session_player

    # Status-Anzeige
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("MQTT Broker", "🟢 localhost:1884")

    with col2:
        st.metric("Nachrichten", len(session_player.messages))

    with col3:
        status = "▶️ Aktiv" if session_player.is_playing else "⏸️ Pausiert"
        st.metric("Replay-Status", status)

    # Session-Auswahl
    st.markdown("### 📁 Session-Auswahl")

    # Verfügbare Sessions finden
    session_files = []

    # SQLite-Sessions aus mqtt-data/sessions
    sqlite_dir = Path("mqtt-data/sessions")
    if sqlite_dir.exists():
        session_files.extend(list(sqlite_dir.glob("aps_persistent_traffic_*.db")))

    # Log-Sessions aus mqtt-data/sessions
    if sqlite_dir.exists():
        session_files.extend(list(sqlite_dir.glob("aps_persistent_traffic_*.log")))

    if not session_files:
        st.warning("❌ Keine Session-Dateien gefunden")
        st.info("💡 Legen Sie Session-Dateien in `mqtt-data/sessions/` ab")
        return

    # Session-Auswahl mit Vorschau
    selected_session = st.selectbox("Session auswählen:", session_files, format_func=lambda x: x.name)

    # Session-Info anzeigen
    if selected_session:
        st.info(f"📁 Ausgewählte Session: {selected_session.name}")

        # Session-Größe anzeigen
        try:
            file_size = selected_session.stat().st_size
            st.text(f"📊 Dateigröße: {file_size:,} Bytes")
        except:
            pass

    if selected_session and st.button("📂 Session laden"):
        with st.spinner("🔄 Session wird geladen..."):
            # Kontrollen zurücksetzen vor dem Laden der neuen Session
            session_player.reset_controls()

            if selected_session.suffix == ".db":
                success = session_player.load_sqlite_session(str(selected_session))
            else:
                success = session_player.load_log_session(str(selected_session))

            if success:
                st.session_state.current_session = selected_session
                st.success(f"✅ Session '{selected_session.name}' erfolgreich geladen!")
                st.info("🔄 Kontrollen wurden zurückgesetzt - bereit für neuen Replay!")
            else:
                st.error(f"❌ Session '{selected_session.name}' konnte nicht geladen werden")

    # Replay-Kontrollen
    if session_player.messages:
        st.markdown("### 🎮 Replay-Kontrollen")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Play/Resume Button - je nach Status
            if session_player.is_playing:
                button_text = "▶️ Playing..."
                button_disabled = True
            elif session_player.current_index > 0 and session_player.current_index < len(session_player.messages):
                button_text = "▶️ Resume"
                button_disabled = False
            else:
                button_text = "▶️ Play"
                button_disabled = False

            if st.button(button_text, disabled=button_disabled):
                speed = st.session_state.get("replay_speed", 1.0)
                loop = st.session_state.get("replay_loop", False)

                if session_player.current_index > 0 and session_player.current_index < len(session_player.messages):
                    session_player.resume_replay()
                else:
                    session_player.start_replay(speed, loop)
                st.rerun()  # Sofortige UI-Aktualisierung

        with col2:
            if st.button("⏸️ Pause", disabled=not session_player.is_playing):
                session_player.pause_replay()
                st.rerun()  # Sofortige UI-Aktualisierung

        with col3:
            if st.button("⏹️ Stop"):
                session_player.stop_replay()
                st.rerun()  # Sofortige UI-Aktualisierung

        # Replay-Einstellungen
        st.markdown("#### ⚙️ Replay-Einstellungen")

        col_speed, col_loop = st.columns(2)

        with col_speed:
            speed = st.slider("🏃 Speed", 0.1, 5.0, 1.0, 0.1)
            st.session_state.replay_speed = speed

        with col_loop:
            loop = st.checkbox("🔄 Loop", value=False)
            st.session_state.replay_loop = loop

        # Fortschrittsbalken
        progress = session_player.get_progress()
        st.progress(progress / 100.0)
        st.text(f"📊 Fortschritt: {progress:.1f}% ({session_player.current_index}/{len(session_player.messages)})")

        # Debug-Informationen
        st.info(
            f"🔍 Debug: is_playing={session_player.is_playing}, current_index={session_player.current_index}, total_messages={len(session_player.messages)}"
        )

        # Manueller Refresh-Button für Live-Updates
        if st.button("🔄 Status aktualisieren"):
            st.rerun()

    # Dashboard-Integration Info
    st.markdown("---")
    st.markdown("### 🔗 Dashboard-Integration")

    st.info(
        """
    **So verbinden Sie das OMF Dashboard mit dem Replay-Broker:**

    1. **MQTT Broker läuft bereits** auf Port 1884 ✅

    2. **Dashboard konfigurieren:**
       - MQTT-Modus: "Replay-Broker"
       - Host: `localhost`
       - Port: `1884`

    3. **Session laden und Replay starten** (oben)

    4. **Dashboard zeigt Replay-Nachrichten** in der Nachrichtenzentrale
    """
    )


if __name__ == "__main__":
    main()
