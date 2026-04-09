#!/usr/bin/env python3
"""
Prüft Abgleich: *.log in data/osf-data/sessions vs. Einträge in INVENTORY.md.

Liefert Exit 0 immer (Hinweis-Tool). Nutzung:
  python scripts/check_session_inventory.py

Pflege: Bei neuer Session Zeile in INVENTORY ergänzen; bei gelöschter Datei Zeile entfernen.
"""

from __future__ import annotations

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

    if not only_files and not only_inventory:
        print("OK: keine offensichtlichen Lücken (Heuristik).")

    sys.exit(0)


if __name__ == "__main__":
    main()
