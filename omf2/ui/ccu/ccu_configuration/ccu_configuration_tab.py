#!/usr/bin/env python3
"""
CCU Configuration Tab - CCU Configuration UI Component
"""

import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_configuration_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Configuration Tab with Subtabs

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("⚙️ Rendering CCU Configuration Tab")
    try:
        # Initialize CCU Gateway if not provided
        if not ccu_gateway:
            if "ccu_gateway" not in st.session_state:
                # Use Gateway Factory to create CCU Gateway with MQTT Client
                from omf2.factory.gateway_factory import get_gateway_factory

                gateway_factory = get_gateway_factory()
                st.session_state["ccu_gateway"] = gateway_factory.get_ccu_gateway()
            ccu_gateway = st.session_state["ccu_gateway"]

        # Initialize Registry Manager if not provided
        if not registry_manager:
            from omf2.registry.manager.registry_manager import get_registry_manager

            registry_manager = get_registry_manager()

        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # Heading SVG (32px) with fallback to emoji icon
        try:
            cfg_icon = get_svg_inline("CONFIGURATION", size_px=32) or ""
            st.markdown(
                f"<h2 style='margin: 0.25rem 0 0.5rem 0; display:flex; align-items:center; gap:8px;'>{cfg_icon} {i18n.translate('tabs.ccu_configuration')}</h2>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.header(f"{UISymbols.get_tab_icon('ccu_configuration')} {i18n.translate('tabs.ccu_configuration')}")
        st.markdown(i18n.t("ccu_configuration.subtitle"))

        # Create subtabs (mit zentralen Tab-Icons)
        # Defensive: resolve labels with fallbacks if i18n returns unresolved keys
        _factory_label = i18n.t("ccu_configuration.subtabs.factory_configuration")
        if _factory_label == "ccu_configuration.subtabs.factory_configuration":
            _factory_label = "Factory Configuration"
        _parameter_label = i18n.t("ccu_configuration.subtabs.parameter_configuration")
        if _parameter_label == "ccu_configuration.subtabs.parameter_configuration":
            _parameter_label = "Parameter Configuration"

        subtabs = st.tabs(
            [
                f"{UISymbols.get_tab_icon('factory')} {_factory_label}",
                f"{UISymbols.get_tab_icon('parameter')} {_parameter_label}",
            ]
        )

        # Render subtab content
        with subtabs[0]:
            from omf2.ui.ccu.ccu_configuration.ccu_factory_configuration_subtab import (
                render_ccu_factory_configuration_subtab,
            )

            render_ccu_factory_configuration_subtab()

        with subtabs[1]:
            from omf2.ui.ccu.ccu_configuration.ccu_parameter_configuration_subtab import (
                render_ccu_parameter_configuration_subtab,
            )

            render_ccu_parameter_configuration_subtab()

        # Business Functions moved to Admin Settings tab (not rendered here)

    except Exception as e:
        logger.error(f"❌ CCU Configuration Tab rendering error: {e}")
        i18n = st.session_state.get("i18n_manager")
        if i18n:
            error_msg = i18n.t("ccu_configuration.error.tab_failed").format(error=e)
            st.error(f"❌ {error_msg}")
            st.info(f"💡 {i18n.t('ccu_configuration.under_development')}")
        else:
            st.error(f"❌ CCU Configuration Tab failed: {e}")
            st.info("💡 This component is currently under development.")


def _refresh_configuration(ccu_gateway, i18n):
    """Refresh Configuration using CCU Gateway"""
    try:
        logger.info("🔄 Refreshing Configuration via CCU Gateway")
        # TODO: Implement actual configuration refresh via ccu_gateway
        # config = ccu_gateway.get_configuration()
        st.success(f"✅ {i18n.t('ccu_configuration.status.refresh_success')}")
    except Exception as e:
        logger.error(f"❌ Configuration refresh error: {e}")
        error_msg = i18n.t("ccu_configuration.error.refresh_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _save_configuration(ccu_gateway, i18n):
    """Save Configuration using CCU Gateway"""
    try:
        logger.info("💾 Saving Configuration via CCU Gateway")
        # TODO: Implement actual configuration save via ccu_gateway
        # ccu_gateway.save_configuration(config_data)
        st.success(f"✅ {i18n.t('ccu_configuration.status.save_success')}")
    except Exception as e:
        logger.error(f"❌ Configuration save error: {e}")
        error_msg = i18n.t("ccu_configuration.error.save_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _reset_configuration(ccu_gateway, i18n):
    """Reset Configuration using CCU Gateway"""
    try:
        logger.info("🔄 Resetting Configuration via CCU Gateway")
        # TODO: Implement actual configuration reset via ccu_gateway
        # ccu_gateway.reset_configuration()
        st.warning(f"🔄 {i18n.t('ccu_configuration.status.reset_warning')}")
    except Exception as e:
        logger.error(f"❌ Configuration reset error: {e}")
        error_msg = i18n.t("ccu_configuration.error.reset_failed").format(error=e)
        st.error(f"❌ {error_msg}")
