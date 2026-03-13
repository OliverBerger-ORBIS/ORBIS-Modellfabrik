#!/usr/bin/env python3
"""
Empirische Analyse der Session-Logs: FTS-Position nach Production-Abschluss und Quality-Fail.

Beantwortet:
1. Erfolgreicher Production-Abschluss: Nach ccu/order/completed oder ccu/order/active mit
   state FINISHED – wo steht das FTS (lastModuleSerialNumber / lastNodeId)?
2. Quality-Fail (AIQS FAILED): Nach module CHECK_QUALITY state/result FAILED –
   wohin fährt das AGV?

Single-Order-Filter: Erkennt Szenarien mit genau einer Order (keine weiteren ENQUEUED/IN_PROGRESS).
Diese sind entscheidend für Verifikation – bei weiteren Orders diktiert der Order-Prozess die FTS-Position.

Session-Format: Jede Zeile JSON mit topic, payload (String mit JSON), timestamp.

Usage:
    python scripts/analyze_session_fts_positions.py
    python scripts/analyze_session_fts_positions.py data/osf-data/sessions/mixed-sr-pr-prnok_20260305_121602.log
    python scripts/analyze_session_fts_positions.py --single-only  # Nur Single-Order-Szenarien
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SESSIONS_DIR = REPO_ROOT / "data/osf-data/sessions"
DPS_SERIAL = "SVR4H73275"  # DPS-Modul
HBW_SERIAL = "SVR3QA0022"  # HBW (Hochregallager)


@dataclass
class LogEvent:
    topic: str
    payload: dict | list
    timestamp: str


def parse_log_line(line: str) -> LogEvent | None:
    """Parst eine Log-Zeile. payload wird als JSON geparst."""
    line = line.strip()
    if not line:
        return None
    try:
        data = json.loads(line)
        topic = data.get("topic", "")
        payload_raw = data.get("payload", "{}")
        timestamp = data.get("timestamp", "")
        if isinstance(payload_raw, str):
            payload = json.loads(payload_raw) if payload_raw else {}
        else:
            payload = payload_raw
        return LogEvent(topic=topic, payload=payload, timestamp=timestamp)
    except (json.JSONDecodeError, TypeError):
        return None


def get_order_queue_info(payload: dict | list) -> tuple[int, bool]:
    """
    Analysiert ccu/order/active Payload.
    Returns (anzahl_orders_in_queue, has_finished).
    Orders in Queue = ENQUEUED oder IN_PROGRESS (nicht FINISHED, ERROR, CANCELLED).
    """
    if isinstance(payload, list):
        orders = [o for o in payload if isinstance(o, dict)]
    elif isinstance(payload, dict):
        orders = [payload]
    else:
        return 0, False
    has_finished = any(o.get("state") == "FINISHED" for o in orders)
    in_queue = sum(1 for o in orders if o.get("state") in ("ENQUEUED", "IN_PROGRESS"))
    return in_queue, has_finished


def is_single_order_scenario(payload: dict | list) -> bool:
    """True wenn genau eine Order fertig und keine anderen in der Queue (Production Success)."""
    in_queue, has_finished = get_order_queue_info(payload)
    return has_finished and in_queue == 0


def is_single_order_quality_fail(payload: dict | list | None) -> bool:
    """True wenn nur eine Order aktiv war (Quality-Fail: genau 1 Order in Queue)."""
    if payload is None:
        return False
    in_queue, _ = get_order_queue_info(payload)
    return in_queue == 1


def has_finished_order(payload: dict | list) -> bool:
    """True wenn mindestens eine Order state FINISHED hat."""
    if isinstance(payload, list):
        return any(isinstance(item, dict) and item.get("state") == "FINISHED" for item in payload)
    return isinstance(payload, dict) and payload.get("state") == "FINISHED"


def is_check_quality_failed(payload: dict) -> bool:
    """Prüft ob module/v1/ff/+/state actionState command CHECK_QUALITY mit state/result FAILED hat."""
    if not isinstance(payload, dict):
        return False

    def check_action(a: dict) -> bool:
        if not isinstance(a, dict):
            return False
        cmd = a.get("command") or a.get("commandType")
        if cmd != "CHECK_QUALITY":
            return False
        # result=FAILED oder state=FAILED (AIQS kann state=FINISHED + result=FAILED haben)
        return a.get("result") == "FAILED" or a.get("state") == "FAILED"

    # actionState (einzelnes Objekt)
    action_state = payload.get("actionState")
    if action_state and check_action(action_state):
        return True

    # actionStates (Array)
    for a in payload.get("actionStates", []):
        if check_action(a):
            return True

    return False


def extract_fts_position(payload: dict) -> tuple[str | None, str | None]:
    """Extrahiert lastModuleSerialNumber, lastNodeId aus FTS-State oder ccu/pairing transports."""
    if not isinstance(payload, dict):
        return None, None

    # Direkt aus fts/v1/ff/+/state
    last_mod = payload.get("lastModuleSerialNumber")
    last_node = payload.get("lastNodeId")

    # Fallback: ccu/pairing/state transports
    if last_mod is None or last_node is None:
        for t in payload.get("transports", []):
            if isinstance(t, dict):
                last_mod = last_mod or t.get("lastModuleSerialNumber")
                last_node = last_node or t.get("lastNodeId")
                if last_mod and last_node:
                    break

    return last_mod, last_node


def analyze_session(path: Path) -> dict:
    """Analysiert eine Session-Datei."""
    events: list[LogEvent] = []
    for line in path.open(encoding="utf-8"):
        ev = parse_log_line(line)
        if ev:
            events.append(ev)

    result = {
        "path": str(path.name),
        "total_events": len(events),
        "production_completion": [],
        "quality_fail": [],
    }

    last_active_orders: dict | list | None = None
    for i, ev in enumerate(events):
        if ev.topic == "ccu/order/active":
            last_active_orders = ev.payload if isinstance(ev.payload, (dict, list)) else None

        # (1) CCU Order FINISHED
        if ev.topic in ("ccu/order/completed", "ccu/order/active") and has_finished_order(ev.payload):
            # Sammle FTS-Positionen zeitlich danach
            fts_positions_after = []
            for j in range(i + 1, min(i + 500, len(events))):
                nex = events[j]
                if nex.topic.startswith("fts/v1/ff/") and nex.topic.endswith("/state"):
                    mod, node = extract_fts_position(nex.payload)
                    if mod or node:
                        fts_positions_after.append(
                            {
                                "timestamp": nex.timestamp,
                                "lastModuleSerialNumber": mod,
                                "lastNodeId": node,
                                "at_dps": node == DPS_SERIAL or mod == DPS_SERIAL,
                                "at_hbw": node == HBW_SERIAL or mod == HBW_SERIAL,
                            }
                        )
                elif "ccu/pairing/state" in nex.topic:
                    mod, node = extract_fts_position(nex.payload)
                    if mod or node:
                        fts_positions_after.append(
                            {
                                "timestamp": nex.timestamp,
                                "source": "pairing",
                                "lastModuleSerialNumber": mod,
                                "lastNodeId": node,
                                "at_dps": node == DPS_SERIAL or mod == DPS_SERIAL,
                                "at_hbw": node == HBW_SERIAL or mod == HBW_SERIAL,
                            }
                        )
            single_order = is_single_order_scenario(ev.payload)
            result["production_completion"].append(
                {
                    "order_timestamp": ev.timestamp,
                    "single_order": single_order,
                    "fts_positions_after": fts_positions_after[:10],
                }
            )

        # (2) Module CHECK_QUALITY FAILED
        if "module/v1/ff/" in ev.topic and ev.topic.endswith("/state") and is_check_quality_failed(ev.payload):
            fts_positions_after = []
            for j in range(i + 1, min(i + 500, len(events))):
                nex = events[j]
                if nex.topic.startswith("fts/v1/ff/") and nex.topic.endswith("/state"):
                    mod, node = extract_fts_position(nex.payload)
                    if mod or node:
                        fts_positions_after.append(
                            {
                                "timestamp": nex.timestamp,
                                "lastModuleSerialNumber": mod,
                                "lastNodeId": node,
                                "at_dps": node == DPS_SERIAL or mod == DPS_SERIAL,
                                "at_hbw": node == HBW_SERIAL or mod == HBW_SERIAL,
                            }
                        )
                elif "ccu/pairing/state" in nex.topic:
                    mod, node = extract_fts_position(nex.payload)
                    if mod or node:
                        fts_positions_after.append(
                            {
                                "timestamp": nex.timestamp,
                                "source": "pairing",
                                "lastModuleSerialNumber": mod,
                                "lastNodeId": node,
                                "at_dps": node == DPS_SERIAL or mod == DPS_SERIAL,
                                "at_hbw": node == HBW_SERIAL or mod == HBW_SERIAL,
                            }
                        )
            single_order = is_single_order_quality_fail(last_active_orders)
            result["quality_fail"].append(
                {
                    "fail_timestamp": ev.timestamp,
                    "module_topic": ev.topic,
                    "single_order": single_order,
                    "fts_positions_after": fts_positions_after[:10],
                }
            )

    return result


def print_report(analysis: dict, *, single_only: bool = False) -> None:
    """Gibt Analyse-Ergebnis formatiert aus. single_only: nur Single-Order-Szenarien."""
    prod = [p for p in analysis["production_completion"] if p.get("single_order")]
    qual = [q for q in analysis["quality_fail"] if q.get("single_order")]
    if single_only:
        prod_list = prod
        qual_list = qual
    else:
        prod_list = analysis["production_completion"]
        qual_list = analysis["quality_fail"]

    print(f"\n=== {analysis['path']} ({analysis['total_events']} Events) ===\n")
    if single_only:
        print("(Nur Single-Order-Szenarien)\n")

    if prod_list:
        print("1. ERFOLGREICHER PRODUCTION-ABSCHLUSS (ccu/order FINISHED)")
        print("-" * 60)
        for pc in prod_list:
            so = pc.get("single_order", False)
            so_tag = " ★ Single-Order (empfohlen für Verifikation)" if so else ""
            print(f"  Order-FINISHED @ {pc['order_timestamp']}{so_tag}")
            for fp in pc["fts_positions_after"]:
                mod = fp.get("lastModuleSerialNumber") or "-"
                node = fp.get("lastNodeId") or "-"
                at_dps = fp.get("at_dps", False)
                at_hbw = fp.get("at_hbw", False)
                src = f" [{fp.get('source', 'fts/state')}]" if "source" in fp else ""
                print(f"    -> FTS: lastModuleSerialNumber={mod}, lastNodeId={node}{src}")
                print(f"       Am DPS ({DPS_SERIAL}): {at_dps}  |  Am HBW ({HBW_SERIAL}): {at_hbw}")
            if not pc["fts_positions_after"]:
                print("    (keine FTS-Position danach gefunden)")
        print()
    elif single_only:
        print("1. ERFOLGREICHER PRODUCTION-ABSCHLUSS: Keine Single-Order-Szenarien.\n")
    else:
        print("1. ERFOLGREICHER PRODUCTION-ABSCHLUSS: Keine Order mit FINISHED gefunden.\n")

    if qual_list:
        print("2. QUALITY-FAIL (AIQS CHECK_QUALITY FAILED)")
        print("-" * 60)
        for qf in qual_list:
            so = qf.get("single_order", False)
            so_tag = " ★ Single-Order (empfohlen für Verifikation)" if so else ""
            print(f"  CHECK_QUALITY FAILED @ {qf['fail_timestamp']}{so_tag}")
            print(f"  Module: {qf['module_topic']}")
            for fp in qf["fts_positions_after"]:
                mod = fp.get("lastModuleSerialNumber") or "-"
                node = fp.get("lastNodeId") or "-"
                at_dps = fp.get("at_dps", False)
                at_hbw = fp.get("at_hbw", False)
                src = f" [{fp.get('source', 'fts/state')}]" if "source" in fp else ""
                print(f"    -> FTS: lastModuleSerialNumber={mod}, lastNodeId={node}{src}")
                print(f"       Am DPS ({DPS_SERIAL}): {at_dps}  |  Am HBW ({HBW_SERIAL}): {at_hbw}")
            if not qf["fts_positions_after"]:
                print("    (keine FTS-Position danach gefunden)")
        print()
    elif single_only:
        print("2. QUALITY-FAIL: Keine Single-Order-Szenarien.\n")
    else:
        print("2. QUALITY-FAIL: Kein CHECK_QUALITY FAILED gefunden.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="FTS-Position nach Production-Abschluss & Quality-Fail analysieren")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Session-Dateien (.log). Ohne Angabe: alle in data/osf-data/sessions",
    )
    parser.add_argument(
        "--single-only",
        action="store_true",
        help="Nur Single-Order-Szenarien anzeigen (empfohlen für Verifikation)",
    )
    args = parser.parse_args()

    if args.paths:
        paths = args.paths
    else:
        paths = sorted(SESSIONS_DIR.glob("*.log"))

    if not paths:
        print("Keine Session-Dateien gefunden.")
        return

    print("Empirische Session-Analyse: FTS-Position nach Production-Abschluss & Quality-Fail")
    print("=" * 70)

    for path in paths:
        if not path.exists():
            print(f"Überspringe (nicht gefunden): {path}")
            continue
        try:
            analysis = analyze_session(path)
            print_report(analysis, single_only=args.single_only)
        except Exception as e:
            print(f"Fehler bei {path}: {e}")


if __name__ == "__main__":
    main()
