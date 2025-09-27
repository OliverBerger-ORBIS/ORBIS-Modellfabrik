#!/usr/bin/env python3
"""
Message Center Gateway - Business logic layer for Message Center MQTT operations
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum

from .message_center_mqtt_client import MessageCenterMqttClient

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageCenterGateway:
    """
    Message Center Gateway - Encapsulates all Message Center MQTT operations
    
    This gateway provides business logic methods for centralized message handling,
    using the Message Center MQTT client as the underlying transport.
    """
    
    def __init__(self, mqtt_client: MessageCenterMqttClient):
        self.client = mqtt_client
        self.logger = logger
        
        # Message Center specific topic patterns
        self.topics = {
            "broadcast": "messages/broadcast",
            "alerts": "messages/alerts",
            "notifications": "messages/notifications",
            "logs": "messages/logs",
            "status": "messages/status"
        }
        
        # Subscribe to Message Center topics on initialization
        self._subscribe_to_message_center_topics()
        
        logger.info("💬 Message Center Gateway initialized")
    
    def _subscribe_to_message_center_topics(self):
        """Subscribe to all Message Center-related topics"""
        message_topics = [
            "messages/+",  # All message topics
            "messages/broadcast",
            "messages/alerts/+",
            "messages/notifications/+", 
            "messages/logs/+",
            "messages/status"
        ]
        self.client.subscribe_many(message_topics)
    
    def _utc_timestamp(self) -> str:
        """Generate UTC timestamp"""
        return datetime.now(timezone.utc).isoformat()
    
    def send_broadcast_message(self, message: str, sender: str, priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """
        Send broadcast message to all subscribers
        
        Args:
            message: Message content
            sender: Message sender identifier
            priority: Message priority level
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "message": message,
            "sender": sender,
            "priority": priority.value,
            "type": "broadcast"
        }
        
        return self.client.publish_json(self.topics["broadcast"], payload)
    
    def send_alert(self, alert_type: str, message: str, source: str, 
                   priority: MessagePriority = MessagePriority.HIGH, 
                   data: Optional[Dict] = None) -> bool:
        """
        Send system alert
        
        Args:
            alert_type: Type of alert (e.g., "error", "warning", "system")
            message: Alert message
            source: Alert source component
            priority: Alert priority level
            data: Additional alert data
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "alert_type": alert_type,
            "message": message,
            "source": source,
            "priority": priority.value,
            "data": data or {}
        }
        
        topic = f"{self.topics['alerts']}/{alert_type}"
        return self.client.publish_json(topic, payload)
    
    def send_notification(self, recipient: str, message: str, title: str, 
                         notification_type: str = "info", data: Optional[Dict] = None) -> bool:
        """
        Send notification to specific recipient
        
        Args:
            recipient: Notification recipient
            message: Notification message
            title: Notification title
            notification_type: Type of notification
            data: Additional notification data
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "recipient": recipient,
            "message": message,
            "title": title,
            "type": notification_type,
            "data": data or {}
        }
        
        topic = f"{self.topics['notifications']}/{recipient}"
        return self.client.publish_json(topic, payload)
    
    def send_log_message(self, level: str, message: str, component: str, 
                        context: Optional[Dict] = None) -> bool:
        """
        Send log message
        
        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            component: Component that generated the log
            context: Additional log context
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "level": level,
            "message": message,
            "component": component,
            "context": context or {}
        }
        
        topic = f"{self.topics['logs']}/{level}"
        return self.client.publish_json(topic, payload)
    
    def send_status_update(self, status: str, details: Optional[Dict] = None) -> bool:
        """
        Send Message Center status update
        
        Args:
            status: Current status
            details: Additional status details
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "status": status,
            "details": details or {}
        }
        
        return self.client.publish_json(self.topics["status"], payload)
    
    def get_recent_broadcasts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent broadcast messages"""
        buffer = self.client.get_buffer(self.topics["broadcast"])
        return list(buffer)[-limit:]
    
    def get_alerts_by_type(self, alert_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get alerts by type"""
        topic = f"{self.topics['alerts']}/{alert_type}"
        buffer = self.client.get_buffer(topic)
        return list(buffer)[-limit:]
    
    def get_notifications_for_recipient(self, recipient: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notifications for specific recipient"""
        topic = f"{self.topics['notifications']}/{recipient}"
        buffer = self.client.get_buffer(topic)
        return list(buffer)[-limit:]
    
    def get_logs_by_level(self, level: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs by level"""
        topic = f"{self.topics['logs']}/{level}"
        buffer = self.client.get_buffer(topic)
        return list(buffer)[-limit:]
    
    def is_connected(self) -> bool:
        """Check if Message Center MQTT client is connected"""
        return self.client.connected
    
    def add_broadcast_callback(self, callback):
        """Add callback for broadcast messages"""
        self.client.add_callback(self.topics["broadcast"], callback)
    
    def add_alert_callback(self, alert_type: str, callback):
        """Add callback for specific alert type"""
        pattern = f"{self.topics['alerts']}/{alert_type}"
        self.client.add_callback(pattern, callback)
    
    def add_notification_callback(self, recipient: str, callback):
        """Add callback for notifications to specific recipient"""
        pattern = f"{self.topics['notifications']}/{recipient}"
        self.client.add_callback(pattern, callback)