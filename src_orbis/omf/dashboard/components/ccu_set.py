"""
CCU Set Komponente

Zeigt CCU-Konfiguration und Reset-Befehle an.
MQTT-Topic: ccu/set/reset
"""

from datetime import datetime

import streamlit as st

from .message_processor import create_topic_filter, get_message_processor


def process_ccu_set_messages(messages):
    """Verarbeitet neue CCU-Set-Nachrichten"""
    if not messages:
        return

    # Neueste CCU-Set-Nachricht finden
    set_messages = [msg for msg in messages if msg.get("topic", "").startswith("ccu/set")]

    if set_messages:
        latest_set_msg = max(set_messages, key=lambda x: x.get("ts", 0))
        # Set-Daten in Session-State speichern
        st.session_state["ccu_set_data"] = latest_set_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["ccu_set_last_update"] = latest_set_msg.get("ts", 0)


def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"


def show_ccu_set():
    """Zeigt CCU-Set-Informationen"""
    st.subheader("⚙️ CCU Set")

    # Message-Processor für CCU-Set
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Message-Processor erstellen (nur einmal)
        processor = get_message_processor(
            component_name="ccu_set",
            message_filter=create_topic_filter("ccu/set"),
            processor_function=process_ccu_set_messages,
        )

        # Nachrichten verarbeiten (nur neue)
        processor.process_messages(mqtt_client)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("ccu_set_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ CCU Set aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine CCU-Set-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - CCU Set wird nicht aktualisiert")

    # Set-Daten anzeigen
    set_data = st.session_state.get("ccu_set_data")

    if set_data:
        st.info("🚧 CCU Set-Komponente - In Entwicklung")
        st.write("**Raw Data:**")
        st.json(set_data)
    else:
        st.write("**MQTT-Topic:** `ccu/set/reset`")
