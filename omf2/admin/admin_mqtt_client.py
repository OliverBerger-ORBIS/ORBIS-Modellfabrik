#!/usr/bin/env python3
"""
Admin MQTT Client - Thread-sicherer Singleton für Admin MQTT-Kommunikation
"""

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    import paho.mqtt.client as mqtt

    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None

from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


class AdminMqttClient:
    """
    Thread-sicherer Singleton für Admin MQTT-Kommunikation

    Kapselt alle Verbindungs- und Kommunikationsdetails für Admin.
    Nutzt Registry v2 für Topic-Konfiguration.
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if AdminMqttClient._initialized:
            return

        self.registry_manager = get_registry_manager()
        # Get client_id from registry as prefix
        self.base_client_id = self._get_base_client_id()
        self.client_id = self.base_client_id  # Will be updated based on environment

        # Thread-sichere Locks
        self._client_lock = threading.Lock()
        self._buffer_lock = threading.Lock()

        # MQTT-Client und Konfiguration
        self.client = None
        self.connected = False
        self.current_environment = None
        self.config = self._load_config()

        # Topic-Buffer für Per-Topic-Buffer Pattern (thread-safe) - wie in omf/
        from collections import defaultdict, deque

        self.topic_buffers = defaultdict(lambda: deque(maxlen=1000))

        # Gateway für Message-Routing (Architecture: MQTT → Gateway → Manager → UI)
        self._gateway = None

        # Published/Subscribed Topics aus Registry
        self.published_topics = self._get_published_topics()
        self.subscribed_topics = self._get_subscribed_topics()

        AdminMqttClient._initialized = True
        logger.info("🏗️ Admin MQTT Client initialized")

    def _get_base_client_id(self) -> str:
        """Get base client_id from registry"""
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            admin_client = mqtt_clients.get("mqtt_clients", {}).get("admin_mqtt_client", {})
            return admin_client.get("client_id", "omf_admin")
        except Exception as e:
            logger.error(f"❌ Failed to load base client_id from registry: {e}")
            return "omf_admin"

    def _load_config(self, environment: str = "mock") -> Dict[str, Any]:
        """Lädt MQTT-Konfiguration aus mqtt_settings.yml für spezifisches Environment"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "mqtt_settings.yml"
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    # Environment-spezifische Konfiguration laden
                    env_config = config.get("environments", {}).get(environment, {})
                    # Basis-Konfiguration mit Environment-spezifischen Werten mergen
                    base_config = config.get("mqtt", {})
                    merged_config = {**base_config, **env_config.get("mqtt", {})}
                    return merged_config
            else:
                logger.warning(f"⚠️ Config file not found: {config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback-Konfiguration"""
        return {
            "host": "localhost",
            "port": 1883,
            "username": "",
            "password": "",
            "keepalive": 60,
            "clean_session": True,
            "client_id_postfix": "_mock",
        }

    def _get_published_topics(self) -> List[str]:
        """Lädt Published Topics aus Registry"""
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            admin_client = mqtt_clients.get("mqtt_clients", {}).get("admin_mqtt_client", {})
            return admin_client.get("published_topics", [])
        except Exception as e:
            logger.error(f"❌ Failed to load admin published topics: {e}")
            return []

    def _get_subscribed_topics(self) -> List[str]:
        """Lädt Subscribed Topics aus Registry"""
        try:
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            # TODO: Registry-Struktur Problem - Admin Client sucht nach 'mqtt_clients.admin_mqtt_client'
            # aber Registry hat direkte Keys: 'admin_mqtt_client'. Gleiche Struktur für alle Clients prüfen!
            admin_client = mqtt_clients.get("mqtt_clients", {}).get("admin_mqtt_client", {})
            return admin_client.get("subscribed_topics", [])
        except Exception as e:
            logger.error(f"❌ Failed to load admin subscribed topics: {e}")
            return []

    def connect(self, environment: str = "mock") -> bool:
        """
        Verbindung zum MQTT-Broker herstellen - CLEAN Connect/Disconnect-Handling

        Args:
            environment: Environment ('live', 'replay', 'mock')

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        with self._client_lock:
            try:
                logger.info(f"🔌 Admin MQTT Client connecting to environment: {environment}")

                if not MQTT_AVAILABLE:
                    logger.warning("⚠️ paho-mqtt not available, using mock mode")
                    self.connected = True
                    self._current_environment = environment
                    return True

                # Config für Environment laden
                mqtt_config = self._load_config(environment)

                # Mock-Mode: Keine echte Verbindung
                if environment == "mock":
                    self.client_id = f"{self.base_client_id}_mock"
                    self.connected = True
                    self._current_environment = environment
                    logger.info(f"🧪 Mock mode active - no real MQTT connection (Client ID: {self.client_id})")
                    return True

                # Check if already connected with same environment
                if (
                    self.connected
                    and hasattr(self, "_current_environment")
                    and self._current_environment == environment
                ):
                    logger.debug(f"♻️ Already connected to {environment}")
                    return True

                # CLEAN DISCONNECT: Vor jedem neuen Connect sauber trennen
                if self.connected:
                    logger.info(f"🔄 Clean disconnect before reconnecting to {environment}")
                    self.disconnect()
                    # Warten bis Disconnect vollständig abgeschlossen
                    import time

                    for _ in range(50):  # Max 5 Sekunden warten
                        if not self.connected:
                            break
                        time.sleep(0.1)

                # MQTT-Client initialisieren - NEUE Instanz mit neuer Config
                client_id_postfix = mqtt_config.get("client_id_postfix", f"_{environment}")
                client_id = f"{self.base_client_id}{client_id_postfix}"
                self.client_id = client_id
                self.client = mqtt.Client(client_id=client_id)
                self.client.on_connect = self._on_connect
                self.client.on_message = self._on_message
                self.client.on_disconnect = self._on_disconnect

                # Authentication
                if mqtt_config.get("username"):
                    self.client.username_pw_set(mqtt_config["username"], mqtt_config.get("password", ""))

                # Reconnect-Delay setzen
                self.client.reconnect_delay_set(min_delay=1, max_delay=30)

                # Verbindung herstellen
                host = mqtt_config.get("host", "localhost")
                port = mqtt_config.get("port", 1883)
                keepalive = mqtt_config.get("keepalive", 60)

                logger.info(f"🔗 Connecting to {host}:{port} with client_id: {self.client_id}")
                self.client.loop_start()
                self.client.connect_async(host, port, keepalive)

                # Warten auf Verbindung
                import time

                for _ in range(50):  # Max 5 Sekunden warten
                    if self.connected:
                        break
                    time.sleep(0.1)

                self._current_environment = environment
                # Store connection parameters for get_connection_info()
                self._host = host
                self._port = port
                logger.info(f"✅ Admin MQTT Client connected to {host}:{port} (Environment: {environment})")
                return True

            except Exception as e:
                logger.error(f"❌ Admin MQTT Client connection failed for {environment}: {e}")
                self.connected = False
                return False

    def disconnect(self):
        """Verbindung zum MQTT-Broker trennen - CLEAN Disconnect mit loop_stop"""
        with self._client_lock:
            try:
                if self.client and self.connected:
                    logger.info(
                        f"🔌 Clean disconnecting Admin MQTT Client (Environment: {getattr(self, '_current_environment', 'unknown')})"
                    )
                    # CLEAN DISCONNECT: Erst loop_stop, dann disconnect
                    self.client.loop_stop()
                    self.client.disconnect()
                    self.connected = False
                    self.client = None
                    logger.info("🔌 Admin MQTT Client cleanly disconnected")
                else:
                    logger.debug("🔌 Admin MQTT Client was not connected")
                    self.connected = False

            except Exception as e:
                logger.error(f"❌ Admin MQTT Client disconnect failed: {e}")
                # Force disconnect state
                self.connected = False
                self.client = None

    def publish_message(self, topic: str, message: Dict[str, Any], qos: int = None, retain: bool = None) -> bool:
        """
        Message auf Topic publizieren (thread-safe)

        Args:
            topic: MQTT Topic
            message: Message-Dict
            qos: QoS-Level (wird aus Registry geladen wenn None)
            retain: Retain-Flag (wird aus Registry geladen wenn None)

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        with self._client_lock:
            try:
                # QoS/Retain aus Registry laden wenn nicht angegeben
                if qos is None or retain is None:
                    try:
                        topic_config = self.registry_manager.get_topic_config(topic)
                        topic_qos = topic_config.get("qos", 0) if topic_config else 0
                        topic_retain = topic_config.get("retain", False) if topic_config else False
                        qos = qos if qos is not None else topic_qos
                        retain = retain if retain is not None else topic_retain
                    except Exception:
                        # Fallback für unbekannte Topics
                        qos = qos if qos is not None else 1
                        retain = retain if retain is not None else False

                # Mock-Modus
                if not self.connected or not self.client:
                    logger.info(f"📤 Mock publish to {topic}: {message}")
                    # Auch im Mock-Modus in Buffer hinzufügen
                    self._add_sent_message_to_buffer(topic, message, qos, retain)
                    return True

                # JSON-Payload erstellen
                payload = json.dumps(message, ensure_ascii=False)

                # MQTT-Publish
                result = self.client.publish(topic, payload, qos=qos, retain=retain)

                if result.rc == 0:
                    logger.info(f"📤 Published to {topic}: {message}")

                    # Gesendete Message auch in Buffer hinzufügen (für Message Monitor)
                    self._add_sent_message_to_buffer(topic, message, qos, retain)

                    return True
                else:
                    logger.error(f"❌ Publish failed for topic {topic}: {result.rc}")
                    return False

            except Exception as e:
                logger.error(f"❌ Publish failed for topic {topic}: {e}")
                return False

    def _add_sent_message_to_buffer(self, topic: str, message: Dict[str, Any], qos: int, retain: bool):
        """Gesendete Message in Buffer hinzufügen (für Message Monitor)"""
        try:
            import time

            message_data = {
                "payload": message,
                "raw_payload": json.dumps(message, ensure_ascii=False),
                "timestamp": time.time(),
                "qos": qos,
                "retain": retain,
                "message_type": "sent",  # Mark as sent message
            }

            with self._buffer_lock:
                self.topic_buffers[topic].append(message_data)

        except Exception as e:
            logger.error(f"❌ Failed to add sent message to buffer: {e}")

    def subscribe_to_all(self) -> bool:
        """
        Alle Topics subscriben (Admin subscribiert alles mit '#')

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        with self._client_lock:
            try:
                if not self.connected or not self.client:
                    logger.info("📥 Mock subscribe to all topics")
                    return True

                # TODO: Admin Client Problem - Admin verwendet Wildcard "#" statt Registry-Liste
                # Sollte subscribed_topics aus Registry laden und zu diesen subscriben!
                # Wildcard-Subscription für Admin
                result = self.client.subscribe("#", qos=1)

                if result[0] == 0:
                    logger.info("📥 Subscribed to all topics (#)")
                    return True
                else:
                    logger.error(f"❌ Subscribe to all topics failed: {result[0]}")
                    return False

            except Exception as e:
                logger.error(f"❌ Subscribe to all topics failed: {e}")
                return False

    def reconnect_environment(self, new_environment: str) -> bool:
        """
        Reconnect to new environment - clean disconnect and reconnect

        Args:
            new_environment: New environment ('live', 'replay', 'mock')

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        logger.info(f"🔄 Admin MQTT Client environment switch: {self.current_environment} -> {new_environment}")

        # Disconnect from current environment
        if self.connected:
            self.disconnect()
            # Reset subscription flag for new environment
            if hasattr(self, "_subscribed"):
                delattr(self, "_subscribed")

        # Reload configuration to pick up any changes
        self.config = self._load_config()

        # Connect to new environment
        success = self.connect(new_environment)

        if success:
            logger.info(f"✅ Admin MQTT Client reconnected to {new_environment}")
        else:
            logger.error(f"❌ Admin MQTT Client failed to reconnect to {new_environment}")

        return success

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get current connection information for UI display

        Returns:
            Connection info dict
        """
        try:
            current_env = getattr(self, "_current_environment", "mock")

            # Use actual connection parameters if connected, otherwise fallback to config
            if self.connected and hasattr(self, "client") and self.client:
                # Get actual connection parameters from MQTT client
                host = getattr(self.client, "_host", None) or getattr(self, "_host", None)
                port = getattr(self.client, "_port", None) or getattr(self, "_port", None)
            else:
                # Fallback to config if not connected
                env_config = self.config.get("environments", {}).get(current_env, {})
                mqtt_config = {**self.config.get("mqtt", {}), **env_config.get("mqtt", {})}
                host = mqtt_config.get("host", "unknown")
                port = mqtt_config.get("port", 1883)

            return {
                "connected": self.connected,
                "environment": current_env,
                "client_id": self.client_id,
                "host": host or "unknown",
                "port": port or 1883,
                "mock_mode": current_env == "mock" or not self.connected,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get connection info: {e}")
            return {
                "connected": False,
                "environment": "unknown",
                "client_id": "unknown",
                "host": "unknown",
                "port": 1883,
                "mock_mode": True,
            }
        """
        Broker-Key für Subscription-Tracking (wie im alten Dashboard)

        Returns:
            Broker-Key String (host:port)
        """
        try:
            if hasattr(self, "config") and self.config:
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 1883)
                return f"{host}:{port}"
            else:
                return "localhost:1883"
        except Exception as e:
            logger.error(f"❌ Failed to get broker key: {e}")
            return "unknown:unknown"

    def get_buffer(self, topic: str) -> Optional[Dict]:
        """
        Letzte Message aus Topic-Buffer abrufen (thread-safe)

        Args:
            topic: MQTT Topic

        Returns:
            Letzte Message oder None
        """
        try:
            with self._buffer_lock:
                buffer = self.topic_buffers.get(topic)
                if buffer and len(buffer) > 0:
                    return buffer[-1]  # Letzte Message aus deque
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get buffer for topic {topic}: {e}")
            return None

    def get_all_buffers(self) -> Dict[str, Dict]:
        """
        Alle Topic-Buffer abrufen (thread-safe)

        Returns:
            Dict mit allen Topic-Buffern
        """
        try:
            with self._buffer_lock:
                return self.topic_buffers.copy()
        except Exception as e:
            logger.error(f"❌ Failed to get all buffers: {e}")
            return {}

    def clear_buffers(self) -> bool:
        """
        Alle Topic-Buffer löschen (thread-safe)

        Returns:
            True wenn erfolgreich
        """
        try:
            with self._buffer_lock:
                self.topic_buffers.clear()
                logger.info("🗑️ All topic buffers cleared")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to clear buffers: {e}")
            return False

    def get_system_overview(self) -> Dict[str, Any]:
        """
        System Overview abrufen (thread-safe)

        Returns:
            System Overview Dict
        """
        try:
            with self._buffer_lock:
                overview = {
                    "total_topics": len(self.topic_buffers),
                    "active_topics": [topic for topic, buffer in self.topic_buffers.items() if len(buffer) > 0],
                    "last_activity": max(
                        [
                            max([msg.get("timestamp", "") for msg in buffer], default="")
                            for buffer in self.topic_buffers.values()
                            if len(buffer) > 0
                        ],
                        default="",
                    ),
                    "mqtt_connected": self.connected,
                    "client_id": self.client_id,
                }

            # Only log system overview on significant changes or first call
            if not hasattr(self, "_last_overview") or self._last_overview != overview:
                logger.info(f"📊 System overview: {overview}")
                self._last_overview = overview
            return overview

        except Exception as e:
            logger.error(f"❌ Failed to get system overview: {e}")
            return {}

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback - Subscribe NUR hier!"""
        if rc == 0:
            self.connected = True
            logger.info("✅ Admin MQTT Client connected successfully")

            # SUBSCRIBE NUR IM ON_CONNECT-CALLBACK!
            try:
                # Admin subscribiert zu allen Topics mit '#'
                result = client.subscribe("#", qos=1)
                if result[0] == 0:
                    logger.info("📥 Subscribed to all topics (#)")
                else:
                    logger.error(f"❌ Subscribe to all topics failed: {result[0]}")
            except Exception as e:
                logger.error(f"❌ Exception during subscribe: {e}")
        else:
            self.connected = False
            logger.error(f"❌ Admin MQTT Client connection failed: {rc}")

    def _on_message(self, client, userdata, msg):
        """MQTT on_message Callback (thread-safe)"""
        try:
            topic = msg.topic
            # Sichere Payload-Dekodierung
            try:
                payload_raw = msg.payload.decode("utf-8") if msg.payload else ""
            except (AttributeError, UnicodeDecodeError) as e:
                logger.warning(f"⚠️ Payload decode error: {e}")
                payload_raw = ""

            mqtt_timestamp = time.time()

            # JSON-Parsing
            try:
                message = json.loads(payload_raw)

                # Buffer-Update (mit MQTT-Client timestamp für Monitoring)
                # Robust für alle JSON-Typen (dict, list, str, int, bool)
                if isinstance(message, dict):
                    buffer_message = message.copy()
                    buffer_message["mqtt_timestamp"] = mqtt_timestamp
                else:
                    # Für Listen, Strings, Numbers, Booleans: als Dict wrappen
                    buffer_message = {"data": message, "mqtt_timestamp": mqtt_timestamp}

                with self._buffer_lock:
                    self.topic_buffers[topic].append(buffer_message)

                logger.debug(f"📥 Received on {topic}: {message}")

                # UI Refresh Handler: Detect omf2/ui/refresh/* topics and trigger request_refresh
                if topic.startswith("omf2/ui/refresh/"):
                    try:
                        # Extract group from topic: omf2/ui/refresh/{group}
                        group = topic.replace("omf2/ui/refresh/", "")
                        if group:
                            # Call request_refresh in the UI process (not st.rerun!)
                            from omf2.ui.utils.ui_refresh import request_refresh
                            request_refresh()
                            logger.debug(f"🔄 UI refresh requested for group '{group}' from MQTT")
                    except Exception as e:
                        logger.debug(f"⚠️ Failed to process UI refresh for topic {topic}: {e}")

                # Meta-Parameter für Gateway
                meta = {"mqtt_timestamp": mqtt_timestamp, "qos": msg.qos, "retain": msg.retain}

                # Gateway-Routing: message = clean_payload (keine Änderungen!)
                if self._gateway:
                    self._gateway.on_mqtt_message(topic, message, meta)
                else:
                    logger.debug(f"⚠️ No gateway registered, skipping routing for {topic}")

            except json.JSONDecodeError:
                # Nicht-JSON Messages als Text speichern
                with self._buffer_lock:
                    self.topic_buffers[topic].append({"raw_payload": payload_raw, "mqtt_timestamp": mqtt_timestamp})
                logger.debug(f"📥 Received raw on {topic}: {payload_raw}")

        except Exception as e:
            # Sammle alle Context-Informationen in einem String
            context_parts = []
            context_parts.append(f"❌ Admin Message processing error: {e}")

            try:
                context_parts.append(f"📍 Topic: {topic}")
            except Exception:
                context_parts.append("📍 Topic: <undefined>")

            try:
                context_parts.append(f"📍 Payload type: {type(payload_raw)}")
                context_parts.append(f"📍 Payload preview: {payload_raw[:200]}...")
            except Exception:
                context_parts.append("📍 Payload: <undefined>")

            try:
                context_parts.append(f"📍 MQTT timestamp: {mqtt_timestamp}")
            except Exception:
                context_parts.append("📍 MQTT timestamp: <undefined>")

            try:
                if "message" in locals():
                    context_parts.append(f"📍 Message type: {type(message)}")
                    context_parts.append(f"📍 Message preview: {str(message)[:200]}...")
                else:
                    context_parts.append("📍 Message: <not parsed>")
            except Exception:
                context_parts.append("📍 Message: <error accessing>")

            # Ein einziger Log-Eintrag mit allen Informationen
            logger.error(" | ".join(context_parts))

    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        self.connected = False
        logger.info("🔌 Admin MQTT Client disconnected")

    def register_gateway(self, gateway):
        """
        Registriert ein Gateway für Message-Routing

        Args:
            gateway: AdminGateway Instanz für Message-Routing
        """
        self._gateway = gateway
        logger.info("🚪 Admin Gateway registered for message routing")


# Singleton Factory
def get_admin_mqtt_client() -> AdminMqttClient:
    """
    Factory-Funktion für Admin MQTT Client Singleton

    Returns:
        Admin MQTT Client Singleton Instance
    """
    return AdminMqttClient()
