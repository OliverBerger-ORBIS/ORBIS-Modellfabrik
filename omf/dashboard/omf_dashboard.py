from __future__ import annotations

import logging
import os

import streamlit as st

from omf.config.config import LIVE_CFG, REPLAY_CFG
from omf.dashboard.components.dummy_component import show_dummy_component
from omf.tools.logging_config import configure_logging
from omf.tools.omf_mqtt_factory import ensure_dashboard_client
from omf.tools.streamlit_log_buffer import RingBufferHandler
from omf.tools.structlog_config import configure_structlog

"""
ORBIS Modellfabrik Dashboard (OMF) - Modulare Architektur
"""


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
load_component("module_state_control", "omf.dashboard.components.module_state_control", "Module Control")
load_component("logs", "omf.dashboard.components.logs", "Logs")
load_component("fts", "components.fts", "FTS")
load_component("ccu", "components.ccu", "CCU")
load_component("shopfloor", "components.shopfloor", "Shopfloor")

# =============================================================================
# LOGGING INITIALIZATION
# =============================================================================


def _init_logging_once():
    """Initialisiert Logging einmal pro Streamlit-Session"""
    if st.session_state.get("_log_init"):
        return

    # Logging konfigurieren (Log-Level aus Settings oder Default DEBUG)
    log_level_name = st.session_state.get("log_level", "DEBUG")
    log_level_map = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
    log_level = log_level_map.get(log_level_name, 10)

    root, listener = configure_logging(level=log_level, console_pretty=True)

    # Debug-Log für Log-Level-Verifikation
    print(f"🔍 DEBUG: Log-Level ist auf {log_level} gesetzt (DEBUG=10, INFO=20)")
    print(f"🔍 DEBUG: Root Logger Level: {root.level}")

    # Test-Log um zu prüfen ob Logging funktioniert
    test_logger = logging.getLogger("omf.dashboard.test")
    print(f"🔍 DEBUG: Test Logger Level VOR Konfiguration: {test_logger.level}")

    test_logger.info("🔧 Dashboard-Logging initialisiert")
    test_logger.debug("🐛 Debug-Logging aktiviert")

    print(f"🔍 DEBUG: Test Logger Level NACH Konfiguration: {test_logger.level}")

    # Direkter Debug-Test
    test_logger.debug("🧪 DIREKTER DEBUG-TEST NACH LOGGER-KONFIGURATION")
    test_logger.info("ℹ️ DIREKTER INFO-TEST NACH LOGGER-KONFIGURATION")

    # Zusätzlicher Test für RingBuffer
    if "log_buffer" in st.session_state:
        st.session_state.log_buffer.append("🧪 MANUELLER TEST-LOG FÜR RINGBUFFER")

    # Structlog konfigurieren (optional)
    try:
        configure_structlog()
    except Exception:
        pass

    # Log-Buffer für Live-Logs im Dashboard
    if "log_buffer" not in st.session_state:
        from collections import deque

        # Ring-Buffer erstellen
        buf = deque(maxlen=1000)
        st.session_state.log_buffer = buf

        # Ring-Buffer-Handler an Root-Logger anhängen
        rb = RingBufferHandler(buf)
        rb.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(rb)
        st.session_state["ring_buffer_handler"] = rb
    else:
        # RingBufferHandler aus Session State holen
        rb = st.session_state.get("ring_buffer_handler")
        if rb is None:
            # Fallback: Neuen Handler erstellen
            buf = st.session_state.log_buffer
            rb = RingBufferHandler(buf)
            rb.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            st.session_state["ring_buffer_handler"] = rb

    # Logger-Konfiguration NACH configure_logging() - das ist wichtig!
    # Stelle sicher, dass spezifische Logger auch den RingBufferHandler verwenden
    mqtt_logger = logging.getLogger("omf.tools.mqtt_gateway")
    mqtt_logger.addHandler(rb)
    mqtt_logger.setLevel(log_level)
    mqtt_logger.propagate = False  # Verhindere doppelte Logs

    debug_logger = logging.getLogger("omf.dashboard.debug")
    debug_logger.addHandler(rb)
    debug_logger.setLevel(log_level)
    debug_logger.propagate = False

    logs_test_logger = logging.getLogger("omf.dashboard.logs_test")
    logs_test_logger.addHandler(rb)
    logs_test_logger.setLevel(log_level)
    logs_test_logger.propagate = False

    # Test-Logger auch konfigurieren
    test_logger = logging.getLogger("omf.dashboard.test")
    test_logger.addHandler(rb)
    test_logger.setLevel(log_level)
    test_logger.propagate = False

    # Zusätzliche Debug-Tests nach Logger-Konfiguration
    print(f"🔍 DEBUG: MqttGateway Logger Level: {mqtt_logger.level}")
    print(f"🔍 DEBUG: Debug Logger Level: {debug_logger.level}")
    print(f"🔍 DEBUG: Test Logger Level: {test_logger.level}")

    # Debug-Tests nach Konfiguration
    mqtt_logger.debug("🔧 MQTT DEBUG-TEST NACH KONFIGURATION")
    debug_logger.debug("🐛 DEBUG LOGGER TEST NACH KONFIGURATION")
    test_logger.debug("🧪 TEST LOGGER DEBUG NACH KONFIGURATION")

    st.session_state["_log_init"] = True


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def setup_page_config():
    """Konfiguriert die Streamlit-Seite"""
    st.set_page_config(page_title="OMF Dashboard", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")


def get_default_broker_mode():
    """Holt den Default-Broker-Modus aus den Settings"""
    # Default = live (für Produktionsumgebung)
    return "replay"


def handle_environment_switch():
    """
    Behandelt den Wechsel zwischen Live- und Replay-Umgebung.

    Erweiterte Features basierend auf ChatGPT-Vorschlägen:
    - Prioritäts-Sidebar für Nachrichten-Zentrale
    - Verbesserte Umgebungswechsel-Logik
    """
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

    # Prioritäts-Sidebar (ChatGPT-Vorschlag)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Nachrichten-Zentrale")

    # Prioritäts-Slider
    current_priority = st.session_state.get("mc_priority", 6)
    priority = st.sidebar.select_slider(
        "Priorität",
        options=[1, 2, 3, 4, 5, 6],
        value=current_priority,
        help="1=Kritisch, 2=Wichtig, 3=Normal, 4=UI, 5=Spezifisch, 6=Alle",
    )

    # Debug: Client-ID anzeigen (falls verfügbar)
    client = st.session_state.get("mqtt_client")
    if client:
        st.sidebar.caption(f"🆔 Client ID: `{id(client)}`")
    else:
        st.sidebar.caption("🆔 Client ID: Noch nicht initialisiert")

    # Priorität anwenden wenn geändert
    if priority != current_priority:
        st.session_state["mc_priority"] = priority
        # Reset Subscription-Status für neue Priorität
        mqtt_client = st.session_state.get('mqtt_client', {})
        host = mqtt_client.cfg.host if hasattr(mqtt_client, 'cfg') else 'unknown'
        port = mqtt_client.cfg.port if hasattr(mqtt_client, 'cfg') else 'unknown'
        broker_key = f"{host}:{port}"
        subscribed_key = f"mqtt_subscribed_{broker_key}"
        if subscribed_key in st.session_state:
            del st.session_state[subscribed_key]
        st.rerun()

    if env != st.session_state["env"]:
        # Umgebungswechsel - Factory kümmert sich um Reconnect
        st.session_state["env"] = env
        st.cache_resource.clear()
        st.rerun()

    return env


def initialize_mqtt_client(env):
    """
    Initialisiert den MQTT-Client über die kontrollierte Factory.

    Verwendet ensure_dashboard_client() für Singleton-Verhalten:
    - Ein Client pro Session
    - Reconnect bei Umgebungswechsel
    - Robuste Fehlerbehandlung
    """
    # Verwende die kontrollierte Factory
    client = ensure_dashboard_client(env, st.session_state)

    # Automatisch verbinden wenn nicht verbunden
    if not client.connected:
        # Der Client verbindet sich automatisch im __init__
        # Warten auf Verbindung
        import time

        for _ in range(10):  # Max 10 Sekunden warten
            if client.connected:
                break
            time.sleep(0.1)

    # Konfiguration für Rückwärtskompatibilität
    if env == "live":
        cfg = LIVE_CFG
    elif env == "replay":
        cfg = REPLAY_CFG
    else:
        cfg = {"host": "mock", "port": 0}

    return client, cfg


def setup_mqtt_subscription(client, cfg):
    """
    Richtet MQTT-Subscription ein mit Prioritäts-basierter Logik.

    Subscribiert zu Topics basierend auf der gewählten Prioritätsstufe.
    """
    # Subscribe zu Topics - nur einmal pro Broker-Verbindung
    broker_key = f"{cfg['host']}:{cfg['port']}"
    subscribed_key = f"mqtt_subscribed_{broker_key}"

    if not st.session_state.get(subscribed_key, False):
        try:
            # Prioritäts-basierte Subscriptions
            if hasattr(client, "subscribe_many"):
                try:
                    from omf.dashboard.config.mc_priority import get_all_priority_filters

                    # Standard-Priorität 6 (alle Topics)
                    default_priority = st.session_state.get("mc_priority", 6)
                    priority_filters = get_all_priority_filters(default_priority)

                    if priority_filters:
                        client.subscribe_many(priority_filters, qos=1)
                        st.sidebar.info(f"📡 Subscribed zu Priorität {default_priority} Topics auf {broker_key}")
                        st.sidebar.caption(f"📋 {len(priority_filters)} Filter aktiv")
                    else:
                        # Fallback: Alle Topics
                        client.subscribe("#", qos=1)
                        st.sidebar.info(f"📡 Subscribed zu allen Topics auf {broker_key}")

                except ImportError:
                    # Fallback: Alle Topics wenn Prioritäts-Konfiguration nicht verfügbar
                    client.subscribe("#", qos=1)
                    st.sidebar.info(f"📡 Subscribed zu allen Topics auf {broker_key}")
                    st.sidebar.caption("ℹ️ Prioritäts-Filter nicht verfügbar")

            else:
                # Fallback: Standard-Subscription
                client.subscribe("#", qos=1)
                st.sidebar.info(f"📡 Subscribed zu allen Topics auf {broker_key}")
                st.sidebar.caption("ℹ️ Erweiterte Features nicht verfügbar")

            st.session_state[subscribed_key] = True

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
        if hasattr(client, "client") and client.client and client.connected:
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
            # ORBIS Logo im Header anzeigen (allLowercase Variante)
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "orbis_logo.png")
            if os.path.exists(logo_path):
                st.image(logo_path, width=100, caption="ORBIS Logo")
            else:
                st.markdown("🏭")
                st.caption("Modellfabrik")
        except Exception:
            st.markdown("🏭")
            st.caption("Modellfabrik")

    with col2:
        # Haupttitel (linksbündig ohne Symbol)
        st.markdown("# Modellfabrik Dashboard")

    with col3:
        # MQTT-Verbindung und Versions-Info
        if client.connected:
            st.success("🟢 MQTT Verbindung aktiv")
        else:
            st.error("🔴 MQTT Verbindung getrennt")

        # Versions-Info
        st.caption("Version 3.3.0")


# =============================================================================
# MODULE LOGO HELPER
# =============================================================================
def get_module_logo(module_name):
    """Gibt den Pfad zum Modul-Icon zurück, falls vorhanden, sonst None."""
    # Prüfe PNG und JPEG mit lowercase Namen (wie in asset_manager.py)
    icon_filename_png = f"{module_name.lower()}_icon.png"
    icon_filename_jpeg = f"{module_name.lower()}_icon.jpeg"
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    icon_path_png = os.path.join(assets_dir, icon_filename_png)
    icon_path_jpeg = os.path.join(assets_dir, icon_filename_jpeg)
    if os.path.exists(icon_path_png):
        return icon_path_png
    elif os.path.exists(icon_path_jpeg):
        return icon_path_jpeg
    else:
        return None


def display_tabs():
    """Zeigt die Dashboard-Tabs und deren Inhalte"""
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(
        [
            "📊 Übersicht",
            "🏭 Fertigungsaufträge",
            "📡 Nachrichten-Zentrale",
            "🎮 Steuerung",
            "🏗️ Shopfloor",
            "🚛 FTS",
            "🏢 CCU",
            "⚙️ Einstellungen",
            "🔧 Modul-Steuerung",
            "📋 Logs",
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
        components["shopfloor"]()

    with tab6:
        components["fts"]()

    with tab7:
        components["ccu"]()

    with tab8:
        components["settings"]()

    with tab9:
        components["module_state_control"]()

    with tab10:
        components["logs"]()


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def main():
    """Hauptfunktion des OMF Dashboards - Modulare Architektur"""
    # 1. Logging initialisieren (einmal pro Session)
    _init_logging_once()

    # 2. Seite konfigurieren
    setup_page_config()

    # 3. Umgebung handhaben
    env = handle_environment_switch()

    # 4. MQTT-Client initialisieren
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
