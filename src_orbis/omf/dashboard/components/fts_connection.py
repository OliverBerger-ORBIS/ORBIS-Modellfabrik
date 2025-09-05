"""
FTS Connection Komponente

Zeigt FTS-Verbindungsstatus an.
MQTT-Topic: fts/v1/ff/5iO4/connection
"""

from datetime import datetime

import streamlit as st

from .message_processor import create_topic_filter, get_message_processor


def process_fts_connection_messages(messages):
    """Verarbeitet neue FTS-Connection-Nachrichten"""
    if not messages:
        return

    # Neueste FTS-Connection-Nachricht finden
    connection_messages = [msg for msg in messages if msg.get("topic", "").startswith("fts/v1/ff/5iO4/connection")]

    if connection_messages:
        latest_connection_msg = max(connection_messages, key=lambda x: x.get("ts", 0))
        # Connection-Daten in Session-State speichern
        st.session_state["fts_connection_data"] = latest_connection_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["fts_connection_last_update"] = latest_connection_msg.get("ts", 0)


def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren (wie in overview_inventory)"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        # Unix-Timestamp zu datetime konvertieren
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"


def show_fts_connection():
    """Zeigt FTS-Connection-Informationen"""
    st.subheader("🔗 FTS Connection")

    # Message-Processor für FTS-Connection
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Message-Processor erstellen (nur einmal)
        processor = get_message_processor(
            component_name="fts_connection",
            message_filter=create_topic_filter("fts/v1/ff/5iO4/connection"),
            processor_function=process_fts_connection_messages,
        )

        # Nachrichten verarbeiten (nur neue)
        processor.process_messages(mqtt_client)

        # Status-Anzeige (wie in overview_inventory)
        last_update_timestamp = st.session_state.get("fts_connection_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ FTS Connection aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine FTS-Connection-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - FTS Connection wird nicht aktualisiert")

    # Connection-Daten anzeigen
    connection_data = st.session_state.get("fts_connection_data")

    if connection_data:
        try:
            import json

            if isinstance(connection_data, str):
                connection_data = json.loads(connection_data)

            # Verbindungsstatus
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔗 Verbindungsstatus")
                connection_state = connection_data.get("connectionState", "UNKNOWN")

                if connection_state == "ONLINE":
                    st.success(f"✅ **{connection_state}**")
                else:
                    st.error(f"❌ **{connection_state}**")

                st.write(f"**Serial Number:** {connection_data.get('serialNumber', 'N/A')}")
                st.write(f"**Version:** {connection_data.get('version', 'N/A')}")
                st.write(f"**Manufacturer:** {connection_data.get('manufacturer', 'N/A')}")

            with col2:
                st.markdown("### 🌐 Netzwerk-Informationen")
                ip_address = connection_data.get("ip", "N/A")
                st.write(f"**IP-Adresse:** {ip_address}")

                # Timestamp
                timestamp = connection_data.get("timestamp", "N/A")
                if timestamp != "N/A":
                    st.write(f"**Letzte Verbindung:** {timestamp}")

                # Header ID
                header_id = connection_data.get("headerId", "N/A")
                st.write(f"**Header ID:** {header_id}")

            # Status-Indikator
            st.markdown("### 📊 Status-Übersicht")
            if connection_state == "ONLINE":
                st.info("🟢 FTS ist online und erreichbar")
            else:
                st.warning("🔴 FTS ist offline oder nicht erreichbar")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw Connection Data"):
                st.json(connection_data)

        except Exception as e:
            st.error(f"❌ Fehler beim Anzeigen der Connection-Daten: {e}")
            st.write("**Raw Data:**")
            st.write(connection_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/connection`")
