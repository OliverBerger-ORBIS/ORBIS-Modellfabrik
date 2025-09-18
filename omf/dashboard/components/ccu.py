"""
CCU (Central Control Unit) Dashboard-Komponente

Diese Komponente zeigt alle CCU-relevanten Informationen in separaten Tabs an:
- ccu_state: CCU-Status und Workflow
- ccu_control: CCU-Steuerungsbefehle
- ccu_set: CCU-Konfiguration und Reset
- ccu_status: CCU-Verbindungs- und Gesundheitsstatus
- ccu_pairing: Modul-Pairing-Status
"""

import streamlit as st

from .ccu_control import show_ccu_control
from .ccu_pairing import show_ccu_pairing
from .ccu_set import show_ccu_set

# Import der CCU-Unterkomponenten
from .ccu_state import show_ccu_state
from .ccu_status import show_ccu_status

def show_ccu():
    """Zeigt die CCU-Dashboard-Komponente mit Tab-Navigation"""
    st.header("🏢 CCU (Central Control Unit)")

    # Tab-Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 State", "🎮 Control", "⚙️ Set", "🔗 Status", "🔗 Pairing"])

    with tab1:
        show_ccu_state()

    with tab2:
        show_ccu_control()

    with tab3:
        show_ccu_set()

    with tab4:
        show_ccu_status()

    with tab5:
        show_ccu_pairing()
