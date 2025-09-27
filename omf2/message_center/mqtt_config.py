"""
MQTT Configuration for Message Center
"""

from dataclasses import dataclass
from typing import Optional
import paho.mqtt.client as mqtt


@dataclass(frozen=True)
class MqttConfig:
    """MQTT connection configuration"""
    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = "omf2_message_center"
    keepalive: int = 60
    clean_session: bool = True
    protocol: int = mqtt.MQTTv311
    tls: bool = False


def get_config_for_env(env: str) -> MqttConfig:
    """
    Get MQTT configuration for environment
    
    Args:
        env: Environment ("live", "replay", "mock")
        
    Returns:
        MqttConfig: Configuration for the environment
    """
    if env == "live":
        return MqttConfig(
            host="192.168.0.100",  # Default live broker
            port=1883,
            client_id="omf2_live_client"
        )
    elif env == "replay":
        return MqttConfig(
            host="localhost",
            port=1884,  # Different port for replay
            client_id="omf2_replay_client"
        )
    elif env == "mock":
        return MqttConfig(
            host="localhost",
            port=1883,
            client_id="omf2_mock_client"
        )
    else:
        raise ValueError(f"Unknown environment: {env}")