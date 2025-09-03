"""
ORBIS Modellfabrik Dashboard (OMF) - Einfaches Grundgerüst - Version 2
Version: 3.0.0 - Settings2 Test Version
"""

import os
import sys

import streamlit as st

# Add src_orbis to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Relative imports für lokale Entwicklung
from omf.config.config import LIVE_CFG, REPLAY_CFG  # noqa: E402
from omf.tools.mqtt_client import get_omf_mqtt_client  # noqa: E402

# Import settings components - NEUE VERSION mit settings2, steering2, order2 und overview2
try:
    from components.message_center2 import show_message_center2
    from components.overview2 import show_overview2  # NEU: overview2 statt overview
    from components.order2 import show_order2  # NEU: order2
    from components.settings2 import show_settings2  # NEU: settings2 statt einzelne Funktionen
    from components.steering2 import show_steering2  # NEU: steering2 statt steering

except ImportError:
    # Fallback für Import-Fehler
    def show_settings2():
        st.subheader("⚙️ Settings2")
        st.info("Settings2 wird hier angezeigt")

    def show_overview2():
        st.subheader("📊 Overview2")
        st.info("Overview2 wird hier angezeigt")

    def show_order2():
        st.subheader("📋 Order2")
        st.info("Order2 wird hier angezeigt")

    def show_steering2():
        st.subheader("🎮 Steuerung2")
        st.info("Steuerung2 wird hier angezeigt")

    def show_message_center2():
        st.subheader("📡 Nachrichtenzentrale2")
        st.info("Nachrichtenzentrale2 wird hier angezeigt")


def main():
    """Hauptfunktion des OMF Dashboards - Version 2 mit settings2"""
    st.set_page_config(page_title="OMF Dashboard2", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

    # Default = live
    if "env" not in st.session_state:
        st.session_state["env"] = "live"

    env = st.sidebar.radio(
        "Umgebung", ["live", "replay"], index=0 if st.session_state["env"] == "live" else 1, horizontal=True
    )
    if env != st.session_state["env"]:
        # MQTT-Client sichern bevor Cache gelöscht wird
        old_mqtt_client = st.session_state.get("mqtt_client")

        st.session_state["env"] = env
        st.cache_resource.clear()

        # MQTT-Client wiederherstellen
        if old_mqtt_client:
            st.session_state.mqtt_client = old_mqtt_client

        st.rerun()

    cfg = LIVE_CFG if st.session_state["env"] == "live" else REPLAY_CFG

    # MQTT-Client nur einmal initialisieren (Singleton)
    if "mqtt_client" not in st.session_state:
        st.info("🔍 **Debug: Erstelle neuen MQTT-Client**")
        client = get_omf_mqtt_client(cfg)
        st.session_state.mqtt_client = client
        st.info(f"   - Neuer Client erstellt: {type(client).__name__}")
        st.info(f"   - Client ID: {id(client)}")
        st.info(f"   - Hat clear_history: {hasattr(client, 'clear_history')}")
    else:
        st.info("🔍 **Debug: Verwende bestehenden MQTT-Client**")
        client = st.session_state.mqtt_client
        st.info(f"   - Bestehender Client: {type(client).__name__}")
        st.info(f"   - Client ID: {id(client)}")
        st.info(f"   - Hat clear_history: {hasattr(client, 'clear_history')}")

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
        st.title("🏭 ORBIS Modellfabrik Dashboard")
        st.markdown("**Version:** 3.0.0 - Settings2 Test Version")

    with col3:
        # MQTT Status
        if client.connected:
            st.success("🔗 MQTT Verbunden")
        else:
            st.error("❌ MQTT Nicht verbunden")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Übersicht",
        "📋 Aufträge",
        "📡 Nachrichten-Zentrale",
        "🎮 Steuerung",
        "⚙️ Einstellungen"
    ])

    # Tab 1: Übersicht
    with tab1:
        show_overview2()

    # Tab 2: Aufträge
    with tab2:
        show_order2()

    # Tab 3: Nachrichten-Zentrale
    with tab3:
        show_message_center2()

    # Tab 4: Steuerung
    with tab4:
        show_steering2()

    # Tab 5: Einstellungen
    with tab5:
        show_settings2()


if __name__ == "__main__":
    main()
