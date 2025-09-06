class MockMqttClient:
    def __init__(self):
        self.connected = True
        self.subscriptions = set()
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
        }

    def publish(self, _topic, _payload, _qos=0):
        self.stats["messages_sent"] += 1
        return True

    def subscribe(self, topic, qos=0):
        self.subscriptions.add((topic, qos))
        return True

    def close(self):
        self.connected = False

    def get_connection_status(self):
        return {
            "connected": self.connected,
            "subscriptions": list(self.subscriptions),
            "stats": self.stats.copy(),
        }
