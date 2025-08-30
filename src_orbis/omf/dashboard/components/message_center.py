#!/usr/bin/env python3
"""
OMF Dashboard - Nachrichtenzentrale Component
Version: 3.0.0
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
import streamlit as st


class MessageMonitorService:
    """Service für Message-Monitoring und -Verwaltung"""

    def __init__(self):
        self.sent_messages = []
        self.received_messages = []
        self.max_messages = 1000  # Maximale Anzahl gespeicherter Nachrichten

    def add_sent_message(self, topic: str, payload: str, timestamp: datetime = None):
        """Gesendete Nachricht hinzufügen"""
        if timestamp is None:
            timestamp = datetime.now()

        message = {
            "timestamp": timestamp,
            "topic": topic,
            "payload": payload,
            "direction": "sent",
        }

        self.sent_messages.insert(0, message)  # Neueste zuerst
        self._trim_messages(self.sent_messages)

    def add_received_message(
        self, topic: str, payload: str, timestamp: datetime = None
    ):
        """Empfangene Nachricht hinzufügen"""
        if timestamp is None:
            timestamp = datetime.now()

        message = {
            "timestamp": timestamp,
            "topic": topic,
            "payload": payload,
            "direction": "received",
        }

        self.received_messages.insert(0, message)  # Neueste zuerst
        self._trim_messages(self.received_messages)

    def _trim_messages(self, messages: List[Dict]):
        """Nachrichten auf maximale Anzahl beschränken"""
        if len(messages) > self.max_messages:
            messages[:] = messages[: self.max_messages]

    def get_filtered_messages(self, messages: List[Dict], filters: Dict) -> List[Dict]:
        """Nachrichten nach Filtern filtern"""
        filtered = messages

        # Modul-Filter
        if filters.get("modules"):
            filtered = [
                m
                for m in filtered
                if any(
                    module.lower() in m["topic"].lower()
                    for module in filters["modules"]
                )
            ]

        # Kategorie-Filter
        if filters.get("categories"):
            filtered = [
                m
                for m in filtered
                if any(
                    cat.lower() in m["topic"].lower() for cat in filters["categories"]
                )
            ]

        # Zeitraum-Filter
        if filters.get("time_range"):
            cutoff_time = self._get_cutoff_time(filters["time_range"])
            filtered = [m for m in filtered if m["timestamp"] >= cutoff_time]

        # Topic-Pattern-Filter
        if filters.get("topic_pattern"):
            pattern = filters["topic_pattern"].lower()
            filtered = [m for m in filtered if pattern in m["topic"].lower()]

        return filtered

    def _get_cutoff_time(self, time_range: str) -> datetime:
        """Cutoff-Zeit für Zeitraum-Filter berechnen"""
        now = datetime.now()

        if time_range == "1h":
            return now - timedelta(hours=1)
        elif time_range == "1d":
            return now - timedelta(days=1)
        elif time_range == "1w":
            return now - timedelta(weeks=1)
        else:
            return now - timedelta(hours=1)  # Default: 1 Stunde


def show_message_filters() -> Dict:
    """Filter-Bereich für Nachrichten anzeigen"""
    st.markdown("### 🔍 Filter")

    filters = {}

    col1, col2, col3 = st.columns(3)

    with col1:
        # Modul-Filter
        available_modules = ["HBW", "FTS", "MILL", "DRILL", "AIQS", "OVEN"]
        selected_modules = st.multiselect(
            "🏭 Module",
            available_modules,
            help="Nachrichten von bestimmten Modulen anzeigen",
        )
        if selected_modules:
            filters["modules"] = selected_modules

    with col2:
        # Kategorie-Filter
        available_categories = ["CCU", "TXT", "MODULE", "Node-RED"]
        selected_categories = st.multiselect(
            "📂 Kategorien",
            available_categories,
            help="Nachrichten von bestimmten Kategorien anzeigen",
        )
        if selected_categories:
            filters["categories"] = selected_categories

    with col3:
        # Zeitraum-Filter
        time_range = st.selectbox(
            "⏰ Zeitraum",
            ["all", "1h", "1d", "1w"],
            format_func=lambda x: {
                "all": "Alle Nachrichten",
                "1h": "Letzte Stunde",
                "1d": "Letzter Tag",
                "1w": "Letzte Woche",
            }[x],
            help="Zeitraum für Nachrichten-Filterung",
        )
        if time_range != "all":
            filters["time_range"] = time_range

    # Topic-Pattern-Filter
    topic_pattern = st.text_input(
        "🔍 Topic-Suche", help="Nachrichten mit bestimmten Topic-Patterns suchen"
    )
    if topic_pattern:
        filters["topic_pattern"] = topic_pattern

    return filters


def format_timestamp(timestamp: datetime) -> str:
    """Timestamp für Anzeige formatieren"""
    return timestamp.strftime("%H:%M:%S")


def format_payload(payload: str) -> str:
    """Payload für Anzeige formatieren"""
    try:
        # Versuche JSON zu parsen
        parsed = json.loads(payload)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        # Fallback: Raw payload
        return str(payload)[:200] + "..." if len(str(payload)) > 200 else str(payload)


def get_topic_friendly_name(topic: str) -> str:
    """Friendly Name für Topic generieren"""
    # Einfache Topic-zu-Name Mapping
    topic_mappings = {
        "ccu": "CCU",
        "txt": "TXT",
        "hbw": "HBW",
        "fts": "FTS",
        "mill": "MILL",
        "drill": "DRILL",
        "aiqs": "AIQS",
        "oven": "OVEN",
    }

    topic_lower = topic.lower()
    for key, name in topic_mappings.items():
        if key in topic_lower:
            return f"{name}: {topic}"

    return topic


def show_messages_table(messages: List[Dict], title: str):
    """Nachrichten-Tabelle anzeigen"""
    st.markdown(f"### {title}")

    if not messages:
        st.info("Keine Nachrichten vorhanden")
        return

    # DataFrame erstellen
    df_data = []
    for msg in messages:
        df_data.append(
            {
                "Zeit": format_timestamp(msg["timestamp"]),
                "Topic": get_topic_friendly_name(msg["topic"]),
                "Payload": format_payload(msg["payload"]),
            }
        )

    df = pd.DataFrame(df_data)

    # Tabelle anzeigen
    st.dataframe(
        df,
        column_config={
            "Zeit": st.column_config.TextColumn("Zeit", width="small"),
            "Topic": st.column_config.TextColumn("Topic", width="medium"),
            "Payload": st.column_config.TextColumn("Payload", width="large"),
        },
        hide_index=True,
        use_container_width=True,
    )

    # Anzahl anzeigen
    st.info(f"Zeige {len(messages)} Nachrichten")


def show_message_center():
    """Haupt-Komponente für Nachrichtenzentrale"""
    st.header("📡 Nachrichtenzentrale")

    # Message Monitor Service initialisieren
    if "message_monitor" not in st.session_state:
        st.session_state.message_monitor = MessageMonitorService()

    message_monitor = st.session_state.message_monitor

    # MQTT-Client Integration
    try:
        from mqtt_client import get_omf_mqtt_client

        mqtt_client = get_omf_mqtt_client()

        # Nachrichten aus MQTT-Client in Message Monitor übertragen
        if mqtt_client and mqtt_client.is_connected():
            # Empfangene Nachrichten aus MQTT-Client holen
            mqtt_messages = mqtt_client.get_message_history()

            # Neue Nachrichten zum Message Monitor hinzufügen
            for msg in mqtt_messages:
                # Prüfen ob Nachricht bereits vorhanden
                existing_topics = [
                    m["topic"] for m in message_monitor.received_messages
                ]
                if msg.get("topic") not in existing_topics:
                    message_monitor.add_received_message(
                        topic=msg.get("topic", ""),
                        payload=msg.get("payload", ""),
                        timestamp=msg.get("timestamp", datetime.now()),
                    )

            # Status anzeigen
            st.success(
                f"🔗 Verbunden mit MQTT-Broker - {len(mqtt_messages)} Nachrichten verfügbar"
            )
        else:
            st.warning("⚠️ Nicht mit MQTT-Broker verbunden")

    except ImportError:
        st.warning("⚠️ MQTT-Client nicht verfügbar")
    except Exception as e:
        st.error(f"❌ Fehler bei MQTT-Integration: {e}")

    # Filter anzeigen
    filters = show_message_filters()

    # Tab-Navigation (Empfangene Nachrichten zuerst)
    tab1, tab2 = st.tabs(["📥 Empfangene Nachrichten", "📤 Gesendete Nachrichten"])

    with tab1:
        # Empfangene Nachrichten filtern und anzeigen
        filtered_received = message_monitor.get_filtered_messages(
            message_monitor.received_messages, filters
        )
        show_messages_table(filtered_received, "📥 Empfangene Nachrichten")

    with tab2:
        # Gesendete Nachrichten filtern und anzeigen
        filtered_sent = message_monitor.get_filtered_messages(
            message_monitor.sent_messages, filters
        )
        show_messages_table(filtered_sent, "📤 Gesendete Nachrichten")

    # Auto-Refresh für MQTT-Updates (nur wenn verbunden)
    try:
        if mqtt_client and mqtt_client.is_connected():
            time.sleep(1)  # Kurze Pause für Updates
            st.rerun()
    except Exception:
        pass  # Ignoriere Refresh-Fehler
