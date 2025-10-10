#!/usr/bin/env python3
"""
CCU Overview - Customer Order Subtab
Exakt wie aps_overview_customer_order.py mit Order Manager Integration
Reihenfolge: BLUE, WHITE, RED (wie gewünscht)

i18n: VOLLSTÄNDIG ÜBERSETZT (Pilot-Komponente)
Icons: UISymbols bleiben universell (NICHT übersetzt)
"""

import streamlit as st
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.common.i18n import I18nManager
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
    """
    Rendert eine Werkstück-Sektion (BLUE, WHITE, RED) - DRY Principle
    
    i18n: Alle Texte übersetzt
    Icons: UISymbols bleiben universell
    """
    # i18n Manager aus Session State holen (zentrale Instanz)
    i18n = st.session_state.get('i18n_manager')
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return
    
    # Icons bleiben universell (NICHT übersetzt!)
    icons = {
        "BLUE": "🔵",
        "WHITE": "⚪", 
        "RED": "🔴"
    }
    
    if TEMPLATES_AVAILABLE:
        # Template verwenden für schöne Darstellung
        # TODO: HTML-Templates auf i18n umstellen - enthält hardcoded deutsche Texte
        st.markdown(get_workpiece_box_template(workpiece_type, count, available), unsafe_allow_html=True)
    else:
        # Fallback: Einfache Darstellung (i18n)
        st.markdown(f"**{workpiece_type} {i18n.t('ccu_overview.customer_orders.workpiece')}**")
        st.markdown(f"**{i18n.t('ccu_overview.customer_orders.stock')}: {count}**")
        available_text = i18n.t('common.forms.yes') if available else i18n.t('common.forms.no')
        st.markdown(f"**{i18n.t('ccu_overview.customer_orders.available_label')}: {available_text}**")
    
    # Button Label (i18n) + Icon (universell)
    button_label = f"{UISymbols.get_status_icon('send')} {i18n.t('common.buttons.order')}"
    button_help = i18n.t('ccu_overview.customer_orders.order_button')  # Tooltip
    
    if available:
        if st.button(
            button_label,
            key=f"ccu_customer_order_{workpiece_type.lower()}", 
            type="secondary", 
            help=button_help
        ):
            _send_customer_order(workpiece_type, ccu_gateway)
    else:
        st.button(
            button_label,
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
    
    i18n: Status-Messages übersetzt mit String-Interpolation
    Icons: UISymbols bleiben universell
    """
    # i18n Manager aus Session State holen (zentrale Instanz)
    i18n = st.session_state.get('i18n_manager')
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return
    
    try:
        order_manager = get_order_manager()
        success = order_manager.send_customer_order(workpiece_type, ccu_gateway)
        
        if success:
            # Icon (universell) + Text (übersetzt mit Interpolation)
            message = i18n.t('ccu_overview.customer_orders.order_sent', workpiece_type=workpiece_type)
            st.success(f"{UISymbols.get_status_icon('success')} {message}")
        else:
            # Icon (universell) + Text (übersetzt mit Interpolation)
            message = i18n.t('ccu_overview.customer_orders.order_error', workpiece_type=workpiece_type)
            st.error(f"{UISymbols.get_status_icon('error')} {message}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error sending customer order for {workpiece_type}: {e}")
        # Error-Message mit Icon (universell) + Text (übersetzt)
        error_prefix = i18n.t('common.status.error')
        st.error(f"{UISymbols.get_status_icon('error')} {error_prefix}: {e}")
        return False


def render_customer_order_subtab(ccu_gateway: CcuGateway, registry_manager):
    """
    Render Customer Order Subtab - Business Logic über OrderManager
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    
    i18n: VOLLSTÄNDIG ÜBERSETZT (Pilot-Komponente)
    Icons: UISymbols bleiben universell
    """
    # i18n Manager aus Session State holen (zentrale Instanz)
    i18n = st.session_state.get('i18n_manager')
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return
    
    logger.info("📋 Rendering Customer Order Subtab")
    
    # Subheader mit Icon (universell) + Text (übersetzt)
    st.subheader(f"{UISymbols.get_functional_icon('customer_order')} {i18n.t('ccu_overview.customer_orders.title')}")
    
    # Gateway verfügbar?
    if not ccu_gateway:
        error_msg = i18n.t('common.status.error')
        st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway {error_msg}")
        return
    
    try:
        # Business Logic über OrderManager State-Holder (wie Sensor Manager)
        order_manager = get_order_manager()
        inventory_status = order_manager.get_inventory_status()
        
        if inventory_status and inventory_status.get("inventory"):
            # Echte MQTT-Daten vorhanden
            available_workpieces = inventory_status.get("available", {"RED": 0, "BLUE": 0, "WHITE": 0})
            last_update = inventory_status.get("last_update")
            
            # Zeitstempel anzeigen (übersetzt mit String-Interpolation)
            if last_update:
                message = i18n.t('ccu_overview.customer_orders.stock_updated', timestamp=last_update)
                st.success(f"{UISymbols.get_status_icon('success')} {message}")
        else:
            # Fallback: Default-Werte
            available_workpieces = {"RED": 0, "BLUE": 0, "WHITE": 0}
            message = i18n.t('ccu_overview.customer_orders.waiting_for_stock')
            st.info(f"{UISymbols.get_status_icon('info')} {message}")
        
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
        
        # Zusammenfassung (übersetzt)
        st.markdown("---")
        summary_title = i18n.t('ccu_overview.customer_orders.summary')
        st.markdown(f"### {UISymbols.get_functional_icon('dashboard')} {summary_title}")
        
        total_available = red_count + blue_count + white_count
        total_orders_possible = ((red_count > 0) + (blue_count > 0) + (white_count > 0))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            label = i18n.t('ccu_overview.customer_orders.total_available')
            st.metric(f"{UISymbols.get_functional_icon('inventory')} {label}", total_available)
        with col2:
            label = i18n.t('ccu_overview.customer_orders.orders_possible')
            st.metric(f"{UISymbols.get_functional_icon('customer_order')} {label}", total_orders_possible)
        with col3:
            label = i18n.t('common.status.unavailable')
            st.metric(f"{UISymbols.get_status_icon('info')} {label}", 3 - total_orders_possible)
        
    except Exception as e:
        logger.error(f"❌ Error rendering customer order: {e}")
        # Error-Message (übersetzt)
        error_prefix = i18n.t('common.status.error')
        st.error(f"{UISymbols.get_status_icon('error')} {error_prefix}: {e}")