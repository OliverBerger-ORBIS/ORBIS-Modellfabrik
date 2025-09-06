"""
Sequenz-Steuerung Component für OMF Dashboard
UI für die Workflow-Sequenz-Steuerung mit Status-Anzeige
"""

import os

# Import der Sequenz-Tools
import sys

import streamlit as st

tools_path = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
sys.path.append(tools_path)

try:
    from sequence_executor import SequenceExecutor
    from sequence_ui import SequenceUI
except ImportError as e:
    st.error(f"❌ Fehler beim Import der Sequenz-Tools: {e}")
    st.info(f"ℹ️ Tools-Pfad: {tools_path}")
    st.info("ℹ️ Bitte überprüfen Sie, ob die Sequenz-Tools korrekt installiert sind")


def show_sequence_steering():
    """Hauptfunktion für die Sequenz-Steuerung"""
    st.subheader("🎯 Sequenz-Steuerung")
    st.markdown("**Automatisierte Workflow-Sequenzen für Module:**")

    try:
        # MQTT-Client aus Session State holen
        mqtt_client = st.session_state.get("mqtt_client")
        if not mqtt_client or not mqtt_client.connected:
            st.error("❌ MQTT-Client nicht verfügbar oder nicht verbunden")
            st.info("ℹ️ Bitte verbinden Sie sich zuerst mit MQTT in den Einstellungen")
            return

        # Sequenz-Executor initialisieren falls nötig
        if "sequence_executor" not in st.session_state:
            st.session_state.sequence_executor = SequenceExecutor(mqtt_client)

        # SequenceUI initialisieren
        sequence_ui = SequenceUI(st.session_state.sequence_executor)

        # MQTT-Client an SequenceUI weitergeben
        sequence_ui.mqtt_client = mqtt_client

        # UI anzeigen
        sequence_ui.show_sequence_selector()
        sequence_ui.show_sequence_status()
        sequence_ui.show_active_sequences()

    except Exception as e:
        st.error(f"❌ Fehler in der Sequenz-Steuerung: {e}")
        st.exception(e)
