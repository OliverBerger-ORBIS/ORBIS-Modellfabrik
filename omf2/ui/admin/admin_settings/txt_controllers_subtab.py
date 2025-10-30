#!/usr/bin/env python3
"""
TXT Controllers Subtab - TXT Controllers Verwaltung für Admin Settings
Zeigt alle TXT Controllers aus der Registry an
"""

import html

import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_txt_controllers_subtab():
    """Render TXT Controllers Subtab mit Registry-Daten"""
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # SVG-Header mit Fallback - einfache Lösung mit größerer SVG
        txt_svg = get_svg_inline("TXT_CONTROLLERS", size_px=32)
        header_icon = txt_svg if txt_svg else UISymbols.get_functional_icon("txt_controllers")
        st.markdown(
            f'<h3 style="margin-top: 0; margin-bottom: 1rem;">{header_icon} <strong>{i18n.t("admin.txt_controllers")} Konfiguration</strong></h3>',
            unsafe_allow_html=True,
        )
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

        _render_txt_controllers_table_with_svg_icons(all_txt_controllers, i18n)

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


def _render_txt_controllers_table_with_svg_icons(all_txt_controllers: dict, i18n):
    """Render TXT controllers; if a controller is assigned to a module, show the module SVG next to the module name."""
    from omf2.ccu.module_manager import get_ccu_module_manager
    from omf2.registry.manager.registry_manager import get_registry_manager

    module_manager = get_ccu_module_manager()
    registry_manager = get_registry_manager("omf2/registry/")
    modules = registry_manager.get_modules()

    # Build name->id map to resolve assignments by module name
    module_name_to_id = {info.get("name", mid): mid for mid, info in modules.items()}

    table_html = '<table style="width: 100%; border-collapse: collapse;">'
    headers = [
        "ID",
        "Name",
        "IP Address",
        "Zugeordnet zu Serial",
        "Modul",
        "MQTT Client",
        "Description",
    ]
    table_html += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
    for header in headers:
        table_html += f'<th style="padding: 8px; text-align: left; font-weight: bold;">{html.escape(header)}</th>'
    table_html += "</tr></thead><tbody>"

    for controller_id, controller_info in all_txt_controllers.items():
        name = controller_info.get("name", "Unknown")
        ip_addr = controller_info.get("ip_address", "N/A")
        assigned_serial = controller_info.get("zugeordnet_zu_modul_serial") or controller_info.get(
            "zugeordnet_zu_modul"
        )
        # Lookup module name via serial
        assigned_name = "N/A"
        if assigned_serial and assigned_serial in modules:
            assigned_name = modules[assigned_serial].get("name", assigned_serial)
        mqtt_client = controller_info.get("mqtt_client", "N/A")
        desc = controller_info.get("description", "No description")

        # Try to render module SVG if assignment matches a module name or serial
        assigned_cell = html.escape(assigned_name if assigned_name != "N/A" else "N/A")
        candidate_id = assigned_serial or (module_name_to_id.get(assigned_name) if assigned_name != "N/A" else None)
        if candidate_id and candidate_id in modules:
            try:
                icon_html = module_manager.get_module_icon_html(candidate_id, size_px=20)
                assigned_cell = (
                    f'<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">'
                    f"{icon_html}<span>{html.escape(assigned_name)}</span></span>"
                )
            except Exception:
                assigned_cell = html.escape(assigned_name if assigned_name != "N/A" else "N/A")

        table_html += '<tr style="border-bottom: 1px solid #ddd;">'
        table_html += (
            f'<td style="padding: 8px; font-family: monospace; white-space: nowrap;">{html.escape(controller_id)}</td>'
        )
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(name)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(ip_addr)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(assigned_serial or "N/A")}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{assigned_cell}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(mqtt_client)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(desc)}</td>'
        table_html += "</tr>"

    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)
