#!/usr/bin/env python3
"""
Stations Subtab - Stations Verwaltung für Admin Settings
Zeigt alle Stations aus der Registry nach Kategorien an
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_stations_subtab():
    """Render Stations Subtab mit Registry-Daten"""
    try:
        st.subheader("🏭 Stations Konfiguration")
        st.markdown("Registry-basierte Stations-Verwaltung aus omf2/registry")

        # Load registry manager
        from omf2.registry.manager.registry_manager import get_registry_manager
        registry_manager = get_registry_manager()
        
        # Get all stations
        all_stations = registry_manager.get_stations()
        
        if not all_stations:
            st.warning("⚠️ Keine Stations in der Registry gefunden")
            return
        
        # Gruppiere Stations nach Kategorien
        stations_by_category = _group_stations_by_category(all_stations)
        
        # Zeige Stations nach Kategorien
        for category, stations in stations_by_category.items():
            with st.expander(f"📂 {category} ({len(stations)} stations)", expanded=False):
                # Erstelle DataFrame für diese Kategorie
                station_data = []
                for station_id, station_info in stations.items():
                    station_data.append({
                        "ID": station_id,
                        "Name": station_info.get('name', 'Unknown'),
                        "Type": station_info.get('type', 'Unknown'),
                        "IP Address": station_info.get('ip_address', 'N/A'),
                        "IP Range": station_info.get('ip_range', 'N/A'),
                        "OPC UA Server": "✅" if station_info.get('opc_ua_server', False) else "❌",
                        "OPC UA Endpoint": station_info.get('opc_ua_endpoint', 'N/A'),
                        "Description": station_info.get('description', 'No description')
                    })
                
                if station_data:
                    st.dataframe(
                        station_data,
                        column_config={
                            "ID": st.column_config.TextColumn("Station ID", width="medium"),
                            "Name": st.column_config.TextColumn("Name", width="medium"),
                            "Type": st.column_config.TextColumn("Type", width="small"),
                            "IP Address": st.column_config.TextColumn("IP Address", width="medium"),
                            "IP Range": st.column_config.TextColumn("IP Range", width="medium"),
                            "OPC UA Server": st.column_config.TextColumn("OPC UA", width="small"),
                            "OPC UA Endpoint": st.column_config.TextColumn("OPC UA Endpoint", width="medium"),
                            "Description": st.column_config.TextColumn("Description", width="large"),
                        },
                        hide_index=True,
                    )
        
        # Registry Information
        with st.expander("📊 Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Stations:** {len(all_stations)}")
            st.write(f"**Categories:** {len(stations_by_category)}")
            
            # Zeige Kategorien-Übersicht
            st.write("**Categories Overview:**")
            for category, stations in stations_by_category.items():
                st.write(f"- {category}: {len(stations)} stations")
        
    except Exception as e:
        logger.error(f"❌ Stations Subtab rendering error: {e}")
        st.error(f"❌ Stations Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _group_stations_by_category(all_stations):
    """Gruppiert Stations nach Kategorien"""
    stations_by_category = {}
    
    for station_id, station_info in all_stations.items():
        category = station_info.get('type', 'unknown')
        
        if category not in stations_by_category:
            stations_by_category[category] = {}
        
        stations_by_category[category][station_id] = station_info
    
    return stations_by_category


def show_stations_subtab():
    """Wrapper für Stations Subtab"""
    render_stations_subtab()
