#!/usr/bin/env python3
"""
Test Order Trigger Script
Testet die Auftragsauslösung über MQTT ohne Dashboard
"""

import json
import uuid
import time
import argparse
from datetime import datetime
import paho.mqtt.client as mqtt
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OrderTriggerTester:
    """Testet die Auftragsauslösung über MQTT"""
    
    def __init__(self, broker_host="192.168.1.100", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.mqtt_client = mqtt.Client()
        self.connected = False
        
        # Setup MQTT client
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        self.mqtt_client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info(f"✅ Connected to MQTT broker: {self.broker_host}")
            self.connected = True
        else:
            logger.error(f"❌ Failed to connect to MQTT broker, return code: {rc}")
            self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 Received: {msg.topic}")
            logger.info(f"   Payload: {json.dumps(payload, indent=2)}")
        except Exception as e:
            logger.warning(f"⚠️ Could not parse message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.info("🔌 Disconnected from MQTT broker")
        self.connected = False
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            if self.connected:
                # Subscribe to relevant topics
                topics = [
                    "ccu/order/active",
                    "ccu/order/completed", 
                    "/j1/txt/1/f/i/order",
                    "module/v1/ff/+/state"
                ]
                
                for topic in topics:
                    self.mqtt_client.subscribe(topic)
                    logger.info(f"📡 Subscribed to: {topic}")
                
                return True
            else:
                logger.error("❌ Connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def send_order(self, order_type="WARE_EINGANG", workpiece_color="WHITE", workpiece_id="W1"):
        """Send order via MQTT"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT broker")
            return False
        
        try:
            # Create order message based on session analysis
            order_message = {
                "ts": datetime.now().isoformat() + "Z",
                "state": "WAITING_FOR_ORDER",
                "orderType": order_type,
                "workpieceColor": workpiece_color,
                "workpieceId": workpiece_id,
                "orderId": str(uuid.uuid4())
            }
            
            topic = "/j1/txt/1/f/i/order"
            
            # Send message
            result = self.mqtt_client.publish(topic, json.dumps(order_message), qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✅ Order sent successfully")
                logger.info(f"📡 Topic: {topic}")
                logger.info(f"📦 Order Type: {order_type}")
                logger.info(f"🎨 Workpiece: {workpiece_color} ({workpiece_id})")
                return True
            else:
                logger.error(f"❌ Failed to send order: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending order: {e}")
            return False
    
    def send_ccu_order(self, order_type="WARE_EINGANG", metadata=None):
        """Send order via CCU"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT broker")
            return False
        
        try:
            if metadata is None:
                metadata = {
                    "priority": "NORMAL",
                    "timeout": 300
                }
            
            # Create CCU order message
            ccu_message = {
                "orderId": str(uuid.uuid4()),
                "orderType": order_type,
                "timestamp": datetime.now().isoformat() + "Z",
                "metadata": metadata
            }
            
            topic = "ccu/order/active"
            
            # Send message
            result = self.mqtt_client.publish(topic, json.dumps(ccu_message), qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✅ CCU Order sent successfully")
                logger.info(f"📡 Topic: {topic}")
                logger.info(f"📦 Order Type: {order_type}")
                return True
            else:
                logger.error(f"❌ Failed to send CCU order: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending CCU order: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.connected:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("🔌 Disconnected from MQTT broker")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Order Trigger Script")
    parser.add_argument("--broker", default="192.168.1.100", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--order-type", default="WARE_EINGANG", 
                       choices=["WARE_EINGANG", "AUFTRAG", "AI_NOT_OK"],
                       help="Type of order to send")
    parser.add_argument("--color", default="WHITE",
                       choices=["WHITE", "RED", "BLUE"],
                       help="Workpiece color")
    parser.add_argument("--workpiece-id", default="W1", help="Workpiece ID")
    parser.add_argument("--ccu", action="store_true", help="Send via CCU instead of TXT")
    
    args = parser.parse_args()
    
    print("🎯 Order Trigger Test Script")
    print("=" * 50)
    print(f"Broker: {args.broker}:{args.port}")
    print(f"Order Type: {args.order_type}")
    print(f"Workpiece: {args.color} ({args.workpiece_id})")
    print(f"Via CCU: {args.ccu}")
    print("=" * 50)
    
    # Create tester
    tester = OrderTriggerTester(args.broker, args.port)
    
    try:
        # Connect to broker
        print("🔗 Connecting to MQTT broker...")
        if not tester.connect():
            print("❌ Failed to connect")
            return
        
        # Wait a moment for connection
        time.sleep(2)
        
        # Send order
        print(f"📤 Sending {args.order_type} order...")
        
        if args.ccu:
            success = tester.send_ccu_order(args.order_type)
        else:
            success = tester.send_order(args.order_type, args.color, args.workpiece_id)
        
        if success:
            print("✅ Order sent successfully!")
            print("📡 Listening for responses...")
            
            # Listen for responses for 10 seconds
            time.sleep(10)
        else:
            print("❌ Failed to send order")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        tester.disconnect()
        print("🔌 Disconnected")

if __name__ == "__main__":
    main()
