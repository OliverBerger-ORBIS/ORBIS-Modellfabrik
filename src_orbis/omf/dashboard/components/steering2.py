"""
OMF Dashboard Steering2 - Wrapper für alle Steering-Komponenten
Hauptkomponente für alle Steuerungsfunktionen mit Untertabs
"""

import streamlit as st

# Import der Unterkomponenten
from .steering_factory import show_factory_steering
from .steering_generic import show_generic_steering


def show_steering2():
    """Hauptfunktion für die Steuerung mit Untertabs"""
    st.header("🎮 Steuerung")
    st.markdown("Alle Steuerungsfunktionen der ORBIS Modellfabrik")

    # Untertabs für verschiedene Steuerungsarten
    steering_tab1, steering_tab2 = st.tabs([
        "🏭 Factory-Steuerung",
        "🔧 Generische Steuerung"
    ])

    # Tab 1: Factory-Steuerung (Kommando-Zentrale)
    with steering_tab1:
        show_factory_steering()

    # Tab 2: Generische Steuerung
    with steering_tab2:
        show_generic_steering()
