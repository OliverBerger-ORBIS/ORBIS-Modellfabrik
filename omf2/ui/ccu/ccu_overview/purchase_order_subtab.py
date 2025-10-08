#!/usr/bin/env python3
"""
CCU Overview - Purchase Order Subtab
Exakt wie aps_overview_purchase_order.py mit Order Manager Integration
Reihenfolge: BLUE, WHITE, RED (wie gewünscht)
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

# HTML Templates import
try:
    from omf2.assets.html_templates import get_bucket_template, get_workpiece_box_template
    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    # logger.debug(f"Templates not available: {e}")

logger = get_logger(__name__)


def _render_workpiece_section(workpiece_type: str, count: int, need: int, max_capacity: int, ccu_gateway: CcuGateway):
    """Rendert eine Werkstück-Sektion (BLUE, WHITE, RED) - DRY Principle"""
    
    # Icons und Labels
    icons = {
        "BLUE": "🔵",
        "WHITE": "⚪", 
        "RED": "🔴"
    }
    
    st.markdown(f"#### {icons.get(workpiece_type, '📦')} {workpiece_type} Werkstücke")
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    with col1:
        if TEMPLATES_AVAILABLE:
            st.markdown(get_workpiece_box_template(workpiece_type, count, count > 0), unsafe_allow_html=True)
        else:
            st.markdown(f"**{workpiece_type}**")
            st.markdown(f"**Bestand: {count}**")
            st.markdown(f"**Verfügbar: {'✅ Ja' if count > 0 else '❌ Nein'}**")
    
    with col2:
        st.markdown(f"**Bedarf: {need} von {max_capacity}**")
        if need > 0:
            st.markdown(f"**Noch bestellbar: {need} Werkstücke**")
        else:
            st.success(f"{UISymbols.get_status_icon('success')} Vollständig - Kein Bedarf")
    
    with col3:
        if need > 0:
            # Leere Buckets für fehlende Werkstücke - LINKSBÜNDIG
            if TEMPLATES_AVAILABLE:
                empty_buckets = ""
                for i in range(need):
                    empty_bucket = get_bucket_template(f"{workpiece_type[0]}{i+1}", None)
                    empty_buckets += empty_bucket
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-start;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
            else:
                # Fallback: Einfache Darstellung
                empty_buckets = ""
                for i in range(need):
                    empty_buckets += '<div style="width: 140px; height: 140px; border: 2px solid #ccc; border-top: none; background-color: #f9f9f9; border-radius: 0 0 8px 8px; display: inline-block; margin: 8px;"></div>'
                st.markdown(
                    f'<div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-start;">{empty_buckets}</div>',
                    unsafe_allow_html=True,
                )
    
    with col4:
        if need > 0:
            if st.button(f"{UISymbols.get_status_icon('send')} Rohstoff bestellen", key=f"ccu_purchase_order_{workpiece_type.lower()}", type="secondary"):
                _send_raw_material_order(workpiece_type, ccu_gateway)
        else:
            st.button(f"{UISymbols.get_status_icon('send')} Rohstoff bestellen", key=f"ccu_purchase_order_{workpiece_type.lower()}_disabled", disabled=True)


def _send_raw_material_order(workpiece_type: str, ccu_gateway: CcuGateway) -> bool:
    """
    Sendet Rohmaterial-Bestellung über Order Manager
    
    Args:
        workpiece_type: RED, BLUE, oder WHITE
        ccu_gateway: CCU Gateway für MQTT-Versand
        
    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    try:
        order_manager = get_order_manager()
        success = order_manager.send_raw_material_order(workpiece_type, ccu_gateway)
        
        if success:
            st.success(f"{UISymbols.get_status_icon('success')} Rohmaterial-Bestellung für {workpiece_type} gesendet")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung für {workpiece_type}")
        
        return success
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung: {e}")
        return False


def render_purchase_order_subtab(ccu_gateway: CcuGateway, registry_manager):
    """Render Purchase Order Subtab - Business Logic über OrderManager
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📦 Rendering Purchase Order Subtab")
    
    st.subheader(f"{UISymbols.get_functional_icon('purchase_order')} Rohmaterial-Bestellungen (Purchase Orders)")
    
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
        
        # Konstanten aus CCU Config laden
        from omf2.ccu.config_loader import get_ccu_config_loader
        config_loader = get_ccu_config_loader()
        inventory_settings = config_loader.load_production_settings().get("inventorySettings", {})
        MAX_CAPACITY = inventory_settings.get("maxCapacity", 3)
        workpiece_types = inventory_settings.get("workpieceTypes", ["RED", "BLUE", "WHITE"])
        
        # Verfügbare Werkstücke
        red_count = available_workpieces.get("RED", 0)
        blue_count = available_workpieces.get("BLUE", 0)
        white_count = available_workpieces.get("WHITE", 0)
        
        # Berechne Bedarf für jede Farbe
        red_need = MAX_CAPACITY - red_count
        blue_need = MAX_CAPACITY - blue_count
        white_need = MAX_CAPACITY - white_count
        
        # Werkstück-Sektionen rendern (BLUE, WHITE, RED)
        _render_workpiece_section("BLUE", blue_count, blue_need, MAX_CAPACITY, ccu_gateway)
        
        _render_workpiece_section("WHITE", white_count, white_need, MAX_CAPACITY, ccu_gateway)
        
        _render_workpiece_section("RED", red_count, red_need, MAX_CAPACITY, ccu_gateway)
        
        # Zusammenfassung
        st.markdown("---")
        st.markdown(f"### {UISymbols.get_functional_icon('dashboard')} Zusammenfassung")
        
        total_need = red_need + blue_need + white_need
        total_available = red_count + blue_count + white_count
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{UISymbols.get_functional_icon('inventory')} Gesamt verfügbar", total_available)
        with col2:
            st.metric(f"{UISymbols.get_status_icon('warning')} Gesamt Bedarf", total_need)
        with col3:
            st.metric(f"{UISymbols.get_functional_icon('purchase_order')} Offene Bestellungen", total_need)
        
    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Error rendering purchase order: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Laden der Rohmaterial-Bestellungen: {e}")