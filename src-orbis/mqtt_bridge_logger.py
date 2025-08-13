#!/usr/bin/env python3
"""
MQTT Bridge Logger für Fischertechnik APS
Orbis Development - Traffic Monitoring und Logging
"""

import json
import time
import uuid
import argparse
from datetime import datetime
from typing import Dict, Any, List
import paho.mqtt.client as mqtt
import logging
import threading
import sqlite3
import os

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MQTTBridgeLogger:
    """MQTT Bridge mit Traffic Logging"""
    
    def __init__(self, 
                 cloud_broker: str, cloud_port: int = 1883,
                 local_broker: str = "localhost", local_port: int = 1883,
                 username: str = None, password: str = None,
                 log_file: str = "mqtt_traffic.log",
                 db_file: str = "mqtt_traffic.db"):
        
        self.cloud_broker = cloud_broker
        self.cloud_port = cloud_port
        self.local_broker = local_broker
        self.local_port = local_port
        self.username = username
        self.password = password
        
        # Logging setup
        self.log_file = log_file
        self.db_file = db_file
        
        # Create clients
        self.cloud_client = mqtt.Client()
        self.local_client = mqtt.Client()
        
        # Setup database
        self._setup_database()
        
        # Setup MQTT clients
        self._setup_mqtt_clients()
        
        # Message counters
        self.message_count = 0
        self.cloud_to_local_count = 0
        self.local_to_cloud_count = 0
        
        logger.info(f"MQTT Bridge Logger initialized")
        logger.info(f"Cloud: {cloud_broker}:{cloud_port}")
        logger.info(f"Local: {local_broker}:{local_port}")
    
    def _setup_database(self):
        """Setup SQLite database for message logging"""
        try:
            self.db_conn = sqlite3.connect(self.db_file)
            self.db_cursor = self.db_conn.cursor()
            
            # Create messages table
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS mqtt_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    qos INTEGER,
                    retained BOOLEAN,
                    message_id TEXT
                )
            ''')
            
            # Create statistics table
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_messages INTEGER,
                    cloud_to_local INTEGER,
                    local_to_cloud INTEGER,
                    unique_topics INTEGER
                )
            ''')
            
            self.db_conn.commit()
            logger.info(f"Database initialized: {self.db_file}")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def _setup_mqtt_clients(self):
        """Setup MQTT clients with callbacks"""
        
        # Cloud client setup
        self.cloud_client.on_connect = self._on_cloud_connect
        self.cloud_client.on_message = self._on_cloud_message
        self.cloud_client.on_disconnect = self._on_cloud_disconnect
        
        # Local client setup
        self.local_client.on_connect = self._on_local_connect
        self.local_client.on_message = self._on_local_message
        self.local_client.on_disconnect = self._on_local_disconnect
        
        # Set authentication if provided
        if self.username and self.password:
            self.cloud_client.username_pw_set(self.username, self.password)
            self.local_client.username_pw_set(self.username, self.password)
    
    def _on_cloud_connect(self, client, userdata, flags, rc):
        """Cloud MQTT connection callback"""
        if rc == 0:
            logger.info(f"Connected to cloud MQTT broker: {self.cloud_broker}")
            # Subscribe to all relevant topics
            self._subscribe_to_cloud_topics()
        else:
            logger.error(f"Failed to connect to cloud broker, return code: {rc}")
    
    def _on_local_connect(self, client, userdata, flags, rc):
        """Local MQTT connection callback"""
        if rc == 0:
            logger.info(f"Connected to local MQTT broker: {self.local_broker}")
            # Subscribe to all relevant topics
            self._subscribe_to_local_topics()
        else:
            logger.error(f"Failed to connect to local broker, return code: {rc}")
    
    def _subscribe_to_cloud_topics(self):
        """Subscribe to cloud topics"""
        topics = [
            "module/v1/ff/#",  # All module topics
            "fischertechnik/#",  # Fischertechnik specific topics
            "aps/#",  # APS specific topics
        ]
        
        for topic in topics:
            self.cloud_client.subscribe(topic)
            logger.info(f"Subscribed to cloud topic: {topic}")
    
    def _subscribe_to_local_topics(self):
        """Subscribe to local topics"""
        topics = [
            "module/v1/ff/#",  # All module topics
            "fischertechnik/#",  # Fischertechnik specific topics
            "aps/#",  # APS specific topics
        ]
        
        for topic in topics:
            self.local_client.subscribe(topic)
            logger.info(f"Subscribed to local topic: {topic}")
    
    def _on_cloud_message(self, client, userdata, msg):
        """Handle messages from cloud"""
        try:
            self._log_message("cloud_to_local", msg)
            self._forward_message(self.local_client, msg)
            self.cloud_to_local_count += 1
            
        except Exception as e:
            logger.error(f"Error handling cloud message: {e}")
    
    def _on_local_message(self, client, userdata, msg):
        """Handle messages from local"""
        try:
            self._log_message("local_to_cloud", msg)
            self._forward_message(self.cloud_client, msg)
            self.local_to_cloud_count += 1
            
        except Exception as e:
            logger.error(f"Error handling local message: {e}")
    
    def _log_message(self, direction: str, msg):
        """Log message to file and database"""
        try:
            # Extract payload
            payload = msg.payload.decode() if msg.payload else ""
            
            # Try to parse as JSON
            try:
                json_payload = json.loads(payload)
                payload_formatted = json.dumps(json_payload, indent=2)
            except:
                payload_formatted = payload
            
            # Log to file
            timestamp = datetime.now().isoformat()
            log_entry = f"\n{'='*80}\n"
            log_entry += f"TIMESTAMP: {timestamp}\n"
            log_entry += f"DIRECTION: {direction}\n"
            log_entry += f"TOPIC: {msg.topic}\n"
            log_entry += f"QOS: {msg.qos}\n"
            log_entry += f"RETAINED: {msg.retain}\n"
            log_entry += f"PAYLOAD:\n{payload_formatted}\n"
            log_entry += f"{'='*80}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Log to database
            self.db_cursor.execute('''
                INSERT INTO mqtt_messages 
                (timestamp, direction, topic, payload, qos, retained, message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                direction,
                msg.topic,
                payload,
                msg.qos,
                bool(msg.retain),
                str(uuid.uuid4())
            ))
            self.db_conn.commit()
            
            # Console output
            logger.info(f"📨 {direction.upper()}: {msg.topic}")
            if len(payload) > 100:
                logger.info(f"   Payload: {payload[:100]}...")
            else:
                logger.info(f"   Payload: {payload}")
            
            self.message_count += 1
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    def _forward_message(self, target_client, msg):
        """Forward message to target client"""
        try:
            target_client.publish(
                msg.topic,
                msg.payload,
                qos=msg.qos,
                retain=msg.retain
            )
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
    
    def _on_cloud_disconnect(self, client, userdata, rc):
        """Cloud MQTT disconnection callback"""
        logger.info("Disconnected from cloud MQTT broker")
    
    def _on_local_disconnect(self, client, userdata, rc):
        """Local MQTT disconnection callback"""
        logger.info("Disconnected from local MQTT broker")
    
    def start(self):
        """Start the MQTT bridge"""
        try:
            # Connect to both brokers
            logger.info("Connecting to MQTT brokers...")
            
            # Connect to cloud broker
            self.cloud_client.connect(self.cloud_broker, self.cloud_port, 60)
            self.cloud_client.loop_start()
            
            # Connect to local broker
            self.local_client.connect(self.local_broker, self.local_port, 60)
            self.local_client.loop_start()
            
            logger.info("MQTT Bridge Logger started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MQTT bridge: {e}")
            raise
    
    def stop(self):
        """Stop the MQTT bridge"""
        try:
            self.cloud_client.loop_stop()
            self.cloud_client.disconnect()
            
            self.local_client.loop_stop()
            self.local_client.disconnect()
            
            self.db_conn.close()
            
            logger.info("MQTT Bridge Logger stopped")
            
        except Exception as e:
            logger.error(f"Error stopping MQTT bridge: {e}")
    
    def get_statistics(self):
        """Get current statistics"""
        try:
            # Get unique topics count
            self.db_cursor.execute('''
                SELECT COUNT(DISTINCT topic) FROM mqtt_messages
            ''')
            unique_topics = self.db_cursor.fetchone()[0]
            
            # Save statistics
            timestamp = datetime.now().isoformat()
            self.db_cursor.execute('''
                INSERT INTO message_stats 
                (timestamp, total_messages, cloud_to_local, local_to_cloud, unique_topics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                timestamp,
                self.message_count,
                self.cloud_to_local_count,
                self.local_to_cloud_count,
                unique_topics
            ))
            self.db_conn.commit()
            
            return {
                "total_messages": self.message_count,
                "cloud_to_local": self.cloud_to_local_count,
                "local_to_cloud": self.local_to_cloud_count,
                "unique_topics": unique_topics,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

def print_statistics(stats):
    """Print statistics in a nice format"""
    print("\n" + "="*60)
    print("📊 MQTT TRAFFIC STATISTICS")
    print("="*60)
    print(f"Total Messages:     {stats.get('total_messages', 0)}")
    print(f"Cloud → Local:      {stats.get('cloud_to_local', 0)}")
    print(f"Local → Cloud:      {stats.get('local_to_cloud', 0)}")
    print(f"Unique Topics:      {stats.get('unique_topics', 0)}")
    print(f"Timestamp:          {stats.get('timestamp', 'N/A')}")
    print("="*60)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MQTT Bridge Logger for Fischertechnik APS")
    parser.add_argument("--cloud-broker", required=True, help="Cloud MQTT broker host/IP")
    parser.add_argument("--cloud-port", type=int, default=1883, help="Cloud MQTT broker port")
    parser.add_argument("--local-broker", default="localhost", help="Local MQTT broker host/IP")
    parser.add_argument("--local-port", type=int, default=1883, help="Local MQTT broker port")
    parser.add_argument("--username", help="MQTT username")
    parser.add_argument("--password", help="MQTT password")
    parser.add_argument("--log-file", default="mqtt_traffic.log", help="Log file path")
    parser.add_argument("--db-file", default="mqtt_traffic.db", help="Database file path")
    parser.add_argument("--stats-interval", type=int, default=60, help="Statistics interval in seconds")
    
    args = parser.parse_args()
    
    try:
        # Create bridge logger
        bridge = MQTTBridgeLogger(
            cloud_broker=args.cloud_broker,
            cloud_port=args.cloud_port,
            local_broker=args.local_broker,
            local_port=args.local_port,
            username=args.username,
            password=args.password,
            log_file=args.log_file,
            db_file=args.db_file
        )
        
        # Start bridge
        bridge.start()
        
        print(f"🚀 MQTT Bridge Logger started")
        print(f"📝 Log file: {args.log_file}")
        print(f"🗄️  Database: {args.db_file}")
        print(f"⏱️  Statistics every {args.stats_interval} seconds")
        print(f"🛑 Press Ctrl+C to stop")
        
        # Statistics thread
        def print_stats():
            while True:
                time.sleep(args.stats_interval)
                stats = bridge.get_statistics()
                print_statistics(stats)
        
        stats_thread = threading.Thread(target=print_stats, daemon=True)
        stats_thread.start()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping MQTT Bridge Logger...")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'bridge' in locals():
            bridge.stop()

if __name__ == "__main__":
    main()
