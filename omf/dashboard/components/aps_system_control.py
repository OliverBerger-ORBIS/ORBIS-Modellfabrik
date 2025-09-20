"""
APS System Control Dashboard - Wrapper für alle APS-System-Control-Funktionen
Hauptkomponente für alle APS-System-Control-Funktionen mit Untertabs
"""

import streamlit as st

from .aps_system_control_commands import show_aps_system_control_commands
from .aps_system_control_status import show_aps_system_control_status
from .aps_system_control_monitor import show_aps_system_control_monitor
from .aps_system_control_debug import show_aps_system_control_debug


def show_aps_system_control():
    """Hauptfunktion für die APS System Control mit Untertabs"""
    st.header("🎮 APS System Control")
    st.markdown("System Control und Monitoring für die APS")

    # Untertabs für verschiedene APS-System-Control-Bereiche
    aps_system_tab1, aps_system_tab2, aps_system_tab3, aps_system_tab4 = st.tabs(
        ["⚡ System Commands", "📊 System Status", "📈 System Monitor", "🔧 Debug Tools"]
    )

    # Tab 1: System Commands
    with aps_system_tab1:
        show_aps_system_control_commands()

    # Tab 2: System Status
    with aps_system_tab2:
        show_aps_system_control_status()

    # Tab 3: System Monitor
    with aps_system_tab3:
        show_aps_system_control_monitor()

    # Tab 4: Debug Tools
    with aps_system_tab4:
        show_aps_system_control_debug()
