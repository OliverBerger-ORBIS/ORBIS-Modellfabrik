"""
OMF Dashboard Overview - Modul Status
Exakte Kopie der show_module_status() Funktion aus overview.py
"""

import json
import re
import time
from datetime import datetime

import pandas as pd
import streamlit as st

# Alte message_processor Imports entfernt - verwenden jetzt Per-Topic-Buffer

# Import module manager for static module info
try:
    from src_orbis.omf.tools.module_manager import get_omf_module_manager
except ImportError:
    # Fallback if module manager not available
    get_omf_module_manager = None

# Module configuration and icons (fallback)
MODULE_ICONS = {"MILL": "⚙️", "DRILL": "🔩", "AIQS": "🤖", "HBW": "🏬", "DPS": "📦", "FTS": "🚗", "CHRG": "🔋"}


def get_module_icon(module_name):
    """Get module icon from module name"""
    return MODULE_ICONS.get(module_name.upper(), "❓")


def get_status_icon(status):
    """Get status icon based on status text"""
    status_lower = status.lower()

    if "available" in status_lower or "online" in status_lower:
        return "🟢"
    elif "busy" in status_lower or "processing" in status_lower:
        return "🟡"
    elif "blocked" in status_lower or "error" in status_lower:
        return "🔴"
    elif "charging" in status_lower:
        return "⚡"
    elif "transport" in status_lower or "moving" in status_lower:
        return "🚗"
    elif "maintenance" in status_lower:
        return "🔧"
    elif "idle" in status_lower or "waiting" in status_lower:
        return "😴"
    elif "ready" in status_lower:
        return "🎯"
    else:
        return "⚪"


def get_enhanced_status_display(status, module_type):
    """Get enhanced status display with icons"""
    if not status:
        return f"{get_status_icon('offline')} No Data"

    status_lower = status.lower()

    # Module-specific status mappings
    if module_type == "Transport":
        if "charging" in status_lower:
            return f"{get_status_icon('charging')} Charging"
        elif "moving" in status_lower:
            return f"{get_status_icon('transport')} Moving"
        elif "docked" in status_lower:
            return f"{get_status_icon('ready')} Docked"

    elif module_type == "Storage":
        if "available" in status_lower:
            return f"{get_status_icon('available')} Available"
        elif "full" in status_lower:
            return f"{get_status_icon('blocked')} Full"
        elif "maintenance" in status_lower:
            return f"{get_status_icon('maintenance')} Maintenance"

    elif module_type == "Processing":
        if "available" in status_lower:
            return f"{get_status_icon('available')} Available"
        elif "processing" in status_lower:
            return f"{get_status_icon('busy')} Processing"
        elif "error" in status_lower:
            return f"{get_status_icon('blocked')} Error"
        elif "maintenance" in status_lower:
            return f"{get_status_icon('maintenance')} Maintenance"

    # General status mappings
    if "available" in status_lower or "online" in status_lower:
        return f"{get_status_icon('available')} Available"
    elif "busy" in status_lower or "processing" in status_lower:
        return f"{get_status_icon('busy')} Busy"
    elif "blocked" in status_lower or "error" in status_lower:
        return f"{get_status_icon('blocked')} Blocked"
    elif "charging" in status_lower:
        return f"{get_status_icon('charging')} Charging"
    elif "transport" in status_lower or "moving" in status_lower:
        return f"{get_status_icon('transport')} Transport"
    elif "maintenance" in status_lower:
        return f"{get_status_icon('maintenance')} Maintenance"
    elif "idle" in status_lower or "waiting" in status_lower:
        return f"{get_status_icon('idle')} Idle"
    elif "ready" in status_lower:
        return f"{get_status_icon('ready')} Ready"
    else:
        return f"⚪ {status}"


def get_static_module_info():
    """Get static module information from module manager or fallback"""
    try:
        if get_omf_module_manager:
            module_manager = get_omf_module_manager()
            all_modules = module_manager.get_all_modules()

            # Filter out OVEN (doesn't exist in our factory)
            filtered_modules = {}
            for module_id, module_info in all_modules.items():
                if module_id.upper() != "OVEN":
                    filtered_modules[module_id] = module_info

            return filtered_modules
        else:
            # Fallback to hardcoded modules (without OVEN)
            return {
                "MILL": {
                    "id": "SVR3QA2098",
                    "name": "MILL (Fräse)",
                    "name_lang_de": "MILL (Fräse)",
                    "icon": "⚙️",
                    "type": "Processing",
                    "ip_range": "192.168.0.40",
                    "enabled": True,
                },
                "DRILL": {
                    "id": "SVR4H76449",
                    "name": "DRILL (Bohrer)",
                    "name_lang_de": "DRILL (Bohrer)",
                    "icon": "🔧",
                    "type": "Processing",
                    "ip_range": "192.168.0.50",
                    "enabled": True,
                },
                "AIQS": {
                    "id": "SVR4H76530",
                    "name": "AIQS (Qualitätssicherung)",
                    "name_lang_de": "AIQS (Qualitätssicherung)",
                    "icon": "🔍",
                    "type": "Quality Control",
                    "ip_range": "192.168.0.70",
                    "enabled": True,
                },
                "HBW": {
                    "id": "SVR3QA0022",
                    "name": "HBW (Hochregallager)",
                    "name_lang_de": "HBW (Hochregallager)",
                    "icon": "📦",
                    "type": "Storage",
                    "ip_range": "192.168.0.80",
                    "enabled": True,
                },
                "DPS": {
                    "id": "SVR4H73275",
                    "name": "DPS (Warenein- und -ausgang)",
                    "name_lang_de": "DPS (Warenein- und -ausgang)",
                    "icon": "🚪",
                    "type": "Input/Output",
                    "ip_range": "192.168.0.90",
                    "enabled": True,
                },
                "FTS": {
                    "id": "5iO4",
                    "name": "FTS (Fahrerloses Transportsystem)",
                    "name_lang_de": "FTS (Fahrerloses Transportsystem)",
                    "icon": "🚗",
                    "type": "Transport",
                    "ip_range": "192.168.0.60",
                    "enabled": True,
                },
                "CHRG": {
                    "id": "CHRG0",
                    "name": "CHRG (Ladestation)",
                    "name_lang_de": "CHRG (Ladestation)",
                    "icon": "🔋",
                    "type": "Charging",
                    "ip_range": "192.168.0.65",
                    "enabled": True,
                },
            }
    except Exception as e:
        st.error(f"Fehler beim Laden der Modul-Konfiguration: {e}")
        return {}


def _process_module_messages_from_buffers(state_messages, connection_messages, pairing_messages, module_status_store):
    """Process MQTT messages from Per-Topic-Buffers to update module status store"""

    # Topic patterns for module status
    connection_pattern = re.compile(r"^module/v1/ff/(?P<module_id>[^/]+)/connection$")
    state_pattern = re.compile(r"^module/v1/ff/(?P<module_id>[^/]+)/state$")
    pairing_pattern = re.compile(r"^ccu/pairing/state$")

    # Process all message types
    all_messages = state_messages + connection_messages + pairing_messages
    
    for msg in all_messages:
        try:
            topic = msg.get("topic", "")
            payload = msg.get("payload", {})
            ts = msg.get("ts", time.time())

            if isinstance(payload, str):
                payload = json.loads(payload)

            # Process connection messages
            connection_match = connection_pattern.match(topic)
            if connection_match:
                module_id = connection_match.group("module_id")
                if module_id not in module_status_store:
                    module_status_store[module_id] = {}

                connection_state = payload.get("connectionState", "OFFLINE")
                module_status_store[module_id]["connection"] = connection_state
                module_status_store[module_id]["last_update"] = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                module_status_store[module_id]["message_count"] = (
                    module_status_store[module_id].get("message_count", 0) + 1
                )

            # Process state messages
            state_match = state_pattern.match(topic)
            if state_match:
                module_id = state_match.group("module_id")
                if module_id not in module_status_store:
                    module_status_store[module_id] = {}

                module_state = payload.get("state", "Unknown")
                module_status_store[module_id]["state"] = module_state
                module_status_store[module_id]["last_update"] = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                module_status_store[module_id]["message_count"] = (
                    module_status_store[module_id].get("message_count", 0) + 1
                )

            # Process factsheet messages
            factsheet_match = factsheet_pattern.match(topic)
            if factsheet_match:
                module_id = factsheet_match.group("module_id")
                if module_id not in module_status_store:
                    module_status_store[module_id] = {}

                module_status_store[module_id]["factsheet"] = payload
                module_status_store[module_id]["last_update"] = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                module_status_store[module_id]["message_count"] = (
                    module_status_store[module_id].get("message_count", 0) + 1
                )

            # Process ccu/pairing/state messages (NEU - korrekte Availability-Daten)
            pairing_match = pairing_pattern.match(topic)
            if pairing_match:
                # Parse ccu/pairing/state payload
                modules = payload.get("modules", [])
                for module in modules:
                    serial_number = module.get("serialNumber", "")
                    if not serial_number:
                        continue

                    # Initialize module in store if not exists
                    if serial_number not in module_status_store:
                        module_status_store[serial_number] = {}

                    # Update module status with real data from ccu/pairing/state
                    module_status_store[serial_number]["connected"] = module.get("connected", False)
                    module_status_store[serial_number]["available"] = module.get("available", "Unknown")
                    module_status_store[serial_number]["assigned"] = module.get("assigned", False)
                    module_status_store[serial_number]["ip"] = module.get("ip", "Unknown")
                    module_status_store[serial_number]["subType"] = module.get("subType", "Unknown")
                    module_status_store[serial_number]["version"] = module.get("version", "Unknown")
                    module_status_store[serial_number]["hasCalibration"] = module.get("hasCalibration", False)
                    module_status_store[serial_number]["lastSeen"] = module.get("lastSeen", "")
                    module_status_store[serial_number]["last_update"] = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    module_status_store[serial_number]["message_count"] = (
                        module_status_store[serial_number].get("message_count", 0) + 1
                    )

                # Also process transports if available
                transports = payload.get("transports", [])
                for transport in transports:
                    serial_number = transport.get("serialNumber", "")
                    if not serial_number:
                        continue

                    # Initialize transport in store if not exists
                    if serial_number not in module_status_store:
                        module_status_store[serial_number] = {}

                    # Update transport status
                    module_status_store[serial_number]["connected"] = transport.get("connected", False)
                    module_status_store[serial_number]["available"] = transport.get("available", "Unknown")
                    module_status_store[serial_number]["ip"] = transport.get("ip", "Unknown")
                    module_status_store[serial_number]["subType"] = "FTS"
                    module_status_store[serial_number]["version"] = transport.get("version", "Unknown")
                    module_status_store[serial_number]["batteryPercentage"] = transport.get("batteryPercentage", 0)
                    module_status_store[serial_number]["batteryVoltage"] = transport.get("batteryVoltage", 0)
                    module_status_store[serial_number]["charging"] = transport.get("charging", False)
                    module_status_store[serial_number]["lastSeen"] = transport.get("lastSeen", "")
                    module_status_store[serial_number]["last_update"] = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    module_status_store[serial_number]["message_count"] = (
                        module_status_store[serial_number].get("message_count", 0) + 1
                    )

        except Exception:
            continue


def _get_module_real_time_status(module_id, module_status_store):
    """Get real-time status for a specific module"""
    if module_id not in module_status_store:
        return {"connection": "OFFLINE", "state": "Unknown", "message_count": 0, "last_update": "Never"}

    return module_status_store[module_id]


def show_overview_module_status():
    """Show module status overview - Exakte Kopie von show_module_status() aus overview.py"""
    st.subheader("🏭 Modul-Status")
    st.markdown("Übersicht aller APS-Module mit Status und Verbindungsinformationen")

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return
    
    # Abonniere die benötigten Topics für Per-Topic-Buffer
    client.subscribe_many([
        "module/v1/ff/+/state",
        "module/v1/ff/+/connection", 
        "ccu/pairing/state"
    ])

    # Status wird automatisch aktualisiert - kein Button nötig
    st.info("💡 **Status wird automatisch aus MQTT-Nachrichten aktualisiert**")

    # Get static module information
    all_modules = get_static_module_info()

    if not all_modules:
        st.error("❌ Keine Module konfiguriert")
        return

    # Initialize module status store in session state
    if "module_status_store" not in st.session_state:
        st.session_state["module_status_store"] = {}
    if "module_status_last_count" not in st.session_state:
        st.session_state["module_status_last_count"] = 0

    # Subscribe to ccu/pairing/state for real-time module status
    # Alte Subscribe-Aufrufe entfernt - verwenden jetzt subscribe_many()

    # NEUES PATTERN: Per-Topic-Buffer für Modul-Status
    try:
        # Hole die letzten Nachrichten aus den Per-Topic-Buffern
        state_messages = list(client.get_buffer("module/v1/ff/+/state"))
        connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
        pairing_messages = list(client.get_buffer("ccu/pairing/state"))
        
        total_messages = len(state_messages) + len(connection_messages) + len(pairing_messages)
        if total_messages > 0:
            st.info(f"📊 **{total_messages} Nachrichten in Buffern** (State: {len(state_messages)}, Connection: {len(connection_messages)}, Pairing: {len(pairing_messages)})")
            
            # Verarbeite die Nachrichten aus den Buffern
            _process_module_messages_from_buffers(
                state_messages, 
                connection_messages, 
                pairing_messages, 
                st.session_state["module_status_store"]
            )

    except Exception as e:
        st.warning(f"⚠️ Fehler beim Zugriff auf Per-Topic-Buffer: {e}")

    # Create module table data with real-time status
    module_table_data = []

    for module_id, module_info in all_modules.items():
        # Skip disabled modules
        if not module_info.get("enabled", True):
            continue

        # Get real-time status from store
        real_time_status = _get_module_real_time_status(module_id, st.session_state["module_status_store"])

        # Get module icon
        icon_display = module_info.get("icon", get_module_icon(module_id))

        # Get display name
        display_name = module_info.get("name_lang_de", module_info.get("name", module_id))

        # Status indicators - NEU: Verwende echte Daten aus ccu/pairing/state
        connected = real_time_status.get("connected", False)
        connection_display = (
            f"{get_status_icon('available')} Connected" if connected else f"{get_status_icon('offline')} Disconnected"
        )

        # Availability-Status aus ccu/pairing/state
        available = real_time_status.get("available", "Unknown")
        if available == "READY":
            availability_display = f"{get_status_icon('available')} Verfügbar"
        elif available == "BUSY":
            availability_display = f"{get_status_icon('busy')} Beschäftigt"
        elif available == "BLOCKED":
            availability_display = f"{get_status_icon('blocked')} Blockiert"
        else:
            availability_display = f"⚪ {available}"

        recent_messages = real_time_status.get("message_count", 0)

        # IP-Adresse aus echten Daten oder Fallback
        ip_address = real_time_status.get("ip", module_info.get("ip_range", "Unknown"))

        module_table_data.append(
            {
                "Name": f"{icon_display} {display_name}",
                "ID": module_info["id"],
                "Type": module_info.get("type", "Unknown"),
                "IP": ip_address,
                "Connected": connection_display,
                "Availability Status": availability_display,
                "Recent Messages": recent_messages,
                "Last Update": real_time_status.get("last_update", "Never"),
            }
        )

    # Create DataFrame and display table
    if module_table_data:
        module_df = pd.DataFrame(module_table_data)

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_modules = len(module_table_data)
            st.metric("Gesamt Module", total_modules)

        with col2:
            connected_modules = len([m for m in module_table_data if "Connected" in m["Connected"]])
            st.metric("Verbunden", connected_modules)

        with col3:
            active_modules = len(
                [
                    m
                    for m in module_table_data
                    if "Active" in m["Availability Status"] or "Available" in m["Availability Status"]
                ]
            )
            st.metric("Aktiv", active_modules)

        with col4:
            total_messages = sum([m["Recent Messages"] for m in module_table_data])
            st.metric("Nachrichten", total_messages)

        # Display module table
        st.dataframe(
            module_df,
            use_container_width=True,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "ID": st.column_config.TextColumn("ID", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="medium"),
                "IP": st.column_config.TextColumn("IP", width="medium"),
                "Connected": st.column_config.TextColumn("Connected", width="medium"),
                "Availability Status": st.column_config.TextColumn("Availability Status", width="medium"),
                "Recent Messages": st.column_config.NumberColumn("Recent Messages", width="small"),
                "Last Update": st.column_config.TextColumn("Last Update", width="medium"),
            },
        )

        # Status wird automatisch aktualisiert
        st.success("✅ **Modul-Status wird automatisch aus MQTT-Nachrichten aktualisiert**")

    else:
        st.warning("⚠️ Keine aktiven Module gefunden")
