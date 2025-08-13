#!/usr/bin/env python3
"""
Comprehensive MQTT Logger für Fischertechnik APS
Orbis Development - Vollständiges Traffic Monitoring
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

class ComprehensiveMQTTLogger:
    """Comprehensive MQTT Logger für alle Broker"""
    
    def __init__(self, 
                 log_file: str = "comprehensive_mqtt_traffic.log",
                 db_file: str = "comprehensive_mqtt_traffic.db"):
        
        self.log_file = log_file
        self.db_file = db_file
        
        # MQTT Clients für verschiedene Broker
        self.clients = {}
        self.message_count = 0
        
        # Setup database
        self._setup_database()
        
        # Define all known MQTT brokers
        self.brokers = {
            "raspberry_pi": {
                "host": "192.168.0.100",
                "port": 1883,
                "description": "Raspberry Pi Haupt-MQTT-Broker"
            },
            "secondary": {
                "host": "192.168.2.189", 
                "port": 1883,
                "description": "Sekundärer MQTT-Broker"
            },
            "docker": {
                "host": "host.docker.internal",
                "port": 1883,
                "description": "Docker MQTT-Broker"
            },
            "container": {
                "host": "mqtt-broker",
                "port": 1883,
                "description": "Container MQTT-Broker"
            }
        }
        
        logger.info(f"Comprehensive MQTT Logger initialized")
        logger.info(f"Monitoring {len(self.brokers)} MQTT brokers")
    
    def _setup_database(self):
        """Setup SQLite database for comprehensive message logging"""
        try:
            self.db_conn = sqlite3.connect(self.db_file)
            self.db_cursor = self.db_conn.cursor()
            
            # Create comprehensive messages table
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS comprehensive_mqtt_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    broker_name TEXT NOT NULL,
                    broker_host TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    qos INTEGER,
                    retained BOOLEAN,
                    message_id TEXT,
                    source_type TEXT
                )
            ''')
            
            # Create broker statistics table
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS broker_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    broker_name TEXT NOT NULL,
                    message_count INTEGER,
                    unique_topics INTEGER,
                    connection_status TEXT
                )
            ''')
            
            # Create topic analysis table
            self.db_cursor.execute('''
                CREATE TABLE IF NOT EXISTS topic_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    broker_name TEXT NOT NULL,
                    message_count INTEGER,
                    last_seen TEXT
                )
            ''')
            
            self.db_conn.commit()
            logger.info(f"Database initialized: {self.db_file}")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def _create_mqtt_client(self, broker_name: str, broker_config: Dict[str, Any]):
        """Create MQTT client for a specific broker"""
        try:
            client = mqtt.Client()
            
            # Setup callbacks
            client.on_connect = lambda client, userdata, flags, rc: self._on_connect(broker_name, client, userdata, flags, rc)
            client.on_message = lambda client, userdata, msg: self._on_message(broker_name, client, userdata, msg)
            client.on_disconnect = lambda client, userdata, rc: self._on_disconnect(broker_name, client, userdata, rc)
            
            # Store client
            self.clients[broker_name] = {
                "client": client,
                "config": broker_config,
                "connected": False,
                "message_count": 0
            }
            
            logger.info(f"Created MQTT client for {broker_name}: {broker_config['host']}:{broker_config['port']}")
            
        except Exception as e:
            logger.error(f"Failed to create MQTT client for {broker_name}: {e}")
    
    def _on_connect(self, broker_name: str, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info(f"✅ Connected to {broker_name} MQTT broker")
            self.clients[broker_name]["connected"] = True
            
            # Subscribe to all topics
            self._subscribe_to_all_topics(broker_name, client)
        else:
            logger.error(f"❌ Failed to connect to {broker_name} broker, return code: {rc}")
    
    def _on_disconnect(self, broker_name: str, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.info(f"Disconnected from {broker_name} MQTT broker")
        self.clients[broker_name]["connected"] = False
    
    def _subscribe_to_all_topics(self, broker_name: str, client):
        """Subscribe to all relevant topics"""
        topics = [
            "module/v1/ff/#",        # Fischertechnik Module
            "fischertechnik/#",      # Fischertechnik spezifisch
            "aps/#",                 # APS spezifisch
            "opcua/#",               # OPC-UA Topics
            "txt4/#",                # TXT4.0 Topics
            "raspberry/#",           # Raspberry Pi Topics
            "docker/#",              # Docker Topics
            "system/#",              # System Topics
            "status/#",              # Status Topics
            "config/#",              # Configuration Topics
            "debug/#",               # Debug Topics
            "test/#",                # Test Topics
            "#"                      # ALL Topics (Wildcard)
        ]
        
        for topic in topics:
            client.subscribe(topic)
            logger.info(f"Subscribed to {broker_name}: {topic}")
    
    def _on_message(self, broker_name: str, client, userdata, msg):
        """Handle MQTT messages from any broker"""
        try:
            self._log_comprehensive_message(broker_name, msg)
            self.clients[broker_name]["message_count"] += 1
            self.message_count += 1
            
        except Exception as e:
            logger.error(f"Error handling message from {broker_name}: {e}")
    
    def _log_comprehensive_message(self, broker_name: str, msg):
        """Log message with comprehensive information"""
        try:
            # Extract payload
            payload = msg.payload.decode() if msg.payload else ""
            
            # Try to parse as JSON
            try:
                json_payload = json.loads(payload)
                payload_formatted = json.dumps(json_payload, indent=2)
            except:
                payload_formatted = payload
            
            # Determine source type
            source_type = self._determine_source_type(msg.topic, payload)
            
            # Log to file
            timestamp = datetime.now().isoformat()
            log_entry = f"\n{'='*100}\n"
            log_entry += f"TIMESTAMP: {timestamp}\n"
            log_entry += f"BROKER: {broker_name}\n"
            log_entry += f"BROKER_HOST: {self.brokers[broker_name]['host']}:{self.brokers[broker_name]['port']}\n"
            log_entry += f"TOPIC: {msg.topic}\n"
            log_entry += f"SOURCE_TYPE: {source_type}\n"
            log_entry += f"QOS: {msg.qos}\n"
            log_entry += f"RETAINED: {msg.retain}\n"
            log_entry += f"PAYLOAD:\n{payload_formatted}\n"
            log_entry += f"{'='*100}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Log to database
            self.db_cursor.execute('''
                INSERT INTO comprehensive_mqtt_messages 
                (timestamp, broker_name, broker_host, topic, payload, qos, retained, message_id, source_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                broker_name,
                f"{self.brokers[broker_name]['host']}:{self.brokers[broker_name]['port']}",
                msg.topic,
                payload,
                msg.qos,
                bool(msg.retain),
                str(uuid.uuid4()),
                source_type
            ))
            self.db_conn.commit()
            
            # Console output
            logger.info(f"📨 {broker_name.upper()}: {msg.topic} ({source_type})")
            if len(payload) > 100:
                logger.info(f"   Payload: {payload[:100]}...")
            else:
                logger.info(f"   Payload: {payload}")
            
        except Exception as e:
            logger.error(f"Error logging comprehensive message: {e}")
    
    def _determine_source_type(self, topic: str, payload: str) -> str:
        """Determine the source type based on topic and payload"""
        topic_lower = topic.lower()
        payload_lower = payload.lower()
        
        if "module/v1/ff" in topic:
            return "FISCHERTECHNIK_MODULE"
        elif "fischertechnik" in topic_lower:
            return "FISCHERTECHNIK_SYSTEM"
        elif "opcua" in topic_lower:
            return "OPC_UA"
        elif "txt4" in topic_lower:
            return "TXT4_CONTROLLER"
        elif "raspberry" in topic_lower:
            return "RASPBERRY_PI"
        elif "docker" in topic_lower:
            return "DOCKER"
        elif "system" in topic_lower:
            return "SYSTEM"
        elif "status" in topic_lower:
            return "STATUS"
        elif "config" in topic_lower:
            return "CONFIGURATION"
        elif "debug" in topic_lower:
            return "DEBUG"
        elif "test" in topic_lower:
            return "TEST"
        elif "error" in payload_lower or "fail" in payload_lower:
            return "ERROR"
        else:
            return "UNKNOWN"
    
    def start(self):
        """Start comprehensive MQTT logging"""
        try:
            logger.info("Starting Comprehensive MQTT Logger...")
            
            # Create and connect to all brokers
            for broker_name, broker_config in self.brokers.items():
                self._create_mqtt_client(broker_name, broker_config)
                
                try:
                    client = self.clients[broker_name]["client"]
                    client.connect(broker_config["host"], broker_config["port"], 60)
                    client.loop_start()
                    
                    logger.info(f"Connecting to {broker_name}: {broker_config['host']}:{broker_config['port']}")
                    
                except Exception as e:
                    logger.warning(f"Could not connect to {broker_name}: {e}")
            
            logger.info("Comprehensive MQTT Logger started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start comprehensive MQTT logger: {e}")
            raise
    
    def stop(self):
        """Stop comprehensive MQTT logging"""
        try:
            for broker_name, client_info in self.clients.items():
                client = client_info["client"]
                client.loop_stop()
                client.disconnect()
            
            self.db_conn.close()
            logger.info("Comprehensive MQTT Logger stopped")
            
        except Exception as e:
            logger.error(f"Error stopping comprehensive MQTT logger: {e}")
    
    def get_statistics(self):
        """Get comprehensive statistics"""
        try:
            stats = {
                "total_messages": self.message_count,
                "brokers": {},
                "timestamp": datetime.now().isoformat()
            }
            
            for broker_name, client_info in self.clients.items():
                stats["brokers"][broker_name] = {
                    "connected": client_info["connected"],
                    "message_count": client_info["message_count"],
                    "host": self.brokers[broker_name]["host"],
                    "port": self.brokers[broker_name]["port"]
                }
            
            # Get unique topics count
            self.db_cursor.execute('''
                SELECT COUNT(DISTINCT topic) FROM comprehensive_mqtt_messages
            ''')
            stats["unique_topics"] = self.db_cursor.fetchone()[0]
            
            # Save statistics
            self.db_cursor.execute('''
                INSERT INTO broker_stats 
                (timestamp, broker_name, message_count, unique_topics, connection_status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                stats["timestamp"],
                "comprehensive",
                stats["total_messages"],
                stats["unique_topics"],
                "active"
            ))
            self.db_conn.commit()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}

def print_comprehensive_statistics(stats):
    """Print comprehensive statistics"""
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE MQTT TRAFFIC STATISTICS")
    print("="*80)
    print(f"Total Messages:     {stats.get('total_messages', 0)}")
    print(f"Unique Topics:      {stats.get('unique_topics', 0)}")
    print(f"Timestamp:          {stats.get('timestamp', 'N/A')}")
    
    print(f"\n🔌 BROKER STATUS:")
    for broker_name, broker_stats in stats.get("brokers", {}).items():
        status = "✅ CONNECTED" if broker_stats["connected"] else "❌ DISCONNECTED"
        print(f"  {broker_name}: {status} ({broker_stats['message_count']} messages)")
        print(f"    Host: {broker_stats['host']}:{broker_stats['port']}")
    
    print("="*80)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Comprehensive MQTT Logger for Fischertechnik APS")
    parser.add_argument("--log-file", default="comprehensive_mqtt_traffic.log", help="Log file path")
    parser.add_argument("--db-file", default="comprehensive_mqtt_traffic.db", help="Database file path")
    parser.add_argument("--stats-interval", type=int, default=60, help="Statistics interval in seconds")
    
    args = parser.parse_args()
    
    try:
        # Create comprehensive logger
        logger = ComprehensiveMQTTLogger(
            log_file=args.log_file,
            db_file=args.db_file
        )
        
        # Start logger
        logger.start()
        
        print(f"🚀 Comprehensive MQTT Logger started")
        print(f"📝 Log file: {args.log_file}")
        print(f"🗄️  Database: {args.db_file}")
        print(f"⏱️  Statistics every {args.stats_interval} seconds")
        print(f"🛑 Press Ctrl+C to stop")
        
        # Statistics thread
        def print_stats():
            while True:
                time.sleep(args.stats_interval)
                stats = logger.get_statistics()
                print_comprehensive_statistics(stats)
        
        stats_thread = threading.Thread(target=print_stats, daemon=True)
        stats_thread.start()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping Comprehensive MQTT Logger...")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'logger' in locals():
            logger.stop()

if __name__ == "__main__":
    main()
