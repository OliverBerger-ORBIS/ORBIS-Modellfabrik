#!/usr/bin/env python3
"""
OMF MQTT Client - Zentrale MQTT-Verbindung und Message-Handling
Version: 3.0.0
"""

import json
import logging
import os
import threading
import time
from queue import Empty, Queue
from typing import Any, Callable, Dict, List, Optional

import paho.mqtt.client as mqtt
import yaml


class OMFMQTTClient:
    """Zentrale MQTT-Client für OMF Dashboard"""

    def __init__(self, config_path: str = None):
        """Initialize OMF MQTT Client"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), "..", "config", "mqtt_config.yml"
            )

        self.config_path = config_path
        self.config = self._load_config()

        # MQTT Client
        self.client = None
        self.connected = False
        self.connection_thread = None

        # Message handling
        self.message_queue = Queue(
            maxsize=self.config.get("performance", {})
            .get("queue", {})
            .get("max_size", 1000)
        )
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.message_history: List[Dict] = []

        # Statistics
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "connection_attempts": 0,
            "last_connection": None,
            "last_message": None,
        }

        # Setup logging
        self._setup_logging()

        # Initialize client
        self._init_client()

    def _load_config(self) -> Dict[str, Any]:
        """Load MQTT configuration"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading MQTT config: {e}")
            return {}

    def _setup_logging(self):
        """Setup logging for MQTT client"""
        log_config = self.config.get("connection", {}).get("logging", {})
        log_level = getattr(logging, log_config.get("level", "INFO"))
        log_format = log_config.get(
            "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_config.get("file", "omf_mqtt.log")),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("OMFMQTTClient")

    def _init_client(self):
        """Initialize MQTT client"""
        try:
            self.client = mqtt.Client(
                client_id=self.config.get("broker", {})
                .get("aps", {})
                .get("client_id", "omf_dashboard"),
                clean_session=self.config.get("broker", {})
                .get("aps", {})
                .get("clean_session", True),
            )

            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.on_publish = self._on_publish
            self.client.on_subscribe = self._on_subscribe

            # Set username/password if provided
            broker_config = self.config.get("broker", {}).get("aps", {})
            if broker_config.get("username"):
                self.client.username_pw_set(
                    broker_config.get("username"), broker_config.get("password")
                )

            self.logger.info("MQTT Client initialized")

        except Exception as e:
            self.logger.error(f"Error initializing MQTT client: {e}")

    def get_broker_config(self, mode: str = "live") -> Dict[str, Any]:
        """Get broker configuration based on mode"""
        if mode == "replay":
            # Replay-Station Konfiguration (Mock MQTT-Broker auf Port 1884)
            return {
                "host": "localhost",
                "port": 1884,
                "client_id": "omf_dashboard_replay",
                "clean_session": True,
                "username": None,
                "password": None,
            }
        elif mode == "mock":
            # Mock-Modus Konfiguration
            return {
                "host": "mock",
                "port": 0,
                "client_id": "omf_dashboard_mock",
                "clean_session": True,
                "username": None,
                "password": None,
            }
        else:
            # Live-Fabrik Konfiguration
            return self.config.get("broker", {}).get("aps", {})

    def connect_to_broker(self, mode: str = "live") -> bool:
        """Connect to MQTT broker with specified mode"""
        try:
            broker_config = self.get_broker_config(mode)

            host = broker_config.get("host", "192.168.0.100")
            port = broker_config.get("port", 1883)

            if mode == "replay":
                self.logger.info(f"🎬 Connecting to Replay Station: {host}:{port}")
            elif mode == "mock":
                self.logger.info(f"🧪 Mock mode activated - no real connection")
                # Simuliere erfolgreiche Verbindung für Mock-Modus
                self.connected = True
                self.stats["last_connection"] = time.time()
                return True
            else:
                self.logger.info(f"🔗 Connecting to Live Factory: {host}:{port}")

            result = self.client.connect(host, port, 60)

            if result == mqtt.MQTT_ERR_SUCCESS:
                self.client.loop_start()
                return True
            else:
                self.logger.error(f"Failed to connect: {result}")
                return False

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for successful connection"""
        if rc == 0:
            self.connected = True
            self.stats["last_connection"] = time.time()
            self.logger.info("Connected to MQTT broker")

            # Subscribe to topics
            self._subscribe_to_topics()
        else:
            self.connected = False
            self.logger.error(f"Failed to connect to MQTT broker, return code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for disconnection"""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection, return code: {rc}")
        else:
            self.logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback for received messages"""
        try:
            # Parse message
            message = {
                "topic": msg.topic,
                "payload": msg.payload.decode("utf-8"),
                "qos": msg.qos,
                "retain": msg.retain,
                "timestamp": time.time(),
            }

            # Try to parse JSON payload
            try:
                message["payload_json"] = json.loads(message["payload"])
            except (json.JSONDecodeError, ValueError):
                message["payload_json"] = None

            # Add to queue
            try:
                self.message_queue.put_nowait(message)
            except Exception:
                self.logger.warning("Message queue full, dropping message")

            # Add to message history
            self.message_history.append(message)

            # Limit history size to prevent memory issues
            max_history = (
                self.config.get("performance", {})
                .get("history", {})
                .get("max_size", 1000)
            )
            if len(self.message_history) > max_history:
                self.message_history = self.message_history[-max_history:]

            # Update statistics
            self.stats["messages_received"] += 1
            self.stats["last_message"] = time.time()

            # Call topic handlers
            self._call_topic_handlers(message)

        except Exception as e:
            self.logger.error(f"Error handling message: {e}")

    def _on_publish(self, client, userdata, mid):
        """Callback for successful publish"""
        self.stats["messages_sent"] += 1
        self.logger.debug(f"Message published with ID: {mid}")

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for successful subscription"""
        self.logger.info(f"Subscribed with QoS: {granted_qos}")

    def _subscribe_to_topics(self):
        """Subscribe to configured topics"""
        subscriptions = self.config.get("subscriptions", {})

        for _category, topics in subscriptions.items():
            for topic in topics:
                try:
                    result = self.client.subscribe(topic, qos=1)
                    if result[0] == mqtt.MQTT_ERR_SUCCESS:
                        self.logger.info(f"Subscribed to: {topic}")
                    else:
                        self.logger.error(f"Failed to subscribe to: {topic}")
                except Exception as e:
                    self.logger.error(f"Error subscribing to {topic}: {e}")

    def _call_topic_handlers(self, message: Dict):
        """Call registered handlers for topic"""
        topic = message["topic"]

        # Call exact topic handlers
        if topic in self.message_handlers:
            for handler in self.message_handlers[topic]:
                try:
                    handler(message)
                except Exception as e:
                    self.logger.error(f"Error in topic handler for {topic}: {e}")

        # Call wildcard handlers
        for pattern, handlers in self.message_handlers.items():
            if self._topic_matches_pattern(topic, pattern):
                for handler in handlers:
                    try:
                        handler(message)
                    except Exception as e:
                        self.logger.error(
                            f"Error in pattern handler for {pattern}: {e}"
                        )

    def _topic_matches_pattern(self, topic: str, pattern: str) -> bool:
        """Check if topic matches pattern (simple wildcard matching)"""
        if pattern == topic:
            return True

        # Simple wildcard matching
        if "+" in pattern or "#" in pattern:
            pattern_parts = pattern.split("/")
            topic_parts = topic.split("/")

            for i, pattern_part in enumerate(pattern_parts):
                if i >= len(topic_parts):
                    return False

                if pattern_part == "+":
                    continue
                elif pattern_part == "#":
                    return True
                elif pattern_part != topic_parts[i]:
                    return False

            return len(pattern_parts) == len(topic_parts)

        return False

    def connect(self, broker_name: str = None) -> bool:
        """Connect to MQTT broker"""
        if broker_name is None:
            broker_name = self.config.get("connection", {}).get("default_broker", "aps")

        broker_config = self.config.get("broker", {}).get(broker_name, {})

        try:
            self.stats["connection_attempts"] += 1
            self.logger.info(f"Connecting to broker: {broker_name}")

            # Connect to broker
            result = self.client.connect(
                broker_config.get("host", "localhost"),
                broker_config.get("port", 1883),
                broker_config.get("keepalive", 60),
            )

            if result == mqtt.MQTT_ERR_SUCCESS:
                # Start network loop in separate thread
                self.connection_thread = threading.Thread(
                    target=self.client.loop_forever, daemon=True
                )
                self.connection_thread.start()

                # Wait for connection
                timeout = broker_config.get("timeout", 10)
                start_time = time.time()

                while not self.connected and (time.time() - start_time) < timeout:
                    time.sleep(0.1)

                return self.connected
            else:
                self.logger.error(f"Failed to connect to broker: {result}")
                return False

        except Exception as e:
            self.logger.error(f"Error connecting to broker: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            self.client.disconnect()
            self.connected = False
            self.logger.info("Disconnected from MQTT broker")

    def publish(
        self, topic: str, payload: Any, qos: int = None, retain: bool = None
    ) -> bool:
        """Publish message to topic"""
        if not self.connected:
            self.logger.warning("Not connected to broker")
            return False

        try:
            # Convert payload to JSON if needed
            if isinstance(payload, (dict, list)):
                payload = json.dumps(payload)
            elif not isinstance(payload, str):
                payload = str(payload)

            # Get QoS and retain from config if not provided
            if qos is None:
                qos = self.config.get("connection", {}).get("message", {}).get("qos", 1)
            if retain is None:
                retain = (
                    self.config.get("connection", {})
                    .get("message", {})
                    .get("retain", False)
                )

            # Publish message
            result = self.client.publish(topic, payload, qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to {topic}: {payload}")
                return True
            else:
                self.logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False

        except Exception as e:
            self.logger.error(f"Error publishing to {topic}: {e}")
            return False

    def add_message_handler(self, topic: str, handler: Callable):
        """Add message handler for topic"""
        if topic not in self.message_handlers:
            self.message_handlers[topic] = []
        self.message_handlers[topic].append(handler)
        self.logger.info(f"Added handler for topic: {topic}")

    def remove_message_handler(self, topic: str, handler: Callable):
        """Remove message handler for topic"""
        if topic in self.message_handlers and handler in self.message_handlers[topic]:
            self.message_handlers[topic].remove(handler)
            self.logger.info(f"Removed handler for topic: {topic}")

    def get_message(self, timeout: float = None) -> Optional[Dict]:
        """Get message from queue"""
        try:
            return self.message_queue.get(timeout=timeout)
        except Empty:
            return None

    def get_message_history(self, limit: int = None) -> List[Dict]:
        """Get message history"""
        if limit is None:
            return self.message_history.copy()
        else:
            return self.message_history[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            **self.stats,
            "connected": self.connected,
            "queue_size": self.message_queue.qsize(),
            "handlers_count": len(self.message_handlers),
            "history_size": len(self.message_history),
        }

    def is_connected(self) -> bool:
        """Check if connected to broker"""
        return self.connected


# Singleton instance
_mqtt_client_instance = None


def get_omf_mqtt_client() -> OMFMQTTClient:
    """Get singleton instance of OMFMQTTClient"""
    global _mqtt_client_instance
    if _mqtt_client_instance is None:
        _mqtt_client_instance = OMFMQTTClient()
    return _mqtt_client_instance


# Backward compatibility functions
def get_mqtt_client() -> OMFMQTTClient:
    """Backward compatibility function"""
    return get_omf_mqtt_client()
