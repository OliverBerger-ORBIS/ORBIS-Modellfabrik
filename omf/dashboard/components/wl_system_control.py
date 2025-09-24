"""
WL System Control Dashboard - Wrapper für alle WL-System-Control-Funktionen
Hauptkomponente für alle WL-System-Control-Funktionen mit Untertabs
"""

import streamlit as st

from .wl_system_control_commands import show_wl_system_control_commands
from .wl_system_control_debug import show_wl_system_control_debug
from .wl_system_control_monitor import show_wl_system_control_monitor
from .wl_system_control_status import show_wl_system_control_status


def show_wl_system_control():
    """Hauptfunktion für die WL System Control mit Untertabs"""
    st.header("🎮 WL System Control")
    st.markdown("System Control und Monitoring für die Werksleiter")

    # Untertabs für verschiedene WL-System-Control-Bereiche
    wl_system_tab1, wl_system_tab2, wl_system_tab3, wl_system_tab4 = st.tabs(
        ["⚡ System Commands", "📊 System Status", "📈 System Monitor", "🔧 Debug Tools"]
    )

    # Tab 1: System Commands
    with wl_system_tab1:
        show_wl_system_control_commands()

    # Tab 2: System Status
    with wl_system_tab2:
        show_wl_system_control_status()

    # Tab 3: System Monitor
    with wl_system_tab3:
        show_wl_system_control_monitor()

    # Tab 4: Debug Tools
    with wl_system_tab4:
        show_wl_system_control_debug()
