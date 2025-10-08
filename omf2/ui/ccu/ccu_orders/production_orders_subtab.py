#!/usr/bin/env python3
"""
Production Orders Subtab - Only PRODUCTION orderType
"""

import streamlit as st
from omf2.ccu.production_order_manager import get_production_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def show_production_orders_subtab():
    """Render Production Orders Subtab (nur orderType: PRODUCTION)"""
    logger.info("📝 Rendering Production Orders Subtab")
    
    try:
        # Business Logic über ProductionOrderManager
        production_order_manager = get_production_order_manager()
        
        # Daten holen
        all_active = production_order_manager.get_active_orders()
        all_completed = production_order_manager.get_completed_orders()
        
        # Filter: Nur PRODUCTION Orders
        active_orders = [o for o in all_active if o.get('orderType') == 'PRODUCTION']
        completed_orders = [o for o in all_completed if o.get('orderType') == 'PRODUCTION']
        
        st.markdown("### 🏭 Production Orders")
        st.markdown("Only orders with **orderType: PRODUCTION**")
        
        # Active Production Orders
        _show_active_orders_section(active_orders, production_order_manager)
        
        # Completed Production Orders
        st.divider()
        _show_completed_orders_section(completed_orders, production_order_manager)
        
    except Exception as e:
        logger.error(f"❌ Production Orders Subtab rendering error: {e}")
        st.error(f"❌ Production Orders Subtab failed: {e}")


def _show_active_orders_section(active_orders, production_order_manager):
    """Show Active Production Orders Section"""
    st.markdown("#### Active Production Orders")
    
    if active_orders:
        for order in active_orders:
            _render_order_card(order, production_order_manager, is_completed=False)
    else:
        st.info(f"{UISymbols.get_status_icon('info')} Keine aktiven Production Orders vorhanden")


def _show_completed_orders_section(completed_orders, production_order_manager):
    """Show Completed Production Orders Section"""
    st.markdown("#### Completed Production Orders")
    
    if completed_orders:
        for order in completed_orders:
            _render_order_card(order, production_order_manager, is_completed=True)
    else:
        st.info(f"{UISymbols.get_status_icon('info')} Keine abgeschlossenen Production Orders vorhanden")


def _render_order_card(order, production_order_manager, is_completed=False):
    """Render einzelne Order Card
    
    Args:
        order: Order-Dict
        production_order_manager: ProductionOrderManager Instanz
        is_completed: True für completed orders (ausgegraut)
    """
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            order_id = order.get('orderId', 'N/A')[:8]  # Kurze ID
            if is_completed:
                st.markdown(f"~~**{order_id}...**~~")
            else:
                st.write(f"**{order_id}...**")
        
        with col2:
            workpiece_type = order.get('type', 'N/A')
            workpiece_icon = {
                'RED': '🔴',
                'BLUE': '🔵',
                'WHITE': '⚪'
            }.get(workpiece_type, '⚪')
            if is_completed:
                st.markdown(f"~~{workpiece_icon} {workpiece_type}~~")
            else:
                st.write(f"{workpiece_icon} {workpiece_type}")
        
        with col3:
            if is_completed:
                st.write(f"✅ COMPLETED")
            else:
                state = order.get('state', 'N/A')
                state_icon = {
                    'IN_PROGRESS': '🟡',
                    'COMPLETED': '🟢',
                    'ENQUEUED': '⚪',
                    'FAILED': '🔴'
                }.get(state, '⚪')
                st.write(f"{state_icon} {state}")
        
        with col4:
            order_type = order.get('orderType', 'N/A')
            if is_completed:
                st.markdown(f"~~📋 {order_type}~~")
            else:
                st.write(f"📋 {order_type}")
        
        # Production Steps (expandable)
        complete_production_plan = production_order_manager.get_complete_production_plan(order)
        if complete_production_plan:
            with st.expander(f"Production steps ({len(complete_production_plan)})", expanded=False):
                _render_production_steps(complete_production_plan, is_completed)


def _render_production_steps(production_plan, is_completed=False):
    """Render Production Steps
    
    Args:
        production_plan: List of production steps
        is_completed: True für completed orders (ausgegraut)
    """
    for idx, step in enumerate(production_plan, 1):
        step_state = step.get('state', 'PENDING')
        step_type = step.get('type', 'N/A')
        
        # Status-Icons
        status_icon = {
            'FINISHED': '✅',
            'RUNNING': '🔄',
            'IN_PROGRESS': '🔄',
            'ENQUEUED': '⏳',
            'FAILED': '❌',
            'PENDING': '⚪'
        }.get(step_state, '⚪')
        
        # Station-Icons basierend auf moduleType/source/target
        module_type = step.get('moduleType', '')
        source = step.get('source', '')
        target = step.get('target', '')
        
        # Icon-Mapping für Stationen
        station_icons = {
            'DPS': '🏭',
            'HBW': '🏭',
            'MILL': '⚙️',
            'DRILL': '⚙️',
            'AIQS': '🧠',
            'DELIVERY': '🚚',
            'START': '🚀',
            'AGV': '🤖'
        }
        
        # Bestimme Station-Icon
        station_icon = '🤖'  # Default AGV
        if step_type == 'NAVIGATION':
            if source in station_icons:
                station_icon = station_icons[source]
            elif target in station_icons:
                station_icon = station_icons[target]
        elif step_type == 'MANUFACTURE':
            if module_type in station_icons:
                station_icon = station_icons[module_type]
        
        # Step-Beschreibung
        if step_type == 'NAVIGATION':
            step_desc = f"Automated Guided Vehicle (AGV)"
            if source != target:
                target_icon = station_icons.get(target, '🏭')
                step_desc += f" > {target_icon} {target}"
        elif step_type == 'MANUFACTURE':
            command = step.get('command', '')
            if command in ['LOAD', 'UNLOAD']:
                step_desc = f"{module_type} : {command} AGV"
            else:
                step_desc = f"{module_type} : {command}"
        else:
            step_desc = f"{step_type}"
        
        # Anzeige
        if is_completed:
            st.markdown(f"~~{station_icon} {status_icon} {step_desc}~~")
        else:
            st.write(f"{station_icon} {status_icon} {step_desc}")

