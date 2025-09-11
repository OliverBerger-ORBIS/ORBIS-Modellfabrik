"""
Sequenz-Steuerung Component für OMF Dashboard
UI für die Workflow-Sequenz-Steuerung mit Status-Anzeige
"""

import os

# Import der Sequenz-Tools
import streamlit as st

tools_path = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
# sys.path.append(tools_path)  # Nicht mehr nötig nach pip install -e .

try:
    from src_orbis.omf.tools.sequence_executor import SequenceExecutor
    from src_orbis.omf.tools.sequence_ui import SequenceUI

    SEQUENCE_TOOLS_AVAILABLE = True
except ImportError as e:
    SEQUENCE_TOOLS_AVAILABLE = False
    print(f"❌ Sequenz-Tools nicht verfügbar: {e}")


def show_sequence_steering():
    """Hauptfunktion für die Sequenz-Steuerung"""
    st.subheader("🎯 Sequenz-Steuerung")
    st.markdown("**Automatisierte Workflow-Sequenzen für Module:**")

    # Prüfe ob Sequenz-Tools verfügbar sind
    if not SEQUENCE_TOOLS_AVAILABLE:
        st.warning("⚠️ Sequenz-Steuerung temporär nicht verfügbar")
        st.info("💡 Verwenden Sie die Factory-Steuerung für manuelle Modul-Sequenzen")
        st.error("❌ Sequenz-Tools nicht verfügbar")
        st.info(f"ℹ️ Tools-Pfad: {tools_path}")
        st.info("ℹ️ Bitte überprüfen Sie, ob die Sequenz-Tools korrekt installiert sind")
        return

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
        st.info("ℹ️ Bitte überprüfen Sie die Konfiguration und MQTT-Verbindung")
