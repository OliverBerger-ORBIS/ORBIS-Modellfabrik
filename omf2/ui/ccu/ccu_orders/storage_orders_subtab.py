#!/usr/bin/env python3
"""
Storage Orders Subtab - Only STORAGE orderType
"""

import streamlit as st

from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

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

        # DEBUG: Log all orders before filtering
        logger.info(f"📦 BEFORE FILTER: {len(all_active)} active orders, {len(all_completed)} completed orders")
        for order in all_active:
            order_id = order.get("orderId", "N/A")[:8]
            order_type = order.get("orderType", "N/A")
            logger.info(f"  - Active Order {order_id}: orderType={order_type}")

        # Filter: Nur STORAGE Orders
        active_orders = [o for o in all_active if o.get("orderType") == "STORAGE"]
        completed_orders = [o for o in all_completed if o.get("orderType") == "STORAGE"]

        # DEBUG: Log filtered results
        logger.info(f"📦 AFTER FILTER: {len(active_orders)} STORAGE active, {len(completed_orders)} STORAGE completed")
        for order in active_orders:
            order_id = order.get("orderId", "N/A")[:8]
            state = order.get("state", "N/A")
            logger.info(f"  - STORAGE Order {order_id}: state={state}")

        # Store in session state
        st.session_state["storage_orders_active"] = active_orders
        st.session_state["storage_orders_completed"] = completed_orders

        logger.debug(f"✅ Loaded {len(active_orders)} active and {len(completed_orders)} completed storage orders")

    except Exception as e:
        logger.error(f"❌ Error in reload_storage_orders(): {e}")
        # Set empty lists on error to prevent UI crashes
        st.session_state["storage_orders_active"] = []
        st.session_state["storage_orders_completed"] = []


def show_storage_orders_subtab(i18n):
    """Render Storage Orders Subtab (nur orderType: STORAGE)"""
    logger.info("📝 Rendering Storage Orders Subtab")

    try:
        # Use production_orders_refresh_helper for consistent auto-refresh
        from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload

        # Use order_updates refresh group with polling + compare
        check_and_reload(group="order_updates", reload_callback=reload_storage_orders, interval_ms=1000)

        # Get data from session state (populated by reload_storage_orders callback)
        # If not yet populated OR if empty, load it now
        if "storage_orders_active" not in st.session_state:
            logger.info("🔄 storage_orders_active not in session state, calling reload_storage_orders()")
            reload_storage_orders()
        elif not st.session_state.get("storage_orders_active") and not st.session_state.get("storage_orders_completed"):
            # Session state exists but is empty - reload to get fresh data
            logger.info("🔄 storage_orders are empty in session state, calling reload_storage_orders()")
            reload_storage_orders()

        active_orders = st.session_state.get("storage_orders_active", [])
        completed_orders = st.session_state.get("storage_orders_completed", [])

        # DEBUG: Log what we're about to render
        logger.info(f"📦 RENDERING: {len(active_orders)} active STORAGE orders, {len(completed_orders)} completed")
        for order in active_orders:
            order_id = order.get("orderId", "N/A")[:8]
            logger.info(f"  - Rendering active STORAGE order {order_id}")

        try:
            from omf2.assets.heading_icons import get_svg_inline

            icon = get_svg_inline("STORAGE_ORDERS", size_px=32) or ""
            st.markdown(
                f"<h3 style='display:flex; align-items:center; gap:8px;'>{icon} {i18n.t('ccu_orders.storage.title')}</h3>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown(f"### {i18n.t('ccu_orders.storage.title')}")
        # Subtitle removed (orderType notice)

        # Business Logic über OrderManager (for operations)
        order_manager = get_order_manager()

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
    # DEBUG: Log that we're rendering this card
    order_id = order.get("orderId", "N/A")[:8]  # Kurze ID
    logger.info(f"🎴 Rendering order card for STORAGE order {order_id}, is_completed={is_completed}")

    # Order Header für Expander
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
        expander_label = f"{workpiece_icon} **{order_id}...** - {workpiece_type} - {state_icon} {i18n.t('ccu_orders.status.completed')}"
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

    # Gesamte Order Card in Expander (Storage Steps + Shopfloor zusammen)
    with st.expander(expander_label, expanded=expanded):
        # Zwei-Spalten-Layout (1:2 - Storage Steps:Shopfloor)
        col1, col2 = st.columns([1, 2])

        with col1:
            # Links: Order-Details und Storage Steps (immer sichtbar, nicht collapsible)
            _render_order_details(order, order_manager, i18n, is_completed)

        with col2:
            # Rechts: Shopfloor Layout (nur für aktive Orders)
            if not is_completed:
                _render_shopfloor_for_storage_order(order, order_manager, i18n)
            else:
                st.info(f"🏁 {i18n.t('ccu_orders.info.order_completed_no_shopfloor')}")


def _render_order_details(order, order_manager, i18n, is_completed=False):
    """Render Order-Details (links Spalte)"""
    # Order Info
    order_type = order.get("orderType", "N/A")
    try:
        from omf2.assets.heading_icons import get_svg_inline

        order_heading_icon = get_svg_inline("STORAGE_ORDERS", size_px=18) or ""
        st.markdown(f"{order_heading_icon} <strong>{order_type}</strong>", unsafe_allow_html=True)
    except Exception:
        st.write(f"📦 {order_type}")

    # Full ID line
    order_id = order.get("orderId", "N/A")
    st.write(f"ID: {order_id}")

    st.markdown("---")

    # Storage Steps (immer sichtbar, nicht collapsible)
    complete_storage_plan = order_manager.get_complete_storage_plan(order)
    if complete_storage_plan:
        # Plain heading (icon nur bei STORAGE oben)
        steps_label = f"**{i18n.t('ccu_orders.card.storage_steps')}** ({len(complete_storage_plan)})"
        st.markdown(steps_label)
        _render_storage_steps(complete_storage_plan, i18n, is_completed)


def _render_shopfloor_for_storage_order(order, order_manager, i18n):
    """Zeigt Shopfloor Layout mit aktiver Modul-Hervorhebung und AGV-Route für Storage Orders"""
    from omf2.ccu.config_loader import get_ccu_config_loader
    from omf2.ui.ccu.common.route_utils import get_route_for_navigation_step
    from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

    # Heading removed per requirement

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
            order_type = order.get("orderType")  # Get order type for route calculation

            if source and target and layout_config:
                route_points = get_route_for_navigation_step(
                    layout_config, source, target, cell_size=200, order_type=order_type
                )

                # Calculate AGV progress (for demo, use 50% if IN_PROGRESS)
                if step_state == "IN_PROGRESS":
                    agv_progress = 0.5
                elif step_state == "ENQUEUED":
                    agv_progress = 0.1

        except Exception as e:
            logger.warning(f"Could not compute route: {e}")

    if active_module:
        if active_module == "FTS":
            try:
                from omf2.ui.common.symbols import get_icon_html

                src = active_intersections[0] if active_intersections else "?"
                dst = active_intersections[1] if len(active_intersections) > 1 else "?"
                fts = get_icon_html("FTS", size_px=18)
                src_icon = get_icon_html(src, size_px=18)
                dst_icon = get_icon_html(dst, size_px=18)

                info_html = f"""
                <div style="background:#fff3e0; border-left:4px solid #ff9800; padding:10px 12px; border-radius:6px;">
                  <div style="display:flex; align-items:center; gap:8px; font-weight:600; color:#1f1f1f;">
                    <span>{fts}</span>
                    <span>{i18n.t('ccu_orders.info.fts_navigation_active')}</span>
                    <span style=\"display:inline-flex; align-items:center; gap:6px;\">{src_icon} <span>{src}</span>
                      <span style=\"margin:0 6px;\">→</span>
                      {dst_icon} <span>{dst}</span>
                    </span>
                  </div>
                </div>
                """
                st.markdown(info_html, unsafe_allow_html=True)
            except Exception:
                st.markdown(
                    f"<div style='background:#fff3e0; border-left:4px solid #ff9800; padding:10px 12px; border-radius:6px;'>🚗 <strong>FTS Navigation aktiv:</strong> {active_intersections[0] if active_intersections else 'Unknown'} → {active_intersections[1] if len(active_intersections) > 1 else 'Unknown'}</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info(f"🔵 **{i18n.t('ccu_orders.info.active_module')}** {active_module}")
    else:
        # Alle Steps abgeschlossen
        st.success(f"✅ **{i18n.t('ccu_orders.status.all_storage_steps_completed')}**")

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
    """Render Storage Steps (SVG + Label Layout, konsistent mit Production)."""

    # Helper for SVG icons
    def _svg_icon_for_type(module_type: str, size_px: int = 20) -> str:
        try:
            from omf2.ui.common.symbols import get_icon_html

            return get_icon_html(module_type, size_px=size_px)
        except Exception:
            return ""

    for idx, step in enumerate(storage_plan, 1):
        step_state = step.get("state", "PENDING")
        step_type = step.get("type", "N/A")

        status_icon = {
            "IN_PROGRESS": UISymbols.get_status_icon("step_in_progress"),
            "RUNNING": UISymbols.get_status_icon("step_in_progress"),
            "FINISHED": UISymbols.get_status_icon("step_finished"),
            "COMPLETED": UISymbols.get_status_icon("step_finished"),
            "ENQUEUED": UISymbols.get_status_icon("step_enqueued"),
            "PENDING": UISymbols.get_status_icon("step_pending"),
            "FAILED": UISymbols.get_status_icon("step_failed"),
        }.get(step_state, "⚪")

        module_type = step.get("moduleType", "")
        target = step.get("target", "")

        # Build icon area
        station_icon_svg = _svg_icon_for_type("FTS")
        if step_type == "NAVIGATION":
            try:
                from omf2.ui.common.symbols import get_icon_html

                fts_svg = get_icon_html("FTS", size_px=20)
                target_svg = get_icon_html(target, size_px=20) if target else ""
                station_icon_svg = (
                    f'{fts_svg} <span style="margin-right:6px;">FTS</span>'
                    f'<span style="margin:0 6px;">→</span>'
                    f"{target_svg} <span>{target or ''}</span>"
                )
            except Exception:
                station_icon_svg = _svg_icon_for_type("FTS") or ""
        elif step_type == "MANUFACTURE":
            station_icon_svg = _svg_icon_for_type(module_type) or ""

        # Text area
        if step_type == "NAVIGATION":
            step_desc = ""
        elif step_type == "MANUFACTURE":
            command = step.get("command", "")
            try:
                from omf2.ui.common.symbols import get_icon_html

                fts_svg = get_icon_html("FTS", size_px=20)
            except Exception:
                fts_svg = "FTS"
            if command == "PICK":
                step_desc = f"{module_type} : PICK {fts_svg} FTS"
            elif command == "DROP":
                step_desc = f"{module_type} : DROP {fts_svg} FTS"
            else:
                step_desc = f"{module_type} : {command}"
        else:
            step_desc = f"{step_type}"

        # Render row
        station_part = station_icon_svg if station_icon_svg else ""
        step_label = i18n.t("ccu_orders.labels.step", index=idx)
        html = (
            f'<div style="display:flex; align-items:center; gap: 8px; margin-bottom: 12px;">'
            f'<span style="min-width: 64px; color:#666;"><strong>{step_label}</strong></span>'
            f'<span style="min-width: 22px; text-align:center;">{status_icon}</span>'
            f'<span style="min-width: 26px; margin-left: 1em; display:inline-block;">{station_part}</span>'
            f"<span>{step_desc}</span>"
            f"</div>"
        )
        st.markdown(html, unsafe_allow_html=True)

    # (removed unused duplicate renderer)
