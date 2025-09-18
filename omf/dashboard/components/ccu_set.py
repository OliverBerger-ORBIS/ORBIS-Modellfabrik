"""
CCU Set Komponente

Zeigt CCU-Konfiguration und Reset-Befehle an.
MQTT-Topic: ccu/set/reset
"""

from datetime import datetime

import streamlit as st

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer

def process_ccu_set_messages_from_buffers(set_messages):
    """Verarbeitet CCU-Set-Nachrichten aus Per-Topic-Buffer"""
    if not set_messages:
        return

    # Neueste CCU-Set-Nachricht finden
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

def analyze_ccu_set_data(set_data):
    """Analysiert CCU-Set-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not set_data:
        return {}

    try:
        import json

        if isinstance(set_data, str):
            set_data = json.loads(set_data)

        # Semantische Analyse basierend auf echten CCU-Set-Daten
        analysis = {
            # Grundinformationen (basierend auf echten Daten)
            "serial_number": set_data.get("serialNumber", "N/A"),
            "charge": set_data.get("charge", False),
            "with_storage": set_data.get("withStorage", False),
            "timestamp": set_data.get("timestamp", "N/A"),
            "set_type": set_data.get("set_type", "UNKNOWN"),
            "set_id": set_data.get("set_id", "N/A"),
            "status": set_data.get("status", "UNKNOWN"),
            # Reset-Informationen
            "reset_type": set_data.get("reset_type", "N/A"),
            "reset_scope": set_data.get("reset_scope", "N/A"),
            "reset_reason": set_data.get("reset_reason", "N/A"),
            # Konfiguration
            "config_version": set_data.get("config_version", "N/A"),
            "config_changes": set_data.get("config_changes", []),
            "has_config_changes": len(set_data.get("config_changes", [])) > 0,
            # System-Status
            "execution_status": set_data.get("execution_status", "PENDING"),
            "error_message": set_data.get("error_message", None),
            "has_error": set_data.get("error_message") is not None,
        }

        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der CCU-Set-Analyse: {e}")
        return {}

def show_ccu_set():
    """Zeigt CCU-Set-Informationen"""
    st.subheader("⚙️ CCU Set")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # CCU-Set-Topic abonnieren
        mqtt_client.subscribe_many(["ccu/set/reset"])

        # Nachrichten aus Per-Topic-Buffer holen
        set_messages = list(mqtt_client.get_buffer("ccu/set/reset"))

        # Nachrichten verarbeiten
        process_ccu_set_messages_from_buffers(set_messages)

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
        # Semantische Analyse der CCU-Set-Daten
        analysis = analyze_ccu_set_data(set_data)

        if analysis:
            # Set-Informationen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### ⚙️ Set-Info")

                # Serial Number (neues Feld)
                serial_number = analysis.get("serial_number", "N/A")
                if serial_number != "N/A":
                    st.write(f"**Serial Number:** {serial_number}")

                # Charge Status (neues Feld)
                charge = analysis.get("charge", False)
                if charge:
                    st.success("🔋 **Charge:** Aktiv")
                else:
                    st.info("🔋 **Charge:** Inaktiv")

                # With Storage Status (neues Feld)
                with_storage = analysis.get("with_storage", False)
                if with_storage:
                    st.success("💾 **Storage:** Mit Speicher")
                else:
                    st.info("💾 **Storage:** Ohne Speicher")

                set_type = analysis.get("set_type", "UNKNOWN")
                if set_type == "RESET":
                    st.warning(f"🔄 **Set Type:** {set_type}")
                elif set_type == "CONFIG":
                    st.info(f"⚙️ **Set Type:** {set_type}")
                else:
                    st.write(f"**Set Type:** {set_type}")

                set_id = analysis.get("set_id", "N/A")
                if set_id != "N/A":
                    st.write(f"**Set ID:** {set_id}")

                status = analysis.get("status", "UNKNOWN")
                if status == "SUCCESS":
                    st.success(f"✅ **Status:** {status}")
                elif status == "FAILED":
                    st.error(f"❌ **Status:** {status}")
                else:
                    st.write(f"**Status:** {status}")

            with col2:
                st.markdown("### 🔄 Reset-Info")
                reset_type = analysis.get("reset_type", "N/A")
                if reset_type != "N/A":
                    st.write(f"**Reset Type:** {reset_type}")

                reset_scope = analysis.get("reset_scope", "N/A")
                if reset_scope != "N/A":
                    st.write(f"**Reset Scope:** {reset_scope}")

                reset_reason = analysis.get("reset_reason", "N/A")
                if reset_reason != "N/A":
                    st.write(f"**Reset Reason:** {reset_reason}")

            # Konfiguration
            st.markdown("### ⚙️ Konfiguration")
            config_version = analysis.get("config_version", "N/A")
            st.write(f"**Config Version:** {config_version}")

            has_config_changes = analysis.get("has_config_changes", False)
            if has_config_changes:
                st.markdown("### 📝 Config Changes")
                config_changes = analysis.get("config_changes", [])
                for i, change in enumerate(config_changes, 1):
                    st.write(f"{i}. {change}")

            # Execution-Status
            st.markdown("### ⚡ Execution-Status")
            execution_status = analysis.get("execution_status", "PENDING")
            if execution_status == "EXECUTING":
                st.info(f"🔄 **Status:** {execution_status}")
            elif execution_status == "COMPLETED":
                st.success(f"✅ **Status:** {execution_status}")
            elif execution_status == "FAILED":
                st.error(f"❌ **Status:** {execution_status}")
            else:
                st.write(f"**Status:** {execution_status}")

            # Error-Status
            has_error = analysis.get("has_error", False)
            if has_error:
                st.markdown("### ❌ Error-Status")
                error_message = analysis.get("error_message", "Unknown error")
                st.error(f"🔴 **Error:** {error_message}")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw CCU Set Data"):
                st.json(set_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der CCU-Set-Daten")
            st.write("**Raw Data:**")
            st.write(set_data)
    else:
        st.write("**MQTT-Topic:** `ccu/set/reset`")
