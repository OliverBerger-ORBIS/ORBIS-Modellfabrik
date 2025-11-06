#!/usr/bin/env python3
"""
CCU Overview - Purchase Order Subtab
Exakt wie aps_overview_purchase_order.py mit Stock Manager Integration
Reihenfolge: BLUE, WHITE, RED (wie gewünscht)
"""

import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.stock_manager import get_stock_manager
from omf2.common.i18n import I18nManager
from omf2.common.logger import get_logger
from omf2.ui.common.product_rendering import render_product_svg_as_img
from omf2.ui.common.symbols import UISymbols

# HTML Templates nicht mehr benötigt - Asset-Manager verwendet

logger = get_logger(__name__)


def _render_workpiece_section(
    workpiece_type: str,
    count: int,
    need: int,
    max_capacity: int,
    ccu_gateway: CcuGateway,
    i18n: I18nManager,
    asset_manager,
):
    """Rendert eine Werkstück-Sektion (BLUE, WHITE, RED) - Asset-Manager SVG Integration"""

    # Icons und Labels
    icons = {"BLUE": "🔵", "WHITE": "⚪", "RED": "🔴"}

    workpieces_text = i18n.t("ccu_overview.purchase_orders.workpieces").format(workpiece_type=workpiece_type)
    st.markdown(f"#### {icons.get(workpiece_type, '📦')} {workpieces_text}")
    col1, col2, col3, col4 = st.columns([1, 1, 3, 1])

    with col1:
        # Base64 data URL for universal browser compatibility
        st.markdown(f"**{i18n.t('ccu_overview.labels.unprocessed_svg')}:**")
        svg_data_url = asset_manager.get_workpiece_svg_as_base64_data_url(workpiece_type, "unprocessed")
        if svg_data_url:
            st.markdown(
                render_product_svg_as_img(svg_data_url, scale=1.0),
                unsafe_allow_html=True,
            )
        else:
            st.error(f"❌ {workpiece_type.lower()}_unprocessed.svg nicht gefunden!")

        # Bestand anzeigen
        stock_text = i18n.t("ccu_overview.purchase_orders.stock")
        available_text = i18n.t("ccu_overview.purchase_orders.available")
        yes_text = i18n.t("ccu_overview.purchase_orders.yes")
        no_text = i18n.t("ccu_overview.purchase_orders.no")
        st.markdown(f"**{stock_text}: {count}**")
        st.markdown(f"**{available_text}: {'✅ ' + yes_text if count > 0 else '❌ ' + no_text}**")

    with col2:
        need_text = i18n.t("ccu_overview.purchase_orders.need_of_max").format(need=need, max_capacity=max_capacity)
        st.markdown(f"**{need_text}**")
        if need > 0:
            still_orderable_text = i18n.t("ccu_overview.purchase_orders.still_orderable").format(need=need)
            st.markdown(f"**{still_orderable_text}**")
        else:
            complete_text = i18n.t("ccu_overview.purchase_orders.complete_no_need")
            st.success(f"{UISymbols.get_status_icon('success')} {complete_text}")

    with col3:
        if need > 0:
            # Base64 data URL rendering for universal browser compatibility
            st.markdown("**Fehlende Werkstücke:**")
            palett_data_url = asset_manager.get_workpiece_svg_as_base64_data_url("palett", "palett")
            if palett_data_url:
                # Using Base64 data URLs with scale=0.5 (100px) for palett SVGs
                palett_html = ""
                for _i in range(need):
                    palett_html += render_product_svg_as_img(palett_data_url, scale=0.5, border_style="none", padding="2px", margin="2px")
                st.markdown(palett_html, unsafe_allow_html=True)
            else:
                st.error(f"❌ {i18n.t('ccu_overview.errors.palett_not_found')}")
        else:
            st.success(f"✅ {i18n.t('ccu_overview.status.stock_complete')}")

    with col4:
        order_button_text = i18n.t("ccu_overview.purchase_orders.order_raw_material")
        if need > 0:
            if st.button(
                f"{UISymbols.get_status_icon('send')} {order_button_text}",
                key=f"ccu_purchase_order_{workpiece_type.lower()}",
                type="secondary",
            ):
                _send_raw_material_order(workpiece_type, ccu_gateway, i18n)
        else:
            st.button(
                f"{UISymbols.get_status_icon('send')} {order_button_text}",
                key=f"ccu_purchase_order_{workpiece_type.lower()}_disabled",
                disabled=True,
            )


def _send_raw_material_order(workpiece_type: str, ccu_gateway: CcuGateway, i18n: I18nManager) -> bool:
    """
    Sendet Rohmaterial-Bestellung über Stock Manager

    Args:
        workpiece_type: RED, BLUE, oder WHITE
        ccu_gateway: CCU Gateway für MQTT-Versand

    Returns:
        True wenn erfolgreich, False bei Fehler
    """
    try:
        stock_manager = get_stock_manager()
        success = stock_manager.send_raw_material_order(workpiece_type, ccu_gateway)

        if success:
            st.success(f"{UISymbols.get_status_icon('success')} Rohmaterial-Bestellung für {workpiece_type} gesendet")
        else:
            st.error(
                f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung für {workpiece_type}"
            )

        return success

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung: {e}")
        return False


def render_purchase_order_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """Render Purchase Order Subtab - Business Logic über OrderManager

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
        asset_manager: AssetManager Instanz (Singleton)
    """
    logger.info("📦 Rendering Purchase Order Subtab")

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    st.subheader(f"{UISymbols.get_functional_icon('purchase_order')} {i18n.t('ccu_overview.purchase_orders.title')}")

    # Gateway verfügbar?
    if not ccu_gateway:
        st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway nicht verfügbar")
        return

    try:
        # Business Logic über OrderManager State-Holder (wie Sensor Manager)
        stock_manager = get_stock_manager()
        inventory_status = stock_manager.get_inventory_status()

        if inventory_status and inventory_status.get("inventory"):
            # Echte MQTT-Daten vorhanden
            available_workpieces = inventory_status.get("available", {"RED": 0, "BLUE": 0, "WHITE": 0})
            last_update = inventory_status.get("last_update")

            # Zeitstempel anzeigen
            if last_update:
                stock_updated_text = i18n.t("ccu_overview.purchase_orders.stock_updated").format(
                    last_update=last_update
                )
                st.success(f"{UISymbols.get_status_icon('success')} {stock_updated_text}")
        else:
            # Fallback: Default-Werte
            available_workpieces = {"RED": 0, "BLUE": 0, "WHITE": 0}
            waiting_text = i18n.t("ccu_overview.purchase_orders.waiting_for_stock")
            st.info(f"{UISymbols.get_status_icon('info')} {waiting_text}")

        # Konstanten aus CCU Config laden
        from omf2.ccu.config_loader import get_ccu_config_loader

        config_loader = get_ccu_config_loader()
        inventory_settings = config_loader.load_production_settings().get("inventorySettings", {})
        MAX_CAPACITY = inventory_settings.get("maxCapacity", 3)
        inventory_settings.get("workpieceTypes", ["RED", "BLUE", "WHITE"])

        # Verfügbare Werkstücke
        red_count = available_workpieces.get("RED", 0)
        blue_count = available_workpieces.get("BLUE", 0)
        white_count = available_workpieces.get("WHITE", 0)

        # Berechne Bedarf für jede Farbe
        red_need = MAX_CAPACITY - red_count
        blue_need = MAX_CAPACITY - blue_count
        white_need = MAX_CAPACITY - white_count

        # Werkstück-Sektionen rendern (BLUE, WHITE, RED) - Asset-Manager SVG Integration
        _render_workpiece_section("BLUE", blue_count, blue_need, MAX_CAPACITY, ccu_gateway, i18n, asset_manager)

        _render_workpiece_section("WHITE", white_count, white_need, MAX_CAPACITY, ccu_gateway, i18n, asset_manager)

        _render_workpiece_section("RED", red_count, red_need, MAX_CAPACITY, ccu_gateway, i18n, asset_manager)

        # Zusammenfassung
        st.markdown("---")
        summary_text = i18n.t("ccu_overview.purchase_orders.summary")
        st.markdown(f"### {UISymbols.get_functional_icon('dashboard')} {summary_text}")

        total_need = red_need + blue_need + white_need
        total_available = red_count + blue_count + white_count

        col1, col2, col3 = st.columns(3)
        with col1:
            total_available_text = i18n.t("ccu_overview.purchase_orders.total_available")
            st.metric(f"{UISymbols.get_functional_icon('inventory')} {total_available_text}", total_available)
        with col2:
            total_need_text = i18n.t("ccu_overview.purchase_orders.total_need")
            st.metric(f"{UISymbols.get_status_icon('warning')} {total_need_text}", total_need)
        with col3:
            open_orders_text = i18n.t("ccu_overview.purchase_orders.open_orders")
            st.metric(f"{UISymbols.get_functional_icon('purchase_order')} {open_orders_text}", total_need)

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Error rendering purchase order: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Laden der Rohmaterial-Bestellungen: {e}")
