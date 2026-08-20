"""ORBIS workpiece intake bridge: APS RGB_NFC → osf/workpiece/intake."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
import time
from typing import Any

import paho.mqtt.client as mqtt

from intake import build_intake_event

LOG = logging.getLogger("osf-workpiece-intake-bridge")

DEFAULT_DPS_SERIAL = "SVR4H73275"
DEFAULT_PUBLISH_TOPIC = "osf/workpiece/intake"
DEDUP_TTL_SEC = 5.0


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value is not None and value != "" else default


def source_topics(dps_serial: str) -> list[str]:
    """Node-RED enriched state is primary; TXT direct state as fallback."""
    return [
        f"module/v1/ff/NodeRed/{dps_serial}/state",
        f"module/v1/ff/{dps_serial}/state",
    ]


class IntakeBridge:
    def __init__(self) -> None:
        self.host = _env("MQTT_HOST", "mqtt-broker")
        self.port = int(_env("MQTT_PORT", "1883"))
        self.username = _env("MQTT_USER", "default")
        self.password = _env("MQTT_PASS", "default")
        self.dps_serial = _env("DPS_SERIAL", DEFAULT_DPS_SERIAL)
        self.publish_topic = _env("PUBLISH_TOPIC", DEFAULT_PUBLISH_TOPIC)
        self.client_id = _env("MQTT_CLIENT_ID", "osf-workpiece-intake-bridge")
        self._topics = source_topics(self.dps_serial)
        self._last_by_nfc: dict[str, float] = {}
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
            protocol=mqtt.MQTTv311,
        )
        self._client.username_pw_set(self.username, self.password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

    def _on_connect(
        self,
        client: mqtt.Client,
        _userdata: Any,
        _flags: Any,
        reason_code: Any,
        _properties: Any = None,
    ) -> None:
        rc = getattr(reason_code, "value", reason_code)
        if rc != 0:
            LOG.error("MQTT connect failed rc=%s", reason_code)
            return
        for topic in self._topics:
            client.subscribe(topic, qos=0)
            LOG.info("Subscribed %s", topic)

    def _on_disconnect(
        self,
        _client: mqtt.Client,
        _userdata: Any,
        _disconnect_flags: Any,
        reason_code: Any,
        _properties: Any = None,
    ) -> None:
        LOG.warning("MQTT disconnected: %s", reason_code)

    def _should_publish(self, nfc: str) -> bool:
        now = time.monotonic()
        cutoff = now - DEDUP_TTL_SEC
        stale = [k for k, t in self._last_by_nfc.items() if t < cutoff]
        for k in stale:
            del self._last_by_nfc[k]
        last = self._last_by_nfc.get(nfc)
        if last is not None and now - last < DEDUP_TTL_SEC:
            return False
        self._last_by_nfc[nfc] = now
        return True

    def _on_message(
        self,
        client: mqtt.Client,
        _userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        try:
            raw = msg.payload.decode("utf-8")
            payload = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            LOG.warning("Ignore bad payload on %s: %s", msg.topic, exc)
            return
        if not isinstance(payload, dict):
            return

        event = build_intake_event(payload)
        if not event:
            return
        nfc = str(event["nfc"])
        if not self._should_publish(nfc):
            LOG.debug("Dedup skip nfc=%s", nfc)
            return

        body = json.dumps(event, separators=(",", ":"))
        info = client.publish(self.publish_topic, body, qos=0, retain=False)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            LOG.error("Publish failed rc=%s topic=%s", info.rc, self.publish_topic)
            return
        LOG.info(
            "Published %s nfc=%s productRaw=%s",
            self.publish_topic,
            nfc,
            event.get("productRaw"),
        )

    def run(self) -> None:
        LOG.info(
            "Starting bridge host=%s:%s publish=%s dps=%s",
            self.host,
            self.port,
            self.publish_topic,
            self.dps_serial,
        )
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_forever()


def main() -> None:
    logging.basicConfig(
        level=_env("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bridge = IntakeBridge()

    def _stop(_signum: int, _frame: Any) -> None:
        LOG.info("Shutting down")
        bridge._client.disconnect()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    bridge.run()


if __name__ == "__main__":
    main()
