"""
FTS State Komponente

Zeigt FTS-Status und Position an.
MQTT-Topic: fts/v1/ff/5iO4/state
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


def process_fts_state_messages_from_buffers(state_messages):
    """Verarbeitet FTS-State-Nachrichten aus Per-Topic-Buffer"""
    if not state_messages:
        return

    # Neueste FTS-State-Nachricht finden
    if state_messages:
        latest_state_msg = max(state_messages, key=lambda x: x.get("ts", 0))
        # State-Daten in Session-State speichern
        st.session_state["fts_state_data"] = latest_state_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["fts_state_last_update"] = latest_state_msg.get("ts", 0)


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


def analyze_fts_state_data(state_data):
    """Analysiert FTS-State-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not state_data:
        return {}

    try:
        import json

        if isinstance(state_data, str):
            state_data = json.loads(state_data)

        # Semantische Analyse basierend auf RAW-Data
        analysis = {
            # Position & Navigation
            "current_position": state_data.get("lastNodeId", "N/A"),
            "driving": state_data.get("driving", False),
            "paused": state_data.get("paused", False),
            # Batterie-Status
            "battery_info": {},
            "battery_percentage": "N/A",
            "battery_voltage": "N/A",
            "battery_charging": False,
            # Ladezustand
            "load_info": [],
            "load_summary": "Keine Ladung",
            # Aktuelle Aktion
            "current_action": {},
            "action_status": "Keine Aktion",
            # System-Status
            "errors": state_data.get("errors", []),
            "has_errors": len(state_data.get("errors", [])) > 0,
            "waiting_for_load": state_data.get("waitingForLoadHandling", False),
        }

        # Batterie-Details analysieren
        battery_state = state_data.get("batteryState", {})
        if battery_state:
            analysis["battery_info"] = battery_state
            analysis["battery_percentage"] = battery_state.get("percentage", "N/A")
            analysis["battery_voltage"] = f"{battery_state.get('currentVoltage', 'N/A')}V"
            analysis["battery_charging"] = battery_state.get("charging", False)

        # Ladezustand analysieren
        load_data = state_data.get("load", [])
        if load_data:
            analysis["load_info"] = load_data
            loaded_positions = [pos for pos in load_data if pos.get("loadType") is not None]
            if loaded_positions:
                analysis["load_summary"] = f"{len(loaded_positions)} Positionen beladen"
            else:
                analysis["load_summary"] = "Alle Positionen leer"

        # Aktuelle Aktion analysieren
        action_state = state_data.get("actionState", {})
        if action_state:
            analysis["current_action"] = action_state
            command = action_state.get("command", "N/A")
            state = action_state.get("state", "N/A")
            analysis["action_status"] = f"{command}: {state}"

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche FTS-State-Topic zu validieren
                validation_result = template_manager.validate_message("fts/v1/ff/5iO4/state", state_data)
                if validation_result.get("valid", False):
                    template_validation = {
                        "valid": True,
                        "topic": "fts/v1/ff/5iO4/state",
                        "template": validation_result.get("template", {}),
                    }
                else:
                    template_validation = {
                        "valid": False,
                        "topic": "fts/v1/ff/5iO4/state",
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
        st.warning(f"⚠️ Fehler bei der FTS-State-Analyse: {e}")
        return {}


def show_fts_state():
    """Zeigt FTS-State-Informationen"""
    st.subheader("📊 FTS State")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # FTS-State-Topic abonnieren
        mqtt_client.subscribe_many(["fts/v1/ff/5iO4/state"])
        
        # Nachrichten aus Per-Topic-Buffer holen
        state_messages = list(mqtt_client.get_buffer("fts/v1/ff/5iO4/state"))
        
        # Nachrichten verarbeiten
        process_fts_state_messages_from_buffers(state_messages)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("fts_state_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ FTS State aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine FTS-State-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - FTS State wird nicht aktualisiert")

    # State-Daten anzeigen
    state_data = st.session_state.get("fts_state_data")

    if state_data:
        # Semantische Analyse der FTS-State-Daten
        analysis = analyze_fts_state_data(state_data)

        if analysis:
            # Status-Informationen mit korrekten Feldnamen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📍 Position & Navigation")
                current_position = analysis.get("current_position", "N/A")
                st.write(f"**Aktuelle Position:** {current_position}")

                driving = analysis.get("driving", False)
                if driving:
                    st.info("🚛 **Status:** Fährt gerade")
                else:
                    st.success("⏸️ **Status:** Steht")

                paused = analysis.get("paused", False)
                if paused:
                    st.warning("⏸️ **Pausiert:** Ja")
                else:
                    st.success("▶️ **Pausiert:** Nein")

            with col2:
                st.markdown("### ⚡ System-Status")
                battery_percentage = analysis.get("battery_percentage", "N/A")
                battery_voltage = analysis.get("battery_voltage", "N/A")
                battery_charging = analysis.get("battery_charging", False)

                st.write(f"**Batterie:** {battery_percentage}% ({battery_voltage})")
                if battery_charging:
                    st.info("🔋 **Laden:** Aktiv")
                else:
                    st.success("🔋 **Laden:** Inaktiv")

                load_summary = analysis.get("load_summary", "N/A")
                st.write(f"**Ladezustand:** {load_summary}")

            # Aktuelle Aktion
            st.markdown("### 🎯 Aktuelle Aktion")
            action_status = analysis.get("action_status", "Keine Aktion")
            st.write(f"**Aktion:** {action_status}")

            # System-Status
            st.markdown("### 🚦 System-Status")
            has_errors = analysis.get("has_errors", False)
            waiting_for_load = analysis.get("waiting_for_load", False)

            if has_errors:
                st.error("🔴 **Fehler:** Ja - siehe Raw Data")
            else:
                st.success("🟢 **Fehler:** Nein")

            if waiting_for_load:
                st.info("⏳ **Wartet auf Ladung:** Ja")
            else:
                st.success("✅ **Wartet auf Ladung:** Nein")

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
            with st.expander("🔍 Raw State Data"):
                st.json(state_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der State-Daten")
            st.write("**Raw Data:**")
            st.write(state_data)
    else:
        st.write("**MQTT-Topic:** `fts/v1/ff/5iO4/state`")
