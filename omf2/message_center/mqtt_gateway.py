"""
MQTT Gateway for Message Center
Provides high-level interface for MQTT communication and message processing
"""

import logging
from typing import Any, Dict, List, Optional, Callable

from .mqtt_client import MqttClient
from .mqtt_config import MqttConfig, get_config_for_env


class MqttGateway:
    """
    High-level gateway for MQTT communication
    Provides easy-to-use interface for message center functionality
    """
    
    def __init__(self, environment: str = "mock"):
        """
        Initialize MQTT Gateway
        
        Args:
            environment: Environment to use ("live", "replay", "mock")
        """
        self.logger = logging.getLogger("omf2.message_center.mqtt_gateway")
        self.environment = environment
        self.config = get_config_for_env(environment)
        self._client: Optional[MqttClient] = None
        self._connected = False
        
        self.logger.info(f"MQTT Gateway initialized for environment: {environment}")
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker
        
        Returns:
            bool: True if connection successful
        """
        try:
            self._client = MqttClient(self.config)
            
            # Add connection callbacks
            self._client.add_on_connect_callback(self._on_connect)
            self._client.add_on_disconnect_callback(self._on_disconnect)
            
            success = self._client.connect()
            if success:
                self.logger.info(f"Gateway connected to {self.environment} environment")
            else:
                self.logger.error(f"Gateway failed to connect to {self.environment} environment")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error connecting gateway: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self._client:
            try:
                self._client.disconnect()
                self.logger.info("Gateway disconnected")
            except Exception as e:
                self.logger.error(f"Error disconnecting gateway: {e}")
    
    def is_connected(self) -> bool:
        """
        Check if gateway is connected
        
        Returns:
            bool: Connection status
        """
        return self._connected and self._client is not None
    
    def subscribe_to_all_topics(self) -> bool:
        """
        Subscribe to all MQTT topics (#)
        
        Returns:
            bool: True if subscription successful
        """
        if not self._client:
            self.logger.error("Cannot subscribe: not connected")
            return False
        
        return self._client.subscribe("#")
    
    def publish_message(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
        """
        Publish message to MQTT topic
        
        Args:
            topic: MQTT topic
            payload: Message payload
            qos: Quality of Service level
            retain: Retain flag
            
        Returns:
            bool: True if publish successful
        """
        if not self._client:
            self.logger.error("Cannot publish: not connected")
            return False
        
        return self._client.publish(topic, payload, qos, retain)
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages from history
        
        Returns:
            List[Dict]: List of message dictionaries
        """
        if not self._client:
            return []
        
        return self._client.get_messages()
    
    def get_recent_messages(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent messages from history
        
        Args:
            count: Number of recent messages to return
            
        Returns:
            List[Dict]: List of recent message dictionaries
        """
        messages = self.get_all_messages()
        return messages[-count:] if messages else []
    
    def clear_message_history(self):
        """Clear all message history"""
        if self._client:
            self._client.clear_history()
            self.logger.info("Message history cleared via gateway")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get detailed connection status
        
        Returns:
            Dict: Connection status and statistics
        """
        if not self._client:
            return {
                "connected": False,
                "environment": self.environment,
                "broker": f"{self.config.host}:{self.config.port}",
                "client_id": self.config.client_id,
                "messages": {
                    "total": 0,
                    "sent": 0,
                    "received": 0,
                    "max_capacity": 1000
                }
            }
        
        status = self._client.get_connection_status()
        status["environment"] = self.environment
        return status
    
    def add_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Add callback for incoming messages
        
        Args:
            callback: Function to call when message is received
        """
        if self._client:
            self._client.add_on_message_callback(callback)
    
    def switch_environment(self, new_environment: str) -> bool:
        """
        Switch to different environment
        
        Args:
            new_environment: New environment ("live", "replay", "mock")
            
        Returns:
            bool: True if switch successful
        """
        if new_environment == self.environment:
            self.logger.info(f"Already in {new_environment} environment")
            return True
        
        self.logger.info(f"Switching from {self.environment} to {new_environment}")
        
        # Disconnect current connection
        if self._client:
            self.disconnect()
        
        # Update configuration
        self.environment = new_environment
        self.config = get_config_for_env(new_environment)
        
        # Reset client singleton to force new connection
        MqttClient.reset_singleton()
        
        # Reconnect with new configuration
        return self.connect()
    
    def get_message_statistics(self) -> Dict[str, Any]:
        """
        Get message statistics
        
        Returns:
            Dict: Message statistics
        """
        messages = self.get_all_messages()
        
        if not messages:
            return {
                "total": 0,
                "sent": 0,
                "received": 0,
                "topics": [],
                "recent_activity": 0
            }
        
        # Calculate statistics
        sent_count = sum(1 for msg in messages if msg.get("type") == "sent")
        received_count = len(messages) - sent_count
        
        # Get unique topics
        topics = list(set(msg.get("topic", "") for msg in messages))
        
        # Recent activity (last 5 minutes)
        import time
        five_minutes_ago = time.time() - 300
        recent_activity = sum(1 for msg in messages if msg.get("timestamp", 0) > five_minutes_ago)
        
        return {
            "total": len(messages),
            "sent": sent_count,
            "received": received_count,
            "topics": topics,
            "recent_activity": recent_activity
        }
    
    def _on_connect(self):
        """Internal callback for connection events"""
        self._connected = True
        self.logger.info("Gateway connection established")
    
    def _on_disconnect(self):
        """Internal callback for disconnection events"""
        self._connected = False
        self.logger.warning("Gateway connection lost")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()