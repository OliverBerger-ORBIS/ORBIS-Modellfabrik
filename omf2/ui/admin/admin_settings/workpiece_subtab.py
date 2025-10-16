#!/usr/bin/env python3
"""
Admin Settings - Workpiece Subtab
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_workpiece_subtab():
    """Render Workpiece Configuration Subtab"""
    # Only log on first render
    if "workpiece_subtab_logged" not in st.session_state:
        logger.info(
            f"{UISymbols.get_functional_icon('module_control')} Rendering Workpiece Configuration Subtab (init only)"
        )
        st.session_state["workpiece_subtab_logged"] = True

    try:
        st.subheader(f"{UISymbols.get_functional_icon('module_control')} Werkstück-Konfiguration")
        st.markdown("Registry-basierte Werkstück-Verwaltung aus omf2/registry")

        # Load workpiece data using WorkpieceManager (as per architecture)
        from omf2.common.workpiece_manager import get_workpiece_manager

        try:
            # Get workpiece manager
            manager = get_workpiece_manager()

            # BLAUE Werkstücke (zuerst)
            blue_workpieces = manager.get_workpieces_by_color_with_nfc("BLUE")
            if blue_workpieces:
                with st.expander(
                    f"{UISymbols.get_workpiece_icon('blue')} Blaue Werkstücke ({len(blue_workpieces)})", expanded=False
                ):
                    blue_data = []
                    for workpiece_id, wp_data in blue_workpieces.items():
                        nfc_code = wp_data.get("nfc_code", "Unknown")
                        quality_check = wp_data.get("quality_check", "Unknown")
                        description = wp_data.get("description", "No description")

                        blue_data.append(
                            {
                                "Werkstück": f"{UISymbols.get_workpiece_icon('blue')} {workpiece_id}",
                                "NFC Code": nfc_code[:12] + "...",
                                "Qualität": quality_check,
                                "Beschreibung": description,
                                "Status": (
                                    UISymbols.get_status_icon("success")
                                    if wp_data.get("enabled", True)
                                    else UISymbols.get_status_icon("error")
                                ),
                            }
                        )

                    if blue_data:
                        st.dataframe(
                            blue_data,
                            column_config={
                                "Werkstück": st.column_config.TextColumn("Werkstück", width="medium"),
                                "NFC Code": st.column_config.TextColumn("NFC Code", width="medium"),
                                "Qualität": st.column_config.TextColumn("Qualität", width="small"),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="medium"),
                                "Status": st.column_config.TextColumn("Status", width="small"),
                            },
                            hide_index=True,
                        )

            # WEISSE Werkstücke
            white_workpieces = manager.get_workpieces_by_color_with_nfc("WHITE")
            if white_workpieces:
                with st.expander(
                    f"{UISymbols.get_workpiece_icon('white')} Weiße Werkstücke ({len(white_workpieces)})",
                    expanded=False,
                ):
                    white_data = []
                    for workpiece_id, wp_data in white_workpieces.items():
                        nfc_code = wp_data.get("nfc_code", "Unknown")
                        quality_check = wp_data.get("quality_check", "Unknown")
                        description = wp_data.get("description", "No description")

                        white_data.append(
                            {
                                "Werkstück": f"{UISymbols.get_workpiece_icon('white')} {workpiece_id}",
                                "NFC Code": nfc_code[:12] + "...",
                                "Qualität": quality_check,
                                "Beschreibung": description,
                                "Status": (
                                    UISymbols.get_status_icon("success")
                                    if wp_data.get("enabled", True)
                                    else UISymbols.get_status_icon("error")
                                ),
                            }
                        )

                    if white_data:
                        st.dataframe(
                            white_data,
                            column_config={
                                "Werkstück": st.column_config.TextColumn("Werkstück", width="medium"),
                                "NFC Code": st.column_config.TextColumn("NFC Code", width="medium"),
                                "Qualität": st.column_config.TextColumn("Qualität", width="small"),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="medium"),
                                "Status": st.column_config.TextColumn("Status", width="small"),
                            },
                            hide_index=True,
                        )

            # ROTE Werkstücke (dritte - korrekte Reihenfolge)
            red_workpieces = manager.get_workpieces_by_color_with_nfc("RED")
            if red_workpieces:
                with st.expander(
                    f"{UISymbols.get_workpiece_icon('red')} Rote Werkstücke ({len(red_workpieces)})", expanded=False
                ):
                    red_data = []
                    for workpiece_id, wp_data in red_workpieces.items():
                        nfc_code = wp_data.get("nfc_code", "Unknown")
                        quality_check = wp_data.get("quality_check", "Unknown")
                        description = wp_data.get("description", "No description")

                        red_data.append(
                            {
                                "Werkstück": f"{UISymbols.get_workpiece_icon('red')} {workpiece_id}",
                                "NFC Code": nfc_code[:12] + "...",
                                "Qualität": quality_check,
                                "Beschreibung": description,
                                "Status": (
                                    UISymbols.get_status_icon("success")
                                    if wp_data.get("enabled", True)
                                    else UISymbols.get_status_icon("error")
                                ),
                            }
                        )

                    if red_data:
                        st.dataframe(
                            red_data,
                            column_config={
                                "Werkstück": st.column_config.TextColumn("Werkstück", width="medium"),
                                "NFC Code": st.column_config.TextColumn("NFC Code", width="medium"),
                                "Qualität": st.column_config.TextColumn("Qualität", width="small"),
                                "Beschreibung": st.column_config.TextColumn("Beschreibung", width="medium"),
                                "Status": st.column_config.TextColumn("Status", width="small"),
                            },
                            hide_index=True,
                        )

            # Registry Info
            with st.expander("📊 Registry Information", expanded=False):
                all_workpieces = manager.get_all_workpieces()
                st.write(f"**Total Workpieces:** {len(all_workpieces)}")
                st.write(f"**Red Workpieces:** {len(red_workpieces)}")
                st.write(f"**Blue Workpieces:** {len(blue_workpieces)}")
                st.write(f"**White Workpieces:** {len(white_workpieces)}")

                # Show available colors
                colors = manager.get_workpiece_colors()
                if colors:
                    st.write("**Available Colors:**")
                    for color in colors:
                        st.write(f"- {color}")

        except FileNotFoundError:
            st.error(
                f"{UISymbols.get_status_icon('error')} Registry file not found. Please check omf2/registry/workpieces.yml"
            )
            st.info("💡 Make sure the registry file exists and is accessible.")
        except Exception as e:
            st.error(f"{UISymbols.get_status_icon('error')} Error loading registry: {e}")
            st.info("💡 Check the registry file format and permissions.")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Workpiece Subtab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Workpiece Subtab failed: {e}")
        st.info("💡 This component is currently under development.")
