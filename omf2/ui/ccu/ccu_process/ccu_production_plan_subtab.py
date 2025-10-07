#!/usr/bin/env python3
"""
CCU Process - Production Plan Subtab
Production workflow visualization for BLUE, WHITE, RED products
"""

import streamlit as st
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh
from omf2.ui.common.symbols import UISymbols
from typing import Dict, List, Any

logger = get_logger(__name__)


def render_ccu_production_plan_subtab():
    """Render CCU Production Plan Subtab - Interactive Workflow Design"""
    logger.info("📋 Rendering CCU Production Plan Subtab")
    try:
        st.subheader(f"{UISymbols.get_tab_icon('production_plan')} Production Plan")
        st.markdown("Interactive production workflow planning and management")

        # Load production workflows
        config_loader = get_ccu_config_loader()
        workflows = config_loader.load_production_workflows()

        if not workflows:
            st.error(f"{UISymbols.get_status_icon('error')} Failed to load production workflows.")
            logger.error("Production workflows could not be loaded.")
            return

        # Workflow Controls Section
        _show_workflow_controls_section()

        st.divider()

        # Main Workflow Visualization (like Image 2)
        _show_interactive_workflow_visualization(workflows)

        st.divider()

        # Product Processing Details
        _show_product_processing_cards(workflows)

    except Exception as e:
        logger.error(f"❌ CCU Production Plan Subtab rendering error: {e}")
        st.error(f"❌ CCU Production Plan Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_workflow_controls_section():
    """Show workflow controls section (Add, Save, Refresh, Toggle)"""
    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
    
    with col1:
        if st.button(f"{UISymbols.get_status_icon('add')} Add Step", key="add_workflow_step"):
            st.info("➕ Add Step functionality coming soon!")
    
    with col2:
        if st.button(f"{UISymbols.get_status_icon('save')} Save", key="save_workflow"):
            st.success("💾 Workflow saved successfully!")
    
    with col3:
        if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh", key="refresh_workflow"):
            request_refresh()
            st.info("🔄 Workflow refreshed!")
    
    with col4:
        # Advanced Processing Toggle
        advanced_mode = st.toggle(
            "Activate advanced processing steps",
            value=False,
            key="advanced_processing_toggle"
        )
        if advanced_mode:
            st.info("🔧 Advanced processing mode activated")


def _show_interactive_workflow_visualization(workflows: Dict[str, Any]):
    """Show main interactive workflow visualization (like Image 2)"""
    st.markdown(f"### {UISymbols.get_tab_icon('workflow')} Processing Steps")
    
    # Unified workflow: Start/End spanning all 3 products
    _show_unified_workflow_section(workflows)


def _show_unified_workflow_section(workflows: Dict[str, Any]):
    """Show unified workflow with Start/End spanning all 3 products"""
    
    # Start section spanning all 3 columns
    st.markdown("### 🏬 Retrieve via high-bay warehouse")
    
    # High-Bay Warehouse spanning all products
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #e3f2fd; border-radius: 10px; margin: 10px 0;">
        <h3>🏬 High-Bay Warehouse</h3>
        <p><strong>Retrieve via high-bay warehouse</strong></p>
        <p>Initial material retrieval and staging for all product types</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Arrow down
    st.markdown("<div style='text-align: center; font-size: 24px; margin: 10px 0;'>↓</div>", unsafe_allow_html=True)
    
    # Parallel processing section with 3 product types
    _show_parallel_processing_section(workflows)
    
    # Arrow up
    st.markdown("<div style='text-align: center; font-size: 24px; margin: 10px 0;'>↑</div>", unsafe_allow_html=True)
    
    # End section spanning all 3 columns
    st.markdown("### 📦 Delivery via Goods Outgoing")
    
    # Goods Outgoing spanning all products
    st.markdown("""
    <div style="text-align: center; padding: 20px; background-color: #e8f5e8; border-radius: 10px; margin: 10px 0;">
        <h3>📦 Goods Outgoing</h3>
        <p><strong>Delivery via Goods Outgoing</strong></p>
        <p>Final product delivery and dispatch for all product types</p>
    </div>
    """, unsafe_allow_html=True)


def _show_parallel_processing_section(workflows: Dict[str, Any]):
    """Show parallel processing section with 3 product cards"""
    st.markdown("### Parallel Processing")
    
    # Create 3 columns for Blue, Red, White products
    col1, col2, col3 = st.columns(3)
    
    products = ["BLUE", "WHITE", "RED"]
    product_colors = {"BLUE": "🔵", "RED": "🔴", "WHITE": "⚪"}
    product_bg_colors = {"BLUE": "#e3f2fd", "RED": "#ffebee", "WHITE": "#f5f5f5"}
    
    cols = [col1, col2, col3]
    
    for i, (product, col) in enumerate(zip(products, cols)):
        with col:
            # Product card
            workflow = workflows.get(product, {})
            steps = workflow.get("steps", [])
            
            # Card styling
            st.markdown(f"""
            <div style="padding: 20px; background-color: {product_bg_colors[product]}; border-radius: 10px; margin: 10px 0;">
                <div style="text-align: center;">
                    <h3>{product_colors[product]} {product}</h3>
                    <p><strong>{len(steps)} Processing Steps</strong></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Processing steps list in centered boxes
            if steps:
                st.markdown("**Processing Steps:**")
                for j, step in enumerate(steps, 1):
                    step_icon = _get_module_icon(step)
                    
                    # Create centered box with delete icon on the right
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; 
                                padding: 15px; background-color: white; border: 1px solid #ddd; 
                                border-radius: 8px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="flex: 1; text-align: center; font-size: 18px; font-weight: bold;">
                            <span style="font-size: 24px; margin-right: 10px;">{step_icon}</span>
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
                    """, unsafe_allow_html=True)
            else:
                st.info(f"No steps defined for {product}")




def _show_product_processing_cards(workflows: Dict[str, Any]):
    """Show detailed product processing cards (like Image 3)"""
    st.markdown(f"### {UISymbols.get_status_icon('stats')} Product Processing Details")
    
    products = ["BLUE", "WHITE", "RED"]
    
    # Create tabs for each product (BLUE, WHITE, RED order)
    tabs = st.tabs([f"{_get_product_icon(p)} {p} Product" for p in products])
    
    for i, (product, tab) in enumerate(zip(products, tabs)):
        with tab:
            _show_product_detail_card(product, workflows.get(product, {}))


def _show_product_detail_card(product: str, workflow: Dict[str, Any]):
    """Show detailed card for a specific product"""
    steps = workflow.get("steps", [])
    
    # Product header
    color_icon = _get_product_icon(product)
    st.markdown(f"### {color_icon} {product} Product")
    st.markdown(f"**{len(steps)} Verarbeitungsschritte** (Processing Steps)")
    
    if not steps:
        st.info(f"No processing steps defined for {product}")
        return
    
    # Show each processing step as a centered card
    for i, step in enumerate(steps, 1):
        with st.container():
            # Centered step card with delete icon on the right
            st.markdown(f"""
            <div style="padding: 20px; background-color: white; border: 1px solid #ddd; border-radius: 10px; margin: 15px 0; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="flex: 1; text-align: center;">
                        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                            <span style="font-size: 28px; margin-right: 15px;">{_get_step_status_icon(i, len(steps))}</span>
                            <span style="font-size: 24px; margin-right: 15px;">{_get_module_icon(step)}</span>
                        </div>
                        <h3 style="margin: 0; font-size: 20px; font-weight: bold;">{i}. {step}</h3>
                        <p style="margin: 8px 0 0 0; color: #666; font-size: 14px;">{_get_step_description(step)}</p>
                    </div>
                    <div style="margin-left: 20px;">
                        <button onclick="alert('Delete {step} from {product} workflow')" 
                                style="background: none; border: none; font-size: 20px; cursor: pointer; 
                                       color: #ff4444; padding: 8px; border-radius: 50%; 
                                       transition: background-color 0.3s;" 
                                title="Delete {step} from {product}"
                                onmouseover="this.style.backgroundColor='#ffebee'" 
                                onmouseout="this.style.backgroundColor='transparent'">
                            🗑️
                        </button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def _get_step_status_icon(step_num: int, total_steps: int) -> str:
    """Get status icon for step (green checkmark for completed, red clock for pending)"""
    # Mock logic: first step completed, others pending
    if step_num == 1:
        return "✅"
    else:
        return "⏰"


def _get_step_description(step: str) -> str:
    """Get German description for step"""
    descriptions = {
        "MILL": "Fräsen des Werkstücks",
        "DRILL": "Bohren des Werkstücks", 
        "AIQS": "Qualitätskontrolle mittels KI",
        "HBW": "Materiallager und -bereitstellung",
        "DPS": "Auftragserfüllung und Versand"
    }
    return descriptions.get(step, f"Processing step: {step}")


def _get_product_icon(product: str) -> str:
    """Get product icon"""
    icons = {
        "BLUE": "🔵",
        "WHITE": "⚪",
        "RED": "🔴"
    }
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
                color_emoji = {
                    "BLUE": "🔵",
                    "WHITE": "⚪", 
                    "RED": "🔴"
                }.get(product, "🟦")
                
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
    tabs = st.tabs([f"🔵 BLUE", "⚪ WHITE", "🔴 RED"])
    
    for i, (product, tab) in enumerate(zip(products, tabs)):
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
                st.markdown(f"### {_get_module_icon(part)}")
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
            comparison_data.append({
                "Product": product,
                "Steps Count": len(steps),
                "Workflow": " → ".join(steps) if steps else "No steps",
                "Complexity": _get_complexity_level(len(steps))
            })
    
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
    """Get emoji icon for module"""
    icons = {
        "MILL": "⚙️",
        "DRILL": "🔩", 
        "AIQS": "🤖",
        "HBW": "🏬",
        "DPS": "📦",
        "CHRG": "🔋",
        "FTS": "🚗"
    }
    return icons.get(module, "🛠️")


def _get_module_info(module: str) -> Dict[str, str]:
    """Get module information"""
    module_info = {
        "MILL": {
            "description": "Milling machine for precision machining",
            "function": "Material removal and shaping"
        },
        "DRILL": {
            "description": "Drilling machine for hole creation",
            "function": "Hole drilling and boring"
        },
        "AIQS": {
            "description": "AI Quality System for inspection",
            "function": "Quality control and inspection"
        },
        "HBW": {
            "description": "High-bay warehouse for storage",
            "function": "Material storage and retrieval"
        },
        "DPS": {
            "description": "Distribution and picking station",
            "function": "Order fulfillment and dispatch"
        }
    }
    return module_info.get(module, {})


def _get_estimated_duration(module: str) -> str:
    """Get estimated duration for module"""
    durations = {
        "MILL": "8-12 min",
        "DRILL": "5-8 min",
        "AIQS": "3-5 min",
        "HBW": "1-2 min",
        "DPS": "2-3 min"
    }
    return durations.get(module, "Unknown")


def _get_complexity_level(step_count: int) -> str:
    """Get complexity level based on step count"""
    if step_count <= 2:
        return "🟢 Simple"
    elif step_count <= 3:
        return "🟡 Medium"
    else:
        return "🔴 Complex"
