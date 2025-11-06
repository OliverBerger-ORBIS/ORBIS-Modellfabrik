#!/usr/bin/env python3
"""
CCU Overview - Customer Order Subtab
Exakt wie aps_overview_customer_order.py mit Stock Manager Integration
Reihenfolge: BLUE, WHITE, RED (wie gewünscht)

i18n: VOLLSTÄNDIG ÜBERSETZT (Pilot-Komponente)
Icons: UISymbols bleiben universell (NICHT übersetzt)
"""

import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.stock_manager import get_stock_manager
from omf2.common.logger import get_logger
from omf2.ui.common.product_rendering import render_product_svg_as_img
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def _send_customer_order(workpiece_type: str, ccu_gateway: CcuGateway) -> bool:
    """
    Sendet Kundenauftrag-Bestellung über Stock Manager

    Args:
        workpiece_type: RED, BLUE, oder WHITE
        ccu_gateway: CCU Gateway für MQTT-Versand

    Returns:
        True wenn erfolgreich, False bei Fehler

    i18n: Status-Messages übersetzt mit String-Interpolation
    Icons: UISymbols bleiben universell
    """
    # i18n Manager aus Session State holen (zentrale Instanz)
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    try:
        stock_manager = get_stock_manager()
        success = stock_manager.send_customer_order(workpiece_type, ccu_gateway)

        if success:
            # Icon (universell) + Text (übersetzt mit Interpolation)
            message = i18n.t("ccu_overview.customer_orders.order_sent", workpiece_type=workpiece_type)
            st.success(f"{UISymbols.get_status_icon('success')} {message}")
        else:
            # Icon (universell) + Text (übersetzt mit Interpolation)
            message = i18n.t("ccu_overview.customer_orders.order_error", workpiece_type=workpiece_type)
            st.error(f"{UISymbols.get_status_icon('error')} {message}")

        return success

    except Exception as e:
        logger.error(f"❌ Error sending customer order for {workpiece_type}: {e}")
        # Error-Message mit Icon (universell) + Text (übersetzt)
        error_prefix = i18n.t("common.status.error")
        st.error(f"{UISymbols.get_status_icon('error')} {error_prefix}: {e}")
        return False


def render_customer_order_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """
    Render Customer Order Subtab - Business Logic über OrderManager

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
        asset_manager: AssetManager Instanz (Singleton)

    i18n: VOLLSTÄNDIG ÜBERSETZT (Pilot-Komponente)
    Icons: UISymbols bleiben universell
    """
    # i18n Manager aus Session State holen (zentrale Instanz)
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    logger.info("📋 Rendering Customer Order Subtab")

    # Subheader mit Icon (universell) + Text (übersetzt)
    st.subheader(f"{UISymbols.get_functional_icon('customer_order')} {i18n.t('ccu_overview.customer_orders.title')}")

    # Gateway verfügbar?
    if not ccu_gateway:
        error_msg = i18n.t("common.status.error")
        st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway {error_msg}")
        return

    try:
        # Business Logic über OrderManager State-Holder (wie Sensor Manager)
        stock_manager = get_stock_manager()
        inventory_status = stock_manager.get_inventory_status()

        if inventory_status and inventory_status.get("inventory"):
            # Echte MQTT-Daten vorhanden
            available_workpieces = inventory_status.get("available", {"RED": 0, "BLUE": 0, "WHITE": 0})
            last_update = inventory_status.get("last_update")

            # Zeitstempel anzeigen (übersetzt mit String-Interpolation)
            if last_update:
                message = i18n.t("ccu_overview.customer_orders.stock_updated", timestamp=last_update)
                st.success(f"{UISymbols.get_status_icon('success')} {message}")
        else:
            # Fallback: Default-Werte
            available_workpieces = {"RED": 0, "BLUE": 0, "WHITE": 0}
            message = i18n.t("ccu_overview.customer_orders.waiting_for_stock")
            st.info(f"{UISymbols.get_status_icon('info')} {message}")

        # Verfügbare Werkstücke
        red_count = available_workpieces.get("RED", 0)
        blue_count = available_workpieces.get("BLUE", 0)
        white_count = available_workpieces.get("WHITE", 0)

        # Asset Manager wird als Parameter übergeben (Singleton)

        # Lade Product Manager für Produktdaten
        from omf2.common.product_manager import get_omf2_product_manager

        product_manager = get_omf2_product_manager()
        catalog = product_manager.get_all_products()

        # 3-Spalten-Layout für Werkstücke
        col1, col2, col3 = st.columns(3)

        # Schleife über die Produkte in der Registry
        product_order = ["blue", "white", "red"]  # Definierte Reihenfolge
        columns = [col1, col2, col3]
        counts = [blue_count, white_count, red_count]

        for i, product_id in enumerate(product_order):
            if product_id in catalog and i < 3:
                product = catalog[product_id]
                count = counts[i]
                available = count > 0
                color_name = product.get("name", product_id.capitalize())
                color_emoji = product.get(
                    "icon", "🔵" if product_id == "blue" else "⚪" if product_id == "white" else "🔴"
                )

                with columns[i]:
                    # Restore colored product heading
                    st.markdown(f"#### {color_emoji} **{color_name.upper()} Customer Order**")

                    # PRODUCT SVG - Base64 data URL for universal browser compatibility
                    svg_data_url = asset_manager.get_workpiece_svg_as_base64_data_url(product_id.upper(), "product")
                    if svg_data_url:
                        st.markdown(
                            render_product_svg_as_img(svg_data_url, scale=1.0),
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ {product_id.lower()}_product.svg nicht gefunden!")

                    # Customer Order Daten
                    st.write(f"**{i18n.t('ccu_overview.customer_orders.stock')}: {count}**")
                    available_text = i18n.t("common.forms.yes") if available else i18n.t("common.forms.no")
                    st.write(f"**{i18n.t('ccu_overview.customer_orders.available_label')}: {available_text}**")

                    # Button für Bestellung
                    button_label = f"{UISymbols.get_status_icon('send')} {i18n.t('common.buttons.order')}"
                    button_help = i18n.t("ccu_overview.customer_orders.order_button")

                    if available:
                        if st.button(
                            button_label, key=f"ccu_customer_order_{product_id}", type="secondary", help=button_help
                        ):
                            _send_customer_order(product_id.upper(), ccu_gateway)
                    else:
                        st.button(button_label, key=f"ccu_customer_order_{product_id}_disabled", disabled=True)

        # Zusammenfassung (übersetzt)
        st.markdown("---")
        summary_title = i18n.t("ccu_overview.customer_orders.summary")
        st.markdown(f"### {UISymbols.get_functional_icon('dashboard')} {summary_title}")

        total_available = red_count + blue_count + white_count
        total_orders_possible = (red_count > 0) + (blue_count > 0) + (white_count > 0)

        col1, col2, col3 = st.columns(3)
        with col1:
            label = i18n.t("ccu_overview.customer_orders.total_available")
            st.metric(f"{UISymbols.get_functional_icon('inventory')} {label}", total_available)
        with col2:
            label = i18n.t("ccu_overview.customer_orders.orders_possible")
            st.metric(f"{UISymbols.get_functional_icon('customer_order')} {label}", total_orders_possible)
        with col3:
            label = i18n.t("common.status.unavailable")
            st.metric(f"{UISymbols.get_status_icon('info')} {label}", 3 - total_orders_possible)

    except Exception as e:
        logger.error(f"❌ Error rendering customer order: {e}")
        # Error-Message (übersetzt)
        error_prefix = i18n.t("common.status.error")
        st.error(f"{UISymbols.get_status_icon('error')} {error_prefix}: {e}")
