"""
APS Overview Dashboard - Wrapper für alle APS-Übersichtsfunktionen
Hauptkomponente für alle APS-Übersichtsfunktionen mit Untertabs
"""

import streamlit as st

from .aps_overview_system_status import show_aps_system_status
from .aps_overview_controllers import show_aps_controllers
from .aps_overview_orders import show_aps_orders
from .aps_overview_commands import show_aps_commands

def show_aps_overview():
    """Hauptfunktion für die APS-Übersicht mit Untertabs"""
    st.header("🏭 APS Overview")
    st.markdown("Automatisierte Produktionssysteme - Übersicht")
    
    # Untertabs für verschiedene APS-Übersichtsbereiche
    aps_tab1, aps_tab2, aps_tab3, aps_tab4 = st.tabs(
        ["📊 System Status", "🎮 Controllers", "📋 Orders", "⚡ Commands"]
    )
    
    # Tab 1: System Status
    with aps_tab1:
        show_aps_system_status()
    
    # Tab 2: Controllers
    with aps_tab2:
        show_aps_controllers()
    
    # Tab 3: Orders
    with aps_tab3:
        show_aps_orders()
    
    # Tab 4: Commands
    with aps_tab4:
        show_aps_commands()