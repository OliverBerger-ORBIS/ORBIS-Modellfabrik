"""
CCU Status Komponente

Zeigt CCU-Verbindungs- und Gesundheitsstatus an.
MQTT-Topics: ccu/status, ccu/status/connection, ccu/status/health
"""

from datetime import datetime

import streamlit as st

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer

def process_ccu_status_messages_from_buffers(status_messages):
    """Verarbeitet CCU-Status-Nachrichten aus Per-Topic-Buffer"""
    if not status_messages:
        return

    # Neueste CCU-Status-Nachricht finden
    if status_messages:
        latest_status_msg = max(status_messages, key=lambda x: x.get("ts", 0))
        # Status-Daten in Session-State speichern
        st.session_state["ccu_status_data"] = latest_status_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["ccu_status_last_update"] = latest_status_msg.get("ts", 0)

def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"

def analyze_ccu_status_data(status_data):
    """Analysiert CCU-Status-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not status_data:
        return {}

    try:
        import json

        if isinstance(status_data, str):
            status_data = json.loads(status_data)

        # Semantische Analyse basierend auf CCU-Status-Templates
        analysis = {
            # Grundinformationen
            "status_type": status_data.get("status_type", "UNKNOWN"),
            "status_id": status_data.get("status_id", "N/A"),
            "timestamp": status_data.get("timestamp", "N/A"),
            "overall_status": status_data.get("overall_status", "UNKNOWN"),
            # Verbindungsstatus
            "connection_status": status_data.get("connection_status", "UNKNOWN"),
            "connection_quality": status_data.get("connection_quality", "N/A"),
            "last_connection": status_data.get("last_connection", "N/A"),
            "connection_errors": status_data.get("connection_errors", []),
            "has_connection_errors": len(status_data.get("connection_errors", [])) > 0,
            # Gesundheitsstatus
            "health_status": status_data.get("health_status", "UNKNOWN"),
            "health_score": status_data.get("health_score", 0),
            "health_issues": status_data.get("health_issues", []),
            "has_health_issues": len(status_data.get("health_issues", [])) > 0,
            # System-Informationen
            "uptime": status_data.get("uptime", "N/A"),
            "memory_usage": status_data.get("memory_usage", 0),
            "cpu_usage": status_data.get("cpu_usage", 0),
            "disk_usage": status_data.get("disk_usage", 0),
        }

        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der CCU-Status-Analyse: {e}")
        return {}

def show_ccu_status():
    """Zeigt CCU-Status-Informationen"""
    st.subheader("🔗 CCU Status")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # CCU-Status-Topics abonnieren
        mqtt_client.subscribe_many(["ccu/status", "ccu/status/connection", "ccu/status/health"])

        # Nachrichten aus Per-Topic-Buffer holen (alle CCU-Status-Topics)
        status_messages = []
        for topic in ["ccu/status", "ccu/status/connection", "ccu/status/health"]:
            status_messages.extend(list(mqtt_client.get_buffer(topic)))

        # Nachrichten verarbeiten
        process_ccu_status_messages_from_buffers(status_messages)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("ccu_status_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ CCU Status aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine CCU-Status-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - CCU Status wird nicht aktualisiert")

    # Status-Daten anzeigen
    status_data = st.session_state.get("ccu_status_data")

    if status_data:
        # Semantische Analyse der CCU-Status-Daten
        analysis = analyze_ccu_status_data(status_data)

        if analysis:
            # Overall Status
            st.markdown("### 🏭 Overall Status")
            overall_status = analysis.get("overall_status", "UNKNOWN")
            if overall_status == "HEALTHY":
                st.success(f"✅ **Status:** {overall_status}")
            elif overall_status == "WARNING":
                st.warning(f"⚠️ **Status:** {overall_status}")
            elif overall_status == "CRITICAL":
                st.error(f"🔴 **Status:** {overall_status}")
            else:
                st.info(f"ℹ️ **Status:** {overall_status}")

            # Status-Informationen
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔗 Connection Status")
                connection_status = analysis.get("connection_status", "UNKNOWN")
                if connection_status == "CONNECTED":
                    st.success(f"✅ **Connection:** {connection_status}")
                elif connection_status == "DISCONNECTED":
                    st.error(f"❌ **Connection:** {connection_status}")
                elif connection_status == "RECONNECTING":
                    st.warning(f"🔄 **Connection:** {connection_status}")
                else:
                    st.info(f"ℹ️ **Connection:** {connection_status}")

                connection_quality = analysis.get("connection_quality", "N/A")
                if connection_quality != "N/A":
                    st.write(f"**Quality:** {connection_quality}")

                last_connection = analysis.get("last_connection", "N/A")
                if last_connection != "N/A":
                    st.write(f"**Last Connection:** {last_connection}")

            with col2:
                st.markdown("### 🏥 Health Status")
                health_status = analysis.get("health_status", "UNKNOWN")
                if health_status == "GOOD":
                    st.success(f"🟢 **Health:** {health_status}")
                elif health_status == "WARNING":
                    st.warning(f"🟡 **Health:** {health_status}")
                elif health_status == "CRITICAL":
                    st.error(f"🔴 **Health:** {health_status}")
                else:
                    st.info(f"ℹ️ **Health:** {health_status}")

                health_score = analysis.get("health_score", 0)
                if health_score > 0:
                    st.write(f"**Health Score:** {health_score}/100")

            # System-Informationen
            st.markdown("### 💻 System Info")
            col3, col4 = st.columns(2)

            with col3:
                uptime = analysis.get("uptime", "N/A")
                if uptime != "N/A":
                    st.write(f"**Uptime:** {uptime}")

                memory_usage = analysis.get("memory_usage", 0)
                if memory_usage > 0:
                    st.write(f"**Memory Usage:** {memory_usage}%")

            with col4:
                cpu_usage = analysis.get("cpu_usage", 0)
                if cpu_usage > 0:
                    st.write(f"**CPU Usage:** {cpu_usage}%")

                disk_usage = analysis.get("disk_usage", 0)
                if disk_usage > 0:
                    st.write(f"**Disk Usage:** {disk_usage}%")

            # Connection Errors
            has_connection_errors = analysis.get("has_connection_errors", False)
            if has_connection_errors:
                st.markdown("### ❌ Connection Errors")
                connection_errors = analysis.get("connection_errors", [])
                for i, error in enumerate(connection_errors, 1):
                    st.write(f"{i}. {error}")

            # Health Issues
            has_health_issues = analysis.get("has_health_issues", False)
            if has_health_issues:
                st.markdown("### ⚠️ Health Issues")
                health_issues = analysis.get("health_issues", [])
                for i, issue in enumerate(health_issues, 1):
                    st.write(f"{i}. {issue}")

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw CCU Status Data"):
                st.json(status_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der CCU-Status-Daten")
            st.write("**Raw Data:**")
            st.write(status_data)
    else:
        st.write("**MQTT-Topics:** `ccu/status`, `ccu/status/connection`, `ccu/status/health`")
