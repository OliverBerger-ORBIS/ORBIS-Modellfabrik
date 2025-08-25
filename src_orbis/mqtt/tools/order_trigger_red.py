#!/usr/bin/env python3
"""
Order Trigger für rote Werkstücke - ORBIS APS
"""

import paho.mqtt.client as mqtt
import json
import uuid
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedWorkpieceOrderTrigger:
    def __init__(self, broker_host="192.168.0.100", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.connected = False
        self.mqtt_client = None
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            
            # Set credentials (default/default as used in other scripts)
            self.mqtt_client.username_pw_set("default", "default")
            
            # Connect to broker
            self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
            self.mqtt_client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
                
            if self.connected:
                logger.info("✅ Connected to MQTT broker")
                return True
            else:
                logger.error("❌ Connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            logger.info("🔗 MQTT Connected")
            
            # Subscribe to order responses
            client.subscribe("ccu/order/active")
            client.subscribe("ccu/order/completed")
            client.subscribe("/j1/txt/1/f/i/order")
            client.subscribe("module/v1/ff/#")
            
        else:
            logger.error(f"❌ Connection failed with code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 {msg.topic}: {json.dumps(payload, indent=2)}")
        except:
            logger.info(f"📨 {msg.topic}: {msg.payload.decode()}")
    
    def send_red_workpiece_order(self, workpiece_id="R1", order_type="WARE_EINGANG"):
        """Send order for red workpiece"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT broker")
            return False
            
        try:
            # Create order message
            order_message = {
                "ts": datetime.now().isoformat() + "Z",
                "state": "WAITING_FOR_ORDER",
                "orderType": order_type,
                "workpieceColor": "RED",
                "workpieceId": workpiece_id,
                "orderId": str(uuid.uuid4())
            }
            
            # Send to TXT Controller
            topic = "/j1/txt/1/f/i/order"
            result = self.mqtt_client.publish(topic, json.dumps(order_message), qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✅ Order sent for {workpiece_id}")
                logger.info(f"📋 Topic: {topic}")
                logger.info(f"📄 Payload: {json.dumps(order_message, indent=2)}")
                return True
            else:
                logger.error(f"❌ Failed to send order: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending order: {e}")
            return False
    
    def send_ccu_order(self, workpiece_id="R1", order_type="WARE_EINGANG"):
        """Send order via CCU"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT broker")
            return False
            
        try:
            # Create CCU order message
            ccu_order = {
                "orderId": str(uuid.uuid4()),
                "orderType": order_type,
                "workpieceColor": "RED",
                "workpieceId": workpiece_id,
                "timestamp": datetime.now().isoformat() + "Z"
            }
            
            # Send to CCU
            topic = "ccu/order/active"
            result = self.mqtt_client.publish(topic, json.dumps(ccu_order), qos=1)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"✅ CCU Order sent for {workpiece_id}")
                logger.info(f"📋 Topic: {topic}")
                logger.info(f"📄 Payload: {json.dumps(ccu_order, indent=2)}")
                return True
            else:
                logger.error(f"❌ Failed to send CCU order: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending CCU order: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("🔌 Disconnected from MQTT broker")

def main():
    """Main function"""
    print("🎯 Red Workpiece Order Trigger - ORBIS APS")
    print("=" * 50)
    
    # Available red workpieces
    red_workpieces = ["R1", "R2", "R3"]  # Only R1-R3 were stored in HBW
    order_types = ["WARE_EINGANG", "PRODUCTION", "AI_NOT_OK"]
    
    print(f"🔴 Available red workpieces: {', '.join(red_workpieces)}")
    print(f"📋 Available order types: {', '.join(order_types)}")
    print()
    
    # Create order trigger
    trigger = RedWorkpieceOrderTrigger()
    
    if not trigger.connect():
        print("❌ Failed to connect to MQTT broker")
        return
    
    try:
        while True:
            print("\n🎮 Order Trigger Menu:")
            print("1. Send TXT Controller Order")
            print("2. Send CCU Order")
            print("3. Exit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == "1":
                # TXT Controller Order
                print(f"\n🔴 Select red workpiece: {', '.join(red_workpieces)}")
                workpiece = input("Workpiece ID (e.g., R1): ").strip().upper()
                
                if workpiece not in red_workpieces:
                    print(f"❌ Invalid workpiece: {workpiece}")
                    continue
                
                print(f"\n📋 Select order type: {', '.join(order_types)}")
                order_type = input("Order type: ").strip().upper()
                
                if order_type not in order_types:
                    print(f"❌ Invalid order type: {order_type}")
                    continue
                
                print(f"\n🚀 Sending TXT Controller order for {workpiece}...")
                trigger.send_red_workpiece_order(workpiece, order_type)
                
            elif choice == "2":
                # CCU Order
                print(f"\n🔴 Select red workpiece: {', '.join(red_workpieces)}")
                workpiece = input("Workpiece ID (e.g., R1): ").strip().upper()
                
                if workpiece not in red_workpieces:
                    print(f"❌ Invalid workpiece: {workpiece}")
                    continue
                
                print(f"\n📋 Select order type: {', '.join(order_types)}")
                order_type = input("Order type: ").strip().upper()
                
                if order_type not in order_types:
                    print(f"❌ Invalid order type: {order_type}")
                    continue
                
                print(f"\n🚀 Sending CCU order for {workpiece}...")
                trigger.send_ccu_order(workpiece, order_type)
                
            elif choice == "3":
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice")
                
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    finally:
        trigger.disconnect()

if __name__ == "__main__":
    main()
