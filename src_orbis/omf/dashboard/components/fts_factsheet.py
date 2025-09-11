"""
FTS Factsheet Komponente

Zeigt FTS-Konfiguration und Spezifikationen an.
MQTT-Topic: fts/v1/ff/5iO4/factsheet
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


def process_fts_factsheet_messages_from_buffers(factsheet_messages):
    """Verarbeitet FTS-Factsheet-Nachrichten aus Per-Topic-Buffer"""
    if not factsheet_messages:
        return

    # Neueste FTS-Factsheet-Nachricht finden
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


def analyze_fts_factsheet_data(factsheet_data):
    """Analysiert FTS-Factsheet-Daten semantisch"""
    if not factsheet_data:
        return {}

    try:
        import json

        if isinstance(factsheet_data, str):
            factsheet_data = json.loads(factsheet_data)

        # Semantische Analyse
        analysis = {
            "serial_number": factsheet_data.get("serialNumber", "N/A"),
            "model": factsheet_data.get("model", "N/A"),
            "manufacturer": factsheet_data.get("manufacturer", "N/A"),
            "version": factsheet_data.get("version", "N/A"),
            "firmware": factsheet_data.get("firmware", "N/A"),
            "hardware": factsheet_data.get("hardware", "N/A"),
            "capabilities": factsheet_data.get("capabilities", []),
            "specifications": factsheet_data.get("specifications", {}),
        }

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche FTS-Factsheet-Topic zu validieren
                validation_result = template_manager.validate_message("fts/v1/ff/5iO4/factsheet", factsheet_data)
                if validation_result.get("valid", False):
                    template_validation = {
                        "valid": True,
                        "topic": "fts/v1/ff/5iO4/factsheet",
                        "template": validation_result.get("template", {}),
                    }
                else:
                    template_validation = {
                        "valid": False,
                        "topic": "fts/v1/ff/5iO4/factsheet",
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
        st.warning(f"⚠️ Fehler bei der FTS-Factsheet-Analyse: {e}")
        return {}


def show_fts_factsheet():
    """Zeigt FTS-Factsheet-Informationen"""
    st.subheader("📄 FTS Factsheet")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # FTS-Factsheet-Topic abonnieren
        mqtt_client.subscribe_many(["fts/v1/ff/5iO4/factsheet"])
        
        # Nachrichten aus Per-Topic-Buffer holen
        factsheet_messages = list(mqtt_client.get_buffer("fts/v1/ff/5iO4/factsheet"))
        
        # Nachrichten verarbeiten
        process_fts_factsheet_messages_from_buffers(factsheet_messages)

        # Status-Anzeige
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

            # Semantische Analyse und Template-Validierung
            analysis = analyze_fts_factsheet_data(factsheet_data)
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
            with st.expander("🔍 Raw Factsheet Data"):
                st.json(factsheet_data)

        except Exception as e:
            st.error(f"❌ Fehler beim Anzeigen der Factsheet-Daten: {e}")
            st.write("**Raw Data:**")
            st.write(factsheet_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/factsheet`")
