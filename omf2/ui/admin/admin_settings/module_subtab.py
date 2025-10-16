#!/usr/bin/env python3
"""
Module Subtab - Module Verwaltung für Admin Settings
Zeigt alle Modules aus der Registry an
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_module_subtab():
    """Render Module Subtab mit Registry-Daten"""
    # Only log on first render
    if "module_subtab_logged" not in st.session_state:
        logger.info(
            f"{UISymbols.get_functional_icon('module_control')} Rendering Module Configuration Subtab (init only)"
        )
        st.session_state["module_subtab_logged"] = True

    try:
        st.subheader(f"{UISymbols.get_functional_icon('module_control')} Module Configuration")
        st.markdown("Registry-basierte Module-Verwaltung aus omf2/registry")

        # Load registry manager from session state (initialized in omf.py)
        if "registry_manager" not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager

            st.session_state["registry_manager"] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state["registry_manager"]

        # Get all modules
        all_modules = registry_manager.get_modules()

        if not all_modules:
            st.warning(f"{UISymbols.get_status_icon('warning')} Keine Modules in der Registry gefunden")
            return

        # Erstelle DataFrame für alle Modules
        module_data = []
        for module_id, module_info in all_modules.items():
            module_data.append(
                {
                    "ID": module_id,
                    "Name": module_info.get("name", "Unknown"),
                    "Type": module_info.get("type", "Unknown"),
                    "Enabled": (
                        f"{UISymbols.get_status_icon('success')}"
                        if module_info.get("enabled", True)
                        else f"{UISymbols.get_status_icon('error')}"
                    ),
                    "Icon": module_info.get("icon", "🔧"),
                    "Name EN": module_info.get("name_lang_en", ""),
                    "Name DE": module_info.get("name_lang_de", ""),
                }
            )

        if module_data:
            st.dataframe(
                module_data,
                column_config={
                    "Serial": st.column_config.TextColumn("Serial", width="medium"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Sub Type": st.column_config.TextColumn("Sub Type", width="small"),
                    "Enabled": st.column_config.TextColumn("Enabled", width="small"),
                    "Icon": st.column_config.TextColumn("Icon", width="small"),
                    "Name EN": st.column_config.TextColumn("Name EN", width="medium"),
                    "Name DE": st.column_config.TextColumn("Name DE", width="medium"),
                },
                hide_index=True,
            )

        # Registry Information
        with st.expander(f"{UISymbols.get_functional_icon('dashboard')} Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Modules:** {len(all_modules)}")

            # Zeige Module-Übersicht
            st.write("**Modules Overview:**")
            for module_id, module_info in all_modules.items():
                name = module_info.get("name", "Unknown")
                module_type = module_info.get("type", "Unknown")
                enabled = (
                    f"{UISymbols.get_status_icon('success')}"
                    if module_info.get("enabled", True)
                    else f"{UISymbols.get_status_icon('error')}"
                )
                st.write(f"- {module_id}: {name} ({module_type}) {enabled}")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Module Subtab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Module Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def show_module_subtab():
    """Wrapper für Module Subtab"""
    render_module_subtab()
