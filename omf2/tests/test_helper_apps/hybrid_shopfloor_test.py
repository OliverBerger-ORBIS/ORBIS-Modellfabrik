"""
Test-App für Hybrid Shopfloor Layout
====================================

Testet die neue Hybrid-Lösung mit:
- Copilot's robuster SVG-Struktur
- OMF2 Asset Manager Integration
- Echten SVG-Icons
- Clickable Module mit Navigation
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
spec = importlib.util.spec_from_file_location(
    "shopfloor_layout_hybrid", "omf2/ui/ccu/common/shopfloor_layout_hybrid.py"
)
shopfloor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shopfloor_module)
show_shopfloor_layout_hybrid = shopfloor_module.show_shopfloor_layout_hybrid

# Page configuration
st.set_page_config(
    page_title="Hybrid Shopfloor Layout Test", page_icon="🏭", layout="wide", initial_sidebar_state="expanded"
)


def main():
    st.title("🏭 Hybrid Shopfloor Layout Test")
    st.markdown("**OMF2 Integration + Copilot's SVG-Struktur**")

    # Sidebar Controls
    st.sidebar.header("🎛️ Controls")

    # Active Module Selection
    active_module = st.sidebar.selectbox(
        "Active Module (for highlighting):",
        ["None", "MILL", "DRILL", "AIQS", "HBW", "DPS", "CHRG", "EMPTY1-main", "EMPTY2-main"],
        index=0,
    )

    # Debug Info
    show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

    # Main Content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Hybrid Shopfloor Layout
        show_shopfloor_layout_hybrid(
            active_module_id=active_module if active_module != "None" else None,
            active_intersections=None,
            title="Interactive Shopfloor Grid",
            unique_key="test_hybrid_shopfloor_main",
        )

    with col2:
        st.subheader("📊 Event Information")

        # Selected Module Info
        if hasattr(st.session_state, "selected_module"):
            st.success(f"**Selected Module:** {st.session_state.selected_module}")
            if hasattr(st.session_state, "selected_module_type"):
                st.info(f"**Type:** {st.session_state.selected_module_type}")

        # Navigation Info
        if hasattr(st.session_state, "show_module_detail"):
            st.warning("**Detail View Active**")
            if hasattr(st.session_state, "detail_module_id"):
                st.write(f"**Module:** {st.session_state.detail_module_id}")
            if hasattr(st.session_state, "detail_module_type"):
                st.write(f"**Type:** {st.session_state.detail_module_type}")

        # Debug Information
        if show_debug:
            st.subheader("🐛 Debug Info")
            st.json({"session_state": dict(st.session_state), "active_module": active_module})

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
        - Event-Handling über streamlit-bokeh-events
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
