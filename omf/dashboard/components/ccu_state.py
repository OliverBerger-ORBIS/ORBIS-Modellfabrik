"""
CCU State Komponente

Zeigt CCU-Status und Workflow an.
MQTT-Topics: ccu/state, ccu/state/flow, ccu/state/status, ccu/state/error
"""

from datetime import datetime

import streamlit as st

from omf.dashboard.tools.logging_config import get_logger

logger = get_logger("omf.dashboard.components.ccu_state")

# MessageProcessor entfernt - verwenden jetzt Per-Topic-Buffer
from .validation_error_tracker import get_validation_tracker

# MessageTemplate Bibliothek Import
try:
    from omf.dashboard.tools.registry_manager import get_message_template_manager

    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    logger.debug(f"❌ MessageTemplate Import-Fehler: {e}")
except Exception as e:
    TEMPLATE_MANAGER_AVAILABLE = False
    logger.debug(f"❌ MessageTemplate Fehler: {e}")


def process_ccu_state_messages_from_buffers(state_messages):
    """Verarbeitet CCU-State-Nachrichten aus Per-Topic-Buffer"""
    if not state_messages:
        return

    # Neueste CCU-State-Nachricht finden
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

        # Template-Validierung (falls verfügbar)
        template_validation = None
        if TEMPLATE_MANAGER_AVAILABLE:
            try:
                template_manager = get_message_template_manager()
                # Versuche verschiedene CCU-State-Topics zu validieren
                ccu_topics = ["ccu/state", "ccu/state/status", "ccu/state/config"]
                for topic in ccu_topics:
                    validation_result = template_manager.validate_message(topic, state_data)

                    # Strikte Validierung: Prüfe ob es ein "Auto-analyzed template" ist
                    template = validation_result.get("template", {})
                    template_name = template.get("description", "")
                    is_auto_analyzed = "Auto-analyzed" in template_name

                    if validation_result.get("valid", False) and not is_auto_analyzed:
                        # Auch bei "gültigen" Templates prüfen wir die erwarteten Felder
                        # Das wird später in der Feld-Validierung gemacht
                        template_validation = {
                            "valid": True,
                            "topic": topic,
                            "template": template,
                        }
                        break
                    else:
                        # Fehler zur Historie hinzufügen
                        error_tracker = get_validation_tracker("ccu_state")
                        if is_auto_analyzed:
                            error_msg = (
                                f"Auto-analyzed template erkannt - möglicherweise ungültige Nachricht: {template_name}"
                            )
                        else:
                            error_msg = validation_result.get("error", "Unknown error")

                        error_tracker.add_error(topic, error_msg, state_data)

                        template_validation = {
                            "valid": False,
                            "topic": topic,
                            "errors": validation_result.get("errors", []),
                            "template": template,
                            "error": error_msg,
                            "is_auto_analyzed": is_auto_analyzed,
                        }
                        break

                if not template_validation:
                    template_validation = {
                        "valid": False,
                        "error": "Kein passendes Template gefunden",
                        "tried_topics": ccu_topics,
                    }
                    # Fehler zur Historie hinzufügen
                    error_tracker = get_validation_tracker("ccu_state")
                    error_tracker.add_error("ccu/state", "Kein passendes Template gefunden", state_data)
            except Exception as e:
                template_validation = {
                    "valid": False,
                    "error": f"Template-Validierung fehlgeschlagen: {e}",
                }
                # Fehler zur Historie hinzufügen
                error_tracker = get_validation_tracker("ccu_state")
                error_tracker.add_error("ccu/state", f"Template-Validierung fehlgeschlagen: {e}", state_data)

        # Zusätzliche Validierung: Prüfe erwartete Felder für CCU-State
        # Für ccu/state/status: status, health, active_modules, timestamp
        # Für ccu/state: stockItems, ts
        expected_fields_status = ["status", "health", "active_modules", "timestamp"]
        expected_fields_state = ["stockItems", "ts"]

        # Prüfe ob es ein Status-Template ist
        is_status_template = any(field in state_data for field in expected_fields_status)
        is_state_template = any(field in state_data for field in expected_fields_state)

        missing_fields = []
        if is_status_template:
            missing_fields = [field for field in expected_fields_status if field not in state_data]
        elif is_state_template:
            missing_fields = [field for field in expected_fields_state if field not in state_data]
        else:
            # Keine erwarteten Felder gefunden - das ist ein Problem
            missing_fields = ["Keine erwarteten Felder gefunden"]

        if missing_fields:
            # Fehler zur Historie hinzufügen
            error_tracker = get_validation_tracker("ccu_state")
            error_msg = f"Erwartete Felder fehlen: {', '.join(missing_fields)}"
            error_tracker.add_error("ccu/state", error_msg, state_data)

            # Template-Validierung als ungültig markieren (auch wenn Template "gültig" war)
            if template_validation and template_validation.get("valid", False):
                template_validation = {
                    "valid": False,
                    "topic": template_validation.get("topic", "ccu/state"),
                    "error": error_msg,
                    "missing_fields": missing_fields,
                    "template": template_validation.get("template", {}),
                }

        # Semantische Analyse basierend auf echten CCU-State-Daten (Stock-Items)
        stock_items = state_data.get("stockItems", [])
        timestamp = state_data.get("ts", "N/A")

        # Stock-Items analysieren
        stock_analysis = {
            "total_items": len(stock_items),
            "empty_slots": 0,
            "occupied_slots": 0,
            "reserved_items": 0,
            "raw_items": 0,
            "workpiece_types": {},
            "locations": {},
            "hbw_modules": set(),
        }

        for item in stock_items:
            if isinstance(item, dict):
                location = item.get("location", "UNKNOWN")
                workpiece = item.get("workpiece", {})
                hbw = item.get("hbw", "UNKNOWN")

                # HBW-Module sammeln
                stock_analysis["hbw_modules"].add(hbw)

                # Location-Status
                stock_analysis["locations"][location] = {
                    "hbw": hbw,
                    "workpiece": workpiece,
                    "has_workpiece": bool(workpiece.get("id", "")),
                }

                # Workpiece-Analyse
                if workpiece.get("id", ""):
                    stock_analysis["occupied_slots"] += 1
                    workpiece_type = workpiece.get("type", "UNKNOWN")
                    workpiece_state = workpiece.get("state", "UNKNOWN")

                    # Workpiece-Typen zählen
                    if workpiece_type not in stock_analysis["workpiece_types"]:
                        stock_analysis["workpiece_types"][workpiece_type] = 0
                    stock_analysis["workpiece_types"][workpiece_type] += 1

                    # States zählen
                    if workpiece_state == "RESERVED":
                        stock_analysis["reserved_items"] += 1
                    elif workpiece_state == "RAW":
                        stock_analysis["raw_items"] += 1
                else:
                    stock_analysis["empty_slots"] += 1

        # HBW-Module zu Liste konvertieren
        stock_analysis["hbw_modules"] = list(stock_analysis["hbw_modules"])

        analysis = {
            # Grundinformationen
            "timestamp": timestamp,
            "data_type": "STOCK_ITEMS",
            # Stock-Analyse
            "stock_analysis": stock_analysis,
            # Zusammenfassung
            "total_slots": stock_analysis["total_items"],
            "utilization_percentage": round(
                (stock_analysis["occupied_slots"] / max(stock_analysis["total_items"], 1)) * 100, 1
            ),
            "has_reserved_items": stock_analysis["reserved_items"] > 0,
            "has_raw_items": stock_analysis["raw_items"] > 0,
            "has_empty_slots": stock_analysis["empty_slots"] > 0,
            # Template-Validierung
            "template_validation": template_validation,
        }

        return analysis

    except Exception as e:
        st.warning(f"⚠️ Fehler bei der CCU-State-Analyse: {e}")
        return {}


def show_ccu_state():
    """Zeigt CCU-State-Informationen"""
    st.subheader("📊 CCU State")

    # MQTT-Client für Per-Topic-Buffer
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # CCU-State-Topics abonnieren
        mqtt_client.subscribe_many(["ccu/state", "ccu/state/flow", "ccu/state/status", "ccu/state/error"])

        # Nachrichten aus Per-Topic-Buffer holen (alle CCU-State-Topics)
        state_messages = []
        for topic in ["ccu/state", "ccu/state/flow", "ccu/state/status", "ccu/state/error"]:
            state_messages.extend(list(mqtt_client.get_buffer(topic)))

        # Nachrichten verarbeiten
        process_ccu_state_messages_from_buffers(state_messages)

        # Status-Anzeige
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
            # Data-Type Info
            data_type = analysis.get("data_type", "UNKNOWN")
            st.info(f"📊 **Data Type:** {data_type}")

            # Stock-Overview
            st.markdown("### 📦 Stock Overview")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_slots = analysis.get("total_slots", 0)
                st.write(f"**Total Slots:** {total_slots}")

            with col2:
                occupied_slots = analysis.get("stock_analysis", {}).get("occupied_slots", 0)
                st.write(f"**Occupied:** {occupied_slots}")

            with col3:
                empty_slots = analysis.get("stock_analysis", {}).get("empty_slots", 0)
                st.write(f"**Empty:** {empty_slots}")

            with col4:
                utilization = analysis.get("utilization_percentage", 0)
                st.write(f"**Utilization:** {utilization}%")

            # Workpiece-Typen
            stock_analysis = analysis.get("stock_analysis", {})
            workpiece_types = stock_analysis.get("workpiece_types", {})
            if workpiece_types:
                st.markdown("### 🎨 Workpiece Types")
                col5, col6 = st.columns(2)

                with col5:
                    for wp_type, count in workpiece_types.items():
                        if wp_type == "RED":
                            st.error(f"🔴 **{wp_type}:** {count}")
                        elif wp_type == "WHITE":
                            st.info(f"⚪ **{wp_type}:** {count}")
                        elif wp_type == "BLUE":
                            st.info(f"🔵 **{wp_type}:** {count}")
                        else:
                            st.write(f"**{wp_type}:** {count}")

                with col6:
                    reserved_items = stock_analysis.get("reserved_items", 0)
                    raw_items = stock_analysis.get("raw_items", 0)

                    if reserved_items > 0:
                        st.warning(f"⚠️ **Reserved:** {reserved_items}")
                    if raw_items > 0:
                        st.info(f"📦 **Raw:** {raw_items}")

            # HBW-Module
            hbw_modules = stock_analysis.get("hbw_modules", [])
            if hbw_modules:
                st.markdown("### 🏭 HBW Modules")
                for hbw in hbw_modules:
                    st.write(f"**HBW:** {hbw}")

            # Location-Details
            locations = stock_analysis.get("locations", {})
            if locations:
                st.markdown("### 📍 Location Details")

                # Sortiere Locations (A1, A2, A3, B1, B2, B3, C1, C2, C3)
                sorted_locations = sorted(locations.items(), key=lambda x: (x[0][0], int(x[0][1])))

                for location, details in sorted_locations:
                    with st.expander(f"📍 Location: {location}"):
                        col7, col8 = st.columns(2)

                        with col7:
                            hbw = details.get("hbw", "N/A")
                            st.write(f"**HBW:** {hbw}")

                            has_workpiece = details.get("has_workpiece", False)
                            if has_workpiece:
                                st.success("✅ **Has Workpiece**")
                            else:
                                st.info("📭 **Empty**")

                        with col8:
                            workpiece = details.get("workpiece", {})
                            if workpiece.get("id", ""):
                                wp_id = workpiece.get("id", "N/A")
                                wp_type = workpiece.get("type", "N/A")
                                wp_state = workpiece.get("state", "N/A")

                                st.write(f"**ID:** {wp_id}")
                                st.write(f"**Type:** {wp_type}")
                                st.write(f"**State:** {wp_state}")

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

                    tried_topics = template_validation.get("tried_topics", [])
                    if tried_topics:
                        st.write(f"**Geprüfte Topics:** {', '.join(tried_topics)}")

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
                    st.json(state_data)
            else:
                st.markdown("### 📋 MessageTemplate Bibliothek")
                if TEMPLATE_MANAGER_AVAILABLE:
                    st.info("✅ MessageTemplate Bibliothek verfügbar - Semantische Analyse aktiv")
                else:
                    st.warning("⚠️ MessageTemplate Bibliothek nicht verfügbar - Fallback-Analyse")

            # Validierungsfehler-Historie anzeigen
            error_tracker = get_validation_tracker("ccu_state")
            error_tracker.display_errors()

            # Raw Data (erweiterbar)
            with st.expander("🔍 Raw CCU State Data"):
                st.json(state_data)

        else:
            st.error("❌ Fehler bei der semantischen Analyse der CCU-State-Daten")
            st.write("**Raw Data:**")
            st.write(state_data)
    else:
        st.write("**MQTT-Topics:** `ccu/state`, `ccu/state/flow`, `ccu/state/status`, `ccu/state/error`")
