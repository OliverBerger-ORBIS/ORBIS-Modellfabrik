"""
Erste Zeile in Session-*.log: JSON ohne MQTT-Pflichtfelder (topic/payload/timestamp).

Wird von load_log_session / Replay übersprungen; Session-Analyse überspringt ebenfalls.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from .path_constants import PROJECT_ROOT

SESSION_META_KIND = "session_meta"
SESSION_META_SCHEMA = 1


def read_osf_workspace_version() -> str:
    """Root package.json version (Single Source of Truth neben OSF-UI)."""
    pkg = PROJECT_ROOT / "package.json"
    try:
        with open(pkg, encoding="utf-8") as f:
            data = json.load(f)
        ver = data.get("version", "unknown")
        name = data.get("name", "workspace")
        return f"{name}@{ver}"
    except (OSError, json.JSONDecodeError, TypeError):
        return "unknown"


def _dt_iso(dt: datetime) -> str:
    """ISO mit Millisekunden (naive = lokale Session-Manager-Zeit)."""
    return dt.isoformat(timespec="milliseconds")


def build_session_meta_line(
    *,
    session_name: str,
    log_filename: str,
    recording_started_at: datetime,
    recording_ended_at: datetime,
    recording_exclusion_preset: str,
    broker_host: str,
    broker_port: int,
    ccu_orders_description: str,
    ccu_order_outcome: str,
    note: str,
) -> str:
    """
    Eine JSON-Zeile — keine Keys topic/payload/timestamp → Replay lädt nur echte MQTT-Zeilen.
    """
    duration_sec = (recording_ended_at - recording_started_at).total_seconds()
    if duration_sec < 0:
        duration_sec = 0.0

    meta: dict[str, Any] = {
        "_kind": SESSION_META_KIND,
        "schema": SESSION_META_SCHEMA,
        "sessionName": session_name,
        "logFileName": log_filename,
        "recordingStartedAt": _dt_iso(recording_started_at),
        "recordingEndedAt": _dt_iso(recording_ended_at),
        "durationSec": round(duration_sec, 3),
        "recordingExclusionPreset": recording_exclusion_preset,
        "brokerHost": broker_host,
        "brokerPort": int(broker_port),
        "osfWorkspaceVersion": read_osf_workspace_version(),
        "ccuOrdersDescription": (ccu_orders_description or "").strip(),
        "ccuOrderOutcome": ccu_order_outcome if ccu_order_outcome in ("ok", "nok", "mixed", "unknown") else "unknown",
        "note": (note or "").strip(),
    }
    return json.dumps(meta, ensure_ascii=False)


def is_session_meta_line(parsed: dict[str, Any]) -> bool:
    return parsed.get("_kind") == SESSION_META_KIND and parsed.get("schema") == SESSION_META_SCHEMA
