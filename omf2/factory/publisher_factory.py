#!/usr/bin/env python3
"""
Publisher Factory - Centralized creation of UI Publishers

Provides factory methods to obtain UIPublisher instances, integrating
with existing gateway infrastructure to reuse MQTT clients.
"""

from typing import Optional

from omf2.common.logger import get_logger
from omf2.gateway.mqtt_publisher import MQTTPublisher, NoOpPublisher

logger = get_logger(__name__)


def get_ui_publisher():
    """
    Get a UIPublisher instance

    Attempts to obtain an MQTT client from the gateway factory and wrap it
    in an MQTTPublisher. If the gateway factory or MQTT client is unavailable,
    returns a NoOpPublisher for graceful degradation.

    Returns:
        UIPublisher instance (MQTTPublisher or NoOpPublisher)

    Example:
        >>> publisher = get_ui_publisher()
        >>> publisher.publish_refresh('order_updates', {'source': 'order_manager'})
    """
    try:
        # Try to get MQTT client from gateway factory
        from omf2.factory.gateway_factory import GatewayFactory

        gateway_factory = GatewayFactory()

        # Try to get CCU gateway which has the MQTT client
        try:
            ccu_gateway = gateway_factory.get_ccu_gateway()

            # Try to get the MQTT client from the gateway
            if hasattr(ccu_gateway, "mqtt_client") and ccu_gateway.mqtt_client:
                mqtt_client = ccu_gateway.mqtt_client
                logger.debug("✅ Obtained MQTT client from CCU gateway")
                return MQTTPublisher(mqtt_client)

        except Exception as e:
            logger.debug(f"⚠️ Could not get CCU gateway or MQTT client: {e}")

        # If we reach here, we couldn't get a working MQTT client
        logger.debug("⚠️ No MQTT client available, using NoOpPublisher")
        return NoOpPublisher()

    except Exception as e:
        logger.debug(f"⚠️ Error in get_ui_publisher: {e}, using NoOpPublisher")
        return NoOpPublisher()


def get_ui_publisher_safe() -> Optional[MQTTPublisher]:
    """
    Get a UIPublisher instance, returning None if unavailable

    Similar to get_ui_publisher() but returns None instead of NoOpPublisher
    when MQTT is not available. Useful for optional integrations.

    Returns:
        MQTTPublisher instance if available, None otherwise
    """
    try:
        from omf2.factory.gateway_factory import GatewayFactory

        gateway_factory = GatewayFactory()

        try:
            ccu_gateway = gateway_factory.get_ccu_gateway()

            if hasattr(ccu_gateway, "mqtt_client") and ccu_gateway.mqtt_client:
                mqtt_client = ccu_gateway.mqtt_client
                logger.debug("✅ Obtained MQTT client from CCU gateway (safe mode)")
                return MQTTPublisher(mqtt_client)

        except Exception as e:
            logger.debug(f"⚠️ Could not get CCU gateway or MQTT client (safe mode): {e}")

    except Exception as e:
        logger.debug(f"⚠️ Error in get_ui_publisher_safe: {e}")

    return None
