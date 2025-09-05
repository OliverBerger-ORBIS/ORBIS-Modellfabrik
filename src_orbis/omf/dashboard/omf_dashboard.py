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

# Import settings components - Modulare Architektur
try:
    from components.message_center import show_message_center
    from components.overview import show_overview
    from components.production_order import show_production_order
    from components.settings import show_settings
    from components.steering import show_steering

except ImportError:
    pass


def main():
    """Hauptfunktion des OMF Dashboards - Modulare Architektur"""
    st.set_page_config(page_title="OMF Dashboard", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

    # Default = live
    if "env" not in st.session_state:
        st.session_state["env"] = "live"

    env = st.sidebar.radio(
        "Umgebung", ["live", "replay"], index=0 if st.session_state["env"] == "live" else 1, horizontal=True
    )
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

    cfg = LIVE_CFG if st.session_state["env"] == "live" else REPLAY_CFG

    # MQTT-Client nur einmal initialisieren (Singleton)
    if "mqtt_client" not in st.session_state:
        st.info("🔍 **Debug: Erstelle neuen MQTT-Client**")
        client = get_omf_mqtt_client(cfg)
        st.session_state.mqtt_client = client

    else:

        client = st.session_state.mqtt_client
        st.info(f"   - Verwende bestehenden Client: {type(client).__name__}")

    # Automatisch verbinden wenn nicht verbunden
    if not client.connected:
        # Der Client verbindet sich automatisch im __init__
        # Warten auf Verbindung
        import time

        for _ in range(10):  # Max 10 Sekunden warten
            if client.connected:
                break
            time.sleep(0.1)

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

    # Genereller Aktualisieren-Button in Sidebar (für alle Seiten)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Aktualisierung")

    if st.sidebar.button("🔄 Seite aktualisieren", type="primary", key="sidebar_refresh_page"):
        st.rerun()

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Übersicht", "🏭 Fertigungsaufträge", "📡 Nachrichten-Zentrale", "🎮 Steuerung", "⚙️ Einstellungen"]
    )

    # Tab 1: Übersicht
    with tab1:
        show_overview()

    # Tab 2: Fertigungsaufträge (Production Orders)
    with tab2:
        show_production_order()

    # Tab 3: Nachrichten-Zentrale
    with tab3:
        show_message_center()

    # Tab 4: Steuerung
    with tab4:
        show_steering()

    # Tab 5: Einstellungen
    with tab5:
        show_settings()


if __name__ == "__main__":
    main()
