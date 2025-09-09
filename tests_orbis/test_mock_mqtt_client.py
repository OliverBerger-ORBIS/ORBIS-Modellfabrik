# Datei verschoben nach tests_orbis/test_mock_mqtt_client.py
from src_orbis.omf.tools.mock_mqtt_client import MockMqttClient


def test_mock_mqtt_client_publish():
    client = MockMqttClient()
    result = client.publish("test/topic", "payload", qos=1)
    assert result is True
    assert client.connected


def test_mock_mqtt_client_subscribe():
    client = MockMqttClient()
    result = client.subscribe("test/topic", qos=1)
    assert result is True


def test_mock_mqtt_client_close():
    client = MockMqttClient()
    client.close()  # Sollte keine Exception werfen


def test_mock_mqtt_client_connection_status():
    client = MockMqttClient()
    status = client.get_connection_status()
    assert "stats" in status
    assert status["stats"]["messages_received"] == 0
    assert status["stats"]["messages_sent"] == 0
