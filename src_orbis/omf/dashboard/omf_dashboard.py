"""
ORBIS Modellfabrik Dashboard (OMF) - Einfaches Grundgerüst
Version: 3.0.0
"""

import os
import sys

import streamlit as st

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Relative imports für lokale Entwicklung
from omf.config.config import LIVE_CFG, REPLAY_CFG  # noqa: E402
from omf.tools.mqtt_client import get_omf_mqtt_client  # noqa: E402

# Import settings components
try:
    from components.message_center import show_message_center
    from components.overview import show_overview_tabs
    from components.settings import (
        show_dashboard_settings,
        show_messages_templates,
        show_module_config,
        show_mqtt_config,
        show_nfc_config,
        show_topic_config,
    )
    from components.steering import show_steering
    from components.test_buttons import show_test_buttons
except ImportError:
    # Fallback für Import-Fehler
    def show_dashboard_settings():
        st.subheader("⚙️ Dashboard-Settings")
        st.info("Dashboard-Einstellungen werden hier angezeigt")

    def show_module_config():
        st.subheader("🏭 Modul-Config")
        st.info("Modul-Konfiguration wird hier angezeigt")

    def show_nfc_config():
        st.subheader("📱 NFC-Config")
        st.info("NFC-Konfiguration wird hier angezeigt")

    def show_topic_config():
        st.subheader("📡 Topic-Config")
        st.info("Topic-Konfiguration wird hier angezeigt")

    def show_messages_templates():
        st.subheader("📝 Messages-Templates")
        st.info("Message-Templates werden hier angezeigt")

    def show_mqtt_config():
        st.subheader("🔗 MQTT-Config")
        st.info("MQTT-Konfiguration wird hier angezeigt")

    def show_steering():
        st.subheader("🎮 Steuerung")
        st.info("Steuerung wird hier angezeigt")

    def show_message_center():
        st.subheader("📡 Nachrichtenzentrale")
        st.info("Nachrichtenzentrale wird hier angezeigt")

    def show_overview_tabs():
        st.subheader("📊 Overview")
        st.info("Overview wird hier angezeigt")


def main():
    """Hauptfunktion des OMF Dashboards"""
    st.set_page_config(page_title="OMF Dashboard", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

    # Default = live
    if "env" not in st.session_state:
        st.session_state["env"] = "live"

    env = st.sidebar.radio(
        "Umgebung", ["live", "replay"], index=0 if st.session_state["env"] == "live" else 1, horizontal=True
    )
    if env != st.session_state["env"]:
        st.session_state["env"] = env
        st.cache_resource.clear()
        st.rerun()

    cfg = LIVE_CFG if st.session_state["env"] == "live" else REPLAY_CFG
    client = get_omf_mqtt_client(cfg)

    # Automatisch verbinden wenn nicht verbunden
    if not client.connected:
        # Der Client verbindet sich automatisch im __init__
        # Warten auf Verbindung
        import time

        for _ in range(10):  # Max 10 Sekunden warten
            if client.connected:
                break
            time.sleep(0.1)

    st.sidebar.write("MQTT:", "🟢" if client.connected else "🔴", f"{cfg['host']}:{cfg['port']}")
    try:
        client.subscribe("#", qos=1)
    except Exception:
        pass

    # MQTT Client ist bereits initialisiert - verwende den ersten Client
    st.session_state.mqtt_client = client

    # Main title with ORBIS logo and MQTT connection status
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        try:
            # Versuche ORBIS-Logo zu laden - OMF-Struktur
            possible_paths = [
                # Variante 1: OMF Assets-Verzeichnis (neue Struktur)
                os.path.join(
                    os.path.dirname(__file__),
                    "assets",
                    "orbis_logo.png",
                ),
                # Variante 2: Fallback auf alte Struktur
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "mqtt",
                    "dashboard",
                    "assets",
                    "orbis_logo.png",
                ),
                # Variante 3: Absoluter Pfad vom Projekt-Root
                os.path.join(
                    os.getcwd(),
                    "src_orbis",
                    "omf",
                    "dashboard",
                    "assets",
                    "orbis_logo.png",
                ),
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
        st.title("Modellfabrik Dashboard")

    with col3:
        # Platz für zukünftige Status-Anzeigen
        st.info("🔗 MQTT-Status in Sidebar")

    st.markdown("---")

    # Sidebar mit MQTT Connection Management
    with st.sidebar:
        st.title("🏭 OMF Dashboard")
        st.markdown("---")

        # MQTT Connection Management
        st.subheader("🔗 MQTT Connection Management")

        try:
            mqtt_client = st.session_state.get("mqtt_client")
            if mqtt_client:
                # Connection Status
                if mqtt_client.connected:
                    st.success("✅ CONNECTED")

                    # Connection Info
                    connection_info = mqtt_client.get_connection_status()
                    broker_info = connection_info.get("broker", {})

                    st.info(f"**Broker:** {broker_info.get('host', 'Unknown')}:{broker_info.get('port', 'Unknown')}")
                    st.info(f"**Client ID:** {connection_info.get('client_id', 'Unknown')}")
                    st.info(f"**Mode:** {connection_info.get('mode', 'Unknown')}")

                    # Disconnect Button
                    if st.button("🔌 Disconnect", key="mqtt_disconnect", use_container_width=True):
                        mqtt_client.disconnect()
                        st.rerun()

                else:
                    st.error("❌ DISCONNECTED")

                    # Connection Status Info
                    st.info("**Verbindung wird über den Dashboard-Hauptclient verwaltet**")
                    st.info("**Keine manuellen Verbindungen nötig**")
            else:
                st.warning("⚠️ MQTT Client nicht verfügbar")

        except Exception as e:
            st.error(f"❌ Fehler beim MQTT-Status: {e}")

        st.markdown("---")

        # Quick Stats
        st.subheader("📊 Quick Stats")
        try:
            if mqtt_client:
                stats = mqtt_client.get_connection_status().get("stats", {})
                st.metric("📨 Messages Sent", stats.get("messages_sent", 0))
                st.metric("📥 Messages Received", stats.get("messages_received", 0))
            else:
                st.info("Keine Statistiken verfügbar")
        except Exception:
            st.info("Statistiken nicht verfügbar")

        st.markdown("---")

        # Navigation
        st.subheader("🧭 Navigation")
        st.info("Verwende die Tabs oben für die verschiedenen Bereiche")

    # Tab structure
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📊 Overview",
            "📋 Aufträge",
            "📡 Nachrichtenzentrale",
            "🎮 Steuerung",
            "🧪 Test-Bereich",
            "⚙️ Settings",
        ]
    )

    # Tab 1: Overview
    with tab1:
        show_overview_tabs()

    # Tab 2: Aufträge
    with tab2:
        st.header("📋 Aufträge")

        # Sub-tabs for Orders
        orders_tab1, orders_tab2 = st.tabs(["📋 Auftragsverwaltung", "🔄 Laufende Aufträge"])

        with orders_tab1:
            st.subheader("📋 Auftragsverwaltung")
            st.info("Auftragsverwaltung wird hier angezeigt")

        with orders_tab2:
            st.subheader("🔄 Laufende Aufträge")
            st.info("Laufende Aufträge werden hier angezeigt")

    # Tab 3: Nachrichtenzentrale
    with tab3:
        show_message_center()

    # Tab 4: Steuerung (Kommando-Zentrale)
    with tab4:
        show_steering()

    # Tab 5: Test-Bereich
    with tab5:
        show_test_buttons()

    # Tab 6: Settings
    with tab6:
        st.header("⚙️ Settings")

        # Sub-tabs for Settings
        (
            settings_tab1,
            settings_tab2,
            settings_tab3,
            settings_tab4,
            settings_tab5,
            settings_tab6,
        ) = st.tabs(
            [
                "⚙️ Dashboard-Settings",
                "🏭 Modul-Config",
                "📱 NFC-Config",
                "📡 Topic-Config",
                "🔗 MQTT-Config",
                "📝 Messages-Templates",
            ]
        )

        with settings_tab1:
            show_dashboard_settings()

        with settings_tab2:
            show_module_config()

        with settings_tab3:
            show_nfc_config()

        with settings_tab4:
            show_topic_config()

        with settings_tab5:
            show_mqtt_config()

        with settings_tab6:
            show_messages_templates()


if __name__ == "__main__":
    main()
