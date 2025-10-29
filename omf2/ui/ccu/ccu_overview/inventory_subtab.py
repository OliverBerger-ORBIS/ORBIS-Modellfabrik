#!/usr/bin/env python3
"""
CCU Overview - Inventory Subtab
Kombiniert Customer Orders, Purchase Orders und Inventory Grid
Verwendet session_state Pattern für konsistentes Refresh-Verhalten
"""

import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.stock_manager import get_stock_manager
from omf2.common.i18n import I18nManager
from omf2.common.logger import get_logger
from omf2.ui.common.product_rendering import render_product_svg_container
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
    """
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return False

    try:
        stock_manager = get_stock_manager()
        success = stock_manager.send_customer_order(workpiece_type, ccu_gateway)

        if success:
            message = i18n.t("ccu_overview.customer_orders.order_sent", workpiece_type=workpiece_type)
            st.success(f"{UISymbols.get_status_icon('success')} {message}")
        else:
            message = i18n.t("ccu_overview.customer_orders.order_error", workpiece_type=workpiece_type)
            st.error(f"{UISymbols.get_status_icon('error')} {message}")

        return success

    except Exception as e:
        logger.error(f"❌ Error sending customer order for {workpiece_type}: {e}")
        error_prefix = i18n.t("common.status.error")
        st.error(f"{UISymbols.get_status_icon('error')} {error_prefix}: {e}")
        return False


def _send_raw_material_order(workpiece_type: str, ccu_gateway: CcuGateway, i18n: I18nManager) -> bool:
    """
    Sendet Rohmaterial-Bestellung über Stock Manager

    Args:
        workpiece_type: RED, BLUE, oder WHITE
        ccu_gateway: CCU Gateway für MQTT-Versand
        i18n: I18n Manager für Übersetzungen

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
        logger.error(f"❌ Fehler beim Senden der Rohmaterial-Bestellung: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Fehler beim Senden der Rohmaterial-Bestellung: {e}")
        return False


def reload_inventory():
    """
    Reload inventory data into session state

    This wrapper function loads stock data from StockManager and stores it
    in session state for use by the UI rendering logic.
    """
    try:
        logger.info("🔄 reload_inventory() called - loading fresh stock data")
        stock_manager = get_stock_manager()
        inventory_status = stock_manager.get_inventory_status()

        # DEBUG: Log what Stock Manager returned
        if inventory_status:
            inventory = inventory_status.get("inventory", {})
            inventory_count = len([v for v in inventory.values() if v is not None])
            available = inventory_status.get("available", {})
            inventory_items = {k: v for k, v in inventory.items() if v is not None}
            logger.info(
                f"📦 reload_inventory: Stock Manager returned: {inventory_count} items, "
                f"available={available}, inventory={inventory_items}"
            )
        else:
            logger.warning("⚠️ reload_inventory: Stock Manager returned None for inventory_status")

        # Store in session state
        st.session_state["inventory_status"] = inventory_status
        logger.info("📦 reload_inventory: Stored inventory_status in session_state")

        if inventory_status and inventory_status.get("inventory"):
            inventory_count = len([v for v in inventory_status["inventory"].values() if v is not None])
            logger.info(f"✅ reload_inventory: Loaded inventory with {inventory_count} items into session_state")
        else:
            logger.info("ℹ️ reload_inventory: No inventory data available yet")

    except Exception as e:
        logger.error(f"❌ Error in reload_inventory(): {e}", exc_info=True)
        # Set empty on error to prevent UI crashes
        st.session_state["inventory_status"] = None


def render_inventory_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """Render Inventory Subtab - Business Logic über OrderManager

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
        asset_manager: AssetManager Instanz (Singleton)
    """
    logger.info("🏬 Rendering Inventory Subtab")

    # Add auto-refresh support using the same pattern as storage_orders_subtab
    refresh_triggered = False
    try:
        from omf2.ui.ccu.production_orders_refresh_helper import check_and_reload

        # Use stock_updates refresh group with polling + compare (same pattern as storage_orders_subtab)
        refresh_triggered = check_and_reload(group="stock_updates", reload_callback=reload_inventory, interval_ms=1000)

        # Log whether backend API was responsive
        if refresh_triggered:
            logger.info("✅ Backend API available: Refresh triggered via Redis timestamp polling")
        else:
            # Check if API is reachable by testing if we got a timestamp

            session_key = "stock_updates_last_refresh_timestamp"
            if session_key in st.session_state:
                logger.info("✅ Backend API available: No new refresh timestamp detected")
            else:
                logger.info("⚠️ Backend API unavailable: Will use manual refresh fallback")

        # Get data from session state (populated by reload_inventory callback)
        # If not yet populated, load it now (same pattern as storage_orders_subtab)
        if "inventory_status" not in st.session_state:
            logger.info("🔄 inventory_status not in session state, calling reload_inventory()")
            reload_inventory()

    except Exception as e:
        logger.debug(f"⚠️ Auto-refresh not available: {e}")
        # Fallback: load data directly without auto-refresh (same pattern as storage_orders_subtab)
        if "inventory_status" not in st.session_state:
            reload_inventory()

    # BACKEND API UNAVAILABLE FALLBACK:
    # If the backend Flask API (port 5001) is not running, we cannot use Redis-based refresh polling.
    # In this case, always reload inventory data on every page rerun to ensure MQTT updates are visible.
    # This happens when:
    # - Backend API not running (typical in DEV mode)
    # - Backend API unreachable (network issues, wrong URL)
    # - Redis running but Flask API not started
    # User must manually trigger refresh via "Refresh Dashboard" button or other UI interactions.
    if not refresh_triggered:
        logger.info("🔄 Backend API unavailable: Reloading inventory on manual refresh")
        reload_inventory()

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    st.subheader(f"{UISymbols.get_functional_icon('inventory')} {i18n.t('ccu_overview.inventory.title')}")

    # Gateway verfügbar?
    if not ccu_gateway:
        st.error(f"{UISymbols.get_status_icon('error')} CCU Gateway nicht verfügbar")
        return

    try:
        # Get data from session state (populated by reload_inventory callback)
        inventory_status = st.session_state.get("inventory_status")

        # DEBUG: Log what we have in session state
        logger.info(f"📦 render_inventory_subtab: inventory_status in session_state = {inventory_status is not None}")
        if inventory_status:
            inventory = inventory_status.get("inventory", {})
            inventory_items = {k: v for k, v in inventory.items() if v is not None}
            logger.info(
                f"📦 render_inventory_subtab: inventory items={inventory_items}, "
                f"available={inventory_status.get('available', {})}"
            )
        else:
            logger.warning("⚠️ render_inventory_subtab: No inventory_status in session_state")

        if inventory_status and inventory_status.get("inventory"):
            # Echte MQTT-Daten vorhanden
            inventory_data = inventory_status["inventory"]
            available = inventory_status.get("available", {"BLUE": 0, "WHITE": 0, "RED": 0})
            inventory_count = len([v for v in inventory_data.values() if v is not None])
            logger.info(f"✅ render_inventory_subtab: Displaying inventory: {inventory_count} items")
        else:
            # Fallback: Leeres Grid
            inventory_data = {
                "A1": None,
                "A2": None,
                "A3": None,
                "B1": None,
                "B2": None,
                "B3": None,
                "C1": None,
                "C2": None,
                "C3": None,
            }
            available = {"BLUE": 0, "WHITE": 0, "RED": 0}
            waiting_text = i18n.t("ccu_overview.inventory.waiting_for_stock")
            st.info(f"{UISymbols.get_status_icon('info')} {waiting_text}")

        # SECTION 1: Customer Orders
        st.markdown("---")
        st.markdown(
            f"## {UISymbols.get_functional_icon('customer_order')} {i18n.t('ccu_overview.customer_orders.title')}"
        )
        _render_customer_orders_section(available, ccu_gateway, i18n, asset_manager)

        # SECTION 2: Purchase Orders
        st.markdown("---")
        st.markdown(
            f"## {UISymbols.get_functional_icon('purchase_order')} {i18n.t('ccu_overview.purchase_orders.title')}"
        )
        _render_purchase_orders_section(available, ccu_gateway, i18n, asset_manager)

        # SECTION 3: Inventory Grid

        st.markdown("---")
        with st.expander("### 🏭 Lager - Konstante Größe (160x160)", expanded=True):
            _render_inventory_with_fixed_size(inventory_data, asset_manager)

        # Verfügbare Werkstücke anzeigen
        st.markdown("---")
        available_workpieces_text = i18n.t("ccu_overview.inventory.available_workpieces")
        st.markdown(f"**{UISymbols.get_functional_icon('dashboard')} {available_workpieces_text}:**")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{UISymbols.get_functional_icon('workpiece_blue')} BLUE", available.get("BLUE", 0))
        with col2:
            st.metric(f"{UISymbols.get_functional_icon('workpiece_white')} WHITE", available.get("WHITE", 0))
        with col3:
            st.metric(f"{UISymbols.get_functional_icon('workpiece_red')} RED", available.get("RED", 0))

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Error rendering inventory: {e}")
        error_text = i18n.t("ccu_overview.inventory.error_loading").format(error=e)
        st.error(f"{UISymbols.get_status_icon('error')} {error_text}")


def _render_customer_orders_section(available, ccu_gateway: CcuGateway, i18n, asset_manager):
    """Rendert Customer Orders Section"""
    red_count = available.get("RED", 0)
    blue_count = available.get("BLUE", 0)
    white_count = available.get("WHITE", 0)

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
            available_flag = count > 0
            color_name = product.get("name", product_id.capitalize())
            color_emoji = product.get("icon", "🔵" if product_id == "blue" else "⚪" if product_id == "white" else "🔴")

            with columns[i]:
                st.markdown(f"#### {color_emoji} **{color_name.upper()} Customer Order**")

                # PRODUCT SVG - STANDARDIZED 200x200 CONTAINER
                svg_content = asset_manager.get_workpiece_svg(product_id.upper(), "product")
                if svg_content:
                    st.markdown(
                        render_product_svg_container(svg_content, scale=1.0),
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(f"❌ {product_id.lower()}_product.svg nicht gefunden!")

                # Customer Order Daten
                st.write(f"**{i18n.t('ccu_overview.customer_orders.stock')}: {count}**")
                available_text = i18n.t("common.forms.yes") if available_flag else i18n.t("common.forms.no")
                st.write(f"**{i18n.t('ccu_overview.customer_orders.available_label')}: {available_text}**")

                # Button für Bestellung
                button_label = f"{UISymbols.get_status_icon('send')} {i18n.t('common.buttons.order')}"
                button_help = i18n.t("ccu_overview.customer_orders.order_button")

                if available_flag:
                    if st.button(
                        button_label, key=f"ccu_customer_order_{product_id}", type="secondary", help=button_help
                    ):
                        _send_customer_order(product_id.upper(), ccu_gateway)
                else:
                    st.button(button_label, key=f"ccu_customer_order_{product_id}_disabled", disabled=True)


def _render_purchase_orders_section(available, ccu_gateway: CcuGateway, i18n, asset_manager):
    """Rendert Purchase Orders Section"""
    # Konstanten aus CCU Config laden
    from omf2.ccu.config_loader import get_ccu_config_loader

    config_loader = get_ccu_config_loader()
    inventory_settings = config_loader.load_production_settings().get("inventorySettings", {})
    MAX_CAPACITY = inventory_settings.get("maxCapacity", 3)

    # Verfügbare Werkstücke
    red_count = available.get("RED", 0)
    blue_count = available.get("BLUE", 0)
    white_count = available.get("WHITE", 0)

    # Berechne Bedarf für jede Farbe
    red_need = MAX_CAPACITY - red_count
    blue_need = MAX_CAPACITY - blue_count
    white_need = MAX_CAPACITY - white_count

    # Werkstück-Sektionen rendern (BLUE, WHITE, RED)
    _render_workpiece_section("BLUE", blue_count, blue_need, MAX_CAPACITY, ccu_gateway, i18n, asset_manager)
    _render_workpiece_section("WHITE", white_count, white_need, MAX_CAPACITY, ccu_gateway, i18n, asset_manager)
    _render_workpiece_section("RED", red_count, red_need, MAX_CAPACITY, ccu_gateway, i18n, asset_manager)


def _render_workpiece_section(
    workpiece_type: str,
    count: int,
    need: int,
    max_capacity: int,
    ccu_gateway: CcuGateway,
    i18n: I18nManager,
    asset_manager,
):
    """Rendert eine Werkstück-Sektion (BLUE, WHITE, RED) für Purchase Orders"""
    icons = {"BLUE": "🔵", "WHITE": "⚪", "RED": "🔴"}

    workpieces_text = i18n.t("ccu_overview.purchase_orders.workpieces").format(workpiece_type=workpiece_type)
    st.markdown(f"#### {icons.get(workpiece_type, '📦')} {workpieces_text}")
    col1, col2, col3, col4 = st.columns([1, 1, 3, 1])

    with col1:
        # STANDARDIZED 200x200 CONTAINER
        st.markdown("**UNPROCESSED SVG:**")
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "unprocessed")
        if svg_content:
            st.markdown(
                render_product_svg_container(svg_content, scale=1.0),
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
            # STANDARDIZED 200x200 CONTAINERS FOR PALETT
            st.markdown("**Fehlende Werkstücke:**")
            palett_content = asset_manager.get_workpiece_palett()
            if palett_content:
                # Using standardized 200x200 size for palett SVGs
                palett_html = ""
                for _i in range(need):
                    palett_html += f'<div style="display: inline-block; margin: 2px;">{render_product_svg_container(palett_content, scale=0.5)}</div>'
                st.markdown(palett_html, unsafe_allow_html=True)
            else:
                st.error("❌ palett.svg nicht gefunden!")
        else:
            st.success("✅ Bestand vollständig")

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


def _render_inventory_with_fixed_size(inventory_data, asset_manager):
    """Variante 1: Lager mit konstanter Größe (160x160)"""
    # Row A
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        _render_inventory_position_fixed("A1", inventory_data.get("A1"), asset_manager)
    with col_a2:
        _render_inventory_position_fixed("A2", inventory_data.get("A2"), asset_manager)
    with col_a3:
        _render_inventory_position_fixed("A3", inventory_data.get("A3"), asset_manager)

    # Abstand zwischen den Reihen (eine Fontsize-Höhe)
    st.markdown("<br>", unsafe_allow_html=True)

    # Row B
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        _render_inventory_position_fixed("B1", inventory_data.get("B1"), asset_manager)
    with col_b2:
        _render_inventory_position_fixed("B2", inventory_data.get("B2"), asset_manager)
    with col_b3:
        _render_inventory_position_fixed("B3", inventory_data.get("B3"), asset_manager)

    # Abstand zwischen den Reihen (eine Fontsize-Höhe)
    st.markdown("<br>", unsafe_allow_html=True)

    # Row C
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        _render_inventory_position_fixed("C1", inventory_data.get("C1"), asset_manager)
    with col_c2:
        _render_inventory_position_fixed("C2", inventory_data.get("C2"), asset_manager)
    with col_c3:
        _render_inventory_position_fixed("C3", inventory_data.get("C3"), asset_manager)


def _render_inventory_position_fixed(position: str, workpiece_type: str, asset_manager):
    """Rendert eine Lagerposition mit fester Größe (160x160) - Standardized"""
    if workpiece_type is None:
        # Leere Position → Palett-SVG mit standardisierter Größe (160x160)
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            # Container und Beschriftung gemeinsam zentriert - bleiben zusammen als Block
            palett_div = f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 0 auto; text-align: center; display: flex; align-items: center; justify-content: center; width: 160px; height: 160px;">
                {palett_content}
            </div>
            """
            label_html = f"<div style='text-align: center; margin-top: 5px;'><strong>{position} [EMPTY]</strong></div>"
            st.markdown(
                f"<div style='text-align: center;'>{palett_div}{label_html}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.error("❌ palett.svg nicht gefunden!")
    else:
        # Gefüllte Position → Werkstück-SVG mit standardisierter Größe (160x160)
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            # Container und Beschriftung gemeinsam zentriert - bleiben zusammen als Block
            container_html = render_product_svg_container(svg_content, scale=0.8)
            # Container zentrieren: margin: 0 auto statt margin: 5px
            container_html = container_html.replace("margin: 5px;", "margin: 0 auto;")
            label_html = f"<div style='text-align: center; margin-top: 5px;'><strong>{position} [{workpiece_type}]</strong></div>"
            st.markdown(
                f"<div style='text-align: center;'>{container_html}{label_html}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.error(f"❌ {workpiece_type.lower()}_instock_unprocessed.svg nicht gefunden!")
