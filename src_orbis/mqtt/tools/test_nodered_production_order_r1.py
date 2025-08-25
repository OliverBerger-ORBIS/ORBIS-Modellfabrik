import paho.mqtt.client as mqtt
import json
import uuid
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nodered_production_order_r1():
    """Send a PRODUCTION order for R1 via Node-RED to trigger orchestrated workflow."""
    
    client = mqtt.Client()
    client.username_pw_set("default", "default")
    connected = False
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            logger.info("✅ Connected to MQTT broker")
            connected = True
        else:
            logger.error(f"❌ Connection failed with code: {rc}")
    
    def on_message(client, userdata, msg):
        logger.info(f"📨 Received: {msg.topic}")
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"   Payload: {json.dumps(payload, indent=2)}")
        except:
            logger.info(f"   Payload: {msg.payload.decode()}")
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        logger.info("🔌 Connecting to MQTT broker...")
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
        
        # Subscribe to relevant topics
        client.subscribe("module/v1/ff/NodeRed/#")
        client.subscribe("module/v1/ff/SVR3QA0022/#")  # HBW
        client.subscribe("ccu/#")
        client.subscribe("/j1/txt/1/f/i/order")
        
        logger.info("📡 Subscribed to Node-RED, HBW, CCU and TXT topics")
        time.sleep(1)
        
        # Test 1: Send order to Node-RED directly
        nodered_order = {
            "orderId": str(uuid.uuid4()),
            "orderType": "PRODUCTION",
            "workpieceColor": "RED",
            "workpieceId": "R1",
            "timestamp": datetime.now().isoformat() + "Z",
            "priority": 1,
            "status": "PENDING",
            "targetModule": "HBW",
            "action": "PICK"
        }
        
        topic = "module/v1/ff/NodeRed/order"
        logger.info(f"📤 Test 1: Sending PRODUCTION order to Node-RED at {topic}")
        logger.info(f"   Order: {json.dumps(nodered_order, indent=2)}")
        
        result = client.publish(topic, json.dumps(nodered_order), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Node-RED order sent successfully")
        else:
            logger.error(f"❌ Failed to send Node-RED order: {result.rc}")
        
        time.sleep(5)
        
        # Test 2: Send order to Node-RED via different topic
        topic2 = "nodered/order/input"
        logger.info(f"📤 Test 2: Sending PRODUCTION order to Node-RED at {topic2}")
        
        result2 = client.publish(topic2, json.dumps(nodered_order), qos=1)
        
        if result2.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Node-RED order (test 2) sent successfully")
        else:
            logger.error(f"❌ Failed to send Node-RED order (test 2): {result2.rc}")
        
        time.sleep(5)
        
        # Test 3: Send order to Node-RED via workflow topic
        topic3 = "workflow/order/start"
        logger.info(f"📤 Test 3: Sending PRODUCTION order to workflow at {topic3}")
        
        result3 = client.publish(topic3, json.dumps(nodered_order), qos=1)
        
        if result3.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Workflow order sent successfully")
        else:
            logger.error(f"❌ Failed to send workflow order: {result3.rc}")
        
        # Wait for responses
        logger.info("⏳ Waiting for responses (30 seconds)...")
        time.sleep(30)
        
        logger.info("🔌 Disconnecting...")
        client.loop_stop()
        client.disconnect()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_nodered_production_order_r1()
    if success:
        print("✅ Node-RED PRODUCTION order test completed")
    else:
        print("❌ Node-RED PRODUCTION order test failed")
