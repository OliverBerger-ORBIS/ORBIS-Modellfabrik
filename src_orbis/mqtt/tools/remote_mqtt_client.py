#!/usr/bin/env python3
"""
Remote MQTT Client für Fischertechnik APS
Orbis Development - Remote Control von macOS
"""

import json
import time
import uuid
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
import logging

# Import working message library
from mqtt_message_library import MQTTMessageLibrary, create_message_from_template, list_available_templates

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RemoteFischertechnikClient:
    """Remote Client für Fischertechnik APS Steuerung"""
    
    def __init__(self, broker_host: str, broker_port: int = 1883, 
                 username: str = None, password: str = None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.mqtt_client = mqtt.Client()
        
        # Initialize message library
        self.message_library = MQTTMessageLibrary()
        
        # Setup MQTT client
        self._setup_mqtt_client()
        
        # Connect to broker
        self._connect_to_broker()
        
        # Subscribe to all state topics
        self._subscribe_to_topics()
        
        logger.info(f"Remote Client connected to {broker_host}:{broker_port}")
    
    def _setup_mqtt_client(self):
        """Setup MQTT client with callbacks"""
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        # Set authentication if provided
        if self.username and self.password:
            self.mqtt_client.username_pw_set(self.username, self.password)
    
    def _connect_to_broker(self):
        """Connect to remote MQTT broker"""
        try:
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to {self.broker_host}:{self.broker_port}: {e}")
            raise
    
    def _subscribe_to_topics(self):
        """Subscribe to all relevant topics"""
        topics = [
            "module/v1/ff/+/state",
            "module/v1/ff/+/connection",
            "module/v1/ff/+/factsheet"
        ]
        
        for topic in topics:
            self.mqtt_client.subscribe(topic)
            logger.info(f"Subscribed to {topic}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info(f"Connected to remote MQTT broker: {self.broker_host}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            # Extract module info from topic
            topic_parts = topic.split('/')
            if len(topic_parts) >= 4:
                serial_number = topic_parts[3]
                action_type = topic_parts[4] if len(topic_parts) > 4 else None
                
                logger.info(f"📨 {serial_number} - {action_type}")
                logger.info(f"   {json.dumps(payload, indent=2)}")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.info("Disconnected from MQTT broker")
    
    def send_order(self, module_name: str, command: str, metadata: dict = None):
        """Send working order using message library"""
        try:
            # Create message using library
            order_data = self.message_library.create_order_message(module_name, command, metadata)
            
            # Get topic
            topic = self.message_library.get_topic(module_name, "order")
            
            # Send message
            self.mqtt_client.publish(topic, json.dumps(order_data), qos=1)
            
            logger.info(f"📤 Sent working order to {module_name}: {command}")
            logger.info(f"   Topic: {topic}")
            return order_data["orderId"]
            
        except ValueError as e:
            logger.error(f"❌ Error creating message: {e}")
            return None
    
    def send_template_message(self, template_name: str):
        """Send a message using a pre-defined template"""
        try:
            # Create message from template
            order_data = create_message_from_template(template_name)
            
            # Get template info
            from mqtt_message_library import get_template_info
            template_info = get_template_info(template_name)
            module_name = template_info["module"]
            
            # Get topic
            topic = self.message_library.get_topic(module_name, "order")
            
            # Send message
            self.mqtt_client.publish(topic, json.dumps(order_data), qos=1)
            
            logger.info(f"📤 Sent template message: {template_name}")
            logger.info(f"   Description: {template_info['description']}")
            logger.info(f"   Topic: {topic}")
            return order_data["orderId"]
            
        except ValueError as e:
            logger.error(f"❌ Error creating template message: {e}")
            return None
    
    def send_instant_action(self, serial_number: str, action_type: str):
        """Send instant action to remote module"""
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
        
        logger.info(f"📤 Sent instant action to {serial_number}: {action_type}")
    
    def get_module_status(self, serial_number: str):
        """Request module status"""
        topic = f"module/v1/ff/{serial_number}/state"
        logger.info(f"📤 Requesting status for {serial_number}")
    
    def stop(self):
        """Stop the remote client"""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info("Remote Client stopped")

def interactive_mode(client: RemoteFischertechnikClient):
    """Interactive mode for manual control"""
    print("\n🎮 Interactive Fischertechnik Control")
    print("=" * 60)
    
    # List available modules
    print("Available modules:")
    for module_name in client.message_library.list_all_modules():
        module_info = client.message_library.get_module_info(module_name)
        working_commands = client.message_library.get_working_commands(module_name)
        print(f"  {module_name:8} ({module_info['serial']}) - {', '.join(working_commands)}")
    
    # List available templates
    print("\nAvailable templates:")
    templates = list_available_templates()
    for template_name in templates:
        print(f"  {template_name}")
    
    print("\nCommands:")
    print("  order <module> <command>     - Send working order")
    print("  template <template_name>     - Send template message")
    print("  modules                      - List all modules")
    print("  templates                    - List all templates")
    print("  quit                         - Exit")
    print("=" * 60)
    
    while True:
        try:
            command = input("\n> ").strip().split()
            
            if not command:
                continue
                
            if command[0] == "quit":
                break
            elif command[0] == "order" and len(command) >= 3:
                module, cmd = command[1].upper(), command[2].upper()
                client.send_order(module, cmd)
            elif command[0] == "template" and len(command) >= 2:
                template_name = command[1]
                client.send_template_message(template_name)
            elif command[0] == "modules":
                print("\n🏭 Available modules:")
                for module_name in client.message_library.list_all_modules():
                    module_info = client.message_library.get_module_info(module_name)
                    working_commands = client.message_library.get_working_commands(module_name)
                    print(f"  {module_name:8} ({module_info['serial']}) - {', '.join(working_commands)}")
            elif command[0] == "templates":
                print("\n📋 Available templates:")
                templates = list_available_templates()
                for template_name in templates:
                    print(f"  {template_name}")
            else:
                print("❌ Invalid command. Use: order <module> <command> or template <template_name>")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")

def demo_mode(client: RemoteFischertechnikClient):
    """Demo mode with predefined sequence"""
    print("\n🎬 Starting Remote Demo...")
    
    # Test sequence
    test_sequence = [
        ("SVR3QA2098", "MILL", "MILL"),
        ("SVR4H76449", "DRILL", "DRILL"),
        ("SVR4H76530", "AIQS", "CHECK_QUALITY"),
        ("SVR3QA0022", "HBW", "STORE"),
        ("SVR4H73275", "DPS", "PICK")
    ]
    
    for serial_number, module_type, command in test_sequence:
        print(f"\n🎯 Testing {module_type} module ({serial_number})")
        
        # Send order
        client.send_order(serial_number, command)
        
        # Wait for processing
        time.sleep(3)
        
        # Send instant action
        client.send_instant_action(serial_number, "reset")
        
        # Wait between modules
        time.sleep(2)
    
    print("\n✅ Demo completed!")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description="Remote Fischertechnik MQTT Client")
    parser.add_argument("--broker", required=True, help="MQTT broker host/IP")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--username", help="MQTT username")
    parser.add_argument("--password", help="MQTT password")
    parser.add_argument("--mode", choices=["interactive", "demo"], default="interactive",
                       help="Operation mode")
    parser.add_argument("--order", nargs=2, metavar=("MODULE", "COMMAND"),
                       help="Send single working order and exit")
    parser.add_argument("--template", metavar="TEMPLATE_NAME",
                       help="Send single template message and exit")
    parser.add_argument("--action", nargs=2, metavar=("SERIAL", "ACTION"),
                       help="Send single instant action and exit")
    
    args = parser.parse_args()
    
    try:
        # Create remote client
        client = RemoteFischertechnikClient(
            broker_host=args.broker,
            broker_port=args.port,
            username=args.username,
            password=args.password
        )
        
        # Wait for connection
        time.sleep(2)
        
        # Handle different modes
        if args.order:
            module, command = args.order
            client.send_order(module.upper(), command.upper())
            time.sleep(2)
        elif args.template:
            client.send_template_message(args.template)
            time.sleep(2)
        elif args.action:
            serial, action = args.action
            client.send_instant_action(serial, action)
            time.sleep(2)
        elif args.mode == "demo":
            demo_mode(client)
        else:
            interactive_mode(client)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'client' in locals():
            client.stop()

if __name__ == "__main__":
    main()
