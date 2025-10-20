#!/usr/bin/env python3
"""
CCU Overview - Inventory Subtab
Exakt wie aps_overview_inventory.py mit Stock Manager Integration
"""

import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.stock_manager import get_stock_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

# HTML Templates entfernt - Asset-Manager SVGs verwenden

logger = get_logger(__name__)


# VERALTETE HTML-TEMPLATE-FUNKTION ENTFERNT
# Asset-Manager SVGs werden direkt in den neuen Funktionen verwendet


def render_inventory_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """Render Inventory Subtab - Business Logic über OrderManager

    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
        asset_manager: AssetManager Instanz (Singleton)
    """
    logger.info("🏬 Rendering Inventory Subtab")

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    hbw_overview_text = i18n.t("ccu_overview.inventory.hbw_overview")
    st.subheader(
        f"{UISymbols.get_functional_icon('inventory')} {i18n.t('ccu_overview.inventory.title')} - {hbw_overview_text}"
    )

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
            inventory_data = inventory_status["inventory"]
            available = inventory_status.get("available", {"BLUE": 0, "WHITE": 0, "RED": 0})
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

        # VARIANTE 1: Ohne Manipulation (AS-IS) - ZUERST
        st.markdown("### 🏭 Lager - Ohne Manipulation (AS-IS)")
        _render_inventory_without_manipulation(inventory_data, asset_manager)

        st.markdown("---")

        # VARIANTE 2: Konstante Größe (160x160) - EINGEKLAPPT
        with st.expander("### 🏭 Lager - Konstante Größe (160x160)", expanded=False):
            _render_inventory_with_fixed_size(inventory_data, asset_manager)

        # Verfügbare Werkstücke anzeigen (Summary)
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

    # Row B
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        _render_inventory_position_fixed("B1", inventory_data.get("B1"), asset_manager)
    with col_b2:
        _render_inventory_position_fixed("B2", inventory_data.get("B2"), asset_manager)
    with col_b3:
        _render_inventory_position_fixed("B3", inventory_data.get("B3"), asset_manager)

    # Row C
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        _render_inventory_position_fixed("C1", inventory_data.get("C1"), asset_manager)
    with col_c2:
        _render_inventory_position_fixed("C2", inventory_data.get("C2"), asset_manager)
    with col_c3:
        _render_inventory_position_fixed("C3", inventory_data.get("C3"), asset_manager)


def _render_inventory_without_manipulation(inventory_data, asset_manager):
    """Variante 2: Lager ohne Manipulation (AS-IS Modus)"""
    # Row A
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        _render_inventory_position_as_is("A1", inventory_data.get("A1"), asset_manager)
    with col_a2:
        _render_inventory_position_as_is("A2", inventory_data.get("A2"), asset_manager)
    with col_a3:
        _render_inventory_position_as_is("A3", inventory_data.get("A3"), asset_manager)

    # Row B
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        _render_inventory_position_as_is("B1", inventory_data.get("B1"), asset_manager)
    with col_b2:
        _render_inventory_position_as_is("B2", inventory_data.get("B2"), asset_manager)
    with col_b3:
        _render_inventory_position_as_is("B3", inventory_data.get("B3"), asset_manager)

    # Row C
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        _render_inventory_position_as_is("C1", inventory_data.get("C1"), asset_manager)
    with col_c2:
        _render_inventory_position_as_is("C2", inventory_data.get("C2"), asset_manager)
    with col_c3:
        _render_inventory_position_as_is("C3", inventory_data.get("C3"), asset_manager)


def _render_inventory_position_fixed(position: str, workpiece_type: str, asset_manager):
    """Rendert eine Lagerposition mit fester Größe (160x160)"""
    if workpiece_type is None:
        # Leere Position → Palett-SVG mit fester Größe
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                <div style="width: 160px; height: 160px; overflow: hidden;">
                    {palett_content}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            # Position und Inhalt unterhalb zentriert
            st.markdown(
                f"<div style='text-align: center;'><strong>{position} [EMPTY]</strong></div>", unsafe_allow_html=True
            )
        else:
            st.error("❌ palett.svg nicht gefunden!")
    else:
        # Gefüllte Position → Werkstück-SVG mit fester Größe
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                <div style="width: 160px; height: 160px; overflow: hidden;">
                    {svg_content}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            # Position und Inhalt unterhalb zentriert
            st.markdown(
                f"<div style='text-align: center;'><strong>{position} [{workpiece_type}]</strong></div>",
                unsafe_allow_html=True,
            )
        else:
            st.error(f"❌ {workpiece_type.lower()}_instock_unprocessed.svg nicht gefunden!")


def _render_inventory_position_as_is(position: str, workpiece_type: str, asset_manager):
    """Rendert eine Lagerposition ohne Manipulation (AS-IS Modus)"""
    if workpiece_type is None:
        # Leere Position → Palett-SVG ohne Manipulation
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                {palett_content}
            </div>
            """,
                unsafe_allow_html=True,
            )
            # Position und Inhalt unterhalb zentriert
            st.markdown(
                f"<div style='text-align: center;'><strong>{position} [EMPTY]</strong></div>", unsafe_allow_html=True
            )
        else:
            st.error("❌ palett.svg nicht gefunden!")
    else:
        # Gefüllte Position → Werkstück-SVG ohne Manipulation
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                {svg_content}
            </div>
            """,
                unsafe_allow_html=True,
            )
            # Position und Inhalt unterhalb zentriert
            st.markdown(
                f"<div style='text-align: center;'><strong>{position} [{workpiece_type}]</strong></div>",
                unsafe_allow_html=True,
            )
        else:
            st.error(f"❌ {workpiece_type.lower()}_instock_unprocessed.svg nicht gefunden!")
