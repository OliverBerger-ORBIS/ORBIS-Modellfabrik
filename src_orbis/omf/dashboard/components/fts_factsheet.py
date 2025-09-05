"""
FTS Factsheet Komponente

Zeigt FTS-Konfiguration und Spezifikationen an.
MQTT-Topic: fts/v1/ff/5iO4/factsheet
"""

from datetime import datetime

import streamlit as st

from .message_processor import create_topic_filter, get_message_processor


def process_fts_factsheet_messages(messages):
    """Verarbeitet neue FTS-Factsheet-Nachrichten"""
    if not messages:
        return

    # Neueste FTS-Factsheet-Nachricht finden
    factsheet_messages = [msg for msg in messages if msg.get("topic", "").startswith("fts/v1/ff/5iO4/factsheet")]

    if factsheet_messages:
        latest_factsheet_msg = max(factsheet_messages, key=lambda x: x.get("ts", 0))
        # Factsheet-Daten in Session-State speichern
        st.session_state["fts_factsheet_data"] = latest_factsheet_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["fts_factsheet_last_update"] = latest_factsheet_msg.get("ts", 0)


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


def show_fts_factsheet():
    """Zeigt FTS-Factsheet-Informationen"""
    st.subheader("📄 FTS Factsheet")

    # Message-Processor für FTS-Factsheet
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Message-Processor erstellen (nur einmal)
        processor = get_message_processor(
            component_name="fts_factsheet",
            message_filter=create_topic_filter("fts/v1/ff/5iO4/factsheet"),
            processor_function=process_fts_factsheet_messages,
        )

        # Nachrichten verarbeiten (nur neue)
        processor.process_messages(mqtt_client)

        # Status-Anzeige (wie in overview_inventory)
        last_update_timestamp = st.session_state.get("fts_factsheet_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ FTS Factsheet aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine FTS-Factsheet-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - FTS Factsheet wird nicht aktualisiert")

    # Factsheet-Daten anzeigen
    factsheet_data = st.session_state.get("fts_factsheet_data")

    if factsheet_data:
        try:
            import json

            if isinstance(factsheet_data, str):
                factsheet_data = json.loads(factsheet_data)

            # Grundinformationen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🏭 Grundinformationen")
                st.write(f"**Serial Number:** {factsheet_data.get('serialNumber', 'N/A')}")
                st.write(f"**Version:** {factsheet_data.get('version', 'N/A')}")
                st.write(f"**Manufacturer:** {factsheet_data.get('manufacturer', 'N/A')}")

                # Type Specification
                type_spec = factsheet_data.get("typeSpecification", {})
                if type_spec:
                    st.write(f"**Series Name:** {type_spec.get('seriesName', 'N/A')}")
                    st.write(f"**AGV Class:** {type_spec.get('agvClass', 'N/A')}")

                    nav_types = type_spec.get("navigationTypes", [])
                    if nav_types:
                        st.write(f"**Navigation Types:** {', '.join(nav_types)}")

            with col2:
                st.markdown("### 📦 Load Spezifikationen")
                load_spec = factsheet_data.get("loadSpecification", {})
                if load_spec:
                    load_positions = load_spec.get("loadPositions", [])
                    if load_positions:
                        st.write(f"**Load Positions:** {', '.join(load_positions)}")

                    load_sets = load_spec.get("loadSets", [])
                    if load_sets:
                        st.write("**Load Sets:**")
                        for load_set in load_sets:
                            st.write(f"- {load_set.get('setName', 'N/A')}: {load_set.get('loadType', 'N/A')}")

            # Protocol Features
            protocol_features = factsheet_data.get("protocolFeatures", {})
            if protocol_features:
                st.markdown("### 🔧 Verfügbare Aktionen")
                agv_actions = protocol_features.get("agvActions", [])
                if agv_actions:
                    for action in agv_actions:
                        action_type = action.get("actionType", "N/A")
                        action_scopes = action.get("actionScopes", "N/A")
                        st.write(f"- **{action_type}** (Scope: {action_scopes})")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw Factsheet Data"):
                st.json(factsheet_data)

        except Exception as e:
            st.error(f"❌ Fehler beim Anzeigen der Factsheet-Daten: {e}")
            st.write("**Raw Data:**")
            st.write(factsheet_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/factsheet`")
