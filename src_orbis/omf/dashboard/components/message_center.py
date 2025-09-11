#!/usr/bin/env python3
"""
OMF Dashboard - Nachrichtenzentrale Component2
Exakte Kopie von message_center.py
Version: 3.0.0 - Ressourcenschonend mit Topic-Kategorien
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

import pandas as pd
import streamlit as st

# Import für Prioritäts-basierte Subscriptions
from src_orbis.omf.dashboard.config.mc_priority import get_all_priority_filters

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


# _ensure_store() Funktion entfernt - verwenden jetzt direkt MQTT-Client _history


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

        # Payload vollständig anzeigen
        payload_str = str(msg.payload)
        # Nicht kürzen - vollständigen Payload anzeigen

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


# _apply_message() Funktion entfernt - verwenden jetzt direkt MQTT-Client _history


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
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 1, 1, 1])

    with col5:
        if st.button("🗑️ Historie löschen", type="secondary", key="clear_history"):
            # Direkt MQTT-Client clear_history aufrufen (REPARIERT)
            current_mqtt_client = st.session_state.get("mqtt_client")

            if current_mqtt_client and hasattr(current_mqtt_client, "clear_history"):
                try:
                    current_mqtt_client.clear_history()
                    st.success("✅ Nachrichten-Historie gelöscht")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Fehler beim Löschen der Historie: {e}")
            else:
                st.error("❌ MQTT-Client nicht verfügbar oder hat keine clear_history Methode")

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

    with col6:
        # Prioritäts-Slider für Message Center
        priority_level = st.slider(
            "🎯 Priorität",
            min_value=1,
            max_value=6,
            value=6,
            help="1=Kritisch, 2=Wichtig, 3=Normal, 4=TXT/Node-RED, 5=Spezifisch, 6=Alle",
        )

    # Prioritäts-basierte MQTT-Subscription für Message Center
    if mqtt_client:  # Nur wenn MQTT-Client verfügbar ist
        try:
            # Für Prioritätsstufe 6: Alle Topics (Wildcard)
            if priority_level >= 6:
                mqtt_client.subscribe("#", qos=1)
                st.success("✅ Alle Topics abonniert (Prioritätsstufe 6)")
            else:
                # Für niedrigere Prioritäten: Spezifische Filter
                priority_filters = get_all_priority_filters(priority_level)
                if priority_filters:
                    mqtt_client.subscribe_many(priority_filters, qos=1)
                    st.success(f"✅ Prioritätsstufe {priority_level} aktiv - {len(priority_filters)} Topics abonniert")
                else:
                    # Fallback: Alle Topics
                    mqtt_client.subscribe("#", qos=1)
                    st.success("✅ Alle Topics abonniert (Fallback)")

            # Nachrichten aus der globalen History holen
            all_messages = list(mqtt_client._history)  # Direkter Zugriff auf _history

            # Nachrichten in MessageRow-Format konvertieren
            message_rows = []
            for msg_data in all_messages:
                message_row = MessageRow(
                    topic=msg_data.get("topic", ""),
                    payload=msg_data.get("payload", {}),
                    message_type=msg_data.get("type", "received"),
                    timestamp=msg_data.get("ts", 0),
                    qos=msg_data.get("qos", 0),
                    retain=msg_data.get("retain", False),
                )
                message_rows.append(message_row)

            # Status-Anzeige
            st.success(f"✅ MQTT-Client verbunden - {len(all_messages)} Nachrichten empfangen")

        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Nachrichten: {e}")
            st.info("💡 MQTT-Verbindung wird im Hintergrund wiederhergestellt")
            message_rows = []
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - Nachrichten werden nicht aktualisiert")
        message_rows = []

    # Nachrichten filtern
    filtered_messages = []
    for msg in message_rows:
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
            st.metric("📊 Gesamt", len(message_rows))
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
                "📄": st.column_config.TextColumn("Payload", width="extra-large"),
                "🔢": st.column_config.NumberColumn("QoS", width="small"),
                "💾": st.column_config.TextColumn("Retain", width="small"),
            },
            hide_index=True,
            height=400,
        )

        # Erweiterte Payload-Anzeige für die letzten 5 Nachrichten
        st.subheader("🔍 Detaillierte Payload-Ansicht (letzte 5 Nachrichten)")
        recent_messages = filtered_messages[-5:] if len(filtered_messages) >= 5 else filtered_messages

        for i, msg in enumerate(reversed(recent_messages)):
            with st.expander(f"📄 Nachricht {len(recent_messages) - i}: {msg.topic}", expanded=False):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"**Zeit:** {datetime.fromtimestamp(msg.timestamp).strftime('%H:%M:%S')}")
                    st.write(f"**Typ:** {msg.message_type}")
                    st.write(f"**QoS:** {msg.qos}")
                    st.write(f"**Retain:** {msg.retain}")
                with col2:
                    st.write("**Vollständiger Payload:**")
                    # Payload dekodieren falls es bytes ist
                    if isinstance(msg.payload, bytes):
                        try:
                            payload_str = msg.payload.decode('utf-8')
                            # Versuche JSON zu parsen
                            try:
                                payload_json = json.loads(payload_str)
                                st.code(json.dumps(payload_json, indent=2, ensure_ascii=False), language="json")
                            except json.JSONDecodeError:
                                # Falls kein JSON, zeige als Text
                                st.code(payload_str, language="text")
                        except UnicodeDecodeError:
                            # Falls nicht UTF-8, zeige als hex
                            st.code(msg.payload.hex(), language="text")
                    else:
                        # Falls bereits ein Python-Objekt
                        st.code(json.dumps(msg.payload, indent=2, ensure_ascii=False), language="json")

        # Filter-Info
        filter_info = (
            f"📊 **{len(filtered_messages)} von {len(message_rows)} "
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
        topic = st.text_input("Topic", value="omf/control/example")
        payload = st.text_area("Payload (Text oder JSON)", value='{"cmd": "do what we want"}', height=120)
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
