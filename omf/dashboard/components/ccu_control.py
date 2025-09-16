"""
CCU Control Komponente

Zeigt CCU-Steuerungsbefehle an.
MQTT-Topics: ccu/control, ccu/control/command, ccu/control/order
"""

from datetime import datetime

import streamlit as st

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer

# MessageTemplate Bibliothek Import
try:
    import omf.tools.message_template_manager  # noqa: F401

    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError:
    TEMPLATE_MANAGER_AVAILABLE = False


def process_ccu_control_messages_from_buffers(control_messages):
    """Verarbeitet CCU-Control-Nachrichten aus Per-Topic-Buffer"""
    if not control_messages:
        return

    # Neueste CCU-Control-Nachricht finden
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


def analyze_ccu_control_data(control_data):
    """Analysiert CCU-Control-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not control_data:
        return {}

    try:
        import json

        if isinstance(control_data, str):
            control_data = json.loads(control_data)

        # Semantische Analyse basierend auf CCU-Control-Templates
        analysis = {
            # Grundinformationen
            "command_type": control_data.get("command_type", "UNKNOWN"),
            "command_id": control_data.get("command_id", "N/A"),
            "timestamp": control_data.get("timestamp", "N/A"),
            "status": control_data.get("status", "UNKNOWN"),
            # Steuerungsbefehle
            "action": control_data.get("action", "N/A"),
            "target_module": control_data.get("target_module", "N/A"),
            "parameters": control_data.get("parameters", {}),
            # Auftragssteuerung
            "order_id": control_data.get("order_id", "N/A"),
            "order_type": control_data.get("order_type", "N/A"),
            "priority": control_data.get("priority", "NORMAL"),
            # System-Status
            "execution_status": control_data.get("execution_status", "PENDING"),
            "error_message": control_data.get("error_message", None),
            "has_error": control_data.get("error_message") is not None,
        }

        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der CCU-Control-Analyse: {e}")
        return {}


def show_ccu_control():
    """Zeigt CCU-Control-Informationen"""
    st.subheader("🎮 CCU Control")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # CCU-Control-Topics abonnieren
        mqtt_client.subscribe_many(["ccu/control", "ccu/control/command", "ccu/control/order"])

        # Nachrichten aus Per-Topic-Buffer holen (alle CCU-Control-Topics)
        control_messages = []
        for topic in ["ccu/control", "ccu/control/command", "ccu/control/order"]:
            control_messages.extend(list(mqtt_client.get_buffer(topic)))

        # Nachrichten verarbeiten
        process_ccu_control_messages_from_buffers(control_messages)

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
        # Semantische Analyse der CCU-Control-Daten
        analysis = analyze_ccu_control_data(control_data)

        if analysis:
            # Command-Informationen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🎮 Command-Info")
                command_type = analysis.get("command_type", "UNKNOWN")
                if command_type == "START":
                    st.success(f"✅ **Command:** {command_type}")
                elif command_type == "STOP":
                    st.error(f"❌ **Command:** {command_type}")
                elif command_type == "RESET":
                    st.warning(f"🔄 **Command:** {command_type}")
                else:
                    st.info(f"ℹ️ **Command:** {command_type}")

                action = analysis.get("action", "N/A")
                st.write(f"**Action:** {action}")

                target_module = analysis.get("target_module", "N/A")
                if target_module != "N/A":
                    st.write(f"**Target Module:** {target_module}")

            with col2:
                st.markdown("### 📋 Order-Info")
                order_id = analysis.get("order_id", "N/A")
                if order_id != "N/A":
                    st.write(f"**Order ID:** {order_id}")

                order_type = analysis.get("order_type", "N/A")
                st.write(f"**Order Type:** {order_type}")

                priority = analysis.get("priority", "NORMAL")
                if priority == "HIGH":
                    st.warning(f"🔴 **Priority:** {priority}")
                elif priority == "LOW":
                    st.info(f"🔵 **Priority:** {priority}")
                else:
                    st.write(f"**Priority:** {priority}")

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

            # Parameters (falls vorhanden)
            parameters = analysis.get("parameters", {})
            if parameters:
                st.markdown("### ⚙️ Parameters")
                for key, value in parameters.items():
                    st.write(f"**{key}:** {value}")

            # MessageTemplate Info (falls verfügbar)
            if TEMPLATE_MANAGER_AVAILABLE:
                st.markdown("### 📋 MessageTemplate Bibliothek")
                st.info("✅ MessageTemplate Bibliothek verfügbar - Semantische Analyse aktiv")
            else:
                st.warning("⚠️ MessageTemplate Bibliothek nicht verfügbar - Fallback-Analyse")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw CCU Control Data"):
                st.json(control_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der CCU-Control-Daten")
            st.write("**Raw Data:**")
            st.write(control_data)
    else:
        st.write("**MQTT-Topics:** `ccu/control`, `ccu/control/command`, `ccu/control/order`")
