import time


class MockMqttClient:
    def drain(self):
        print("[MOCK] drain called")
        return getattr(self, "published_messages", [])

    def __init__(self, cfg=None):
        self.connected = True
        self.cfg = cfg or {}
        self.config = {
            "broker": {
                "aps": {
                    "host": "mock",
                    "port": 0,
                    "client_id": "mock_client",
                    "username": "",
                    "password": "",
                    "keepalive": 60,
                }
            },
            "subscriptions": {},
        }
        self.published_messages = []

    def close(self):
        print("[MOCK] Close called")
        self._closed = True
        return True

    def connect(self):
        self.connected = True
        print("[MOCK] Connect called")
        return True

    def disconnect(self):
        self.connected = False
        print("[MOCK] Disconnect called")
        return True

    def loop_start(self):
        self._loop_running = True
        print("[MOCK] loop_start called")
        return True

    def loop_stop(self):
        self._loop_running = False
        print("[MOCK] loop_stop called")
        return True

    def is_connected(self):
        return self.connected

    def get_client_id(self):
        return getattr(self, "_client_id", "mock_client")

    def get_broker(self):
        return getattr(self, "_broker", "mock")

    def get_port(self):
        return getattr(self, "_port", 0)

    def get_last_error(self):
        return getattr(self, "_last_error", None)

    def get_subscriptions(self):
        return getattr(self, "_subscriptions", {}).copy()

    def get_published_messages(self):
        return getattr(self, "published_messages", []).copy()

    def get_messages(self):
        return getattr(self, "_messages", []).copy()

    def __str__(self):
        return (
            f"<MockMqttClient id={self.get_client_id()} broker={self.get_broker()}:{self.get_port()} "
            f"connected={self.connected}>"
        )

    def get_connection_status(self):
        return {"stats": {"messages_received": 0, "messages_sent": 0}}

    @property
    def client(self):
        return None

    def subscribe(self, topic, qos=1):
        print(f"[MOCK] Subscribe called: {topic} (qos={qos})")
        return True

    def publish(self, topic: str, payload, qos: int = 1, retain: bool = False):
        """
        Akzeptiert 'qos' für Kompatibilität mit dem echten Client. Zusätzliche kwargs werden ignoriert.
        """
        print(f"[MOCK] Publish called: {topic} -> {payload} (qos={qos}, retain={retain})")
        self.published_messages.append(
            {
                "topic": topic,
                "payload": payload,
                "qos": qos,
                "retain": retain,
                "ts": time.time(),
            }
        )
        return True
