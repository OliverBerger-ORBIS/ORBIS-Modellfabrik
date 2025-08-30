#!/usr/bin/env python3
"""
APS Persistent MQTT Logger
Orbis Development - Robuster Logger mit Persistierung ohne SQLite-Probleme
"""

import json
import logging
import queue
import signal
import sqlite3
import sys
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class APSPersistentLogger:
    """APS Persistent MQTT Logger mit Thread-sicherer Persistierung"""

    def __init__(
        self,
        host="192.168.0.100",
        port=1883,
        username="default",
        password="default",
        session_label=None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        # Session labeling
        self.session_label = session_label or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Logging Setup - Use absolute paths
        import os

        # Get project root (3 levels up from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../.."))

        # Ensure sessions directory exists
        sessions_dir = os.path.join(project_root, "mqtt-data/sessions")
        os.makedirs(sessions_dir, exist_ok=True)

        self.log_file = os.path.join(sessions_dir, f"aps_persistent_traffic_{self.session_label}.log")
        self.db_file = os.path.join(sessions_dir, f"aps_persistent_traffic_{self.session_label}.db")

        # Thread-safe Queue für Datenbank-Operationen
        self.db_queue = queue.Queue()
        self.running = True

        # MQTT Client
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)

        # Setup callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # Message counter
        self.message_count = 0
        self.start_time = time.time()

        # Initialize database
        self._init_database()

        # Start database worker thread
        self.db_thread = threading.Thread(target=self._db_worker, daemon=True)
        self.db_thread.start()

        logger.info(f"Log file: {self.log_file}")
        logger.info(f"Database: {self.db_file}")
        logger.info(f"Target: {host}:{port}")
        logger.info(f"Credentials: {username} / {password}")

    def _init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_file, check_same_thread=False)
            cursor = conn.cursor()

            # Create messages table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS mqtt_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    payload TEXT,
                    qos INTEGER,
                    retain BOOLEAN,
                    message_type TEXT,
                    module_type TEXT,
                    serial_number TEXT,
                    status TEXT,
                    session_label TEXT,
                    process_label TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index for faster queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp ON mqtt_messages(timestamp)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_topic ON mqtt_messages(topic)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_module_type ON mqtt_messages(module_type)
            """
            )

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def _db_worker(self):
        """Database worker thread - handles all database operations"""
        while self.running:
            try:
                # Get message from queue with timeout
                message_data = self.db_queue.get(timeout=1)

                if message_data is None:  # Shutdown signal
                    break

                # Insert into database
                conn = sqlite3.connect(self.db_file, check_same_thread=False)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO mqtt_messages
                    (timestamp, topic, payload, qos, retain, message_type, module_type, serial_number, status, session_label, process_label)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        message_data["timestamp"],
                        message_data["topic"],
                        message_data["payload"],
                        message_data["qos"],
                        message_data["retain"],
                        message_data["message_type"],
                        message_data["module_type"],
                        message_data["serial_number"],
                        message_data["status"],
                        message_data["session_label"],
                        message_data["process_label"],
                    ),
                )

                conn.commit()
                conn.close()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Database worker error: {e}")

    def _extract_message_info(self, topic, payload):
        """Extract structured information from MQTT message"""
        try:
            data = json.loads(payload) if payload else {}

            # Extract message type
            message_type = "unknown"
            if "type" in data:
                message_type = data["type"]
            elif "messageType" in data:
                message_type = data["messageType"]

            # Extract module type
            module_type = "unknown"
            if "subType" in data:
                module_type = data["subType"]
            elif "moduleType" in data:
                module_type = data["moduleType"]

            # Extract serial number
            serial_number = data.get("serialNumber", "unknown")

            # Extract status
            status = data.get("available", data.get("status", "unknown"))

            return {
                "message_type": message_type,
                "module_type": module_type,
                "serial_number": serial_number,
                "status": status,
            }

        except Exception as e:
            logger.warning(f"Failed to extract message info: {e}")
            return {
                "message_type": "unknown",
                "module_type": "unknown",
                "serial_number": "unknown",
                "status": "unknown",
            }

    def _detect_process_type(self, topic, payload):
        """Detect process type from topic and payload"""
        try:
            # Convert to lowercase for easier matching
            topic_lower = topic.lower()
            payload_lower = payload.lower() if payload else ""

            # Order processing
            if any(
                keyword in topic_lower or keyword in payload_lower
                for keyword in [
                    "order",
                    "bestellung",
                    "blue",
                    "blau",
                    "red",
                    "rot",
                    "yellow",
                    "gelb",
                ]
            ):
                return "order_processing"

            # Wareneingang
            if any(
                keyword in topic_lower or keyword in payload_lower
                for keyword in [
                    "wareneingang",
                    "input",
                    "classify",
                    "klassifizierung",
                    "nfc",
                ]
            ):
                return "wareneingang"

            # Transport
            if any(
                keyword in topic_lower or keyword in payload_lower
                for keyword in ["transport", "fts", "move", "position"]
            ):
                return "transport"

            # Storage
            if any(
                keyword in topic_lower or keyword in payload_lower for keyword in ["storage", "hbw", "store", "lager"]
            ):
                return "storage"

            # Production
            if any(
                keyword in topic_lower or keyword in payload_lower
                for keyword in ["production", "mill", "drill", "oven", "bearbeitung"]
            ):
                return "production"

            # Quality control
            if any(
                keyword in topic_lower or keyword in payload_lower
                for keyword in ["quality", "aiqs", "pruefung", "test"]
            ):
                return "quality_control"

            # System status
            if any(
                keyword in topic_lower or keyword in payload_lower
                for keyword in ["status", "connection", "pairing", "state"]
            ):
                return "system_status"

            return "unknown"

        except Exception as e:
            logger.warning(f"Failed to detect process type: {e}")
            return "unknown"

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            logger.info("✅ Connected to APS MQTT broker")

            # Subscribe to all relevant topics
            topics = [
                "module/v1/ff/#",
                "fischertechnik/#",
                "aps/#",
                "opcua/#",
                "txt4/#",
                "raspberry/#",
                "system/#",
                "status/#",
                "config/#",
                "debug/#",
                "test/#",
                "#",
            ]

            for topic in topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to: {topic}")
        else:
            logger.error(f"❌ Connection failed with return code: {rc}")

    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            timestamp = datetime.now().isoformat()
            payload = msg.payload.decode("utf-8")

            # Debug: Log first few messages
            if self.message_count < 5:
                logger.info(f"📨 Message #{self.message_count + 1}: {msg.topic}")

            # Extract structured information
            info = self._extract_message_info(msg.topic, payload)

            # Log to file
            log_entry = {
                "timestamp": timestamp,
                "topic": msg.topic,
                "payload": payload,
                "qos": msg.qos,
                "retain": msg.retain,
                **info,
            }

            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            # Detect process type from topic/payload
            process_label = self._detect_process_type(msg.topic, payload)

            # Queue for database insertion
            db_data = {
                "timestamp": timestamp,
                "topic": msg.topic,
                "payload": payload,
                "qos": msg.qos,
                "retain": msg.retain,
                "message_type": info["message_type"],
                "module_type": info["module_type"],
                "serial_number": info["serial_number"],
                "status": info["status"],
                "session_label": self.session_label,
                "process_label": process_label,
            }

            self.db_queue.put(db_data)

            # Update counter
            self.message_count += 1

            # Progress update every 100 messages
            if self.message_count % 100 == 0:
                elapsed = time.time() - self.start_time
                rate = self.message_count / elapsed if elapsed > 0 else 0
                logger.info(f"📊 Received {self.message_count} messages ({rate:.1f} msg/s)")

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        logger.info("Disconnected from APS MQTT broker")

    def start(self):
        """Start the logger"""
        try:
            logger.info("🚀 APS Persistent Logger starting...")
            logger.info(f"📝 Log file: {self.log_file}")
            logger.info(f"🗄️  Database: {self.db_file}")
            logger.info("🛑 Press Ctrl+C to stop")

            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()

        except Exception as e:
            logger.error(f"Failed to start logger: {e}")

    def stop(self):
        """Stop the logger"""
        logger.info("🛑 Stopping APS Persistent Logger...")
        self.running = False

        # Signal database worker to stop
        self.db_queue.put(None)

        # Stop MQTT client
        self.client.loop_stop()
        self.client.disconnect()

        # Wait for database worker
        if self.db_thread.is_alive():
            self.db_thread.join(timeout=5)

        logger.info(f"✅ Logger stopped. Total messages: {self.message_count}")
        logger.info(f"📁 Log file: {self.log_file}")
        logger.info(f"🗄️  Database: {self.db_file}")


def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    logger.info("Received shutdown signal")
    if hasattr(signal_handler, "logger"):
        signal_handler.logger.stop()
    sys.exit(0)


def main():
    """Main function"""
    # Create labeled session for Bestellung Blau
    session_label = "Order_cloud_blue_ok"
    logger = APSPersistentLogger(session_label=session_label)
    signal_handler.logger = logger

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        logger.start()

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.stop()


if __name__ == "__main__":
    main()
