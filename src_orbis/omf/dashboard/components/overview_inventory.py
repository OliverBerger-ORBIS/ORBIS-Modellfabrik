"""
OMF Dashboard Overview - Lagerbestand
Verwendet OrderManager für zentrale Verwaltung aller Dashboard-relevanten Informationen
"""

import json
import os
import sys
from datetime import datetime

import streamlit as st

# Template-Import hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "assets"))
try:
    from html_templates import get_bucket_template

    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    st.error(f"❌ Templates nicht verfügbar: {e}")


class OrderManager:
    """Zentraler Manager für alle Dashboard-relevanten Informationen (Bestellungen, Lagerbestand, etc.)"""

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
        self.workpiece_types = ["RED", "BLUE", "WHITE"]  # Korrekte Farben aus HBW-Nachrichten
        self.orders = []
        self.last_update_timestamp = None

    def update_inventory_from_mqtt_client(self, mqtt_client):
        """Lagerbestand aus MQTT-Client-Nachrichten aktualisieren"""
        if not mqtt_client:
            return

        try:
            # Alle Nachrichten aus MQTT-Client holen
            all_messages = mqtt_client.drain()

            # Nach HBW-relevanten Topics filtern
            hbw_messages = [
                msg for msg in all_messages if msg.get("topic", "").startswith("module/v1/ff/SVR3QA0022/state")
            ]

            # Neueste HBW-Nachricht verarbeiten
            if hbw_messages:
                latest_hbw_msg = max(hbw_messages, key=lambda x: x.get("ts", 0))
                self._process_hbw_state_message(latest_hbw_msg)

        except Exception as e:
            st.error(f"❌ Fehler beim Aktualisieren des Lagerbestands: {e}")

    def _process_hbw_state_message(self, message):
        """HBW-Modul-Status-Nachricht verarbeiten (primäre Quelle für Lagerbestand)"""
        try:
            payload = message.get("payload", {})
            if isinstance(payload, str):
                payload = json.loads(payload)

            if not isinstance(payload, dict):
                return

            # HBW-Modul-Status verarbeiten: {"loads": [{"loadType": "RED", "loadPosition": "A1", ...}]}
            loads = payload.get("loads", [])

            # Alle Positionen erst auf leer setzen
            for position in self.inventory:
                self.inventory[position] = None

            # Belegte Positionen aktualisieren
            for load in loads:
                load_type = load.get("loadType", "")
                load_position = load.get("loadPosition", "")

                if load_type and load_position in self.inventory:
                    # Farben von HBW-Format zu Display-Format konvertieren
                    if load_type == "RED":
                        self.inventory[load_position] = "RED"
                    elif load_type == "BLUE":
                        self.inventory[load_position] = "BLUE"
                    elif load_type == "WHITE":
                        self.inventory[load_position] = "WHITE"

            self.last_update_timestamp = message.get("ts", 0)

        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            st.warning(f"⚠️ Fehler beim Verarbeiten der HBW-Nachricht: {e}")

    def get_formatted_timestamp(self):
        """Timestamp in lesbares Format konvertieren"""
        if not self.last_update_timestamp:
            return "Nie aktualisiert"

        try:
            # Unix-Timestamp zu datetime konvertieren
            dt = datetime.fromtimestamp(self.last_update_timestamp)
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except (ValueError, OSError):
            return f"Timestamp: {self.last_update_timestamp}"

    def get_available_workpieces(self):
        """Verfügbare Werkstücke für Bestellungen zurückgeben"""
        available = {}
        for workpiece_type in self.workpiece_types:
            count = sum(1 for pos, wp in self.inventory.items() if wp == workpiece_type)
            if count > 0:
                available[workpiece_type] = count
        return available


def _create_large_bucket_display(position, workpiece_type):
    """Erstellt eine große Bucket-Darstellung für eine Lagerposition - Verwendet Template"""
    if TEMPLATES_AVAILABLE:
        # Template verwenden
        return get_bucket_template(position, workpiece_type)
    else:
        # Fallback: Einfache Darstellung
        return f"""
        <div style="width: 140px; height: 140px; margin: 8px auto; position: relative; border: 2px solid #ccc; border-radius: 8px; background-color: #f9f9f9; display: flex; align-items: center; justify-content: center;">
            <div style="text-align: center;">
                <div style="font-size: 12px; color: #666;">{position}</div>
                <div style="font-size: 10px; color: #999;">{workpiece_type or 'Leer'}</div>
            </div>
        </div>
        """


def show_overview_inventory():
    """3x3 Lagerbestand-Raster anzeigen - Verwendet MQTT-Client für Live-Updates"""
    st.subheader("📚 Lagerbestand - HBW Übersicht")
    st.markdown("Aktuelle Belegung des Hochregallagers (3x3 Raster)")

    # OrderManager initialisieren
    if "order_manager" not in st.session_state:
        st.session_state.order_manager = OrderManager()

    order_manager = st.session_state.order_manager

    # Auto-Refresh aus Settings (global)
    auto_refresh = st.session_state.get("auto_refresh_enabled", False)
    refresh_interval = st.session_state.get("auto_refresh_interval", 10)

    # Auto-Refresh Timer (nur wenn aktiviert)
    if auto_refresh:
        import time

        time.sleep(refresh_interval)
        st.rerun()

    # Lagerbestand aus MQTT-Client aktualisieren
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        order_manager.update_inventory_from_mqtt_client(mqtt_client)

        # Status-Anzeige
        if order_manager.last_update_timestamp:
            formatted_time = order_manager.get_formatted_timestamp()
            st.success(f"✅ Lagerbestand aktualisiert: {formatted_time}")
        else:
            st.info("ℹ️ Keine HBW-Nachrichten empfangen")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar - Lagerbestand wird nicht aktualisiert")

    # 3x3 Raster erstellen
    st.markdown("### 🏗️ Lagerpositionen (A1-C3)")

    # Grid-Layout mit 3 Spalten
    col1, col2, col3 = st.columns(3)

    # Zeile A - Große Bucket-Darstellung
    with col1:
        a1_status = order_manager.inventory["A1"]
        bucket_html = _create_large_bucket_display("A1", a1_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    with col2:
        a2_status = order_manager.inventory["A2"]
        bucket_html = _create_large_bucket_display("A2", a2_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    with col3:
        a3_status = order_manager.inventory["A3"]
        bucket_html = _create_large_bucket_display("A3", a3_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    # Zeile B - Große Bucket-Darstellung
    with col1:
        b1_status = order_manager.inventory["B1"]
        bucket_html = _create_large_bucket_display("B1", b1_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    with col2:
        b2_status = order_manager.inventory["B2"]
        bucket_html = _create_large_bucket_display("B2", b2_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    with col3:
        b3_status = order_manager.inventory["B3"]
        bucket_html = _create_large_bucket_display("B3", b3_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    # Zeile C - Große Bucket-Darstellung
    with col1:
        c1_status = order_manager.inventory["C1"]
        bucket_html = _create_large_bucket_display("C1", c1_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    with col2:
        c2_status = order_manager.inventory["C2"]
        bucket_html = _create_large_bucket_display("C2", c2_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    with col3:
        c3_status = order_manager.inventory["C3"]
        bucket_html = _create_large_bucket_display("C3", c3_status)
        st.markdown(bucket_html, unsafe_allow_html=True)

    # Debug-Info
    if st.checkbox("🔍 Lagerbestand Debug-Info", key="show_inventory_debug"):
        st.markdown("**🔍 Debug-Informationen:**")
        st.markdown("**Aktueller Lagerbestand:**")
        st.json(order_manager.inventory)
        available_workpieces = order_manager.get_available_workpieces()
        st.markdown("**Verfügbare Werkstücke:**")
        st.json(available_workpieces)
