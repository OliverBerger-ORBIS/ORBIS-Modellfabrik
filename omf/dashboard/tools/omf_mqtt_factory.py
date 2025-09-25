from __future__ import annotations

__all__ = ["ensure_dashboard_client", "create_ephemeral", "get_omf_mqtt_client"]
from typing import MutableMapping

from .mqtt_config import cfg_for
from .omf_mqtt_client import OmfMqttClient
from .logging_config import get_logger

# Logger für MQTT Factory
logger = get_logger("omf.dashboard.tools.omf_mqtt_factory")


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
    # INFO-Logging: Aufruf protokollieren
    logger.info(f"🔍 ensure_dashboard_client aufgerufen: env='{env}', store_keys={list(store.keys())}")
    
    cfg = cfg_for(env)
    cli = store.get("mqtt_client")
    stored_env = store.get("mqtt_env")
    
    # INFO-Logging: Aktuelle Zustände
    logger.info(f"🔍 Aktueller Zustand: cli={cli is not None}, stored_env='{stored_env}', requested_env='{env}'")

    if cli is None:
        # Erstinitialisierung
        logger.info(f"🆕 ERSTINITIALISIERUNG: Neuer MQTT-Client für env='{env}' wird erstellt")
        cli = OmfMqttClient(cfg)
        cli.connect()
        store["mqtt_client"] = cli
        store["mqtt_env"] = env
        logger.info(f"✅ ERSTINITIALISIERUNG: MQTT-Client erstellt und verbunden für env='{env}'")
        return cli

    # Strenge Prüfung auf Environment-Wechsel
    env_changed = stored_env != env
    logger.info(f"🔍 Environment-Wechsel geprüft: stored_env='{stored_env}' != requested_env='{env}' = {env_changed}")
    
    if env_changed:
        # Umgebung gewechselt -> sauberer Reconnect statt Neuaufbau
        logger.info(f"🔄 ENVIRONMENT-WECHSEL: Reconnect von '{stored_env}' zu '{env}'")
        try:
            # Altes Objekt aus Session State entfernen (doppelte Handles vermeiden)
            old_cli = store.get("mqtt_client")
            if old_cli and hasattr(old_cli, 'client'):
                logger.info(f"🔌 Alte MQTT-Verbindung wird getrennt")
                old_cli.client.loop_stop()
                old_cli.client.disconnect()
            
            cli.reconnect(cfg)
            store["mqtt_env"] = env
            logger.info(f"✅ ENVIRONMENT-WECHSEL: Reconnect erfolgreich zu env='{env}'")
            
            # Optional: Verlauf leeren
            if hasattr(cli, "clear_history"):
                try:
                    cli.clear_history()
                    logger.info(f"🧹 Verlauf geleert nach Environment-Wechsel")
                except Exception as e:
                    logger.warning(f"⚠️ Fehler beim Leeren des Verlaufs: {e}")
        except Exception as e:
            # Fallback: Neuen Client erstellen
            logger.error(f"❌ RECONNECT FEHLGESCHLAGEN: Fallback zu neuem Client. Fehler: {e}")
            cli = OmfMqttClient(cfg)
            cli.connect()
            store["mqtt_client"] = cli
            store["mqtt_env"] = env
            logger.info(f"✅ FALLBACK: Neuer MQTT-Client erstellt für env='{env}'")
    else:
        logger.info(f"♻️ BESTEHENDER CLIENT: Kein Environment-Wechsel, bestehender Client wird zurückgegeben")

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
