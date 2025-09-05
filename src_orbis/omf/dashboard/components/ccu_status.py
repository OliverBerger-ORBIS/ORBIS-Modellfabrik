"""
CCU Status Komponente

Zeigt CCU-Verbindungs- und Gesundheitsstatus an.
MQTT-Topics: ccu/status, ccu/status/connection, ccu/status/health
"""

from datetime import datetime

import streamlit as st

from .message_processor import create_topic_filter, get_message_processor


def process_ccu_status_messages(messages):
    """Verarbeitet neue CCU-Status-Nachrichten"""
    if not messages:
        return

    # Neueste CCU-Status-Nachricht finden
    status_messages = [msg for msg in messages if msg.get("topic", "").startswith("ccu/status")]

    if status_messages:
        latest_status_msg = max(status_messages, key=lambda x: x.get("ts", 0))
        # Status-Daten in Session-State speichern
        st.session_state["ccu_status_data"] = latest_status_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["ccu_status_last_update"] = latest_status_msg.get("ts", 0)


def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"


def show_ccu_status():
    """Zeigt CCU-Status-Informationen"""
    st.subheader("🔗 CCU Status")

    # Message-Processor für CCU-Status
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Message-Processor erstellen (nur einmal)
        processor = get_message_processor(
            component_name="ccu_status",
            message_filter=create_topic_filter("ccu/status"),
            processor_function=process_ccu_status_messages,
        )

        # Nachrichten verarbeiten (nur neue)
        processor.process_messages(mqtt_client)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("ccu_status_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ CCU Status aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine CCU-Status-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - CCU Status wird nicht aktualisiert")

    # Status-Daten anzeigen
    status_data = st.session_state.get("ccu_status_data")

    if status_data:
        st.info("🚧 CCU Status-Komponente - In Entwicklung")
        st.write("**Raw Data:**")
        st.json(status_data)
    else:
        st.write("**MQTT-Topics:** `ccu/status`, `ccu/status/connection`, `ccu/status/health`")
