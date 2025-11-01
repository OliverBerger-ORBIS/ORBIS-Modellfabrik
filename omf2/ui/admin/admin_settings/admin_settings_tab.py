#!/usr/bin/env python3
"""
Admin Settings Tab - Admin Settings UI Component
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.factory.gateway_factory import get_admin_gateway
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_admin_settings_tab():
    """Render Admin Settings Tab with Subtabs"""
    logger.info(f"{UISymbols.get_tab_icon('admin_settings')} Rendering Admin Settings Tab")
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        st.header(f"{UISymbols.get_tab_icon('admin_settings')} {i18n.translate('tabs.admin_settings')}")
        st.markdown(i18n.t("admin.settings.subtitle"))

        # Gateway-Pattern: Get AdminGateway from Factory
        admin_gateway = get_admin_gateway()
        if not admin_gateway:
            st.error(f"{UISymbols.get_status_icon('error')} {i18n.t('admin.settings.gateway_not_available')}")
            return

        # Get Registry Manager from session state
        st.session_state.get("registry_manager")

        # Create subtabs using centralized TAB_ICONS for consistency
        subtabs = st.tabs(
            [
                f"{UISymbols.get_tab_icon('admin_dashboard')} {i18n.t('admin.settings.subtabs.dashboard')}",
                f"{UISymbols.get_tab_icon('mqtt_clients')} {i18n.t('admin.settings.subtabs.mqtt_clients')}",
                f"{UISymbols.get_tab_icon('gateway')} {i18n.t('admin.settings.subtabs.gateway')}",
                f"{UISymbols.get_tab_icon('business_functions')} {i18n.t('admin.settings.subtabs.business_functions')}",
                f"{UISymbols.get_tab_icon('topics')} {i18n.t('admin.settings.subtabs.topics')}",
                f"{UISymbols.get_tab_icon('schemas')} {i18n.t('admin.settings.subtabs.schemas')}",
                f"{UISymbols.get_tab_icon('admin_modules')} {i18n.t('admin.settings.subtabs.modules')}",
                f"{UISymbols.get_tab_icon('stations')} {i18n.t('admin.settings.subtabs.stations')}",
                f"{UISymbols.get_tab_icon('txt_controllers')} {i18n.t('admin.settings.subtabs.txt_controllers')}",
                f"{UISymbols.get_tab_icon('workpieces')} {i18n.t('admin.settings.subtabs.workpieces')}",
            ]
        )

        # Render subtab content
        with subtabs[0]:  # Dashboard
            from omf2.ui.admin.admin_settings.dashboard_subtab import render_dashboard_subtab

            render_dashboard_subtab()

        with subtabs[1]:  # MQTT Clients
            from omf2.ui.admin.admin_settings.mqtt_clients_subtab import render_mqtt_clients_subtab

            render_mqtt_clients_subtab()

        with subtabs[2]:  # Gateway
            from omf2.ui.admin.admin_settings.gateway_subtab import render_gateway_subtab

            render_gateway_subtab()

        with subtabs[3]:  # Business Functions
            from omf2.ui.admin.admin_settings.business_functions_subtab import render_business_functions_subtab

            render_business_functions_subtab()

        with subtabs[4]:  # Topics
            from omf2.ui.admin.admin_settings.topics_subtab import render_topics_subtab

            render_topics_subtab()

        with subtabs[5]:  # Schemas
            from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab

            render_schemas_subtab()

        with subtabs[6]:  # Modules
            from omf2.ui.admin.admin_settings.module_subtab import render_module_subtab

            render_module_subtab()

        with subtabs[7]:  # Stations
            from omf2.ui.admin.admin_settings.stations_subtab import render_stations_subtab

            render_stations_subtab()

        with subtabs[8]:  # TXT Controllers
            from omf2.ui.admin.admin_settings.txt_controllers_subtab import render_txt_controllers_subtab

            render_txt_controllers_subtab()

        with subtabs[9]:  # Workpieces
            from omf2.ui.admin.admin_settings.workpiece_subtab import render_workpiece_subtab

            render_workpiece_subtab()

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Admin Settings Tab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Admin Settings Tab failed: {e}")
        st.info("💡 This component is currently under development.")
