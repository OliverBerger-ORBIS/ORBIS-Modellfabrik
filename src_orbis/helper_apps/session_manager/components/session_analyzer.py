"""
Session Analyzer - Core functionality for session data analysis
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import streamlit as st

from src_orbis.omf.tools.topic_manager import OmfTopicManager

logger = logging.getLogger(__name__)


class SessionAnalyzer:
    """Session Analyse mit OMF Topic-Config Integration"""

    def __init__(self):
        self.topic_manager = OmfTopicManager()
        self.session_data = None
        self.messages_df = None

    def load_session_data(self, session_file_path: str) -> bool:
        """Lädt Session-Daten aus einer Log-Datei"""
        try:
            logger.debug(f"Lade Session-Daten: {session_file_path}")
            # Lade Session-Daten (vereinfacht für Demo)
            # In der echten Implementierung würde hier die Session-Datenbank abgefragt
            self.session_data = self._parse_session_file(session_file_path)
            logger.debug(f"Session-Daten erfolgreich geladen: {len(self.session_data['messages'])} Messages")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Laden der Session-Daten: {e}", exc_info=True)
            st.error(f"Fehler beim Laden der Session-Daten: {e}")
            return False

    def _parse_session_file(self, file_path: str) -> Dict:
        """Parst eine Session-Log-Datei (JSON-Format)"""
        logger.debug(f"Parse Session-Datei: {file_path}")

        if file_path == "demo":
            # Mock-Daten für Demo
            return {
                "session_id": "demo_session",
                "start_time": datetime(2024, 1, 15, 10, 30, 0),
                "end_time": datetime(2024, 1, 15, 11, 45, 0),
                "messages": self._generate_mock_messages(),
            }

        # Echte Session-Datei parsen
        try:
            session_path = Path(file_path)
            if not session_path.exists():
                logger.error(f"Session-Datei nicht gefunden: {file_path}")
                return self._generate_mock_messages()

            messages = []
            start_time = None
            end_time = None

            with open(session_path, encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        line = line.strip()
                        if not line:
                            continue

                        # Versuche JSON-Format zu parsen
                        try:
                            # Parse JSON-Format: {"timestamp": "...", "topic": "...", "payload": "..."}
                            data = json.loads(line)

                            if "timestamp" in data and "topic" in data and "payload" in data:
                                # Parse Timestamp
                                timestamp_str = data["timestamp"]
                                if timestamp_str.endswith('Z'):
                                    timestamp_str = timestamp_str[:-1] + '+00:00'
                                elif '+' not in timestamp_str and 'Z' not in timestamp_str:
                                    timestamp_str += '+00:00'

                                timestamp = datetime.fromisoformat(timestamp_str)

                                messages.append(
                                    {
                                        "timestamp": timestamp,
                                        "topic": data["topic"],
                                        "payload": data["payload"],
                                        "qos": data.get("qos", 0),
                                    }
                                )

                                if start_time is None:
                                    start_time = timestamp
                                end_time = timestamp

                        except json.JSONDecodeError:
                            # Fallback: Versuche altes Format [timestamp] topic: payload
                            if ']' in line and ':' in line:
                                timestamp_str = line.split(']')[0][1:]  # Entferne [ und ]
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                                topic_payload = line.split(']')[1].strip()
                                if ':' in topic_payload:
                                    topic, payload = topic_payload.split(':', 1)
                                    topic = topic.strip()
                                    payload = payload.strip()

                                    messages.append(
                                        {"timestamp": timestamp, "topic": topic, "payload": payload, "qos": 0}
                                    )

                                    if start_time is None:
                                        start_time = timestamp
                                    end_time = timestamp

                    except Exception as e:
                        logger.warning(f"Fehler beim Parsen von Zeile {line_num}: {e}")
                        continue

            if not messages:
                logger.warning("Keine gültigen Messages gefunden, verwende Mock-Daten")
                return self._generate_mock_messages()

            logger.debug(f"Session geparst: {len(messages)} Messages, {start_time} bis {end_time}")

            return {
                "session_id": session_path.stem,
                "start_time": start_time,
                "end_time": end_time,
                "messages": sorted(messages, key=lambda x: x["timestamp"]),
            }

        except Exception as e:
            logger.error(f"Fehler beim Parsen der Session-Datei: {e}")
            return self._generate_mock_messages()

    def _generate_mock_messages(self) -> List[Dict]:
        """Generiert Mock-Messages für Demo"""
        import random

        topics = [
            "ccu/state/status",
            "ccu/state/flow",
            "module/v1/ff/SVR3QA0022/state",
            "module/v1/ff/SVR3QA0022/order",
            "module/v1/ff/SVR4H76449/state",
            "fts/v1/ff/5iO4/state",
            "fts/v1/ff/5iO4/order",
            "/j1/txt/1/f/i/stock",
            "/j1/txt/1/f/o/order",
        ]

        messages = []
        start_time = datetime(2024, 1, 15, 10, 30, 0)

        for i in range(200):
            timestamp = start_time + timedelta(seconds=i * 2 + random.randint(0, 5))
            topic = random.choice(topics)
            payload = f"{{'value': {random.randint(0, 100)}, 'timestamp': '{timestamp.isoformat()}'}}"

            messages.append(
                {"timestamp": timestamp, "topic": topic, "payload": payload, "qos": random.choice([0, 1, 2])}
            )

        return sorted(messages, key=lambda x: x["timestamp"])

    def get_available_topics(self, exclude_prefilter: bool = True) -> List[str]:
        """Gibt alle verfügbaren Topics aus der Session zurück"""
        if not self.session_data:
            return []

        topics = set()
        for message in self.session_data["messages"]:
            topics.add(message["topic"])

        # Vorfilter anwenden
        if exclude_prefilter:
            prefilter_topics = self._get_prefilter_topics()
            topics = topics - set(prefilter_topics)

        return sorted(topics)

    def _get_prefilter_topics(self) -> List[str]:
        """Gibt die Vorfilter-Topics zurück (uninteressante Topics)"""
        # Versuche Settings Manager zu verwenden, falls verfügbar
        try:
            import streamlit as st

            if hasattr(st.session_state, 'settings_manager'):
                return st.session_state.settings_manager.get_prefilter_topics()
        except Exception:
            pass

        # Fallback zu Standard-Topics
        return [
            "/j1/txt/1/i/cam",  # Kamera-Daten
            "/j1/txt/1/i/bme",  # BME680-Sensor-Daten
            "/j1/txt/1/c/bme680",  # BME680-Sensor-Daten (andere Schreibweise)
            "/j1/txt/1/c/cam",  # Kamera-Daten (andere Schreibweise)
            "/j1/txt/1/c/ldr",  # LDR-Sensor-Daten
        ]

    def get_message_statistics(self) -> Dict:
        """Gibt Statistiken über die Messages zurück"""
        if not self.session_data:
            return {}

        messages = self.session_data["messages"]
        topics = self.get_available_topics()

        return {
            "total_messages": len(messages),
            "unique_topics": len(topics),
            "start_time": self.session_data["start_time"],
            "end_time": self.session_data["end_time"],
            "duration_minutes": (self.session_data["end_time"] - self.session_data["start_time"]).total_seconds() / 60,
        }
