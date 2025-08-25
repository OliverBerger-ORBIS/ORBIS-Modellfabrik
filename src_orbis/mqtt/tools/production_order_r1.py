#!/usr/bin/env python3
"""
Production Order für R1 - ORBIS APS
Send PRODUCTION order for R1 via CCU
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

def send_production_order_r1():
    """Send PRODUCTION order for R1 via CCU"""
    
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
        client.subscribe("module/v1/ff/#")
        client.subscribe("fts/v1/ff/#")
        
        # Create PRODUCTION order message for R1
        production_order = {
            "orderId": str(uuid.uuid4()),
            "orderType": "PRODUCTION",
            "workpieceColor": "RED",
            "workpieceId": "R1",
            "timestamp": datetime.now().isoformat() + "Z",
            "priority": 1,
            "status": "PENDING"
        }
        
        # Send order via CCU
        topic = "ccu/order/active"
        logger.info(f"🚀 Sending PRODUCTION order for R1 via CCU...")
        logger.info(f"📋 Topic: {topic}")
        logger.info(f"📄 Payload: {json.dumps(production_order, indent=2)}")
        
        result = client.publish(topic, json.dumps(production_order), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ PRODUCTION order sent successfully!")
            
            # Wait for responses
            logger.info("⏳ Waiting for responses (15 seconds)...")
            time.sleep(15)
            
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
    print("🎯 Production Order für R1 - ORBIS APS")
    print("=" * 50)
    print("🔴 Sending PRODUCTION order for R1 via CCU")
    print("📋 Order Type: PRODUCTION (für eingelagerte Werkstücke)")
    print()
    
    success = send_production_order_r1()
    
    if success:
        print("✅ PRODUCTION order sent successfully!")
    else:
        print("❌ Failed to send PRODUCTION order")
