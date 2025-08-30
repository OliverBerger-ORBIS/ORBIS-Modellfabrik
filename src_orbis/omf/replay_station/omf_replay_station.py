#!/usr/bin/env python3
"""
OMF Replay Station - Lokaler MQTT-Broker für Session-Replay
Version: 3.0.0
"""

import logging
import os
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

import paho.mqtt.client as mqtt_client
import streamlit as st


class SessionPlayer:
    """Session-Player für MQTT-Nachrichten-Replay"""

    def __init__(self, broker_client: mqtt_client.Client):
        self.broker_client = broker_client
        self.messages = []
        self.current_index = 0
        self.start_time = None
        self.is_playing = False
        self.speed = 1.0
        self.loop = False

    def load_session(self, session_file: str) -> bool:
        """Session-Datei laden und parsen"""
        try:
            if self._is_sqlite_session(session_file):
                return self._load_sqlite_session(session_file)
            elif self._is_log_session(session_file):
                return self._load_log_session(session_file)
            else:
                st.error(f"Unbekanntes Session-Format: {session_file}")
                return False
        except Exception as e:
            st.error(f"Fehler beim Laden der Session: {e}")
            return False

    def _is_sqlite_session(self, filename: str) -> bool:
        """Prüft ob es sich um eine SQLite-Session handelt"""
        return filename.endswith(".db")

    def _is_log_session(self, filename: str) -> bool:
        """Prüft ob es sich um eine Log-Session handelt"""
        return filename.endswith(".log")

    def _load_sqlite_session(self, session_file: str) -> bool:
        """SQLite-Session laden"""
        try:
            conn = sqlite3.connect(session_file)
            cursor = conn.cursor()

            # Überprüfe Datenbankstruktur
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            st.info(f"📋 Verfügbare Tabellen: {tables}")

            if "mqtt_messages" not in tables:
                st.error("❌ Tabelle 'mqtt_messages' nicht gefunden!")
                return False

            # Nachrichten mit Timestamps laden
            cursor.execute(
                """
                SELECT topic, payload, timestamp
                FROM mqtt_messages
                ORDER BY timestamp ASC
            """
            )

            self.messages = []
            for row in cursor.fetchall():
                topic, payload, timestamp = row
                self.messages.append(
                    {
                        "topic": topic,
                        "payload": payload,
                        "timestamp": datetime.fromisoformat(timestamp),
                    }
                )

            conn.close()
            st.success(f"✅ {len(self.messages)} Nachrichten aus SQLite-Session geladen")
            return True

        except Exception as e:
            st.error(f"Fehler beim Laden der SQLite-Session: {e}")
            st.info("💡 **Debug-Info:**")
            st.info(f"- Datei: {session_file}")
            st.info(f"- Datei existiert: {os.path.exists(session_file)}")
            if os.path.exists(session_file):
                st.info(f"- Dateigröße: {os.path.getsize(session_file)} Bytes")
            return False

    def _load_log_session(self, session_file: str) -> bool:
        """Log-Session laden"""
        try:
            self.messages = []
            with open(session_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        # Einfaches Log-Format: timestamp|topic|payload
                        parts = line.strip().split("|", 2)
                        if len(parts) == 3:
                            timestamp_str, topic, payload = parts
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str)
                                self.messages.append(
                                    {
                                        "topic": topic,
                                        "payload": payload,
                                        "timestamp": timestamp,
                                    }
                                )
                            except ValueError:
                                continue

            st.success(f"✅ {len(self.messages)} Nachrichten aus Log-Session geladen")
            return True

        except Exception as e:
            st.error(f"Fehler beim Laden der Log-Session: {e}")
            return False

    def start_replay(self, speed: float = 1.0, loop: bool = False):
        """Replay starten"""
        if not self.messages:
            st.warning("❌ Keine Nachrichten zum Abspielen")
            return

        self.speed = speed
        self.loop = loop
        self.current_index = 0
        self.start_time = datetime.now()
        self.is_playing = True

        # Replay in separatem Thread starten
        thread = threading.Thread(target=self._replay_thread)
        thread.daemon = True
        thread.start()

        st.success(f"▶️ Replay gestartet ({len(self.messages)} Nachrichten, Speed: {speed}x)")

    def _replay_thread(self):
        """Replay-Thread für asynchrone Nachrichten-Wiedergabe"""
        while self.is_playing and self.current_index < len(self.messages):
            if self.current_index == 0:
                # Erste Nachricht sofort senden
                self._send_message(self.messages[0])
                self.current_index = 1
                last_timestamp = self.messages[0]["timestamp"]
            else:
                # Zeitliche Abstände zwischen Nachrichten berechnen
                current_msg = self.messages[self.current_index]
                previous_msg = self.messages[self.current_index - 1]

                time_diff = (current_msg["timestamp"] - previous_msg["timestamp"]).total_seconds()
                adjusted_time = time_diff / self.speed

                time.sleep(adjusted_time)

                if self.is_playing:
                    self._send_message(current_msg)
                    self.current_index += 1

            # Loop-Check
            if self.loop and self.current_index >= len(self.messages):
                self.current_index = 0
                st.info("🔄 Replay-Loop: Neustart")

        self.is_playing = False
        st.info("⏹️ Replay beendet")

    def _send_message(self, message: Dict):
        """Nachricht über MQTT-Broker senden"""
        try:
            topic = message["topic"]
            payload = message["payload"]

            # Nachricht an Broker senden
            result = self.broker_client.publish(topic, payload, qos=1)

            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                logging.info(f"📤 Replay: {topic} → {payload[:50]}...")
            else:
                logging.error(f"❌ Replay-Fehler: {result.rc}")

        except Exception as e:
            logging.error(f"❌ Fehler beim Senden der Replay-Nachricht: {e}")

    def pause_replay(self):
        """Replay pausieren"""
        self.is_playing = False
        st.info("⏸️ Replay pausiert")

    def stop_replay(self):
        """Replay stoppen"""
        self.is_playing = False
        self.current_index = 0
        st.info("⏹️ Replay gestoppt")

    def get_progress(self) -> float:
        """Fortschritt in Prozent"""
        if not self.messages:
            return 0.0
        return (self.current_index / len(self.messages)) * 100.0


class LocalMQTTBroker:
    """Lokaler MQTT-Broker für Replay-Station (Echter MQTT-Broker)"""

    def __init__(self, port: int = 1884):
        self.port = port
        self.is_running = False
        self.broker_process = None
        self.subscribers = {}  # topic -> list of callbacks

    def start(self):
        """MQTT-Broker starten"""
        try:
            import socket
            import subprocess
            import time

            # Prüfen ob Port bereits belegt ist
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", self.port))
            sock.close()

            if result == 0:
                # Port ist bereits belegt - Broker läuft bereits
                self.is_running = True
                logging.info(f"✅ MQTT-Broker läuft bereits auf Port {self.port}")
                return True

            # Mosquitto-Broker starten
            self.broker_process = subprocess.Popen(["mosquitto", "-p", str(self.port), "-v"])  # Verbose logging

            # Kurz warten, bis Broker gestartet ist
            time.sleep(3)

            if self.broker_process.poll() is None:  # Prozess läuft noch
                self.is_running = True
                logging.info(f"✅ MQTT-Broker gestartet auf Port {self.port}")
                return True
            else:
                logging.error("❌ MQTT-Broker konnte nicht gestartet werden")
                return False

        except Exception as e:
            logging.error(f"❌ Fehler beim Starten des MQTT-Brokers: {e}")
            return False

    def stop(self):
        """MQTT-Broker stoppen"""
        if self.broker_process:
            self.broker_process.terminate()
            self.broker_process.wait()
        self.is_running = False
        logging.info("🛑 MQTT-Broker gestoppt")

    def publish(self, topic: str, payload: str, qos: int = 1):
        """Nachricht veröffentlichen"""
        if self.is_running:
            try:
                import subprocess

                # Nachricht über mosquitto_pub senden
                result = subprocess.run(
                    [
                        "mosquitto_pub",
                        "-h",
                        "localhost",
                        "-p",
                        str(self.port),
                        "-t",
                        topic,
                        "-m",
                        payload,
                        "-q",
                        str(qos),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logging.info(f"📤 Broker: {topic} → {payload[:50]}...")
                    return type("MockResult", (), {"rc": 0})()  # Success
                else:
                    logging.error(f"❌ Broker-Fehler: {result.stderr}")
                    return type("MockResult", (), {"rc": 1})()
            except Exception as e:
                logging.error(f"❌ Fehler beim Senden: {e}")
                return type("MockResult", (), {"rc": 1})()
        else:
            return type("MockResult", (), {"rc": 1})()  # Error


def show_replay_controls(session_player: SessionPlayer):
    """Replay-Kontrollen anzeigen"""
    st.markdown("### 🎮 Replay-Kontrollen")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ Play", disabled=session_player.is_playing):
            speed = st.session_state.get("replay_speed", 1.0)
            loop = st.session_state.get("replay_loop", False)
            session_player.start_replay(speed, loop)

    with col2:
        if st.button("⏸️ Pause", disabled=not session_player.is_playing):
            session_player.pause_replay()

    with col3:
        if st.button("⏹️ Stop"):
            session_player.stop_replay()

    # Replay-Einstellungen
    st.markdown("#### ⚙️ Replay-Einstellungen")

    col_speed, col_loop = st.columns(2)

    with col_speed:
        speed = st.slider("🏃 Speed", 0.1, 5.0, 1.0, 0.1)
        st.session_state.replay_speed = speed

    with col_loop:
        loop = st.checkbox("🔄 Loop", value=False)
        st.session_state.replay_loop = loop

    # Fortschritt
    if session_player.messages:
        progress = session_player.get_progress()
        st.progress(progress / 100.0)
        st.info(f"📊 Fortschritt: {progress:.1f}% ({session_player.current_index}/{len(session_player.messages)})")


def main():
    """Hauptfunktion der OMF Replay Station"""

    st.set_page_config(
        page_title="OMF Replay Station",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.title("🎬 OMF Replay Station")
    st.markdown("Lokaler MQTT-Broker für Session-Replay der Modellfabrik")

    # MQTT-Broker initialisieren und sofort starten
    if "mqtt_broker" not in st.session_state:
        st.session_state.mqtt_broker = LocalMQTTBroker(port=1884)

    # Broker starten (immer, auch wenn bereits initialisiert)
    if not st.session_state.mqtt_broker.is_running:
        if st.session_state.mqtt_broker.start():
            st.success("✅ Lokaler MQTT-Broker gestartet (Port 1884)")
        else:
            st.error("❌ Fehler beim Starten des MQTT-Brokers")
            return

    # Session-Player initialisieren
    if "session_player" not in st.session_state:
        st.session_state.session_player = SessionPlayer(st.session_state.mqtt_broker)

    session_player = st.session_state.session_player

    # Session-Auswahl
    st.markdown("### 📁 Session-Auswahl")

    # Verfügbare Sessions finden
    session_files = []

    # SQLite-Sessions aus mqtt-data/sessions
    sqlite_dir = Path("mqtt-data/sessions")
    if sqlite_dir.exists():
        # Nur aps_persistent_traffic_*.db Dateien
        session_files.extend(list(sqlite_dir.glob("aps_persistent_traffic_*.db")))

    # Log-Sessions aus mqtt-data/sessions
    if sqlite_dir.exists():
        # Nur aps_persistent_traffic_*.log Dateien
        session_files.extend(list(sqlite_dir.glob("aps_persistent_traffic_*.log")))

    if not session_files:
        st.warning("❌ Keine Session-Dateien gefunden")
        st.info("💡 Legen Sie Session-Dateien in `mqtt-data/sessions/` oder `mqtt-data/logs/` ab")
        return

    # Session-Auswahl
    selected_session = st.selectbox("Session auswählen:", session_files, format_func=lambda x: x.name)

    if selected_session and st.button("📂 Session laden"):
        with st.spinner("🔄 Session wird geladen..."):
            if session_player.load_session(str(selected_session)):
                st.session_state.current_session = selected_session
                st.success(f"✅ Session geladen: {selected_session.name}")
                st.info(f"📊 {len(session_player.messages)} Nachrichten gefunden")
            else:
                st.error(f"❌ Fehler beim Laden der Session: {selected_session.name}")

    # Replay-Kontrollen
    if hasattr(session_player, "messages"):
        if session_player.messages:
            show_replay_controls(session_player)
        else:
            st.warning("⚠️ Keine Nachrichten in der geladenen Session gefunden")
            st.info("💡 Versuchen Sie eine andere Session oder prüfen Sie das Session-Format")
    else:
        st.info("📂 Laden Sie zuerst eine Session, um Replay-Kontrollen zu sehen")

    # Status-Anzeige
    st.markdown("---")
    st.markdown("### 📊 Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "MQTT-Broker",
            "🟢 Aktiv" if st.session_state.mqtt_broker.is_running else "🔴 Inaktiv",
        )

    with col2:
        if hasattr(session_player, "messages"):
            st.metric("Nachrichten", len(session_player.messages))
        else:
            st.metric("Nachrichten", 0)

    with col3:
        st.metric("Replay-Status", "▶️ Aktiv" if session_player.is_playing else "⏸️ Pausiert")

    # Dashboard-Integration Info
    st.markdown("---")
    st.markdown("### 🔗 Dashboard-Integration")

    st.info(
        """
    **So verbinden Sie das OMF Dashboard mit der Replay-Station:**

    1. **MQTT-Client im Dashboard konfigurieren:**
       - Host: `localhost`
       - Port: `1884`

    2. **Replay-Station starten** (diese Anwendung)

    3. **Session laden und Replay starten**

    4. **Dashboard zeigt Replay-Nachrichten** wie echte MQTT-Nachrichten
    """
    )

    # Auto-refresh für Status-Updates
    if session_player.is_playing:
        time.sleep(0.5)
        st.rerun()


if __name__ == "__main__":
    main()
