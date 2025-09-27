"""
MQTT Client Singleton for Message Center
Thread-safe singleton implementation with reconnect logic
"""

import json
import logging
import threading
import time
from collections import deque
from typing import Any, Callable, Dict, List, Optional

import paho.mqtt.client as mqtt

from .mqtt_config import MqttConfig


class MqttClient:
    """
    Thread-safe MQTT Client Singleton with automatic reconnection
    Manages up to 1000 messages in memory
    """
    
    _instance: Optional['MqttClient'] = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls, config: MqttConfig) -> 'MqttClient':
        """Singleton pattern implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: MqttConfig):
        """Initialize MQTT client (only once)"""
        if self._initialized:
            return
            
        self.logger = logging.getLogger("omf2.message_center.mqtt_client")
        self.config = config
        self.connected = False
        
        # Message history with max 1000 messages
        self._history = deque(maxlen=1000)
        self._history_lock = threading.Lock()
        
        # Callbacks
        self._on_message_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._on_connect_callbacks: List[Callable[[], None]] = []
        self._on_disconnect_callbacks: List[Callable[[], None]] = []
        
        # MQTT client setup
        self.client = mqtt.Client(
            client_id=config.client_id,
            clean_session=config.clean_session,
            protocol=config.protocol,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        
        if config.username:
            self.client.username_pw_set(config.username, config.password or "")
            
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Reconnect configuration
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        
        self._initialized = True
        self.logger.info(f"MQTT Client initialized: {config.host}:{config.port}")
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker with automatic reconnection
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.logger.info(f"Connecting to MQTT broker: {self.config.host}:{self.config.port}")
            self.client.connect(self.config.host, self.config.port, self.config.keepalive)
            self.client.loop_start()
            
            # Wait for connection (max 10 seconds)
            for _ in range(100):
                if self.connected:
                    self.logger.info("MQTT connection established")
                    return True
                time.sleep(0.1)
                
            self.logger.warning("MQTT connection timeout")
            return False
            
        except Exception as e:
            self.logger.error(f"MQTT connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.logger.info("MQTT client disconnected")
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
    
    def subscribe(self, topic: str = "#", qos: int = 0) -> bool:
        """
        Subscribe to MQTT topic
        
        Args:
            topic: MQTT topic pattern (default: # for all topics)
            qos: Quality of Service level
            
        Returns:
            bool: True if subscription successful
        """
        if not self.connected:
            self.logger.warning("Cannot subscribe: not connected")
            return False
            
        try:
            result, _ = self.client.subscribe(topic, qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Subscribed to topic: {topic}")
                return True
            else:
                self.logger.error(f"Failed to subscribe to {topic}: {result}")
                return False
        except Exception as e:
            self.logger.error(f"Error subscribing to {topic}: {e}")
            return False
    
    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
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
        if not self.connected:
            self.logger.warning("Cannot publish: not connected")
            return False
            
        try:
            # Convert payload to JSON if not already string/bytes
            if isinstance(payload, (dict, list)):
                data = json.dumps(payload)
            elif isinstance(payload, str):
                data = payload
            else:
                data = str(payload)
                
            result = self.client.publish(topic, data, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to {topic}: {data}")
                
                # Add to history
                self._add_to_history({
                    "type": "sent",
                    "topic": topic,
                    "payload": payload,
                    "timestamp": time.time(),
                    "qos": qos,
                    "retain": retain
                })
                return True
            else:
                self.logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing to {topic}: {e}")
            return False
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages from history
        
        Returns:
            List[Dict]: List of message dictionaries
        """
        with self._history_lock:
            return list(self._history)
    
    def clear_history(self):
        """Clear message history"""
        with self._history_lock:
            self._history.clear()
        self.logger.info("Message history cleared")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get connection status and statistics
        
        Returns:
            Dict: Connection status information
        """
        with self._history_lock:
            total_messages = len(self._history)
            sent_messages = sum(1 for msg in self._history if msg.get("type") == "sent")
            received_messages = total_messages - sent_messages
        
        return {
            "connected": self.connected,
            "broker": f"{self.config.host}:{self.config.port}",
            "client_id": self.config.client_id,
            "messages": {
                "total": total_messages,
                "sent": sent_messages,
                "received": received_messages,
                "max_capacity": self._history.maxlen
            }
        }
    
    def add_on_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for incoming messages"""
        self._on_message_callbacks.append(callback)
    
    def add_on_connect_callback(self, callback: Callable[[], None]):
        """Add callback for connection events"""
        self._on_connect_callbacks.append(callback)
    
    def add_on_disconnect_callback(self, callback: Callable[[], None]):
        """Add callback for disconnection events"""
        self._on_disconnect_callbacks.append(callback)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Internal callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            self.logger.info("MQTT connected successfully")
            
            # Auto-subscribe to all topics
            self.subscribe("#")
            
            # Call user callbacks
            for callback in self._on_connect_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in connect callback: {e}")
        else:
            self.logger.error(f"MQTT connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Internal callback for MQTT disconnection"""
        self.connected = False
        self.logger.warning(f"MQTT disconnected with code: {rc}")
        
        # Call user callbacks
        for callback in self._on_disconnect_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in disconnect callback: {e}")
    
    def _on_message(self, client, userdata, msg):
        """Internal callback for MQTT messages"""
        try:
            # Decode payload
            try:
                payload = json.loads(msg.payload.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload = msg.payload.decode('utf-8', errors='replace')
            
            message_data = {
                "type": "received",
                "topic": msg.topic,
                "payload": payload,
                "timestamp": time.time(),
                "qos": msg.qos,
                "retain": msg.retain
            }
            
            # Add to history
            self._add_to_history(message_data)
            
            # Call user callbacks
            for callback in self._on_message_callbacks:
                try:
                    callback(message_data)
                except Exception as e:
                    self.logger.error(f"Error in message callback: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _add_to_history(self, message: Dict[str, Any]):
        """Thread-safe method to add message to history"""
        with self._history_lock:
            self._history.append(message)
    
    @classmethod
    def reset_singleton(cls):
        """Reset singleton for testing purposes"""
        with cls._lock:
            if cls._instance:
                try:
                    cls._instance.disconnect()
                except:
                    pass
            cls._instance = None
            cls._initialized = False