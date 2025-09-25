from __future__ import annotations

import logging
import os
from pathlib import Path

import streamlit as st

from omf.config.config import LIVE_CFG, REPLAY_CFG
from omf.dashboard.components.dummy_component import show_dummy_component
from omf.dashboard.tools.logging_config import configure_logging, get_logger
from omf.dashboard.tools.omf_mqtt_factory import ensure_dashboard_client

# Logger für Dashboard
logger = get_logger("omf.dashboard")
from omf.dashboard.tools.streamlit_log_buffer import RingBufferHandler
from omf.dashboard.tools.structlog_config import configure_structlog
from omf.dashboard.utils.ui_refresh import request_refresh, consume_refresh

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
# load_component("overview", "components.overview", "Overview")  # Entfernt - wird ersetzt durch aps_overview
# load_component("production_order", "components.production_order", "Production Order")  # Entfernt - nur Placeholder
load_component("settings", "components.settings", "Settings")
load_component("steering", "components.steering", "Steering")
load_component("wl_module_state_control", "omf.dashboard.components.wl_module_state_control", "WL Module Control")
load_component("logs", "omf.dashboard.components.logs", "Logs")
# load_component("fts", "components.fts", "FTS")  # Entfernt - übernommen in aps_modules.py
# load_component("ccu", "components.ccu", "CCU")  # Entfernt - übernommen in aps_modules.py
# load_component("shopfloor", "components.shopfloor", "Shopfloor")  # Entfernt - übernommen in aps_modules.py

# APS-spezifische Komponenten
load_component("aps_control", "components.aps_control", "APS Control")
# load_component("aps_orders", "components.aps_orders", "APS Orders")  # Entfernt - redundant
load_component("aps_orders", "components.aps_orders", "APS Orders")
# load_component("aps_steering", "components.aps_steering", "APS Steering")  # Entfernt - redundant
load_component("aps_configuration", "components.aps_configuration", "APS Configuration")
load_component("aps_modules", "components.aps_modules", "APS Modules")
load_component("aps_overview", "components.aps_overview", "APS Overview")
# load_component("aps_overview_new", "components.aps_overview_new", "APS Overview New")  # Entfernt - redundant
load_component("aps_processes", "components.aps_processes", "APS Processes")

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

    # Logger für Debug-Logs erstellen
    logger = get_logger("omf.dashboard.init")

    # Debug-Log für Log-Level-Verifikation
    logger.debug(f"🔍 DEBUG: Log-Level ist auf {log_level} gesetzt (DEBUG=10, INFO=20)")
    logger.debug(f"🔍 DEBUG: Root Logger Level: {root.level}")

    # OMF-Logging für Dashboard (thread-sicher)
    dashboard_logger = get_logger("omf.dashboard")
    dashboard_logger.info("🔧 Dashboard-Logging initialisiert")

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

    # OMF-Logging für MQTT (thread-sicher für Callbacks)
    mqtt_logger = get_logger("omf.dashboard.tools.mqtt_gateway")
    mqtt_logger.addHandler(rb)
    mqtt_logger.setLevel(log_level)
    mqtt_logger.propagate = False  # Verhindere doppelte Logs

    # Debug-Info für Logger-Konfiguration
    logger.debug(f"🔍 DEBUG: MqttGateway Logger Level: {mqtt_logger.level}")
    logger.debug(f"🔍 DEBUG: Dashboard Logger Level: {dashboard_logger.level}")

    # Debug-Tests nach Konfiguration
    mqtt_logger.debug("🔧 MQTT DEBUG-TEST NACH KONFIGURATION")
    dashboard_logger.debug("🐛 DASHBOARD DEBUG-TEST NACH KONFIGURATION")

    st.session_state["_log_init"] = True


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def setup_page_config():
    """Konfiguriert die Streamlit-Seite"""
    st.set_page_config(page_title="OMF Dashboard", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")


def get_default_broker_mode():
    """Holt den Default-Broker-Modus aus den Settings"""
    # Default = replay (für Testing)
    return "replay"


def handle_environment_switch():
    """
    Behandelt den Wechsel zwischen Live- und Replay-Umgebung.

    Erweiterte Features basierend auf ChatGPT-Vorschlägen:
    - Prioritäts-Sidebar für Nachrichten-Zentrale
    - Verbesserte Umgebungswechsel-Logik
    """
    # Debug-Logging: Environment-Switch Start
    logger.info(f"🔍 ENV-SWITCH: handle_environment_switch gestartet")
    
    # Default aus Settings holen
    if "env" not in st.session_state:
        default_env = get_default_broker_mode()
        st.session_state["env"] = default_env
        logger.info(f"🔍 ENV-SWITCH: Default Environment gesetzt: '{default_env}'")
    else:
        logger.info(f"🔍 ENV-SWITCH: Bestehende Environment: '{st.session_state['env']}'")

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
        request_refresh()

    if env != st.session_state["env"]:
        # Umgebungswechsel - Factory kümmert sich um Reconnect
        old_env = st.session_state["env"]
        logger.info(f"🔄 ENV-SWITCH: Environment-Wechsel erkannt: '{old_env}' -> '{env}'")
        st.session_state["env"] = env
        st.cache_resource.clear()
        logger.info(f"🔄 ENV-SWITCH: Cache geleert, Environment aktualisiert")
        # KEIN request_refresh() - verursacht Connection-Loop!
        # Die Factory kümmert sich automatisch um den Reconnect
    else:
        logger.info(f"♻️ ENV-SWITCH: Kein Environment-Wechsel, env='{env}' bleibt gleich")

    logger.info(f"🔍 ENV-SWITCH: handle_environment_switch beendet, return env='{env}'")
    return env


def initialize_mqtt_client(env):
    """
    Initialisiert den MQTT-Client über die kontrollierte Factory.

    Verwendet ensure_dashboard_client() für Singleton-Verhalten:
    - Ein Client pro Session
    - Reconnect bei Umgebungswechsel
    - Robuste Fehlerbehandlung
    """
    # Debug-Logging: Aufruf protokollieren
    logger.info(f"🔍 initialize_mqtt_client aufgerufen: env='{env}'")
    
    # Verwende die kontrollierte Factory
    client = ensure_dashboard_client(env, st.session_state)
    
    logger.info(f"🔍 initialize_mqtt_client: Client erhalten, connected={client.connected}")

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
        request_refresh()


def display_header(client):
    """Zeigt den Dashboard-Header mit Logo, Titel und Controls"""
    # Header Layout: Logo, Titel, Controls
    header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

    with header_col1:
        try:
            # ORBIS Logo im Header anzeigen (allLowercase Variante)
            logo_path = str(Path(__file__).parent / "assets" / "orbis_logo.png")
            if os.path.exists(logo_path):
                st.image(logo_path, width=100, caption="ORBIS Logo")
            else:
                st.markdown("🏭")
                st.caption("Modellfabrik")
        except Exception:
            st.markdown("🏭")
            st.caption("Modellfabrik")

    with header_col2:
        # Haupttitel (zentriert)
        st.markdown("# Modellfabrik Dashboard")

    with header_col3:
        # Factory Reset Controls
        from omf.dashboard.components.controls.factory_reset import render_factory_reset
        render_factory_reset()
        
        # MQTT-Verbindung Info
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
    assets_dir = str(Path(__file__).parent / "assets")
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
    # Tabs (reduziert von 16 auf 11 Tabs) - Korrekte Reihenfolge: APS → Werksleiter → Admin
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(
        [
            # APS-Tabs (Business-User)
            "🏭 APS Overview",
            "📋 APS Orders",
            "🔄 APS Processes",
            "⚙️ APS Configuration",
            "🏭 APS Modules",
            # Werksleiter-Tabs (WL)
            "🔧 WL Modul-Steuerung",
            "⚙️ WL System Control",
            # Admin-Tabs (System)
            "🎮 Steuerung",
            "📡 Nachrichten-Zentrale",
            "📋 Logs",
            "⚙️ Einstellungen",
        ]
    )

    # Tab-Inhalte (reduziert von 16 auf 11 Tabs) - Korrekte Reihenfolge: APS → Werksleiter → Admin
    # APS-Tabs (Business-User)
    with tab1:
        components["aps_overview"]()

    with tab2:
        components["aps_orders"]()

    with tab3:
        components["aps_processes"]()

    with tab4:
        components["aps_configuration"]()

    with tab5:
        components["aps_modules"]()

    # Werksleiter-Tabs (WL)
    with tab6:
        components["wl_module_state_control"]()

    with tab7:
        components["aps_control"]()

    # Admin-Tabs (System)
    with tab8:
        components["steering"]()

    with tab9:
        components["message_center"]()

    with tab10:
        components["logs"]()

    with tab11:
        components["settings"]()


# =============================================================================
# MAIN FUNCTION
# =============================================================================


def main():
    """Hauptfunktion des OMF Dashboards - Modulare Architektur"""
    # 1. Logging initialisieren (einmal pro Session)
    _init_logging_once()

    # 2. UI-Refresh verarbeiten (früh aufrufen)
    if consume_refresh():
        st.rerun()

    # 3. Seite konfigurieren
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
