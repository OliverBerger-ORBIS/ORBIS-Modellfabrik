"""
OMF Dashboard Overview - Wrapper für alle Overview-Komponenten
Hauptkomponente für alle Übersichtsfunktionen mit Untertabs
"""

import streamlit as st

from .overview_customer_order import show_overview_order
from .overview_inventory import show_overview_inventory

# Import der Unterkomponenten
from .overview_module_status import show_overview_module_status
from .overview_product_catalog import show_overview_product_catalog
from .overview_purchase_order import show_overview_order_raw


def show_overview():
    """Hauptfunktion für die Übersicht mit Untertabs"""
    st.header("📊 Übersicht (Overview)")
    st.markdown("Alle Übersichtsfunktionen der ORBIS Modellfabrik")

    # Untertabs für verschiedene Übersichtsbereiche
    overview_tab1, overview_tab2, overview_tab3, overview_tab4, overview_tab5 = st.tabs(
        ["🏭 Modul Status", "📋 Kundenaufträge", "📊 Rohmaterial-Bestellungen", "📦 Lagerbestand", "📦 Produktkatalog"]
    )

    # Tab 1: Modul Status
    with overview_tab1:
        show_overview_module_status()

    # Tab 2: Kundenaufträge (Customer Orders)
    with overview_tab2:
        show_overview_order()

    # Tab 3: Rohmaterial-Bestellungen (Purchase Orders)
    with overview_tab3:
        show_overview_order_raw()

    # Tab 4: Lagerbestand
    with overview_tab4:
        show_overview_inventory()

    # Tab 5: Produktkatalog
    with overview_tab5:
        show_overview_product_catalog()
