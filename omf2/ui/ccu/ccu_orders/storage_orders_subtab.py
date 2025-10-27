#!/usr/bin/env python3
"""
Storage Orders Subtab - Only STORAGE orderType
"""

import streamlit as st

from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload

logger = get_logger(__name__)


def reload_storage_orders():
    """
    Reload storage orders data into session state
    
    This wrapper function loads orders from OrderManager and stores them
    in session state for use by the UI rendering logic.
    """
    try:
        logger.debug("🔄 reload_storage_orders() called - loading fresh data")
        order_manager = get_order_manager()
        
        # Load fresh data
        all_active = order_manager.get_active_orders()
        all_completed = order_manager.get_completed_orders()
        
        # Filter: Nur STORAGE Orders
        active_orders = [o for o in all_active if o.get("orderType") == "STORAGE"]
        completed_orders = [o for o in all_completed if o.get("orderType") == "STORAGE"]
        
        # Store in session state
        st.session_state['storage_orders_active'] = active_orders
        st.session_state['storage_orders_completed'] = completed_orders
        
        logger.debug(f"✅ Loaded {len(active_orders)} active and {len(completed_orders)} completed storage orders")
        
    except Exception as e:
        logger.error(f"❌ Error in reload_storage_orders(): {e}")
        # Set empty lists on error to prevent UI crashes
        st.session_state['storage_orders_active'] = []
        st.session_state['storage_orders_completed'] = []


def show_storage_orders_subtab(i18n):
    """Render Storage Orders Subtab (nur orderType: STORAGE)"""
    logger.info("📝 Rendering Storage Orders Subtab")

    try:
        # Use production_orders_refresh_helper for robust polling + compare
        check_and_reload(group='order_updates', reload_callback=reload_storage_orders, interval_ms=1000)
        
        # Get data from session state (populated by reload_storage_orders callback)
        # If not yet populated, load it now
        if 'storage_orders_active' not in st.session_state:
            reload_storage_orders()
        
        active_orders = st.session_state.get('storage_orders_active', [])
        completed_orders = st.session_state.get('storage_orders_completed', [])
        
        # Get order_manager for rendering operations
        order_manager = get_order_manager()

        st.markdown(f"### {i18n.t('ccu_orders.storage.title')}")
        st.markdown(i18n.t("ccu_orders.storage.subtitle"))

        # Active Storage Orders
        _show_active_orders_section(active_orders, order_manager, i18n)

        # Completed Storage Orders
        st.divider()
        _show_completed_orders_section(completed_orders, order_manager, i18n)

    except Exception as e:
        logger.error(f"❌ Storage Orders Subtab rendering error: {e}")
        st.error(f"❌ Storage Orders Subtab failed: {e}")


def _show_active_orders_section(active_orders, order_manager, i18n):
    """Show Active Storage Orders Section"""
    st.markdown(f"#### {i18n.t('ccu_orders.storage.active_title')}")

    if active_orders:
        for order in active_orders:
            _render_order_card(order, order_manager, i18n, is_completed=False)
    else:
        st.info(f"{UISymbols.get_status_icon('info')} {i18n.t('ccu_orders.storage.no_active')}")


def _show_completed_orders_section(completed_orders, order_manager, i18n):
    """Show Completed Storage Orders Section"""
    st.markdown(f"#### {i18n.t('ccu_orders.storage.completed_title')}")

    if completed_orders:
        for order in completed_orders:
            _render_order_card(order, order_manager, i18n, is_completed=True)
    else:
        st.info(f"{UISymbols.get_status_icon('info')} {i18n.t('ccu_orders.storage.no_completed')}")


def _render_order_card(order, order_manager, i18n, is_completed=False):
    """Render einzelne Order Card

    Args:
        order: Order-Dict
        order_manager: OrderManager Instanz
        i18n: I18nManager Instanz
        is_completed: True für completed orders (ausgegraut)
    """
    with st.container():
        # NEU: Zwei-Spalten-Layout (1:2 - Liste:Shopfloor) - EXAKT wie production_orders_subtab.py
        col1, col2 = st.columns([1, 2])

        with col1:
            # Links: Order-Details und Storage Steps
            _render_order_details(order, order_manager, i18n, is_completed)

        with col2:
            # Rechts: Shopfloor Layout (nur für aktive Orders)
            if not is_completed:
                _render_shopfloor_for_storage_order(order, order_manager, i18n)
            else:
                st.info("🏁 Order completed - no active shopfloor")


def _render_order_details(order, order_manager, i18n, is_completed=False):
    """Render Order-Details (links Spalte) - EXAKT wie production_orders_subtab.py"""
    # Order Header
    order_id = order.get("orderId", "N/A")[:8]  # Kurze ID
    st.write(f"**{order_id}...**")

    # Order Info Row
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        workpiece_type = order.get("type", "N/A")
        workpiece_icon = {"RED": "🔴", "BLUE": "🔵", "WHITE": "⚪"}.get(workpiece_type, "⚪")
        st.write(f"{workpiece_icon} {workpiece_type}")

    with col2:
        order_type = order.get("orderType", "N/A")
        st.write(f"📋 {order_type}")

    with col3:
        if is_completed:
            st.write(f"✅ {i18n.t('ccu_orders.card.completed')}")
        else:
            state = order.get("state", "N/A")
            # KONSISTENT mit production_orders_subtab.py
            state_icon = {
                # Aktive Zustände
                "IN_PROGRESS": "🟠",  # ORANGE CIRCLE - konsistent!
                "RUNNING": "🟠",  # Alias
                # Abgeschlossene Zustände
                "FINISHED": "✅",
                "COMPLETED": "✅",  # Alias
                # Wartende Zustände
                "ENQUEUED": "⏳",
                "PENDING": "⚪",
                # Fehler-Zustände
                "FAILED": "❌",
            }.get(state, "⚪")
            st.write(f"{state_icon} {state}")

    # Storage Steps (immer anzeigen, nicht expandable)
    complete_storage_plan = order_manager.get_complete_storage_plan(order)
    if complete_storage_plan:
        st.markdown(f"**{i18n.t('ccu_orders.card.storage_steps')}:**")
        _render_storage_steps(complete_storage_plan, i18n, is_completed)


def _render_shopfloor_for_storage_order(order, order_manager, i18n):
    """Zeigt Shopfloor Layout mit aktiver Modul-Hervorhebung und AGV-Route für Storage Orders"""
    from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout
    from omf2.ui.ccu.common.route_utils import get_route_for_navigation_step
    from omf2.ccu.config_loader import get_ccu_config_loader

    st.markdown("#### 🗺️ Shopfloor Layout")

    # Aktuelles Modul aus Storage Plan ermitteln
    storage_plan = order_manager.get_complete_storage_plan(order)
    active_module = _get_current_active_module(storage_plan)
    active_intersections = _get_active_intersections(storage_plan)
    
    # AGV Route berechnen NUR wenn FTS Navigation der AKTIVE Step ist
    # FIX: Nur Route zeigen wenn active_module == "FTS", nicht bei anderen Modulen
    route_points = None
    agv_progress = 0.0
    current_nav_step = None
    
    # Find current navigation step - but only show route if it's the ACTIVE step
    if active_module == "FTS":
        for step in storage_plan:
            step_state = step.get("state", "PENDING")
            # Only IN_PROGRESS navigation steps should show route, not ENQUEUED
            if step_state == "IN_PROGRESS" and step.get("type") == "NAVIGATION":
                current_nav_step = step
                break
    
    if current_nav_step:
        # Compute route for FTS navigation
        try:
            config_loader = get_ccu_config_loader()
            layout_config = config_loader.load_shopfloor_layout()
            
            source = current_nav_step.get("source")
            target = current_nav_step.get("target")
            
            if source and target and layout_config:
                route_points = get_route_for_navigation_step(layout_config, source, target, cell_size=200)
                
                # Calculate AGV progress (for demo, use 50% if IN_PROGRESS)
                if step_state == "IN_PROGRESS":
                    agv_progress = 0.5
                elif step_state == "ENQUEUED":
                    agv_progress = 0.1
                    
        except Exception as e:
            logger.warning(f"Could not compute route: {e}")

    if active_module:
        if active_module == "FTS":
            st.info(
                f"🚗 **FTS Navigation aktiv:** {active_intersections[0] if active_intersections else 'Unknown'} → {active_intersections[1] if len(active_intersections) > 1 else 'Unknown'}"
            )
        else:
            st.info(f"🔵 **Active Module:** {active_module}")
    else:
        # Alle Steps abgeschlossen
        st.success("✅ **Alle Storage Steps abgeschlossen**")

    # Shopfloor Layout mit aktiver Modul-Hervorhebung und AGV-Route (linksbündig)
    with st.container():
        # Linksbündige Ausrichtung des Shopfloor Layouts
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        # Eindeutiger Schlüssel je Auftrag und Zustand, um Key-Kollisionen zu vermeiden
        order_id_short = (order.get("orderId", "N/A") or "N/A")[:8]
        show_shopfloor_layout(
            active_module_id=active_module,
            active_intersections=active_intersections,
            show_controls=False,
            unique_key=f"storage_orders_shopfloor_{order_id_short}_{active_module}_{len(active_intersections) if active_intersections else 0}",
            mode="view_mode",  # View mode: only show active modules, no clicks
            route_points=route_points,
            agv_progress=agv_progress,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def _get_current_active_module(storage_plan):
    """Ermittelt das aktuell aktive Modul aus Storage Plan (exakt wie Production Orders)

    Args:
        storage_plan: Liste der Storage Steps

    Returns:
        str: Aktuell aktives Modul (z.B. 'HBW', 'DRILL', 'FTS') oder None
    """
    if not storage_plan:
        return None

    # Suche den ersten nicht-FINISHED Step
    for step in storage_plan:
        state = step.get("state", "PENDING")
        step_type = step.get("type", "")

        if state in ["IN_PROGRESS", "ENQUEUED"]:
            if step_type == "NAVIGATION":
                return "FTS"  # FTS ist für Navigation verantwortlich
            elif step_type == "MANUFACTURE":
                module_type = step.get("moduleType", "")
                if module_type in ["HBW", "MILL", "DRILL", "AIQS", "DPS"]:
                    return module_type

    return None


def _get_active_intersections(storage_plan):
    """Ermittelt aktive Intersections für FTS Navigation (exakt wie Production Orders)

    Args:
        storage_plan: Liste der Storage Steps

    Returns:
        list: Liste der aktiven Intersections [source, target] oder []
    """
    if not storage_plan:
        return []

    # Suche den ersten IN_PROGRESS Navigation Step
    for step in storage_plan:
        state = step.get("state", "PENDING")
        step_type = step.get("type", "")

        if state == "IN_PROGRESS" and step_type == "NAVIGATION":
            source = step.get("source", "")
            target = step.get("target", "")
            return [source, target] if source and target else []

    # Falls kein IN_PROGRESS Navigation Step, suche ENQUEUED
    for step in storage_plan:
        state = step.get("state", "PENDING")
        step_type = step.get("type", "")

        if state == "ENQUEUED" and step_type == "NAVIGATION":
            source = step.get("source", "")
            target = step.get("target", "")
            return [source, target] if source and target else []

    return []


def _render_storage_steps(storage_plan, i18n, is_completed=False):
    """Render Storage Steps

    Args:
        storage_plan: List of storage steps
        i18n: I18nManager Instanz
        is_completed: True für completed orders (ausgegraut)
    """
    for idx, step in enumerate(storage_plan, 1):
        step_state = step.get("state", "PENDING")
        step_type = step.get("type", "N/A")

        # Status-Icons (KONSISTENT mit production_orders_subtab.py _render_production_step_status)
        status_icon = {
            # Aktive Zustände
            "IN_PROGRESS": UISymbols.get_status_icon("step_in_progress"),  # 🟠 (ORANGE CIRCLE - konsistent!)
            "RUNNING": UISymbols.get_status_icon("step_in_progress"),  # 🟠 (Alias)
            # Abgeschlossene Zustände
            "FINISHED": UISymbols.get_status_icon("step_finished"),  # ✅
            "COMPLETED": UISymbols.get_status_icon("step_finished"),  # ✅ (Alias)
            # Wartende Zustände
            "ENQUEUED": UISymbols.get_status_icon("step_enqueued"),  # ⏳
            "PENDING": UISymbols.get_status_icon("step_pending"),  # ⚪
            # Fehler-Zustände
            "FAILED": UISymbols.get_status_icon("step_failed"),  # ❌
        }.get(step_state, "⚪")

        # Station-Icons basierend auf moduleType/source/target (EXAKT wie production_orders_subtab.py)
        module_type = step.get("moduleType", "")
        source = step.get("source", "")
        target = step.get("target", "")

        # NEU: Module-Icons über vorhandene Funktion holen
        from omf2.ui.ccu.ccu_process.ccu_production_plan_subtab import _get_module_icon

        # Bestimme Station-Icon über vorhandene Funktion
        station_icon = _get_module_icon("FTS")  # FTS/AGV Icon für Transport
        if step_type == "NAVIGATION":
            # Bei NAVIGATION: FTS/AGV Icon verwenden
            station_icon = _get_module_icon("FTS") or "🚗"
        elif step_type == "MANUFACTURE":
            # Bei MANUFACTURE: Modul-Icon verwenden
            station_icon = _get_module_icon(module_type) or "🛠️"

        # Step-Beschreibung (EXAKT wie production_orders_subtab.py)
        if step_type == "NAVIGATION":
            step_desc = i18n.t("ccu_orders.steps.automated_guided_vehicle")
            if source != target:
                target_icon = _get_module_icon(target) or "🏭"
                step_desc += f" > {target_icon} {target}"
        elif step_type == "MANUFACTURE":
            command = step.get("command", "")
            if command == "PICK":  # Storage Orders: PICK = Werkstück aus Modul entnehmen = ENTLADEN AGV
                step_desc = f"{module_type} : {i18n.t('ccu_orders.steps.unload_agv')}"
            elif command == "DROP":  # Storage Orders: DROP = Werkstück in Modul einlagern = LADEN AGV
                step_desc = f"{module_type} : {i18n.t('ccu_orders.steps.load_agv')}"
            else:
                step_desc = f"{module_type} : {command}"
        else:
            step_desc = step.get("description", f"Step {idx}")

        # Anzeige (EXAKT wie production_orders_subtab.py)
        # SOLL Format: Step n, [Status Icon] [Station Icon] [Step-description]
        step_info = f"**Step {idx}:** {status_icon} {station_icon} {step_desc}"

        # Einfache Darstellung ohne zusätzliche Status-Wörter
        st.markdown(step_info)


def _render_production_steps(production_plan, i18n, is_completed=False):
    """Render Production Steps

    Args:
        production_plan: List of production steps
        i18n: I18nManager Instanz
        is_completed: True für completed orders (ausgegraut)
    """
    for _idx, step in enumerate(production_plan, 1):
        step_state = step.get("state", "PENDING")
        step_type = step.get("type", "N/A")

        # Status-Icons (KONSISTENT mit production_orders_subtab.py)
        status_icon = {
            # Aktive Zustände
            "IN_PROGRESS": UISymbols.get_status_icon("step_in_progress"),  # 🟠 (ORANGE CIRCLE - konsistent!)
            "RUNNING": UISymbols.get_status_icon("step_in_progress"),  # 🟠 (Alias)
            # Abgeschlossene Zustände
            "FINISHED": UISymbols.get_status_icon("step_finished"),  # ✅
            "COMPLETED": UISymbols.get_status_icon("step_finished"),  # ✅ (Alias)
            # Wartende Zustände
            "ENQUEUED": UISymbols.get_status_icon("step_enqueued"),  # ⏳
            "PENDING": UISymbols.get_status_icon("step_pending"),  # ⚪
            # Fehler-Zustände
            "FAILED": UISymbols.get_status_icon("step_failed"),  # ❌
        }.get(step_state, "⚪")

        # Station-Icons basierend auf moduleType/source/target (EXAKT wie production_orders_subtab.py)
        module_type = step.get("moduleType", "")
        source = step.get("source", "")
        target = step.get("target", "")

        # NEU: Module-Icons über vorhandene Funktion holen
        from omf2.ui.ccu.ccu_process.ccu_production_plan_subtab import _get_module_icon

        # Bestimme Station-Icon über vorhandene Funktion
        station_icon = _get_module_icon("FTS")  # FTS/AGV Icon für Transport
        if step_type == "NAVIGATION":
            # Bei NAVIGATION: FTS/AGV Icon verwenden
            station_icon = _get_module_icon("FTS") or "🚗"
        elif step_type == "MANUFACTURE":
            # Bei MANUFACTURE: Modul-Icon verwenden
            station_icon = _get_module_icon(module_type) or "🛠️"

        # Step-Beschreibung
        if step_type == "NAVIGATION":
            step_desc = i18n.t("ccu_orders.steps.automated_guided_vehicle")
            if source != target:
                target_icon = _get_module_icon(target) or "🏭"
                step_desc += f" > {target_icon} {target}"
        elif step_type == "MANUFACTURE":
            command = step.get("command", "")
            if command == "PICK":  # Storage Orders: PICK = Werkstück aus Modul entnehmen = ENTLADEN AGV
                step_desc = f"{module_type} : {i18n.t('ccu_orders.steps.unload_agv')}"
            elif command == "DROP":  # Storage Orders: DROP = Werkstück in Modul einlagern = LADEN AGV
                step_desc = f"{module_type} : {i18n.t('ccu_orders.steps.load_agv')}"
            else:
                step_desc = f"{module_type} : {command}"
        else:
            step_desc = f"{step_type}"

        # Anzeige
        st.write(f"{station_icon} {status_icon} {step_desc}")
