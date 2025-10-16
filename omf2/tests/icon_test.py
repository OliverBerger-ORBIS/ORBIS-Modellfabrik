#!/usr/bin/env python3
"""
Icon Test - Separater Test für Icon-Styles
Unabhängig von der Hauptanwendung
"""

import streamlit as st

from omf2.assets import get_asset_manager
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_grid_only


def main():
    st.title("🎨 Icon Style Test")

    # Icon-Style Auswahl
    icon_style = st.selectbox(
        "Icon-Style auswählen:", ["ic_ft", "omf"], index=0, help="ic_ft: Fischertechnik-Icons | omf: OMF-Icons"
    )

    st.write(f"**Aktueller Style:** {icon_style}")

    # Asset Manager mit gewähltem Style initialisieren
    asset_manager = get_asset_manager(icon_style=icon_style)

    # Shopfloor Layout mit gewähltem Style anzeigen
    show_shopfloor_grid_only(active_module_id="MILL", title="Icon Test")

    # Debug-Info
    with st.expander("🔍 Debug Info"):
        st.write(f"**Icon-Style:** {icon_style}")
        st.write(f"**Asset Manager Style:** {asset_manager.icon_style}")

        # Verfügbare Icons anzeigen
        st.write("**Verfügbare Module-Icons:**")
        for module in ["HBW", "DPS", "MILL", "DRILL", "AIQS", "CHRG", "FTS"]:
            icon_path = asset_manager.module_icons.get(module)
            if icon_path:
                filename = icon_path.split("/")[-1]
                st.write(f"- {module}: {filename}")
            else:
                st.write(f"- {module}: ❌ Nicht gefunden")


if __name__ == "__main__":
    main()
