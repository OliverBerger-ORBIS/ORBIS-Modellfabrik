#!/usr/bin/env python3
"""
CCU Overview - Inventory Subtab
Exakt wie aps_overview_inventory.py mit Order Manager Integration
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

# HTML Templates import
try:
    from omf2.assets.html_templates import get_bucket_template
    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    logger.debug(f"Templates not available: {e}")

logger = get_logger(__name__)


def _create_large_bucket_display(position, workpiece_type):
    """Erstellt eine große Bucket-Darstellung für eine Lagerposition"""
    # Versuche Templates, sonst Fallback
    if TEMPLATES_AVAILABLE:
        return get_bucket_template(position, workpiece_type)
    
    # Fallback: Bucket-Style Darstellung
    if workpiece_type:
        # Gefüllter Bucket
        color = {"RED": "#ff6b6b", "BLUE": "#4ecdc4", "WHITE": "#f7f7f7"}.get(workpiece_type, "#ddd")
        border_color = {"RED": "#e74c3c", "BLUE": "#3498db", "WHITE": "#95a5a6"}.get(workpiece_type, "#bbb")
        text_color = "#fff" if workpiece_type in ["RED", "BLUE"] else "#333"
    else:
        # Leerer Bucket
        color = "#f8f9fa"
        border_color = "#dee2e6"
        text_color = "#6c757d"
    
    return f"""
    <div style="width: 140px; height: 140px; margin: 8px auto; position: relative; 
                border: 3px solid {border_color}; border-radius: 12px; 
                background: linear-gradient(145deg, {color}, {color}dd); 
                display: flex; align-items: center; justify-content: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; color: {text_color};">
            <div style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">{position}</div>
            <div style="font-size: 11px; opacity: 0.8;">{workpiece_type or 'Leer'}</div>
        </div>
    </div>
    """


def render_inventory_subtab(ccu_gateway: CcuGateway, registry_manager):
    """Render Inventory Subtab - Business Logic über OrderManager
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("🏬 Rendering Inventory Subtab")
    
    st.subheader("🏬 Lagerbestand - HBW Übersicht")
    
    # Gateway verfügbar?
    if not ccu_gateway:
        st.error("❌ CCU Gateway nicht verfügbar")
        return
    
    try:
        # Business Logic über OrderManager State-Holder (wie Sensor Manager)
        order_manager = get_order_manager()
        inventory_status = order_manager.get_inventory_status()
        
        if inventory_status and inventory_status.get("inventory"):
            # Echte MQTT-Daten vorhanden
            inventory_data = inventory_status["inventory"]
            available = inventory_status.get("available", {"BLUE": 0, "WHITE": 0, "RED": 0})
        else:
            # Fallback: Leeres Grid
            inventory_data = {
                "A1": None, "A2": None, "A3": None,
                "B1": None, "B2": None, "B3": None,
                "C1": None, "C2": None, "C3": None
            }
            available = {"BLUE": 0, "WHITE": 0, "RED": 0}
            st.info("💡 Warte auf Lagerbestand-Daten via MQTT...")
        
        # 3x3 Grid Layout
        st.markdown("**Lagerbestand (A1-C3):**")
        
        # Row A
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            st.markdown(_create_large_bucket_display("A1", inventory_data.get("A1")), unsafe_allow_html=True)
        with col_a2:
            st.markdown(_create_large_bucket_display("A2", inventory_data.get("A2")), unsafe_allow_html=True)
        with col_a3:
            st.markdown(_create_large_bucket_display("A3", inventory_data.get("A3")), unsafe_allow_html=True)
        
        # Row B
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.markdown(_create_large_bucket_display("B1", inventory_data.get("B1")), unsafe_allow_html=True)
        with col_b2:
            st.markdown(_create_large_bucket_display("B2", inventory_data.get("B2")), unsafe_allow_html=True)
        with col_b3:
            st.markdown(_create_large_bucket_display("B3", inventory_data.get("B3")), unsafe_allow_html=True)
        
        # Row C
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(_create_large_bucket_display("C1", inventory_data.get("C1")), unsafe_allow_html=True)
        with col_c2:
            st.markdown(_create_large_bucket_display("C2", inventory_data.get("C2")), unsafe_allow_html=True)
        with col_c3:
            st.markdown(_create_large_bucket_display("C3", inventory_data.get("C3")), unsafe_allow_html=True)
        
        # Verfügbare Werkstücke anzeigen (Summary)
        st.markdown("---")
        st.markdown("**📊 Verfügbare Werkstücke:**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔵 BLUE", available.get("BLUE", 0))
        with col2:
            st.metric("⚪ WHITE", available.get("WHITE", 0))
        with col3:
            st.metric("🔴 RED", available.get("RED", 0))
        
    except Exception as e:
        logger.error(f"❌ Error rendering inventory: {e}")
        st.error(f"❌ Fehler beim Laden des Lagerbestands: {e}")
