"""
APS Dashboard Overview - Kundenaufträge (Customer Orders)
Kopie von overview_customer_order.py mit eindeutigen APS-Keys
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

            # Neue Lagerbestand-Daten verarbeiten
            for load in loads:
                position = load.get("position")
                workpiece = load.get("workpiece")
                if position in self.inventory:
                    self.inventory[position] = workpiece

            # Zeitstempel aktualisieren
            from datetime import datetime, timezone
            self.last_update_timestamp = datetime.now(timezone.utc)

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


def process_customer_order_messages_from_buffers(messages, order_manager):
    """Verarbeitet Nachrichten aus dem Per-Topic-Buffer für Kundenaufträge"""
    for message in messages:
        order_manager._process_hbw_state_message(message)


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


def show_aps_overview_order():
    """Zeigt die APS Kundenaufträge (Customer Orders) - Kopie mit eindeutigen Keys"""
    st.subheader("📋 Kundenaufträge (Customer Orders)")

    # Verwende den gleichen OrderManager wie die Original-Komponente
    from omf.dashboard.components.overview_customer_order import OrderManager
    
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
                from omf.dashboard.components.overview_customer_order import process_customer_order_messages_from_buffers
                process_customer_order_messages_from_buffers(hbw_messages, order_manager)

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

    # Zeige verfügbare Werkstücke
    available_workpieces = order_manager.get_available_workpieces()

    # 3-Spalten-Layout für Werkstücke
    col1, col2, col3 = st.columns(3)

    # RED Werkstück
    with col1:
        red_count = available_workpieces.get("RED", 0)
        red_available = red_count > 0

        if TEMPLATES_AVAILABLE:
            # Template verwenden für schöne Darstellung
            st.markdown(get_workpiece_box_template("RED", red_count, red_available), unsafe_allow_html=True)
        else:
            # Fallback: Einfache Darstellung
            st.markdown("**RED Werkstück**")
            st.markdown(f"**Bestand: {red_count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if red_available else '❌ Nein'}**")

        if red_available:
            if st.button(
                "📋 Bestellen", key="aps_overview_customer_order_red", type="secondary", help="Bestellung für ROT Werkstück"
            ):
                _send_order_directly("RED")
        else:
            st.button("📋 Bestellen", key="aps_overview_customer_order_red_disabled", disabled=True)

    # BLUE Werkstück
    with col2:
        blue_count = available_workpieces.get("BLUE", 0)
        blue_available = blue_count > 0

        if TEMPLATES_AVAILABLE:
            # Template verwenden für schöne Darstellung
            st.markdown(get_workpiece_box_template("BLUE", blue_count, blue_available), unsafe_allow_html=True)
        else:
            # Fallback: Einfache Darstellung
            st.markdown("**BLUE Werkstück**")
            st.markdown(f"**Bestand: {blue_count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if blue_available else '❌ Nein'}**")

        if blue_available:
            if st.button(
                "📋 Bestellen", key="aps_overview_customer_order_blue", type="secondary", help="Bestellung für BLUE Werkstück"
            ):
                _send_order_directly("BLUE")
        else:
            st.button("📋 Bestellen", key="aps_overview_customer_order_blue_disabled", disabled=True)

    # WHITE Werkstück
    with col3:
        white_count = available_workpieces.get("WHITE", 0)
        white_available = white_count > 0

        if TEMPLATES_AVAILABLE:
            # Template verwenden für schöne Darstellung
            st.markdown(get_workpiece_box_template("WHITE", white_count, white_available), unsafe_allow_html=True)
        else:
            # Fallback: Einfache Darstellung
            st.markdown("**WHITE Werkstück**")
            st.markdown(f"**Bestand: {white_count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if white_available else '❌ Nein'}**")

        if white_available:
            if st.button(
                "📋 Bestellen", key="aps_overview_customer_order_white", type="secondary", help="Bestellung für WHITE Werkstück"
            ):
                _send_order_directly("WHITE")
        else:
            st.button("📋 Bestellen", key="aps_overview_customer_order_white_disabled", disabled=True)
