#!/usr/bin/env python3
"""
Message Center MQTT Client - Singleton implementation for Message Center domain
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable
from collections import defaultdict, deque

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MessageCenterMqttClient:
    """Singleton MQTT Client for Message Center domain operations"""
    
    def __init__(self, host: str = "localhost", port: int = 1883, 
                 username: Optional[str] = None, password: Optional[str] = None,
                 client_id: Optional[str] = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id or f"msgcenter_client_{int(time.time())}"
        
        # MQTT client setup
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
        if username:
            self.client.username_pw_set(username, password or "")
            
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.connected = False
        self._subscribed_topics = set()
        self._message_buffers = defaultdict(lambda: deque(maxlen=1000))
        self._callbacks = defaultdict(list)
        
        logger.info(f"💬 Message Center MQTT Client initialized: {self.client_id}")
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"❌ Message Center MQTT connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("🔌 Message Center MQTT Client disconnected")
    
    def subscribe(self, topic: str, qos: int = 1) -> bool:
        """Subscribe to a topic"""
        if topic not in self._subscribed_topics:
            try:
                self.client.subscribe(topic, qos)
                self._subscribed_topics.add(topic)
                logger.info(f"📬 Message Center subscribed to: {topic}")
                return True
            except Exception as e:
                logger.error(f"❌ Message Center subscription failed for {topic}: {e}")
                return False
        return True
    
    def subscribe_many(self, topics: List[str], qos: int = 1) -> bool:
        """Subscribe to multiple topics"""
        success = True
        for topic in topics:
            if not self.subscribe(topic, qos):
                success = False
        return success
    
    def publish(self, topic: str, payload: str, qos: int = 1) -> bool:
        """Publish message to topic"""
        try:
            result = self.client.publish(topic, payload, qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📤 Message Center published to {topic}: {payload[:100]}...")
                return True
            else:
                logger.error(f"❌ Message Center publish failed to {topic}: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"❌ Message Center publish exception for {topic}: {e}")
            return False
    
    def publish_json(self, topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
        """Publish JSON payload to topic"""
        import json
        return self.publish(topic, json.dumps(payload), qos)
    
    def get_buffer(self, topic: str) -> deque:
        """Get message buffer for a topic"""
        return self._message_buffers[topic]
    
    def add_callback(self, topic_pattern: str, callback: Callable[[str, Dict[str, Any]], None]):
        """Add callback for topic pattern"""
        self._callbacks[topic_pattern].append(callback)
        logger.info(f"📞 Message Center callback added for pattern: {topic_pattern}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect callback"""
        if rc == 0:
            self.connected = True
            logger.info("✅ Message Center MQTT Client connected")
        else:
            logger.error(f"❌ Message Center MQTT connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect callback"""
        self.connected = False
        logger.info(f"🔌 Message Center MQTT Client disconnected (code: {rc})")
    
    def _on_message(self, client, userdata, msg):
        """MQTT on_message callback"""
        try:
            topic = msg.topic
            payload_str = msg.payload.decode('utf-8')
            
            # Try to parse as JSON
            try:
                import json
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                payload = {"raw": payload_str}
            
            # Store in buffer
            self._message_buffers[topic].append({
                "timestamp": time.time(),
                "topic": topic,
                "payload": payload
            })
            
            # Execute callbacks
            import fnmatch
            for pattern, callbacks in self._callbacks.items():
                if fnmatch.fnmatch(topic, pattern):
                    for callback in callbacks:
                        try:
                            callback(topic, payload)
                        except Exception as e:
                            logger.error(f"❌ Message Center callback error for {topic}: {e}")
            
            logger.debug(f"📨 Message Center received: {topic} -> {payload_str[:100]}...")
            
        except Exception as e:
            logger.error(f"❌ Message Center message processing error: {e}")


# Singleton instance
_message_center_mqtt_client = None


def get_message_center_mqtt_client(**kwargs) -> MessageCenterMqttClient:
    """Get singleton Message Center MQTT client instance"""
    global _message_center_mqtt_client
    if _message_center_mqtt_client is None:
        _message_center_mqtt_client = MessageCenterMqttClient(**kwargs)
        logger.info("💬 Message Center MQTT Client singleton created")
    return _message_center_mqtt_client


def cleanup_message_center_mqtt_client():
    """Cleanup Message Center MQTT client singleton"""
    global _message_center_mqtt_client
    if _message_center_mqtt_client:
        _message_center_mqtt_client.disconnect()
        _message_center_mqtt_client = None
        logger.info("🧹 Message Center MQTT Client singleton cleaned up")


# Export singleton instance
message_center_mqtt_client = get_message_center_mqtt_client()