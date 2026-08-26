#!/usr/bin/env python3
"""
Insert synthetic osf/workpiece/intake lines into session logs (DR-30 Nachtrag 26.08.2026).

For each APS RGB_NFC FINISHED that would trigger the RPi intake bridge (NFC + known color),
insert one facade message immediately after that log line. Idempotent: skips if an intake
line for the same nfc already exists later in the file (or --force rewrites after strip).

Usage:
  python scripts/patch_session_intake_events.py              # all *.log under data/osf-data/sessions
  python scripts/patch_session_intake_events.py --dry-run
  python scripts/patch_session_intake_events.py path/to/one.log
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_SRC = ROOT / "osf-workpiece-intake-bridge" / "src"
sys.path.insert(0, str(BRIDGE_SRC))

from intake import build_intake_event  # noqa: E402

SESSIONS_DIR = ROOT / "data" / "osf-data" / "sessions"
INTAKE_TOPIC = "osf/workpiece/intake"


def _parse_payload(raw: object) -> dict | None:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _intake_nfcs_in_file(lines: list[str]) -> set[str]:
    found: set[str] = set()
    for line in lines:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("topic") != INTAKE_TOPIC:
            continue
        payload = _parse_payload(obj.get("payload"))
        if payload and isinstance(payload.get("nfc"), str) and payload["nfc"].strip():
            found.add(payload["nfc"].strip())
    return found


def patch_file(path: Path, *, dry_run: bool) -> tuple[int, int]:
    """Return (inserted_count, skipped_already)."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    existing = _intake_nfcs_in_file([ln.rstrip("\n") for ln in lines])

    out: list[str] = []
    inserted = 0
    skipped = 0
    published_this_pass: set[str] = set()

    for line in lines:
        out.append(line)
        raw = line.rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith('{"_kind"'):
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        topic = obj.get("topic") or ""
        if "SVR4H73275" not in topic or "/state" not in topic:
            continue
        payload = _parse_payload(obj.get("payload"))
        if not payload:
            continue
        event = build_intake_event(payload)
        if not event:
            continue
        nfc = str(event["nfc"])
        if nfc in existing or nfc in published_this_pass:
            skipped += 1
            continue

        log_ts = obj.get("timestamp") or event["timestamp"]
        intake_line = {
            "topic": INTAKE_TOPIC,
            "payload": json.dumps(event, separators=(",", ":")),
            "timestamp": log_ts,
            "qos": 0,
            "retain": False,
        }
        out.append(json.dumps(intake_line, separators=(",", ":")) + ("\n" if line.endswith("\n") else ""))
        published_this_pass.add(nfc)
        inserted += 1

    if inserted and not dry_run:
        path.write_text("".join(out), encoding="utf-8")
    return inserted, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Log files (default: all *.log in data/osf-data/sessions)",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    paths = args.paths or sorted(SESSIONS_DIR.glob("*.log"))
    total_ins = 0
    for path in paths:
        if not path.is_file():
            print(f"skip missing: {path}", file=sys.stderr)
            continue
        ins, skip = patch_file(path, dry_run=args.dry_run)
        total_ins += ins
        flag = "DRY " if args.dry_run else ""
        print(f"{flag}{path.name}: +{ins} intake (skip existing/dup {skip})")

    print(f"Total inserted: {total_ins}" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
