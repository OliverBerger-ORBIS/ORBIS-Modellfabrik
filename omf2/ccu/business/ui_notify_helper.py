#!/usr/bin/env python3
"""
UI Notify Helper - Business function integration for UI refresh

Provides helper functions for business functions to notify the UI
about data changes via the MQTT-driven refresh pipeline.
"""

from typing import Any, Dict, Optional

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def notify_ui_on_change(
    ui_publisher, group: str, changed: bool = True, details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Notify UI of data changes

    This helper function can be called by business functions after processing
    incoming MQTT messages or data updates to trigger UI refresh.

    Args:
        ui_publisher: UIPublisher instance (from get_ui_publisher())
        group: Refresh group identifier (e.g., 'order_updates', 'sensor_data')
        changed: Whether data actually changed (default: True)
        details: Optional dict with additional context (e.g., {'source': 'order_manager'})

    Returns:
        True if notification was published, False otherwise

    Example:
        >>> from omf2.factory.publisher_factory import get_ui_publisher
        >>> publisher = get_ui_publisher()
        >>> # After processing an order update...
        >>> notify_ui_on_change(publisher, 'order_updates', changed=True, details={'order_id': '123'})
    """
    if not changed:
        logger.debug(f"⏭️ No changes detected for group '{group}', skipping UI notification")
        return False

    if not ui_publisher:
        logger.debug(f"⚠️ No UI publisher available, cannot notify for group '{group}'")
        return False

    try:
        # Prepare payload
        payload = details.copy() if details else {}

        # Add metadata
        if "source" not in payload:
            payload["source"] = "business_function"

        # Publish refresh notification
        success = ui_publisher.publish_refresh(group, payload)

        if success:
            logger.debug(f"✅ UI notification sent for group '{group}'")
        else:
            logger.debug(f"⚠️ UI notification failed for group '{group}'")

        return success

    except Exception as e:
        logger.error(f"❌ Error sending UI notification for group '{group}': {e}")
        return False
