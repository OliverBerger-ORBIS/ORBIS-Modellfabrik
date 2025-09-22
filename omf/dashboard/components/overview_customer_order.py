"""
OMF Dashboard Overview - Kundenaufträge (Customer Orders)
Kopiert aus overview_inventory.py - Sektion 2: Bestellungen
"""

from datetime import datetime, timezone

import streamlit as st

from omf.dashboard.utils.ui_refresh import request_refresh

# Template-Import hinzufügen
try:
    from omf.dashboard.assets.html_templates import get_workpiece_box_template

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
        self.workpiece_types = ["RED", "BLUE", "WHITE"]
        self.orders = []
        self.last_update_timestamp = None

    def update_inventory_from_mqtt_client(self, mqtt_client):
        """Aktualisiert den Lagerbestand basierend auf MQTT-Nachrichten - DEPRECATED"""
        # Diese Methode wird durch das neue Message-Processor Pattern ersetzt
        pass

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


def process_customer_order_messages_from_buffers(hbw_messages, order_manager):
    """Verarbeitet HBW-Nachrichten aus Per-Topic-Buffer für Kundenaufträge"""
    if not hbw_messages:
        return

    # Neueste HBW-Nachricht finden
    if hbw_messages:
        latest_hbw_msg = max(hbw_messages, key=lambda x: x.get("ts", 0))
        if order_manager:
            order_manager._process_hbw_state_message(latest_hbw_msg)


def show_overview_order():
    """Zeigt die Kundenaufträge (Customer Orders) - Kopiert aus overview_inventory.py"""
    st.subheader("📋 Kundenaufträge (Customer Orders)")

    # OrderManager aus Session-State holen oder erstellen
    if "order_manager" not in st.session_state:
        st.session_state["order_manager"] = OrderManager()
    order_manager = st.session_state["order_manager"]

    # NEUES PATTERN: Per-Topic-Buffer für Kundenaufträge
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
                process_customer_order_messages_from_buffers(hbw_messages, order_manager)

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
            request_refresh()  # Seite aktualisieren
        else:
            st.error("❌ Fehler beim Senden der Bestellung")

    except Exception as e:
        st.error(f"❌ Fehler beim Senden der Bestellung: {e}")
