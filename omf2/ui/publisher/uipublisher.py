#!/usr/bin/env python3
"""
UIPublisher - Protocol/ABC for UI refresh notifications

Defines the interface for publishing UI refresh events to trigger
client-side updates via MQTT or other mechanisms.
"""

from typing import Any, Dict, Optional, Protocol


class UIPublisher(Protocol):
    """
    Protocol for UI refresh publishers

    Implementations should publish refresh notifications to a backend
    (MQTT, Redis, etc.) that triggers UI components to reload data.
    """

    def publish_refresh(self, group: str, payload: Optional[Dict[str, Any]] = None) -> bool:
        """
        Publish a UI refresh notification for a specific group

        Args:
            group: Refresh group identifier (e.g., 'order_updates', 'sensor_data')
            payload: Optional payload dict to include with the refresh notification.
                     Should include a 'ts' (timestamp) field if not provided by implementation.

        Returns:
            True if publish succeeded, False otherwise

        Example:
            >>> publisher.publish_refresh('order_updates', {'ts': 1234567890, 'source': 'order_manager'})
        """
        ...
