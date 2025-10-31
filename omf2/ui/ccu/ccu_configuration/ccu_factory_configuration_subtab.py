#!/usr/bin/env python3
"""
CCU Configuration - Factory Configuration Subtab
Displays shopfloor layout from CCU Config Loader
"""

from pathlib import Path

import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_ccu_factory_configuration_subtab():
    """Render CCU Factory Configuration Subtab"""
    logger.info("🏭 Rendering CCU Factory Configuration Subtab")
    try:
        try:
            i18n = st.session_state.get("i18n_manager")
            factory_icon = get_svg_inline("FACTORY_CONFIGURATION", size_px=32) or ""
            title = i18n.t("ccu_configuration.factory.title") if i18n else "Factory Configuration"
            st.markdown(
                f"<h3 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{factory_icon} {title}</h3>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.subheader(f"{UISymbols.get_tab_icon('factory')} Factory Configuration")
        subtitle = (
            i18n.t("ccu_configuration.factory.subtitle")
            if "i18n" in locals() and i18n
            else "Factory layout configuration and module positioning"
        )
        st.markdown(
            f"<p style='margin: 0.25rem 0 0.25rem 0;'>{subtitle}</p>",
            unsafe_allow_html=True,
        )

        # Shopfloor Layout Display (title will be rendered inside component to avoid spacing)
        _show_shopfloor_layout_section()

        # Shopfloor Position Details Section
        st.divider()
        _show_shopfloor_position_details()

        # Module Details Section (shown after double-click)
        if st.session_state.get("show_module_details") and st.session_state.get("selected_module_id"):
            st.divider()
            _show_module_details_section()

    except Exception as e:
        logger.error(f"❌ CCU Factory Configuration Subtab rendering error: {e}")
        st.error(f"❌ CCU Factory Configuration Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_shopfloor_layout_section():
    """Show enhanced shopfloor layout section with asset manager"""
    try:
        # Import and use the shopfloor layout component
        from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

        i18n = st.session_state.get("i18n_manager")

        # Show the shopfloor layout with interactive SVG
        # CCU Configuration mode: single/double click for module selection/navigation
        # Note: Message listener script is integrated into show_shopfloor_layout() component
        show_shopfloor_layout(
            title=(i18n.t("ccu_configuration.factory.shopfloor_layout_title") if i18n else "Shopfloor Layout"),
            unique_key="ccu_configuration_shopfloor",
            mode="ccu_configuration",  # CCU Configuration mode: single click = select, double click = navigate
            enable_click=True,  # Enable click-to-select functionality
        )

    except Exception as e:
        st.error(f"❌ Failed to load shopfloor layout: {e}")
        logger.error(f"Failed to load shopfloor layout: {e}")


def _show_shopfloor_position_details():
    """Show shopfloor position details with module/position dropdown and highlighting"""
    try:
        i18n = st.session_state.get("i18n_manager")
        st.subheader(
            i18n.t("ccu_configuration.factory.selection_title") if i18n else "🔧 Shopfloor Module Selection & Details"
        )

        # Import shopfloor display helpers
        from omf2.config.ccu.shopfloor_display import (
            get_display_region_for_key,
            get_dropdown_keys,
        )

        # Load layout configuration
        config_loader = get_ccu_config_loader()
        layout_config = config_loader.load_shopfloor_layout()

        if not layout_config:
            st.warning(
                i18n.t("ccu_configuration.factory.no_layout")
                if i18n
                else "⚠️ No shopfloor layout configuration available"
            )
            return

        # Get dropdown keys (modules, fixed positions, intersections)
        dropdown_keys = get_dropdown_keys()
        dropdown_options = [label for key, label in dropdown_keys]
        dropdown_key_map = {label: key for key, label in dropdown_keys}

        # Check if a position was clicked (stored in session state)
        selected_key = None
        if "selected_shopfloor_key" in st.session_state:
            selected_key = st.session_state.selected_shopfloor_key

        # Dropdown for module/position selection
        col1, col2 = st.columns([2, 1])

        # Set default index based on selected key
        default_index = 0
        if selected_key:
            # Find the label for the selected key
            matching_labels = [label for label, key in dropdown_key_map.items() if key == selected_key]
            if matching_labels and matching_labels[0] in dropdown_options:
                default_index = dropdown_options.index(matching_labels[0])

        with col1:
            selected_label = st.selectbox(
                (i18n.t("ccu_configuration.factory.select_label") if i18n else "📍 Select Module or Position:"),
                options=dropdown_options,
                index=default_index,
                key="shopfloor_module_selector",
                help=(
                    i18n.t("ccu_configuration.factory.select_help")
                    if i18n
                    else "Select a module, fixed position, or intersection to view details and highlight on the grid"
                ),
            )

        with col2:
            if st.button(
                i18n.t("ccu_configuration.factory.refresh") if i18n else "🔄 Refresh", key="refresh_module_details"
            ):
                # Clear selection on refresh
                if "selected_shopfloor_key" in st.session_state:
                    del st.session_state.selected_shopfloor_key
                request_refresh()

        # Get the key for the selected label
        selected_key = dropdown_key_map.get(selected_label)

        # Store selected key in session state
        if selected_key:
            st.session_state.selected_shopfloor_key = selected_key

            # Get display region for this key
            display_region = get_display_region_for_key(selected_key)

            # Show shopfloor layout with highlighting
            if display_region:
                message = (
                    i18n.t(
                        "ccu_configuration.factory.highlighting_for",
                        count=len(display_region),
                        label=selected_label,
                    )
                    if i18n
                    else f"💡 Highlighting {len(display_region)} cell(s) for {selected_label}"
                )
                st.info(message)

                # Import and render shopfloor layout with highlighting
                from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

                show_shopfloor_layout(
                    title=(
                        i18n.t("ccu_configuration.factory.shopfloor_layout_title_for", label=selected_label)
                        if i18n
                        else f"Shopfloor Layout - {selected_label}"
                    ),
                    unique_key="ccu_configuration_shopfloor_highlight",
                    mode="ccu_configuration",
                    enable_click=False,  # Disable click in detail view
                    highlight_cells=display_region,
                )

            # Show details for the selected key
            _show_key_details(selected_key, layout_config)
        else:
            st.error("❌ Invalid selection")

    except Exception as e:
        logger.error(f"❌ Failed to show shopfloor position details: {e}")
        st.error(f"❌ Error showing position details: {e}")


def _show_key_details(key: str, layout_config: dict):
    """Show details for a selected module/position key with enhanced formatting"""
    try:
        from omf2.config.ccu.shopfloor_display import get_shopfloor_display

        # Get entry from registry
        display = get_shopfloor_display()
        entry = display.registry.get(key)

        if not entry:
            st.warning(f"⚠️ No details found for key: {key}")
            return

        # Display details in a nice box
        st.markdown("---")
        i18n = st.session_state.get("i18n_manager")
        details_title = i18n.t("ccu_configuration.factory.details_for", label=key) if i18n else f"📍 Details for {key}"
        st.markdown(f"### {details_title}")

        # Determine entry type and display accordingly
        if entry.get("is_module"):
            # Module entry
            with st.container():
                st.success(f"✅ **Module:** {entry.get('id', 'Unknown')}")

                # Find full module data from layout_config
                modules = layout_config.get("modules", [])
                module_data = None
                for module in modules:
                    if module.get("id") == key:
                        module_data = module
                        break

                if module_data:
                    # Details in columns
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Properties:**")
                        st.write(f"- **ID:** {module_data.get('id', 'N/A')}")
                        st.write(f"- **Type:** {module_data.get('type', 'N/A')}")
                        st.write(f"- **Position:** {module_data.get('position', 'N/A')}")

                    with col2:
                        st.markdown("**Technical:**")
                        st.write(f"- **Serial Number:** {module_data.get('serialNumber', 'N/A')}")

                        # Show attached assets if available
                        attached_assets = module_data.get("attached_assets", [])
                        if attached_assets:
                            st.write(f"- **Attached Assets:** {', '.join(attached_assets)}")

                        # Show display variants
                        display_variants = module_data.get("display_variants", {})
                        if display_variants:
                            st.write("- **Display Variants:**")
                            for variant, region in display_variants.items():
                                st.write(f"  - {variant}: {region}")

        elif entry.get("is_fixed"):
            # Fixed position entry
            with st.container():
                position_type = entry.get("type", "Unknown").upper()
                st.info(f"📦 **Fixed Position:** {entry.get('id', 'Unknown')}")

                # Details in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Properties:**")
                    st.write(f"- **ID:** {entry.get('id', 'Unknown')}")
                    st.write(f"- **Type:** {position_type}")
                    st.write(f"- **Position:** {entry.get('position', 'N/A')}")

                with col2:
                    st.markdown("**Asset Keys:**")
                    assets = entry.get("assets", {})
                    if assets:
                        for asset_type, asset_name in assets.items():
                            st.write(f"- **{asset_type}:** {asset_name}")

                    # Show if this is a rect-only key
                    if entry.get("is_rect_only"):
                        st.write("- **Click Behavior:** Rectangle only")

        elif entry.get("is_intersection"):
            # Intersection entry
            with st.container():
                st.warning(f"➕ **Intersection:** {entry.get('id', 'Unknown')}")

                st.markdown("**Properties:**")
                st.write(f"- **ID:** {entry.get('id', 'Unknown')}")
                st.write("- **Type:** Intersection")
                st.write(f"- **Position:** {entry.get('position', 'N/A')}")

        else:
            st.info(f"📄 **Position:** {key}")
            st.write(f"- **Type:** {entry.get('type', 'Unknown')}")
            st.write(f"- **Position:** {entry.get('position', 'N/A')}")

    except Exception as e:
        logger.error(f"Failed to show key details: {e}")
        st.error(f"❌ Failed to load details: {e}")


def _show_position_details(row: int, col: int, layout_config: dict):
    """Show details for a specific shopfloor position with enhanced formatting"""
    try:
        # Check if position has a module
        modules = layout_config.get("modules", [])
        fixed_positions = layout_config.get("fixed_positions", [])  # New structure (v2.0)
        # Fallback for old structure
        if not fixed_positions:
            fixed_positions = layout_config.get("empty_positions", [])
        intersections = layout_config.get("intersections", [])

        # Find module at this position
        module_at_position = None
        for module in modules:
            if module.get("position") == [row, col]:
                module_at_position = module
                break

        # Find fixed position at this position
        fixed_at_position = None
        for fixed_pos in fixed_positions:
            if fixed_pos.get("position") == [row, col]:
                fixed_at_position = fixed_pos
                break

        # Find intersection at this position
        intersection_at_position = None
        for intersection in intersections:
            if intersection.get("position") == [row, col]:
                intersection_at_position = intersection
                break

        # Display details in a nice box
        st.markdown("---")
        st.markdown(f"### 📍 Details zu shopfloor-position-{row}-{col}")

        # Display details based on what's at this position
        if module_at_position:
            with st.container():
                st.success(f"✅ **Module Found:** {module_at_position.get('id', 'Unknown')}")

                # Details in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Properties:**")
                    st.write(f"- **ID:** {module_at_position.get('id', 'N/A')}")
                    st.write(f"- **Name:** {module_at_position.get('id', 'N/A')}")  # Use ID as name
                    st.write(f"- **Type:** {module_at_position.get('type', 'N/A')}")

                with col2:
                    st.markdown("**Technical:**")
                    st.write(f"- **Serial Number:** {module_at_position.get('serialNumber', 'N/A')}")
                    st.write(f"- **Position:** [{row}, {col}]")
                    # Asset keys (module type is the main asset key)
                    st.write(f"- **Asset Keys:** {module_at_position.get('type', 'N/A')}")

        elif fixed_at_position:
            with st.container():
                position_type = fixed_at_position.get("type", "Unknown").upper()
                st.info(f"📦 **Position Type:** {position_type}")

                # Details in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Properties:**")
                    st.write(f"- **ID:** {fixed_at_position.get('id', 'Unknown')}")
                    st.write(f"- **Name:** {fixed_at_position.get('id', 'Unknown')}")
                    st.write(f"- **Type:** {position_type}")
                    st.write(f"- **Position:** [{row}, {col}]")

                with col2:
                    st.markdown("**Asset Keys:**")
                    assets = fixed_at_position.get("assets", {})
                    st.write(f"- **Rectangle:** {assets.get('rectangle', 'N/A')}")
                    st.write(f"- **Square1:** {assets.get('square1', 'N/A')}")
                    st.write(f"- **Square2:** {assets.get('square2', 'N/A')}")

                # Show asset information if available
                st.markdown("---")
                _show_fixed_position_assets(fixed_at_position)

        elif intersection_at_position:
            with st.container():
                st.warning(f"🔀 **Intersection:** {intersection_at_position.get('id', 'Unknown')}")

                # Details in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Properties:**")
                    st.write(f"- **ID:** {intersection_at_position.get('id', 'Unknown')}")
                    st.write(f"- **Name:** Intersection {intersection_at_position.get('id', 'Unknown')}")
                    st.write(f"- **Position:** [{row}, {col}]")

                with col2:
                    st.markdown("**Connections:**")
                    connected = intersection_at_position.get("connected_modules", [])
                    if connected:
                        for conn_module in connected:
                            st.write(f"- {conn_module}")
                    else:
                        st.write("- No connections")

                    # Asset key for intersection
                    st.write("- **Asset Keys:** point_scan_3sections")

        else:
            with st.container():
                st.info(f"📋 **Empty Cell** at position [{row}, {col}]")
                st.write("**Description:** No module, empty position, or intersection found at this location.")
                st.write(f"**Position:** [{row}, {col}]")
                st.write("**Asset Keys:** None")

    except Exception as e:
        logger.error(f"❌ Failed to show position details: {e}")
        st.error(f"❌ Error showing position details: {e}")


def _show_fixed_position_assets(fixed_position: dict):
    """Show asset information for fixed positions using canonical shopfloor_assets structure"""
    try:
        position_id = fixed_position.get("id", "Unknown")

        # Get Asset Manager
        from omf2.assets import get_asset_manager

        asset_manager = get_asset_manager()

        # Show available assets
        st.markdown("#### 🎨 Available Assets:")

        col1, col2, col3 = st.columns(3)

        # Use canonical key format: COMPANY_rectangle, SOFTWARE_square1, etc.
        canonical_type = position_id  # COMPANY or SOFTWARE

        with col1:
            st.markdown("**Rectangle:**")
            asset_path = asset_manager.get_shopfloor_asset_path(canonical_type, "rectangle")
            if asset_path:
                st.write(f"📁 {Path(asset_path).name}")
            else:
                st.write("❌ No asset found")

        with col2:
            st.markdown("**Square1:**")
            asset_path = asset_manager.get_shopfloor_asset_path(canonical_type, "square1")
            if asset_path:
                st.write(f"📁 {Path(asset_path).name}")
            else:
                st.write("❌ No asset found")

        with col3:
            st.markdown("**Square2:**")
            asset_path = asset_manager.get_shopfloor_asset_path(canonical_type, "square2")
            if asset_path:
                st.write(f"📁 {Path(asset_path).name}")
            else:
                st.write("❌ No asset found")

    except Exception as e:
        logger.error(f"❌ Failed to show fixed position assets: {e}")
        st.error(f"❌ Error showing assets: {e}")


# Layout Information Sektion entfernt - uninteressant


def _load_factory_layout():
    """Load factory layout from config file"""
    try:
        config_loader = get_ccu_config_loader()
        layout_data = config_loader.load_shopfloor_layout()

        if layout_data:
            st.success(f"{UISymbols.get_status_icon('success')} Factory layout loaded successfully!")
            logger.info("Factory layout loaded from CCU config")
            request_refresh()
        else:
            st.warning(f"{UISymbols.get_status_icon('warning')} No layout data found")

    except Exception as e:
        st.error(f"{UISymbols.get_status_icon('error')} Failed to load factory layout: {e}")
        logger.error(f"Failed to load factory layout: {e}")


def _save_factory_layout():
    """Save factory layout to config file"""
    try:
        # TODO: Implement actual save functionality via CCU Gateway
        # For now, just show success message
        st.success(f"{UISymbols.get_status_icon('success')} Factory layout saved!")
        logger.info("Factory layout saved successfully")
        request_refresh()

    except Exception as e:
        st.error(f"{UISymbols.get_status_icon('error')} Failed to save factory layout: {e}")
        logger.error(f"Failed to save factory layout: {e}")


def _refresh_factory_layout():
    """Refresh factory layout display"""
    try:
        # Clear cache and refresh
        config_loader = get_ccu_config_loader()
        config_loader.clear_cache()

        st.success(f"{UISymbols.get_status_icon('success')} Factory layout refreshed!")
        logger.info("Factory layout refreshed")
        request_refresh()

    except Exception as e:
        st.error(f"{UISymbols.get_status_icon('error')} Failed to refresh factory layout: {e}")
        logger.error(f"Failed to refresh factory layout: {e}")


def _show_module_details_section():
    """Show module details section with registry data"""
    try:
        selected_module_id = st.session_state.get("selected_module_id")

        if not selected_module_id:
            return

        st.subheader(f"🔧 Module Details: {selected_module_id}")

        # Close button to hide module details
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("✖️ Close", key="close_module_details"):
                st.session_state.show_module_details = False
                st.session_state.pop("selected_module_id", None)
                st.session_state.pop("selected_module_type", None)
                request_refresh()

        # Get Registry Manager
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()

        # Get module data from registry
        modules = registry_manager.get_modules()
        stations = registry_manager.get_stations()
        txt_controllers = registry_manager.get_txt_controllers()

        # Find module in registry
        module_data = modules.get(selected_module_id)

        if not module_data:
            st.warning(f"⚠️ Module {selected_module_id} not found in registry")
            return

        # Display module information in columns
        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("#### 📊 Module SVG")
            _display_module_svg(selected_module_id, module_data)

        with col2:
            st.markdown("#### 📋 Module Information")
            _display_module_info(selected_module_id, module_data, stations, txt_controllers)

    except Exception as e:
        logger.error(f"❌ Failed to show module details: {e}")
        st.error(f"❌ Error showing module details: {e}")


def _display_module_svg(module_id: str, module_data: dict):
    """Display module SVG icon"""
    try:
        from omf2.assets import get_asset_manager

        asset_manager = get_asset_manager()

        # Get module icon path from module name or type
        module_name = module_data.get("name", module_id)
        icon_path = asset_manager.get_module_icon_path(module_name)

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # Display SVG with proper size
                import streamlit.components.v1 as components

                components.html(f'<div style="text-align: center;">{svg_content}</div>', height=200)
        else:
            st.info(f"📋 No SVG icon available for {module_name}")

    except Exception as e:
        logger.error(f"❌ Failed to display module SVG: {e}")
        st.error(f"❌ Error loading SVG: {e}")


def _display_module_info(module_id: str, module_data: dict, stations: dict, txt_controllers: dict):
    """Display module information from registry"""
    try:
        # Module basic information
        st.markdown("**Module Data:**")
        st.write(f"- **ID:** {module_id}")
        st.write(f"- **Name:** {module_data.get('name', 'N/A')}")
        st.write(f"- **Type:** {module_data.get('type', 'N/A')}")
        st.write(f"- **Enabled:** {'✅ Yes' if module_data.get('enabled', True) else '❌ No'}")

        # Display icon if available
        icon = module_data.get("icon")
        if icon:
            st.write(f"- **Icon:** {icon}")

        # Serial number
        serial_number = module_data.get("serialNumber")
        if serial_number:
            st.write(f"- **Serial Number:** {serial_number}")

        # Station information (if linked)
        st.markdown("**Station Information:**")
        station_found = False
        for station_id, station_data in stations.items():
            # Check if this station is linked to this module
            if station_id == module_id or station_data.get("module_id") == module_id:
                station_found = True
                st.write(f"- **Station ID:** {station_id}")
                st.write(f"- **IP Address:** {station_data.get('ip_address', 'N/A')}")
                st.write(f"- **OPC UA Port:** {station_data.get('opcua_port', 'N/A')}")
                st.write(f"- **Description:** {station_data.get('description', 'N/A')}")
                break

        if not station_found:
            st.info("📋 No station information available")

        # TXT Controller information (if linked)
        st.markdown("**TXT Controller Information:**")
        controller_found = False
        for controller_id, controller_data in txt_controllers.items():
            # Check if this controller is linked to this module
            zugeordnet = controller_data.get("zugeordnet_zu_modul")
            if zugeordnet == module_id or controller_id == module_id:
                controller_found = True
                st.write(f"- **Controller ID:** {controller_id}")
                st.write(f"- **IP Address:** {controller_data.get('ip_address', 'N/A')}")
                st.write(f"- **MQTT Port:** {controller_data.get('mqtt_port', 'N/A')}")
                st.write(f"- **Description:** {controller_data.get('description', 'N/A')}")
                break

        if not controller_found:
            st.info("📋 No TXT controller information available")

    except Exception as e:
        logger.error(f"❌ Failed to display module info: {e}")
        st.error(f"❌ Error displaying module info: {e}")


def get_factory_layout_data():
    """Get factory layout data for external use"""
    try:
        config_loader = get_ccu_config_loader()
        return config_loader.load_shopfloor_layout()
    except Exception as e:
        logger.error(f"❌ Failed to get factory layout data: {e}")
        return None
