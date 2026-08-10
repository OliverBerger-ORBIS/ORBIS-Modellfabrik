"""
Persistenter MQTT-Client für Session Manager
Thread-sichere Implementierung ohne Connection-Loops
"""

# pylint: disable=broad-exception-caught,unused-argument

import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable

try:
    import paho.mqtt.client as mqtt

    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None

# Paho return codes we care about in Replay diagnostics (names stable across versions).
_PAHO_RC_NAMES: dict[int, str] = {
    -1: "NOT_CONNECTED",
    0: "SUCCESS",
    1: "NOMEM",
    2: "PROTOCOL",
    3: "INVAL",
    4: "NO_CONN",
    5: "CONN_REFUSED",
    6: "NOT_FOUND",
    7: "CONN_LOST",
    8: "TLS",
    9: "PAYLOAD_SIZE",
    10: "NOT_SUPPORTED",
    11: "AUTH",
    12: "ACL_DENIED",
    13: "UNKNOWN",
    14: "ERRNO",
    15: "QUEUE_SIZE",
    16: "KEEPALIVE",
}


def paho_rc_name(rc: int) -> str:
    """Human-readable Paho publish/connect return code."""
    if mqtt is not None:
        known = {
            int(mqtt.MQTT_ERR_SUCCESS): "SUCCESS",
            int(getattr(mqtt, "MQTT_ERR_NO_CONN", 4)): "NO_CONN",
            int(getattr(mqtt, "MQTT_ERR_QUEUE_SIZE", 15)): "QUEUE_SIZE",
            int(getattr(mqtt, "MQTT_ERR_CONN_LOST", 7)): "CONN_LOST",
        }
        if int(rc) in known:
            return known[int(rc)]
    return _PAHO_RC_NAMES.get(int(rc), f"RC_{rc}")


@dataclass
class MQTTMessage:
    """MQTT-Nachricht Datenstruktur"""

    topic: str
    payload: str | bytes
    qos: int = 0
    retain: bool = False


class SessionManagerMQTTClient:
    """
    Thread-sicherer, persistenter MQTT-Client für Session Manager.
    Verhindert Connection-Loops durch persistente Verbindung.
    """

    def __init__(self, host: str = "localhost", port: int = 1883, client_id: str | None = None):
        self.host = host
        self.port = port
        # Unique IDs avoid broker kicks when Streamlit reruns / second SM instance.
        self.client_id = client_id or f"session_manager_{uuid.uuid4().hex[:10]}"
        self.connected = False
        self.last_disconnect_rc: int | None = None
        self.last_connect_rc: int | None = None
        # RLock: connect() may call disconnect() while already holding the lock.
        self._lock = threading.RLock()
        self._client: Any = None
        self._message_callbacks: list[Callable[[MQTTMessage], None]] = []

    def connect(self) -> bool:
        """
        Verbindung zum MQTT-Broker herstellen.

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        if not MQTT_AVAILABLE:
            return False

        with self._lock:
            try:
                # Alte Verbindung sauber trennen
                if self._client:
                    self._disconnect_unlocked()

                # Neuen Client erstellen
                if mqtt is None:
                    return False
                self._client = mqtt.Client(client_id=self.client_id)
                self._client.on_connect = self._on_connect
                self._client.on_disconnect = self._on_disconnect
                self._client.on_message = self._on_message
                # High-speed replay: avoid QoS1 inflight / outbound queue stalls
                try:
                    self._client.max_inflight_messages_set(2000)
                except Exception:
                    pass
                try:
                    self._client.max_queued_messages_set(0)  # 0 = unlimited in paho
                except Exception:
                    pass

                # Verbindung herstellen
                self._client.connect(self.host, self.port, 60)
                self._client.loop_start()

                # Warten auf Verbindung
                for _ in range(50):  # Max 5 Sekunden
                    if self.connected:
                        break
                    time.sleep(0.1)

                return self.connected

            except Exception:
                self.connected = False
                return False

    def ensure_connected(self, timeout_s: float = 5.0) -> bool:
        """Return True if connected; otherwise attempt one reconnect."""
        if self.is_connected():
            return True
        # connect() has its own wait loop (~5s); timeout_s kept for API clarity.
        _ = timeout_s
        return self.connect()

    def disconnect(self):
        """Verbindung sauber trennen"""
        with self._lock:
            self._disconnect_unlocked()

    def _disconnect_unlocked(self) -> None:
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
            finally:
                self._client = None
                self.connected = False

    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> bool:
        """
        Nachricht publizieren.

        Args:
            topic: MQTT-Topic
            payload: Nachrichteninhalt
            qos: Quality of Service (0, 1, 2)
            retain: Retain-Flag

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        return self.publish_with_status(topic, payload, qos, retain)[0]

    def publish_with_status(
        self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False
    ) -> tuple[bool, int]:
        """
        Publish and return ``(ok, rc)``.

        ``rc`` is the paho return code (``MQTT_ERR_SUCCESS`` / queue / etc.).
        """
        if not self.connected or not self._client:
            return False, -1

        try:
            if mqtt is None:
                return False, -1
            result = self._client.publish(topic, payload, qos, retain)
            return result.rc == mqtt.MQTT_ERR_SUCCESS, int(result.rc)
        except Exception:
            return False, -1

    def subscribe(self, topic: str, qos: int = 0) -> bool:
        """
        Topic abonnieren.

        Args:
            topic: MQTT-Topic
            qos: Quality of Service

        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        if not self.connected or not self._client:
            return False

        try:
            if mqtt is None:
                return False
            result = self._client.subscribe(topic, qos)
            return result[0] == mqtt.MQTT_ERR_SUCCESS
        except Exception:
            return False

    def add_message_callback(self, callback: Callable[[MQTTMessage], None]):
        """Callback für eingehende Nachrichten hinzufügen"""
        with self._lock:
            self._message_callbacks.append(callback)

    def remove_message_callback(self, callback: Callable[[MQTTMessage], None]):
        """Callback für eingehende Nachrichten entfernen"""
        with self._lock:
            if callback in self._message_callbacks:
                self._message_callbacks.remove(callback)

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on_connect Callback"""
        self.last_connect_rc = int(rc)
        if rc == 0:
            self.connected = True
        else:
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        self.last_disconnect_rc = int(rc)
        self.connected = False

    def _on_message(self, client, userdata, msg):
        """MQTT on_message Callback"""
        message = MQTTMessage(topic=msg.topic, payload=msg.payload, qos=msg.qos, retain=msg.retain)

        # Alle Callbacks aufrufen
        with self._lock:
            for callback in self._message_callbacks:
                try:
                    callback(message)
                except Exception:
                    pass  # Callback-Fehler ignorieren

    def is_connected(self) -> bool:
        """Prüft ob Client verbunden ist"""
        return self.connected

    def get_client_info(self) -> dict:
        """Gibt Client-Informationen zurück"""
        return {
            "host": self.host,
            "port": self.port,
            "client_id": self.client_id,
            "connected": self.connected,
            "mqtt_available": MQTT_AVAILABLE,
            "last_connect_rc": self.last_connect_rc,
            "last_disconnect_rc": self.last_disconnect_rc,
        }
