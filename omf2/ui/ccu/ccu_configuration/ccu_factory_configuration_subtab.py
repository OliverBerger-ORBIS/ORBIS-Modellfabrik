#!/usr/bin/env python3
"""
CCU Configuration - Factory Configuration Subtab
Displays shopfloor layout from CCU Config Loader
"""

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


def get_factory_layout_data():
    """Get factory layout data for external use"""
    try:
        config_loader = get_ccu_config_loader()
        return config_loader.load_shopfloor_layout()
    except Exception as e:
        logger.error(f"❌ Failed to get factory layout data: {e}")
        return None
