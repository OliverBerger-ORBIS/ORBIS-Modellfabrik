#!/usr/bin/env python3
"""
TXT Controllers Subtab - TXT Controllers Verwaltung für Admin Settings
Zeigt alle TXT Controllers aus der Registry an
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_txt_controllers_subtab():
    """Render TXT Controllers Subtab mit Registry-Daten"""
    try:
        st.subheader(f"{UISymbols.get_functional_icon('txt_controllers')} TXT Controllers Konfiguration")
        st.markdown("Registry-basierte TXT Controllers-Verwaltung aus omf2/registry")

        # Load registry manager from session state (initialized in omf.py)
        if "registry_manager" not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager

            st.session_state["registry_manager"] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state["registry_manager"]

        # Get all TXT controllers
        all_txt_controllers = registry_manager.get_txt_controllers()

        if not all_txt_controllers:
            st.warning(f"{UISymbols.get_status_icon('warning')} Keine TXT Controllers in der Registry gefunden")
            return

        # Erstelle DataFrame für alle TXT Controllers
        txt_controller_data = []
        for controller_id, controller_info in all_txt_controllers.items():
            txt_controller_data.append(
                {
                    "ID": controller_id,
                    "Name": controller_info.get("name", "Unknown"),
                    "IP Address": controller_info.get("ip_address", "N/A"),
                    "Zugeordnet zu Modul": controller_info.get("zugeordnet_zu_modul_name", "N/A"),
                    "MQTT Client": controller_info.get("mqtt_client", "N/A"),
                    "Description": controller_info.get("description", "No description"),
                }
            )

        if txt_controller_data:
            st.dataframe(
                txt_controller_data,
                column_config={
                    "ID": st.column_config.TextColumn("Controller ID", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "IP Address": st.column_config.TextColumn("IP Address", width="medium"),
                    "Zugeordnet zu Modul": st.column_config.TextColumn("Zugeordnet zu Modul", width="medium"),
                    "MQTT Client": st.column_config.TextColumn("MQTT Client", width="medium"),
                    "Description": st.column_config.TextColumn("Description", width="large"),
                },
                hide_index=True,
            )

        # Registry Information
        with st.expander(f"{UISymbols.get_functional_icon('dashboard')} Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total TXT Controllers:** {len(all_txt_controllers)}")

            # Zeige TXT Controllers Übersicht
            st.write("**TXT Controllers Overview:**")
            for controller_id, controller_info in all_txt_controllers.items():
                name = controller_info.get("name", "Unknown")
                ip_address = controller_info.get("ip_address", "N/A")
                st.write(f"- {controller_id}: {name} ({ip_address})")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} TXT Controllers Subtab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} TXT Controllers Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def show_txt_controllers_subtab():
    """Wrapper für TXT Controllers Subtab"""
    render_txt_controllers_subtab()
