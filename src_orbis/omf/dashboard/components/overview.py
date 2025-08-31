"""
OMF Dashboard Overview Components
Version: 3.0.0
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st


class OrderManager:
    """Manager für Bestellungen und Lagerbestand"""

    def __init__(self):
        self.inventory = {
            "A1": None,
            "A2": None,
            "A3": None,
            "B1": None,
            "B2": None,
            "B3": None,
            "C1": None,
            "C2": None,
            "C3": None,
        }
        self.workpiece_types = ["ROT", "BLAU", "WEISS"]
        self.orders = []

    def update_inventory_from_messages(self, messages):
        """Lagerbestand aus MQTT-Nachrichten aktualisieren"""
        for msg in messages:
            try:
                payload = msg.get("payload", "")
                if isinstance(payload, str):
                    payload = json.loads(payload)

                # HBW-spezifische Nachrichten verarbeiten
                if "hbw" in msg.get("topic", "").lower():
                    self._process_hbw_message(payload)

            except (json.JSONDecodeError, KeyError, AttributeError):
                continue

    def _process_hbw_message(self, payload):
        """HBW-Nachricht verarbeiten und Lagerbestand aktualisieren"""
        if not isinstance(payload, dict):
            return

        # Verschiedene HBW-Nachrichtenformate verarbeiten
        if "positions" in payload:
            # Format: {"positions": {"A1": "ROT", "B2": "BLAU", ...}}
            for position, workpiece in payload["positions"].items():
                if position in self.inventory:
                    self.inventory[position] = workpiece if workpiece else None

        elif "position" in payload and "workpiece" in payload:
            # Format: {"position": "A1", "workpiece": "ROT"}
            position = payload.get("position")
            workpiece = payload.get("workpiece")
            if position in self.inventory:
                self.inventory[position] = workpiece if workpiece else None

        elif "status" in payload:
            # Format: {"status": "A1:ROT,B2:BLAU,C3:WEISS"}
            status_str = payload.get("status", "")
            for pos_workpiece in status_str.split(","):
                if ":" in pos_workpiece:
                    pos, wp = pos_workpiece.split(":", 1)
                    if pos in self.inventory:
                        self.inventory[pos] = wp if wp else None

    def get_available_workpieces(self):
        """Verfügbare Werkstücke für Bestellungen zurückgeben"""
        available = {}
        for workpiece_type in self.workpiece_types:
            count = sum(1 for pos, wp in self.inventory.items() if wp == workpiece_type)
            if count > 0:
                available[workpiece_type] = count
        return available

    def can_fulfill_order(self, workpiece_type, quantity=1):
        """Prüfen ob Bestellung erfüllt werden kann"""
        available = self.get_available_workpieces()
        return available.get(workpiece_type, 0) >= quantity

    def place_order(self, workpiece_type, quantity=1):
        """Bestellung aufgeben"""
        if self.can_fulfill_order(workpiece_type, quantity):
            order = {
                "id": f"ORDER_{len(self.orders) + 1:04d}",
                "workpiece_type": workpiece_type,
                "quantity": quantity,
                "status": "pending",
                "timestamp": datetime.now(),
                "positions": [],
            }

            # Verfügbare Positionen für diese Bestellung finden
            for pos, wp in self.inventory.items():
                if wp == workpiece_type and len(order["positions"]) < quantity:
                    order["positions"].append(pos)

            self.orders.append(order)
            return order
        else:
            return None


def show_inventory_grid():
    """3x3 Lagerbestand-Raster anzeigen"""
    st.subheader("📚 Lagerbestand - HBW Übersicht")
    st.markdown("Aktuelle Belegung des Hochregallagers (3x3 Raster)")

    # OrderManager initialisieren
    if "order_manager" not in st.session_state:
        st.session_state.order_manager = OrderManager()

    order_manager = st.session_state.order_manager

    # Lagerbestand aus Nachrichten aktualisieren
    if "message_monitor" in st.session_state:
        message_monitor = st.session_state.message_monitor
        order_manager.update_inventory_from_messages(message_monitor.received_messages)

    # 3x3 Raster erstellen
    st.markdown("### 🏗️ Lagerpositionen (A1-C3)")

    # Grid-Layout mit 3 Spalten
    col1, col2, col3 = st.columns(3)

    # Zeile A
    with col1:
        st.markdown("**A1**")
        a1_status = order_manager.inventory["A1"]
        if a1_status:
            if a1_status == "ROT":
                st.markdown("🔴 ROT")
            elif a1_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif a1_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    with col2:
        st.markdown("**A2**")
        a2_status = order_manager.inventory["A2"]
        if a2_status:
            if a2_status == "ROT":
                st.markdown("🔴 ROT")
            elif a2_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif a2_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    with col3:
        st.markdown("**A3**")
        a3_status = order_manager.inventory["A3"]
        if a3_status:
            if a3_status == "ROT":
                st.markdown("🔴 ROT")
            elif a3_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif a3_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    # Zeile B
    with col1:
        st.markdown("**B1**")
        b1_status = order_manager.inventory["B1"]
        if b1_status:
            if b1_status == "ROT":
                st.markdown("🔴 ROT")
            elif b1_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif b1_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    with col2:
        st.markdown("**B2**")
        b2_status = order_manager.inventory["B2"]
        if b2_status:
            if b2_status == "ROT":
                st.markdown("🔴 ROT")
            elif b2_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif b2_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    with col3:
        st.markdown("**B3**")
        b3_status = order_manager.inventory["B3"]
        if b3_status:
            if b3_status == "ROT":
                st.markdown("🔴 ROT")
            elif b3_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif b3_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    # Zeile C
    with col1:
        st.markdown("**C1**")
        c1_status = order_manager.inventory["C1"]
        if c1_status:
            if c1_status == "ROT":
                st.markdown("🔴 ROT")
            elif c1_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif c1_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    with col2:
        st.markdown("**C2**")
        c2_status = order_manager.inventory["C2"]
        if c2_status:
            if c2_status == "ROT":
                st.markdown("🔴 ROT")
            elif c2_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif c2_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    with col3:
        st.markdown("**C3**")
        c3_status = order_manager.inventory["C3"]
        if c3_status:
            if c3_status == "ROT":
                st.markdown("🔴 ROT")
            elif c3_status == "BLAU":
                st.markdown("🔵 BLAU")
            elif c3_status == "WEISS":
                st.markdown("⚪ WEISS")
        else:
            st.markdown("⬜ Leer")

    # Zusammenfassung
    st.markdown("---")
    st.markdown("### 📊 Lagerbestand Zusammenfassung")

    available_workpieces = order_manager.get_available_workpieces()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 ROT verfügbar", available_workpieces.get("ROT", 0))
    with col2:
        st.metric("🔵 BLAU verfügbar", available_workpieces.get("BLAU", 0))
    with col3:
        st.metric("⚪ WEISS verfügbar", available_workpieces.get("WEISS", 0))

    # Bestellungen
    st.markdown("### 🛒 Bestellungen")

    if order_manager.orders:
        for order in order_manager.orders:
            with st.expander(f"📋 {order['id']} - {order['workpiece_type']} x{order['quantity']}"):
                st.markdown(f"**Status:** {order['status']}")
                st.markdown(f"**Zeitstempel:** {order['timestamp'].strftime('%H:%M:%S')}")
                st.markdown(f"**Positionen:** {', '.join(order['positions'])}")
    else:
        st.info("📋 Keine aktiven Bestellungen")

    # Debug-Info
    if st.checkbox("🔍 Lagerbestand Debug-Info", key="show_inventory_debug"):
        st.markdown("**🔍 Debug-Informationen:**")
        st.markdown("**Aktueller Lagerbestand:**")
        st.json(order_manager.inventory)
        st.markdown("**Verfügbare Werkstücke:**")
        st.json(available_workpieces)


# Import module manager for static module info
try:
    from omf.tools.module_manager import get_omf_module_manager
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


def extract_availability_status(messages_df, module_id):
    """Extract availability status from recent messages for a module"""
    if messages_df.empty:
        return None

    # Look for recent messages with activity status
    for _, row in messages_df.iterrows():
        try:
            payload = row["payload"]
            if isinstance(payload, str):
                payload = json.loads(payload)

            # Check for activity status in payload
            if isinstance(payload, dict):
                # Look for common status fields
                for field in ["activityStatus", "status", "state", "activity"]:
                    if field in payload:
                        status_value = payload[field]
                        if isinstance(status_value, str):
                            return status_value.upper()
                        elif isinstance(status_value, dict) and "state" in status_value:
                            return status_value["state"].upper()

                # Check for actionState
                if "actionState" in payload and isinstance(payload["actionState"], dict):
                    if "state" in payload["actionState"]:
                        return payload["actionState"]["state"].upper()

                # Check for connection state
                if "connectionState" in payload:
                    return payload["connectionState"].upper()

        except (json.JSONDecodeError, KeyError, AttributeError):
            continue

    return None


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


def get_dynamic_module_status(module_id, module_info):
    """Get dynamic status information from message center data"""
    # Get recent messages for this module from message monitor (same as message center)
    recent_messages = []

    # Try to get messages from message monitor (same source as message center)
    if "message_monitor" in st.session_state:
        message_monitor = st.session_state.message_monitor
        # Use received_messages from message monitor (same as message center)
        recent_messages = [
            msg for msg in message_monitor.received_messages if module_info["id"] in msg.get("topic", "")
        ]

    # Fallback: try old mqtt_messages key (for backward compatibility)
    elif "mqtt_messages" in st.session_state:
        recent_messages = [msg for msg in st.session_state.mqtt_messages if module_info["id"] in msg.get("topic", "")]

    # Extract availability status from recent messages
    availability_status = extract_availability_status(
        pd.DataFrame(recent_messages) if recent_messages else pd.DataFrame(), module_info["id"]
    )

    # Check MQTT connection status
    mqtt_connected = st.session_state.get("mqtt_connected", False)

    # Connection status
    if mqtt_connected:
        connection_status = f"{get_status_icon('available')} Connected"
    else:
        connection_status = f"{get_status_icon('offline')} Disconnected"

    # Activity status with enhanced icons
    if availability_status:
        activity_display = get_enhanced_status_display(availability_status, module_info["type"])
    elif recent_messages:
        # If we have recent messages but no specific status, show "Active"
        activity_display = f"{get_status_icon('available')} Active"
    else:
        # No recent messages at all
        activity_display = f"{get_status_icon('offline')} No Data"

    return {
        "connection_status": connection_status,
        "activity_status": activity_display,
        "recent_messages": len(recent_messages),
    }


def show_module_status():
    """Show module status overview"""
    st.subheader("🏭 Modul-Status")
    st.markdown("Übersicht aller APS-Module mit Status und Verbindungsinformationen")

    # Get static module information
    all_modules = get_static_module_info()

    if not all_modules:
        st.error("❌ Keine Module konfiguriert")
        return

    # Create module table data
    module_table_data = []

    for module_id, module_info in all_modules.items():
        # Skip disabled modules
        if not module_info.get("enabled", True):
            continue

        # Get dynamic status information
        dynamic_status = get_dynamic_module_status(module_id, module_info)

        # Get module icon
        icon_display = module_info.get("icon", get_module_icon(module_id))

        # Get display name
        display_name = module_info.get("name_lang_de", module_info.get("name", module_id))

        module_table_data.append(
            {
                "Name": f"{icon_display} {display_name}",
                "ID": module_info["id"],
                "Type": module_info.get("type", "Unknown"),
                "IP": module_info.get("ip_range", "Unknown"),
                "Connected": dynamic_status["connection_status"],
                "Activity Status": dynamic_status["activity_status"],
                "Recent Messages": dynamic_status["recent_messages"],
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
                    if "Active" in m["Activity Status"] or "Available" in m["Activity Status"]
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
                "Activity Status": st.column_config.TextColumn("Activity Status", width="medium"),
                "Recent Messages": st.column_config.NumberColumn("Recent Messages", width="small"),
            },
        )

        # Connection status summary
        st.markdown("---")
        st.markdown("**📊 Verbindungsstatus Zusammenfassung:**")

        mqtt_connected = st.session_state.get("mqtt_connected", False)
        if mqtt_connected:
            st.success("🟢 MQTT-Broker verbunden - Alle Module können überwacht werden")
        else:
            st.warning("🟡 MQTT-Broker nicht verbunden - Modul-Status basiert auf gespeicherten Daten")

        # Data source info
        st.info(
            "💡 **Datenquelle:** Statische Module-Info aus Settings/Modul-Config, "
            "dynamische Status aus Nachrichtenzentrale"
        )

        # Debug info for testing
        if st.checkbox("🔍 Debug-Info anzeigen", key="show_debug_info"):
            st.markdown("**📊 Debug-Informationen:**")

            # Show MQTT connection status
            mqtt_connected = st.session_state.get("mqtt_connected", False)
            st.markdown(f"**MQTT Connected:** {mqtt_connected}")

            # Show message count from message monitor (same as message center)
            if "message_monitor" in st.session_state:
                message_monitor = st.session_state.message_monitor
                total_messages = len(message_monitor.received_messages)
                st.markdown(f"**Nachrichten in Message Monitor:** {total_messages}")

                # Show sample messages for each module
                if total_messages > 0:
                    st.markdown("**📋 Beispiele für Module-Nachrichten:**")
                    for module_id, module_info in all_modules.items():
                        if module_info.get("enabled", True):
                            recent_messages = [
                                msg
                                for msg in message_monitor.received_messages
                                if module_info["id"] in msg.get("topic", "")
                            ]
                            if recent_messages:
                                st.markdown(f"**{module_id}:** {len(recent_messages)} Nachrichten")
                                # Show first message as example
                                if recent_messages:
                                    with st.expander(f"Erste Nachricht für {module_id}"):
                                        st.json(recent_messages[0])
            else:
                st.warning("⚠️ Message Monitor nicht verfügbar")

            # Show session state keys
            st.markdown("**🔑 Session State Keys:**")
            session_keys = list(st.session_state.keys())
            st.markdown(f"Verfügbare Keys: {', '.join(session_keys)}")

    else:
        st.info("📋 Keine aktiven Module konfiguriert")


def show_overview_tabs():
    """Show all overview tabs"""
    st.header("📊 Overview")
    st.markdown("Übersicht der ORBIS Modellfabrik mit Modul-Status, Bestellungen und Lagerbestand")

    # Sub-tabs for Overview
    overview_tab1, overview_tab2, overview_tab3, overview_tab4 = st.tabs(
        ["🏭 Modul-Status", "📦 Bestellung", "🔧 Bestellung-Rohware", "📚 Lagerbestand"]
    )

    with overview_tab1:
        show_module_status()

    with overview_tab2:
        st.subheader("📦 Bestellung")
        st.info("💡 Bestellungs-Funktionalität wird hier implementiert")
        st.markdown(
            """
        **Geplante Features:**
        - Bestellungs-Trigger (ROT, WEISS, BLAU)
        - HBW-Status-Integration
        - Bestellungsverwaltung
        """
        )

    with overview_tab3:
        st.subheader("🔧 Bestellung-Rohware")
        st.info("💡 Rohware-Bestellungs-Funktionalität wird hier implementiert")
        st.markdown(
            """
        **Geplante Features:**
        - Wareneingang-Steuerung
        - Rohware-Bestellungen
        - Materialverwaltung
        """
        )

    with overview_tab4:
        st.subheader("📚 Lagerbestand")
        st.info("💡 Lagerbestands-Funktionalität wird hier implementiert")
        st.markdown(
            """
        **Geplante Features:**
        - Lagerbestands-Übersicht
        - Werkstück-Positionen
        - Lagerbestands-Historie
        """
        )
