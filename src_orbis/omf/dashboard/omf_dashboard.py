"""
ORBIS Modellfabrik Dashboard (OMF) - Einfaches Grundgerüst
Version: 3.0.0
"""

import os
import sys

import streamlit as st

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

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

    # Page config
    st.set_page_config(
        page_title="Modellfabrik Dashboard",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

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
        # Platzsparende MQTT Connection Status
        try:
            # Füge den tools-Pfad hinzu
            tools_path = os.path.join(os.path.dirname(__file__), "..", "tools")
            if tools_path not in sys.path:
                sys.path.append(tools_path)

            from mqtt_client import get_omf_mqtt_client

            mqtt_client = get_omf_mqtt_client()

            # Connection Status (inkl. Modus-Support)
            mqtt_mode = st.session_state.get("mqtt_mode", "live")
            mock_enabled = st.session_state.get("mqtt_mock_enabled", False)

            # Automatische Verbindung für Replay-Modus
            if mqtt_mode == "replay" and not mqtt_client.is_connected():
                if mqtt_client.connect("replay"):
                    st.success("✅ Auto-Connect Replay-Broker")
                else:
                    st.warning("⚠️ Auto-Connect fehlgeschlagen")

            # Platzsparende Anzeige
            if mock_enabled:
                st.success("🧪 MOCK")
                stats = mqtt_client.get_statistics()
                st.metric("📨", stats.get("messages_received", 0), "Empfangen")
            elif mqtt_mode == "replay":
                if mqtt_client.is_connected():
                    st.success("🎬 REPLAY-BROKER")
                    stats = mqtt_client.get_statistics()
                    st.metric("📨", stats.get("messages_received", 0), "Empfangen")
                else:
                    st.error("🎬 REPLAY-BROKER")
                    if st.button("🔗 Connect", key="replay_connect", use_container_width=True):
                        if mqtt_client.connect("replay"):
                            st.success("✅ Connected!")
                        else:
                            st.error("❌ Failed!")
                        st.rerun()
            elif mqtt_client.is_connected():
                st.success("🔗 LIVE-FABRIK")
                stats = mqtt_client.get_statistics()
                st.metric("📨", stats.get("messages_received", 0), "Empfangen")
                if st.button("🔌 Disconnect", key="mqtt_disconnect", use_container_width=True):
                    mqtt_client.disconnect()
                    st.rerun()
            else:
                st.error("❌ DISCONNECTED")
                if st.button("🔗 Connect", key="mqtt_connect", use_container_width=True):
                    if mqtt_client.connect():
                        st.success("✅ Connected!")
                    else:
                        st.error("❌ Failed!")
                    st.rerun()
        except ImportError:
            st.warning("⚠️ MQTT Client nicht verfügbar")

    st.markdown("---")

    # Tab structure
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "📋 Aufträge",
            "📡 Nachrichtenzentrale",
            "🎮 Steuerung",
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

    # Tab 5: Settings
    with tab5:
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
