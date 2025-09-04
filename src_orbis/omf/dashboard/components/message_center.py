#!/usr/bin/env python3
"""
OMF Dashboard - Nachrichtenzentrale Component2
Exakte Kopie von message_center.py
Version: 3.0.0 - Ressourcenschonend mit Topic-Kategorien
"""

import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# --- Konfiguration ---
SITE = "ff"  # falls variabel: z. B. aus Settings nehmen

# Topic-Patterns basierend auf topic_config.yml
TOPIC_PATTERNS = {
    "CCU": [
        "ccu/state",
        "ccu/state/flow",
        "ccu/state/status",
        "ccu/state/error",
        "ccu/control",
        "ccu/control/command",
        "ccu/control/order",
        "ccu/status",
        "ccu/status/connection",
        "ccu/status/health",
    ],
    "MODULE": [
        f"module/v1/{SITE}/+/connection",
        f"module/v1/{SITE}/+/state",
        f"module/v1/{SITE}/+/order",
        f"module/v1/{SITE}/+/factsheet",
    ],
    "TXT": [
        "/j1/txt/1/f/i/order",
        "/j1/txt/1/f/i/stock",
        "/j1/txt/1/f/o/order",
        "/j1/txt/1/f/o/stock",
        "/j1/txt/1/c/bme680",
        "/j1/txt/1/i/order",
        "/j1/txt/1/o/order",
    ],
    "Node-RED": [
        f"module/v1/{SITE}/NodeRed/+/connection",
        f"module/v1/{SITE}/NodeRed/+/state",
        f"module/v1/{SITE}/NodeRed/+/factsheet",
        f"module/v1/{SITE}/NodeRed/status",
    ],
    "FTS": ["fts/v1/ff/+/connection", "fts/v1/ff/+/state", "fts/v1/ff/+/order", "fts/v1/ff/+/factsheet"],
}

# Regex für Topic-Parsing
TOPIC_RE = re.compile(r"^(?P<category>ccu|module|txt|fts|node-red)/.*")


@dataclass
class MessageRow:
    """Repräsentiert eine Nachricht mit allen relevanten Informationen"""

    topic: str
    payload: Any
    message_type: str  # "received" oder "sent"
    timestamp: float
    qos: int = 0
    retain: bool = False

    def get_category(self) -> str:
        """Ermittelt die Kategorie basierend auf dem Topic"""
        topic_lower = self.topic.lower()

        if topic_lower.startswith("ccu/"):
            return "CCU"
        elif topic_lower.startswith("module/v1/ff/"):
            if "nodered" in topic_lower:
                return "Node-RED"
            else:
                return "MODULE"
        elif topic_lower.startswith("/j1/txt/"):
            return "TXT"
        elif topic_lower.startswith("fts/"):
            return "FTS"
        else:
            return "Sonstige"

    def get_sub_category(self) -> str:
        """Ermittelt die Sub-Kategorie basierend auf dem Topic"""
        topic_lower = self.topic.lower()

        if "connection" in topic_lower:
            return "Connection"
        elif "state" in topic_lower:
            return "State"
        elif "order" in topic_lower:
            return "Order"
        elif "factsheet" in topic_lower:
            return "Factsheet"
        elif "control" in topic_lower:
            return "Control"
        elif "status" in topic_lower:
            return "Status"
        else:
            return "General"


def _ensure_store():
    """Stellt sicher, dass der Message-Store existiert"""
    if "message_store" not in st.session_state:
        st.session_state["message_store"]: List[MessageRow] = []
    if "message_last_count" not in st.session_state:
        st.session_state["message_last_count"] = 0


def _flatten_for_df(messages: List[MessageRow]) -> pd.DataFrame:
    """Konvertiert MessageRow-Objekte in ein DataFrame"""
    if not messages:
        return pd.DataFrame()

    data = []
    for msg in messages:
        # Timestamp formatieren
        try:
            from datetime import datetime

            timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
        except Exception:
            timestamp = str(msg.timestamp)

        # Payload kürzen
        payload_str = str(msg.payload)
        if len(payload_str) > 100:
            payload_str = payload_str[:100] + "..."

        # Topic kürzen
        topic_short = msg.topic
        if len(topic_short) > 50:
            topic_short = topic_short[:50] + "..."

        data.append(
            {
                "⏰": timestamp,
                "📨": msg.message_type,
                "🏷️": msg.get_category(),
                "📋": msg.get_sub_category(),
                "📡": topic_short,
                "📄": payload_str,
                "🔢": msg.qos,
                "💾": "✓" if msg.retain else "✗",
            }
        )

    df = pd.DataFrame(data)
    if not df.empty:
        # Nach Zeit sortieren (neueste zuerst)
        df = df.sort_values("⏰", ascending=False)

    return df


def _apply_message(message_store: List[MessageRow], msg_data: Dict[str, Any]):
    """Fügt eine neue Nachricht zum Store hinzu"""
    try:
        message_row = MessageRow(
            topic=msg_data.get("topic", ""),
            payload=msg_data.get("payload", ""),
            message_type=msg_data.get("type", "unknown"),
            timestamp=msg_data.get("ts", time.time()),
            qos=msg_data.get("qos", 0),
            retain=msg_data.get("retain", False),
        )

        # Alle Nachrichten speichern (sowohl received als auch sent)
        message_store.append(message_row)

        # Store auf maximale Größe begrenzen (1000 Nachrichten)
        if len(message_store) > 1000:
            message_store.pop(0)

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Nachricht: {e}")


def show_message_center():
    """Nachrichtenzentrale anzeigen - ressourcenschonend mit Topic-Kategorien"""
    st.header("📡 Nachrichtenzentrale")

    # Get MQTT client from session state
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        st.error("❌ MQTT Client nicht verfügbar")
        st.warning("💡 Bitte warten Sie, bis die MQTT-Verbindung hergestellt ist")
        # NICHT return - UI-Elemente trotzdem anzeigen

    # Status wird automatisch aktualisiert - keine UI-Elemente nötig
    st.info("💡 **Nachrichten werden automatisch aus MQTT-Nachrichten geladen**")

    # Filter-Optionen
    st.subheader("🔍 Filter & Einstellungen")
    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

    with col5:
        if st.button("🗑️ Historie löschen", type="secondary", key="clear_history"):
            # Debug: Session State analysieren
            st.info("🔍 **Debug: Session State Analyse**")
            st.info(f"   - Session State Keys: {list(st.session_state.keys())}")
            st.info(f"   - mqtt_client in session_state: {'mqtt_client' in st.session_state}")

            # MQTT-Client neu holen (könnte sich geändert haben)
            current_mqtt_client = st.session_state.get("mqtt_client")
            st.info(f"   - current_mqtt_client: {current_mqtt_client}")

            if current_mqtt_client:
                st.info(f"   - Client Type: {type(current_mqtt_client).__name__}")
                st.info(f"   - Client ID: {id(current_mqtt_client)}")
                st.info(f"   - Hat clear_history: {hasattr(current_mqtt_client, 'clear_history')}")
                st.info(f"   - Hat drain: {hasattr(current_mqtt_client, 'drain')}")
                st.info(f"   - Hat publish: {hasattr(current_mqtt_client, 'publish')}")

                # Erweiterter Debug: Alle verfügbaren Methoden
                st.info("🔍 **Erweiterter Debug: Alle verfügbaren Methoden**")
                all_methods = [method for method in dir(current_mqtt_client) if not method.startswith("_")]
                st.info(f"   - Alle Methoden: {all_methods}")

                # Spezifische Methoden prüfen
                st.info("🔍 **Spezifische Methoden-Prüfung**")
                st.info(
                    f"   - getattr clear_history: {getattr(current_mqtt_client, 'clear_history', 'NICHT_VERFÜGBAR')}"
                )
                st.info(f"   - callable clear_history: {callable(getattr(current_mqtt_client, 'clear_history', None))}")

                if hasattr(current_mqtt_client, "clear_history"):
                    st.info("   ✅ clear_history gefunden - versuche aufzurufen")
                    try:
                        current_mqtt_client.clear_history()
                        st.success("✅ Nachrichten-Historie gelöscht")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Fehler beim Aufrufen von clear_history: {e}")
                else:
                    st.error("❌ MQTT-Client hat keine clear_history Methode")
                    st.info("💡 Das ist ein Code-Problem - die Methode sollte existieren")
            else:
                st.error("❌ MQTT-Client nicht verfügbar")
                st.info("💡 Versuchen Sie es in einigen Sekunden erneut")

    with col1:
        # Nachrichten-Typ Filter
        message_type_filter = st.selectbox("📨 Nachrichten-Typ", options=["Alle", "received", "sent"], index=0)

    with col2:
        # Topic-Kategorie Filter
        topic_categories = ["Alle", "CCU", "MODULE", "TXT", "Node-RED", "FTS"]
        category_filter = st.selectbox("🏷️ Kategorie", options=topic_categories, index=0)

    with col3:
        # Sub-Kategorie Filter
        sub_categories = ["Alle", "Connection", "State", "Order", "Factsheet", "Control", "Status"]
        sub_category_filter = st.selectbox("📋 Sub-Kategorie", options=sub_categories, index=0)

    with col4:
        # Anzahl Nachrichten
        max_messages = st.number_input("📊 Max", min_value=10, max_value=1000, value=200, step=10)

    # Message Store initialisieren
    _ensure_store()

    # Nur NEUE Nachrichten seit letztem Run einarbeiten
    if mqtt_client:  # Nur wenn MQTT-Client verfügbar ist
        try:
            all_messages = mqtt_client.drain()
            start_idx = st.session_state["message_last_count"]
            new_messages = all_messages[start_idx:] if start_idx < len(all_messages) else []

            # Neue Nachrichten verarbeiten
            for msg_data in new_messages:
                _apply_message(st.session_state["message_store"], msg_data)

            st.session_state["message_last_count"] = len(all_messages)

        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Nachrichten: {e}")
            st.info("💡 MQTT-Verbindung wird im Hintergrund wiederhergestellt")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - Nachrichten werden nicht aktualisiert")

    # Nachrichten filtern
    filtered_messages = []
    for msg in st.session_state["message_store"]:
        # Typ-Filter
        if message_type_filter != "Alle" and msg.message_type != message_type_filter:
            continue

        # Kategorie-Filter
        if category_filter != "Alle" and msg.get_category() != category_filter:
            continue

        # Sub-Kategorie-Filter
        if sub_category_filter != "Alle" and msg.get_sub_category() != sub_category_filter:
            continue

        filtered_messages.append(msg)

    # Nach Anzahl begrenzen
    filtered_messages = filtered_messages[-max_messages:]

    # Nachrichten anzeigen
    st.subheader("📨 Nachrichten")

    if filtered_messages:
        # Kompakte Tabellen-Darstellung
        df = _flatten_for_df(filtered_messages)

        # Statistiken
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Gesamt", len(st.session_state["message_store"]))
        with col2:
            st.metric("🔍 Gefiltert", len(filtered_messages))
        with col3:
            received_count = len([m for m in filtered_messages if m.message_type == "received"])
            st.metric("📥 Empfangen", received_count)
        with col4:
            sent_count = len([m for m in filtered_messages if m.message_type == "sent"])
            st.metric("📤 Gesendet", sent_count)

        # Tabelle anzeigen
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "⏰": st.column_config.TextColumn("Zeit", width="small"),
                "📨": st.column_config.TextColumn("Typ", width="small"),
                "🏷️": st.column_config.TextColumn("Kategorie", width="small"),
                "📋": st.column_config.TextColumn("Sub-Kat", width="small"),
                "📡": st.column_config.TextColumn("Topic", width="medium"),
                "📄": st.column_config.TextColumn("Payload", width="large"),
                "🔢": st.column_config.NumberColumn("QoS", width="small"),
                "💾": st.column_config.TextColumn("Retain", width="small"),
            },
            hide_index=True,
            height=400,
        )

        # Filter-Info
        filter_info = (
            f"📊 **{len(filtered_messages)} von {len(st.session_state['message_store'])} "
            f"Nachrichten angezeigt** (gefiltert nach: {message_type_filter}, "
            f"{category_filter}, {sub_category_filter})"
        )
        st.info(filter_info)

    else:
        st.warning("⚠️ Keine Nachrichten entsprechen den aktuellen Filtern")

    # Test section
    st.markdown("---")
    st.subheader("🧪 Test-Bereich")
    with st.form("publish_form", clear_on_submit=False):
        topic = st.text_input("Topic", value="aps/control/example")
        payload = st.text_area("Payload (Text oder JSON)", value='{"cmd": "ping"}', height=120)
        qos = st.selectbox("QoS", options=[0, 1, 2], index=0)
        retain = st.checkbox("Retain", value=False)
        submitted = st.form_submit_button("Senden")
        if submitted:
            data = payload
            try:
                data = json.loads(payload)
            except Exception:
                pass
            result = mqtt_client.publish(topic, data, qos=int(qos), retain=retain)
            if result:
                st.success(f"Nachricht gesendet: {topic}")
        else:
            st.error("Senden fehlgeschlagen.")
