#!/usr/bin/env python3
"""
CCU Modules Tab - CCU Module Management with Real-time MQTT Data
"""


import pandas as pd
import streamlit as st

from omf2.ccu.module_manager import get_ccu_module_manager
from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_modules_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Modules Tab - CCU Module Management with Real-time MQTT Data"""
    logger.info("🏗️ Rendering CCU Modules Tab")
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # Use UISymbols for consistent icon usage
        st.header(f"{UISymbols.get_tab_icon('ccu_modules')} {i18n.translate('tabs.ccu_modules')}")
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

        module_table_data = []
        for module_id, module_info in modules.items():
            if not module_info.get("enabled", True):
                continue

            # Get real-time status from Module Manager State-Holder
            real_time_status = module_manager.get_module_status_from_state(module_id)

            # Get module icon and display name from Module Manager (Registry-based)
            icon_display = module_manager.get_module_icon(module_id)
            display_name = _get_module_display_name(module_id, module_info)

            # Get connection and availability display from Module Manager
            connected = real_time_status.get("connected", False)
            connection_display = module_manager.get_connection_display(connected)

            available = real_time_status.get("available", "Unknown")
            availability_display = module_manager.get_availability_display(available)

            # Get configured status from Module Manager (UISymbols-based)
            factory_config = module_manager.get_factory_configuration()
            configured = module_manager.is_module_configured(module_id, factory_config)
            configured_display = module_manager.get_configuration_display(configured)

            # Get message count and last update
            message_count = real_time_status.get("message_count", 0)
            last_update = real_time_status.get("last_update", "Never")

            module_table_data.append(
                {
                    i18n.t("ccu_modules.table.id"): module_id,
                    i18n.t("ccu_modules.table.name"): f"{icon_display} {display_name}",
                    i18n.t("ccu_modules.table.connected"): connection_display,
                    i18n.t("ccu_modules.table.availability_status"): availability_display,
                    i18n.t("ccu_modules.table.configured"): configured_display,
                    i18n.t("ccu_modules.table.messages"): message_count,
                    i18n.t("ccu_modules.table.last_update"): last_update,
                }
            )

        if module_table_data:
            df = pd.DataFrame(module_table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Show real-time statistics
            _show_module_statistics_summary(status_store, i18n)
        else:
            st.info(f"📋 {i18n.t('ccu_modules.overview.no_modules_available')}")

    except Exception as e:
        logger.error(f"❌ Module Overview Table error: {e}")
        error_msg = i18n.t("ccu_modules.error.table_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _get_module_display_name(module_id, module_info):
    """Get display name for module"""
    return module_info.get("name", module_id)


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

    except Exception as e:
        logger.error(f"❌ Failed to show module statistics summary: {e}")
        error_msg = i18n.t("ccu_modules.error.statistics_summary_failed").format(error=e)
        logger.error(error_msg)


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
