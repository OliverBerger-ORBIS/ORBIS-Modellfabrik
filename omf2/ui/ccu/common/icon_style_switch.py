"""Icon Style Switch für Shopfloor Layout

Ermöglicht einfaches Umschalten zwischen verschiedenen Icon-Styles:
- ic_ft: Fischertechnik-Icons (24x24, korrekt dargestellt)
- omf: OMF-spezifische Icons (105x104, zentriert dargestellt)
"""

import streamlit as st

from omf2.assets import get_asset_manager
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_grid_only


def show_icon_style_switch():
    """Zeigt Icon-Style Switch und Shopfloor Layout"""

    st.markdown("### 🎨 Icon Style Switch")

    # Icon-Style Auswahl
    icon_style = st.selectbox(
        "Icon-Style auswählen:",
        ["ic_ft", "omf"],
        index=0,
        help="ic_ft: Fischertechnik-Icons (24x24) | omf: OMF-Icons (105x104)",
    )

    # Asset Manager mit gewähltem Style initialisieren
    asset_manager = get_asset_manager(icon_style=icon_style)

    # Style-Info anzeigen
    if icon_style == "ic_ft":
        st.info("🔧 **Fischertechnik-Icons:** 24x24px, korrekt zentriert und groß dargestellt")
    else:
        st.info("🏭 **OMF-Icons:** 105x104px, in 66px Container zentriert dargestellt")

    # Shopfloor Layout mit gewähltem Style anzeigen
    show_shopfloor_grid_only(active_module_id="MILL")

    # Debug-Info
    with st.expander("🔍 Debug Info"):
        st.write(f"**Aktueller Icon-Style:** {asset_manager.icon_style}")
        st.write(f"**Geladene Module:** {len(asset_manager.module_icons)}")

        # Verfügbare Icons anzeigen
        st.write("**Verfügbare Icons:**")
        for module, icon_path in asset_manager.module_icons.items():
            if icon_path:
                st.write(f"- {module}: {icon_path.split('/')[-1]}")
            else:
                st.write(f"- {module}: None")


if __name__ == "__main__":
    show_icon_style_switch()
