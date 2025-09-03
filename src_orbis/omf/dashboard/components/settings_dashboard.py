"""
OMF Dashboard Settings - Dashboard Einstellungen
Exakte Kopie der show_dashboard_settings Funktion aus settings.py
"""

import streamlit as st


def show_dashboard_settings():
    """Zeigt Dashboard-Einstellungen"""
    st.subheader("⚙️ Dashboard-Einstellungen")

    # MQTT-Verbindungsmodus wird jetzt über Sidebar verwaltet
    st.info("💡 **MQTT-Verbindungsmodus wird über die Sidebar konfiguriert**")

    # Weitere Dashboard-Einstellungen können hier hinzugefügt werden
    st.markdown("#### 📊 Dashboard-Konfiguration")
    st.info("Weitere Einstellungen werden hier angezeigt...")
