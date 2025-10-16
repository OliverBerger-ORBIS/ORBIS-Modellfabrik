#!/usr/bin/env python3
"""
Environment Switch Utility for OMF2
Robust environment switching with proper cleanup and reinitialization
"""

import streamlit as st

from omf2.admin.admin_gateway import AdminGateway
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger
from omf2.factory.client_factory import get_client_factory
from omf2.factory.gateway_factory import get_gateway_factory

logger = get_logger(__name__)


def switch_ccu_environment(new_env: str):
    """
    Robust environment switch for CCU (disconnects, resets, and reinitializes client/gateway).
    Args:
        new_env (str): Environment name, e.g. 'mock', 'replay', 'live'
    """
    logger.info(f"🔄 Switching CCU environment to '{new_env}'")

    # 1. Disconnect and remove old MQTT client
    if "ccu_mqtt_client" in st.session_state:
        old_client = st.session_state["ccu_mqtt_client"]
        if hasattr(old_client, "disconnect"):
            old_client.disconnect()
        st.session_state.pop("ccu_mqtt_client")
        logger.info("🔌 Old CCU MQTT client disconnected and removed from session state")

    # 2. Remove old gateway from Session-State and Factory
    if "ccu_gateway" in st.session_state:
        st.session_state.pop("ccu_gateway")
        logger.info("🏗️ Old CCU gateway removed from session state")

    factory = get_gateway_factory()
    factory._gateways.pop("ccu", None)  # Remove old from factory cache
    logger.info("🏭 Old CCU gateway removed from factory cache")

    # 3. Create new MQTT client with the environment-specific client-id
    client_factory = get_client_factory()
    new_client = client_factory.get_mqtt_client("ccu_mqtt_client", environment=new_env)
    st.session_state["ccu_mqtt_client"] = new_client
    logger.info(f"🔌 New CCU MQTT client created for environment '{new_env}'")

    # 4. Create new Gateway and register it
    new_gateway = CcuGateway(mqtt_client=new_client)
    new_client.set_gateway(new_gateway)
    st.session_state["ccu_gateway"] = new_gateway
    factory._gateways["ccu"] = new_gateway
    logger.info("🏗️ New CCU gateway created and registered")

    # 5. Auto-refresh UI to show new connection status
    try:
        from omf2.ui.utils.ui_refresh import request_refresh

        request_refresh()
        logger.info("🔄 UI refreshed automatically after CCU environment switch")
    except Exception as e:
        logger.warning(f"⚠️ Failed to auto-refresh UI after CCU environment switch: {e}")

    # 6. Log confirmation
    logger.info(f"✅ CCU environment successfully switched to '{new_env}'; new client and gateway initialized")


def switch_admin_environment(new_env: str):
    """
    Robust environment switch for Admin (disconnects, resets, and reinitializes client/gateway).
    Args:
        new_env (str): Environment name, e.g. 'mock', 'replay', 'live'
    """
    logger.info(f"🔄 Switching Admin environment to '{new_env}'")

    # 1. Disconnect and remove old MQTT client
    if "admin_mqtt_client" in st.session_state:
        old_client = st.session_state["admin_mqtt_client"]
        if hasattr(old_client, "disconnect"):
            old_client.disconnect()
        st.session_state.pop("admin_mqtt_client")
        logger.info("🔌 Old Admin MQTT client disconnected and removed from session state")

    # 2. Remove old gateway from Session-State and Factory
    if "admin_gateway" in st.session_state:
        st.session_state.pop("admin_gateway")
        logger.info("⚙️ Old Admin gateway removed from session state")

    factory = get_gateway_factory()
    factory._gateways.pop("admin", None)  # Remove old from factory cache
    logger.info("🏭 Old Admin gateway removed from factory cache")

    # 3. Create new MQTT client with the environment-specific client-id
    client_factory = get_client_factory()
    new_client = client_factory.get_mqtt_client("admin_mqtt_client", environment=new_env)
    st.session_state["admin_mqtt_client"] = new_client
    logger.info(f"🔌 New Admin MQTT client created for environment '{new_env}'")

    # 4. Create new Gateway and register it
    new_gateway = AdminGateway(mqtt_client=new_client)
    new_client.register_gateway(new_gateway)
    st.session_state["admin_gateway"] = new_gateway
    factory._gateways["admin"] = new_gateway
    logger.info("⚙️ New Admin gateway created and registered")

    # 5. Auto-refresh UI to show new connection status
    try:
        from omf2.ui.utils.ui_refresh import request_refresh

        request_refresh()
        logger.info("🔄 UI refreshed automatically after Admin environment switch")
    except Exception as e:
        logger.warning(f"⚠️ Failed to auto-refresh UI after Admin environment switch: {e}")

    # 6. Log confirmation
    logger.info(f"✅ Admin environment successfully switched to '{new_env}'; new client and gateway initialized")


def switch_all_environments(new_env: str):
    """
    Switch all domains (CCU, Admin) to new environment.
    Args:
        new_env (str): Environment name, e.g. 'mock', 'replay', 'live'
    """
    logger.info(f"🔄 Switching ALL environments to '{new_env}'")

    # Switch CCU environment
    switch_ccu_environment(new_env)

    # Switch Admin environment
    switch_admin_environment(new_env)

    # Clear any cached resources
    if hasattr(st, "cache_resource"):
        st.cache_resource.clear()
        logger.info("🧹 Cache cleared after environment switch")

    # Auto-refresh UI to show new connection status for all environments
    try:
        from omf2.ui.utils.ui_refresh import request_refresh

        request_refresh()
        logger.info("🔄 UI refreshed automatically after ALL environments switch")
    except Exception as e:
        logger.warning(f"⚠️ Failed to auto-refresh UI after ALL environments switch: {e}")

    logger.info(f"✅ ALL environments successfully switched to '{new_env}'")
