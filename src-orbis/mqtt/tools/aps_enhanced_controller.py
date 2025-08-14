#!/usr/bin/env python3
"""
APS Enhanced Controller - Fischertechnik APS
Enhanced module controller using MQTT message library
"""

import json
import time
import uuid
import argparse
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
import logging

# Import our message library
from mqtt_message_library import MQTTMessageLibrary, create_message_from_template, list_available_templates, get_template_info

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APSEnhancedController:
    """Enhanced APS Controller using MQTT message library"""
    
    def __init__(self, broker_host: str = "192.168.0.100", broker_port: int = 1883,
                 username: str = "default", password: str = "default"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.mqtt_client = mqtt.Client()
        self.message_library = MQTTMessageLibrary()
        
        # Setup MQTT client
        self._setup_mqtt_client()
        
        # Connect to broker
        self._connect_to_broker()
        
        # Subscribe to all state topics
        self._subscribe_to_topics()
        
        logger.info(f"APS Enhanced Controller connected to {broker_host}:{broker_port}")
    
    def _setup_mqtt_client(self):
        """Setup MQTT client with callbacks"""
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect
        
        # Set authentication
        self.mqtt_client.username_pw_set(self.username, self.password)
    
    def _connect_to_broker(self):
        """Connect to APS MQTT broker"""
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
            logger.info(f"Connected to APS MQTT broker: {self.broker_host}")
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
                
                # Find module name
                module_name = "UNKNOWN"
                for name, config in self.message_library.APS_MODULES.items():
                    if config['serial'] == serial_number:
                        module_name = name
                        break
                
                logger.info(f"📨 {module_name} ({serial_number}) - {action_type}")
                
                # Check for success/failure
                if "actionState" in payload:
                    state = payload["actionState"].get("state", "UNKNOWN")
                    command = payload["actionState"].get("command", "UNKNOWN")
                    logger.info(f"🎯 Status: {state}, Command: {command}")
                    
                    if state == "RUNNING":
                        logger.info("✅ Command accepted and running!")
                    elif state == "FINISHED":
                        logger.info("✅ Command completed successfully!")
                    elif state == "FAILED":
                        logger.info("❌ Command failed!")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.info("Disconnected from MQTT broker")
    
    def send_working_order(self, module_name: str, command: str, metadata: dict = None):
        """Send a working order using the message library"""
        try:
            # Create message using library
            order_data = self.message_library.create_order_message(module_name, command, metadata)
            
            # Get topic
            topic = self.message_library.get_topic(module_name, "order")
            
            # Send message
            self.mqtt_client.publish(topic, json.dumps(order_data), qos=1)
            
            logger.info(f"📤 Sent working order to {module_name}: {command}")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   {json.dumps(order_data, indent=2)}")
            
            return order_data
            
        except ValueError as e:
            logger.error(f"❌ Error creating message: {e}")
            return None
    
    def send_template_message(self, template_name: str):
        """Send a message using a pre-defined template"""
        try:
            # Create message from template
            order_data = create_message_from_template(template_name)
            
            # Get template info
            template_info = get_template_info(template_name)
            module_name = template_info["module"]
            
            # Get topic
            topic = self.message_library.get_topic(module_name, "order")
            
            # Send message
            self.mqtt_client.publish(topic, json.dumps(order_data), qos=1)
            
            logger.info(f"📤 Sent template message: {template_name}")
            logger.info(f"   Description: {template_info['description']}")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   {json.dumps(order_data, indent=2)}")
            
            return order_data
            
        except ValueError as e:
            logger.error(f"❌ Error creating template message: {e}")
            return None
    
    def list_modules(self):
        """List all available modules and their working commands"""
        print("\n🏭 Available APS Modules:")
        print("=" * 50)
        
        for module_name in self.message_library.list_all_modules():
            module_info = self.message_library.get_module_info(module_name)
            working_commands = self.message_library.get_working_commands(module_name)
            
            print(f"  {module_name:8} ({module_info['serial']})")
            print(f"    IP: {module_info['ip']}")
            print(f"    Working Commands: {', '.join(working_commands)}")
            print()
    
    def list_templates(self):
        """List all available message templates"""
        print("\n📋 Available Message Templates:")
        print("=" * 50)
        
        templates = list_available_templates()
        
        for template_name in templates:
            template_info = get_template_info(template_name)
            print(f"  {template_name}")
            print(f"    Description: {template_info['description']}")
            print(f"    Module: {template_info['module']}")
            print(f"    Command: {template_info['command']}")
            print(f"    Expected Response: {template_info['expected_response']}")
            print(f"    Notes: {template_info['notes']}")
            print()
    
    def stop(self):
        """Stop the enhanced controller"""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        logger.info("APS Enhanced Controller stopped")

def interactive_mode(controller: APSEnhancedController):
    """Interactive mode for enhanced control"""
    print("\n🎮 APS Enhanced Controller - Interactive Mode")
    print("=" * 60)
    
    controller.list_modules()
    controller.list_templates()
    
    print("Commands:")
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
                controller.send_working_order(module, cmd)
            elif command[0] == "template" and len(command) >= 2:
                template_name = command[1]
                controller.send_template_message(template_name)
            elif command[0] == "modules":
                controller.list_modules()
            elif command[0] == "templates":
                controller.list_templates()
            else:
                print("❌ Invalid command. Use: order <module> <command> or template <template_name>")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")

def demo_mode(controller: APSEnhancedController):
    """Demo mode with working commands"""
    print("\n🎬 Starting Enhanced Demo...")
    
    # Test working commands
    demo_sequence = [
        ("DRILL", "PICK"),
        ("MILL", "PICK"),
        ("HBW", "STORE"),
        ("AIQS", "CHECK_QUALITY"),
        ("DPS", "PICK")
    ]
    
    for module_name, command in demo_sequence:
        print(f"\n🎯 Testing {module_name} - {command}")
        
        # Send working order
        controller.send_working_order(module_name, command)
        
        # Wait for processing
        time.sleep(3)
    
    # Test template messages
    print(f"\n🎯 Testing template messages...")
    templates = ["DRILL_PICK_WHITE", "MILL_PICK_WHITE", "HBW_STORE_WHITE"]
    
    for template_name in templates:
        print(f"\n🎯 Testing template: {template_name}")
        controller.send_template_message(template_name)
        time.sleep(3)
    
    print("\n✅ Enhanced demo completed!")

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description="APS Enhanced Controller")
    parser.add_argument("--broker", default="192.168.0.100", help="MQTT broker host/IP")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--username", default="default", help="MQTT username")
    parser.add_argument("--password", default="default", help="MQTT password")
    parser.add_argument("--mode", choices=["interactive", "demo"], default="interactive",
                       help="Operation mode")
    parser.add_argument("--order", nargs=2, metavar=("MODULE", "COMMAND"),
                       help="Send single working order and exit")
    parser.add_argument("--template", metavar="TEMPLATE_NAME",
                       help="Send single template message and exit")
    
    args = parser.parse_args()
    
    try:
        # Create enhanced controller
        controller = APSEnhancedController(
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
            controller.send_working_order(module.upper(), command.upper())
            time.sleep(2)
        elif args.template:
            controller.send_template_message(args.template)
            time.sleep(2)
        elif args.mode == "demo":
            demo_mode(controller)
        else:
            interactive_mode(controller)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'controller' in locals():
            controller.stop()

if __name__ == "__main__":
    main()
