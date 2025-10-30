#!/usr/bin/env python3
"""
CCU Modules Tab - CCU Module Management with Real-time MQTT Data
"""


import pandas as pd
import streamlit as st

from omf2.ccu.module_manager import get_ccu_module_manager
from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.ui.common.symbols import UISymbols, get_icon_html

logger = get_logger(__name__)


def reload_modules():
    """
    Reload module data into session state

    This wrapper function triggers a reload of module data from ModuleManager
    and stores it in session state for use by the UI rendering logic.
    """
    try:
        logger.debug("🔄 reload_modules() called - refreshing module data")
        module_manager = get_ccu_module_manager()

        # Get fresh module data
        modules = module_manager.get_all_modules()

        # Store in session state
        st.session_state["modules_data_refreshed"] = True
        st.session_state["modules_last_reload"] = pd.Timestamp.now()

        logger.debug(f"✅ Module data refreshed: {len(modules)} modules")

    except Exception as e:
        logger.error(f"❌ Error in reload_modules(): {e}")


def render_ccu_modules_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Modules Tab - CCU Module Management with Real-time MQTT Data"""
    logger.info("🏗️ Rendering CCU Modules Tab")
    try:
        # Add auto-refresh support using the same pattern as production_orders_subtab
        try:
            from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload

            # Use module_updates refresh group with polling + compare
            check_and_reload(group="module_updates", reload_callback=reload_modules, interval_ms=1000)

        except Exception as e:
            logger.debug(f"⚠️ Auto-refresh not available: {e}")
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # Use UISymbols for consistent icon usage - with SVG support
        header_icon = get_icon_html('MODULES_TAB', size_px=32)
        st.markdown(
            f"{header_icon} <span style='font-size: 32px; vertical-align: middle;'>{i18n.translate('tabs.ccu_modules')}</span>",
            unsafe_allow_html=True
        )
        st.markdown(i18n.t("ccu_modules.subtitle"))

        # Gateway-Pattern: Get CcuGateway from Factory (EXACT like Admin)
        from omf2.factory.gateway_factory import get_ccu_gateway

        ccu_gateway = get_ccu_gateway()
        if not ccu_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} {i18n.t('ccu_modules.error.gateway_not_available')}")
            return

        # Initialize Registry Manager if not provided
        if not registry_manager:
            registry_manager = get_registry_manager()

        # Initialize CCU Module Manager
        get_ccu_module_manager()

        # Module Overview Controls
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button(
                f"{UISymbols.get_status_icon('refresh')} {i18n.t('ccu_modules.controls.refresh_status')}",
                use_container_width=True,
                key="module_refresh_status",
            ):
                _refresh_module_status(ccu_gateway, i18n)

        with col2:
            if st.button(
                f"{UISymbols.get_functional_icon('dashboard')} {i18n.t('ccu_modules.controls.show_statistics')}",
                use_container_width=True,
                key="module_show_statistics",
            ):
                _show_module_statistics(ccu_gateway, i18n)

        with col3:
            if st.button(
                f"{UISymbols.get_functional_icon('settings')} {i18n.t('ccu_modules.controls.module_settings')}",
                use_container_width=True,
                key="module_settings",
            ):
                _show_module_settings(i18n)

        st.divider()

        # Module Overview Table - ECHTE MQTT-Daten
        _show_module_overview_table(ccu_gateway, i18n)

        # Module Details - IMMER ANZEIGEN
        st.divider()
        from omf2.ui.ccu.ccu_modules.ccu_modules_details import show_module_details_section

        show_module_details_section(ccu_gateway, i18n)

        # CCU Message Monitor - ECHTE MQTT-Daten über Gateway
        st.divider()
        from omf2.ui.ccu.ccu_message_monitor import render_ccu_message_monitor

        render_ccu_message_monitor(ccu_gateway, "CCU Message Monitor", show_controls=True)

    except Exception as e:
        logger.error(f"❌ CCU Modules Tab error: {e}")
        i18n = st.session_state.get("i18n_manager")
        if i18n:
            error_msg = i18n.t("ccu_modules.error.tab_failed").format(error=e)
            st.error(f"❌ {error_msg}")
        else:
            st.error(f"❌ CCU Modules Tab failed: {e}")


def _show_module_overview_table(ccu_gateway, i18n):
    """Show Module Overview Table - ECHTE MQTT-Daten vom ccu_gateway mit Module Manager"""
    try:
        logger.info("📊 Showing Module Overview Table")

        # Initialize Module Manager
        module_manager = get_ccu_module_manager()

        # Get modules from Module Manager
        modules = module_manager.get_all_modules()
        if not modules:
            st.info(f"📋 {i18n.t('ccu_modules.overview.no_modules')}")
            return

        # NEU: Business-Manager Pattern - lese aus Manager State-Holder
        # Module-Status wird automatisch über MQTT-Callbacks aktualisiert
        status_store = module_manager.get_module_status_from_state()  # Liest aus State-Holder

        # Display real-time status info with refresh indicator
        if status_store:
            status_msg = i18n.t("ccu_modules.overview.real_time_status").format(count=len(status_store))
            st.info(f"📊 {status_msg}")
            st.success(f"✅ **{i18n.t('ccu_modules.overview.auto_updated')}**")
        else:
            st.warning(f"⚠️ {i18n.t('ccu_modules.overview.no_status_data')}")

        # Render custom table with SVG icons
        _render_module_table_with_svg_icons(modules, status_store, module_manager, i18n)

        # Show real-time statistics
        _show_module_statistics_summary(status_store, i18n)

    except Exception as e:
        logger.error(f"❌ Module Overview Table error: {e}")
        error_msg = i18n.t("ccu_modules.error.table_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _render_module_table_with_svg_icons(modules, status_store, module_manager, i18n):
    """
    Render module table with SVG icons using st.markdown for proper HTML rendering.

    This approach allows SVG icons to be properly displayed instead of showing HTML as text.
    """
    try:
        # Build HTML table with SVG icons
        table_html = '<table style="width: 100%; border-collapse: collapse;">'

        # Header row
        table_html += '<thead><tr style="background-color: #f0f2f6; border-bottom: 2px solid #ddd;">'
        headers = [
            i18n.t("ccu_modules.table.id"),
            i18n.t("ccu_modules.table.name"),
            i18n.t("ccu_modules.table.registry_active"),
            i18n.t("ccu_modules.table.position"),
            i18n.t("ccu_modules.table.configured"),
            i18n.t("ccu_modules.table.connected"),
            i18n.t("ccu_modules.table.availability_status"),
            i18n.t("ccu_modules.table.messages"),
            i18n.t("ccu_modules.table.last_update"),
        ]
        for header in headers:
            table_html += f'<th style="padding: 8px; text-align: left; font-weight: bold;">{header}</th>'
        table_html += '</tr></thead>'

        # Body rows
        table_html += '<tbody>'
        for module_id, module_info in modules.items():
            if not module_info.get("enabled", True):
                continue

            # Get real-time status
            real_time_status = module_manager.get_module_status_from_state(module_id)

            # Get module icon with SVG support
            icon_html = _get_module_icon_html(module_id, size_px=20)
            display_name = _get_module_display_name(module_id, module_info)

            # Get status displays
            connected = real_time_status.get("connected", False)
            connection_display = module_manager.get_connection_display(connected)

            available = real_time_status.get("available", "Unknown")
            availability_display = module_manager.get_availability_display(available)

            factory_config = module_manager.get_factory_configuration()
            configured = module_manager.is_module_configured(module_id, factory_config)
            configured_display = module_manager.get_configuration_display(configured)

            position_display = module_manager.get_module_position_display(module_id)
            message_count = real_time_status.get("message_count", 0)
            last_update = real_time_status.get("last_update", "Never")

            registry_active = "✅ Active" if module_info.get("enabled", True) else "❌ Inactive"

            # Add row
            table_html += '<tr style="border-bottom: 1px solid #ddd;">'
            table_html += f'<td style="padding: 8px;">{module_id}</td>'
            table_html += f'<td style="padding: 8px;">{icon_html} {display_name}</td>'
            table_html += f'<td style="padding: 8px;">{registry_active}</td>'
            table_html += f'<td style="padding: 8px;">{position_display}</td>'
            table_html += f'<td style="padding: 8px;">{configured_display}</td>'
            table_html += f'<td style="padding: 8px;">{connection_display}</td>'
            table_html += f'<td style="padding: 8px;">{availability_display}</td>'
            table_html += f'<td style="padding: 8px;">{message_count}</td>'
            table_html += f'<td style="padding: 8px;">{last_update}</td>'
            table_html += '</tr>'

        table_html += '</tbody></table>'

        # Render table with HTML
        st.markdown(table_html, unsafe_allow_html=True)

        # Show diagnostic information
        svg_count = table_html.count('<svg')
        span_count = table_html.count('<span style="font-size:')
        st.caption(f"✨ Module icons rendered as SVG graphics ({svg_count} SVG icons, {span_count} emoji fallbacks)")

    except Exception as e:
        logger.error(f"❌ Failed to render custom table: {e}")
        # Fallback to simple display
        st.error(f"⚠️ Could not render custom table: {e}")


def _get_module_display_name(module_id, module_info):
    """Get display name for module"""
    return module_info.get("name", module_id)


def _get_module_icon_html(module_id, size_px=24):
    """
    Get module icon as HTML with SVG support via Module Manager.

    Uses Module Manager's get_module_icon_html() which maps serial ID → type → SVG.

    Args:
        module_id: Module serial ID (e.g., "SVR3QA0022")
        size_px: Size in pixels for the icon

    Returns:
        HTML string with inline SVG or emoji span

    Example:
        >>> _get_module_icon_html("SVR3QA0022", size_px=28)
        '<svg width="28"...>...</svg>'  # HBW SVG
    """
    try:
        # Use Module Manager's method which handles serial ID → type mapping
        module_manager = get_ccu_module_manager()
        result = module_manager.get_module_icon_html(module_id, size_px=size_px)

        # Log success for debugging
        if "<svg" in result:
            logger.debug(f"✅ Got SVG icon for {module_id} ({len(result)} chars)")
        else:
            logger.warning(f"⚠️ No SVG icon for {module_id}, got fallback: {result[:50]}")

        return result
    except Exception as e:
        logger.error(f"❌ Failed to get icon HTML for {module_id}: {type(e).__name__}: {e}")
        # Fallback to module manager emoji icon
        try:
            module_manager = get_ccu_module_manager()
            emoji_icon = module_manager.get_module_icon(module_id)
            return f'<span style="font-size: {size_px}px;">{emoji_icon}</span>'
        except Exception as e2:
            logger.error(f"❌ Fallback also failed: {e2}")
            return f'<span style="font-size: {size_px}px;">⚙️</span>'


# REMOVED: _get_module_icon() - Icons are now managed by Registry via ModuleManager
# All module icons are defined in registry/modules.yml and loaded via ModuleManager.get_module_icon()


def _is_module_configured(module_id, ccu_gateway):
    """Check if module is configured in factory"""
    try:
        # Get factory configuration
        factory_config = ccu_gateway.get_factory_configuration()
        if factory_config and "modules" in factory_config:
            modules = factory_config["modules"]
            return module_id in modules
        return False
    except Exception as e:
        logger.warning(f"⚠️ Could not check module configuration: {e}")
        return False


def _refresh_module_status(ccu_gateway, i18n):
    """Refresh module status from MQTT data"""
    try:
        logger.info("🔄 Refreshing module status")

        # Initialize Module Manager
        module_manager = get_ccu_module_manager()

        # Process module messages and update status store
        status_store = module_manager.get_module_status_from_state()  # Liest aus State-Holder

        st.success(f"✅ {i18n.t('ccu_modules.status.refresh_success')}")
        logger.info(f"📊 Refreshed status for {len(status_store)} modules")

        # CRITICAL: Request UI refresh to update the display
        from omf2.ui.utils.ui_refresh import request_refresh

        request_refresh()

    except Exception as e:
        logger.error(f"❌ Failed to refresh module status: {e}")
        error_msg = i18n.t("ccu_modules.error.refresh_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _show_module_statistics(ccu_gateway, i18n):
    """Show module statistics"""
    try:
        logger.info("📊 Showing module statistics")

        # Initialize Module Manager
        module_manager = get_ccu_module_manager()

        # Get modules from Module Manager
        modules = module_manager.get_all_modules()

        # Get status store
        status_store = st.session_state.get("ccu_module_status_store", {})

        # Calculate statistics
        total_modules = len(modules)
        connected_modules = sum(1 for status in status_store.values() if status.get("connected", False))
        available_modules = sum(1 for status in status_store.values() if status.get("available") == "READY")

        # Get configured modules count from Module Manager
        factory_config = module_manager.get_factory_configuration()
        configured_modules = sum(
            1 for module_id in modules.keys() if module_manager.is_module_configured(module_id, factory_config)
        )

        # Display statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(i18n.t("ccu_modules.statistics.total_modules"), total_modules)

        with col2:
            st.metric(i18n.t("ccu_modules.statistics.connected"), connected_modules)

        with col3:
            st.metric(i18n.t("ccu_modules.statistics.available"), available_modules)

        with col4:
            st.metric(i18n.t("ccu_modules.statistics.configured"), configured_modules)

        # Show detailed status
        st.markdown(f"#### 📊 {i18n.t('ccu_modules.statistics.detailed_status')}")
        for module_id, status in status_store.items():
            st.write(
                f"**{module_id}**: Connected={status.get('connected', False)}, Available={status.get('available', 'Unknown')}"
            )

    except Exception as e:
        logger.error(f"❌ Failed to show module statistics: {e}")
        error_msg = i18n.t("ccu_modules.error.statistics_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _show_module_statistics_summary(status_store, i18n):
    """Show module statistics summary"""
    try:
        if not status_store:
            return

        # Calculate summary statistics
        total_modules = len(status_store)
        connected_modules = sum(1 for status in status_store.values() if status.get("connected", False))
        available_modules = sum(1 for status in status_store.values() if status.get("available") == "READY")

        # Get configured modules count from Module Manager
        module_manager = get_ccu_module_manager()
        factory_config = module_manager.get_factory_configuration()
        modules = module_manager.get_all_modules()
        configured_modules = sum(
            1 for module_id in modules.keys() if module_manager.is_module_configured(module_id, factory_config)
        )

        # Display summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(i18n.t("ccu_modules.statistics.total"), total_modules)

        with col2:
            st.metric(i18n.t("ccu_modules.statistics.connected"), connected_modules)

        with col3:
            st.metric(i18n.t("ccu_modules.statistics.available"), available_modules)

        with col4:
            st.metric(i18n.t("ccu_modules.statistics.configured"), configured_modules)

        # Add SVG Module Icons Display Section
        _show_module_icons_gallery(modules, i18n)

    except Exception as e:
        logger.error(f"❌ Failed to show module statistics summary: {e}")
        error_msg = i18n.t("ccu_modules.error.statistics_summary_failed").format(error=e)
        logger.error(error_msg)


def _show_module_icons_gallery(modules, i18n):
    """
    Display a gallery of module icons using SVG rendering.

    This demonstrates consistent usage of get_icon_html() for visual representation
    of all available module types with their SVG icons.
    """
    try:
        st.markdown("---")
        st.markdown("### 🎨 Module Icons Gallery (SVG-first Rendering)")
        st.caption("Demonstrating SVG icon rendering with automatic fallback to emoji")

        # Get list of module types
        module_types = list(modules.keys())

        # Display icons in a grid layout
        cols_per_row = 6
        for i in range(0, len(module_types), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(module_types):
                    module_id = module_types[i + j]
                    with col:
                        # Get SVG icon HTML
                        icon_html = _get_module_icon_html(module_id, size_px=48)

                        # Display using st.markdown for proper HTML rendering
                        st.markdown(
                            f"""
                            <div style="text-align: center; padding: 10px; border: 1px solid #ddd; border-radius: 8px;">
                                <div style="margin-bottom: 8px;">{icon_html}</div>
                                <div style="font-size: 12px; font-weight: bold;">{module_id}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        st.caption("✨ Icons automatically use SVG graphics when available, with emoji fallback for compatibility")

    except Exception as e:
        logger.debug(f"⚠️ Could not display module icons gallery: {e}")


def _show_module_settings(i18n):
    """Show module settings"""
    try:
        logger.info("⚙️ Showing module settings")
        st.info(f"📋 {i18n.t('ccu_modules.status.settings_info')}")

    except Exception as e:
        logger.error(f"❌ Failed to show module settings: {e}")
        error_msg = i18n.t("ccu_modules.error.settings_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _calibrate_module(module_id, ccu_gateway, i18n):
    """Calibrate a specific module"""
    try:
        logger.info(f"🔧 Calibrating module {module_id}")

        # TODO: Implement actual calibration logic
        success_msg = i18n.t("ccu_modules.status.calibration_started").format(module_id=module_id)
        st.success(f"✅ {success_msg}")

    except Exception as e:
        logger.error(f"❌ Failed to calibrate module {module_id}: {e}")
        error_msg = i18n.t("ccu_modules.error.calibration_failed").format(module_id=module_id, error=e)
        st.error(f"❌ {error_msg}")


def _dock_fts(module_id, ccu_gateway, i18n):
    """Dock FTS module"""
    try:
        logger.info(f"🚗 Docking FTS module {module_id}")

        # TODO: Implement actual docking logic
        success_msg = i18n.t("ccu_modules.status.docking_started").format(module_id=module_id)
        st.success(f"✅ {success_msg}")

    except Exception as e:
        logger.error(f"❌ Failed to dock FTS module {module_id}: {e}")
        error_msg = i18n.t("ccu_modules.error.docking_failed").format(module_id=module_id, error=e)
        st.error(f"❌ {error_msg}")


def _undock_fts(module_id, ccu_gateway, i18n):
    """Undock FTS module"""
    try:
        logger.info(f"🚗 Undocking FTS module {module_id}")

        # TODO: Implement actual undocking logic
        success_msg = i18n.t("ccu_modules.status.undocking_started").format(module_id=module_id)
        st.success(f"✅ {success_msg}")

    except Exception as e:
        logger.error(f"❌ Failed to undock FTS module {module_id}: {e}")
        error_msg = i18n.t("ccu_modules.error.undocking_failed").format(module_id=module_id, error=e)
        st.error(f"❌ {error_msg}")
