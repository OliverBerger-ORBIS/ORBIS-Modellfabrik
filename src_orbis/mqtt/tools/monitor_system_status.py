import paho.mqtt.client as mqtt
import json
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def monitor_system_status():
    """Monitor system status and wait for modules to become ready."""
    client = mqtt.Client()
    client.username_pw_set("default", "default")
    connected = False
    
    # Track module states
    module_states = {}
    order_states = {}
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            logger.info("✅ Connected to APS MQTT broker")
            connected = True
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            
            # Monitor module pairing states
            if msg.topic == "ccu/pairing/state":
                if "modules" in payload:
                    for module in payload["modules"]:
                        serial = module.get("serialNumber")
                        available = module.get("available")
                        sub_type = module.get("subType")
                        module_states[serial] = {
                            "available": available,
                            "type": sub_type,
                            "last_seen": module.get("lastSeen")
                        }
                        logger.info(f"🏭 {sub_type} ({serial}): {available}")
            
            # Monitor active orders
            elif msg.topic == "ccu/order/active":
                if isinstance(payload, list):
                    order_states.clear()
                    for order in payload:
                        order_id = order.get("orderId")
                        order_type = order.get("orderType")
                        order_state = order.get("state")
                        workpiece_type = order.get("type")
                        order_states[order_id] = {
                            "type": order_type,
                            "state": order_state,
                            "workpiece": workpiece_type
                        }
                        logger.info(f"📋 Order {order_id[:8]}... ({workpiece_type}): {order_state}")
            
            # Monitor TXT order states
            elif msg.topic == "/j1/txt/1/f/i/order":
                logger.info(f"🎮 TXT Order: {payload.get('type')} - {payload.get('state')}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse message: {e}")
    
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
        
        # Subscribe to monitoring topics
        client.subscribe("ccu/pairing/state")
        client.subscribe("ccu/order/active")
        client.subscribe("/j1/txt/1/f/i/order")
        
        logger.info("📡 Monitoring system status...")
        logger.info("⏳ Waiting for system to become ready...")
        
        # Monitor for 60 seconds
        start_time = time.time()
        while time.time() - start_time < 60:
            time.sleep(2)
            
            # Check if HBW and FTS are ready
            hbw_ready = module_states.get("SVR3QA0022", {}).get("available") == "READY"
            fts_ready = module_states.get("5iO4", {}).get("available") == "READY"
            
            # Check if no active orders
            no_orders = len(order_states) == 0
            
            logger.info(f"🔍 Status Check:")
            logger.info(f"   HBW Ready: {hbw_ready}")
            logger.info(f"   FTS Ready: {fts_ready}")
            logger.info(f"   No Active Orders: {no_orders}")
            
            if hbw_ready and fts_ready and no_orders:
                logger.info("✅ System is ready for new orders!")
                break
        
        client.loop_stop()
        client.disconnect()
        logger.info("✅ System monitoring completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = monitor_system_status()
    if success:
        print("✅ System monitoring completed")
    else:
        print("❌ System monitoring failed")
