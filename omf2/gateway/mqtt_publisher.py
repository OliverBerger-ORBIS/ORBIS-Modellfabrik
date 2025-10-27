#!/usr/bin/env python3
"""
MQTTPublisher - MQTT implementation of UIPublisher

Publishes UI refresh notifications to MQTT broker using an existing
paho MQTT client instance. Topics follow the pattern: omf2/ui/refresh/{group}
"""

import json
import time
from typing import Any, Dict, Optional

from omf2.common.logger import get_logger

logger = get_logger(__name__)


class MQTTPublisher:
    """
    MQTT-based UI refresh publisher

    Publishes refresh notifications to MQTT topics to trigger UI updates.
    Uses an existing paho MQTT client instance provided by the gateway factory.

    Topic pattern: omf2/ui/refresh/{group}
    Payload: JSON with 'ts' (timestamp) and optional additional fields
    """

    def __init__(self, mqtt_client):
        """
        Initialize MQTTPublisher with an existing MQTT client

        Args:
            mqtt_client: Paho MQTT client instance with publish() method
                        Expected signature: publish(topic, message, qos, retain) -> bool
        """
        self.mqtt_client = mqtt_client
        self.topic_prefix = "omf2/ui/refresh"
        logger.debug(f"🔧 MQTTPublisher initialized with topic prefix: {self.topic_prefix}")

    def publish_refresh(self, group: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a UI refresh notification for a specific group

        Args:
            group: Refresh group identifier (e.g., 'order_updates', 'sensor_data')
            payload: Optional payload dict. If not provided or missing 'ts',
                    a timestamp will be added automatically.

        Returns:
            True if publish succeeded, False otherwise
        """
        if not self.mqtt_client:
            logger.debug(f"⚠️ No MQTT client available, skipping refresh publish for group '{group}'")
            return False

        try:
            # Construct topic
            topic = f"{self.topic_prefix}/{group}"

            # Prepare payload with timestamp
            if payload is None:
                payload = {}
            else:
                payload = payload.copy()  # Don't modify caller's dict

            # Ensure timestamp is present
            if "ts" not in payload:
                payload["ts"] = time.time()

            # Check if mqtt_client has a publish method that accepts Dict (like CcuMqttClient)
            # or raw string payload (like standard paho client)
            if hasattr(self.mqtt_client, "publish"):
                # Try to publish - handle both CcuMqttClient style and raw paho style
                try:
                    # First try CcuMqttClient style (accepts Dict)
                    result = self.mqtt_client.publish(topic, payload, qos=0, retain=False)
                    success = bool(result)
                except TypeError:
                    # Fallback to raw paho style (accepts string payload)
                    payload_str = json.dumps(payload)
                    result = self.mqtt_client.publish(topic, payload_str, qos=0, retain=False)
                    # For paho client, result is MQTTMessageInfo with rc attribute
                    success = hasattr(result, "rc") and result.rc == 0

                if success:
                    logger.debug(f"✅ Published refresh to {topic}: {payload}")
                    return True
                else:
                    logger.warning(f"⚠️ Failed to publish refresh to {topic}")
                    return False

            else:
                logger.warning(f"⚠️ MQTT client does not have publish method")
                return False

        except Exception as e:
            logger.error(f"❌ Error publishing refresh for group '{group}': {e}")
            return False


class NoOpPublisher:
    """
    No-op publisher implementation for when MQTT is not available

    Always returns False but doesn't raise exceptions, allowing graceful degradation.
    """

    def publish_refresh(self, group: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        """No-op publish - always returns False"""
        logger.debug(f"🔇 NoOpPublisher: skipping refresh for group '{group}' (MQTT not configured)")
        return False
