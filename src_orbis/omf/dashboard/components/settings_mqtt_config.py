"""
OMF Dashboard Settings - MQTT-Konfiguration
Exakte Kopie der show_mqtt_config Funktion aus settings.py
"""

import streamlit as st


def show_mqtt_config():
    """Zeigt die MQTT-Broker Konfiguration an"""
    st.markdown("### 🔗 MQTT-Broker Konfiguration")
    st.markdown("MQTT-Broker Einstellungen und Verbindungsverwaltung")

    # Aktueller Modus-Status anzeigen
    current_mode = st.session_state.get("mqtt_mode", "live")
    mode_display = {
        "live": "🏭 Live-Fabrik",
        "replay": "🎬 Replay-Station",
        "mock": "🧪 Mock-Modus",
    }.get(current_mode, current_mode)

    st.info(f"**Aktueller Modus:** {mode_display} (Einstellung über Sidebar)")
    st.markdown("💡 **Hinweis:** Der MQTT-Verbindungsmodus wird über die Sidebar-Umgebungsauswahl (Live/Replay) konfiguriert.")

    st.markdown("---")

    try:
        import os
        import sys

        # Füge den tools-Pfad hinzu
        tools_path = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
        if tools_path not in sys.path:
            sys.path.append(tools_path)

        # Verwende Dashboard MQTT-Client
        mqtt_client = st.session_state.get("mqtt_client")


        # Broker Konfiguration
        st.markdown("#### 🌐 Broker Einstellungen")

        # Aktuelle Broker-Konfiguration basierend auf Sidebar-Modus
        current_mode = st.session_state.get("env", "live")
        mode_display = {
            "live": "🏭 Live-Fabrik",
            "replay": "🎬 Replay-Broker",
            "mock": "🧪 Mock-Modus",
        }.get(current_mode, current_mode)

        st.info(f"**Aktuelle Konfiguration:** {mode_display}")

        if current_mode == "replay":
            st.info("🎬 **Replay-Broker:** localhost:1884 (Mosquitto MQTT-Broker)")
        elif current_mode == "mock":
            st.info("🧪 **Mock-Modus:** Simulierte Verbindung (kein echter Broker)")
        else:
            st.info("🏭 **Live-Fabrik:** Echte APS-Modellfabrik")

        # Lade aktuelle Konfiguration
        config = mqtt_client.config
        broker_config = config.get("broker", {}).get("aps", {})

        col1, col2 = st.columns(2)
        with col1:
            # Modus-spezifische Host/Port-Anzeige
            if current_mode == "replay":
                host_value = "localhost"
                port_value = 1884
                host_disabled = True
                port_disabled = True
                st.info("🎬 **Replay-Broker:** Automatische Konfiguration")
            elif current_mode == "mock":
                host_value = "mock"
                port_value = 0
                host_disabled = True
                port_disabled = True
                st.info("🧪 **Mock-Modus:** Keine echte Verbindung")
            else:
                host_value = broker_config.get("host", "192.168.178.100")
                port_value = broker_config.get("port", 1883)
                host_disabled = False
                port_disabled = False
                st.info("🏭 **Live-Fabrik:** Konfigurierbare Einstellungen")

            host = st.text_input("🌐 Host", value=host_value, key="mqtt_host", disabled=host_disabled)

            port = st.number_input(
                "🔌 Port",
                min_value=1,
                max_value=65535,
                value=port_value,
                key="mqtt_port",
                disabled=port_disabled,
            )

            client_id = st.text_input(
                "🆔 Client ID",
                value=broker_config.get("client_id", "omf_dashboard"),
                key="mqtt_client_id",
            )

        with col2:
            username = st.text_input(
                "👤 Username",
                value=broker_config.get("username", ""),
                key="mqtt_username",
            )

            password = st.text_input(
                "🔒 Password",
                value=broker_config.get("password", ""),
                type="password",
                key="mqtt_password",
            )

            keepalive = st.number_input(
                "⏱️ Keepalive (Sekunden)",
                min_value=1,
                max_value=3600,
                value=broker_config.get("keepalive", 60),
                key="mqtt_keepalive",
            )

        # Speichern Button
        if st.button("💾 Broker-Konfiguration speichern"):
            # Update Konfiguration
            broker_config.update(
                {
                    "host": host,
                    "port": port,
                    "username": username,
                    "password": password,
                    "client_id": client_id,
                    "keepalive": keepalive,
                }
            )

            # Speichere Konfiguration
            try:
                import yaml

                config_path = os.path.join(tools_path, "..", "config", "mqtt_config.yml")
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                st.success("✅ Broker-Konfiguration gespeichert!")
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {e}")

        st.markdown("---")

        # Topic Subscriptions
        st.markdown("#### 📡 Topic Subscriptions")
        subscriptions = config.get("subscriptions", {})

        for category, topics in subscriptions.items():
            with st.expander(f"📡 {category.upper()}", expanded=False):
                for topic in topics:
                    st.code(topic)

    except ImportError:
        st.error("MQTT Client konnte nicht importiert werden.")
        st.info("MQTT-Konfiguration wird implementiert...")
