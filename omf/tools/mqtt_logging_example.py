"""
MQTT Logging Beispiel

Zeigt die Verwendung von strukturiertem Logging in MQTT-Callbacks.
"""

import logging
from typing import Any, Dict

# Standard logging
logger = logging.getLogger("omf.mqtt")

# Structlog (falls verfügbar)
try:
    import structlog

    struct_logger = structlog.get_logger("omf.mqtt")
except ImportError:
    struct_logger = None


def on_message_stdlib(client, userdata, msg):
    """
    MQTT Callback mit Standard-Logging.

    Args:
        client: MQTT-Client
        userdata: User-Daten
        msg: MQTT-Nachricht
    """
    try:
        # Nur Metadaten loggen, keine sensiblen Payloads
        logger.info(
            "mqtt_rx", extra={"topic": msg.topic, "qos": int(msg.qos), "size": len(msg.payload), "retain": msg.retain}
        )
    except Exception:
        # Ignoriere Logging-Fehler in Callbacks
        pass


def on_message_structlog(client, userdata, msg):
    """
    MQTT Callback mit Structlog (strukturiert).

    Args:
        client: MQTT-Client
        userdata: User-Daten
        msg: MQTT-Nachricht
    """
    if not struct_logger:
        return

    try:
        # Strukturierte Logs mit Metadaten
        struct_logger.info("mqtt_rx", topic=msg.topic, qos=int(msg.qos), size=len(msg.payload), retain=msg.retain)
    except Exception:
        # Ignoriere Logging-Fehler in Callbacks
        pass


def on_connect_stdlib(client, userdata, flags, rc):
    """
    MQTT Connect Callback mit Standard-Logging.

    Args:
        client: MQTT-Client
        userdata: User-Daten
        flags: Connect-Flags
        rc: Return-Code
    """
    try:
        if rc == 0:
            logger.info("mqtt_connected", extra={"client_id": client._client_id})
        else:
            logger.error("mqtt_connect_failed", extra={"rc": rc})
    except Exception:
        pass


def on_connect_structlog(client, userdata, flags, rc):
    """
    MQTT Connect Callback mit Structlog.

    Args:
        client: MQTT-Client
        userdata: User-Daten
        flags: Connect-Flags
        rc: Return-Code
    """
    if not struct_logger:
        return

    try:
        if rc == 0:
            struct_logger.info("mqtt_connected", client_id=client._client_id)
        else:
            struct_logger.error("mqtt_connect_failed", rc=rc)
    except Exception:
        pass


def log_module_state_change(module_id: str, old_state: str, new_state: str, extra_data: Dict[str, Any] = None):
    """
    Loggt Modul-Status-Änderungen strukturiert.

    Args:
        module_id: Modul-ID
        old_state: Alter Status
        new_state: Neuer Status
        extra_data: Zusätzliche Daten
    """
    try:
        if struct_logger:
            struct_logger.info(
                "module_state_change",
                module_id=module_id,
                old_state=old_state,
                new_state=new_state,
                **(extra_data or {}),
            )
        else:
            logger.info(
                "module_state_change",
                extra={"module_id": module_id, "old_state": old_state, "new_state": new_state, **(extra_data or {})},
            )
    except Exception:
        pass


def log_sequence_event(
    sequence_id: str, event: str, module_id: str = None, step: int = None, extra_data: Dict[str, Any] = None
):
    """
    Loggt Sequenz-Ereignisse strukturiert.

    Args:
        sequence_id: Sequenz-ID
        event: Ereignis-Typ
        module_id: Modul-ID (optional)
        step: Schritt-Nummer (optional)
        extra_data: Zusätzliche Daten
    """
    try:
        if struct_logger:
            struct_logger.info(
                "sequence_event",
                sequence_id=sequence_id,
                event=event,
                module_id=module_id,
                step=step,
                **(extra_data or {}),
            )
        else:
            logger.info(
                "sequence_event",
                extra={
                    "sequence_id": sequence_id,
                    "event": event,
                    "module_id": module_id,
                    "step": step,
                    **(extra_data or {}),
                },
            )
    except Exception:
        pass
