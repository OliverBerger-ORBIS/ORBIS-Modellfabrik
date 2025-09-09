from dataclasses import dataclass

import paho.mqtt.client as mqtt


@dataclass(frozen=True)
class MqttConfig:
    host: str
    port: int = 1883
    username: str | None = None
    password: str | None = None
    client_id: str = "omf_dashboard"
    keepalive: int = 60
    clean_session: bool = True
    protocol: int = mqtt.MQTTv311  # passt i.d.R. für Mosquitto v2
    tls: bool = False
