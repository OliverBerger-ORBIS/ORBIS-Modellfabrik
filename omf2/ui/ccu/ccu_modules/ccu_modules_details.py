#!/usr/bin/env python3
"""
CCU Modules Details - Module Details Section
Ausgelagerte Funktionalität für Module-Details
"""


import streamlit as st

from omf2.ccu.module_manager import get_ccu_module_manager
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def _show_module_svg(
    module_id: str, module_type: str = None, module_info: dict = None, i18n=None, size_px: int = 24
) -> str:
    """Return SVG HTML for a module using Module Manager (test helper).

    This small wrapper keeps backward compatibility with integration tests
    expecting a dedicated function for SVG generation.
    """
    try:
        module_manager = get_ccu_module_manager()
        return module_manager.get_module_icon_html(module_id, size_px=size_px)
    except Exception:
        # Fallback to emoji span to avoid hard failures in tests/UI if icon lookup fails
        return f'<span style="font-size: {size_px}px;">⚙️</span>'


def show_module_details_section(ccu_gateway, i18n):
    """Show module details section with dropdown selection - PERFORMANCE OPTIMIERT"""
    try:
        # Use SVG icon in header with st.markdown
        st.markdown("### 🔧 Module Details")
        st.caption("💡 Select a module to view detailed information with SVG icons")

        # CACHING: Load managers and data once, refresh happens via auto-refresh mechanism
        # Cache is initialized once per session and refreshed automatically via check_and_reload()
        if "module_details_cache" not in st.session_state:
            # ALLE MANAGER CACHEN
            module_manager = get_ccu_module_manager()
            from omf2.assets import get_asset_manager

            asset_manager = get_asset_manager()

            modules = module_manager.get_all_modules()

            # Module-Options mit Icons cachen
            # Note: st.selectbox doesn't render HTML, so we use emoji icons here
            # SVG icons are shown in the expanded details and visual list below
            module_options = {}
            for module_id, module_info in modules.items():
                module_icon = module_manager.get_module_icon(module_id)  # Emoji for selectbox
                module_name = module_info.get("name", module_id)
                serial_id = module_info.get("serialNumber", module_id)
                display_name = f"{module_icon} {module_name} ({serial_id})"
                module_options[display_name] = module_id

            # ALLE MANAGER UND DATEN CACHEN
            st.session_state.module_details_cache = {
                "modules": modules,
                "module_options": module_options,
                "module_manager": module_manager,
                "asset_manager": asset_manager,
            }

        # Cached data verwenden
        cache = st.session_state.module_details_cache
        modules = cache["modules"]
        module_options = cache["module_options"]
        module_manager = cache["module_manager"]

        if not modules:
            st.info("📋 No modules available")
            return

        # Show visual module list with SVG icons before selectbox
        st.markdown("**Available Modules (with SVG icons):**")
        _show_module_icons_list(modules, module_manager)

        # Selectbox with emoji icons (HTML not supported in selectbox)
        selected_module_display = st.selectbox(
            "Select Module for Details:", options=list(module_options.keys()), key="module_details_selector"
        )

        if selected_module_display:
            selected_module_id = module_options[selected_module_display]
            selected_module_type = modules[selected_module_id].get("type", "unknown")

            # Zeige Module-Details
            _show_production_module_details(selected_module_id, selected_module_type, ccu_gateway, i18n)

    except Exception as e:
        logger.error(f"❌ Failed to show module details section: {e}")
        st.error(f"❌ Error: {e}")


def _show_module_icons_list(modules, module_manager):
    """
    Display a visual list of all modules with their SVG icons.

    This provides a consistent visual reference using SVG icons,
    complementing the selectbox which uses emoji icons.
    """
    try:
        # Create HTML list with SVG icons
        html_list = '<div style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin-bottom: 10px;">'

        for module_id, module_info in modules.items():
            module_name = module_info.get("name", module_id)
            serial_id = module_info.get("serialNumber", module_id)

            # Get SVG icon using Module Manager's method
            icon_html = module_manager.get_module_icon_html(module_id, size_px=20)

            # Add to list
            html_list += f'<div style="padding: 4px 0;">{icon_html} <strong>{module_name}</strong> ({serial_id})</div>'

        html_list += "</div>"

        # Render with st.markdown
        st.markdown(html_list, unsafe_allow_html=True)

        # Show count
        svg_count = sum(1 for m in modules.values() if m.get("name"))
        st.caption(f"✨ Module icons rendered as SVG graphics ({svg_count} modules)")

    except Exception as e:
        logger.warning(f"⚠️ Could not display module icons list: {e}")


def _show_production_module_details(module_id: str, module_type: str, ccu_gateway, i18n):
    """Show details for production modules (MILL, DRILL, AIQS, HBW, DPS, CHRG) - PERFORMANCE OPTIMIERT"""
    try:
        # Use Module Manager to get SVG icon for header
        cache = st.session_state.get("module_details_cache", {})
        module_manager = cache.get("module_manager")

        if not module_manager:
            # Fallback: Module Manager neu erstellen
            module_manager = get_ccu_module_manager()

        # Get module info
        module_info = module_manager.get_all_modules().get(module_id, {})
        module_name = module_info.get("name", module_type)

        # Get SVG icon for header using Module Manager
        header_icon_html = module_manager.get_module_icon_html(module_id, size_px=32)

        # Render header with SVG icon
        st.markdown(f"### {header_icon_html} {module_name} Module Details", unsafe_allow_html=True)

        # Get module status
        module_status = module_manager.get_module_status_from_state(module_id)

        # Get factsheet status
        factsheet_status = module_manager.get_module_factsheet_status(module_id)

        # Two columns: SVG and Details
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📊 Module Icon")
            # Display large SVG icon using Module Manager
            large_icon_html = module_manager.get_module_icon_html(module_id, size_px=200)
            st.markdown(
                f'<div style="text-align: center; padding: 20px;">{large_icon_html}</div>', unsafe_allow_html=True
            )
            st.caption("✨ High-quality SVG icon with CSS scoping")

        with col2:
            st.subheader("📋 Module Information")
            _show_module_info(module_id, module_type, module_status, factsheet_status, i18n)

    except Exception as e:
        logger.error(f"❌ Failed to show production module details: {e}")
        st.error(f"❌ Error showing production module details: {e}")


def _show_storage_module_details(module_id: str, module_type: str, ccu_gateway, i18n):
    """Show details for storage modules (shelves, conveyor_belt, warehouse)"""
    # DELEGATION - KEINE DUPLIKATION
    _show_production_module_details(module_id, module_type, ccu_gateway, i18n)


def _show_generic_module_details(module_id: str, module_type: str, ccu_gateway, i18n):
    """Show details for generic modules"""
    # DELEGATION - KEINE DUPLIKATION
    _show_production_module_details(module_id, module_type, ccu_gateway, i18n)


def _show_module_info(module_id: str, module_type: str, module_status: dict, factsheet_status: dict, i18n):
    """Show module information including factsheet data"""
    try:
        # Basic module info
        st.write(f"**Module ID:** {module_id}")
        st.write(f"**Module Type:** {module_type}")

        # Module status
        if module_status:
            st.write("**Status:**")
            for key, value in module_status.items():
                st.write(f"  - {key}: {value}")
        else:
            st.info("📋 No status data available")

        # Factsheet information
        if factsheet_status:
            st.write("**Factsheet Information:**")
            factsheet_data = factsheet_status.get("factsheet_data", {})
            if factsheet_data:
                for key, value in factsheet_data.items():
                    st.write(f"  - {key}: {value}")
            else:
                st.info("📋 No factsheet data available")
        else:
            st.info("📋 No factsheet available")

    except Exception as e:
        logger.error(f"❌ Failed to show module info: {e}")
        st.error(f"❌ Error showing module info: {e}")
