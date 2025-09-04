"""
OMF Dashboard Overview - Kundenaufträge (Customer Orders)
Kopiert aus overview_inventory.py - Sektion 2: Bestellungen
"""

import os
import sys
from datetime import datetime, timezone

import streamlit as st

# Template-Import hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "assets"))
try:
    from html_templates import get_workpiece_box_template

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
        self.workpiece_types = ["RED", "BLUE", "WHITE"]
        self.orders = []
        self.last_update_timestamp = None

    def update_inventory_from_mqtt_client(self, mqtt_client):
        """Aktualisiert den Lagerbestand basierend auf MQTT-Nachrichten"""
        if not mqtt_client:
            return

        try:
            # Alle Nachrichten aus dem MQTT-Client holen
            all_messages = mqtt_client.drain()

            # HBW-Nachrichten filtern
            hbw_messages = [
                msg for msg in all_messages if msg.get("topic", "").startswith("module/v1/ff/SVR3QA0022/state")
            ]

            if hbw_messages:
                # Neueste HBW-Nachricht verwenden
                latest_hbw_msg = max(hbw_messages, key=lambda x: x.get("ts", 0))
                self._process_hbw_state_message(latest_hbw_msg)

        except Exception as e:
            st.error(f"❌ Fehler beim Aktualisieren des Lagerbestands: {e}")

    def _process_hbw_state_message(self, message):
        """Verarbeitet eine HBW State-Nachricht und aktualisiert den Lagerbestand"""
        try:
            payload = message.get("payload", {})
            loads = payload.get("loads", [])

            # Lagerbestand zurücksetzen
            for position in self.inventory:
                self.inventory[position] = None

            # Neue Ladungen verarbeiten
            for load in loads:
                load_type = load.get("loadType")
                load_position = load.get("loadPosition")

                if load_type in self.workpiece_types and load_position in self.inventory:
                    self.inventory[load_position] = load_type

            # Timestamp aktualisieren
            self.last_update_timestamp = message.get("ts")

        except Exception as e:
            st.error(f"❌ Fehler beim Verarbeiten der HBW-Nachricht: {e}")

    def get_available_workpieces(self):
        """Gibt die verfügbaren Werkstücke zurück"""
        available = {}
        for workpiece_type in self.workpiece_types:
            count = sum(1 for pos_type in self.inventory.values() if pos_type == workpiece_type)
            if count > 0:
                available[workpiece_type] = count
        return available

    def get_formatted_timestamp(self):
        """Gibt den formatierten Zeitstempel zurück"""
        if not self.last_update_timestamp:
            return "Nie aktualisiert"

        try:
            from datetime import datetime

            dt = datetime.fromtimestamp(self.last_update_timestamp)
            return dt.strftime("%d.%m.%Y %H:%M:%S")
        except (ValueError, OSError):
            return f"Timestamp: {self.last_update_timestamp}"


def show_overview_order():
    """Zeigt die Kundenaufträge (Customer Orders) - Kopiert aus overview_inventory.py"""
    st.subheader("📋 Kundenaufträge (Customer Orders)")

    # OrderManager initialisieren
    order_manager = OrderManager()

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

    # Bestellungen
    st.markdown("### 🛒 Bestellungen")

    available_workpieces = order_manager.get_available_workpieces()

    col1, col2, col3 = st.columns(3)

    # ROT Werkstück
    with col1:
        red_count = available_workpieces.get("RED", 0)
        red_available = red_count > 0

        if TEMPLATES_AVAILABLE:
            # Template verwenden
            st.markdown(get_workpiece_box_template("RED", red_count, red_available), unsafe_allow_html=True)
        else:
            # Fallback: Einfache Darstellung
            st.markdown("**RED Werkstück**")
            st.markdown(f"**Bestand: {red_count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if red_available else '❌ Nein'}**")

        if red_available:
            if st.button(
                "📋 Bestellen", key="order_inventory_order_red", type="secondary", help="Bestellung für ROT Werkstück"
            ):
                _send_order_directly("RED")
        else:
            st.button("📋 Bestellen", key="order_inventory_order_red_disabled", disabled=True)

    # BLUE Werkstück
    with col2:
        blue_count = available_workpieces.get("BLUE", 0)
        blue_available = blue_count > 0

        if TEMPLATES_AVAILABLE:
            # Template verwenden
            st.markdown(get_workpiece_box_template("BLUE", blue_count, blue_available), unsafe_allow_html=True)
        else:
            # Fallback: Einfache Darstellung
            st.markdown("**BLUE Werkstück**")
            st.markdown(f"**Bestand: {blue_count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if blue_available else '❌ Nein'}**")

        if blue_available:
            if st.button(
                "📋 Bestellen", key="order_inventory_order_blue", type="secondary", help="Bestellung für BLUE Werkstück"
            ):
                _send_order_directly("BLUE")
        else:
            st.button("📋 Bestellen", key="order_inventory_order_blue_disabled", disabled=True)

    # WHITE Werkstück
    with col3:
        white_count = available_workpieces.get("WHITE", 0)
        white_available = white_count > 0

        if TEMPLATES_AVAILABLE:
            # Template verwenden
            st.markdown(get_workpiece_box_template("WHITE", white_count, white_available), unsafe_allow_html=True)
        else:
            # Fallback: Einfache Darstellung
            st.markdown("**WHITE Werkstück**")
            st.markdown(f"**Bestand: {white_count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if white_available else '❌ Nein'}**")

        if white_available:
            if st.button(
                "📋 Bestellen",
                key="order_inventory_order_white",
                type="secondary",
                help="Bestellung für WHITE Werkstück",
            ):
                _send_order_directly("WHITE")
        else:
            st.button("📋 Bestellen", key="order_inventory_order_white_disabled", disabled=True)


def _send_order_directly(color: str):
    """Sendet Bestellung direkt ohne Bestätigung - basierend auf steering_factory.py"""
    try:
        mqtt_client = st.session_state.get("mqtt_client")
        if not mqtt_client or not mqtt_client.connected:
            st.error("❌ MQTT-Client nicht verbunden")
            return

        # Bestellungs-Topic und Payload (exakt wie in steering_factory.py)
        topic = "ccu/order/request"
        payload = {
            "type": color,  # RED, WHITE, BLUE
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "orderType": "PRODUCTION",
        }

        # Direkter Versand ohne Bestätigung
        result = mqtt_client.publish(topic, payload, qos=1, retain=False)

        if result:
            st.success(f"✅ Bestellung für {color} erfolgreich gesendet!")
            st.rerun()  # Seite aktualisieren
        else:
            st.error("❌ Fehler beim Senden der Bestellung")

    except Exception as e:
        st.error(f"❌ Fehler beim Senden der Bestellung: {e}")
