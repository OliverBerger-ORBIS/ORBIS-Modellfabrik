#!/usr/bin/env python3
"""
CCU Modules Details - Module Details Section
Ausgelagerte Funktionalität für Module-Details
"""

from pathlib import Path

import streamlit as st

from omf2.ccu.module_manager import get_ccu_module_manager
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def show_module_details_section(ccu_gateway, i18n):
    """Show module details section with dropdown selection - PERFORMANCE OPTIMIERT"""
    try:
        st.markdown("### 🔧 Module Details")

        # Check if we have a preselected module from navigation (double-click)
        preselected_module_id = st.session_state.get("preselected_module_id")
        if preselected_module_id:
            logger.info(f"🚀 Preselected module detected: {preselected_module_id}")

        # CACHING: Alle Manager und Daten nur einmal laden
        # Cache invalidieren wenn nötig (z.B. bei Refresh)
        if "module_details_cache" not in st.session_state or st.button(
            "🔄 Refresh Module Cache", key="refresh_module_cache"
        ):
            if "refresh_module_cache" in st.session_state and st.session_state.refresh_module_cache:
                # Cache löschen
                if "module_details_cache" in st.session_state:
                    del st.session_state.module_details_cache
                st.session_state.refresh_module_cache = False

            # ALLE MANAGER CACHEN
            module_manager = get_ccu_module_manager()
            from omf2.assets import get_asset_manager

            asset_manager = get_asset_manager()

            modules = module_manager.get_all_modules()

            # Module-Options mit Icons cachen
            module_options = {}
            for module_id, module_info in modules.items():
                module_icon = module_manager.get_module_icon(module_id)
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

        if not modules:
            st.info("📋 No modules available")
            return

        # Find the index of preselected module if it exists
        default_index = 0
        if preselected_module_id:
            for i, (display_name, module_id) in enumerate(module_options.items()):
                if module_id == preselected_module_id:
                    default_index = i
                    logger.info(f"✅ Found preselected module at index {i}: {display_name}")
                    break

        selected_module_display = st.selectbox(
            "Select Module for Details:", 
            options=list(module_options.keys()), 
            index=default_index,
            key="module_details_selector"
        )

        # Clear preselected module after it's been used
        if preselected_module_id:
            st.session_state.pop("preselected_module_id", None)
            st.session_state.pop("preselected_module_type", None)
            st.session_state.pop("show_module_details", None)
            logger.info("✅ Cleared preselected module from session state")

        if selected_module_display:
            selected_module_id = module_options[selected_module_display]
            selected_module_type = modules[selected_module_id].get("type", "unknown")

            # Zeige Module-Details
            _show_production_module_details(selected_module_id, selected_module_type, ccu_gateway, i18n)

    except Exception as e:
        logger.error(f"❌ Failed to show module details section: {e}")
        st.error(f"❌ Error: {e}")


def _show_production_module_details(module_id: str, module_type: str, ccu_gateway, i18n):
    """Show details for production modules (MILL, DRILL, AIQS, HBW, DPS, CHRG) - PERFORMANCE OPTIMIERT"""
    try:
        st.header(f"🏭 {module_type} Module Details")

        # MODULE MANAGER AUS CACHE VERWENDEN
        cache = st.session_state.get("module_details_cache", {})
        module_manager = cache.get("module_manager")

        if not module_manager:
            # Fallback: Module Manager neu erstellen
            module_manager = get_ccu_module_manager()

        # Get module status
        module_status = module_manager.get_module_status_from_state(module_id)

        # Get factsheet status
        factsheet_status = module_manager.get_module_factsheet_status(module_id)

        # Two columns: SVG and Details
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("📊 Module SVG")
            # Get module_info from Module Manager
            module_info = module_manager.get_all_modules().get(module_id, {})
            _show_module_svg(module_id, module_type, module_info, i18n)

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


def _show_module_svg(module_id: str, module_type: str, module_info: dict, i18n):
    """Show module SVG using Asset Manager - PERFORMANCE OPTIMIERT"""
    try:
        # ASSET MANAGER AUS CACHE VERWENDEN
        cache = st.session_state.get("module_details_cache", {})
        asset_manager = cache.get("asset_manager")

        if not asset_manager:
            # Fallback: Asset Manager neu erstellen
            from omf2.assets import get_asset_manager

            asset_manager = get_asset_manager()

        # ICON ÜBER DEN NAMEN SUCHEN - WIE ANGEORDNET
        module_name = module_info.get("name", module_type)
        icon_path = asset_manager.get_module_icon_path(module_name)

        if icon_path and Path(icon_path).exists():
            # SVG laden und skalieren - WIE IN SHOPFLOOR_LAYOUT
            with open(icon_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # ViewBox-bewusste Skalierung - keine Verzerrung!
                svg_content = _scale_svg_properly(svg_content, 200, 200)
                # IMPORT FEHLT!
                import streamlit.components.v1 as components

                components.html(svg_content, height=200)
        else:
            st.info(f"📋 {i18n.t('ccu_modules.details.no_svg_available')}")

    except Exception as e:
        logger.error(f"❌ Failed to show module SVG: {e}")
        st.error(f"❌ Error loading module SVG: {e}")


def _scale_svg_properly(svg_content: str, width: int, height: int) -> str:
    """KORREKTE SVG-Skalierung - EINFACH UND FUNKTIONAL"""
    try:
        # EINFACHE LÖSUNG: Direkte width/height setzen
        # Alle SVGs haben viewBox="0 0 24 24" - das ist standardisiert

        # SVG mit korrekten Dimensionen
        scaled_svg = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"')

        # DEBUG: Log the scaling
        logger.info(f"🔍 SVG Scaling: {width}x{height} applied")

        return scaled_svg

    except Exception as e:
        logger.warning(f"Could not scale SVG properly: {e}")
        return svg_content


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
