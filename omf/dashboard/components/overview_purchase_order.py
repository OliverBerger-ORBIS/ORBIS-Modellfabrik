"""
OMF Dashboard Overview - Rohmaterial-Bestellungen (Purchase Orders)
Kopiert aus overview_inventory.py - Sektion 3: Bestellungen von Rohmaterial
"""

import streamlit as st

# Template-Import hinzufügen
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "assets"))  # Nicht mehr nötig nach pip install -e .
try:
    from omf.dashboard.assets.html_templates import get_bucket_template, get_workpiece_box_template

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
            from datetime import datetime

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


def process_purchase_order_messages_from_buffers(hbw_messages, order_manager):
    """Verarbeitet HBW-Nachrichten aus Per-Topic-Buffer für Rohmaterial-Bestellungen"""
    if not hbw_messages:
        return

    # Neueste HBW-Nachricht finden
    if hbw_messages:
        latest_hbw_msg = max(hbw_messages, key=lambda x: x.get("ts", 0))
        if order_manager:
            order_manager._process_hbw_state_message(latest_hbw_msg)


def show_overview_order_raw():
    """Zeigt die Rohmaterial-Bestellungen (Purchase Orders) - Kopiert aus overview_inventory.py"""
    st.subheader("📊 Rohmaterial-Bestellungen (Purchase Orders)")
    st.info("🔄 Im Lager ist Platz für drei rohe Werkstücke jeder Farbe")

    # OrderManager aus Session-State holen oder erstellen
    if "order_manager" not in st.session_state:
        st.session_state["order_manager"] = OrderManager()
    order_manager = st.session_state["order_manager"]

    # NEUES PATTERN: Per-Topic-Buffer für Rohmaterial-Bestellungen
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
                process_purchase_order_messages_from_buffers(hbw_messages, order_manager)

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

    # Verfügbare Werkstücke berechnen
    available_workpieces = order_manager.get_available_workpieces()
    red_count = available_workpieces.get("RED", 0)
    blue_count = available_workpieces.get("BLUE", 0)
    white_count = available_workpieces.get("WHITE", 0)

    # Konstanten für maximale Kapazität
    MAX_CAPACITY = 3

    # Berechne Bedarf für jede Farbe
    red_need = MAX_CAPACITY - red_count
    blue_need = MAX_CAPACITY - blue_count
    white_need = MAX_CAPACITY - white_count

    # Zeilenweise Darstellung des Bedarfs
    st.markdown("#### 🔴 Rote Werkstücke")
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
        if TEMPLATES_AVAILABLE:
            # Template verwenden - as is
            st.markdown(get_workpiece_box_template("RED", red_count, red_count > 0), unsafe_allow_html=True)
        else:
            st.markdown("**RED**")
    with col2:
        st.markdown(f"**Bedarf: {red_need} von {MAX_CAPACITY}**")
        if red_need > 0:
            st.markdown(f"**Noch bestellbar: {red_need} Werkstücke**")
        else:
            st.success("✅ Vollständig - Kein Bedarf")
    with col3:
        if red_need > 0:
            # Leere Buckets für fehlende Werkstücke - Template verwenden (große Version)
            if TEMPLATES_AVAILABLE:
                empty_buckets = ""
                for _i in range(red_need):
                    # Template für leeren Bucket verwenden - as is (große Version)
                    empty_bucket = get_bucket_template(f"R{_i+1}", None)
                    empty_buckets += empty_bucket
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Fallback: Einfache Darstellung
                empty_buckets = ""
                for _i in range(red_need):
                    empty_buckets += '<div style="width: 140px; height: 140px; border: 2px solid #ccc; border-top: none; background-color: #f9f9f9; border-radius: 0 0 8px 8px; display: inline-block; margin: 8px;"></div>'  # noqa: E501
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
    with col4:
        if red_need > 0:
            if st.button("📦 Rohstoff bestellen", key="order_raw_red", type="secondary"):
                st.info("🔄 Bestellung ROT Rohstoff - Funktion wird implementiert")
        else:
            st.button("📦 Rohstoff bestellen", key="order_raw_red_disabled", disabled=True)

    st.markdown("#### 🔵 Blaue Werkstücke")
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
        if TEMPLATES_AVAILABLE:
            # Template verwenden - as is
            st.markdown(get_workpiece_box_template("BLUE", blue_count, blue_count > 0), unsafe_allow_html=True)
        else:
            st.markdown("**BLUE**")
    with col2:
        st.markdown(f"**Bedarf: {blue_need} von {MAX_CAPACITY}**")
        if blue_need > 0:
            st.markdown(f"**Noch bestellbar: {blue_need} Werkstücke**")
        else:
            st.success("✅ Vollständig - Kein Bedarf")
    with col3:
        if blue_need > 0:
            # Leere Buckets für fehlende Werkstücke - Template verwenden (große Version)
            if TEMPLATES_AVAILABLE:
                empty_buckets = ""
                for _i in range(blue_need):
                    # Template für leeren Bucket verwenden - as is (große Version)
                    empty_bucket = get_bucket_template(f"B{_i+1}", None)
                    empty_buckets += empty_bucket
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Fallback: Einfache Darstellung
                empty_buckets = ""
                for _i in range(blue_need):
                    empty_buckets += '<div style="width: 140px; height: 140px; border: 2px solid #ccc; border-top: none; background-color: #f9f9f9; border-radius: 0 0 8px 8px; display: inline-block; margin: 8px;"></div>'  # noqa: E501
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
    with col4:
        if blue_need > 0:
            if st.button("📦 Rohstoff bestellen", key="order_raw_blue", type="secondary"):
                st.info("🔄 Bestellung BLUE Rohstoff - Funktion wird implementiert")
        else:
            st.button("📦 Rohstoff bestellen", key="order_raw_blue_disabled", disabled=True)

    st.markdown("#### ⚪ Weiße Werkstücke")
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
        if TEMPLATES_AVAILABLE:
            # Template verwenden - as is
            st.markdown(get_workpiece_box_template("WHITE", white_count, white_count > 0), unsafe_allow_html=True)
        else:
            st.markdown("**WHITE**")
    with col2:
        st.markdown(f"**Bedarf: {white_need} von {MAX_CAPACITY}**")
        if white_need > 0:
            st.markdown(f"**Noch bestellbar: {white_need} Werkstücke**")
        else:
            st.success("✅ Vollständig - Kein Bedarf")
    with col3:
        if white_need > 0:
            # Leere Buckets für fehlende Werkstücke - Template verwenden (große Version)
            if TEMPLATES_AVAILABLE:
                empty_buckets = ""
                for _i in range(white_need):
                    # Template für leeren Bucket verwenden - as is (große Version)
                    empty_bucket = get_bucket_template(f"W{_i+1}", None)
                    empty_buckets += empty_bucket
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Fallback: Einfache Darstellung
                empty_buckets = ""
                for _i in range(white_need):
                    empty_buckets += '<div style="width: 140px; height: 140px; border: 2px solid #ccc; border-top: none; background-color: #f9f9f9; border-radius: 0 0 8px 8px; display: inline-block; margin: 8px;"></div>'
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
    with col4:
        if white_need > 0:
            if st.button("📦 Rohstoff bestellen", key="order_raw_white", type="secondary"):
                st.info("🔄 Bestellung WHITE Rohstoff - Funktion wird implementiert")
        else:
            st.button("📦 Rohstoff bestellen", key="order_raw_white_disabled", disabled=True)

    st.markdown("---")
