"""
FTS Connection Komponente

Zeigt FTS-Verbindungsstatus an.
MQTT-Topic: fts/v1/ff/5iO4/connection
"""

from datetime import datetime

import streamlit as st

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer

# MessageTemplate Bibliothek Import
try:
    from src_orbis.omf.tools.message_template_manager import get_message_template_manager

    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    print(f"❌ MessageTemplate Import-Fehler: {e}")
except Exception as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    print(f"❌ MessageTemplate Fehler: {e}")


def process_fts_connection_messages_from_buffers(connection_messages):
    """Verarbeitet FTS-Connection-Nachrichten aus Per-Topic-Buffer"""
    if not connection_messages:
        return

    # Neueste FTS-Connection-Nachricht finden
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


def analyze_fts_connection_data(connection_data):
    """Analysiert FTS-Connection-Daten semantisch"""
    if not connection_data:
        return {}

    try:
        import json

        if isinstance(connection_data, str):
            connection_data = json.loads(connection_data)

        # Semantische Analyse
        analysis = {
            "connection_state": connection_data.get("connectionState", "N/A"),
            "connection_quality": connection_data.get("connectionQuality", "N/A"),
            "signal_strength": connection_data.get("signalStrength", "N/A"),
            "last_seen": connection_data.get("lastSeen", "N/A"),
            "ip_address": connection_data.get("ipAddress", "N/A"),
            "port": connection_data.get("port", "N/A"),
            "protocol": connection_data.get("protocol", "N/A"),
        }

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche FTS-Connection-Topic zu validieren
                validation_result = template_manager.validate_message("fts/v1/ff/5iO4/connection", connection_data)
                if validation_result.get("valid", False):
                    template_validation = {
                        "valid": True,
                        "topic": "fts/v1/ff/5iO4/connection",
                        "template": validation_result.get("template", {}),
                    }
                else:
                    template_validation = {
                        "valid": False,
                        "topic": "fts/v1/ff/5iO4/connection",
                        "errors": validation_result.get("errors", []),
                        "template": validation_result.get("template", {}),
                        "error": validation_result.get("error", "Unknown error"),
                    }
            except Exception as e:
                template_validation = {
                    "valid": False,
                    "error": f"Template-Validierung fehlgeschlagen: {e}",
                }

        analysis["template_validation"] = template_validation
        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der FTS-Connection-Analyse: {e}")
        return {}


def show_fts_connection():
    """Zeigt FTS-Connection-Informationen"""
    st.subheader("🔗 FTS Connection")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # FTS-Connection-Topic abonnieren
        mqtt_client.subscribe_many(["fts/v1/ff/5iO4/connection"])

        # Nachrichten aus Per-Topic-Buffer holen
        connection_messages = list(mqtt_client.get_buffer("fts/v1/ff/5iO4/connection"))

        # Nachrichten verarbeiten
        process_fts_connection_messages_from_buffers(connection_messages)

        # Status-Anzeige
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

            # Semantische Analyse und Template-Validierung
            analysis = analyze_fts_connection_data(connection_data)
            if analysis:
                template_validation = analysis.get("template_validation")
                st.markdown("### 📋 MessageTemplate Validierung")

                if template_validation:
                    if template_validation.get("valid", False):
                        st.success(f"✅ **Template gültig:** {template_validation.get('topic', 'Unknown')}")
                        template = template_validation.get("template", {})
                        if template:
                            st.write(f"**Template:** {template.get('description', 'N/A')}")
                            st.write(f"**Kategorie:** {template.get('category', 'N/A')}")
                    else:
                        st.error("❌ **Template-Validierung fehlgeschlagen**")
                        error = template_validation.get("error", "Unknown error")
                        st.write(f"**Fehler:** {error}")
                        errors = template_validation.get("errors", [])
                        if errors:
                            st.write("**Validierungsfehler:**")
                            for error in errors:
                                st.write(f"- {error}")
                else:
                    st.warning("⚠️ **Template-Validierung nicht verfügbar**")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw Connection Data"):
                st.json(connection_data)

        except Exception as e:
            st.error(f"❌ Fehler beim Anzeigen der Connection-Daten: {e}")
            st.write("**Raw Data:**")
            st.write(connection_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/connection`")
