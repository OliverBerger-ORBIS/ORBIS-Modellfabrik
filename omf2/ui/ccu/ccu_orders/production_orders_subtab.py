#!/usr/bin/env python3
"""
Production Orders Subtab - Only PRODUCTION orderType
"""

import streamlit as st

from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def show_production_orders_subtab(i18n):
    """Render Production Orders Subtab (nur orderType: PRODUCTION)"""
    logger.info("📝 Rendering Production Orders Subtab")

    try:
        # Business Logic über ProductionOrderManager
        order_manager = get_order_manager()

        # Daten holen
        all_active = order_manager.get_active_orders()
        all_completed = order_manager.get_completed_orders()

        # Filter: Nur PRODUCTION Orders
        active_orders = [o for o in all_active if o.get("orderType") == "PRODUCTION"]
        completed_orders = [o for o in all_completed if o.get("orderType") == "PRODUCTION"]

        st.markdown(f"### {i18n.t('ccu_orders.production.title')}")
        st.markdown(i18n.t("ccu_orders.production.subtitle"))

        # Active Production Orders
        _show_active_orders_section(active_orders, order_manager, i18n)

        # Completed Production Orders
        st.divider()
        _show_completed_orders_section(completed_orders, order_manager, i18n)

    except Exception as e:
        logger.error(f"❌ Production Orders Subtab rendering error: {e}")
        st.error(f"❌ Production Orders Subtab failed: {e}")


def _show_active_orders_section(active_orders, order_manager, i18n):
    """Show Active Production Orders Section"""
    st.markdown(f"#### {i18n.t('ccu_orders.production.active_title')}")

    if active_orders:
        for order in active_orders:
            _render_order_card(order, order_manager, i18n, is_completed=False)
    else:
        st.info(f"{UISymbols.get_status_icon('info')} {i18n.t('ccu_orders.production.no_active')}")


def _show_completed_orders_section(completed_orders, order_manager, i18n):
    """Show Completed Production Orders Section"""
    st.markdown(f"#### {i18n.t('ccu_orders.production.completed_title')}")

    if completed_orders:
        for order in completed_orders:
            _render_order_card(order, order_manager, i18n, is_completed=True)
    else:
        st.info(f"{UISymbols.get_status_icon('info')} {i18n.t('ccu_orders.production.no_completed')}")


def _render_order_card(order, order_manager, i18n, is_completed=False):
    """Render einzelne Order Card

    Args:
        order: Order-Dict
        order_manager: OrderManager Instanz
        i18n: I18nManager Instanz
        is_completed: True für completed orders (ausgegraut)
    """
    with st.container():
        # NEU: Zwei-Spalten-Layout (1:2 - Liste:Shopfloor)
        col1, col2 = st.columns([1, 2])

        with col1:
            # Links: Order-Details und Production Steps
            _render_order_details(order, order_manager, i18n, is_completed)

        with col2:
            # Rechts: Shopfloor Layout (nur für aktive Orders)
            if not is_completed:
                _render_shopfloor_for_order(order, order_manager, i18n)
            else:
                st.info("🏁 Order completed - no active shopfloor")


def _render_order_details(order, order_manager, i18n, is_completed=False):
    """Render Order-Details (links Spalte)"""
    # Order Header
    order_id = order.get("orderId", "N/A")[:8]  # Kurze ID
    if is_completed:
        st.markdown(f"~~**{order_id}...**~~")
    else:
        st.write(f"**{order_id}...**")

    # Order Info Row
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        workpiece_type = order.get("type", "N/A")
        # NEU: UI-Symbols verwenden
        workpiece_icon = UISymbols.get_workpiece_icon(workpiece_type)
        if is_completed:
            st.markdown(f"~~{workpiece_icon} {workpiece_type}~~")
        else:
            st.write(f"{workpiece_icon} {workpiece_type}")

    with col2:
        order_type = order.get("orderType", "N/A")
        # NEU: UI-Symbols verwenden
        order_icon = UISymbols.get_tab_icon("production_plan")  # 📋 für Production Plan
        if is_completed:
            st.markdown(f"~~{order_icon} {order_type}~~")
        else:
            st.write(f"{order_icon} {order_type}")

    with col3:
        if is_completed:
            # NEU: UI-Symbols verwenden
            st.write(f"{UISymbols.get_status_icon('success')} {i18n.t('ccu_orders.card.completed')}")
        else:
            state = order.get("state", "N/A")
            # NEU: UI-Symbols verwenden - Vollständige Zustands-Matrix
            state_icon = {
                # Aktive Zustände (KONSISTENT mit _render_production_step_status)
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
            }.get(state, "⚪")
            st.write(f"{state_icon} {state}")

        # Production Steps (expandable)
        complete_production_plan = order_manager.get_complete_production_plan(order)
    if complete_production_plan:
        steps_label = f"{i18n.t('ccu_orders.card.production_steps')} ({len(complete_production_plan)})"
        with st.expander(steps_label, expanded=False):
            _render_production_steps(complete_production_plan, i18n, is_completed)


def _render_shopfloor_for_order(order, order_manager, i18n):
    """Zeigt Shopfloor Layout mit aktiver Modul-Hervorhebung (rechts Spalte)"""
    from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

    st.markdown("#### 🗺️ Shopfloor Layout")

    # Aktuelles Modul aus Production Plan ermitteln
    production_plan = order_manager.get_complete_production_plan(order)
    active_module = _get_current_active_module(production_plan)
    active_intersections = _get_active_intersections(production_plan)

    if active_module:
        if active_module == "FTS":
            st.info(
                f"🚗 **FTS Navigation aktiv:** {active_intersections[0] if active_intersections else 'Unknown'} → {active_intersections[1] if len(active_intersections) > 1 else 'Unknown'}"
            )
        else:
            st.info(f"🔵 **Active Module:** {active_module}")
    else:
        # Alle Steps abgeschlossen
        st.success("✅ **Alle Production Steps abgeschlossen**")

    # Shopfloor Layout mit aktiver Modul-Hervorhebung (linksbündig)
    with st.container():
        # Linksbündige Ausrichtung des Shopfloor Layouts
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        show_shopfloor_layout(
            active_module_id=active_module,
            active_intersections=active_intersections,
            show_controls=False,
            unique_key="production_orders_shopfloor",
            mode="view_mode",  # View mode: only show active modules, no clicks
        )
        st.markdown("</div>", unsafe_allow_html=True)


def _get_current_active_module(production_plan):
    """Ermittelt das aktuell aktive Modul aus Production Plan

    Logik (original - funktionierend):
    - Finde das erste PENDING/IN_PROGRESS Modul als aktives Modul
    - FINISHED = abgeschlossen = NICHT mehr aktiv
    - PENDING = wartend = NÄCHSTES aktives Modul
    """
    active_module = None

    # Finde das erste nicht-FINISHED Modul (wie Original)
    for idx, step in enumerate(production_plan):
        step_state = step.get("state", "PENDING")
        step_type = step.get("type", "")

        # Ersten nicht-FINISHED Step finden
        if step_state != "FINISHED":
            if step_type == "NAVIGATION":
                # FTS Navigation: Zeige FTS als aktiv
                active_module = "FTS"
                logger.debug(f"🚗 FTS Navigation aktiv (Step {idx + 1}): {step.get('source')} → {step.get('target')}")
            elif step_type == "MANUFACTURE":
                # Manufacture Step: Zeige Modul als aktiv
                active_module = step.get("moduleType") or step.get("target") or step.get("source")
                logger.debug(f"🏭 Manufacture aktiv (Step {idx + 1}): {active_module} - {step.get('command')}")

            # Erstes nicht-FINISHED Modul gefunden
            break
    logger.info(f"🔍 DEBUG: Aktives Modul: {active_module}")
    return active_module


def _get_active_intersections(production_plan):
    """Ermittelt aktive Intersections für FTS Navigation"""
    active_intersections = []

    for step in production_plan:
        step_state = step.get("state", "PENDING")

        # FTS Navigation Steps die IN_PROGRESS oder PENDING sind
        if step_state in ["IN_PROGRESS", "RUNNING", "PENDING"] and step.get("type") == "NAVIGATION":
            # FTS Navigation aktiv: Markiere Source und Target als Intersections
            source = step.get("source")
            target = step.get("target")

            if source and source != "FTS":
                active_intersections.append(source)
            if target and target != "FTS":
                active_intersections.append(target)

    return active_intersections


def _render_production_steps(production_plan, i18n, is_completed=False):
    """Render Production Steps

    Args:
        production_plan: List of production steps
        i18n: I18nManager Instanz
        is_completed: True für completed orders (ausgegraut)
    """
    for idx, step in enumerate(production_plan, 1):
        step_state = step.get("state", "PENDING")
        step_type = step.get("type", "N/A")

        # Status-Icons - Production Process Step Icons (neue spezifische Icons)
        status_icon = {
            # Abgeschlossene Zustände
            "FINISHED": UISymbols.get_status_icon("step_finished"),  # ✅
            "COMPLETED": UISymbols.get_status_icon("step_finished"),  # ✅ (Alias)
            # Aktive Zustände
            "IN_PROGRESS": UISymbols.get_status_icon("step_in_progress"),  # 🟠 (ORANGE CIRCLE - wie aktive Station)
            "RUNNING": UISymbols.get_status_icon("step_in_progress"),  # 🟠 (Alias)
            # Wartende Zustände
            "ENQUEUED": UISymbols.get_status_icon("step_enqueued"),  # ⏳
            "PENDING": UISymbols.get_status_icon("step_pending"),  # ⚪
            # Fehler-Zustände
            "FAILED": UISymbols.get_status_icon("step_failed"),  # ❌
        }.get(step_state, "⚪")

        # Station-Icons basierend auf moduleType/source/target
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
            if command == "LOAD":
                step_desc = f"{module_type} : {i18n.t('ccu_orders.steps.load_agv')}"
            elif command == "UNLOAD":
                step_desc = f"{module_type} : {i18n.t('ccu_orders.steps.unload_agv')}"
            else:
                step_desc = f"{module_type} : {command}"
        else:
            step_desc = f"{step_type}"

        # Anzeige mit verbesserter Sequenz-Visualisierung
        if is_completed:
            st.markdown(f"~~{station_icon} {status_icon} {step_desc}~~")
        else:
            # SOLL Format: Step n, [Status Icon] [Station Icon] [Station Name] [Step-description]
            step_info = f"**Step {idx}:** {status_icon} {station_icon} {step_desc}"

            # Einfache Darstellung ohne zusätzliche Status-Wörter
            st.markdown(step_info)
