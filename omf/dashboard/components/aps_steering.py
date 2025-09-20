"""
APS Steering Dashboard - Wrapper für alle APS-Steering-Funktionen
Hauptkomponente für alle APS-Steering-Funktionen mit Untertabs
"""

import streamlit as st

from .aps_steering_factory import show_aps_steering_factory
from .aps_steering_orders import show_aps_steering_orders
from .aps_steering_modules import show_aps_steering_modules
from .aps_steering_fts import show_aps_steering_fts


def show_aps_steering():
    """Hauptfunktion für die APS Steering mit Untertabs"""
    st.header("🎮 APS Steering")
    st.markdown("Steuerung und Kontrolle der APS")

    # Untertabs für verschiedene APS-Steering-Bereiche
    aps_steering_tab1, aps_steering_tab2, aps_steering_tab3, aps_steering_tab4 = st.tabs(
        ["🏭 Factory Steering", "📋 Order Steering", "🔧 Module Steering", "🚗 FTS Steering"]
    )

    # Tab 1: Factory Steering
    with aps_steering_tab1:
        show_aps_steering_factory()

    # Tab 2: Order Steering
    with aps_steering_tab2:
        show_aps_steering_orders()

    # Tab 3: Module Steering
    with aps_steering_tab3:
        show_aps_steering_modules()

    # Tab 4: FTS Steering
    with aps_steering_tab4:
        show_aps_steering_fts()
