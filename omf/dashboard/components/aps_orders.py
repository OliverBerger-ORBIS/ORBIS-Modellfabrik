"""
APS Orders Dashboard - Wrapper für alle APS-Order-Funktionen
Hauptkomponente für alle APS-Order-Funktionen mit Untertabs
"""

import streamlit as st

from .aps_orders_vda5050 import show_aps_orders_vda5050
from .aps_orders_instant_actions import show_aps_orders_instant_actions
from .aps_orders_history import show_aps_orders_history
from .aps_orders_tools import show_aps_orders_tools


def show_aps_orders():
    """Hauptfunktion für die APS Orders mit Untertabs"""
    st.header("📋 APS Orders")
    st.markdown("VDA5050 Orders und Instant Actions für die APS")

    # Untertabs für verschiedene APS-Order-Bereiche
    aps_orders_tab1, aps_orders_tab2, aps_orders_tab3, aps_orders_tab4 = st.tabs(
        ["📋 VDA5050 Orders", "⚡ Instant Actions", "📊 Order History", "🔧 Order Tools"]
    )

    # Tab 1: VDA5050 Orders
    with aps_orders_tab1:
        show_aps_orders_vda5050()

    # Tab 2: Instant Actions
    with aps_orders_tab2:
        show_aps_orders_instant_actions()

    # Tab 3: Order History
    with aps_orders_tab3:
        show_aps_orders_history()

    # Tab 4: Order Tools
    with aps_orders_tab4:
        show_aps_orders_tools()
