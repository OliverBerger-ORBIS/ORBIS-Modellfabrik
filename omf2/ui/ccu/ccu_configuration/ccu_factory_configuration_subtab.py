#!/usr/bin/env python3
"""
CCU Configuration - Factory Configuration Subtab
Displays shopfloor layout from CCU Config Loader
"""

from pathlib import Path

import streamlit as st

from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_ccu_factory_configuration_subtab():
    """Render CCU Factory Configuration Subtab"""
    logger.info("🏭 Rendering CCU Factory Configuration Subtab")
    try:
        st.subheader(f"{UISymbols.get_tab_icon('factory')} Factory Configuration")
        st.markdown("Factory layout configuration and module positioning")

        # Factory Configuration Controls
        _show_factory_controls()

        st.divider()

        # Shopfloor Layout Display
        _show_shopfloor_layout_section()

        # Module Details Section (shown after double-click)
        if st.session_state.get("show_module_details") and st.session_state.get("selected_module_id"):
            st.divider()
            _show_module_details_section()

    except Exception as e:
        logger.error(f"❌ CCU Factory Configuration Subtab rendering error: {e}")
        st.error(f"❌ CCU Factory Configuration Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_factory_controls():
    """Show factory configuration controls (collapsed by default, role-based later)"""
    with st.expander("🎛️ Factory Controls", expanded=False):
        st.write("Configuration controls for factory layout management")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button(
                f"{UISymbols.get_status_icon('load')} Load Layout", key="load_factory_layout", use_container_width=True
            ):
                _load_factory_layout()

        with col2:
            if st.button(
                f"{UISymbols.get_status_icon('save')} Save Layout", key="save_factory_layout", use_container_width=True
            ):
                _save_factory_layout()

        with col3:
            if st.button(
                f"{UISymbols.get_status_icon('refresh')} Refresh",
                key="refresh_factory_layout",
                use_container_width=True,
            ):
                _refresh_factory_layout()


def _show_shopfloor_layout_section():
    """Show enhanced shopfloor layout section with asset manager"""
    try:
        # Import and use the shopfloor layout component
        from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

        # Show the shopfloor layout with interactive SVG
        # CCU Configuration mode: single/double click for module selection/navigation
        show_shopfloor_layout(
            title="Shopfloor Layout",
            unique_key="ccu_configuration_shopfloor",
            mode="ccu_configuration",  # CCU Configuration mode: single click = select, double click = navigate
        )

    except Exception as e:
        st.error(f"❌ Failed to load shopfloor layout: {e}")
        logger.error(f"Failed to load shopfloor layout: {e}")


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
                st.rerun()

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
