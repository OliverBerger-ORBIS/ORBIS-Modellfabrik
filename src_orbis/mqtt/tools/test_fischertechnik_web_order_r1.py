import paho.mqtt.client as mqtt
import json
import uuid
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fischertechnik_web_order_r1():
    """Send orders in the exact same format as Fischertechnik web interface."""
    
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
        client.subscribe("module/v1/ff/SVR3QA0022/#")  # HBW
        client.subscribe("ccu/#")
        client.subscribe("/j1/txt/1/f/i/order")
        client.subscribe("fischertechnik/#")
        
        logger.info("📡 Subscribed to HBW, CCU, TXT and Fischertechnik topics")
        time.sleep(1)
        
        # Test 1: Send WARE_EINGANG order (like web interface)
        ware_eingang_order = {
            "ts": datetime.now().isoformat() + "Z",
            "state": "WAITING_FOR_ORDER",
            "orderType": "WARE_EINGANG",
            "workpieceColor": "RED",
            "workpieceId": "R1",
            "orderId": str(uuid.uuid4())
        }
        
        topic = "/j1/txt/1/f/i/order"
        logger.info(f"📤 Test 1: Sending WARE_EINGANG order to {topic}")
        logger.info(f"   Order: {json.dumps(ware_eingang_order, indent=2)}")
        
        result = client.publish(topic, json.dumps(ware_eingang_order), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ WARE_EINGANG order sent successfully")
        else:
            logger.error(f"❌ Failed to send WARE_EINGANG order: {result.rc}")
        
        time.sleep(10)
        
        # Test 2: Send PRODUCTION order (like web interface)
        production_order = {
            "ts": datetime.now().isoformat() + "Z",
            "state": "WAITING_FOR_ORDER",
            "orderType": "PRODUCTION",
            "workpieceColor": "RED",
            "workpieceId": "R1",
            "orderId": str(uuid.uuid4())
        }
        
        logger.info(f"📤 Test 2: Sending PRODUCTION order to {topic}")
        logger.info(f"   Order: {json.dumps(production_order, indent=2)}")
        
        result2 = client.publish(topic, json.dumps(production_order), qos=1)
        
        if result2.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ PRODUCTION order sent successfully")
        else:
            logger.error(f"❌ Failed to send PRODUCTION order: {result2.rc}")
        
        time.sleep(10)
        
        # Test 3: Send direct fischertechnik order
        fischertech_order = {
            "timestamp": datetime.now().isoformat() + "Z",
            "orderType": "PRODUCTION",
            "workpieceColor": "RED",
            "workpieceId": "R1",
            "orderId": str(uuid.uuid4()),
            "source": "fischertechnik_web"
        }
        
        topic2 = "fischertechnik/order/start"
        logger.info(f"📤 Test 3: Sending Fischertechnik order to {topic2}")
        logger.info(f"   Order: {json.dumps(fischertech_order, indent=2)}")
        
        result3 = client.publish(topic2, json.dumps(fischertech_order), qos=1)
        
        if result3.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("✅ Fischertechnik order sent successfully")
        else:
            logger.error(f"❌ Failed to send Fischertechnik order: {result3.rc}")
        
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
    success = test_fischertechnik_web_order_r1()
    if success:
        print("✅ Fischertechnik Web Order test completed")
    else:
        print("❌ Fischertechnik Web Order test failed")
