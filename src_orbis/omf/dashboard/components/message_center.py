#!/usr/bin/env python3
"""
OMF Dashboard - Nachrichtenzentrale Component
Version: 3.0.0
"""

import json
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

    def add_received_message(self, topic: str, payload: str, timestamp: datetime = None):
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

    def send_message(self, topic: str, payload: dict) -> bool:
        """Nachricht über MQTT senden und in gesendete Nachrichten speichern"""
        try:
            # Den bereits existierenden MQTT-Client direkt aus dem Dashboard verwenden
            mqtt_client = None

            # Versuche den MQTT-Client aus dem Dashboard Session-State zu holen
            if "mqtt_client" in st.session_state:
                mqtt_client = st.session_state.mqtt_client
                st.info("🔍 Verwende MQTT-Client aus Dashboard Session-State")
            else:
                # Fallback: Über get_omf_mqtt_client
                try:
                    from ..tools.mqtt_client import get_omf_mqtt_client

                    mqtt_client = get_omf_mqtt_client()
                    st.info("🔍 Verwende MQTT-Client über get_omf_mqtt_client")
                except ImportError:
                    from src_orbis.omf.tools.mqtt_client import get_omf_mqtt_client

                    mqtt_client = get_omf_mqtt_client()
                    st.info("🔍 Verwende MQTT-Client über absoluten Import")

            # Debug: MQTT-Client Status anzeigen
            st.info(f"🔍 MQTT-Client Status: connected={mqtt_client.is_connected() if mqtt_client else 'None'}")

            # MQTT-Verbindung prüfen
            if mqtt_client and mqtt_client.is_connected():
                # Nachricht über MQTT senden
                st.info(f"📤 Sende Nachricht über MQTT: {topic}")
                success = mqtt_client.publish(topic, payload)

                if success:
                    # Nachricht in gesendete Nachrichten speichern
                    self.add_sent_message(topic, json.dumps(payload) if isinstance(payload, dict) else str(payload))
                    st.success(f"✅ Nachricht erfolgreich über MQTT gesendet: {topic}")
                    return True
                else:
                    st.error(f"❌ Fehler beim MQTT-Versand: {topic}")
                    return False
            else:
                # Mock-Modus: Nachricht nur lokal speichern
                self.add_sent_message(topic, json.dumps(payload) if isinstance(payload, dict) else str(payload))
                st.warning(f"⚠️ MQTT nicht verbunden - Nachricht nur lokal gespeichert: {topic}")
                return True

        except Exception as e:
            st.error(f"❌ Fehler beim Senden der Nachricht: {e}")
            return False

    def _trim_messages(self, messages: List[Dict]):
        """Nachrichten auf maximale Anzahl beschränken"""
        if len(messages) > self.max_messages:
            messages[:] = messages[: self.max_messages]

    def get_filtered_messages(self, messages: List[Dict], filters: Dict) -> List[Dict]:
        """Nachrichten nach Filtern filtern"""
        filtered = messages

        # Prioritäten-Filter (neue Funktion)
        if filters.get("min_priority"):
            filtered = self._filter_by_priority(filtered, filters["min_priority"])

        # Modul-Filter
        if filters.get("modules"):
            filtered = [
                m for m in filtered if any(module.lower() in m["topic"].lower() for module in filters["modules"])
            ]

        # Kategorie-Filter
        if filters.get("categories"):
            filtered = [m for m in filtered if any(cat.lower() in m["topic"].lower() for cat in filters["categories"])]

        # Zeitraum-Filter
        if filters.get("time_range") and filters["time_range"] != "all":
            cutoff_time = self._get_cutoff_time(filters["time_range"])
            filtered = [m for m in filtered if m["timestamp"] >= cutoff_time]

        # Topic-Pattern-Filter
        if filters.get("topic_pattern"):
            pattern = filters["topic_pattern"].lower()
            filtered = [m for m in filtered if pattern in m["topic"].lower()]

        return filtered

    def _filter_by_priority(self, messages: List[Dict], min_priority: int) -> List[Dict]:
        """Filtere Nachrichten nach Priorität (niedrigere Zahlen = höhere Priorität)"""
        # Topic-Prioritäten Mapping
        topic_priorities = {
            # Priority 1: Critical Control (höchste Priorität)
            "module/+/+/+/order": 1,  # Modul-Befehle
            "ccu/order/request": 1,  # CCU-Bestellungen
            "ccu/order/active": 1,  # Aktive Bestellungen
            # Priority 2: Important Status
            "module/+/+/+/state": 2,  # Modul-Status
            "module/+/+/+/connection": 2,  # Modul-Verbindungen
            "ccu/pairing/state": 2,  # CCU-Pairing
            "fts/+/+/+/state": 2,  # FTS-Status
            # Priority 3: Normal Info (Default)
            "module/+/+/+/+": 3,  # Alle anderen Modul-Topics
            "ccu/+/+": 3,  # Alle anderen CCU-Topics
            "fts/+/+/+/+": 3,  # Alle anderen FTS-Topics
            # Priority 4: NodeRED Topics
            "module/+/+/NodeRed/+/+": 4,  # NodeRED-spezifische Topics
            # Priority 5: High Frequency (niedrigste Priorität)
            "/j1/txt/+/i/cam": 5,  # Kamera-Daten
            "/j1/txt/+/i/bme680": 5,  # Sensor-Daten
        }

        def get_topic_priority(topic: str) -> int:
            """Ermittle Priorität für ein Topic"""
            for pattern, priority in topic_priorities.items():
                if self._topic_matches_pattern(topic, pattern):
                    return priority
            return 3  # Default: Normal Info

        # Filtere Nachrichten: Zeige alle mit Priorität <= min_priority (niedrigere Zahlen = höhere Priorität)
        return [m for m in messages if get_topic_priority(m["topic"]) <= min_priority]

    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """Prüfe ob Topic einem Pattern entspricht"""
        import re

        # Konvertiere MQTT-Wildcards zu Regex
        regex_pattern = pattern.replace("+", "[^/]+").replace("#", ".*")

        try:
            return bool(re.match(regex_pattern, topic))
        except Exception:
            return topic == pattern

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


def _capture_sent_messages(message_monitor):
    """Diese Funktion wird nicht mehr benötigt - Nachrichten werden direkt über send_message() gesendet"""
    pass


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
