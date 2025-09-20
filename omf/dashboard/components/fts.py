"""
FTS (Fahrerloses Transportsystem) Dashboard-Komponente

Diese Komponente zeigt alle FTS-relevanten Informationen in separaten Tabs an:
- fts_order: FTS-Befehle und Navigation
- fts_instantaction: Sofortige FTS-Aktionen
- fts_state: FTS-Status und Position
- fts_connection: FTS-Verbindungsstatus
- fts_factsheet: FTS-Konfiguration
"""

import streamlit as st

from .fts_connection import show_fts_connection
from .fts_factsheet import show_fts_factsheet
from .fts_instantaction import show_fts_instantaction

# Import der FTS-Unterkomponenten
from .fts_order import show_fts_order
from .fts_state import show_fts_state


def show_fts():
    """Zeigt die FTS-Dashboard-Komponente mit Tab-Navigation"""
    st.header("🚛 FTS (Fahrerloses Transportsystem)")

    # Tab-Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📋 Order", "⚡ Instant Action", "📊 State", "🔗 Connection", "📄 Factsheet"]
    )

    with tab1:
        show_fts_order()

    with tab2:
        show_fts_instantaction()

    with tab3:
        show_fts_state()

    with tab4:
        show_fts_connection()

    with tab5:
        show_fts_factsheet()
