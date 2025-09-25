"""
APS Dashboard Overview - Lagerbestand
Kopie von overview_inventory.py mit eindeutigen APS-Keys
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


class APSOrderManager:
    """Zentraler Manager für alle APS Dashboard-relevanten Informationen (Bestellungen, Lagerbestand, etc.)"""

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
            loads = payload.get("loads", [])

            # Lagerbestand zurücksetzen
            for position in self.inventory:
                self.inventory[position] = None

            # Neue Lagerbestand-Daten verarbeiten
            for load in loads:
                position = load.get("position")
                workpiece = load.get("workpiece")
                if position in self.inventory:
                    self.inventory[position] = workpiece

            # Zeitstempel aktualisieren
            from datetime import datetime
            self.last_update_timestamp = datetime.now()

        except Exception as e:
            st.error(f"❌ Fehler beim Verarbeiten der HBW State-Nachricht: {e}")

    def get_available_workpieces(self):
        """Gibt die verfügbaren Werkstücke zurück"""
        available = {"RED": 0, "BLUE": 0, "WHITE": 0}
        
        for position, workpiece in self.inventory.items():
            if workpiece in available:
                available[workpiece] += 1
        
        return available

    def get_formatted_timestamp(self):
        """Gibt den formatierten Zeitstempel zurück"""
        if self.last_update_timestamp:
            return self.last_update_timestamp.strftime("%d.%m.%Y %H:%M:%S")
        return "Nie"


def process_inventory_messages_from_buffers(messages, order_manager):
    """Verarbeitet Nachrichten aus dem Per-Topic-Buffer für Lagerbestand"""
    for message in messages:
        order_manager._process_hbw_state_message(message)


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


def show_aps_overview_inventory():
    """Zeigt den APS Lagerbestand - Kopie mit eindeutigen Keys"""
    st.subheader("🏬 Lagerbestand - HBW Übersicht")
    st.write("Aktuelle Belegung des Hochregallagers (3x3 Raster)")

    # Verwende den gleichen OrderManager wie die Original-Komponente
    from omf.dashboard.components.operator.overview_inventory import OrderManager
    
    if "order_manager" not in st.session_state:
        st.session_state["order_manager"] = OrderManager()
    order_manager = st.session_state["order_manager"]

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
                from omf.dashboard.components.operator.overview_inventory import process_inventory_messages_from_buffers
                process_inventory_messages_from_buffers(hbw_messages, order_manager)

                # Status-Anzeige
                if order_manager.last_update_timestamp:
                    formatted_time = order_manager.get_formatted_timestamp()
                    st.success(f"✅ Lagerbestand aktualisiert: {formatted_time}")
            else:
                st.warning("⚠️ Keine HBW-Nachrichten im Buffer")

        except Exception as e:
            st.error(f"❌ Fehler beim Verarbeiten der HBW-Nachrichten: {e}")
    else:
        st.warning("⚠️ MQTT-Client nicht verfügbar")

    # 3x3 Raster erstellen - ECHTE Grid-Darstellung
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

    # Debug-Info mit eindeutigem Key
    if st.checkbox("🔍 Lagerbestand Debug-Info", key="aps_overview_inventory_debug"):
        st.markdown("**🔍 Debug-Informationen:**")
        st.markdown("**Aktueller Lagerbestand:**")
        st.json(order_manager.inventory)
        st.markdown("**Verfügbare Werkstücke:**")
        st.json(order_manager.get_available_workpieces())
        st.markdown("**Letzte Aktualisierung:**")
        st.write(order_manager.get_formatted_timestamp())
