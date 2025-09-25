"""
OMF Dashboard Steering2 - Wrapper für alle Steering-Komponenten
Hauptkomponente für alle Steuerungsfunktionen mit Untertabs
"""

import streamlit as st

from omf.dashboard.tools.logging_config import get_logger

# Import der Unterkomponenten
from omf.dashboard.components.admin.steering_factory import show_factory_steering
from omf.dashboard.components.admin.steering_generic import show_generic_steering
from omf.dashboard.components.admin.steering_sequence import show_sequence_steering

# Logger für Steering
logger = get_logger("omf.dashboard.components.admin.steering")


def show_steering():
    """Hauptfunktion für die Steuerung mit Untertabs"""
    logger.info("🎮 Steering geladen")
    st.header("🎮 Steuerung")
    st.markdown("Alle Steuerungsfunktionen der ORBIS Modellfabrik")

    # Untertabs für verschiedene Steuerungsarten
    steering_tab1, steering_tab2, steering_tab3 = st.tabs(
        ["🏭 Factory-Steuerung", "🔧 Generische Steuerung", "🎯 Sequenz-Steuerung"]
    )

    # Tab 1: Factory-Steuerung (Kommando-Zentrale)
    with steering_tab1:
        show_factory_steering()

    # Tab 2: Generische Steuerung
    with steering_tab2:
        show_generic_steering()

    # Tab 3: Sequenz-Steuerung
    with steering_tab3:
        show_sequence_steering()
