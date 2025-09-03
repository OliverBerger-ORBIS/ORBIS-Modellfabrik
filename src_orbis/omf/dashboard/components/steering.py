"""
Steering Component für OMF Dashboard
Hauptkomponente für alle Steuerungsfunktionen mit Untertabs
"""

import streamlit as st

# Import der Unterkomponenten
from .factory_steering import show_factory_steering
from .generic_steering import show_generic_steering


def show_steering():
    """Hauptfunktion für die Steuerung mit Untertabs"""
    st.header("🎮 Steuerung")
    st.markdown("Alle Steuerungsfunktionen der ORBIS Modellfabrik")
    
    # Untertabs für verschiedene Steuerungsarten
    steering_tab1, steering_tab2 = st.tabs([
        "🏭 Kommando-Zentrale", 
        "🔧 Generische Steuerung"
    ])
    
    # Tab 1: Kommando-Zentrale (Factory Steering)
    with steering_tab1:
        show_factory_steering()
    
    # Tab 2: Generische Steuerung (Generic Steering)
    with steering_tab2:
        show_generic_steering()
