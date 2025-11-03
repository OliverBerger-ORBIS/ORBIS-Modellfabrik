#!/usr/bin/env python3
"""
Stations Subtab - Stations Verwaltung für Admin Settings
Zeigt alle Stations aus der Registry nach Kategorien an
"""

import html

import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_stations_subtab():
    """Render Stations Subtab mit Registry-Daten"""
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # SVG-Header mit Fallback - einfache Lösung mit größerer SVG
        stations_svg = get_asset_manager().get_asset_inline("STATIONS", size_px=32)
        header_icon = stations_svg if stations_svg else UISymbols.get_functional_icon("stations")
        st.markdown(
            f'<h3 style="margin-top: 0; margin-bottom: 1rem;">{header_icon} <strong>{i18n.t("admin.stations")} Konfiguration</strong></h3>',
            unsafe_allow_html=True,
        )
        st.markdown("Registry-basierte Stations-Verwaltung aus omf2/registry")

        # Load registry manager from session state (initialized in omf.py)
        if "registry_manager" not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager

            st.session_state["registry_manager"] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state["registry_manager"]

        # Get all stations
        all_stations = registry_manager.get_stations()

        if not all_stations:
            st.warning(f"{UISymbols.get_status_icon('warning')} Keine Stations in der Registry gefunden")
            return

        # Gruppiere Stations nach Kategorien
        stations_by_category = _group_stations_by_category(all_stations)

        # Zeige Stations nach Kategorien
        for category, stations in stations_by_category.items():
            with st.expander(f"📂 {category} ({len(stations)} stations)", expanded=False):
                _render_stations_table_with_svg_icons(stations, i18n)

        # Registry Information
        with st.expander(f"{UISymbols.get_functional_icon('dashboard')} Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Stations:** {len(all_stations)}")
            st.write(f"**Categories:** {len(stations_by_category)}")

            # Zeige Kategorien-Übersicht
            st.write("**Categories Overview:**")
            for category, stations in stations_by_category.items():
                st.write(f"- {category}: {len(stations)} stations")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Stations Subtab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Stations Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _group_stations_by_category(all_stations):
    """Gruppiert Stations nach Kategorien"""
    stations_by_category = {}

    for station_id, station_info in all_stations.items():
        category = station_info.get("type", "unknown")

        if category not in stations_by_category:
            stations_by_category[category] = {}

        stations_by_category[category][station_id] = station_info

    return stations_by_category


def show_stations_subtab():
    """Wrapper für Stations Subtab"""
    render_stations_subtab()


def _render_stations_table_with_svg_icons(stations: dict, i18n):
    """Render stations as HTML table; if a station ID matches a module serial, show module SVG."""
    from omf2.ccu.module_manager import get_ccu_module_manager
    from omf2.registry.manager.registry_manager import get_registry_manager

    module_manager = get_ccu_module_manager()
    registry_manager = get_registry_manager("omf2/registry/")
    modules = registry_manager.get_modules()

    table_html = '<table style="width: 100%; border-collapse: collapse;">'
    headers = [
        "ID",
        "Name",
        "Type",
        "IP Address",
        "IP Range",
        "OPC UA",
        "OPC UA Endpoint",
        "Description",
    ]
    table_html += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
    for header in headers:
        table_html += f'<th style="padding: 8px; text-align: left; font-weight: bold;">{html.escape(header)}</th>'
    table_html += "</tr></thead><tbody>"

    for station_id, station_info in stations.items():
        name = station_info.get("name", "Unknown")
        st_type = station_info.get("type", "Unknown")
        ip_addr = station_info.get("ip_address", "N/A")
        ip_range = station_info.get("ip_range", "N/A")
        opc_ok = station_info.get("opc_ua_server", False)
        opc_display = "✅" if opc_ok else "❌"
        opc_endpoint = station_info.get("opc_ua_endpoint", "N/A")
        desc = station_info.get("description", "No description")

        # If station_id is also a module serial → render SVG + name
        if station_id in modules:
            try:
                icon_html = module_manager.get_module_icon_html(station_id, size_px=20)
                name_cell = (
                    f'<span style="display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;">'
                    f"{icon_html}<span>{html.escape(name)}</span></span>"
                )
            except Exception:
                name_cell = html.escape(name)
        else:
            name_cell = html.escape(name)

        table_html += '<tr style="border-bottom: 1px solid #ddd;">'
        table_html += (
            f'<td style="padding: 8px; font-family: monospace; white-space: nowrap;">{html.escape(station_id)}</td>'
        )
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name_cell}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(st_type)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(ip_addr)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(ip_range)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{opc_display}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap;">{html.escape(opc_endpoint)}</td>'
        table_html += f'<td style="padding: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{html.escape(desc)}</td>'
        table_html += "</tr>"

    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)
