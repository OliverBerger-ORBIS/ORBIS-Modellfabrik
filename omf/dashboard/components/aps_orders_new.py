"""
APS Orders Tab - Laufende Fertigungsaufträge mit Production Steps und Fabrik-Layout
Entspricht dem "Orders" Tab des Original APS-Dashboards
Basiert auf production_order_current.py, aber vollständig implementiert im APS-Stil
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("dashboard.components.aps_orders")


def show_aps_orders_new():
    """Zeigt den APS Orders Tab mit 2-Spalten-Layout"""
    st.header("📋 APS Orders")
    st.write("Laufende Fertigungsaufträge mit Production Steps und Werkstück-Positionierung")
    
    # 2-Spalten-Layout: Links Orders & Production Steps, Rechts Visualisierung & Order Info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        _show_orders_and_steps_section()
    
    with col2:
        _show_visualization_and_info_section()


def _show_orders_and_steps_section():
    """Zeigt die linke Spalte: Orders & Production Steps"""
    
    # 1. Ongoing Orders (Laufende Aufträge)
    st.subheader("📋 Ongoing Orders")
    _show_ongoing_orders()
    
    st.divider()
    
    # 2. Production Steps (Produktionsschritte)
    st.subheader("⚙️ Production Steps")
    _show_production_steps()


def _show_ongoing_orders():
    """Zeigt die Tabelle der laufenden Aufträge"""
    
    # Beispiel-Daten für laufende Aufträge
    orders_data = [
        {
            "Order": "PO-001",
            "Color": "🔴 Red",
            "Timestamp": "2025-09-22 18:30:55"
        },
        {
            "Order": "PO-002", 
            "Color": "🔵 Blue",
            "Timestamp": "2025-09-22 18:25:30"
        },
        {
            "Order": "PO-003",
            "Color": "⚪ White", 
            "Timestamp": "2025-09-22 18:20:15"
        }
    ]
    
    # Interaktive Tabelle mit Auswahl
    selected_order = st.selectbox(
        "Wählen Sie einen Auftrag aus:",
        options=orders_data,
        format_func=lambda x: f"{x['Order']} - {x['Color']} ({x['Timestamp']})",
        key="aps_orders_tab19_selection_new"
    )
    
    # Zeige ausgewählten Auftrag
    if selected_order:
        st.write(f"**Ausgewählter Auftrag:** {selected_order['Order']} - {selected_order['Color']}")
        
        # Speichere ausgewählten Auftrag in Session State
        st.session_state.selected_aps_order = selected_order


def _show_production_steps():
    """Zeigt die detaillierte Liste der Production Steps"""
    
    # Hole ausgewählten Auftrag
    selected_order = st.session_state.get("selected_aps_order", None)
    
    if not selected_order:
        st.info("👆 Wählen Sie zuerst einen Auftrag aus der Liste oben aus")
        return
    
    # Production Steps für den ausgewählten Auftrag
    steps = _get_production_steps_for_order(selected_order["Order"])
    
    st.write(f"**Production Steps für {selected_order['Order']}:**")
    
    # Zeige alle Schritte mit Status-Icons
    for i, step in enumerate(steps, 1):
        status_icon = step["status_icon"]
        step_name = step["step"]
        description = step.get("description", "")
        
        # Farbige Box für jeden Schritt
        if step["status"] == "completed":
            color = "#d4edda"  # Grün
            border_color = "#28a745"
        elif step["status"] == "in_progress":
            color = "#fff3cd"  # Gelb
            border_color = "#ffc107"
        else:
            color = "#f8f9fa"  # Grau
            border_color = "#6c757d"
        
        st.markdown(f"""
        <div style="border: 2px solid {border_color}; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: {color};">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">{status_icon}</span>
                <div>
                    <h5 style="margin: 0; color: #495057;">{i}. {step_name}</h5>
                    <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">{description}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _show_visualization_and_info_section():
    """Zeigt die rechte Spalte: Visualisierung & Order Info"""
    
    # 1. Current Production Step (Aktueller Produktionsschritt)
    st.subheader("🏭 Current Production Step")
    _show_factory_layout_visualization()
    
    st.divider()
    
    # 2. Order Information (Auftragsinformationen)
    st.subheader("📊 Order Information")
    _show_order_information()


def _show_factory_layout_visualization():
    """Zeigt die grafische Repräsentation des Fabrik-Layouts (3x4 Grid)"""
    
    # Hole ausgewählten Auftrag
    selected_order = st.session_state.get("selected_aps_order", None)
    
    if not selected_order:
        st.info("👆 Wählen Sie zuerst einen Auftrag aus der linken Spalte aus")
        return
    
    # Fabrik-Layout (3x4 Grid) - verwende das echte Factory Layout
    st.write("**Fabrik-Layout mit Werkstück-Position:**")
    
    # Importiere Factory Layout
    try:
        from omf.dashboard.components.shopfloor_layout import show_shopfloor_grid
        show_shopfloor_grid()
    except ImportError:
        st.error("❌ Factory Layout konnte nicht geladen werden")
        # Fallback: Einfaches Grid
        _show_simple_factory_grid(selected_order)
    
def _show_simple_factory_grid(selected_order):
    """Fallback: Einfaches Factory Grid wenn das echte Layout nicht verfügbar ist"""
    
    # Aktuelle Position des Werkstücks
    current_position = _get_current_workpiece_position(selected_order["Order"])
    
    # Grid-Layout
    col1, col2, col3 = st.columns(3)
    
    # Obere Reihe
    with col1:
        _show_factory_station("🏬 HBW", "High-Bay Warehouse", current_position == "HBW")
    
    with col2:
        _show_factory_station("⚙️ MILL", "Milling Station", current_position == "MILL")
    
    with col3:
        _show_factory_station("🤖 AIQS", "Quality Control", current_position == "AIQS")
    
    col4, col5, col6 = st.columns(3)
    
    # Untere Reihe
    with col4:
        _show_factory_station("📦 DPS", "Delivery Station", current_position == "DPS")
    
    with col5:
        _show_factory_station("🔩 DRILL", "Drilling Station", current_position == "DRILL")
    
    with col6:
        _show_factory_station("🔋 CHRG", "Charging Station", current_position == "CHRG")


def _show_factory_station(station_icon, station_name, is_active):
    """Zeigt eine Fabrik-Station mit aktivem Status"""
    
    if is_active:
        # Aktive Station
        st.markdown(f"""
        <div style="border: 3px solid #dc3545; border-radius: 8px; padding: 20px; margin: 10px 0; background-color: #f8d7da; text-align: center;">
            <h4 style="margin: 0; color: #721c24;">{station_icon} {station_name}</h4>
            <p style="margin: 5px 0; color: #721c24; font-weight: bold;">(AKTIV)</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Inaktive Station
        st.markdown(f"""
        <div style="border: 2px solid #6c757d; border-radius: 8px; padding: 20px; margin: 10px 0; background-color: #f8f9fa; text-align: center;">
            <h4 style="margin: 0; color: #495057;">{station_icon} {station_name}</h4>
        </div>
        """, unsafe_allow_html=True)


def _show_order_information():
    """Zeigt detaillierte Informationen zum aktuell ausgewählten Auftrag"""
    
    # Hole ausgewählten Auftrag
    selected_order = st.session_state.get("selected_aps_order", None)
    
    if not selected_order:
        st.info("👆 Wählen Sie zuerst einen Auftrag aus der linken Spalte aus")
        return
    
    # Order Information
    st.write(f"**OrderID:** {selected_order['Order']}")
    st.write(f"**Status:** In Progress")
    st.write(f"**Timestamp:** {selected_order['Timestamp']}")
    
    # Zusätzliche Informationen
    st.write("**Zusätzliche Informationen:**")
    st.write(f"- **Werkstück-Typ:** {selected_order['Color']}")
    st.write(f"- **Gestartet:** {selected_order['Timestamp']}")
    st.write(f"- **Geschätzte Fertigstellung:** {_get_estimated_completion(selected_order['Order'])}")
    st.write(f"- **Aktueller Schritt:** {_get_current_step(selected_order['Order'])}")


def _get_production_steps_for_order(order_id):
    """Gibt die Production Steps für einen bestimmten Auftrag zurück"""
    
    # Beispiel-Production Steps (basierend auf der Analyse)
    if "PO-001" in order_id:  # Red Product
        return [
            {"step": "AGV > High-Bay Warehouse", "status": "completed", "status_icon": "✅", "description": "Transport zum Hochregallager"},
            {"step": "High-Bay Warehouse: Load AGV", "status": "completed", "status_icon": "✅", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Milling Station", "status": "completed", "status_icon": "✅", "description": "Transport zur Frässtation"},
            {"step": "Milling Station: Unload AGV", "status": "completed", "status_icon": "✅", "description": "Werkstück von AGV entladen"},
            {"step": "Milling Station: Milling", "status": "in_progress", "status_icon": "▶️", "description": "Fräsen des Werkstücks"},
            {"step": "Milling Station: Load AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Quality Control with AI", "status": "pending", "status_icon": "⏰", "description": "Transport zur Qualitätskontrolle"},
            {"step": "Quality Control with AI: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"},
            {"step": "Quality Control with AI: Quality check", "status": "pending", "status_icon": "⏰", "description": "Qualitätskontrolle mittels KI"},
            {"step": "Quality Control with AI: Load AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Delivery and Pickup Station", "status": "pending", "status_icon": "⏰", "description": "Transport zur Auslieferung"},
            {"step": "Delivery and Pickup Station: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"}
        ]
    elif "PO-002" in order_id:  # Blue Product
        return [
            {"step": "AGV > High-Bay Warehouse", "status": "completed", "status_icon": "✅", "description": "Transport zum Hochregallager"},
            {"step": "High-Bay Warehouse: Load AGV", "status": "completed", "status_icon": "✅", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Drilling Station", "status": "completed", "status_icon": "✅", "description": "Transport zur Bohrstation"},
            {"step": "Drilling Station: Unload AGV", "status": "completed", "status_icon": "✅", "description": "Werkstück von AGV entladen"},
            {"step": "Drilling Station: Drilling", "status": "completed", "status_icon": "✅", "description": "Bohren des Werkstücks"},
            {"step": "Drilling Station: Load AGV", "status": "completed", "status_icon": "✅", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Milling Station", "status": "in_progress", "status_icon": "▶️", "description": "Transport zur Frässtation"},
            {"step": "Milling Station: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"},
            {"step": "Milling Station: Milling", "status": "pending", "status_icon": "⏰", "description": "Fräsen des Werkstücks"},
            {"step": "Milling Station: Load AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Quality Control with AI", "status": "pending", "status_icon": "⏰", "description": "Transport zur Qualitätskontrolle"},
            {"step": "Quality Control with AI: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"},
            {"step": "Quality Control with AI: Quality check", "status": "pending", "status_icon": "⏰", "description": "Qualitätskontrolle mittels KI"},
            {"step": "Quality Control with AI: Load AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Delivery and Pickup Station", "status": "pending", "status_icon": "⏰", "description": "Transport zur Auslieferung"},
            {"step": "Delivery and Pickup Station: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"}
        ]
    else:  # White Product
        return [
            {"step": "AGV > High-Bay Warehouse", "status": "completed", "status_icon": "✅", "description": "Transport zum Hochregallager"},
            {"step": "High-Bay Warehouse: Load AGV", "status": "completed", "status_icon": "✅", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Drilling Station", "status": "in_progress", "status_icon": "▶️", "description": "Transport zur Bohrstation"},
            {"step": "Drilling Station: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"},
            {"step": "Drilling Station: Drilling", "status": "pending", "status_icon": "⏰", "description": "Bohren des Werkstücks"},
            {"step": "Drilling Station: Load AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Quality Control with AI", "status": "pending", "status_icon": "⏰", "description": "Transport zur Qualitätskontrolle"},
            {"step": "Quality Control with AI: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"},
            {"step": "Quality Control with AI: Quality check", "status": "pending", "status_icon": "⏰", "description": "Qualitätskontrolle mittels KI"},
            {"step": "Quality Control with AI: Load AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück auf AGV laden"},
            {"step": "AGV > Delivery and Pickup Station", "status": "pending", "status_icon": "⏰", "description": "Transport zur Auslieferung"},
            {"step": "Delivery and Pickup Station: Unload AGV", "status": "pending", "status_icon": "⏰", "description": "Werkstück von AGV entladen"}
        ]


def _get_current_workpiece_position(order_id):
    """Gibt die aktuelle Position des Werkstücks zurück"""
    
    if "PO-001" in order_id:  # Red Product - aktuell in Milling Station
        return "MILL"
    elif "PO-002" in order_id:  # Blue Product - aktuell auf dem Weg zur Milling Station
        return "DRILL"
    else:  # White Product - aktuell auf dem Weg zur Drilling Station
        return "HBW"


def _get_estimated_completion(order_id):
    """Gibt die geschätzte Fertigstellungszeit zurück"""
    
    if "PO-001" in order_id:
        return "2025-09-22 19:15:30"
    elif "PO-002" in order_id:
        return "2025-09-22 19:30:45"
    else:
        return "2025-09-22 19:45:20"


def _get_current_step(order_id):
    """Gibt den aktuellen Produktionsschritt zurück"""
    
    if "PO-001" in order_id:
        return "Milling Station: Milling"
    elif "PO-002" in order_id:
        return "AGV > Milling Station"
    else:
        return "AGV > Drilling Station"


def get_orders_data():
    """Gibt die aktuellen Auftragsdaten zurück"""
    return {
        "ongoing_orders": [
            {"Order": "PO-001", "Color": "🔴 Red", "Timestamp": "2025-09-22 18:30:55"},
            {"Order": "PO-002", "Color": "🔵 Blue", "Timestamp": "2025-09-22 18:25:30"},
            {"Order": "PO-003", "Color": "⚪ White", "Timestamp": "2025-09-22 18:20:15"}
        ]
    }


def set_orders_data(orders_data):
    """Setzt die Auftragsdaten"""
    logger.info(f"Auftragsdaten gesetzt: {orders_data}")
