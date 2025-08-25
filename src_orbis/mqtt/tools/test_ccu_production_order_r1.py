import paho.mqtt.client as mqtt
import json
import uuid
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ccu_production_order_r1():
    """Send a PRODUCTION order for R1 via CCU to trigger HBW PICK."""
    
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
        client.subscribe("ccu/#")
        client.subscribe("module/v1/ff/SVR3QA0022/#")  # HBW
        client.subscribe("/j1/txt/1/f/i/order")
        
        logger.info("📡 Subscribed to CCU and HBW topics")
        time.sleep(1)
        
        # Create PRODUCTION order for R1
        production_order = {
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
        
        topic = "ccu/order/active"
        logger.info(f"📤 Sending PRODUCTION order for R1 to {topic}")
        logger.info(f"   Order: {json.dumps(production_order, indent=2)}")
        
        result = client.publish(topic, json.dumps(production_order), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ PRODUCTION order sent successfully")
        else:
            logger.error(f"❌ Failed to send order: {result.rc}")
            return False
        
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
    success = test_ccu_production_order_r1()
    if success:
        print("✅ CCU PRODUCTION order test completed")
    else:
        print("❌ CCU PRODUCTION order test failed")
