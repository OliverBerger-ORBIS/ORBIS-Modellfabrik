import contextlib
import fnmatch
import json
import time
from collections import defaultdict, deque
from typing import Any, Callable, Deque, Dict, List, Set

import paho.mqtt.client as mqtt

from .mqtt_config import MqttConfig


class OmfMqttClient:
    def __init__(self, cfg: MqttConfig, on_message: Callable[[dict], None] | None = None, history_size: int = 10000):
        self.cfg = cfg
        self.config = {
            "broker": {
                "aps": {
                    "host": cfg.host,
                    "port": cfg.port,
                    "username": cfg.username or "",
                    "password": cfg.password or "",
                    "client_id": cfg.client_id,
                    "keepalive": cfg.keepalive,
                }
            },
            "subscriptions": {},
            "mode": "live",
        }
        self.client = mqtt.Client(client_id=cfg.client_id, clean_session=cfg.clean_session, protocol=cfg.protocol)
        if cfg.username:
            self.client.username_pw_set(cfg.username, cfg.password or "")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.connected = False
        self._topics = set()
        self._history = deque(maxlen=history_size)
        self._user_on_message = on_message

        # Neue Buffer-Architektur für per-Topic-Puffer
        self._buffers: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=1000))
        self._subscribed: Set[str] = set()

        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.loop_start()
        self.client.connect_async(cfg.host, cfg.port, keepalive=cfg.keepalive)

        # Warten auf Verbindung
        import time

        for _ in range(50):  # Max 5 Sekunden warten
            if self.connected:
                break
            time.sleep(0.1)

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self.connected = rc == 0
        for topic, qos in list(self._topics):
            try:
                client.subscribe(topic, qos)
            except TypeError:
                client.subscribe(topic, qos)

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False

    def _on_message(self, client, userdata, msg):
        # Legacy: In globale History schreiben
        message_record = {
            "type": "received",
            "topic": msg.topic,
            "payload": self._decode(msg.payload),
            "qos": msg.qos,
            "retain": msg.retain,
            "ts": time.time(),
        }
        self._history.append(message_record)

        # Neue Buffer-Architektur: In per-Topic-Buffer schreiben
        topic = msg.topic
        payload = self._decode(msg.payload)
        record = {"topic": topic, "payload": payload, "ts": time.time()}

        # Alle passenden Filter finden und in entsprechende Buffer schreiben
        for filt in list(self._subscribed):
            if self._matches_topic(topic, filt):
                self._buffers[filt].append(record)

        if self._user_on_message:
            try:
                self._user_on_message(message_record)
            except Exception:
                pass

    @staticmethod
    def _decode(payload: bytes):
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            try:
                return payload.decode("utf-8", errors="replace")
            except Exception:
                return repr(payload)

    def subscribe(self, topic: str, qos: int = 1):
        self._topics.add((topic, qos))
        self._subscribed.add(topic)  # Auch zu _subscribed hinzufügen
        if self.connected:
            self.client.subscribe(topic, qos)

    def publish(self, topic: str, payload, qos: int = 1, retain: bool = False) -> bool:
        data = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload)
        res = self.client.publish(topic, data, qos=qos, retain=retain)
        if res.rc == mqtt.MQTT_ERR_SUCCESS:
            self._history.append(
                {
                    "type": "sent",
                    "topic": topic,
                    "payload": payload,
                    "qos": qos,
                    "retain": retain,
                    "ts": time.time(),
                }
            )
            return True
        return False

    def drain(self) -> list[dict]:
        return list(self._history)

    def clear_history(self):
        self._history.clear()

    def get_history_stats(self) -> dict:
        history_copy = list(self._history)
        received = len([msg for msg in history_copy if msg.get("type") == "received"])
        sent = len([msg for msg in history_copy if msg.get("type") == "sent"])
        return {"total": len(history_copy), "received": received, "sent": sent, "max_capacity": self._history.maxlen}

    def get_connection_status(self) -> dict:
        stats = {"messages_received": 0, "messages_sent": 0}
        history_copy = list(self._history)
        for msg in history_copy:
            if msg["type"] == "received":
                stats["messages_received"] += 1
            elif msg["type"] == "sent":
                stats["messages_sent"] += 1
        return {
            "connected": self.connected,
            "broker": {"host": self.cfg.host, "port": self.cfg.port},
            "client_id": self.cfg.client_id,
            "stats": stats,
        }

    def close(self):
        try:
            self.client.loop_stop()
        finally:
            with contextlib.suppress(Exception):
                self.client.disconnect()

    # ---------- Neue Buffer-Architektur Methoden ----------

    def _matches_topic(self, topic: str, pattern: str) -> bool:
        """
        Prüft ob ein Topic einem Wildcard-Pattern entspricht.

        Args:
            topic: MQTT Topic
            pattern: Wildcard-Pattern mit + und #

        Returns:
            True wenn Topic dem Pattern entspricht
        """
        # Konvertiere MQTT-Wildcards zu fnmatch-Patterns
        # + entspricht einem einzelnen Level (nicht /)
        # # entspricht allen folgenden Levels
        fnmatch_pattern = pattern.replace('+', '*').replace('#', '*')
        return fnmatch.fnmatch(topic, fnmatch_pattern)

    def subscribe_many(self, filters: List[str], qos: int = 0) -> None:
        """
        Abonniert mehrere Topic-Filter idempotent.

        Args:
            filters: Liste von Topic-Filtern
            qos: MQTT QoS Level
        """
        new_ones = [f for f in filters if f not in self._subscribed]
        if not new_ones:
            return

        for f in new_ones:
            self.client.subscribe(f, qos=qos)
            self._subscribed.add(f)

    def get_buffer(self, filt: str, *, maxlen: int | None = None) -> Deque[Dict[str, Any]]:
        """
        Gibt den Buffer für einen Topic-Filter zurück.

        Args:
            filt: Topic-Filter
            maxlen: Maximale Buffer-Größe (optional)

        Returns:
            Deque mit Nachrichten für diesen Filter
        """
        buf = self._buffers[filt]
        if maxlen and buf.maxlen != maxlen:
            self._buffers[filt] = deque(buf, maxlen=maxlen)
            buf = self._buffers[filt]
        return buf

    def publish_json(self, topic: str, payload: dict, qos: int = 1, retain: bool = False) -> bool:
        """
        Publiziert eine JSON-Payload.

        Args:
            topic: MQTT Topic
            payload: Dictionary das als JSON serialisiert wird
            qos: MQTT QoS Level
            retain: MQTT Retain Flag

        Returns:
            True wenn erfolgreich publiziert
        """
        try:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            return self.publish(topic, data, qos=qos, retain=retain)
        except Exception as e:
            print(f"publish_json failed: {e}")
            return False

    def connect(self) -> bool:
        """
        Verbindet zum MQTT-Broker.

        Returns:
            True wenn Verbindung erfolgreich
        """
        try:
            self.client.connect(self.cfg.host, self.cfg.port, keepalive=self.cfg.keepalive)
            self.client.loop_start()  # Starte den MQTT-Loop
            self.connected = True
            return True
        except Exception as e:
            print(f"MQTT connect failed: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """
        Trennt die MQTT-Verbindung.
        """
        try:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
        except Exception as e:
            print(f"MQTT disconnect failed: {e}")

    def reconnect(self, new_cfg: MqttConfig) -> bool:
        """
        Reconnectet mit neuer Konfiguration.

        Args:
            new_cfg: Neue MQTT-Konfiguration

        Returns:
            True wenn Reconnect erfolgreich
        """
        try:
            # Alte Verbindung sauber trennen
            self.client.loop_stop()
            self.client.disconnect()

            # Neue Konfiguration setzen
            self.cfg = new_cfg
            self.config = {
                "broker": {
                    "aps": {
                        "host": new_cfg.host,
                        "port": new_cfg.port,
                        "username": new_cfg.username or "",
                        "password": new_cfg.password or "",
                        "client_id": new_cfg.client_id,
                        "keepalive": new_cfg.keepalive,
                    }
                },
                "subscriptions": {},
                "mode": "live",
            }

            # Neuen Client erstellen
            self.client = mqtt.Client(
                client_id=new_cfg.client_id, clean_session=new_cfg.clean_session, protocol=new_cfg.protocol
            )
            if new_cfg.username:
                self.client.username_pw_set(new_cfg.username, new_cfg.password or "")
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Verbinden
            self.client.reconnect_delay_set(min_delay=1, max_delay=30)
            self.client.loop_start()
            self.client.connect_async(new_cfg.host, new_cfg.port, keepalive=new_cfg.keepalive)

            return True
        except Exception as e:
            print(f"MQTT reconnect failed: {e}")
            return False

    def set_message_center_priority(self, level: int, prio_map: Dict[int, List[str]], history_maxlen: int = 5000):
        """
        Setzt die Priorität für die Nachrichten-Zentrale.

        Args:
            level: Prioritätsstufe (1-5)
            prio_map: Mapping von Prioritätsstufen zu Topic-Filtern
            history_maxlen: Maximale History-Größe
        """
        want: Set[str] = set()
        for n in range(1, level + 1):
            want.update(prio_map.get(n, []))

        # History begrenzen
        if not isinstance(self._history, deque):
            self._history = deque(self._history, maxlen=history_maxlen)
        else:
            self._history = deque(self._history, maxlen=history_maxlen)

        # Neue Subscriptions setzen
        self.subscribe_many(list(want), qos=1)
