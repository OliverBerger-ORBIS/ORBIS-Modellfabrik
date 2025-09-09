__all__ = ["get_omf_mqtt_client"]
import streamlit as st

from .mqtt_config import MqttConfig
from .omf_mqtt_client import OMFMqttClient


@st.cache_resource(show_spinner=False)
def get_omf_mqtt_client(cfg_dict: dict = None) -> OMFMqttClient:
    """Singleton pro (konfigurationsgleicher) Session."""
    if cfg_dict is None:
        # Default-Konfiguration, kann angepasst werden
        cfg_dict = {"host": "localhost", "port": 1883}
    cfg = MqttConfig(**cfg_dict)
    client = OMFMqttClient(cfg)
    # NICHT in session_state überschreiben - das macht der Aufrufer
    return client
