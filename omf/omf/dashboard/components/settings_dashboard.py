"""
OMF Dashboard Settings - Dashboard Einstellungen
Exakte Kopie der show_dashboard_settings Funktion aus settings.py
"""

import streamlit as st

from src_orbis.omf.dashboard.utils.ui_refresh import request_refresh


def show_dashboard_settings():
    """Zeigt Dashboard-Einstellungen"""
    st.subheader("⚙️ Dashboard-Einstellungen")

    # Default Broker-Connection-Modus
    st.markdown("#### 🔗 Default Broker-Connection")

    col1, col2 = st.columns([2, 1])

    with col1:
        default_broker_mode = st.selectbox(
            "🌐 Default Broker-Modus",
            options=["live", "replay"],
            index=1,  # Default: replay (für Testing)
            key="settings_default_broker_mode",
            help="Standard-Broker-Modus beim Dashboard-Start",
        )

        if default_broker_mode == "replay":
            st.info("🔄 **Replay-Modus:** Für Testing ohne reale Fabrik")
        else:
            st.success("🏭 **Live-Modus:** Verbindung zur realen Fabrik")

    with col2:
        st.markdown("#### 📅 Zeitplan")
        st.info("⏰ **In 2 Tagen:** Wieder auf Live-Modus umstellen")

    # MQTT-Verbindungsmodus wird jetzt über Sidebar verwaltet
    st.markdown("#### 🔄 Aktuelle Verbindung")
    st.info("💡 **MQTT-Verbindungsmodus wird über die Sidebar konfiguriert**")

    # Auto-Refresh-Einstellungen (global für alle Seiten)
    st.markdown("#### 🔄 Auto-Refresh-Einstellungen")

    col1, col2 = st.columns([1, 1])

    with col1:
        auto_refresh_enabled = st.checkbox(
            "🔄 Auto-Refresh aktivieren",
            value=st.session_state.get("auto_refresh_enabled", False),
            key="settings_auto_refresh_enabled",
            help="Aktiviert automatische Aktualisierung aller Dashboard-Seiten",
        )
        st.session_state["auto_refresh_enabled"] = auto_refresh_enabled

    with col2:
        if auto_refresh_enabled:
            refresh_interval = st.selectbox(
                "⏰ Aktualisierungsintervall",
                options=[5, 10, 30, 60],
                index=1,  # Default: 10 Sekunden
                key="settings_auto_refresh_interval",
                help="Intervall für automatische Aktualisierung in Sekunden",
            )
            st.session_state["auto_refresh_interval"] = refresh_interval
            st.caption(f"📊 Aktualisierung alle {refresh_interval} Sekunden")
        else:
            st.info("ℹ️ Auto-Refresh deaktiviert")

    # Logging-Einstellungen
    st.markdown("#### 📝 Logging-Einstellungen")

    col1, col2 = st.columns([1, 1])

    with col1:
        log_level = st.selectbox(
            "📊 Log-Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            index=0,  # Default: DEBUG
            key="settings_log_level",
            help="Logging-Level für Dashboard-Logs",
        )
        st.session_state["log_level"] = log_level

    with col2:
        if st.button("🔄 Logging neu laden", type="secondary"):
            # Logging-Konfiguration zurücksetzen
            if "_log_init" in st.session_state:
                del st.session_state["_log_init"]
            st.success("✅ Logging-Konfiguration wird beim nächsten Reload angewendet")
            request_refresh()

    # Weitere Dashboard-Einstellungen können hier hinzugefügt werden
    st.markdown("#### 📊 Dashboard-Konfiguration")
    st.info("Weitere Einstellungen werden hier angezeigt...")
