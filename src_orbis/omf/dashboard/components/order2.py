"""
OMF Dashboard Order2 - Wrapper für alle Order-Komponenten
Hauptkomponente für alle Auftragsfunktionen mit Untertabs
"""

import streamlit as st

# Import der Unterkomponenten
from .order_management import show_order_management
from .order_current import show_order_current


def show_order2():
    """Hauptfunktion für die Aufträge mit Untertabs"""
    st.header("📋 Aufträge")
    st.markdown("Alle Auftragsfunktionen der ORBIS Modellfabrik")

    # Untertabs für verschiedene Auftragsbereiche
    order_tab1, order_tab2 = st.tabs([
        "📋 Auftragsverwaltung",
        "🔄 Laufende Aufträge"
    ])

    # Tab 1: Auftragsverwaltung
    with order_tab1:
        show_order_management()

    # Tab 2: Laufende Aufträge
    with order_tab2:
        show_order_current()
