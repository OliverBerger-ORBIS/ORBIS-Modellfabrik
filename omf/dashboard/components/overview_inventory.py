"""
OMF Dashboard Overview - Lagerbestand
Verwendet OrderManager für zentrale Verwaltung aller Dashboard-relevanten Informationen
"""

import json
from datetime import datetime

import streamlit as st

# Template-Import hinzufügen
try:
    from omf.dashboard.assets.html_templates import get_bucket_template

    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    st.error(f"❌ Templates nicht verfügbar: {e}")

# Alte message_processor Imports entfernt - verwenden jetzt Per-Topic-Buffer


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
        """Lagerbestand aus MQTT-Client-Nachrichten aktualisieren - DEPRECATED"""
        # Diese Methode wird durch das neue Message-Processor Pattern ersetzt
        pass

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


def process_inventory_messages_from_buffers(hbw_messages, order_manager):
    """Verarbeitet HBW-Nachrichten aus Per-Topic-Buffer für den Lagerbestand"""
    if not hbw_messages:
        return

    # Neueste HBW-Nachricht finden
    if hbw_messages:
        latest_hbw_msg = max(hbw_messages, key=lambda x: x.get("ts", 0))
        if order_manager:
            order_manager._process_hbw_state_message(latest_hbw_msg)


def _create_large_bucket_display(position, workpiece_type):
    """Erstellt eine große Bucket-Darstellung für eine Lagerposition - Verwendet Template"""
    if TEMPLATES_AVAILABLE:
        # Template verwenden
        return get_bucket_template(position, workpiece_type)
    else:
        # Fallback: Einfache Darstellung
        return f"""
    <div style="width: 140px; height: 140px; margin: 8px auto; position: relative; border: 2px solid #ccc; border-radius: 8px; background-color: #f9f9f9; display: flex; align-items: center; justify-content: center;">  # noqa: E501
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

    # Auto-Refresh aus Settings (global) - DEAKTIVIERT für Performance
    auto_refresh = st.session_state.get("auto_refresh_enabled", False)

    # Auto-Refresh Timer (nur wenn aktiviert) - PERFORMANCE-PROBLEM BEHOBEN
    if auto_refresh:
        # PERFORMANCE-FIX: Auto-Refresh deaktiviert, da es das UI blockiert
        st.warning("⚠️ Auto-Refresh ist deaktiviert (Performance-Grund)")
        # import time
        # time.sleep(refresh_interval)  # BLOCKIERT DAS UI!
        # request_refresh()  # ENDLOS-SCHLEIFE!

    # NEUES PATTERN: Per-Topic-Buffer für Lagerbestand
    mqtt_client = st.session_state.get("mqtt_client")
    if mqtt_client:
        # Abonniere die benötigten Topics für Per-Topic-Buffer
        mqtt_client.subscribe_many(["module/v1/ff/SVR3QA0022/state"])  # HBW State für Lagerbestand

        # NEUES PATTERN: Per-Topic-Buffer für HBW-Status
        try:
            # Hole die letzten Nachrichten aus dem Per-Topic-Buffer
            hbw_messages = list(mqtt_client.get_buffer("module/v1/ff/SVR3QA0022/state"))

            if hbw_messages:
                st.info(f"📊 **{len(hbw_messages)} HBW-Nachrichten in Buffer**")

                # Verarbeite die Nachrichten aus dem Buffer
                process_inventory_messages_from_buffers(hbw_messages, order_manager)

                # Status-Anzeige
                if order_manager.last_update_timestamp:
                    formatted_time = order_manager.get_formatted_timestamp()
                    st.success(f"✅ Lagerbestand aktualisiert: {formatted_time}")
                else:
                    st.info("ℹ️ Keine HBW-Nachrichten verarbeitet")
            else:
                st.info("ℹ️ Keine HBW-Nachrichten empfangen")

        except Exception as e:
            st.warning(f"⚠️ Fehler beim Zugriff auf Per-Topic-Buffer: {e}")
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
