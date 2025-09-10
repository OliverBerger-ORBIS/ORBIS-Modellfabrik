class OMFMqttClient:
    _instance = None

    def __init__(self):
        if OMFMqttClient._instance is not None:
            raise Exception("Singleton!")
        OMFMqttClient._instance = self

    @staticmethod
    def get_instance():
        if OMFMqttClient._instance is None:
            OMFMqttClient()
        return OMFMqttClient._instance

    def publish(self, topic: str, payload: dict):
        print(f"[MQTT] Publish: {topic} - {payload}")


def send_mqtt_command(step: dict):
    client = OMFMqttClient.get_instance()
    topic = step.get("topic", "test/topic")
    payload = step.get("payload", {"default": True})
    client.publish(topic, payload)
