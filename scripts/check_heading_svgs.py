#!/usr/bin/env python3
"""
Validate that all heading SVG files referenced by the OMF2 asset manager exist.

Historically this script imported `omf2.assets.heading_icons`. That module was
merged into `omf2.assets.asset_manager`, so we now introspect the central
`ASSET_MAPPINGS` structure and filter for entries that live inside the
`headings/` subdirectory.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from omf2.assets.asset_manager import ASSET_MAPPINGS
except Exception as exc:  # pragma: no cover - defensive guard for CI
    print(f"❌ Could not import omf2.assets.asset_manager: {exc}")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parents[1]
HEADINGS_DIR = REPO_ROOT / "omf2" / "assets" / "svg" / "headings"


def iter_heading_icons():
    """Yield (key, filename) pairs for heading icons defined in the asset manager."""
    for logical_key, mapping in ASSET_MAPPINGS.items():
        if not isinstance(mapping, tuple) or len(mapping) != 2:
            continue

        subdirectory, filename = mapping
        if subdirectory == "headings" and filename:
            yield logical_key, filename


def main() -> int:
    missing: list[str] = []

    for key, filename in iter_heading_icons():
        path = HEADINGS_DIR / filename
        if not path.exists():
            missing.append(f"{key}: {path}")

    if missing:
        print("❌ Missing heading SVG files:")
        for entry in missing:
            print(f" - {entry}")
        return 2

    print("✅ All heading SVG files referenced by the asset manager exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

