#!/usr/bin/env python3
"""
Test HBW PICK für R1 - ORBIS APS
Send direct PICK command to HBW for R1
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

def test_hbw_pick_r1():
    """Test direct HBW PICK command for R1"""
    
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
        
        # Subscribe to HBW topics
        client.subscribe("module/v1/ff/SVR3QA0022/#")
        client.subscribe("module/v1/ff/#")
        
        # Create HBW PICK command for R1
        hbw_pick_command = {
            "timestamp": datetime.now().isoformat() + "Z",
            "serialNumber": "SVR3QA0022",
            "actions": [
                {
                    "actionId": str(uuid.uuid4()),
                    "actionType": "PICK",
                    "metadata": {
                        "type": "RED",
                        "workpieceId": "R1",
                        "position": "B1"
                    }
                }
            ]
        }
        
        # Send PICK command to HBW
        topic = "module/v1/ff/SVR3QA0022/instantAction"
        logger.info(f"🚀 Sending HBW PICK command for R1...")
        logger.info(f"📋 Topic: {topic}")
        logger.info(f"📄 Payload: {json.dumps(hbw_pick_command, indent=2)}")
        
        result = client.publish(topic, json.dumps(hbw_pick_command), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ HBW PICK command sent successfully!")
            
            # Wait for responses
            logger.info("⏳ Waiting for HBW responses (10 seconds)...")
            time.sleep(10)
            
        else:
            logger.error(f"❌ Failed to send HBW PICK command: {result.rc}")
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
    print("🎯 Test HBW PICK für R1 - ORBIS APS")
    print("=" * 50)
    print("📦 Testing direct HBW PICK command for R1")
    print("📍 Position: B1 (RED workpiece)")
    print()
    
    success = test_hbw_pick_r1()
    
    if success:
        print("✅ HBW PICK test completed!")
    else:
        print("❌ HBW PICK test failed")
