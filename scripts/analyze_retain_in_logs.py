#!/usr/bin/env python3
"""
Analysiert Session-Logs und test_topics auf QoS/Retain-Verteilung.

Zweck: Verifizieren ob State/Connection/Factsheet-Topics retained publiziert werden
(Fischertechnik-Doku).

WICHTIG: qos/retain-Werte müssen aus realen Sessions der Fischertechnik-Modellfabrik
kommen. Bestehende Sessions (production_order_*, storage_*, etc.) enthalten KEINE
qos/retain-Daten – empirische Verifizierung erfordert Neuaufnahme an der echten APS
mit Session Recorder v1.2+.

Usage:
    python scripts/analyze_retain_in_logs.py
    python scripts/analyze_retain_in_logs.py data/osf-data/sessions/auftrag-blau_1.log
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def analyze_log(path: Path) -> dict:
    """Analysiert eine .log Datei (JSON-Zeilen)."""
    stats = {
        "total": 0,
        "with_meta": 0,
        "state": {"retained": 0, "non_retained": 0},
        "connection": {"retained": 0, "non_retained": 0},
        "factsheet": {"retained": 0, "non_retained": 0},
    }
    for line in path.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            stats["total"] += 1
            if "qos" in data or "retain" in data:
                stats["with_meta"] += 1
            topic = data.get("topic", "")
            retain = data.get("retain", None)
            if retain is None:
                continue
            if topic.endswith("/state"):
                stats["state"]["retained" if retain else "non_retained"] += 1
            elif topic.endswith("/connection"):
                stats["connection"]["retained" if retain else "non_retained"] += 1
            elif topic.endswith("/factsheet"):
                stats["factsheet"]["retained" if retain else "non_retained"] += 1
        except json.JSONDecodeError:
            continue
    return stats


def analyze_test_topic(path: Path) -> dict | None:
    """Analysiert eine test_topic JSON-Datei."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        topic = data.get("topic", "")
        retain = data.get("retain")
        if retain is None:
            return None
        return {"topic": topic, "retain": retain, "qos": data.get("qos")}
    except Exception:
        return None


def main() -> None:
    if len(sys.argv) > 1:
        paths = [Path(p) for p in sys.argv[1:]]
    else:
        sessions_dir = REPO_ROOT / "data/osf-data/sessions"
        test_topics_dir = REPO_ROOT / "data/osf-data/test_topics"
        paths = list(sessions_dir.glob("*.log")) if sessions_dir.exists() else []
        paths.extend(test_topics_dir.rglob("*.json"))

    if not paths:
        print("Keine Dateien gefunden. Usage:")
        print("  python scripts/analyze_retain_in_logs.py")
        print("  python scripts/analyze_retain_in_logs.py <path-to.log>")
        return

    for path in sorted(paths):
        if not path.exists():
            continue
        if path.suffix == ".log":
            stats = analyze_log(path)
            if stats["total"] == 0:
                continue
            has_meta = "✅" if stats["with_meta"] else "❌"
            print(f"\n📄 {path.name}")
            print(f"   Total: {stats['total']} | Mit qos/retain: {stats['with_meta']} {has_meta}")
            if stats["with_meta"]:
                for kind in ("state", "connection", "factsheet"):
                    r, n = stats[kind]["retained"], stats[kind]["non_retained"]
                    if r or n:
                        print(f"   {kind}: retained={r}, non_retained={n}")
        elif path.suffix == ".json":
            info = analyze_test_topic(path)
            if info and info.get("retain") is not None:
                print(f"\n📄 {path.relative_to(REPO_ROOT)}")
                print(f"   topic={info['topic'][:50]}... retain={info['retain']} qos={info.get('qos')}")

    print("\n💡 Empirische Verifizierung erfordert: An realer Fischertechnik-Modellfabrik")
    print("   verbinden, Session Recorder v1.2+ aufnehmen, dann dieses Script auf die")
    print("   neue .log ausführen. Bestehende Sessions enthalten keine qos/retain-Daten.")


if __name__ == "__main__":
    main()
