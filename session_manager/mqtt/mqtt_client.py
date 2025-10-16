"""
Persistenter MQTT-Client für Session Manager
Thread-sichere Implementierung ohne Connection-Loops
"""

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    mqtt = None


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

    def __init__(self, host: str = "localhost", port: int = 1883, client_id: str = "session_manager"):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.connected = False
        self._lock = threading.Lock()
        self._client: Optional[mqtt.Client] = None
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
                    self.disconnect()

                # Neuen Client erstellen
                self._client = mqtt.Client(client_id=self.client_id)
                self._client.on_connect = self._on_connect
                self._client.on_disconnect = self._on_disconnect
                self._client.on_message = self._on_message

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

    def disconnect(self):
        """Verbindung sauber trennen"""
        with self._lock:
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
        if not self.connected or not self._client:
            return False

        try:
            result = self._client.publish(topic, payload, qos, retain)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception:
            return False

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
        if rc == 0:
            self.connected = True
        else:
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """MQTT on_disconnect Callback"""
        self.connected = False

    def _on_message(self, client, userdata, msg):
        """MQTT on_message Callback"""
        message = MQTTMessage(
            topic=msg.topic,
            payload=msg.payload,
            qos=msg.qos,
            retain=msg.retain
        )

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
            "mqtt_available": MQTT_AVAILABLE
        }
