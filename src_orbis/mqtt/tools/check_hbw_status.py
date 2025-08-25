#!/usr/bin/env python3
"""
Check HBW Status - ORBIS APS
Check HBW status after PICK command
"""

import paho.mqtt.client as mqtt
import json
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_hbw_status():
    """Check HBW status"""
    
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
            if "SVR3QA0022" in msg.topic:  # HBW
                logger.info(f"📦 HBW {msg.topic}: {json.dumps(payload, indent=2)}")
        except:
            pass
    
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
        
        # Request HBW factsheet to get current status
        factsheet_request = {
            "timestamp": "2025-08-25T12:15:00.000Z",
            "serialNumber": "SVR3QA0022",
            "actions": [
                {
                    "actionId": "check-status",
                    "actionType": "factsheetRequest",
                    "metadata": {}
                }
            ]
        }
        
        # Send factsheet request
        topic = "module/v1/ff/SVR3QA0022/instantAction"
        logger.info(f"🔍 Requesting HBW status...")
        
        result = client.publish(topic, json.dumps(factsheet_request), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Status request sent!")
            
            # Wait for responses
            logger.info("⏳ Waiting for HBW status (5 seconds)...")
            time.sleep(5)
            
        else:
            logger.error(f"❌ Failed to send status request: {result.rc}")
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
    print("🔍 Check HBW Status - ORBIS APS")
    print("=" * 50)
    print("📦 Checking HBW status after PICK command")
    print()
    
    success = check_hbw_status()
    
    if success:
        print("✅ HBW status check completed!")
    else:
        print("❌ HBW status check failed")
