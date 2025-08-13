#!/usr/bin/env python3
"""
MQTT Test Client für Fischertechnik Module Testing
Orbis Development - MQTT Test Interface
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt
import logging

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MQTTTestClient:
    """Test Client für MQTT Nachrichten"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.mqtt_client = mqtt.Client()
        
        # Setup MQTT client
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        
        # Connect to broker
        self.mqtt_client.connect(broker_host, broker_port, 60)
        self.mqtt_client.loop_start()
        
        # Subscribe to all state topics
        self.mqtt_client.subscribe("module/v1/ff/+/state")
        self.mqtt_client.subscribe("module/v1/ff/+/connection")
        
        logger.info("MQTT Test Client started")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("Test Client connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            logger.info(f"Received: {topic}")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def send_order(self, serial_number: str, command: str, order_id: str = None):
        """Send order to module"""
        if order_id is None:
            order_id = str(uuid.uuid4())
        
        order_data = {
            "serialNumber": serial_number,
            "orderId": order_id,
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": command,
                "metadata": {
                    "priority": "NORMAL",
                    "timeout": 300
                }
            }
        }
        
        topic = f"module/v1/ff/{serial_number}/order"
        self.mqtt_client.publish(topic, json.dumps(order_data), qos=1)
        
        logger.info(f"Sent order to {serial_number}: {command}")
        return order_id
    
    def send_instant_action(self, serial_number: str, action_type: str):
        """Send instant action to module"""
        action_data = {
            "serialNumber": serial_number,
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "actions": [
                {
                    "actionId": str(uuid.uuid4()),
                    "actionType": action_type,
                    "metadata": {}
                }
            ]
        }
        
        topic = f"module/v1/ff/{serial_number}/instantAction"
        self.mqtt_client.publish(topic, json.dumps(action_data), qos=1)
        
        logger.info(f"Sent instant action to {serial_number}: {action_type}")
    
    def stop(self):
        """Stop the test client"""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info("MQTT Test Client stopped")

def run_demo():
    """Run demo with different module types"""
    test_client = MQTTTestClient()
    
    # Wait for modules to initialize
    time.sleep(2)
    
    logger.info("Starting MQTT Demo...")
    
    # Test different modules and commands
    test_cases = [
        ("FF22-001", "MILL", "MILL"),
        ("FF22-002", "DRILL", "DRILL"),
        ("FF22-003", "OVEN", "HEAT"),
        ("FF22-004", "AIQS", "CHECK_QUALITY"),
        ("FF22-005", "HBW", "STORE"),
        ("FF22-006", "DPS", "PICK")
    ]
    
    for serial_number, module_type, command in test_cases:
        logger.info(f"Testing {module_type} module ({serial_number})")
        
        # Send order
        test_client.send_order(serial_number, command)
        
        # Wait for processing
        time.sleep(2)
        
        # Send instant action
        test_client.send_instant_action(serial_number, "reset")
        
        # Wait between modules
        time.sleep(3)
    
    # Test error case
    logger.info("Testing error case...")
    test_client.send_order("FF22-999", "INVALID_COMMAND")  # Non-existent module
    
    # Keep running to see responses
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Demo finished")
        test_client.stop()

if __name__ == "__main__":
    run_demo()
