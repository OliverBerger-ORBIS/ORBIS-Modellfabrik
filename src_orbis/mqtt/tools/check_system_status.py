import paho.mqtt.client as mqtt
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_status():
    """Check the current status of all APS modules to understand system state."""
    client = mqtt.Client()
    client.username_pw_set("default", "default")
    connected = False
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            logger.info("✅ Connected to APS MQTT broker")
            connected = True
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def on_message(client, userdata, msg):
        logger.info(f"📨 {msg.topic}: {msg.payload.decode()}")
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
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
        
        # Subscribe to all module states
        modules = [
            "SVR3QA0022",  # HBW
            "SVR3QA2098",  # DRILL
            "SVR4H76449",  # MILL
            "SVR4H76530",  # AIQS
            "SVR4H73275",  # OVEN
            "5iO4",        # FTS
            "CHRG0"        # Charging Station
        ]
        
        for module in modules:
            client.subscribe(f"module/v1/ff/{module}/state")
            client.subscribe(f"module/v1/ff/{module}/connection")
        
        # Subscribe to system-wide topics
        client.subscribe("ccu/#")
        client.subscribe("fischertechnik/#")
        client.subscribe("/j1/txt/1/f/i/order")
        
        logger.info("📡 Subscribed to all module states")
        logger.info("🔍 Requesting factsheets for all modules...")
        
        # Request factsheets for all modules
        for module in modules:
            factsheet_request = {
                "timestamp": "2025-08-25T12:45:00.000Z",
                "serialNumber": module,
                "actions": [
                    {
                        "actionId": f"status-check-{module}",
                        "actionType": "factsheetRequest",
                        "metadata": {}
                    }
                ]
            }
            topic = f"module/v1/ff/{module}/instantAction"
            result = client.publish(topic, json.dumps(factsheet_request), qos=1)
            logger.info(f"📤 Requested factsheet for {module}")
            time.sleep(0.5)
        
        # Wait for responses
        logger.info("⏳ Waiting 10 seconds for module responses...")
        time.sleep(10)
        
        # Check CCU status
        ccu_status_request = {
            "timestamp": "2025-08-25T12:45:10.000Z",
            "request": "status"
        }
        client.publish("ccu/status/request", json.dumps(ccu_status_request), qos=1)
        logger.info("📤 Requested CCU status")
        
        time.sleep(5)
        
        client.loop_stop()
        client.disconnect()
        logger.info("✅ System status check completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_system_status()
    if success:
        print("✅ System status check completed")
    else:
        print("❌ System status check failed")
