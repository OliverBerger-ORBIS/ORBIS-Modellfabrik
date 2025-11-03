#!/usr/bin/env python3
"""
CCU Process - Production Plan Subtab
Production workflow visualization for BLUE, WHITE, RED products
"""

from typing import Any, Dict, List

import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.common.product_manager import get_omf2_product_manager
from omf2.ui.common.product_rendering import render_product_svg_container
from omf2.ui.common.symbols import UISymbols, get_icon_html
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_ccu_production_plan_subtab():
    """Render CCU Production Plan Subtab - Interactive Workflow Design"""
    logger.info("📋 Rendering CCU Production Plan Subtab")
    try:
        # Ensure i18n manager present (no assignment to avoid linter warnings)
        st.session_state.get("i18n_manager")

        # Top section focuses on Processing Steps; heading style with SVG icon

        # Load production workflows
        config_loader = get_ccu_config_loader()
        workflows = config_loader.load_production_workflows()

        if not workflows:
            st.error(f"{UISymbols.get_status_icon('error')} Failed to load production workflows.")
            logger.error("Production workflows could not be loaded.")
            return

        # Processing Steps (main workflow visualization)
        _show_interactive_workflow_visualization(workflows)

        st.divider()

        # Section 2: Production Plan (dropdown + controls)
        try:
            heading_icon = get_asset_manager().get_asset_inline("PROCESS", size_px=32) or ""
            title_txt = (
                st.session_state.get("i18n_manager").t("ccu_process.sections.production_plan.title")
                if st.session_state.get("i18n_manager")
                else "Production Plan"
            )
            if title_txt == "ccu_process.sections.production_plan.title":
                title_txt = "Production Plan"
            st.markdown(
                f"<h3 style='display:flex; align-items:center; gap:8px;'>{heading_icon} {title_txt}</h3>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.subheader(
                f"{UISymbols.get_tab_icon('production_plan')} "
                f"{st.session_state.get('i18n_manager').t('ccu_process.sections.production_plan.title') if st.session_state.get('i18n_manager') else 'Production Plan'}"
            )
        i18n = st.session_state.get("i18n_manager")
        plan_desc = (
            i18n.t("ccu_process.production_plan.description")
            if i18n
            else "Interactive production workflow planning and management"
        )
        if plan_desc == "ccu_process.production_plan.description":
            plan_desc = "Interactive production workflow planning and management"
        st.markdown(plan_desc)

        # Dropdown: Product selection and step details
        _show_product_processing_details_dropdown(workflows)

        # Controls at the end of the section
        st.divider()
        _show_workflow_controls_section()

    except Exception as e:
        logger.error(f"❌ CCU Production Plan Subtab rendering error: {e}")
        st.error(f"❌ CCU Production Plan Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_workflow_controls_section():
    """Show workflow controls section (Add, Save, Refresh, Toggle)"""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

    i18n = st.session_state.get("i18n_manager")
    add_label = i18n.t("ccu_process.controls.add_step") if i18n else "Add Step"
    save_label = i18n.t("ccu_process.controls.save") if i18n else "Save"
    refresh_label = i18n.t("ccu_process.controls.refresh") if i18n else "Refresh"
    toggle_label = i18n.t("ccu_process.controls.toggle_label") if i18n else "Activate advanced processing steps"
    toggle_on_info = i18n.t("ccu_process.controls.toggle_on_info") if i18n else "Advanced processing mode activated"
    saved_success = i18n.t("ccu_process.controls.saved_success") if i18n else "Workflow saved successfully!"
    refreshed_info = i18n.t("ccu_process.controls.refreshed_info") if i18n else "Workflow refreshed!"

    with col1:
        if st.button(f"{UISymbols.get_status_icon('add')} {add_label}", key="add_workflow_step"):
            st.info("➕ " + add_label)

    with col2:
        if st.button(f"{UISymbols.get_status_icon('save')} {save_label}", key="save_workflow"):
            st.success("💾 " + saved_success)

    with col3:
        if st.button(f"{UISymbols.get_status_icon('refresh')} {refresh_label}", key="refresh_workflow"):
            request_refresh()
            st.info("🔄 " + refreshed_info)

    with col4:
        # Advanced Processing Toggle
        advanced_mode = st.toggle(toggle_label, value=False, key="advanced_processing_toggle")
        if advanced_mode:
            st.info("🔧 " + toggle_on_info)


def _show_interactive_workflow_visualization(workflows: Dict[str, Any]):
    """Show main interactive workflow visualization (like Image 2)"""
    try:
        heading_icon = get_asset_manager().get_asset_inline("PROCESS", size_px=32) or ""
        i18n = st.session_state.get("i18n_manager")
        title_txt = i18n.t("ccu_process.sections.processing_steps.title") if i18n else "Processing Steps"
        if title_txt == "ccu_process.sections.processing_steps.title":
            title_txt = "Processing Steps"
        st.markdown(
            f"<h3 style='display:flex; align-items:center; gap:8px;'>{heading_icon} {title_txt}</h3>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(f"### {UISymbols.get_tab_icon('workflow')} Processing Steps")

    # Unified workflow: Start/End spanning all 3 products
    _show_unified_workflow_section(workflows)


def _show_unified_workflow_section(workflows: Dict[str, Any]):
    """Show unified workflow with Start/End spanning all 3 products"""

    # Start section: show HBW icon (48px) without extra heading text
    from omf2.ui.common.symbols import get_icon_html as _get_icon_html

    hbw_icon = _get_icon_html("HBW", size_px=64)
    i18n = st.session_state.get("i18n_manager")
    retrieve_title = i18n.t("ccu_process.processing.retrieve.title") if i18n else "Retrieve via high-bay warehouse"
    if retrieve_title == "ccu_process.processing.retrieve.title":
        retrieve_title = "Retrieve via high-bay warehouse"
    retrieve_sub = (
        i18n.t("ccu_process.processing.retrieve.subtitle")
        if i18n
        else "Initial material retrieval and staging for all product types"
    )
    if retrieve_sub == "ccu_process.processing.retrieve.subtitle":
        retrieve_sub = "Initial material retrieval and staging for all product types"
    st.markdown(
        f"""
        <div style='text-align: center; padding: 16px; background-color: #e3f2fd; border-radius: 10px; margin: 10px 0;'>
          <div style='margin-bottom:8px;'>{hbw_icon}</div>
          <div style='font-weight:700;'>{retrieve_title}</div>
          <div style='opacity:0.8;'>{retrieve_sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Arrow down (more prominent, same vertical footprint)
    st.markdown(
        "<div style='text-align: center; font-size: 28px; margin: 6px 0;'>⬇️</div>",
        unsafe_allow_html=True,
    )

    # Parallel processing section with 3 product types
    _show_parallel_processing_section(workflows)

    # Arrow down again to emphasize top-to-bottom flow
    st.markdown(
        "<div style='text-align: center; font-size: 28px; margin: 6px 0;'>⬇️</div>",
        unsafe_allow_html=True,
    )

    # End section: show DPS icon (48px) without extra heading text
    dps_icon = _get_icon_html("DPS", size_px=64)
    dps_sq1 = _get_icon_html("DPS_SQUARE1", size_px=64)
    dps_sq2 = _get_icon_html("DPS_SQUARE2", size_px=64)
    delivery_title = i18n.t("ccu_process.processing.delivery.title") if i18n else "Delivery via Goods Outgoing"
    if delivery_title == "ccu_process.processing.delivery.title":
        delivery_title = "Delivery via Goods Outgoing"
    delivery_sub = (
        i18n.t("ccu_process.processing.delivery.subtitle")
        if i18n
        else "Final product delivery and dispatch for all product types"
    )
    if delivery_sub == "ccu_process.processing.delivery.subtitle":
        delivery_sub = "Final product delivery and dispatch for all product types"
    st.markdown(
        f"""
        <div style='text-align: center; padding: 16px; background-color: #e8f5e8; border-radius: 10px; margin: 10px 0;'>
          <div style='margin-bottom:8px; display:flex; gap:12px; align-items:center; justify-content:center;'>
            {dps_icon}{dps_sq1}{dps_sq2}
          </div>
          <div style='font-weight:700;'>{delivery_title}</div>
          <div style='opacity:0.8;'>{delivery_sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _show_parallel_processing_section(workflows: Dict[str, Any]):
    """Show parallel processing section with 3 product cards"""
    # No section heading; compact layout per specification

    # Create 3 columns for Blue, Red, White products
    col1, col2, col3 = st.columns(3)

    products = ["BLUE", "WHITE", "RED"]
    product_bg_colors = {"BLUE": "#e3f2fd", "RED": "#ffebee", "WHITE": "#f5f5f5"}

    cols = [col1, col2, col3]

    for _i, (product, col) in enumerate(zip(products, cols)):
        with col:
            # Product card
            workflow = workflows.get(product, {})
            steps = workflow.get("steps", [])

            # Card header with workpiece product SVG (3D/product view)
            asset_mgr = get_asset_manager()
            # 64px Zielgröße ≈ 200 * 0.32
            svg_3d_raw = asset_mgr.get_workpiece_svg(product, "3dim")
            svg_prod_raw = asset_mgr.get_workpiece_svg(product, "product")
            product_svg_3d = render_product_svg_container(svg_3d_raw, scale=0.32) if svg_3d_raw else None
            product_svg = render_product_svg_container(svg_prod_raw, scale=0.32) if svg_prod_raw else None
            if not svg_3d_raw:
                st.warning(f"{product.lower()}_3dim.svg nicht gefunden – bitte Asset prüfen.")
            if not svg_prod_raw:
                st.warning(f"{product.lower()}_product.svg nicht gefunden – bitte Asset prüfen.")
            _i18n = st.session_state.get("i18n_manager")
            steps_count = (
                _i18n.t("ccu_process.processing.steps_count", count=len(steps))
                if _i18n
                else f"{len(steps)} Processing Steps"
            )
            st.markdown(
                f"""
            <div style="padding: 20px; background-color: {product_bg_colors[product]}; border-radius: 10px; margin: 10px 0; text-align:center;">
                <div style="display:inline-flex; align-items:flex-start; gap:12px; justify-content:center;">
                    <div style="background:#fff; border-radius:6px; padding:4px;">{product_svg_3d or ''}</div>
                    <div style="background:#fff; border-radius:6px; padding:4px;">{product_svg or ''}</div>
                </div>
                <div style="font-weight:700; font-size:18px; margin-top:8px;">{product} </div>
                <div style="opacity:0.8;">{steps_count}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Down arrow under each product card (compact)
            st.markdown(
                "<div style='text-align: center; font-size: 26px; margin: 4px 0;'>⬇️</div>",
                unsafe_allow_html=True,
            )

            # Processing steps list in centered boxes
            if steps:
                # No per-column "Processing Steps" heading; go directly to step cards
                for _j, step in enumerate(steps, 1):
                    step_icon = _get_module_icon(step)

                    # Create centered box with delete icon on the right
                    st.markdown(
                        f"""
                    <div style="display: flex; align-items: center; justify-content: space-between;
                                padding: 14px; background-color: white; border: 1px solid #ddd;
                                border-radius: 8px; margin: 6px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                        <div style="flex: 1; text-align: center; font-size: 18px; font-weight: bold;">
                            <span style="font-size: 64px; margin-right: 10px;">{step_icon}</span>
                            {step}
                        </div>
                        <div style="margin-left: 15px;">
                            <button onclick="alert('Delete {step} from {product} workflow')"
                                    style="background: none; border: none; font-size: 18px; cursor: pointer;
                                           color: #ff4444; padding: 5px;"
                                    title="Delete {step} from {product}">
                                🗑️
                            </button>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info(f"No steps defined for {product}")


def _show_product_processing_cards(workflows: Dict[str, Any]):
    """Show detailed product processing cards (like Image 3)"""
    # Product Processing Details heading with workpiece SVGs per tab
    st.markdown(f"### {UISymbols.get_status_icon('stats')} Product Processing Details")

    products = ["BLUE", "WHITE", "RED"]

    # Create tabs for each product (BLUE, WHITE, RED order)
    # Enrich tab titles with small workpiece SVGs
    asset_mgr = get_asset_manager()
    tab_titles = []
    for p in products:
        svg = asset_mgr.get_product_svg_with_sizing(p, state="product", scale=0.18) or ""
        tab_titles.append(f"{svg} {p} Product")
    tabs = st.tabs(tab_titles)

    for _i, (product, tab) in enumerate(zip(products, tabs)):
        with tab:
            _show_product_detail_card(product, workflows.get(product, {}))


def _show_product_processing_details_dropdown(workflows: Dict[str, Any]):
    """Show product processing details using a product selector (dropdown)."""

    # Load enabled products from Registry (single source of truth)
    pm = get_omf2_product_manager()
    enabled_products = pm.get_enabled_products()  # keys: lower-case ids
    if not enabled_products:
        st.info("No enabled products in registry")
        return

    # Preferred visual order
    preferred_order = ["BLUE", "WHITE", "RED"]
    # Collect uppercase IDs from registry (respect enabled flag)
    reg_ids = [data.get("id", key.upper()) for key, data in enabled_products.items()]
    # Keep only those that we have workflows for (to avoid empty details)
    available_ids = [pid for pid in reg_ids if pid in workflows]
    if not available_ids:
        st.info("No product workflows available")
        return
    # Order per preference
    products = [pid for pid in preferred_order if pid in available_ids] + [
        pid for pid in available_ids if pid not in preferred_order
    ]

    # Selectbox with format_func (no HTML in options)
    def _format_product(pid: str) -> str:
        info = pm.get_product_by_id(pid) or {}
        name = info.get("name", pid)
        return f"{UISymbols.get_workpiece_icon(pid)} {name}"

    i18n = st.session_state.get("i18n_manager")
    select_label = i18n.t("ccu_process.dropdown.select_product") if i18n else "Select product"
    if select_label == "ccu_process.dropdown.select_product":
        select_label = "Select product"
    selected_product = st.selectbox(select_label, products, index=0, format_func=_format_product)
    _show_product_detail_card(selected_product, workflows.get(selected_product, {}))


def _show_product_detail_card(product: str, workflow: Dict[str, Any]):
    """Show detailed card for a specific product"""
    steps = workflow.get("steps", [])

    # Product header
    asset_mgr = get_asset_manager()
    # Resolve display name from registry and remove leading "Product " if present
    pm = get_omf2_product_manager()
    pinfo = pm.get_product_by_id(product) or {}
    pname = pinfo.get("name", product)
    if isinstance(pname, str) and pname.lower().startswith("product "):
        pname = pname[8:]
    # Render both 3DIM and PRODUCT with the same container as in product_catalog
    header_prod_raw = asset_mgr.get_workpiece_svg(product, "product")
    header_3d_raw = asset_mgr.get_workpiece_svg(product, "3dim")
    header_prod = render_product_svg_container(header_prod_raw, scale=0.24) if header_prod_raw else ""
    header_3d = render_product_svg_container(header_3d_raw, scale=0.24) if header_3d_raw else ""
    st.markdown(
        f"""
        <div style='display:flex; align-items:center; gap:12px;'>
            <div style='display:inline-flex; gap:8px; align-items:flex-start;'>{header_3d}{header_prod}</div>
            <h3 style='margin:0;'>{pname}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    i18n = st.session_state.get("i18n_manager")
    steps_count = (
        i18n.t("ccu_process.processing.steps_count", count=len(steps)) if i18n else f"{len(steps)} Processing Steps"
    )
    st.markdown(f"**{steps_count}**")

    if not steps:
        st.info(f"No processing steps defined for {product}")
        return

    # Show each processing step as a centered card
    for i, step in enumerate(steps, 1):
        with st.container():
            # Centered step card with delete icon on the right
            st.markdown(
                f"""
            <div style="padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 10px; margin: 15px 0; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                <div style="display:flex; align-items:flex-start; justify-content:flex-start; gap:16px;">
                    <div style="text-align:left;">
                        <h3 style="margin: 0; font-size: 20px; font-weight: bold;">{i}. {step}</h3>
                        <p style="margin: 8px 0 0 0; color: #666; font-size: 14px;">{_get_step_description(step)}</p>
                    </div>
                    <div style="min-width: 64px; text-align:center;">{_get_module_icon(step)}</div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def _get_step_status_icon(step_num: int, total_steps: int) -> str:
    """Get status icon for step (green checkmark for completed, red clock for pending)"""
    # Mock logic: first step completed, others pending
    if step_num == 1:
        return "✅"
    else:
        return "⏰"


def _get_step_description(step: str) -> str:
    """Get i18n description for a processing step"""
    i18n = st.session_state.get("i18n_manager")
    if i18n:
        key = f"ccu_process.steps.{step.lower()}"
        try:
            text = i18n.t(key)
            if text and text != key:
                return text
        except Exception:
            pass
    return f"Processing step: {step}"


def _get_product_icon(product: str) -> str:
    """Get product icon"""
    icons = {"BLUE": "🔵", "WHITE": "⚪", "RED": "🔴"}
    return icons.get(product, "📦")


def _show_workflow_overview_section(workflows: Dict[str, Any]):
    """Show workflow overview section"""
    st.markdown(f"### {UISymbols.get_status_icon('overview')} Workflow Overview")
    st.write("Production workflows for different workpiece types")

    # Extract product workflows (BLUE, WHITE, RED)
    products = ["BLUE", "WHITE", "RED"]

    # Create overview cards
    cols = st.columns(3)

    for i, product in enumerate(products):
        if product in workflows:
            workflow = workflows[product]
            steps = workflow.get("steps", [])

            with cols[i]:
                # Product header with color
                color_emoji = {"BLUE": "🔵", "WHITE": "⚪", "RED": "🔴"}.get(product, "🟦")

                st.markdown(f"### {color_emoji} {product}")

                # Steps count
                st.metric("Production Steps", len(steps))

                # Steps list
                if steps:
                    st.markdown("**Workflow Steps:**")
                    for j, step in enumerate(steps, 1):
                        st.write(f"{j}. {step}")
                else:
                    st.info("No steps defined")


def _show_detailed_workflows_section(workflows: Dict[str, Any]):
    """Show detailed workflows section"""
    st.markdown(f"### {UISymbols.get_tab_icon('detailed')} Detailed Workflows")
    st.write("Step-by-step production process for each product")

    products = ["BLUE", "WHITE", "RED"]

    # Create tabs for each product
    tabs = st.tabs(["🔵 BLUE", "⚪ WHITE", "🔴 RED"])

    for _i, (product, tab) in enumerate(zip(products, tabs)):
        with tab:
            if product in workflows:
                _show_product_workflow_detail(product, workflows[product])
            else:
                st.warning(f"No workflow defined for {product}")


def _show_product_workflow_detail(product: str, workflow: Dict[str, Any]):
    """Show detailed workflow for a specific product"""
    steps = workflow.get("steps", [])

    if not steps:
        st.info(f"No production steps defined for {product}")
        return

    # Workflow visualization
    st.markdown(f"#### {product} Production Workflow")

    # Show workflow as a process flow
    _show_workflow_process_flow(product, steps)

    # Show step details
    st.markdown("#### Step Details")
    for i, step in enumerate(steps, 1):
        with st.expander(f"Step {i}: {step}", expanded=False):
            _show_step_details(step, i, len(steps))


def _show_workflow_process_flow(product: str, steps: List[str]):
    """Show workflow as a visual process flow"""
    # Create a visual flow: HBW → [Steps] → DPS
    flow_parts = ["HBW"] + steps + ["DPS"]

    # Display flow as columns
    cols = st.columns(len(flow_parts))

    for i, (part, col) in enumerate(zip(flow_parts, cols)):
        with col:
            # Different styling for start/end vs process steps
            if part == "HBW":
                st.markdown("### 🏬")
                st.markdown("**HBW**")
                st.caption("Warehouse")
                st.markdown("**Start**")
            elif part == "DPS":
                st.markdown("### 📦")
                st.markdown("**DPS**")
                st.caption("Output")
                st.markdown("**End**")
            else:
                # Process step
                st.markdown(f"### {_get_module_icon(part)}", unsafe_allow_html=True)
                st.markdown(f"**{part}**")
                st.caption(f"Step {i}")

                # Add arrow between steps (except last)
                if i < len(flow_parts) - 1:
                    st.markdown("↓")


def _show_step_details(step: str, step_number: int, total_steps: int):
    """Show detailed information for a workflow step"""
    st.write(f"**Module:** {step}")
    st.write(f"**Position:** Step {step_number} of {total_steps}")

    # Module-specific information
    module_info = _get_module_info(step)
    if module_info:
        st.write(f"**Description:** {module_info['description']}")
        st.write(f"**Function:** {module_info['function']}")

    # Estimated duration (placeholder)
    st.write(f"**Estimated Duration:** {_get_estimated_duration(step)}")


def _show_workflow_comparison_section(workflows: Dict[str, Any]):
    """Show workflow comparison section"""
    st.markdown(f"### {UISymbols.get_status_icon('stats')} Workflow Comparison")
    st.write("Compare production workflows across different products")

    products = ["BLUE", "WHITE", "RED"]

    # Create comparison table
    comparison_data = []

    for product in products:
        if product in workflows:
            steps = workflows[product].get("steps", [])
            comparison_data.append(
                {
                    "Product": product,
                    "Steps Count": len(steps),
                    "Workflow": " → ".join(steps) if steps else "No steps",
                    "Complexity": _get_complexity_level(len(steps)),
                }
            )

    if comparison_data:
        st.table(comparison_data)

        # Summary statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            avg_steps = sum(row["Steps Count"] for row in comparison_data) / len(comparison_data)
            st.metric("Average Steps", f"{avg_steps:.1f}")

        with col2:
            max_steps = max(row["Steps Count"] for row in comparison_data)
            st.metric("Max Steps", max_steps)

        with col3:
            min_steps = min(row["Steps Count"] for row in comparison_data)
            st.metric("Min Steps", min_steps)


def _get_module_icon(module: str) -> str:
    """Get SVG icon HTML for module (fallback to empty)"""
    try:
        return get_icon_html(module, size_px=64)
    except Exception:
        return ""


def _get_module_info(module: str) -> Dict[str, str]:
    """Get module information"""
    module_info = {
        "MILL": {"description": "Milling machine for precision machining", "function": "Material removal and shaping"},
        "DRILL": {"description": "Drilling machine for hole creation", "function": "Hole drilling and boring"},
        "AIQS": {"description": "AI Quality System for inspection", "function": "Quality control and inspection"},
        "HBW": {"description": "High-bay warehouse for storage", "function": "Material storage and retrieval"},
        "DPS": {"description": "Distribution and picking station", "function": "Order fulfillment and dispatch"},
    }
    return module_info.get(module, {})


def _get_estimated_duration(module: str) -> str:
    """Get estimated duration for module"""
    durations = {"MILL": "8-12 min", "DRILL": "5-8 min", "AIQS": "3-5 min", "HBW": "1-2 min", "DPS": "2-3 min"}
    return durations.get(module, "Unknown")


def _get_complexity_level(step_count: int) -> str:
    """Get complexity level based on step count"""
    if step_count <= 2:
        return "🟢 Simple"
    elif step_count <= 3:
        return "🟡 Medium"
    else:
        return "🔴 Complex"
