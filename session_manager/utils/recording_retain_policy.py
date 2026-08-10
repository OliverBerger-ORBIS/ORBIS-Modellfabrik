"""
Retained-Message-Policy für den Session-Recorder.

Ziel:
- Broker-Dump **alter** Retained beim Subscribe/Start verwerfen (Grace).
- Live-Publishes mit retain=True behalten (z. B. quality_check).
- quality_check / dsp/aiqs/action: zusätzlich nach Payload-``ts`` filtern und
  deduplizieren — verhindert 28 MB-Spam, wenn dasselbe Retained alle ~2 s
  erneut zugestellt wird (Reconnect / gleiche MQTT-Client-ID).
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

# Window after recording start / re-subscribe in which retain=True is treated as
# the broker's retained dump (stale), not as a live publish.
RETAINED_STARTUP_GRACE_SEC = 2.0

# Allow through grace (live retain publishes); still subject to ts/dedupe filters.
RETAIN_ALWAYS_KEEP_TOPICS = frozenset(
    {
        "/j1/txt/1/i/quality_check",
        "dsp/aiqs/action",
    }
)

# Clock skew: accept payload ts slightly before wall-clock recording start.
PAYLOAD_TS_SKEW_SEC = 5.0


def should_skip_retained_message(
    is_retain: bool,
    *,
    recording_started_monotonic: float | None,
    now_monotonic: float | None = None,
    grace_sec: float = RETAINED_STARTUP_GRACE_SEC,
    include_startup_retained: bool = False,
    topic: str | None = None,
) -> bool:
    """
    True = Nachricht nicht ins Session-Log schreiben (Grace-Pfad).

    Whitelisted topics bypass grace (then apply ``should_skip_stale_or_duplicate_payload``).
    """
    if not is_retain:
        return False
    if topic and topic in RETAIN_ALWAYS_KEEP_TOPICS:
        return False
    if include_startup_retained:
        return False
    if recording_started_monotonic is None:
        return True
    now = time.monotonic() if now_monotonic is None else now_monotonic
    return (now - recording_started_monotonic) < grace_sec


def parse_payload_ts(payload: str | bytes | dict[str, Any] | None) -> datetime | None:
    """Extract ISO ``ts`` from quality_check / similar JSON payloads."""
    data: Any = payload
    if data is None:
        return None
    if isinstance(data, (bytes, bytearray)):
        try:
            data = data.decode("utf-8")
        except Exception:
            return None
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return None
    if not isinstance(data, dict):
        return None
    raw = data.get("ts")
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def payload_ts_key(payload: str | bytes | dict[str, Any] | None) -> str | None:
    """Stable dedupe key = payload ``ts`` string, if present."""
    data: Any = payload
    if isinstance(data, (bytes, bytearray)):
        try:
            data = data.decode("utf-8")
        except Exception:
            return None
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return None
    if not isinstance(data, dict):
        return None
    raw = data.get("ts")
    return raw.strip() if isinstance(raw, str) and raw.strip() else None


def should_skip_stale_or_duplicate_payload(
    topic: str,
    payload: str | bytes | dict[str, Any] | None,
    *,
    recording_started_at_utc: datetime | None,
    seen_payload_ts: set[str],
    skew_sec: float = PAYLOAD_TS_SKEW_SEC,
) -> bool:
    """
    True = skip for timestamped topics (quality_check, optionally aiqs/action).

    - Skip if payload ``ts`` is before recording start (minus skew) → alter Retain.
    - Skip if same payload ``ts`` already recorded → Reconnect-Spam.
    - If no ``ts``: only dedupe by empty marker once for non-quality topics; for
      quality_check without ts, keep (rare).
    """
    if topic not in RETAIN_ALWAYS_KEEP_TOPICS:
        return False

    key = payload_ts_key(payload)
    if key is not None:
        if key in seen_payload_ts:
            return True
        ts = parse_payload_ts(payload)
        if ts is not None and recording_started_at_utc is not None:
            start = recording_started_at_utc
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            else:
                start = start.astimezone(timezone.utc)
            if ts.timestamp() < (start.timestamp() - skew_sec):
                return True
        seen_payload_ts.add(key)
        return False

    # No ts: dedupe identical raw payload hash lightly via sentinel once per topic burst
    if topic == "dsp/aiqs/action":
        # action payloads are small; allow through without ts (changeLight)
        return False
    return False
