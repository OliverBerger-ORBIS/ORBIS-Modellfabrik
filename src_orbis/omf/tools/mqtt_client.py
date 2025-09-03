# src_orbis/omf/tools/mqtt_client.py
from __future__ import annotations

import contextlib
import json
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable

import paho.mqtt.client as mqtt
import streamlit as st


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


class OMFMqttClient:
    def __init__(self, cfg: MqttConfig, on_message: Callable[[dict], None] | None = None, history_size: int = 1000):
        self.cfg = cfg
        # Konfiguration für Settings-Tab kompatibel machen
        self.config = {
            "broker": {
                "aps": {
                    "host": cfg.host,
                    "port": cfg.port,
                    "username": cfg.username or "",
                    "password": cfg.password or "",
                    "client_id": cfg.client_id,
                    "keepalive": cfg.keepalive,
                }
            },
            "subscriptions": {},
            "mode": "live",  # Standard-Modus
        }
        self.client = mqtt.Client(client_id=cfg.client_id, clean_session=cfg.clean_session, protocol=cfg.protocol)
        if cfg.username:
            self.client.username_pw_set(cfg.username, cfg.password or "")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.connected: bool = False
        self._topics: set[tuple[str, int]] = set()
        self._history = deque(maxlen=history_size)
        self._user_on_message = on_message

        # Backoff & Loop
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        self.client.loop_start()
        self.client.connect_async(cfg.host, cfg.port, keepalive=cfg.keepalive)

    # ---- Callbacks ----
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        self.connected = rc == 0
        # Resubscribe
        for topic, qos in list(self._topics):
            try:
                client.subscribe(topic, qos)  # kein noLocal setzen → eigene Publishes sichtbar
            except TypeError:
                client.subscribe(topic, qos)

    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False

    def _on_message(self, client, userdata, msg):
        self._history.append(
            {
                "type": "received",
                "topic": msg.topic,
                "payload": self._decode(msg.payload),
                "qos": msg.qos,
                "retain": msg.retain,
                "ts": time.time(),
            }
        )
        if self._user_on_message:
            try:
                self._user_on_message(self._history[-1])
            except Exception:
                pass

    # ---- Helpers ----
    @staticmethod
    def _decode(payload: bytes):
        try:
            return json.loads(payload.decode("utf-8"))
        except Exception:
            try:
                return payload.decode("utf-8", errors="replace")
            except Exception:
                return repr(payload)

    # ---- Public API ----
    def subscribe(self, topic: str, qos: int = 1):
        self._topics.add((topic, qos))
        if self.connected:
            self.client.subscribe(topic, qos)

    def publish(self, topic: str, payload, qos: int = 1, retain: bool = False) -> bool:
        data = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload)
        res = self.client.publish(topic, data, qos=qos, retain=retain)
        if res.rc == mqtt.MQTT_ERR_SUCCESS:
            # Sofort lokal spiegeln (UI-Feedback), Broker echo folgt (wenn subscribed)
            self._history.append(
                {
                    "type": "sent",
                    "topic": topic,
                    "payload": payload,
                    "qos": qos,
                    "retain": retain,
                    "ts": time.time(),
                }
            )
            return True
        return False

    def drain(self) -> list[dict]:
        # Schnapper für UI - Kopie erstellen um Race Conditions zu vermeiden
        return list(self._history)

    def get_connection_status(self) -> dict:
        """Gibt Connection-Status und Statistiken zurück"""
        stats = {"messages_received": 0, "messages_sent": 0}

        # Nachrichten zählen - Kopie erstellen um Race Conditions zu vermeiden
        history_copy = list(self._history)
        for msg in history_copy:
            if msg["type"] == "received":
                stats["messages_received"] += 1
            elif msg["type"] == "sent":
                stats["messages_sent"] += 1

        return {
            "connected": self.connected,
            "broker": {"host": self.cfg.host, "port": self.cfg.port},
            "client_id": self.cfg.client_id,
            "stats": stats,
        }

    def close(self):
        try:
            self.client.loop_stop()
        finally:
            with contextlib.suppress(Exception):
                self.client.disconnect()


@st.cache_resource(show_spinner=False)
def get_omf_mqtt_client(cfg_dict: dict) -> OMFMqttClient:
    """Singleton pro (konfigurationsgleicher) Session."""
    cfg = MqttConfig(**cfg_dict)
    client = OMFMqttClient(cfg)
    st.session_state["mqtt_client"] = client  # Convenience
    return client
