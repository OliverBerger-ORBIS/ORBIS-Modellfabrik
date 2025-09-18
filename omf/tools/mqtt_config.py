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

def cfg_for(env: str) -> MqttConfig:
    """
    Erstellt MqttConfig basierend auf Umgebung.

    Args:
        env: Umgebung ("live", "replay", "mock")

    Returns:
        MqttConfig: Konfiguration für die angegebene Umgebung
    """
    if env == "live":
        from omf.config.config import LIVE_CFG

        return MqttConfig(**LIVE_CFG)
    elif env == "replay":
        from omf.config.config import REPLAY_CFG

        return MqttConfig(**REPLAY_CFG)
    elif env == "mock":
        return MqttConfig(host="localhost", port=1883, client_id="omf_dashboard_mock")
    else:
        raise ValueError(f"Unbekannte Umgebung: {env}")
