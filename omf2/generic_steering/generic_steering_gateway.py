#!/usr/bin/env python3
"""
Generic Steering Gateway - Business logic layer for Generic Steering MQTT operations
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .generic_steering_mqtt_client import GenericSteeringMqttClient

logger = logging.getLogger(__name__)


class GenericSteeringGateway:
    """
    Generic Steering Gateway - Encapsulates all Generic Steering MQTT operations
    
    This gateway provides business logic methods for generic control operations,
    using the Generic Steering MQTT client as the underlying transport.
    """
    
    def __init__(self, mqtt_client: GenericSteeringMqttClient):
        self.client = mqtt_client
        self.logger = logger
        
        # Generic Steering specific topic patterns
        self.topics = {
            "command": "steering/command",
            "status": "steering/status",
            "control": "steering/control",
            "feedback": "steering/feedback",
            "config": "steering/config"
        }
        
        # Subscribe to Generic Steering topics on initialization
        self._subscribe_to_steering_topics()
        
        logger.info("🎮 Generic Steering Gateway initialized")
    
    def _subscribe_to_steering_topics(self):
        """Subscribe to all Generic Steering-related topics"""
        steering_topics = [
            "steering/+",  # All steering topics
            "steering/command/+",
            "steering/status/+", 
            "steering/control/+",
            "steering/feedback/+",
            "steering/config"
        ]
        self.client.subscribe_many(steering_topics)
    
    def _utc_timestamp(self) -> str:
        """Generate UTC timestamp"""
        return datetime.now(timezone.utc).isoformat()
    
    def send_command(self, device_id: str, command: str, parameters: Optional[Dict] = None) -> bool:
        """
        Send steering command to device
        
        Args:
            device_id: Target device identifier
            command: Command to execute
            parameters: Command parameters
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "device_id": device_id,
            "command": command,
            "parameters": parameters or {}
        }
        
        topic = f"{self.topics['command']}/{device_id}"
        return self.client.publish_json(topic, payload)
    
    def send_control_signal(self, device_id: str, signal_type: str, value: Any) -> bool:
        """
        Send control signal to device
        
        Args:
            device_id: Target device identifier
            signal_type: Type of control signal (e.g., "speed", "position", "enable")
            value: Signal value
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "device_id": device_id,
            "signal_type": signal_type,
            "value": value
        }
        
        topic = f"{self.topics['control']}/{device_id}"
        return self.client.publish_json(topic, payload)
    
    def send_status_update(self, device_id: str, status: str, details: Optional[Dict] = None) -> bool:
        """
        Send device status update
        
        Args:
            device_id: Device identifier
            status: Current status
            details: Additional status details
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "device_id": device_id,
            "status": status,
            "details": details or {}
        }
        
        topic = f"{self.topics['status']}/{device_id}"
        return self.client.publish_json(topic, payload)
    
    def send_feedback(self, device_id: str, feedback_type: str, data: Dict[str, Any]) -> bool:
        """
        Send device feedback
        
        Args:
            device_id: Device identifier
            feedback_type: Type of feedback (e.g., "position", "sensor", "error")
            data: Feedback data
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "device_id": device_id,
            "feedback_type": feedback_type,
            "data": data
        }
        
        topic = f"{self.topics['feedback']}/{device_id}"
        return self.client.publish_json(topic, payload)
    
    def update_device_config(self, device_id: str, config: Dict[str, Any]) -> bool:
        """
        Update device configuration
        
        Args:
            device_id: Device identifier
            config: Configuration parameters
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "device_id": device_id,
            "config": config
        }
        
        return self.client.publish_json(self.topics["config"], payload)
    
    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get latest status for specific device"""
        topic = f"{self.topics['status']}/{device_id}"
        buffer = self.client.get_buffer(topic)
        if buffer:
            return buffer[-1]["payload"]
        return None
    
    def get_device_feedback(self, device_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get feedback history for specific device"""
        topic = f"{self.topics['feedback']}/{device_id}"
        buffer = self.client.get_buffer(topic)
        return list(buffer)[-limit:]
    
    def get_command_history(self, device_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get command history for specific device"""
        topic = f"{self.topics['command']}/{device_id}"
        buffer = self.client.get_buffer(topic)
        return list(buffer)[-limit:]
    
    def is_connected(self) -> bool:
        """Check if Generic Steering MQTT client is connected"""
        return self.client.connected
    
    def add_command_callback(self, device_id: str, callback):
        """Add callback for device commands"""
        pattern = f"{self.topics['command']}/{device_id}"
        self.client.add_callback(pattern, callback)
    
    def add_status_callback(self, device_id: str, callback):
        """Add callback for device status updates"""
        pattern = f"{self.topics['status']}/{device_id}"
        self.client.add_callback(pattern, callback)
    
    def add_feedback_callback(self, device_id: str, callback):
        """Add callback for device feedback"""
        pattern = f"{self.topics['feedback']}/{device_id}"
        self.client.add_callback(pattern, callback)