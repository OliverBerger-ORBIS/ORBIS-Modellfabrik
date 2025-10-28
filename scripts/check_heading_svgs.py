#!/usr/bin/env python3
"""
Check that all files referenced in omf2/assets/heading_icons.HEADING_ICON_FILES exist.
Exit non-zero on missing files.
"""
from pathlib import Path
import sys
try:
    from omf2.assets import heading_icons as hi
except Exception as e:
    print("Could not import omf2.assets.heading_icons:", e)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
HEADINGS_DIR = REPO_ROOT / "omf2" / "assets" / "headings"

missing = []
for key, filename in getattr(hi, "HEADING_ICON_FILES", {}).items():
    if not (HEADINGS_DIR / filename).exists():
        missing.append(str(HEADINGS_DIR / filename))

if missing:
    print("Missing heading SVG files:")
    for m in missing:
        print(" -", m)
    sys.exit(2)

print("All heading SVGs present.")
sys.exit(0)
