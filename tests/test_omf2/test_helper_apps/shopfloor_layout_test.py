"""
Test-App für Shopfloor Layout
============================

Testet die Shopfloor Layout Lösung mit:
- Streamlit-native Komponenten (st.columns)
- OMF2 Asset Manager Integration
- Echten SVG-Icons
- Clickable Module mit Navigation
- Mode-basierte Highlighting-Systeme
"""

import sys
from pathlib import Path

import streamlit as st

# OMF2 Imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Force reload to avoid cache issues
import importlib
import importlib.util

# Lade die Funktion direkt aus der Datei (umgeht Python Cache)
spec = importlib.util.spec_from_file_location("shopfloor_layout", "omf2/ui/ccu/common/shopfloor_layout.py")
shopfloor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shopfloor_module)
show_shopfloor_layout = shopfloor_module.show_shopfloor_layout

# Page configuration
st.set_page_config(page_title="Shopfloor Layout Test", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")


def main():
    st.title("🏭 Shopfloor Layout Test")
    st.markdown("**OMF2 Integration + SVG-Struktur mit Mode-basierten Highlighting-Systemen**")

    # Sidebar Controls
    st.sidebar.header("🎛️ Controls")

    # Active Module Selection
    active_module = st.sidebar.selectbox(
        "Active Module (for highlighting):",
        ["None", "MILL", "DRILL", "AIQS", "HBW", "DPS", "CHRG", "COMPANY", "SOFTWARE"],
        index=0,
    )

    # Active Intersections Selection (für Roads-Hervorhebung)
    st.sidebar.subheader("🛣️ Active Roads")
    active_intersections = st.sidebar.multiselect(
        "Active Intersections (für Roads-Hervorhebung):",
        ["1", "2", "3", "4"],
        default=[],
        help="Wähle Intersections für orange Roads-Hervorhebung",
    )

    # Business-Funktionen (basierend auf echten Manager-Methoden)
    st.sidebar.subheader("🔧 Business-Funktionen")
    st.sidebar.markdown("**Production Orders:**")
    st.sidebar.markdown("- `_get_current_active_module()`")
    st.sidebar.markdown("- `_get_active_intersections()`")
    st.sidebar.markdown("**Storage Orders:**")
    st.sidebar.markdown("- `_get_current_active_module()`")
    st.sidebar.markdown("- `_get_active_intersections()`")

    # Simulation Buttons
    if st.sidebar.button("🚗 FTS Navigation simulieren"):
        st.session_state.simulate_fts = True
        st.sidebar.success("FTS Navigation aktiviert!")

    if st.sidebar.button("🏭 Production Order simulieren"):
        st.session_state.simulate_production = True
        st.sidebar.success("Production Order aktiviert!")

    # Debug Info
    show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

    # Mode Selection
    mode = st.sidebar.selectbox(
        "Verwendungsmodus:",
        ["interactive", "view_mode", "ccu_configuration"],
        index=0,
        help="Wähle den Verwendungsmodus für das Shopfloor Layout",
    )

    # Main Content
    col1, col2 = st.columns([2, 1])

    with col1:
        #  Shopfloor Layout mit Mode
        show_shopfloor_layout(
            active_module_id=active_module if active_module != "None" else None,
            active_intersections=active_intersections if active_intersections else None,
            title=f"Shopfloor Grid ({mode})",
            unique_key="test_shopfloor_main",
            mode=mode,
        )

    with col2:
        st.subheader("📊 Event Information")

        # Selected Module Info
        if hasattr(st.session_state, "selected_module"):
            st.success(f"**Selected Module:** {st.session_state.selected_module}")
            if hasattr(st.session_state, "selected_module_type"):
                st.info(f"**Type:** {st.session_state.selected_module_type}")

        # Navigation Info (für CCU Configuration Mode)
        if hasattr(st.session_state, "navigate_to_module"):
            st.info(f"🚀 **Navigation:** Würde zu {st.session_state.navigate_to_module} Detail-Seite weiterleiten")
            st.write("**Simulation:** In der echten App würde hier die Modul-Konfiguration geöffnet werden")
            if st.button("🔙 Zurück zur Übersicht"):
                del st.session_state.navigate_to_module
                st.rerun()

        # Detail View Info
        if hasattr(st.session_state, "show_module_detail"):
            st.warning("**Detail View Active**")
            if hasattr(st.session_state, "detail_module_id"):
                st.write(f"**Module:** {st.session_state.detail_module_id}")
            if hasattr(st.session_state, "detail_module_type"):
                st.write(f"**Type:** {st.session_state.detail_module_type}")

        # Mode-spezifische Informationen
        st.subheader("🎯 Verwendungsmodus")
    if mode == "view_mode":
        st.info("📊 **View Mode:** Nur aktive Module werden angezeigt (orange Umrandung). Keine Klicks möglich.")
    elif mode == "ccu_configuration":
        st.info(
            "⚙️ **CCU Configuration Mode:** Single Click = Auswahl (orange), Double Click = Navigation zur Modul-Konfiguration (blau)"
        )
    else:
        st.info("🖱️ **Interactive Mode:** Standard-Interaktivität mit allen Klick-Funktionen")

        # Business-Funktionen Status
        st.subheader("🔧 Business-Funktionen Status")
        if hasattr(st.session_state, "simulate_fts") and st.session_state.simulate_fts:
            st.success("🚗 FTS Navigation aktiv - Roads werden orange hervorgehoben")
        if hasattr(st.session_state, "simulate_production") and st.session_state.simulate_production:
            st.success("🏭 Production Order aktiv - Module werden hervorgehoben")

        # Active Module Info
        if active_module and active_module != "None":
            st.success(f"🏭 Aktives Modul: {active_module} - Modul wird orange umrandet")
        else:
            st.info("🏭 Kein aktives Modul - Module sind weiß")

        # Active Intersections Info
        if active_intersections:
            st.info(f"🛣️ Aktive Intersections: {', '.join(active_intersections)} - Roads werden orange hervorgehoben")
        else:
            st.info("🛣️ Keine aktiven Intersections - Roads sind schwarz")

        # Debug Information
        if show_debug:
            st.subheader("🐛 Debug Info")
            st.json(
                {
                    "session_state": dict(st.session_state),
                    "active_module": active_module,
                    "active_intersections": active_intersections,
                }
            )

            # Roads Debug Info
            st.subheader("🛣️ Roads Debug")
            st.info(f"Active Intersections: {active_intersections}")
            st.info("Roads sollten verlängert sein wenn Intersections ausgewählt sind")

        # Instructions
        st.subheader("📋 Instructions")
        st.markdown(
            """
        **Interaktion:**
        - **Single-Click:** Modul auswählen
        - **Double-Click:** Detail-Seite öffnen

        **Spezielle Zellen:**
        - **(0,0):** ORBIS-Logo + DSP-Info + Status
        - **(0,3):** ORBIS-Logo + Warehouse + Delivery

        **Navigation:**
        - Module leiten zu entsprechenden Detail-Seiten weiter
        - Event-Handling über Streamlit-native Buttons
        """
        )

    # Event History
    if hasattr(st.session_state, "event_history"):
        st.subheader("📜 Event History")
        for event in st.session_state.event_history[-5:]:  # Last 5 events
            st.text(f"{event['timestamp']}: {event['type']} - {event['id']}")

    # Reset Button
    if st.sidebar.button("🔄 Reset State"):
        # Clear session state
        keys_to_clear = [
            "selected_module",
            "selected_module_type",
            "show_module_detail",
            "detail_module_id",
            "detail_module_type",
            "current_page",
            "navigation_source",
            "event_history",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


if __name__ == "__main__":
    main()
