#!/usr/bin/env python3
"""
MQTT Mock System für Fischertechnik Agile Production Simulation
Orbis Development - MQTT Interface Mocking
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import paho.mqtt.client as mqtt
import threading
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FischertechnikModuleMock:
    """Mock für ein einzelnes Fischertechnik Modul"""
    
    def __init__(self, serial_number: str, module_type: str, mqtt_client: mqtt.Client):
        self.serial_number = serial_number
        self.module_type = module_type
        self.mqtt_client = mqtt_client
        self.mqtt_topic_base = f"module/v1/ff/{serial_number}"
        
        # Module State
        self.header_id = 1
        self.order_id = "0"
        self.order_update_id = 0
        self.action_state = {
            "id": None,
            "state": "IDLE",
            "command": None,
            "metadata": {}
        }
        self.loads = []
        self.errors = []
        self.paused = False
        self.operating_mode = "AUTOMATIC"
        
        # Connection State
        self.connection_state = "ONLINE"
        self.version = "1.0.0"
        self.manufacturer = "Fischertechnik"
        
        # Subscribe to topics
        self._subscribe_to_topics()
        
        # Publish initial state
        self._publish_connection_state()
        self._publish_state()
        
    def _subscribe_to_topics(self):
        """Subscribe to relevant MQTT topics"""
        topics = [
            f"{self.mqtt_topic_base}/order",
            f"{self.mqtt_topic_base}/instantAction"
        ]
        
        for topic in topics:
            self.mqtt_client.subscribe(topic)
            logger.info(f"Subscribed to {topic}")
    
    def _publish_connection_state(self):
        """Publish connection state"""
        connection_msg = {
            "headerId": self.header_id,
            "timestamp": datetime.now().isoformat(),
            "version": self.version,
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "connectionState": self.connection_state
        }
        
        topic = f"{self.mqtt_topic_base}/connection"
        self.mqtt_client.publish(topic, json.dumps(connection_msg), qos=1, retain=True)
        logger.info(f"Published connection state: {self.connection_state}")
    
    def _publish_state(self):
        """Publish current state"""
        state_msg = {
            "headerId": self.header_id,
            "timestamp": datetime.now().isoformat(),
            "serialNumber": self.serial_number,
            "actionState": self.action_state,
            "loads": self.loads,
            "errors": self.errors,
            "paused": self.paused,
            "operatingMode": self.operating_mode,
            "orderId": self.order_id,
            "orderUpdateId": self.order_update_id
        }
        
        topic = f"{self.mqtt_topic_base}/state"
        self.mqtt_client.publish(topic, json.dumps(state_msg), qos=1)
        logger.info(f"Published state: {self.action_state['state']}")
    
    def handle_order(self, order_data: Dict[str, Any]):
        """Handle incoming order"""
        logger.info(f"Received order: {order_data}")
        
        # Extract order information
        order_command = order_data.get("action", {}).get("command")
        action_id = order_data.get("action", {}).get("id")
        order_id = order_data.get("orderId")
        order_update_id = order_data.get("orderUpdateId")
        
        # Validate order
        if not self._validate_order(order_data):
            self._publish_error("Invalid order", "WARNING")
            return
        
        # Update state
        self.order_id = order_id
        self.order_update_id = order_update_id
        self.action_state.update({
            "id": action_id,
            "state": "PENDING",
            "command": order_command
        })
        
        self._publish_state()
        
        # Simulate processing
        self._simulate_order_processing(order_command)
    
    def handle_instant_action(self, action_data: Dict[str, Any]):
        """Handle instant action"""
        logger.info(f"Received instant action: {action_data}")
        
        # Extract action information
        action = action_data.get("actions", [{}])[0]
        action_type = action.get("actionType")
        action_id = action.get("actionId")
        
        # Update state
        self.action_state.update({
            "id": action_id,
            "state": "PENDING",
            "command": action_type
        })
        
        self._publish_state()
        
        # Simulate instant action processing
        self._simulate_instant_action(action_type)
    
    def _validate_order(self, order_data: Dict[str, Any]) -> bool:
        """Validate incoming order"""
        required_fields = ["serialNumber", "orderId", "action"]
        
        for field in required_fields:
            if field not in order_data:
                return False
        
        if order_data["serialNumber"] != self.serial_number:
            return False
        
        return True
    
    def _simulate_order_processing(self, command: str):
        """Simulate order processing with state transitions"""
        # Start processing
        self.action_state["state"] = "RUNNING"
        self._publish_state()
        
        # Simulate processing time based on command
        processing_time = self._get_processing_time(command)
        time.sleep(processing_time)
        
        # Complete processing
        self.action_state["state"] = "FINISHED"
        self.header_id += 1
        self._publish_state()
        
        logger.info(f"Order completed: {command}")
    
    def _simulate_instant_action(self, action_type: str):
        """Simulate instant action processing"""
        # Start processing
        self.action_state["state"] = "RUNNING"
        self._publish_state()
        
        # Simulate quick processing
        time.sleep(1)
        
        # Complete processing
        self.action_state["state"] = "FINISHED"
        self.header_id += 1
        self._publish_state()
        
        logger.info(f"Instant action completed: {action_type}")
    
    def _get_processing_time(self, command: str) -> float:
        """Get processing time for different commands"""
        processing_times = {
            "PICK": 3.0,
            "DROP": 2.0,
            "MILL": 10.0,
            "DRILL": 8.0,
            "HEAT": 15.0,
            "CHECK_QUALITY": 5.0,
            "STORE": 4.0,
            "RETRIEVE": 4.0
        }
        
        return processing_times.get(command, 5.0)
    
    def _publish_error(self, error_message: str, error_level: str = "WARNING"):
        """Publish error message"""
        error = {
            "timestamp": datetime.now().isoformat(),
            "errorType": "MockError",
            "errorMessage": error_message,
            "errorLevel": error_level,
            "errorReferences": [
                {"topic": "order"},
                {"headerId": self.header_id},
                {"orderId": self.order_id},
                {"orderUpdateId": self.order_update_id}
            ]
        }
        
        self.errors.append(error)
        self._publish_state()

class MQTTMockSystem:
    """Hauptsystem für MQTT Mocking"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.mqtt_client = mqtt.Client()
        self.modules: Dict[str, FischertechnikModuleMock] = {}
        
        # Setup MQTT client
        self._setup_mqtt_client()
    
    def _setup_mqtt_client(self):
        """Setup MQTT client with callbacks"""
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            # Extract serial number from topic
            # topic format: module/v1/ff/{serialNumber}/{action}
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                serial_number = topic_parts[3]
                action_type = topic_parts[4] if len(topic_parts) > 4 else None
                
                if serial_number in self.modules:
                    module = self.modules[serial_number]
                    
                    if action_type == "order":
                        module.handle_order(payload)
                    elif action_type == "instantAction":
                        module.handle_instant_action(payload)
                    else:
                        logger.warning(f"Unknown action type: {action_type}")
                else:
                    logger.warning(f"Module not found: {serial_number}")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.info("Disconnected from MQTT broker")
    
    def add_module(self, serial_number: str, module_type: str):
        """Add a new module to the mock system"""
        module = FischertechnikModuleMock(serial_number, module_type, self.mqtt_client)
        self.modules[serial_number] = module
        logger.info(f"Added module: {module_type} ({serial_number})")
    
    def start(self):
        """Start the MQTT mock system"""
        try:
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
            logger.info("MQTT Mock System started")
        except Exception as e:
            logger.error(f"Failed to start MQTT system: {e}")
    
    def stop(self):
        """Stop the MQTT mock system"""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info("MQTT Mock System stopped")

def create_demo_modules():
    """Create demo modules for testing"""
    mock_system = MQTTMockSystem()
    
    # Add different module types
    modules = [
        ("FF22-001", "MILL"),
        ("FF22-002", "DRILL"),
        ("FF22-003", "OVEN"),
        ("FF22-004", "AIQS"),
        ("FF22-005", "HBW"),
        ("FF22-006", "DPS")
    ]
    
    for serial_number, module_type in modules:
        mock_system.add_module(serial_number, module_type)
    
    return mock_system

if __name__ == "__main__":
    # Create and start mock system
    mock_system = create_demo_modules()
    mock_system.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        mock_system.stop()
