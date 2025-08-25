#!/usr/bin/env python3
"""
Simple Red Workpiece Order - ORBIS APS
Send a single order for R1
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

def send_red_order():
    """Send a simple order for R1"""
    
    # Create MQTT client
    client = mqtt.Client()
    client.username_pw_set("default", "default")
    
    connected = False
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            connected = True
            logger.info("✅ Connected to MQTT broker")
        else:
            logger.error(f"❌ Connection failed with code: {rc}")
    
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"📨 {msg.topic}: {json.dumps(payload, indent=2)}")
        except:
            logger.info(f"📨 {msg.topic}: {msg.payload.decode()}")
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to broker
        logger.info("🔗 Connecting to MQTT broker...")
        client.connect("192.168.0.100", 1883, 60)
        client.loop_start()
        
        # Wait for connection
        timeout = 10
        while not connected and timeout > 0:
            time.sleep(0.1)
            timeout -= 0.1
        
        if not connected:
            logger.error("❌ Connection timeout")
            return False
        
        # Subscribe to topics
        client.subscribe("ccu/order/active")
        client.subscribe("ccu/order/completed")
        client.subscribe("/j1/txt/1/f/i/order")
        client.subscribe("module/v1/ff/#")
        
        # Create order message for R1
        order_message = {
            "ts": datetime.now().isoformat() + "Z",
            "state": "WAITING_FOR_ORDER",
            "orderType": "WARE_EINGANG",
            "workpieceColor": "RED",
            "workpieceId": "R1",
            "orderId": str(uuid.uuid4())
        }
        
        # Send order
        topic = "/j1/txt/1/f/i/order"
        logger.info(f"🚀 Sending order for R1...")
        logger.info(f"📋 Topic: {topic}")
        logger.info(f"📄 Payload: {json.dumps(order_message, indent=2)}")
        
        result = client.publish(topic, json.dumps(order_message), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Order sent successfully!")
            
            # Wait for responses
            logger.info("⏳ Waiting for responses (10 seconds)...")
            time.sleep(10)
            
        else:
            logger.error(f"❌ Failed to send order: {result.rc}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False
        
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("🔌 Disconnected from MQTT broker")
    
    return True

if __name__ == "__main__":
    print("🎯 Simple Red Workpiece Order - ORBIS APS")
    print("=" * 50)
    print("🔴 Sending order for R1 (WARE_EINGANG)")
    print()
    
    success = send_red_order()
    
    if success:
        print("✅ Order sent successfully!")
    else:
        print("❌ Failed to send order")
