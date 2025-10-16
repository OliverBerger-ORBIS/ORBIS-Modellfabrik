#!/usr/bin/env python3
"""
CCU Orders Tab - Order Management UI Component (Wrapper mit Subtabs)
"""

import streamlit as st

from omf2.ccu.order_manager import get_order_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

from .production_orders_subtab import show_production_orders_subtab
from .storage_orders_subtab import show_storage_orders_subtab

logger = get_logger(__name__)


def render_ccu_orders_tab(ccu_gateway=None, registry_manager=None):
    """Render CCU Orders Tab (Wrapper mit Production/Storage Subtabs)

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📝 Rendering CCU Orders Tab")
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

        st.header(f"{UISymbols.get_tab_icon('ccu_orders')} {i18n.translate('tabs.ccu_orders')}")
        st.markdown(i18n.t("ccu_orders.subtitle"))

        # Business Logic über OrderManager
        order_manager = get_order_manager()
        statistics = order_manager.get_order_statistics()

        # Order Statistics Section (oberhalb der Tabs)
        stats_title = i18n.t("ccu_orders.statistics.title")
        with st.expander(f"{UISymbols.get_status_icon('stats')} {stats_title}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(i18n.t("ccu_orders.statistics.total_orders"), statistics.get("total_count", 0))

            with col2:
                st.metric(
                    i18n.t("ccu_orders.statistics.active_orders"),
                    statistics.get("active_count", 0),
                    i18n.t("ccu_orders.statistics.processing"),
                )

            with col3:
                st.metric(i18n.t("ccu_orders.statistics.completed_orders"), statistics.get("completed_count", 0))

            with col4:
                stub_mode = (
                    i18n.t("ccu_orders.statistics.stub_mode")
                    if statistics.get("stub_mode")
                    else i18n.t("ccu_orders.statistics.live_mode")
                )
                st.metric(i18n.t("ccu_orders.statistics.mode"), stub_mode)

        # Tabs für Production vs Storage Orders
        tab1, tab2 = st.tabs(
            [i18n.t("ccu_orders.subtabs.production_orders"), i18n.t("ccu_orders.subtabs.storage_orders")]
        )

        with tab1:
            show_production_orders_subtab(i18n)

        with tab2:
            show_storage_orders_subtab(i18n)

        # Order Actions Section (unterhalb der Tabs)
        actions_title = i18n.t("ccu_orders.actions.title")
        with st.expander(f"🎛️ {actions_title}", expanded=False):
            st.markdown(f"### {i18n.t('ccu_orders.actions.control')}")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"📤 {i18n.t('ccu_orders.actions.create_new')}", key="ccu_orders_create_btn"):
                    _create_new_order(ccu_gateway, i18n)

            with col2:
                if st.button(f"⏸️ {i18n.t('ccu_orders.actions.pause_all')}", key="ccu_orders_pause_btn"):
                    _pause_all_orders(ccu_gateway, i18n)

            with col3:
                if st.button(f"▶️ {i18n.t('ccu_orders.actions.resume_all')}", key="ccu_orders_resume_btn"):
                    _resume_all_orders(ccu_gateway, i18n)

    except Exception as e:
        logger.error(f"❌ CCU Orders Tab rendering error: {e}")
        st.error(f"❌ CCU Orders Tab failed: {e}")
        i18n = st.session_state.get("i18n_manager")
        if i18n:
            st.info(f"💡 {i18n.t('ccu_orders.under_development')}")


def _create_new_order(ccu_gateway, i18n):
    """Create New Order using CCU Gateway"""
    try:
        logger.info("📝 Creating New Order via CCU Gateway")
        # TODO: Implement actual order creation via ccu_gateway
        # order_id = ccu_gateway.create_order(workpiece_data)
        st.success(f"✅ {i18n.t('ccu_orders.status.order_created')}")
    except Exception as e:
        logger.error(f"❌ Order creation error: {e}")
        error_msg = i18n.t("ccu_orders.status.creation_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _pause_all_orders(ccu_gateway, i18n):
    """Pause All Orders using CCU Gateway"""
    try:
        logger.info("⏸️ Pausing All Orders via CCU Gateway")
        # TODO: Implement actual order pause via ccu_gateway
        # ccu_gateway.pause_all_orders()
        st.success(f"⏸️ {i18n.t('ccu_orders.status.orders_paused')}")
    except Exception as e:
        logger.error(f"❌ Order pause error: {e}")
        error_msg = i18n.t("ccu_orders.status.pause_failed").format(error=e)
        st.error(f"❌ {error_msg}")


def _resume_all_orders(ccu_gateway, i18n):
    """Resume All Orders using CCU Gateway"""
    try:
        logger.info("▶️ Resuming All Orders via CCU Gateway")
        # TODO: Implement actual order resume via ccu_gateway
        # ccu_gateway.resume_all_orders()
        st.success(f"▶️ {i18n.t('ccu_orders.status.orders_resumed')}")
    except Exception as e:
        logger.error(f"❌ Order resume error: {e}")
        error_msg = i18n.t("ccu_orders.status.resume_failed").format(error=e)
        st.error(f"❌ {error_msg}")
