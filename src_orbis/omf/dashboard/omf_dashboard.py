class MockMqttClient:
    def drain(self, *args, **kwargs):
        print("[MOCK] drain called")
        return getattr(self, "published_messages", [])

    def __init__(self, cfg=None, *args, **kwargs):
        self.connected = True
        self.cfg = cfg or {}
        self.config = {
            "broker": {
                "aps": {
                    "host": "mock",
                    "port": 0,
                    "client_id": "mock_client",
                    "username": "",
                    "password": "",
                    "keepalive": 60,
                }
            },
            "subscriptions": {},
        }

    def close(self, *args, **kwargs):
        print("[MOCK] Close called")
        self._closed = True
        return True

    def connect(self, *args, **kwargs):
        self.connected = True
        print("[MOCK] Connect called")
        return True

    def disconnect(self, *args, **kwargs):
        self.connected = False
        print("[MOCK] Disconnect called")
        return True

    def loop_start(self, *args, **kwargs):
        self._loop_running = True
        print("[MOCK] loop_start called")
        return True

    def loop_stop(self, *args, **kwargs):
        self._loop_running = False
        print("[MOCK] loop_stop called")
        return True

    def is_connected(self, *args, **kwargs):
        return self.connected

    def get_client_id(self, *args, **kwargs):
        return self._client_id

    def get_broker(self, *args, **kwargs):
        return self._broker

    def get_port(self, *args, **kwargs):
        return self._port

    def get_last_error(self, *args, **kwargs):
        return self._last_error

    def get_subscriptions(self, *args, **kwargs):
        return self._subscriptions.copy()

    def get_published_messages(self, *args, **kwargs):
        return self.published_messages.copy()

    def get_messages(self, *args, **kwargs):
        return self._messages.copy()

    def __str__(self):
        return f"<MockMqttClient id={self._client_id} broker={self._broker}:{self._port} connected={self.connected}>"

    def get_connection_status(self):
        return {"stats": {"messages_received": 0, "messages_sent": 0}}

    @property
    def client(self):
        return None


"""
ORBIS Modellfabrik Dashboard (OMF) - Modulare Architektur - Version 3.1.1
Version: 3.1.1 - Refactored
"""


sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "components"))
import os
import sys

import streamlit as st
from components.dummy_component import show_dummy_component
from omf.config.config import LIVE_CFG, REPLAY_CFG
from omf.tools.mqtt_client import get_omf_mqtt_client

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "components"))

# =============================================================================
# COMPONENT LOADING - FAULT TOLERANT
# =============================================================================

# Komponenten-Imports mit Fehlerbehandlung
components = {}


def load_component(component_name, import_path, display_name=None):
    """Lädt eine Komponente fehlertolerant"""
    if display_name is None:
        display_name = component_name.replace("_", " ").title()

    try:
        module = __import__(import_path, fromlist=[f"show_{component_name}"])
        show_function = getattr(module, f"show_{component_name}")
        components[component_name] = show_function
    except ImportError as e:
        error_msg = str(e)
        components[component_name] = lambda: show_dummy_component(display_name, error_msg)


# Komponenten laden
load_component("message_center", "components.message_center", "Message Center")
load_component("overview", "components.overview", "Overview")
load_component("production_order", "components.production_order", "Production Order")
load_component("settings", "components.settings", "Settings")
load_component("steering", "components.steering", "Steering")
load_component("fts", "components.fts", "FTS")
load_component("ccu", "components.ccu", "CCU")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def setup_page_config():
    """Konfiguriert die Streamlit-Seite"""
    st.set_page_config(page_title="OMF Dashboard", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")


def get_default_broker_mode():
    """Holt den Default-Broker-Modus aus den Settings"""
    # Default = replay (für Testing ohne reale Fabrik)
    # TODO: In 2 Tagen wieder auf "live" umstellen
    return "replay"


def handle_environment_switch():
    """Behandelt den Wechsel zwischen Live- und Replay-Umgebung"""
    # Default aus Settings holen
    if "env" not in st.session_state:
        st.session_state["env"] = get_default_broker_mode()

    # Default-Modus Info
    default_mode = get_default_broker_mode()
    if default_mode == "replay":
        st.sidebar.info("🔄 **Default:** Replay-Modus (Testing)")
    else:
        st.sidebar.success("🏭 **Default:** Live-Modus (Produktion)")

    env_options = ["live", "replay", "mock"]
    env = st.sidebar.radio("Umgebung", env_options, index=env_options.index(st.session_state["env"]), horizontal=True)

    if env != st.session_state["env"]:
        # MQTT-Client bei Umgebungswechsel komplett neu initialisieren
        old_mqtt_client = st.session_state.get("mqtt_client")

        # Alten Client schließen
        if old_mqtt_client:
            try:
                old_mqtt_client.close()
            except Exception:
                pass

        st.session_state["env"] = env
        st.cache_resource.clear()

        # MQTT-Client aus session_state entfernen - wird neu erstellt
        if "mqtt_client" in st.session_state:
            del st.session_state["mqtt_client"]

        st.rerun()

    return env


def initialize_mqtt_client(env):
    """Initialisiert den MQTT-Client"""
    if env == "live":
        cfg = LIVE_CFG
    elif env == "replay":
        cfg = REPLAY_CFG
    else:
        cfg = {"host": "mock", "port": 0}

    # MQTT-Client nur einmal initialisieren (Singleton)
    if "mqtt_client" not in st.session_state:
        st.info("🔍 **Debug: Erstelle neuen MQTT-Client**")
        if env == "mock":
            client = MockMqttClient(cfg)
        else:
            client = get_omf_mqtt_client(cfg)
        st.session_state.mqtt_client = client
    else:
        client = st.session_state.mqtt_client
        st.info(f"   - Verwende bestehenden Client: {type(client).__name__}")

    # Automatisch verbinden wenn nicht verbunden (nur für echte Clients)
    if env != "mock" and not client.connected:

        # ...Imports stehen bereits am Anfang des Files...

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
        sys.path.append(os.path.join(os.path.dirname(__file__), "components"))


def setup_mqtt_subscription(client, cfg):
    """Richtet MQTT-Subscription ein"""
    # Subscribe zu allen Topics - nur einmal pro Broker-Verbindung
    broker_key = f"{cfg['host']}:{cfg['port']}"
    subscribed_key = f"mqtt_subscribed_{broker_key}"

    if not st.session_state.get(subscribed_key, False):
        try:
            client.subscribe("#", qos=1)
            st.session_state[subscribed_key] = True
            st.sidebar.info(f"📡 Subscribed zu allen Topics auf {broker_key}")
        except Exception as e:
            st.sidebar.error(f"❌ Subscribe-Fehler: {e}")
    else:
        st.sidebar.info(f"✅ Bereits subscribed zu {broker_key}")


def display_mqtt_status(client, cfg):
    """Zeigt MQTT-Status in der Sidebar"""
    # Erweiterte MQTT-Informationen in der Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔗 MQTT Status")

    # Verbindungsstatus - MQTT-Client connected-Eigenschaft ist nicht zuverlässig
    # Daher prüfen wir auch die Broker-Verbindung
    try:
        # Teste ob Client funktioniert (auch wenn connected=False)
        if hasattr(client, "client") and client.client and client.client.is_connected():
            st.sidebar.success(f"🟢 Verbunden: {cfg['host']}:{cfg['port']}")
        elif client.connected:
            st.sidebar.success(f"🟢 Verbunden: {cfg['host']}:{cfg['port']}")
        else:
            st.sidebar.warning(f"🟡 Verbindung unklar: {cfg['host']}:{cfg['port']}")
    except Exception:
        st.sidebar.error(f"🔴 Nicht verbunden: {cfg['host']}:{cfg['port']}")

    # MQTT-Statistiken
    try:
        stats = client.get_connection_status()
        messages_received = stats.get("stats", {}).get("messages_received", 0)
        messages_sent = stats.get("stats", {}).get("messages_sent", 0)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.sidebar.metric("📨 Empfangen", messages_received)
        with col2:
            st.sidebar.metric("📤 Gesendet", messages_sent)
    except Exception:
        st.sidebar.info("📊 Statistiken nicht verfügbar")


def display_refresh_button():
    """Zeigt den Aktualisieren-Button in der Sidebar"""
    # Genereller Aktualisieren-Button in Sidebar (für alle Seiten)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Aktualisierung")

    if st.sidebar.button("🔄 Seite aktualisieren", type="primary", key="sidebar_refresh_page"):
        st.rerun()


def display_header(client):
    """Zeigt den Dashboard-Header mit Logo und Status"""
    # Main title with ORBIS logo and MQTT connection status
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        try:
            # Versuche ORBIS-Logo zu laden - OMF-Struktur
            possible_paths = [
                # Variante 1: OMF Assets-Verzeichnis (neue Struktur)
                os.path.join(os.path.dirname(__file__), "assets", "orbis_logo.png"),
                # Variante 2: Fallback auf alte Struktur
                os.path.join(os.path.dirname(__file__), "..", "..", "mqtt", "dashboard", "assets", "orbis_logo.png"),
                # Variante 3: Absoluter Pfad vom Projekt-Root
                os.path.join(os.getcwd(), "src_orbis", "omf", "dashboard", "assets", "orbis_logo.png"),
            ]

            logo_found = False
            for logo_path in possible_paths:
                if os.path.exists(logo_path):
                    st.image(logo_path, width=100)
                    logo_found = True
                    break

            if not logo_found:
                # Fallback: Schönes Fabrik-Logo als Emoji
                st.markdown("🏭")
                st.caption("Modellfabrik")

        except Exception:
            # Fallback bei Fehlern: Schönes Fabrik-Logo
            st.markdown("🏭")
            st.caption("Modellfabrik")

    with col2:
        st.title("🏭 ORBIS Modellfabrik Dashboard")
        st.markdown("**Version:** 3.0.0 - Settings2 Test Version")

    with col3:
        # MQTT Status
        if client.connected:
            st.success("🔗 MQTT Verbunden")
        else:
            st.error("❌ MQTT Nicht verbunden")


def display_tabs():
    """Zeigt die Dashboard-Tabs und deren Inhalte"""
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📊 Übersicht",
            "🏭 Fertigungsaufträge",
            "📡 Nachrichten-Zentrale",
            "🎮 Steuerung",
            "🚛 FTS",
            "🏢 CCU",
            "⚙️ Einstellungen",
        ]
    )

    # Tab-Inhalte
    with tab1:
        components["overview"]()

    with tab2:
        components["production_order"]()

    with tab3:
        components["message_center"]()

    with tab4:
        components["steering"]()

    with tab5:
        components["fts"]()

    with tab6:
        components["ccu"]()

    with tab7:
        components["settings"]()


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def main():
    """Hauptfunktion des OMF Dashboards - Modulare Architektur"""
    # 1. Seite konfigurieren
    setup_page_config()

    # 2. Umgebung handhaben
    env = handle_environment_switch()

    # 3. MQTT-Client initialisieren
    client, cfg = initialize_mqtt_client(env)

    # 4. MQTT-Subscription einrichten
    setup_mqtt_subscription(client, cfg)

    # 5. MQTT-Status anzeigen
    display_mqtt_status(client, cfg)

    # 6. Aktualisieren-Button anzeigen
    display_refresh_button()

    # 7. Header anzeigen
    display_header(client)

    # 8. Tabs anzeigen
    display_tabs()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
