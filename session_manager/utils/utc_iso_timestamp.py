"""Canonical UTC ISO-8601 with millisecond precision and Z suffix (aligned with OSF `utcIsoTimestampMs` / Arduino v1.1.6+)."""

from datetime import datetime, timezone


def utc_iso_timestamp_ms() -> str:
    """Return e.g. ``2026-03-31T12:00:00.123Z``."""
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{dt.microsecond // 1000:03d}Z"
