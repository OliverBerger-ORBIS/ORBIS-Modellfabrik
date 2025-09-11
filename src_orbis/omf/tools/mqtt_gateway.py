"""
MessageGateway für sauberes MQTT-Publishing.

Adapter zwischen UI und message_generator für saubere Integration ohne st.rerun().
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from . import message_generator as mg
from .omf_mqtt_client import OmfMqttClient


def utc_iso() -> str:
    """Gibt UTC-Zeitstempel im ISO-Format zurück."""
    return datetime.now(timezone.utc).isoformat()


class MqttGateway:
    """
    Schlanke Brücke: nutzt den message_generator (mg) UNVERÄNDERT.

    - Ihr gebt eine Builder-Funktion (Name als str oder Callable) + kwargs.
    - Gateway ergänzt (wo sinnvoll) timestamp/orderId, published via client.publish_json().
    """

    def __init__(self, client: OmfMqttClient, id_start: int = 1000) -> None:
        self.client = client
        self._order_id = id_start

    def _next_order_id(self) -> int:
        """Generiert nächste Order-ID."""
        self._order_id += 1
        return self._order_id

    def build_via_mg(self, builder: str | Callable[..., dict[str, Any]], **kwargs) -> dict[str, Any]:
        """
        Baut Payload über message_generator.

        Args:
            builder: Funktionsname als String oder Callable
            **kwargs: Parameter für die Builder-Funktion

        Returns:
            Dict mit Payload
        """
        fn: Callable[..., dict[str, Any]] | None = None

        if callable(builder):
            fn = builder
        else:
            fn = getattr(mg, builder, None)

            if fn is None:
                # Falls mg Klassen nutzt (z.B. mg.MessageGenerator.instance().drill(...)):
                # erlaube "Klasse.Methode" als String
                if "." in builder:
                    cls_name, meth = builder.split(".", 1)
                    cls = getattr(mg, cls_name, None)
                    if cls:
                        inst = getattr(cls, "instance", None)
                        obj = inst() if callable(inst) else cls()
                        fn = getattr(obj, meth, None)

            if not callable(fn):
                raise ValueError(f"Unbekannter message_generator-Builder: {builder}")

        return fn(**kwargs)

    def enrich(self, payload: dict[str, Any], ensure_order_id: bool = False) -> dict[str, Any]:
        """
        Ergänzt Standardfelder nur, wenn sie fehlen.

        Args:
            payload: Payload-Dict
            ensure_order_id: Ob Order-ID ergänzt werden soll

        Returns:
            Angereicherte Payload
        """
        if "timestamp" not in payload:
            payload["timestamp"] = utc_iso()
        if ensure_order_id and "orderId" not in payload:
            payload["orderId"] = self._next_order_id()
        return payload

    def send(
        self,
        topic: str,
        builder: str | Callable[..., dict[str, Any]],
        *,
        ensure_order_id: bool = False,
        qos: int = 1,
        retain: bool = False,
        **kwargs,
    ) -> bool:
        """
        Baut Payload via message_generator, bereichert und publiziert.

        Args:
            topic: MQTT Topic
            builder: Builder-Funktion
            ensure_order_id: Ob Order-ID ergänzt werden soll
            qos: MQTT QoS Level
            retain: MQTT Retain Flag
            **kwargs: Parameter für Builder

        Returns:
            True wenn erfolgreich publiziert
        """
        payload = self.build_via_mg(builder, **kwargs)
        payload = self.enrich(payload, ensure_order_id=ensure_order_id)
        return self.client.publish_json(topic, payload, qos=qos, retain=retain)
