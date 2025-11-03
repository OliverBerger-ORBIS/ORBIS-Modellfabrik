#!/usr/bin/env python3
"""
Module Subtab - Module Verwaltung für Admin Settings
Zeigt alle Modules aus der Registry an
"""

import html

import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
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
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # SVG-Header mit Fallback - einfache Lösung mit größerer SVG
        modules_svg = get_asset_manager().get_asset_inline("MODULES_ADMIN", size_px=32)
        header_icon = modules_svg if modules_svg else UISymbols.get_functional_icon("module_control")
        st.markdown(
            f'<h3 style="margin-top: 0; margin-bottom: 1rem;">{header_icon} <strong>{i18n.t("admin.modules")} Configuration</strong></h3>',
            unsafe_allow_html=True,
        )
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
            _render_registry_modules_table_with_svg_icons(all_modules, i18n)

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


def _render_registry_modules_table_with_svg_icons(all_modules: dict, i18n):
    """Render registry modules as HTML table with SVG icons and single-line rows.

    Columns displayed (preserve all original info):
    - ID | Name | Type | Enabled | Icon | Name EN | Name DE
    """
    from omf2.ccu.module_manager import get_ccu_module_manager

    module_manager = get_ccu_module_manager()

    table_html = '<table style="width: 100%; border-collapse: collapse;">'

    headers = [
        "ID",
        "Name",
        "Type",
        "Enabled",
        "Icon",
        "Name EN",
        "Name DE",
    ]
    table_html += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
    for header in headers:
        table_html += f'<th style="padding: 8px; text-align: left; font-weight: bold;">{html.escape(header)}</th>'
    table_html += "</tr></thead>"

    table_html += "<tbody>"
    for module_id, module_info in all_modules.items():
        name = module_info.get("name", module_id)
        enabled = module_info.get("enabled", True)
        enabled_display = "✅" if enabled else "❌"
        module_type = module_info.get("type", "Unknown")
        emoji_icon = module_info.get("icon", "")
        name_en = module_info.get("name_lang_en", "")
        name_de = module_info.get("name_lang_de", "")

        # SVG icon + name single-line
        try:
            icon_html = module_manager.get_module_icon_html(module_id, size_px=20)
            name_text = html.escape(name)
            name_cell = (
                f'<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">'
                f"{icon_html}<span>{name_text}</span></span>"
            )
        except Exception:
            name_cell = html.escape(f"{name} ({module_id})")

        table_html += '<tr style="border-bottom: 1px solid #ddd;">'
        table_html += f'<td style="padding: 8px; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(module_id)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name_cell}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(module_type)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{enabled_display}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(emoji_icon)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(name_en)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(name_de)}</td>'
        table_html += "</tr>"

    table_html += "</tbody></table>"

    st.markdown(table_html, unsafe_allow_html=True)
