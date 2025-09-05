"""
CCU State Komponente

Zeigt CCU-Status und Workflow an.
MQTT-Topics: ccu/state, ccu/state/flow, ccu/state/status, ccu/state/error
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


def process_ccu_state_messages(messages):
    """Verarbeitet neue CCU-State-Nachrichten"""
    if not messages:
        return

    # Neueste CCU-State-Nachricht finden
    state_messages = [msg for msg in messages if msg.get("topic", "").startswith("ccu/state")]

    if state_messages:
        latest_state_msg = max(state_messages, key=lambda x: x.get("ts", 0))
        # State-Daten in Session-State speichern
        st.session_state["ccu_state_data"] = latest_state_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["ccu_state_last_update"] = latest_state_msg.get("ts", 0)


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


def analyze_ccu_state_data(state_data):
    """Analysiert CCU-State-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not state_data:
        return {}

    try:
        import json

        if isinstance(state_data, str):
            state_data = json.loads(state_data)

        # Semantische Analyse basierend auf CCU-Templates
        analysis = {
            # Grundinformationen
            "status": state_data.get("status", "UNKNOWN"),
            "health": state_data.get("health", "UNKNOWN"),
            "active_modules": state_data.get("active_modules", 0),
            "timestamp": state_data.get("timestamp", "N/A"),
            # Workflow-Status
            "workflow_state": state_data.get("workflow_state", "UNKNOWN"),
            "current_operation": state_data.get("current_operation", "N/A"),
            # Fehler-Status
            "errors": state_data.get("errors", []),
            "has_errors": len(state_data.get("errors", [])) > 0,
            "error_count": len(state_data.get("errors", [])),
            # System-Status
            "system_ready": state_data.get("system_ready", False),
            "maintenance_mode": state_data.get("maintenance_mode", False),
        }

        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der CCU-State-Analyse: {e}")
        return {}


def show_ccu_state():
    """Zeigt CCU-State-Informationen"""
    st.subheader("📊 CCU State")

    # Message-Processor für CCU-State
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Message-Processor erstellen (nur einmal)
        processor = get_message_processor(
            component_name="ccu_state",
            message_filter=create_topic_filter("ccu/state"),
            processor_function=process_ccu_state_messages,
        )

        # Nachrichten verarbeiten (nur neue)
        processor.process_messages(mqtt_client)

        # Status-Anzeige (wie in overview_inventory)
        last_update_timestamp = st.session_state.get("ccu_state_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ CCU State aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine CCU-State-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - CCU State wird nicht aktualisiert")

    # State-Daten anzeigen
    state_data = st.session_state.get("ccu_state_data")

    if state_data:
        # Semantische Analyse der CCU-State-Daten
        analysis = analyze_ccu_state_data(state_data)

        if analysis:
            # Status-Informationen mit korrekten Feldnamen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🏭 System-Status")
                status = analysis.get("status", "UNKNOWN")
                if status == "running":
                    st.success(f"✅ **Status:** {status}")
                elif status == "stopped":
                    st.error(f"❌ **Status:** {status}")
                elif status == "error":
                    st.error(f"🔴 **Status:** {status}")
                elif status == "maintenance":
                    st.warning(f"⚠️ **Status:** {status}")
                else:
                    st.info(f"ℹ️ **Status:** {status}")

                health = analysis.get("health", "UNKNOWN")
                if health == "good":
                    st.success(f"🟢 **Health:** {health}")
                elif health == "warning":
                    st.warning(f"🟡 **Health:** {health}")
                elif health == "critical":
                    st.error(f"🔴 **Health:** {health}")
                else:
                    st.info(f"ℹ️ **Health:** {health}")

            with col2:
                st.markdown("### 📊 System-Info")
                active_modules = analysis.get("active_modules", 0)
                st.write(f"**Aktive Module:** {active_modules}")

                system_ready = analysis.get("system_ready", False)
                if system_ready:
                    st.success("✅ **System bereit**")
                else:
                    st.warning("⚠️ **System nicht bereit**")

                maintenance_mode = analysis.get("maintenance_mode", False)
                if maintenance_mode:
                    st.info("🔧 **Wartungsmodus aktiv**")

            # Workflow-Status
            st.markdown("### 🔄 Workflow-Status")
            workflow_state = analysis.get("workflow_state", "UNKNOWN")
            current_operation = analysis.get("current_operation", "N/A")

            st.write(f"**Workflow:** {workflow_state}")
            st.write(f"**Aktuelle Operation:** {current_operation}")

            # Fehler-Status
            st.markdown("### ❌ Fehler-Status")
            has_errors = analysis.get("has_errors", False)
            error_count = analysis.get("error_count", 0)

            if has_errors:
                st.error(f"🔴 **Fehler:** {error_count} Fehler gefunden")
                errors = analysis.get("errors", [])
                if errors:
                    st.markdown("**Fehler-Details:**")
                    for i, error in enumerate(errors, 1):
                        st.write(f"{i}. {error}")
            else:
                st.success("🟢 **Keine Fehler**")

            # MessageTemplate Info (falls verfügbar)
            if TEMPLATE_MANAGER_AVAILABLE:
                st.markdown("### 📋 MessageTemplate Bibliothek")
                st.info("✅ MessageTemplate Bibliothek verfügbar - Semantische Analyse aktiv")
            else:
                st.warning("⚠️ MessageTemplate Bibliothek nicht verfügbar - Fallback-Analyse")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw CCU State Data"):
                st.json(state_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der CCU-State-Daten")
            st.write("**Raw Data:**")
            st.write(state_data)
    else:
        st.write("**MQTT-Topics:** `ccu/state`, `ccu/state/flow`, `ccu/state/status`, `ccu/state/error`")
