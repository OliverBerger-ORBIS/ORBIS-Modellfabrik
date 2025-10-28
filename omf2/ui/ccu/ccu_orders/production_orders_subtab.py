#!/usr/bin/env python3
"""
Production Orders Subtab - Only PRODUCTION orderType
"""

import streamlit as st

from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def reload_orders():
    """
    Reload production orders data into session state

    This wrapper function loads orders from OrderManager and stores them
    in session state for use by the UI rendering logic.
    """
    try:
        logger.debug("🔄 reload_orders() called - loading fresh data")
        order_manager = get_order_manager()

        # Load fresh data
        all_active = order_manager.get_active_orders()
        all_completed = order_manager.get_completed_orders()

        # Filter: Nur PRODUCTION Orders
        active_orders = [o for o in all_active if o.get("orderType") == "PRODUCTION"]
        completed_orders = [o for o in all_completed if o.get("orderType") == "PRODUCTION"]

        # Store in session state
        st.session_state["production_orders_active"] = active_orders
        st.session_state["production_orders_completed"] = completed_orders

        logger.debug(f"✅ Loaded {len(active_orders)} active and {len(completed_orders)} completed production orders")

    except Exception as e:
        logger.error(f"❌ Error in reload_orders(): {e}")
        # Set empty lists on error to prevent UI crashes
        st.session_state["production_orders_active"] = []
        st.session_state["production_orders_completed"] = []


def show_production_orders_subtab(i18n):
    """Render Production Orders Subtab (nur orderType: PRODUCTION)"""
    logger.info("📝 Rendering Production Orders Subtab")

    try:
        # NEW: Optional MQTT UI refresh integration (opt-in via configuration)
        try:
            from omf2.ui.components.mqtt_subscriber import (
                get_mqtt_ws_url,
                is_mqtt_ui_enabled,
                mqtt_subscriber_component,
            )

            mqtt_ws_url = get_mqtt_ws_url()

            if mqtt_ws_url and is_mqtt_ui_enabled():
                # MQTT UI refresh is enabled
                logger.debug("🔌 MQTT UI refresh enabled for production orders")

                # Subscribe to MQTT refresh topic
                mqtt_message = mqtt_subscriber_component(
                    broker_url=mqtt_ws_url,
                    topic="omf2/ui/refresh/order_updates",
                    key="ui_mqtt_production_orders",
                )

                # If we received a message, trigger reload
                if mqtt_message:
                    logger.debug(f"📨 MQTT refresh message received: {mqtt_message}")
                    reload_orders()

        except Exception as mqtt_error:
            logger.debug(f"⚠️ MQTT UI component not available or error: {mqtt_error}")

        # FALLBACK: Use production_orders_refresh_helper for robust polling + compare
        check_and_reload(group="order_updates", reload_callback=reload_orders, interval_ms=1000)

        # Get data from session state (populated by reload_orders callback)
        # If not yet populated, load it now
        if "production_orders_active" not in st.session_state:
            reload_orders()

        active_orders = st.session_state.get("production_orders_active", [])
        completed_orders = st.session_state.get("production_orders_completed", [])

        # Get order_manager for rendering operations
        order_manager = get_order_manager()

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
    # Order Header für Expander
    order_id = order.get("orderId", "N/A")[:8]  # Kurze ID
    workpiece_type = order.get("type", "N/A")
    workpiece_icon = UISymbols.get_workpiece_icon(workpiece_type)
    state = order.get("state", "N/A")

    # Compute expanded flag based on order completion state
    is_order_completed = False
    try:
        status = order.get("status") if isinstance(order, dict) else getattr(order, "status", None)
        if status == "COMPLETED":
            is_order_completed = True
        else:
            last_step = None
            steps = order.get("steps") if isinstance(order, dict) else getattr(order, "steps", None)
            if steps:
                last_step = steps[-1]
            last_step_state = None
            if isinstance(last_step, dict):
                last_step_state = last_step.get("state")
            else:
                last_step_state = getattr(last_step, "state", None) if last_step is not None else None
            if last_step_state == "COMPLETED":
                is_order_completed = status == "COMPLETED"
    except Exception:
        is_order_completed = False

    expanded = not is_order_completed

    # Expander label mit Order-Info
    if is_completed:
        state_icon = UISymbols.get_status_icon("success")
        expander_label = f"{workpiece_icon} **{order_id}...** - {workpiece_type} - {state_icon} Completed"
    else:
        state_icon = {
            "IN_PROGRESS": UISymbols.get_status_icon("step_in_progress"),
            "RUNNING": UISymbols.get_status_icon("step_in_progress"),
            "FINISHED": UISymbols.get_status_icon("step_finished"),
            "COMPLETED": UISymbols.get_status_icon("step_finished"),
            "ENQUEUED": UISymbols.get_status_icon("step_enqueued"),
            "PENDING": UISymbols.get_status_icon("step_pending"),
            "FAILED": UISymbols.get_status_icon("step_failed"),
        }.get(state, "⚪")
        expander_label = f"{workpiece_icon} **{order_id}...** - {workpiece_type} - {state_icon} {state}"

    # Gesamte Order Card in Expander (Production Steps + Shopfloor zusammen)
    with st.expander(expander_label, expanded=expanded):
        # Zwei-Spalten-Layout (1:2 - Production Steps:Shopfloor)
        col1, col2 = st.columns([1, 2])

        with col1:
            # Links: Order-Details und Production Steps (immer sichtbar, nicht collapsible)
            _render_order_details(order, order_manager, i18n, is_completed)

        with col2:
            # Rechts: Shopfloor Layout (nur für aktive Orders)
            if not is_completed:
                _render_shopfloor_for_order(order, order_manager, i18n)
            else:
                st.info("🏁 Order completed - no active shopfloor")


def _render_order_details(order, order_manager, i18n, is_completed=False):
    """Render Order-Details (links Spalte)"""
    # Order Info Row
    col1, col2 = st.columns([1, 1])

    with col1:
        order_type = order.get("orderType", "N/A")
        order_icon = UISymbols.get_tab_icon("production_plan")
        st.write(f"{order_icon} {order_type}")

    with col2:
        order_id = order.get("orderId", "N/A")
        st.write(f"ID: {order_id[:16]}...")

    st.markdown("---")

    # Production Steps (immer sichtbar, nicht collapsible)
    complete_production_plan = order_manager.get_complete_production_plan(order)
    if complete_production_plan:
        steps_label = f"**{i18n.t('ccu_orders.card.production_steps')}** ({len(complete_production_plan)})"
        st.markdown(steps_label)
        _render_production_steps(complete_production_plan, i18n, is_completed)


def _render_shopfloor_for_order(order, order_manager, i18n):
    """Zeigt Shopfloor Layout mit aktiver Modul-Hervorhebung und AGV-Route (rechts Spalte)"""
    from omf2.ccu.config_loader import get_ccu_config_loader
    from omf2.ui.ccu.common.route_utils import get_route_for_navigation_step
    from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

    st.markdown("#### 🗺️ Shopfloor Layout")

    # Aktuelles Modul aus Production Plan ermitteln
    production_plan = order_manager.get_complete_production_plan(order)
    active_module = _get_current_active_module(production_plan)
    active_intersections = _get_active_intersections(production_plan)

    # AGV Route berechnen NUR wenn FTS Navigation der AKTIVE Step ist
    # FIX: Nur Route zeigen wenn active_module == "FTS", nicht bei anderen Modulen
    route_points = None
    agv_progress = 0.0
    current_nav_step = None

    # Find current navigation step - but only show route if it's the ACTIVE step
    if active_module == "FTS":
        for step in production_plan:
            step_state = step.get("state", "PENDING")
            # Only IN_PROGRESS or RUNNING navigation steps should show route
            if step_state in ["IN_PROGRESS", "RUNNING"] and step.get("type") == "NAVIGATION":
                current_nav_step = step
                break

    if current_nav_step:
        # Compute route for FTS navigation
        try:
            config_loader = get_ccu_config_loader()
            layout_config = config_loader.load_shopfloor_layout()

            source = current_nav_step.get("source")
            target = current_nav_step.get("target")
            order_type = order.get("orderType")  # Get order type for route calculation

            if source and target and layout_config:
                route_points = get_route_for_navigation_step(
                    layout_config, source, target, cell_size=200, order_type=order_type
                )

                # Calculate AGV progress (for demo, use 50% if IN_PROGRESS)
                if step_state == "IN_PROGRESS":
                    agv_progress = 0.5
                elif step_state == "RUNNING":
                    agv_progress = 0.3

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
        st.success("✅ **Alle Production Steps abgeschlossen**")

    # Shopfloor Layout mit aktiver Modul-Hervorhebung und AGV-Route (linksbündig)
    with st.container():
        # Linksbündige Ausrichtung des Shopfloor Layouts
        st.markdown("<div style='text-align: left;'>", unsafe_allow_html=True)
        show_shopfloor_layout(
            active_module_id=active_module,
            active_intersections=active_intersections,
            show_controls=False,
            unique_key=f"production_orders_shopfloor_{active_module}_{len(active_intersections) if active_intersections else 0}",
            mode="view_mode",  # View mode: only show active modules, no clicks
            route_points=route_points,
            agv_progress=agv_progress,
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
        # SOLL Format: Step n, [Status Icon] [Station Icon] [Station Name] [Step-description]
        step_info = f"**Step {idx}:** {status_icon} {station_icon} {step_desc}"

        # Einfache Darstellung ohne zusätzliche Status-Wörter
        st.markdown(step_info)
