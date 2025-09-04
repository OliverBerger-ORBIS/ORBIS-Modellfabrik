"""
OMF Dashboard Overview - Lagerbestand
Exakte Kopie der show_inventory_grid() Funktion aus overview.py
"""

import json

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


def show_overview_inventory():
    """3x3 Lagerbestand-Raster anzeigen - Exakte Kopie von show_inventory_grid() aus overview.py"""
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
