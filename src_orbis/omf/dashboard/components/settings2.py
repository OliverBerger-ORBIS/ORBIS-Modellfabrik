"""
OMF Dashboard Settings2 - Wrapper für alle Settings-Komponenten
Hauptkomponente für alle Einstellungen mit Untertabs
"""

import streamlit as st

# Import der Unterkomponenten
from .settings_dashboard import show_dashboard_settings
from .settings_modul_config import show_module_config
from .settings_nfc_config import show_nfc_config
from .settings_mqtt_config import show_mqtt_config
from .settings_topic_config import show_topic_config
from .settings_message_templates import show_messages_templates


def show_settings2():
    """Hauptfunktion für die Einstellungen mit Untertabs"""
    st.header("⚙️ Einstellungen")
    st.markdown("Alle Konfigurations- und Einstellungsfunktionen der ORBIS Modellfabrik")

    # Untertabs für verschiedene Einstellungsbereiche
    settings_tab1, settings_tab2, settings_tab3, settings_tab4, settings_tab5, settings_tab6 = st.tabs([
        "⚙️ Dashboard",
        "🏭 Module",
        "📱 NFC",
        "🔗 MQTT",
        "📡 Topics",
        "📋 Templates"
    ])

    # Tab 1: Dashboard Einstellungen
    with settings_tab1:
        show_dashboard_settings()

    # Tab 2: Modul Konfiguration
    with settings_tab2:
        show_module_config()

    # Tab 3: NFC Konfiguration
    with settings_tab3:
        show_nfc_config()

    # Tab 4: MQTT Konfiguration
    with settings_tab4:
        show_mqtt_config()

    # Tab 5: Topic Konfiguration
    with settings_tab5:
        show_topic_config()

    # Tab 6: Message Templates
    with settings_tab6:
        show_messages_templates()
