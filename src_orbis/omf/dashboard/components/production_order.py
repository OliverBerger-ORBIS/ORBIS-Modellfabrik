"""
OMF Dashboard Production Order - Wrapper für alle Production Order-Komponenten
Hauptkomponente für alle internen Fertigungsaufträge mit Untertabs
"""

import streamlit as st

from .production_order_current import show_production_order_current

# Import der Unterkomponenten
from .production_order_management import show_production_order_management


def show_production_order():
    """Hauptfunktion für die Production Orders (interne Fertigungsaufträge) mit Untertabs"""
    st.header("🏭 Fertigungsaufträge (Production Orders)")
    st.markdown("Interne Fertigungsaufträge der ORBIS Modellfabrik")

    # Untertabs für verschiedene Production Order-Bereiche
    order_tab1, order_tab2 = st.tabs(["📋 Fertigungsauftrags-Verwaltung", "🔄 Laufende Fertigungsaufträge"])

    # Tab 1: Fertigungsauftrags-Verwaltung (Production Order Management)
    with order_tab1:
        show_production_order_management()

    # Tab 2: Laufende Fertigungsaufträge (Production Orders)
    with order_tab2:
        show_production_order_current()
