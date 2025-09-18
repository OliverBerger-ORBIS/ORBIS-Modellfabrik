from __future__ import annotations

__all__ = ["ensure_dashboard_client", "create_ephemeral", "get_omf_mqtt_client"]
from typing import MutableMapping

from .mqtt_config import cfg_for
from .omf_mqtt_client import OmfMqttClient

def ensure_dashboard_client(env: str, store: MutableMapping) -> OmfMqttClient:
    """
    Liefert genau EINEN MQTT-Client pro Streamlit-Session.
    Verwendung NUR im omf_dashboard.py. Nicht in Komponenten aufrufen.

    Args:
        env: Umgebung ("live", "replay", "mock")
        store: MutableMapping (z.B. st.session_state)

    Returns:
        OmfMqttClient: Singleton-Client für die Session
    """
    cfg = cfg_for(env)
    cli = store.get("mqtt_client")

    if cli is None:
        # Erstinitialisierung
        cli = OmfMqttClient(cfg)
        cli.connect()
        store["mqtt_client"] = cli
        store["mqtt_env"] = env
        return cli

    # Umgebung gewechselt -> sauberer Reconnect statt Neuaufbau
    if store.get("mqtt_env") != env:
        try:
            cli.reconnect(cfg)
            store["mqtt_env"] = env
            # Optional: Verlauf leeren
            if hasattr(cli, "clear_history"):
                try:
                    cli.clear_history()
                except Exception:
                    pass
        except Exception:
            # Fallback: Neuen Client erstellen
            cli = OmfMqttClient(cfg)
            cli.connect()
            store["mqtt_client"] = cli
            store["mqtt_env"] = env

    return cli

def create_ephemeral(env: str) -> OmfMqttClient:
    """
    Für Tests/Tools außerhalb der Streamlit-App: separater, kurzfristiger Client.
    In der App NICHT verwenden, sonst drohen Doppelverbindungen.

    Args:
        env: Umgebung ("live", "replay", "mock")

    Returns:
        OmfMqttClient: Ephemeraler Client für Tests/Tools
    """
    cfg = cfg_for(env)
    cli = OmfMqttClient(cfg)
    cli.connect()
    return cli

# Legacy-Funktion für Rückwärtskompatibilität (nur für Tests/Tools)
def get_omf_mqtt_client(cfg_dict: dict = None) -> OmfMqttClient:
    """
    Legacy-Funktion für Tests/Tools außerhalb der Streamlit-App.

    WARNUNG: In der Streamlit-App NICHT verwenden!
    Verwende stattdessen ensure_dashboard_client() im omf_dashboard.py.
    """
    if cfg_dict is None:
        cfg_dict = {"host": "localhost", "port": 1883}
    return create_ephemeral("live")  # Fallback auf live
