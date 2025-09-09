"""
OMF Dashboard Shopfloor - Shopfloor-Management
Hauptkomponente für Shopfloor-Layout, Routenplanung und Modul-Positionierung
"""

import streamlit as st

from .shopfloor_utils import (
    get_shopfloor_statistics,
)


def show_shopfloor():
    """Hauptfunktion für Shopfloor-Management mit Untertabs"""
    st.header("🏗️ Shopfloor")
    st.markdown("Shopfloor-Layout, Routenplanung und Modul-Positionierung")

    # Lazy imports der Unterkomponenten (verhindert Circular Imports)
    from .shopfloor_layout import show_shopfloor_layout
    from .shopfloor_positioning import show_shopfloor_positioning
    from .shopfloor_routes import show_shopfloor_routes

    # Untertabs für verschiedene Shopfloor-Bereiche
    shopfloor_tab1, shopfloor_tab2, shopfloor_tab3 = st.tabs(
        ["🗺️ Shopfloor-Layout", "🛣️ Routenplanung", "📍 Modul-Positionierung"]
    )

    # Tab 1: Shopfloor-Layout (4x3 Grid)
    with shopfloor_tab1:
        show_shopfloor_layout()

    # Tab 2: FTS-Routenplanung
    with shopfloor_tab2:
        show_shopfloor_routes()

    # Tab 3: Modul-Positionierung
    with shopfloor_tab3:
        show_shopfloor_positioning()

    # Shopfloor-Statistiken am Ende
    st.markdown("---")
    st.markdown("### 📊 Shopfloor-Statistiken")

    try:
        stats = get_shopfloor_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Module gesamt", value=stats["modules"]["total"], delta=f"{stats['modules']['enabled']} aktiv"
            )

        with col2:
            st.metric(label="Intersections", value=stats["intersections"])

        with col3:
            st.metric(label="FTS-Routen", value=stats["routes"]["fts"])

        with col4:
            st.metric(label="Produkt-Routen", value=stats["routes"]["products"])

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Statistiken: {e}")
