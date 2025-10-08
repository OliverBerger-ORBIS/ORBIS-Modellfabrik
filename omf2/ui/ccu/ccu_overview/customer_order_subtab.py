#!/usr/bin/env python3
"""
CCU Overview - Customer Order Subtab
Exakt wie aps_overview_customer_order.py mit Order Manager Integration
Reihenfolge: BLUE, WHITE, RED (wie gewünscht)
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

# HTML Templates import
try:
    from omf2.assets.html_templates import get_workpiece_box_template
    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    # logger.debug(f"Templates not available: {e}")

logger = get_logger(__name__)


def _render_workpiece_section(workpiece_type: str, count: int, available: bool, ccu_gateway: CcuGateway):
    """Rendert eine Werkstück-Sektion (BLUE, WHITE, RED) - DRY Principle"""
    
    # Icons und Labels
    icons = {
        "BLUE": "🔵",
        "WHITE": "⚪", 
        "RED": "🔴"
    }
    
    if TEMPLATES_AVAILABLE:
        # Template verwenden für schöne Darstellung
        st.markdown(get_workpiece_box_template(workpiece_type, count, available), unsafe_allow_html=True)
    else:
        # Fallback: Einfache Darstellung
        st.markdown(f"**{workpiece_type} Werkstück**")
        st.markdown(f"**Bestand: {count}**")
        st.markdown(f"**Verfügbar: {'✅ Ja' if available else '❌ Nein'}**")
    
    if available:
        if st.button(
            f"{UISymbols.get_status_icon('send')} Bestellen", 
            key=f"ccu_customer_order_{workpiece_type.lower()}", 
            type="secondary", 
            help=f"Bestellung für {workpiece_type} Werkstück"
        ):
            _send_customer_order(workpiece_type, ccu_gateway)
    else:
        st.button(
            f"{UISymbols.get_status_icon('send')} Bestellen", 
            key=f"ccu_customer_order_{workpiece_type.lower()}_disabled", 
            disabled=True
        )


def _send_customer_order(workpiece_type: str, ccu_gateway: CcuGateway) -> bool:
    """
    Sendet Kundenauftrag-Bestellung über Order Manager
    
    Args:
        workpiece_type: RED, BLUE, oder WHITE
        ccu_gateway: CCU Gateway für MQTT-Versand
        
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    try:
        order_manager = get_order_manager()
        success = order_manager.send_customer_order(workpiece_type, ccu_gateway)
        
        if success:
            st.success(f"{UISymbols.get_status_icon('success')} Kundenauftrag für {workpiece_type} gesendet")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Kundenauftrag-Bestellung für {workpiece_type}")
        
        return success
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Kundenauftrag-Bestellung: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Kundenauftrag-Bestellung: {e}")
        return False


def render_customer_order_subtab(ccu_gateway: CcuGateway, registry_manager):
    """Render Customer Order Subtab - Business Logic über OrderManager
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📋 Rendering Customer Order Subtab")
    
    st.subheader(f"{UISymbols.get_functional_icon('customer_order')} Kundenaufträge (Customer Orders)")
    
    # Gateway verfügbar?
    if not ccu_gateway:
        st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway nicht verfügbar")
        return
    
    try:
        # Business Logic über OrderManager State-Holder (wie Sensor Manager)
        order_manager = get_order_manager()
        inventory_status = order_manager.get_inventory_status()
        
        if inventory_status and inventory_status.get("inventory"):
            # Echte MQTT-Daten vorhanden
            available_workpieces = inventory_status.get("available", {"RED": 0, "BLUE": 0, "WHITE": 0})
            last_update = inventory_status.get("last_update")
            
            # Zeitstempel anzeigen
            if last_update:
                st.success(f"{UISymbols.get_status_icon('success')} Lagerbestand aktualisiert: {last_update}")
        else:
            # Fallback: Default-Werte
            available_workpieces = {"RED": 0, "BLUE": 0, "WHITE": 0}
            st.info(f"{UISymbols.get_status_icon('info')} Warte auf Lagerbestand-Daten via MQTT...")
        
        # Verfügbare Werkstücke
        red_count = available_workpieces.get("RED", 0)
        blue_count = available_workpieces.get("BLUE", 0)
        white_count = available_workpieces.get("WHITE", 0)
        
        # 3-Spalten-Layout für Werkstücke (BLUE, WHITE, RED)
        col1, col2, col3 = st.columns(3)
        
        # Werkstück-Sektionen rendern (BLUE, WHITE, RED) - DRY Principle
        with col1:
            _render_workpiece_section("BLUE", blue_count, blue_count > 0, ccu_gateway)
        
        with col2:
            _render_workpiece_section("WHITE", white_count, white_count > 0, ccu_gateway)
        
        with col3:
            _render_workpiece_section("RED", red_count, red_count > 0, ccu_gateway)
        
        # Zusammenfassung
        st.markdown("---")
        st.markdown(f"### {UISymbols.get_functional_icon('dashboard')} Zusammenfassung")
        
        total_available = red_count + blue_count + white_count
        total_orders_possible = ((red_count > 0) + (blue_count > 0) + (white_count > 0))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{UISymbols.get_functional_icon('inventory')} Gesamt verfügbar", total_available)
        with col2:
            st.metric(f"{UISymbols.get_functional_icon('customer_order')} Bestellbar", total_orders_possible)
        with col3:
            st.metric(f"{UISymbols.get_status_icon('info')} Nicht verfügbar", 3 - total_orders_possible)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Error rendering customer order: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Laden der Kundenaufträge: {e}")