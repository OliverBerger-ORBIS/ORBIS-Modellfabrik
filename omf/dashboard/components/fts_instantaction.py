"""
FTS Instant Action Komponente

Zeigt sofortige FTS-Aktionen an.
MQTT-Topic: fts/v1/ff/5iO4/instantAction
"""

from datetime import datetime

import streamlit as st

from omf.tools.logging_config import get_logger

logger = get_logger("omf.dashboard.components.fts_instantaction")

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer

# MessageTemplate Bibliothek Import
try:
    from omf.tools.message_template_manager import get_message_template_manager

    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    logger.debug(f"❌ MessageTemplate Import-Fehler: {e}")
except Exception as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    logger.debug(f"❌ MessageTemplate Fehler: {e}")


def process_fts_instantaction_messages_from_buffers(instantaction_messages):
    """Verarbeitet FTS-InstantAction-Nachrichten aus Per-Topic-Buffer"""
    if not instantaction_messages:
        return

    # Neueste FTS-InstantAction-Nachricht finden
    if instantaction_messages:
        latest_instantaction_msg = max(instantaction_messages, key=lambda x: x.get("ts", 0))
        # InstantAction-Daten in Session-State speichern
        st.session_state["fts_instantaction_data"] = latest_instantaction_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["fts_instantaction_last_update"] = latest_instantaction_msg.get("ts", 0)


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


def analyze_fts_instantaction_data(instantaction_data):
    """Analysiert FTS-InstantAction-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not instantaction_data:
        return {}

    try:
        import json

        if isinstance(instantaction_data, str):
            instantaction_data = json.loads(instantaction_data)

        # Semantische Analyse basierend auf RAW-Data
        analysis = {
            # Grundinformationen
            "serial_number": instantaction_data.get("serialNumber", "N/A"),
            "timestamp": instantaction_data.get("timestamp", "N/A"),
            # Aktionen
            "actions": [],
            "action_count": 0,
            "latest_action": {},
            "action_summary": "Keine Aktionen",
            # Aktion-Details
            "action_types": [],
            "has_clear_load_handler": False,
            "has_get_status": False,
            "has_reset": False,
        }

        # Aktionen analysieren
        actions = instantaction_data.get("actions", [])
        if actions:
            analysis["actions"] = actions
            analysis["action_count"] = len(actions)

            # Neueste Aktion (letzte in der Liste)
            latest_action = actions[-1] if actions else {}
            analysis["latest_action"] = latest_action

            # Aktion-Typen sammeln
            action_types = [action.get("actionType", "UNKNOWN") for action in actions]
            analysis["action_types"] = list(set(action_types))  # Eindeutige Typen

            # Spezifische Aktion-Typen prüfen
            analysis["has_clear_load_handler"] = "clearLoadHandler" in action_types
            analysis["has_get_status"] = "getStatus" in action_types
            analysis["has_reset"] = "reset" in action_types

            # Aktion-Zusammenfassung
            if latest_action:
                action_type = latest_action.get("actionType", "UNKNOWN")
                metadata = latest_action.get("metadata", {})

                # Spezifische Aktion-Details
                if action_type == "clearLoadHandler":
                    load_dropped = metadata.get("loadDropped", False)
                    load_type = metadata.get("loadType", "N/A")
                    load_position = metadata.get("loadPosition", "N/A")
                    if load_dropped:
                        analysis["action_summary"] = f"Load Handler geleert: {load_type} von Position {load_position}"
                    else:
                        analysis["action_summary"] = "Load Handler geleert (keine Ladung)"
                elif action_type == "getStatus":
                    analysis["action_summary"] = "Status abgefragt"
                elif action_type == "reset":
                    analysis["action_summary"] = "FTS zurückgesetzt"
                else:
                    analysis["action_summary"] = f"Aktion: {action_type}"
            else:
                analysis["action_summary"] = f"{len(actions)} Aktionen ausgeführt"

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche FTS-InstantAction-Topic zu validieren
                validation_result = template_manager.validate_message(
                    "fts/v1/ff/5iO4/instantAction", instantaction_data
                )
                if validation_result.get("valid", False):
                    template_validation = {
                        "valid": True,
                        "topic": "fts/v1/ff/5iO4/instantAction",
                        "template": validation_result.get("template", {}),
                    }
                else:
                    template_validation = {
                        "valid": False,
                        "topic": "fts/v1/ff/5iO4/instantAction",
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
        st.warning(f"⚠️ Fehler bei der FTS-InstantAction-Analyse: {e}")
        return {}


def show_fts_instantaction():
    """Zeigt FTS-Instant-Action-Informationen"""
    st.subheader("⚡ FTS Instant Action")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # FTS-InstantAction-Topic abonnieren
        mqtt_client.subscribe_many(["fts/v1/ff/5iO4/instantAction"])

        # Nachrichten aus Per-Topic-Buffer holen
        instantaction_messages = list(mqtt_client.get_buffer("fts/v1/ff/5iO4/instantAction"))

        # Nachrichten verarbeiten
        process_fts_instantaction_messages_from_buffers(instantaction_messages)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("fts_instantaction_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ FTS Instant Action aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine FTS-InstantAction-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - FTS Instant Action wird nicht aktualisiert")

    # InstantAction-Daten anzeigen
    instantaction_data = st.session_state.get("fts_instantaction_data")

    if instantaction_data:
        # Semantische Analyse der FTS-InstantAction-Daten
        analysis = analyze_fts_instantaction_data(instantaction_data)

        if analysis:
            # InstantAction-Informationen mit korrekten Feldnamen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ⚡ Aktuelle Aktion")
                action_summary = analysis.get("action_summary", "Keine Aktionen")
                st.write(f"**Aktion:** {action_summary}")

                action_count = analysis.get("action_count", 0)
                st.write(f"**Anzahl Aktionen:** {action_count}")

                # Serial Number
                serial_number = analysis.get("serial_number", "N/A")
                st.write(f"**Serial Number:** {serial_number}")

            with col2:
                st.markdown("### 🔧 Aktion-Details")
                # Aktion-Typen
                action_types = analysis.get("action_types", [])
                if action_types:
                    st.write(f"**Aktion-Typen:** {', '.join(action_types)}")
                else:
                    st.write("**Aktion-Typen:** Keine")

                # Spezifische Aktionen
                if analysis.get("has_clear_load_handler", False):
                    st.success("✅ **Load Handler geleert**")
                if analysis.get("has_get_status", False):
                    st.info("ℹ️ **Status abgefragt**")
                if analysis.get("has_reset", False):
                    st.warning("⚠️ **FTS zurückgesetzt**")

                # Timestamp
                timestamp = analysis.get("timestamp", "N/A")
                if timestamp != "N/A":
                    st.write(f"**Timestamp:** {timestamp}")

            # Neueste Aktion-Details
            st.markdown("### 🎯 Neueste Aktion")
            latest_action = analysis.get("latest_action", {})
            if latest_action:
                action_type = latest_action.get("actionType", "N/A")
                action_id = latest_action.get("actionId", "N/A")
                metadata = latest_action.get("metadata", {})

                st.write(f"**Typ:** {action_type}")
                st.write(f"**ID:** {action_id}")

                # Metadata-Details
                if metadata:
                    st.markdown("**Metadata:**")
                    for key, value in metadata.items():
                        st.write(f"- **{key}:** {value}")
            else:
                st.info("ℹ️ Keine Aktion-Details verfügbar")

            # Aktion-Übersicht
            st.markdown("### 🚦 Aktion-Übersicht")
            if action_count > 0:
                st.success(f"🟢 {action_count} Aktion(en) ausgeführt")
            else:
                st.info("ℹ️ Keine Aktionen ausgeführt")

            # Template-Validierung
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
            with st.expander("🔍 Raw InstantAction Data"):
                st.json(instantaction_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der InstantAction-Daten")
            st.write("**Raw Data:**")
            st.write(instantaction_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/instantAction`")
