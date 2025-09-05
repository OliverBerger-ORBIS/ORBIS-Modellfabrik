"""
CCU Control Komponente

Zeigt CCU-Steuerungsbefehle an.
MQTT-Topics: ccu/control, ccu/control/command, ccu/control/order
"""

from datetime import datetime

import streamlit as st

from .message_processor import create_topic_filter, get_message_processor

# MessageTemplate Bibliothek Import
try:
    import omf.tools.message_template_manager  # noqa: F401

    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError:
    TEMPLATE_MANAGER_AVAILABLE = False


def process_ccu_control_messages(messages):
    """Verarbeitet neue CCU-Control-Nachrichten"""
    if not messages:
        return

    # Neueste CCU-Control-Nachricht finden
    control_messages = [msg for msg in messages if msg.get("topic", "").startswith("ccu/control")]

    if control_messages:
        latest_control_msg = max(control_messages, key=lambda x: x.get("ts", 0))
        # Control-Daten in Session-State speichern
        st.session_state["ccu_control_data"] = latest_control_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["ccu_control_last_update"] = latest_control_msg.get("ts", 0)


def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"


def show_ccu_control():
    """Zeigt CCU-Control-Informationen"""
    st.subheader("🎮 CCU Control")

    # Message-Processor für CCU-Control
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Message-Processor erstellen (nur einmal)
        processor = get_message_processor(
            component_name="ccu_control",
            message_filter=create_topic_filter("ccu/control"),
            processor_function=process_ccu_control_messages,
        )

        # Nachrichten verarbeiten (nur neue)
        processor.process_messages(mqtt_client)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("ccu_control_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ CCU Control aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine CCU-Control-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - CCU Control wird nicht aktualisiert")

    # Control-Daten anzeigen
    control_data = st.session_state.get("ccu_control_data")

    if control_data:
        st.info("🚧 CCU Control-Komponente - In Entwicklung")
        st.write("**Raw Data:**")
        st.json(control_data)
    else:
        st.write("**MQTT-Topics:** `ccu/control`, `ccu/control/command`, `ccu/control/order`")
