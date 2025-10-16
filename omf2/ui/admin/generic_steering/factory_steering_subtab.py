#!/usr/bin/env python3
"""
Factory Steering Subtab - Commands from omf/dashboard/components/admin/steering_factory.py
Gateway-Pattern konform: Nutzt AdminGateway statt direkten MQTT-Client
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_factory_steering_subtab(admin_gateway, registry_manager):
    """Render Factory Steering Subtab with commands from steering_factory.py

    Args:
        admin_gateway: AdminGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz
    """
    logger.info(f"{UISymbols.get_functional_icon('factory_reset')} Rendering Factory Steering Subtab")

    try:
        st.subheader(f"{UISymbols.get_functional_icon('factory_reset')} Factory Steuerung")
        st.markdown("**Traditionelle Steuerungsfunktionen für die Modellfabrik:**")

        # 1) Factory Reset Section
        with st.expander(f"{UISymbols.get_functional_icon('factory_reset')} Factory Reset", expanded=True):
            st.markdown("**Factory Reset und Notfall-Funktionen:**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    f"{UISymbols.get_functional_icon('factory_reset')} Factory Reset", key="factory_reset_btn"
                ):
                    _send_factory_reset(admin_gateway)
            with col2:
                if st.button(
                    f"{UISymbols.get_functional_icon('emergency_stop')} Emergency Stop", key="emergency_stop_btn"
                ):
                    _send_emergency_stop(admin_gateway)

        # 2) FTS Section
        with st.expander(f"{UISymbols.get_functional_icon('transport')} FTS Steuerung", expanded=True):
            st.markdown("**Fahrerloses Transportsystem - Docken und Laden:**")

            # FTS Serial Number Selection
            fts_serial = st.selectbox(
                "FTS Serial Number:", ["5iO4", "SVR3QA0022", "SVR4H76449"], key="fts_serial_select"
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"{UISymbols.get_functional_icon('transport')} Docke an", key="fts_dock_btn"):
                    _send_fts_dock(admin_gateway, fts_serial)
            with col2:
                if st.button(f"{UISymbols.get_status_icon('receive')} Laden", key="fts_load_btn"):
                    _send_fts_load(admin_gateway, fts_serial)
            with col3:
                if st.button(f"{UISymbols.get_status_icon('send')} Laden beenden", key="fts_unload_btn"):
                    _send_fts_unload(admin_gateway, fts_serial)

        # 3) Bestellung Section
        with st.expander("📦 Bestellungen", expanded=True):
            st.markdown("**Produktionsaufträge - Farben:**")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"{UISymbols.get_workpiece_icon('blue')} BLAU", key="order_blue_btn"):
                    _send_order(admin_gateway, "BLUE")
            with col2:
                if st.button(f"{UISymbols.get_workpiece_icon('white')} WEISS", key="order_white_btn"):
                    _send_order(admin_gateway, "WHITE")
            with col3:
                if st.button(f"{UISymbols.get_workpiece_icon('red')} ROT", key="order_red_btn"):
                    _send_order(admin_gateway, "RED")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Factory Steering Subtab error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Factory Steering failed: {e}")


def _send_factory_reset(admin_gateway):
    """Send Factory Reset Command"""
    try:
        from datetime import datetime

        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload("ccu/set/reset") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {"timestamp": datetime.now().isoformat(), "withStorage": False}

        success = admin_gateway.publish_message("ccu/set/reset", payload, qos=1, retain=False)
        if success:
            st.success(f"{UISymbols.get_status_icon('success')} Factory Reset gesendet!")
            logger.info(f"{UISymbols.get_functional_icon('factory_reset')} Factory Reset Command sent")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} Factory Reset fehlgeschlagen!")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Factory Reset error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Factory Reset failed: {e}")


def _send_emergency_stop(admin_gateway):
    """Send Emergency Stop Command"""
    try:
        from datetime import datetime

        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload("ccu/control") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {"timestamp": datetime.now().isoformat(), "emergency": True}

        success = admin_gateway.publish_message("ccu/set/emergency", payload, qos=2, retain=False)
        if success:
            st.error("🛑 Emergency Stop gesendet!")
            logger.warning("🚨 Emergency Stop Command sent")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} Emergency Stop fehlgeschlagen!")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Emergency Stop error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Emergency Stop failed: {e}")


def _send_fts_dock(admin_gateway, fts_serial):
    """Send FTS Dock Command"""
    try:
        from datetime import datetime

        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload(f"fts/v1/ff/{fts_serial}/instantAction") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {
            "timestamp": datetime.now().isoformat(),
            "serialNumber": fts_serial,
            "actions": [
                {
                    "actionType": "findInitialDockPosition",
                    "actionId": f"dock-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "metadata": {"nodeId": "SVR4H73275"},
                }
            ],
        }

        success = admin_gateway.publish_message(f"fts/v1/ff/{fts_serial}/instantAction", payload, qos=1, retain=False)
        if success:
            st.success(f"{UISymbols.get_functional_icon('transport')} FTS {fts_serial} - Docke an gesendet!")
            logger.info(f"{UISymbols.get_functional_icon('transport')} FTS Dock Command sent for {fts_serial}")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} FTS Dock fehlgeschlagen!")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} FTS Dock error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} FTS Dock failed: {e}")


def _send_fts_load(admin_gateway, fts_serial):
    """Send FTS Load Command"""
    try:
        from datetime import datetime

        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload(f"fts/v1/ff/{fts_serial}/instantAction") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {"serialNumber": fts_serial, "charge": True, "timestamp": datetime.now().isoformat()}

        success = admin_gateway.publish_message("ccu/set/charge", payload, qos=1, retain=False)
        if success:
            st.success(f"📦 FTS {fts_serial} - Laden gesendet!")
            logger.info(f"📦 FTS Load Command sent for {fts_serial}")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} FTS Laden fehlgeschlagen!")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} FTS Load error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} FTS Load failed: {e}")


def _send_fts_unload(admin_gateway, fts_serial):
    """Send FTS Unload Command"""
    try:
        from datetime import datetime

        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload("ccu/set/charge") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {"serialNumber": fts_serial, "charge": False, "timestamp": datetime.now().isoformat()}

        success = admin_gateway.publish_message("ccu/set/charge", payload, qos=1, retain=False)
        if success:
            st.success(f"{UISymbols.get_status_icon('send')} FTS {fts_serial} - Laden beenden gesendet!")
            logger.info(f"{UISymbols.get_status_icon('send')} FTS Unload Command sent for {fts_serial}")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} FTS Laden beenden fehlgeschlagen!")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} FTS Unload error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} FTS Unload failed: {e}")


def _send_order(admin_gateway, color):
    """Send Production Order"""
    try:
        from datetime import datetime

        # TODO: Replace hardcoded payload with schema-driven approach
        # TODO: Use PayloadGenerator.generate_example_payload("ccu/orders/send") instead
        # TODO: Integrate with Registry Manager for proper schema validation
        payload = {"type": color, "timestamp": datetime.now().isoformat(), "orderType": "PRODUCTION"}

        success = admin_gateway.publish_message("ccu/order/request", payload, qos=1, retain=False)
        if success:
            st.success(f"📦 {color} Bestellung gesendet!")
            logger.info(f"📦 Order Command sent for {color}")
        else:
            st.error(f"{UISymbols.get_status_icon('error')} {color} Bestellung fehlgeschlagen!")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Order error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Order failed: {e}")
