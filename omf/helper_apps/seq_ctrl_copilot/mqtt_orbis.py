class MockMqttClient:
    _instance = None

    def __init__(self):
        if MockMqttClient._instance is not None:
            raise Exception("Singleton!")
        MockMqttClient._instance = self

    @staticmethod
    def get_instance():
        if MockMqttClient._instance is None:
            MockMqttClient()
        return MockMqttClient._instance

    def publish(self, topic: str, payload: dict):
        print(f"[MQTT] Publish: {topic} - {payload}")


def send_mqtt_command(step: dict):
    client = MockMqttClient.get_instance()
    topic = step.get("topic", "test/topic")
    payload = step.get("payload", {"default": True})
    client.publish(topic, payload)
