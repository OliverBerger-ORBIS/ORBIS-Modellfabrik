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
    from components.settings import (
        show_dashboard_settings,
        show_messages_templates,
        show_module_config,
        show_mqtt_config,
        show_nfc_config,
        show_topic_config,
    )
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


def main():
    """Hauptfunktion des OMF Dashboards"""

    # Page config
    st.set_page_config(
        page_title="ORBIS Modellfabrik Dashboard",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Main title with ORBIS logo and MQTT connection status
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        try:
            logo_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "mqtt",
                "dashboard",
                "assets",
                "orbis_logo.png",
            )
            if os.path.exists(logo_path):
                st.image(logo_path, width=100)
            else:
                st.markdown("🔵")
        except Exception:
            st.markdown("🔵")

    with col2:
        st.title("ORBIS Modellfabrik Dashboard")

    with col3:
        # MQTT Connection Status
        try:
            # Füge den tools-Pfad hinzu
            tools_path = os.path.join(os.path.dirname(__file__), "..", "tools")
            if tools_path not in sys.path:
                sys.path.append(tools_path)

            from mqtt_client import get_omf_mqtt_client

            mqtt_client = get_omf_mqtt_client()

            # Connection Status
            if mqtt_client.is_connected():
                st.success("🔗 MQTT Connected")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(
                        "🔌 Disconnect", 
                        key="mqtt_disconnect", 
                        use_container_width=True
                    ):
                        mqtt_client.disconnect()
                        st.rerun()
                with col_btn2:
                    # Statistiken anzeigen
                    stats = mqtt_client.get_statistics()
                    st.metric(
                        "📨",
                        stats.get("messages_received", 0),
                        help="Empfangene Nachrichten",
                    )
            else:
                st.error("❌ MQTT Disconnected")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(
                        "🔗 Connect", 
                        key="mqtt_connect", 
                        use_container_width=True
                    ):
                        if mqtt_client.connect():
                            st.success("✅ Connected successfully!")
                        else:
                            st.error("❌ Connection failed!")
                        st.rerun()
                with col_btn2:
                    # Verbindungsversuche anzeigen
                    stats = mqtt_client.get_statistics()
                    st.metric(
                        "🔄",
                        stats.get("connection_attempts", 0),
                        help="Verbindungsversuche",
                    )
        except ImportError:
            st.warning("⚠️ MQTT Client nicht verfügbar")

    st.markdown("---")

    # Tab structure
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "📋 Aufträge",
            "📡 Messages-Monitor",
            "🎮 Message-Controls",
            "⚙️ Settings",
        ]
    )

    # Tab 1: Overview
    with tab1:
        st.header("📊 Overview")

        # Sub-tabs for Overview
        overview_tab1, overview_tab2, overview_tab3, overview_tab4 = st.tabs(
            [
                "🏭 Modul-Status", 
                "📦 Bestellung", 
                "🔧 Bestellung-Rohware", 
                "📚 Lagerbestand"
            ]
        )

        with overview_tab1:
            st.subheader("🏭 Modul-Status")
            st.info("Modul-Status wird hier angezeigt")

        with overview_tab2:
            st.subheader("📦 Bestellung")
            st.info("Bestellungen werden hier angezeigt")

        with overview_tab3:
            st.subheader("🔧 Bestellung-Rohware")
            st.info("Bestellung-Rohware wird hier angezeigt")

        with overview_tab4:
            st.subheader("📚 Lagerbestand")
            st.info("Lagerbestand wird hier angezeigt")

    # Tab 2: Aufträge
    with tab2:
        st.header("📋 Aufträge")

        # Sub-tabs for Orders
        orders_tab1, orders_tab2 = st.tabs(
            ["📋 Auftragsverwaltung", "🔄 Laufende Aufträge"]
        )

        with orders_tab1:
            st.subheader("📋 Auftragsverwaltung")
            st.info("Auftragsverwaltung wird hier angezeigt")

        with orders_tab2:
            st.subheader("🔄 Laufende Aufträge")
            st.info("Laufende Aufträge werden hier angezeigt")

    # Tab 3: Messages-Monitor
    with tab3:
        st.header("📡 Messages-Monitor")
        st.info("MQTT-Messages werden hier angezeigt")

    # Tab 4: Message-Controls
    with tab4:
        st.header("🎮 Message-Controls")
        st.info("Fabrik/Module-Steuerung wird hier angezeigt")

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
