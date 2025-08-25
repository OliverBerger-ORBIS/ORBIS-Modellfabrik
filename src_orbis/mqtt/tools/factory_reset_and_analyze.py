import paho.mqtt.client as mqtt
import json
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def factory_reset_and_analyze():
    """Perform factory reset and analyze current stock/workpieces."""
    client = mqtt.Client()
    client.username_pw_set("default", "default")
    connected = False
    
    # Track reset and stock data
    reset_completed = False
    stock_data = None
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connected
        if rc == 0:
            logger.info("✅ Connected to APS MQTT broker")
            connected = True
        else:
            logger.error(f"❌ Connection failed with code {rc}")
    
    def on_message(client, userdata, msg):
        nonlocal reset_completed, stock_data
        try:
            payload = json.loads(msg.payload.decode())
            
            # Monitor reset completion
            if msg.topic == "ccu/set/reset":
                logger.info(f"🔄 Reset Response: {payload}")
                reset_completed = True
            
            # Monitor stock data
            elif msg.topic == "ccu/state/stock":
                stock_data = payload
                logger.info(f"📦 Stock Data Received: {len(payload.get('stockItems', []))} items")
                
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
        
        # Subscribe to reset and stock topics
        client.subscribe("ccu/set/reset")
        client.subscribe("ccu/state/stock")
        client.subscribe("ccu/pairing/state")
        
        logger.info("📡 Subscribed to reset and stock topics")
        
        # Step 1: Perform Factory Reset
        logger.info("🔄 Performing Factory Reset...")
        reset_command = {
            "timestamp": datetime.now().isoformat() + "Z",
            "withStorage": True
        }
        client.publish("ccu/set/reset", json.dumps(reset_command), qos=1)
        
        # Wait for reset to complete
        logger.info("⏳ Waiting for reset to complete...")
        start_time = time.time()
        while not reset_completed and time.time() - start_time < 30:
            time.sleep(1)
        
        if reset_completed:
            logger.info("✅ Factory Reset completed")
        else:
            logger.warning("⚠️ Reset completion not confirmed, continuing...")
        
        # Step 2: Wait for system to stabilize
        logger.info("⏳ Waiting for system to stabilize...")
        time.sleep(10)
        
        # Step 3: Request current stock data
        logger.info("📦 Requesting current stock data...")
        stock_request = {
            "timestamp": datetime.now().isoformat() + "Z",
            "request": "stock"
        }
        client.publish("ccu/state/request", json.dumps(stock_request), qos=1)
        
        # Wait for stock data
        time.sleep(5)
        
        # Step 4: Analyze stock data
        if stock_data:
            logger.info("🔍 Analyzing current stock...")
            stock_items = stock_data.get('stockItems', [])
            
            logger.info(f"📊 Total stock items: {len(stock_items)}")
            
            # Categorize by type and state
            by_type = {}
            by_state = {}
            available_workpieces = []
            
            for item in stock_items:
                workpiece = item.get('workpiece', {})
                workpiece_type = workpiece.get('type', 'UNKNOWN')
                workpiece_state = workpiece.get('state', 'UNKNOWN')
                location = item.get('location', 'UNKNOWN')
                hbw = item.get('hbw', 'UNKNOWN')
                
                # Count by type
                if workpiece_type not in by_type:
                    by_type[workpiece_type] = 0
                by_type[workpiece_type] += 1
                
                # Count by state
                if workpiece_state not in by_state:
                    by_state[workpiece_state] = 0
                by_state[workpiece_state] += 1
                
                # Track available workpieces
                if workpiece_type and workpiece_type != "":
                    available_workpieces.append({
                        'type': workpiece_type,
                        'state': workpiece_state,
                        'location': location,
                        'hbw': hbw,
                        'id': workpiece.get('id', 'NO_ID')
                    })
            
            # Display analysis
            logger.info("📈 Stock Analysis:")
            logger.info("   By Type:")
            for wtype, count in by_type.items():
                logger.info(f"     {wtype}: {count}")
            
            logger.info("   By State:")
            for state, count in by_state.items():
                logger.info(f"     {state}: {count}")
            
            logger.info("   Available Workpieces:")
            for wp in available_workpieces:
                logger.info(f"     {wp['type']} ({wp['state']}) at {wp['location']} - ID: {wp['id'][:8]}...")
            
            # Recommend next test workpiece
            if available_workpieces:
                # Prefer RAW state workpieces
                raw_workpieces = [wp for wp in available_workpieces if wp['state'] == 'RAW']
                if raw_workpieces:
                    recommended = raw_workpieces[0]
                    logger.info(f"🎯 Recommended for next test: {recommended['type']} at {recommended['location']}")
                else:
                    recommended = available_workpieces[0]
                    logger.info(f"🎯 Recommended for next test: {recommended['type']} at {recommended['location']} (state: {recommended['state']})")
            else:
                logger.warning("⚠️ No workpieces available for testing")
        
        client.loop_stop()
        client.disconnect()
        logger.info("✅ Factory reset and analysis completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = factory_reset_and_analyze()
    if success:
        print("✅ Factory reset and analysis completed")
    else:
        print("❌ Factory reset and analysis failed")
