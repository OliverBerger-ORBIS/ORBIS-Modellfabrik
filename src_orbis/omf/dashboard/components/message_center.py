#!/usr/bin/env python3
"""
OMF Dashboard - Nachrichtenzentrale Component
Version: 3.0.0
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List

import paho.mqtt.client as mqtt
import pandas as pd
import streamlit as st


class MessageMonitorService:
    """Service für das Monitoring und Management von MQTT-Nachrichten"""

    def __init__(self):
        """Initialize MessageMonitorService ohne eigenen MQTT-Client"""
        self.sent_messages = []
        self.received_messages = []
        self.max_messages = 1000

    def send_message(self, topic: str, payload: dict, qos: int = 1, retain: bool = False) -> bool:
        """Sende Nachricht über Dashboard MQTT-Client und speichere sie lokal"""
        try:
            # Verwende Dashboard MQTT-Client
            if "mqtt_client" not in st.session_state or not st.session_state.mqtt_client.connected:
                st.warning("⚠️ Dashboard MQTT-Client nicht verbunden")
                return False

            # Sende Nachricht über Dashboard MQTT-Client
            result = st.session_state.mqtt_client.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                # Speichere gesendete Nachricht
                message = {
                    "topic": topic,
                    "payload": payload,
                    "timestamp": datetime.now().isoformat(),
                    "qos": qos,
                    "retain": retain,
                    "type": "sent",
                }
                self.sent_messages.append(message)

                st.success(f"✅ Nachricht erfolgreich gesendet und gespeichert: {topic}")
                return True
            else:
                st.error(f"❌ MQTT-Publish fehlgeschlagen: {result.rc}")
                return False

        except Exception as e:
            st.error(f"❌ Fehler beim Senden der Nachricht: {e}")
            return False

    def add_sent_message(self, topic: str, payload: str, timestamp: datetime = None):
        """Gesendete Nachricht hinzufügen"""
        if timestamp is None:
            timestamp = datetime.now()

        message = {"topic": topic, "payload": payload, "timestamp": timestamp.isoformat(), "type": "sent"}

        self.sent_messages.append(message)
        self._trim_messages()

    def add_received_message(self, topic: str, payload: str, timestamp: datetime = None):
        """Empfangene Nachricht hinzufügen"""
        if timestamp is None:
            timestamp = datetime.now()

        message = {"topic": topic, "payload": payload, "timestamp": timestamp.isoformat(), "type": "received"}

        self.received_messages.append(message)
        self._trim_messages()

    def _trim_messages(self):
        """Nachrichten auf maximale Anzahl beschränken"""
        if len(self.sent_messages) > self.max_messages:
            self.sent_messages = self.sent_messages[-self.max_messages :]

        if len(self.received_messages) > self.max_messages:
            self.received_messages = self.received_messages[-self.max_messages :]

    def get_messages_by_time_range(self, time_range: str = "1h") -> tuple:
        """Nachrichten nach Zeitraum filtern"""
        cutoff_time = self._get_cutoff_time(time_range)

        sent_filtered = [msg for msg in self.sent_messages if datetime.fromisoformat(msg["timestamp"]) >= cutoff_time]

        received_filtered = [
            msg for msg in self.received_messages if datetime.fromisoformat(msg["timestamp"]) >= cutoff_time
        ]

        return sent_filtered, received_filtered

    def _get_cutoff_time(self, time_range: str) -> datetime:
        """Cutoff-Zeit für Zeitraum-Filter berechnen"""
        now = datetime.now()

        if time_range == "15m":
            return now - timedelta(minutes=15)
        elif time_range == "1h":
            return now - timedelta(hours=1)
        elif time_range == "6h":
            return now - timedelta(hours=6)
        elif time_range == "24h":
            return now - timedelta(days=1)
        elif time_range == "7d":
            return now - timedelta(days=7)
        else:
            return now - timedelta(hours=1)  # Default: 1 Stunde

    def get_sent_messages(self) -> List[Dict]:
        """Gesendete Nachrichten abrufen"""
        return self.sent_messages

    def get_received_messages(self) -> List[Dict]:
        """Empfangene Nachrichten abrufen"""
        return self.received_messages

    def clear_sent_messages(self):
        """Gesendete Nachrichten löschen"""
        self.sent_messages.clear()

    def clear_received_messages(self):
        """Empfangene Nachrichten löschen"""
        self.received_messages.clear()

    def get_message_stats(self) -> Dict:
        """Statistiken über Nachrichten abrufen"""
        return {
            "sent_count": len(self.sent_messages),
            "received_count": len(self.received_messages),
            "total_count": len(self.sent_messages) + len(self.received_messages),
        }

    def get_filtered_messages(self, messages: List[Dict], filters: Dict) -> List[Dict]:
        """Nachrichten nach Filtern filtern"""
        filtered = messages

        # Modul-Filter
        if "modules" in filters:
            module_patterns = [f"module/v1/ff/+/+/{module.lower()}" for module in filters["modules"]]
            filtered = [
                msg
                for msg in filtered
                if any(self._topic_matches_pattern(msg["topic"], pattern) for pattern in module_patterns)
            ]

        # Kategorie-Filter
        if "categories" in filters:
            category_patterns = []
            for category in filters["categories"]:
                if category == "CCU":
                    category_patterns.append("ccu/#")
                elif category == "TXT":
                    category_patterns.append("/j1/txt/#")
                elif category == "MODULE":
                    category_patterns.append("module/v1/ff/#")
                elif category == "Node-RED":
                    category_patterns.append("node_red/#")

            filtered = [
                msg
                for msg in filtered
                if any(self._topic_matches_pattern(msg["topic"], pattern) for pattern in category_patterns)
            ]

        # Zeitraum-Filter
        if "time_range" in filters:
            cutoff_time = self._get_cutoff_time(filters["time_range"])
            filtered = [msg for msg in filtered if datetime.fromisoformat(msg["timestamp"]) >= cutoff_time]

        # Topic-Pattern-Filter
        if "topic_pattern" in filters:
            pattern = filters["topic_pattern"]
            filtered = [msg for msg in filtered if self._topic_matches_pattern(msg["topic"], pattern)]

        return filtered

    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """Prüft ob Topic dem Pattern entspricht (einfache Wildcard-Unterstützung)"""
        try:
            # Einfache Wildcard-Implementierung
            if "*" in pattern:
                # Konvertiere Wildcard-Pattern zu Regex
                import re

                regex_pattern = pattern.replace("*", ".*")
                return re.match(regex_pattern, topic) is not None
            else:
                return topic == pattern
        except Exception:
            return topic == pattern

    def test_fts_charge(self) -> bool:
        """Test-Methode für FTS-Charge mit Dashboard MQTT-Client"""
        try:
            # Verwende Dashboard MQTT-Client
            if "mqtt_client" not in st.session_state or not st.session_state.mqtt_client.connected:
                st.warning("⚠️ Dashboard MQTT-Client nicht verbunden")
                return False

            # FTS-Charge Nachricht erstellen
            payload = {
                "serialNumber": "5iO4",
                "orderId": "test-order-123",
                "orderUpdateId": 1,
                "action": {
                    "id": "test-action-456",
                    "command": "CHARGE",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"},
                },
                "timestamp": datetime.now().isoformat(),
            }

            topic = "fts/v1/ff/5iO4/command"

            # Sende Nachricht über Dashboard MQTT-Client
            return self.send_message(topic, payload)

        except Exception as e:
            st.error(f"❌ Fehler beim FTS-Charge Test: {e}")
            return False


def _capture_sent_messages(message_monitor):
    """Callback-Funktion für gesendete Nachrichten"""

    def on_message_sent(topic, payload, qos=1, retain=False):
        message_monitor.add_sent_message(topic, payload)

    return on_message_sent


def _capture_received_messages(message_monitor):
    """Callback-Funktion für empfangene Nachrichten"""

    def on_message_received(topic, payload):
        message_monitor.add_received_message(topic, payload)

    return on_message_received


def show_message_filters() -> Dict:
    """Filter-Bereich für Nachrichten anzeigen"""
    st.markdown("### 🔍 Filter")

    filters = {}

    # Prioritäten-Filter (neue Zeile)
    priority_levels = {
        1: "Critical Control",
        2: "Important Status",
        3: "Normal Info",
        4: "NodeRED Topics",
        5: "High Frequency",
    }

    # Lade gespeicherte Prioritäten-Einstellung
    try:
        from omf.config.omf_config import config

        default_priority = config.get("dashboard.min_priority", 3)
    except Exception:
        default_priority = 3

    min_priority = st.selectbox(
        "📊 Maximale Priorität:",
        [1, 2, 3, 4, 5],
        index=default_priority - 1,  # Index ist 0-basiert
        format_func=lambda x: f"Prio {x}: {priority_levels[x]}",
        help="Zeige Nachrichten mit Priorität 1 bis zur ausgewählten Priorität",
    )
    filters["min_priority"] = min_priority

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
    topic_pattern = st.text_input("🔍 Topic-Suche", help="Nachrichten mit bestimmten Topic-Patterns suchen")
    if topic_pattern:
        filters["topic_pattern"] = topic_pattern

    return filters


def format_timestamp(timestamp) -> str:
    """Timestamp für Anzeige formatieren"""
    try:
        # Handle both datetime objects and float timestamps
        if isinstance(timestamp, float):
            from datetime import datetime

            timestamp = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, str):
            from datetime import datetime

            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        return timestamp.strftime("%H:%M:%S")
    except Exception:
        return str(timestamp)


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

    # Gesendete Nachrichten aus der Steuerung erfassen
    _capture_sent_messages(message_monitor)

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
                # Prüfen ob Nachricht bereits vorhanden (Topic + Timestamp Kombination)
                existing_messages = [(m["topic"], m["timestamp"]) for m in message_monitor.received_messages]
                msg_key = (msg.get("topic", ""), msg.get("timestamp", datetime.now()))
                if msg_key not in existing_messages:
                    message_monitor.add_received_message(
                        topic=msg.get("topic", ""),
                        payload=msg.get("payload", ""),
                        timestamp=msg.get("timestamp", datetime.now()),
                    )

            # Status anzeigen
            st.success(f"🔗 Verbunden mit MQTT-Broker - {len(mqtt_messages)} Nachrichten verfügbar")
        else:
            st.warning("⚠️ Nicht mit MQTT-Broker verbunden")

    except ImportError:
        st.warning("⚠️ MQTT-Client nicht verfügbar")
    except Exception:
        st.error("❌ Fehler bei MQTT-Integration")

    # Filter anzeigen
    filters = show_message_filters()

    # Manueller Refresh-Button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("🔄 Nachrichten aktualisieren", type="primary"):
            st.rerun()

    # Tab-Navigation (Empfangene Nachrichten zuerst)
    tab1, tab2 = st.tabs(["📥 Empfangene Nachrichten", "📤 Gesendete Nachrichten"])

    with tab1:
        # Empfangene Nachrichten filtern und anzeigen
        filtered_received = message_monitor.get_filtered_messages(message_monitor.received_messages, filters)
        show_messages_table(filtered_received, "📥 Empfangene Nachrichten")

    with tab2:
        # Gesendete Nachrichten filtern und anzeigen
        filtered_sent = message_monitor.get_filtered_messages(message_monitor.sent_messages, filters)
        show_messages_table(filtered_sent, "📤 Gesendete Nachrichten")
