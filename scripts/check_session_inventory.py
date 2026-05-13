#!/usr/bin/env python3
"""
Prüft Abgleich: *.log in data/osf-data/sessions vs. Einträge in INVENTORY.md.

Liefert Exit 0 immer (Hinweis-Tool). Nutzung:
  python scripts/check_session_inventory.py

Pflege: Bei neuer Session Zeile in INVENTORY ergänzen; bei gelöschter Datei Zeile entfernen.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Erste Tabellenspalte: typischer Session-Dateiname ohne .log
_ROW_FIRST_COL = re.compile(r"^\|\s*([a-zA-Z0-9][a-zA-Z0-9_.-]*)\s*\|")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    sessions_dir = root / "data" / "osf-data" / "sessions"
    inventory = root / "data" / "osf-data" / "sessions" / "INVENTORY.md"

    log_files = sorted(sessions_dir.glob("*.log"))
    stems = {p.stem for p in log_files}

    inv_text = inventory.read_text(encoding="utf-8") if inventory.exists() else ""
    # Nur Tabelle „Schnellübersicht“ (bis nächste ##-Sektion)
    section_match = re.search(
        r"## Schnellübersicht\s*\n(.*?)(?=\n## |\Z)",
        inv_text,
        flags=re.DOTALL,
    )
    block = section_match.group(1) if section_match else inv_text

    mentioned: set[str] = set()
    for line in block.splitlines():
        m = _ROW_FIRST_COL.match(line)
        if not m:
            continue
        name = m.group(1)
        if name == "Session":
            continue
        if name.endswith(".log"):
            name = name[:-4]
        mentioned.add(name)

    only_files = sorted(stems - mentioned)
    only_inventory = sorted(mentioned - stems)
    missing_ccu_version: list[str] = []
    unknown_ccu_version: list[str] = []

    for log_file in log_files:
        try:
            first_line = log_file.read_text(encoding="utf-8").splitlines()[0].strip()
        except Exception:
            continue
        if not first_line:
            continue
        try:
            first_obj = json.loads(first_line)
        except json.JSONDecodeError:
            continue
        if first_obj.get("_kind") != "session_meta":
            continue

        ccu_version = str(first_obj.get("ccuVersion", "") or "").strip()
        if not ccu_version:
            missing_ccu_version.append(log_file.name)
        elif ccu_version == "unknown":
            unknown_ccu_version.append(log_file.name)

    print("Session-Logs vs. INVENTORY.md")
    print(f"  Verzeichnis: {sessions_dir}")
    print(f"  *.log Anzahl: {len(log_files)}")
    print(f"  INVENTORY-Namen (heuristisch): {len(mentioned)}")
    print()

    if only_files:
        print(".log ohne passende INVENTORY-Zeile (bitte Tabelle ergänzen):")
        for s in only_files[:50]:
            print(f"  - {s}")
        if len(only_files) > 50:
            print(f"  ... +{len(only_files) - 50} weitere")
        print()

    if only_inventory:
        print("INVENTORY-Einträge ohne .log (evtl. veraltet oder anderer Pfad):")
        for s in only_inventory[:50]:
            print(f"  - {s}")
        if len(only_inventory) > 50:
            print(f"  ... +{len(only_inventory) - 50} weitere")
        print()

    if missing_ccu_version:
        print("Session-Logs mit session_meta, aber ohne ccuVersion:")
        for name in missing_ccu_version[:50]:
            print(f"  - {name}")
        if len(missing_ccu_version) > 50:
            print(f"  ... +{len(missing_ccu_version) - 50} weitere")
        print()

    if unknown_ccu_version:
        print("Session-Logs mit ccuVersion=unknown (Version nicht erkannt):")
        for name in unknown_ccu_version[:50]:
            print(f"  - {name}")
        if len(unknown_ccu_version) > 50:
            print(f"  ... +{len(unknown_ccu_version) - 50} weitere")
        print()

    if not only_files and not only_inventory:
        print("OK: keine offensichtlichen Lücken (Heuristik).")

    sys.exit(0)


if __name__ == "__main__":
    main()
