"""
CCU Pairing Komponente

Zeigt Modul-Pairing-Status an.
MQTT-Topic: ccu/pairing/state
"""

from datetime import datetime

import streamlit as st

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer
from .validation_error_tracker import get_validation_tracker

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


def process_ccu_pairing_messages_from_buffers(pairing_messages):
    """Verarbeitet CCU-Pairing-Nachrichten aus Per-Topic-Buffer"""
    if not pairing_messages:
        return

    # Neueste CCU-Pairing-Nachricht finden
    if pairing_messages:
        latest_pairing_msg = max(pairing_messages, key=lambda x: x.get("ts", 0))
        # Pairing-Daten in Session-State speichern
        st.session_state["ccu_pairing_data"] = latest_pairing_msg.get("payload", {})
        # Timestamp für letzte Aktualisierung speichern
        st.session_state["ccu_pairing_last_update"] = latest_pairing_msg.get("ts", 0)


def get_formatted_timestamp(timestamp):
    """Timestamp in lesbares Format konvertieren"""
    if not timestamp:
        return "Nie aktualisiert"

    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except (ValueError, OSError):
        return f"Timestamp: {timestamp}"


def analyze_ccu_pairing_data(pairing_data):
    """Analysiert CCU-Pairing-Daten semantisch basierend auf RAW-Data-Struktur"""
    if not pairing_data:
        return {}

    try:
        import json

        if isinstance(pairing_data, str):
            pairing_data = json.loads(pairing_data)

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche CCU-Pairing-Topic zu validieren
                validation_result = template_manager.validate_message("ccu/pairing/state", pairing_data)

                # Strikte Validierung: Prüfe ob es ein "Auto-analyzed template" ist
                template = validation_result.get("template", {})
                template_name = template.get("description", "")
                is_auto_analyzed = "Auto-analyzed" in template_name

                if validation_result.get("valid", False) and not is_auto_analyzed:
                    template_validation = {
                        "valid": True,
                        "topic": "ccu/pairing/state",
                        "template": template,
                    }
                else:
                    # Fehler zur Historie hinzufügen
                    error_tracker = get_validation_tracker("ccu_pairing")
                    if is_auto_analyzed:
                        error_msg = (
                            f"Auto-analyzed template erkannt - möglicherweise ungültige Nachricht: {template_name}"
                        )
                    else:
                        error_msg = validation_result.get("error", "Unknown error")

                    error_tracker.add_error("ccu/pairing/state", error_msg, pairing_data)

                    template_validation = {
                        "valid": False,
                        "topic": "ccu/pairing/state",
                        "errors": validation_result.get("errors", []),
                        "template": template,
                        "error": error_msg,
                        "is_auto_analyzed": is_auto_analyzed,
                    }
            except Exception as e:
                # Fehler zur Historie hinzufügen
                error_tracker = get_validation_tracker("ccu_pairing")
                error_tracker.add_error("ccu/pairing/state", f"Template-Validierung fehlgeschlagen: {e}", pairing_data)

                template_validation = {
                    "valid": False,
                    "error": f"Template-Validierung fehlgeschlagen: {e}",
                }

        # Zusätzliche Validierung: Prüfe erwartete Felder für CCU-Pairing
        expected_fields = ["modules", "transports"]
        missing_fields = [field for field in expected_fields if field not in pairing_data]

        if missing_fields:
            # Fehler zur Historie hinzufügen
            error_tracker = get_validation_tracker("ccu_pairing")
            error_msg = f"Erwartete Felder fehlen: {', '.join(missing_fields)}"
            error_tracker.add_error("ccu/pairing/state", error_msg, pairing_data)

            # Template-Validierung als ungültig markieren
            if template_validation and template_validation.get("valid", False):
                template_validation = {
                    "valid": False,
                    "topic": "ccu/pairing/state",
                    "error": error_msg,
                    "missing_fields": missing_fields,
                }

        # Semantische Analyse basierend auf echten CCU-Pairing-Daten
        modules = pairing_data.get("modules", [])
        transports = pairing_data.get("transports", [])

        # Module analysieren
        module_details = {}
        connected_modules = 0
        available_modules = 0
        busy_modules = 0
        ready_modules = 0

        for module in modules:
            if isinstance(module, dict):
                serial_number = module.get("serialNumber", "UNKNOWN")
                module_details[serial_number] = {
                    "type": module.get("type", "UNKNOWN"),
                    "sub_type": module.get("subType", "UNKNOWN"),
                    "connected": module.get("connected", False),
                    "available": module.get("available", "UNKNOWN"),
                    "assigned": module.get("assigned", False),
                    "ip_address": module.get("ip", "N/A"),
                    "version": module.get("version", "N/A"),
                    "last_seen": module.get("lastSeen", "N/A"),
                    "paired_since": module.get("pairedSince", "N/A"),
                    "has_calibration": module.get("hasCalibration", False),
                    "production_duration": module.get("productionDuration", "N/A"),
                }

                # Statistiken sammeln
                if module.get("connected", False):
                    connected_modules += 1
                if module.get("available") == "READY":
                    ready_modules += 1
                elif module.get("available") == "BUSY":
                    busy_modules += 1
                if module.get("available") in ["READY", "BUSY"]:
                    available_modules += 1

        # Transports analysieren (FTS)
        transport_details = {}
        for transport in transports:
            if isinstance(transport, dict):
                serial_number = transport.get("serialNumber", "UNKNOWN")
                transport_details[serial_number] = {
                    "type": transport.get("type", "UNKNOWN"),
                    "connected": transport.get("connected", False),
                    "available": transport.get("available", "UNKNOWN"),
                    "ip_address": transport.get("ip", "N/A"),
                    "version": transport.get("version", "N/A"),
                    "last_seen": transport.get("lastSeen", "N/A"),
                    "paired_since": transport.get("pairedSince", "N/A"),
                    "charging": transport.get("charging", False),
                    "battery_voltage": transport.get("batteryVoltage", "N/A"),
                    "battery_percentage": transport.get("batteryPercentage", "N/A"),
                    "last_node_id": transport.get("lastNodeId", "N/A"),
                    "last_module_serial": transport.get("lastModuleSerialNumber", "N/A"),
                    "last_load_position": transport.get("lastLoadPosition", "N/A"),
                }

        analysis = {
            # Grundinformationen
            "total_modules": len(modules),
            "total_transports": len(transports),
            "connected_modules": connected_modules,
            "available_modules": available_modules,
            "ready_modules": ready_modules,
            "busy_modules": busy_modules,
            # Modul-Details
            "module_details": module_details,
            "transport_details": transport_details,
            # Verfügbarkeit
            "overall_availability": "GOOD" if available_modules > 0 else "POOR",
            "connection_status": "CONNECTED" if connected_modules > 0 else "DISCONNECTED",
            # Template-Validierung
            "template_validation": template_validation,
        }

        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der CCU-Pairing-Analyse: {e}")
        return {}


def show_ccu_pairing():
    """Zeigt CCU-Pairing-Informationen"""
    st.subheader("🔗 CCU Pairing")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # CCU-Pairing-Topic abonnieren
        mqtt_client.subscribe_many(["ccu/pairing/state"])
        
        # Nachrichten aus Per-Topic-Buffer holen
        pairing_messages = list(mqtt_client.get_buffer("ccu/pairing/state"))
        
        # Nachrichten verarbeiten
        process_ccu_pairing_messages_from_buffers(pairing_messages)

        # Status-Anzeige
        last_update_timestamp = st.session_state.get("ccu_pairing_last_update")
        if last_update_timestamp:
            formatted_time = get_formatted_timestamp(last_update_timestamp)
            st.success(f"✅ CCU Pairing aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine CCU-Pairing-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - CCU Pairing wird nicht aktualisiert")

    # Pairing-Daten anzeigen
    pairing_data = st.session_state.get("ccu_pairing_data")

    if pairing_data:
        # Semantische Analyse der CCU-Pairing-Daten
        analysis = analyze_ccu_pairing_data(pairing_data)

        if analysis:
            # Overall Status
            st.markdown("### 🔗 Overall Status")
            overall_availability = analysis.get("overall_availability", "UNKNOWN")
            if overall_availability == "GOOD":
                st.success(f"✅ **Availability:** {overall_availability}")
            elif overall_availability == "POOR":
                st.error(f"❌ **Availability:** {overall_availability}")
            else:
                st.write(f"**Availability:** {overall_availability}")

            connection_status = analysis.get("connection_status", "UNKNOWN")
            if connection_status == "CONNECTED":
                st.success(f"✅ **Connection:** {connection_status}")
            elif connection_status == "DISCONNECTED":
                st.error(f"❌ **Connection:** {connection_status}")
            else:
                st.write(f"**Connection:** {connection_status}")

            # Modul-Statistiken
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("### 📊 Module Statistics")
                total_modules = analysis.get("total_modules", 0)
                st.write(f"**Total Modules:** {total_modules}")

            with col2:
                connected_modules = analysis.get("connected_modules", 0)
                st.write(f"**Connected:** {connected_modules}")

            with col3:
                ready_modules = analysis.get("ready_modules", 0)
                st.write(f"**Ready:** {ready_modules}")

            with col4:
                busy_modules = analysis.get("busy_modules", 0)
                st.write(f"**Busy:** {busy_modules}")

            # Transport-Statistiken
            total_transports = analysis.get("total_transports", 0)
            if total_transports > 0:
                st.markdown("### 🚛 Transport Statistics")
                st.write(f"**Total Transports:** {total_transports}")

            # Modul-Details
            module_details = analysis.get("module_details", {})
            if module_details:
                st.markdown("### 📋 Module Details")
                for module_id, details in module_details.items():
                    with st.expander(f"🔧 {details.get('sub_type', 'MODULE')}: {module_id}"):
                        col5, col6 = st.columns(2)

                        with col5:
                            availability = details.get("available", "UNKNOWN")
                            if availability == "READY":
                                st.success(f"✅ **Availability:** {availability}")
                            elif availability == "BUSY":
                                st.warning(f"⚠️ **Availability:** {availability}")
                            else:
                                st.write(f"**Availability:** {availability}")

                            connected = details.get("connected", False)
                            if connected:
                                st.success(f"✅ **Connected:** {connected}")
                            else:
                                st.error(f"❌ **Connected:** {connected}")

                            assigned = details.get("assigned", False)
                            if assigned:
                                st.info(f"📋 **Assigned:** {assigned}")

                        with col6:
                            ip_address = details.get("ip_address", "N/A")
                            if ip_address != "N/A":
                                st.write(f"**IP Address:** {ip_address}")

                            version = details.get("version", "N/A")
                            if version != "N/A":
                                st.write(f"**Version:** {version}")

                            last_seen = details.get("last_seen", "N/A")
                            if last_seen != "N/A":
                                st.write(f"**Last Seen:** {last_seen}")

                            has_calibration = details.get("has_calibration", False)
                            if has_calibration:
                                st.success("✅ **Calibrated**")
                            else:
                                st.warning("⚠️ **Not Calibrated**")

            # Transport-Details (FTS)
            transport_details = analysis.get("transport_details", {})
            if transport_details:
                st.markdown("### 🚛 Transport Details")
                for transport_id, details in transport_details.items():
                    with st.expander(f"🚛 {details.get('type', 'TRANSPORT')}: {transport_id}"):
                        col7, col8 = st.columns(2)

                        with col7:
                            availability = details.get("available", "UNKNOWN")
                            if availability == "READY":
                                st.success(f"✅ **Availability:** {availability}")
                            elif availability == "BUSY":
                                st.warning(f"⚠️ **Availability:** {availability}")
                            else:
                                st.write(f"**Availability:** {availability}")

                            connected = details.get("connected", False)
                            if connected:
                                st.success(f"✅ **Connected:** {connected}")
                            else:
                                st.error(f"❌ **Connected:** {connected}")

                            charging = details.get("charging", False)
                            if charging:
                                st.info("🔋 **Charging**")
                            else:
                                st.write("🔋 **Not Charging**")

                        with col8:
                            ip_address = details.get("ip_address", "N/A")
                            if ip_address != "N/A":
                                st.write(f"**IP Address:** {ip_address}")

                            battery_percentage = details.get("battery_percentage", "N/A")
                            if battery_percentage != "N/A":
                                st.write(f"**Battery:** {battery_percentage}%")

                            last_node_id = details.get("last_node_id", "N/A")
                            if last_node_id != "N/A":
                                st.write(f"**Last Node:** {last_node_id}")

                            last_load_position = details.get("last_load_position", "N/A")
                            if last_load_position != "N/A":
                                st.write(f"**Load Position:** {last_load_position}")

            # Template-Validierung
            template_validation = analysis.get("template_validation")

            # Template-Validierung
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

                    # Zeige Auto-analyzed Template Warnung
                    if template_validation.get("is_auto_analyzed", False):
                        st.warning(
                            "⚠️ **Auto-analyzed Template erkannt** - Diese Nachricht entspricht möglicherweise nicht dem erwarteten Schema!"
                        )

                    # Zeige fehlende Felder
                    missing_fields = template_validation.get("missing_fields", [])
                    if missing_fields:
                        st.error(f"❌ **Fehlende Felder:** {', '.join(missing_fields)}")

                    # Zeige Original Payload bei Validierungsfehlern
                    st.markdown("#### 📄 Original Payload:")
                    st.json(pairing_data)

            # Validierungsfehler-Historie anzeigen
            error_tracker = get_validation_tracker("ccu_pairing")
            error_tracker.display_errors()

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw CCU Pairing Data"):
                st.json(pairing_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der CCU-Pairing-Daten")
            st.write("**Raw Data:**")
            st.write(pairing_data)
    else:
        st.write("**MQTT-Topic:** `ccu/pairing/state`")
