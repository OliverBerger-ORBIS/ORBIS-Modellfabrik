import json
import logging
import queue
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple

try:
    import paho.mqtt.client as mqtt
except ImportError as e:
    raise RuntimeError("Please install paho-mqtt: pip install paho-mqtt") from e


@dataclass
class MqttMessage:
    ts: float
    direction: str  # "in" | "out"
    topic: str
    payload: str
    qos: int
    retain: int
    mid: Optional[int] = None


class MessageMonitorService:
    """
    A robust MQTT monitor with persistence.
    - Uses ONE client for both subscribe and publish (simplest & most reliable).
    - Auto-reconnects via connect_async + loop_start + reconnect_delay_set.
    - Thread-safe publish; messages are persisted to SQLite via a writer thread.
    - Designed to be kept as a singleton in Streamlit via st.cache_resource.
    """

    def __init__(
        self,
        broker_host: str,
        broker_port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: Optional[str] = None,
        subscribe_filter: Tuple[str, int] = ("#", 0),
        db_path: str = "messages.sqlite",
        keepalive: int = 45,
        tls: bool = False,
        client_logger: Optional[logging.Logger] = None,
    ) -> None:
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client_id = client_id or f"monitor-{uuid.uuid4()}"
        self.subscribe_filter = subscribe_filter
        self.db_path = db_path
        self.keepalive = keepalive
        self.tls = tls

        self._client = mqtt.Client(client_id=self.client_id, clean_session=True, protocol=mqtt.MQTTv311)
        if client_logger:
            self._client.enable_logger(client_logger)
        else:
            self._client.enable_logger()

        if username:
            self._client.username_pw_set(username, password or None)
        if tls:
            self._client.tls_set()  # use system CA bundle

        # Last will: indicate this monitor went offline
        self._client.will_set(
            "monitor/status",
            payload=json.dumps({"client_id": self.client_id, "state": "offline"}),
            qos=1,
            retain=True,
        )

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.on_publish = self._on_publish

        # Auto-reconnect backoff
        self._client.reconnect_delay_set(min_delay=1, max_delay=60)

        self._msg_q: "queue.Queue[MqttMessage]" = queue.Queue(maxsize=10_000)
        self._stop_evt = threading.Event()
        self._writer_thread = threading.Thread(target=self._writer_loop, name="mqtt-writer", daemon=True)
        self._connected = False
        self._last_connect_ts: Optional[float] = None

        self._init_db()

    # ---- Public API ---------------------------------------------------------
    def start(self) -> "MessageMonitorService":
        """Start MQTT network loop and DB writer thread."""
        if not self._writer_thread.is_alive():
            self._writer_thread.start()
        # Connect async + background loop for auto-reconnect behavior.
        self._client.connect_async(self.broker_host, self.broker_port, keepalive=self.keepalive)
        self._client.loop_start()
        return self

    def stop(self) -> None:
        self._stop_evt.set()
        try:
            self._client.loop_stop()
        except Exception:
            pass
        try:
            self._client.disconnect()
        except Exception:
            pass

    def is_connected(self) -> bool:
        return self._connected

    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False) -> Optional[int]:
        """
        Thread-safe publish. Payload may be str, bytes, dict/list (will be JSON-encoded).
        Returns message ID (mid) or None if publish failed quickly (e.g., disconnected).
        """
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload, ensure_ascii=False)
        elif not isinstance(payload, (str, bytes)):
            payload = str(payload)

        try:
            info = self._client.publish(topic, payload=payload, qos=qos, retain=retain)
            # Persist immediately (outbound) for auditability
            self._enqueue("out", topic, payload, qos, int(retain), mid=getattr(info, "mid", None))
            return getattr(info, "mid", None)
        except Exception:
            return None

    def fetch_recent(self, limit: int = 200) -> List[MqttMessage]:
        """Return recent messages (newest first)."""
        con = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            "SELECT ts, direction, topic, payload, qos, retain, mid FROM messages ORDER BY id DESC LIMIT ?",
            (int(limit),),
        )
        rows = cur.fetchall()
        con.close()
        return [MqttMessage(*row) for row in rows]

    # ---- Internals ----------------------------------------------------------
    def _init_db(self) -> None:
        con = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts REAL NOT NULL,
                direction TEXT NOT NULL,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                qos INTEGER NOT NULL,
                retain INTEGER NOT NULL,
                mid INTEGER
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(ts);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_topic ON messages(topic);")
        con.commit()
        con.close()

    def _writer_loop(self) -> None:
        con = sqlite3.connect(self.db_path, check_same_thread=False)
        cur = con.cursor()
        while not self._stop_evt.is_set():
            try:
                msg: MqttMessage = self._msg_q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                cur.execute(
                    "INSERT INTO messages (ts, direction, topic, payload, qos, retain, mid) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (msg.ts, msg.direction, msg.topic, msg.payload, msg.qos, msg.retain, msg.mid),
                )
                con.commit()
            except Exception as e:
                print(f"[writer] DB error: {e}")
        con.close()

    def _enqueue(
        self, direction: str, topic: str, payload: str, qos: int, retain: int, mid: Optional[int] = None
    ) -> None:
        try:
            self._msg_q.put_nowait(MqttMessage(time.time(), direction, topic, payload, qos, retain, mid))
        except queue.Full:
            # Drop one and retry to avoid blocking UI
            try:
                _ = self._msg_q.get_nowait()
                self._msg_q.put_nowait(MqttMessage(time.time(), direction, topic, payload, qos, retain, mid))
            except Exception:
                pass

    # ---- MQTT callbacks -----------------------------------------------------
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self._connected = rc == 0
        self._last_connect_ts = time.time()
        if self._connected:
            topic, qos = self.subscribe_filter
            try:
                client.subscribe(topic, qos=qos)
            except Exception as e:
                print(f"[mqtt] subscribe error: {e}")
            # Publish "online" state (retain so others can see)
            try:
                client.publish(
                    "monitor/status",
                    json.dumps({"client_id": self.client_id, "state": "online"}),
                    qos=1,
                    retain=True,
                )
            except Exception:
                pass
        else:
            print(f"[mqtt] connect failed with rc={rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self._connected = False
        # connect_async + loop_start will retry with backoff.

    def _on_message(self, client, userdata, msg):
        # Decode payload safely for storage/inspection
        try:
            payload_text = msg.payload.decode("utf-8", errors="replace")
        except Exception:
            payload_text = repr(msg.payload)
        self._enqueue("in", msg.topic, payload_text, msg.qos, int(msg.retain))

    def _on_publish(self, client, userdata, mid):
        # Optionally update DB with publish acknowledge
        pass


def make_unique_client_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"
