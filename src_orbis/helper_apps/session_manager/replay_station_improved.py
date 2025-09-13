#!/usr/bin/env python3
"""
Improved Replay Station mit Session Manager Konzepten
Demonstriert die Anwendung von kontrolliertem st.rerun() und zentralem Logging
"""

import logging
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from .logging_utils import get_session_logger
from .rerun_control import get_rerun_controller, request_rerun, execute_pending_rerun


class ImprovedSessionPlayer:
    """Session-Player mit integriertem Logging und Rerun-Kontrolle"""

    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.messages = []
        self.current_index = 0
        self.is_playing = False
        self.replay_thread = None
        self.speed = 1.0
        self.loop = False

        # Logging und Rerun-Kontrolle integrieren
        self.logger = get_session_logger("replay_station", "INFO")
        self.rerun_controller = get_rerun_controller("replay_station")

        self.logger.log_event("SessionPlayer initialized", "INFO", host=broker_host, port=broker_port)

    def load_sqlite_session(self, file_path: str) -> bool:
        """SQLite Session laden mit verbessertem Logging"""
        self.logger.log_event(f"Loading SQLite session: {file_path}", "INFO")

        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()

            # Prüfen ob Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'")
            if not cursor.fetchone():
                error_msg = f"❌ Tabelle 'mqtt_messages' nicht gefunden in {file_path}"
                self.logger.log_warning("SQLite table not found", file_path=file_path)
                st.error(error_msg)
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
                warning_msg = f"⚠️ Session {file_path} enthält keine gültigen Nachrichten"
                self.logger.log_warning("Empty session file", file_path=file_path)
                st.warning(warning_msg)
                st.info("💡 Mögliche Ursachen:")
                st.info("   - Session wurde ohne MQTT-Traffic aufgenommen")
                st.info("   - Alle Nachrichten sind leer oder ungültig")
                st.info("   - Session-Datei ist beschädigt")
                return False
            else:
                success_msg = f"✅ {len(self.messages)} Nachrichten aus SQLite geladen"
                self.logger.log_event("SQLite session loaded successfully", "INFO", messages_count=len(self.messages))
                st.success(success_msg)
                
                # Kontrollierten Rerun anfordern statt direktem st.rerun()
                request_rerun("SQLite-Session wurde geladen", "load_sqlite_session", show_ui_feedback=False)
                return True

        except Exception as e:
            self.logger.log_error(e, f"Failed to load SQLite session: {file_path}")
            st.error("❌ Fehler beim Laden der SQLite Session")
            return False

    def send_message(self, topic: str, payload: str) -> bool:
        """Nachricht über mosquitto_pub senden mit verbessertem Logging"""
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
                # Detailliertes Logging statt nur logger.info()
                self.logger.log_event(
                    "MQTT message sent successfully",
                    "INFO",
                    topic=topic,
                    payload_length=len(payload),
                    broker=f"{self.broker_host}:{self.broker_port}",
                )
                return True
            else:
                self.logger.log_error(
                    Exception(f"mosquitto_pub failed: {result.stderr}"),
                    f"Failed to send message to topic: {topic}",
                )
                return False

        except Exception as e:
            self.logger.log_error(e, f"Exception while sending message to topic: {topic}")
            return False

    def start_replay(self, speed: float = 1.0, loop: bool = False):
        """Replay starten mit kontrolliertem Rerun"""
        if not self.messages:
            warning_msg = "⚠️ Keine Nachrichten zum Abspielen"
            self.logger.log_warning("Cannot start replay - no messages loaded")
            st.warning(warning_msg)
            return

        self.speed = speed
        self.loop = loop
        self.is_playing = True

        # Nur von vorne starten wenn current_index am Ende ist
        if self.current_index >= len(self.messages):
            self.current_index = 0

        # Logging
        self.logger.log_ui_action("replay_started", {"speed": speed, "loop": loop, "message_count": len(self.messages)})

        # Replay in separatem Thread
        self.replay_thread = threading.Thread(target=self._replay_worker)
        self.replay_thread.daemon = True
        self.replay_thread.start()

        st.success("▶️ Replay gestartet")
        
        # Kontrollierten Rerun anfordern
        request_rerun("Replay wurde gestartet", "start_replay")

    def pause_replay(self):
        """Replay pausieren mit kontrolliertem Rerun"""
        self.is_playing = False
        self.logger.log_ui_action("replay_paused", {"current_index": self.current_index})
        st.info("⏸️ Replay pausiert")
        
        # Kontrollierten Rerun anfordern
        request_rerun("Replay wurde pausiert", "pause_replay")

    def stop_replay(self):
        """Replay stoppen mit kontrolliertem Rerun"""
        self.is_playing = False
        old_index = self.current_index
        self.current_index = 0
        
        self.logger.log_ui_action("replay_stopped", {"stopped_at_index": old_index})
        st.info("⏹️ Replay gestoppt")
        
        # Kontrollierten Rerun anfordern
        request_rerun("Replay wurde gestoppt", "stop_replay")

    def _replay_worker(self):
        """Replay Worker Thread mit detailliertem Logging"""
        self.logger.log_event("Replay worker thread started", "INFO")
        
        messages_sent = 0
        start_time = time.time()
        
        while self.is_playing and self.current_index < len(self.messages):
            msg = self.messages[self.current_index]

            # Nachricht senden
            if self.send_message(msg["topic"], msg["payload"]):
                self.current_index += 1
                messages_sent += 1
            else:
                self.logger.log_error(
                    Exception("Message send failed"),
                    f"Failed to send message at index {self.current_index}",
                )
                break

            # Warten bis zur nächsten Nachricht (existing logic)
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

                except Exception:
                    # Fallback: 1 Sekunde warten
                    time.sleep(1.0 / self.speed)

        # Loop oder beenden
        duration = time.time() - start_time
        
        if self.loop and self.is_playing:
            self.logger.log_event(
                "Replay loop completed - restarting",
                "INFO",
                messages_sent=messages_sent,
                duration=duration,
            )
            self.current_index = 0
            self._replay_worker()
        else:
            self.is_playing = False
            self.logger.log_event(
                "Replay completed",
                "INFO",
                messages_sent=messages_sent,
                total_messages=len(self.messages),
                duration=duration,
            )

    def reset_controls(self):
        """Kontrollen zurücksetzen"""
        self.is_playing = False
        self.current_index = 0
        self.speed = 1.0
        self.loop = False
        
        self.logger.log_ui_action("controls_reset")

    def get_progress(self) -> float:
        """Fortschritt in Prozent"""
        if not self.messages:
            return 0.0
        return (self.current_index / len(self.messages)) * 100.0


def main():
    """Hauptfunktion der verbesserten Replay Station"""
    st.set_page_config(page_title="🎬 Improved Replay Station", page_icon="🎬", layout="wide")

    st.title("🎬 Improved Replay Station")
    st.markdown("Demonstriert kontrolliertes st.rerun() Handling und zentrales Logging")

    # Session-Player initialisieren
    if "improved_session_player" not in st.session_state:
        st.session_state.improved_session_player = ImprovedSessionPlayer()

    session_player = st.session_state.improved_session_player

    # Prüfe und führe anstehende Reruns aus - WICHTIG: am Anfang jeder Streamlit-Ausführung
    execute_pending_rerun()

    # Status-Anzeige
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("MQTT Broker", "🟢 localhost:1883")

    with col2:
        st.metric("Nachrichten", len(session_player.messages))

    with col3:
        status = "▶️ Aktiv" if session_player.is_playing else "⏸️ Pausiert"
        st.metric("Replay-Status", status)

    # Session-Auswahl (vereinfacht für Demo)
    st.markdown("### 📁 Session-Auswahl")

    # Verfügbare Sessions finden
    session_files = []
    sqlite_dir = Path("mqtt-data/sessions")
    if sqlite_dir.exists():
        session_files.extend(list(sqlite_dir.glob("aps_persistent_traffic_*.db")))

    if not session_files:
        st.warning("❌ Keine Session-Dateien gefunden")
        st.info("💡 Legen Sie Session-Dateien in `mqtt-data/sessions/` ab")
        return

    # Session-Auswahl
    selected_session = st.selectbox("Session auswählen:", session_files, format_func=lambda x: x.name)

    if selected_session and st.button("📂 Session laden"):
        with st.spinner("🔄 Session wird geladen..."):
            session_player.reset_controls()
            
            if selected_session.suffix == ".db":
                success = session_player.load_sqlite_session(str(selected_session))
                if success:
                    st.session_state.current_session = selected_session

    # Replay-Kontrollen
    if session_player.messages:
        st.markdown("### 🎮 Replay-Kontrollen")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("▶️ Play", disabled=session_player.is_playing):
                session_player.start_replay(speed=1.0, loop=False)

        with col2:
            if st.button("⏸️ Pause", disabled=not session_player.is_playing):
                session_player.pause_replay()

        with col3:
            if st.button("⏹️ Stop"):
                session_player.stop_replay()

        # Fortschrittsbalken
        progress = session_player.get_progress()
        st.progress(progress / 100.0)
        st.text(f"📊 Fortschritt: {progress:.1f}% ({session_player.current_index}/{len(session_player.messages)})")

    # Verbesserungen-Info
    st.markdown("---")
    st.markdown("### 🚀 Verbesserungen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Kontrolliertes st.rerun():**")
        st.info(
            """
        - ✅ Zentrale `request_rerun()` Funktion
        - ✅ Verhindert Rerun-Kaskaden
        - ✅ UI-Feedback bei Reruns
        - ✅ Nachvollziehbare Rerun-Gründe
        """
        )

    with col2:
        st.markdown("**Zentrales Logging:**")
        st.info(
            """
        - ✅ Strukturierte Log-Nachrichten
        - ✅ Separate Developer-Logs
        - ✅ Konfigurierbare Log-Level
        - ✅ Rottierende Log-Dateien
        """
        )

    # Log-Datei Viewer
    st.markdown("### 📄 Live-Logs")
    log_file = Path("logs/replay_station.log")

    if log_file.exists():
        try:
            with open(log_file, encoding="utf-8") as f:
                lines = f.readlines()
            
            if lines:
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                st.code("\n".join(recent_lines), language="text")
            else:
                st.info("Log-Datei ist leer")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Lesen der Log-Datei: {e}")
    else:
        st.info("🔄 Log-Datei wird beim ersten Event erstellt")


if __name__ == "__main__":
    main()