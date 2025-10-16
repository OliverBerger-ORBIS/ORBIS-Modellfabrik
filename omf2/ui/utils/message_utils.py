#!/usr/bin/env python3
"""
Message Utilities - Helper functions for message processing and display
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

import pandas as pd

from omf2.common.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MessageRow:
    """Repräsentiert eine Nachricht mit allen relevanten Informationen"""

    topic: str
    payload: Any
    message_type: str  # "received" oder "sent"
    timestamp: float
    qos: int = 0
    retain: bool = False

    def get_category(self) -> str:
        """Ermittelt die Kategorie basierend auf dem Topic"""
        return self.get_category_for_topic(self.topic)

    @staticmethod
    def get_category_for_topic(topic: str) -> str:
        """Ermittelt die Kategorie für einen gegebenen Topic (statische Methode)"""
        topic_lower = topic.lower()

        if topic_lower.startswith("ccu/"):
            return "ccu"
        elif topic_lower.startswith("nodered/"):
            return "nodered"
        elif topic_lower.startswith("module/v1/ff/"):
            return "module"
        elif topic_lower.startswith("txt/"):
            return "txt"
        elif topic_lower.startswith("fts/"):
            return "fts"
        else:
            return "Sonstige"


def flatten_messages_for_df(messages: List[MessageRow]) -> pd.DataFrame:
    """Konvertiert MessageRow-Objekte in ein DataFrame"""
    if not messages:
        return pd.DataFrame()

    data = []
    for msg in messages:
        # Timestamp formatieren
        try:
            timestamp = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
        except Exception:
            timestamp = str(msg.timestamp)

        # Payload vollständig anzeigen
        payload_str = str(msg.payload)
        # Nicht kürzen - vollständigen Payload anzeigen

        # Topic kürzen
        topic_short = msg.topic
        if len(topic_short) > 50:
            topic_short = topic_short[:50] + "..."

        data.append(
            {
                "⏰": timestamp,
                "📨": msg.message_type,
                "🏷️": msg.get_category(),
                "📡": topic_short,
                "📄": payload_str,
                "🔢": msg.qos,
                "💾": "✓" if msg.retain else "✗",
            }
        )

    df = pd.DataFrame(data)
    if not df.empty:
        # Nach Zeit sortieren (neueste zuerst)
        df = df.sort_values("⏰", ascending=False)

    return df


def parse_payload_for_display(payload: Any) -> str:
    """Parse payload for display in expandable sections"""
    try:
        if isinstance(payload, bytes):
            payload_str = payload.decode("utf-8")
            try:
                payload_json = json.loads(payload_str)
                return json.dumps(payload_json, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return payload_str
        elif isinstance(payload, dict):
            return json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            return str(payload)
    except Exception as e:
        logger.error(f"❌ Failed to parse payload: {e}")
        return str(payload)


def get_available_categories() -> List[str]:
    """Get list of available topic categories"""
    return ["Alle", "ccu", "module", "txt", "nodered", "fts", "Sonstige"]


def filter_messages_by_category(messages: List[MessageRow], category: str) -> List[MessageRow]:
    """Filter messages by category"""
    try:
        if category == "Alle":
            return messages

        return [msg for msg in messages if msg.get_category() == category]
    except Exception as e:
        logger.error(f"❌ Category filter failed: {e}")
        return messages  # Fallback to all messages


def filter_messages_by_type(messages: List[MessageRow], message_type: str) -> List[MessageRow]:
    """Filter messages by type (received/sent)"""
    try:
        if message_type == "Alle":
            return messages

        return [msg for msg in messages if msg.message_type == message_type]
    except Exception as e:
        logger.error(f"❌ Message type filter failed: {e}")
        return messages  # Fallback to all messages
