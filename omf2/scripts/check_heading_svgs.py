#!/usr/bin/env python3
"""
Check that all files referenced in omf2/assets/heading_icons.HEADING_ICON_FILES exist.
Exit non-zero on missing files.
"""
import sys


def main():
    # Import the registry
    try:
        from omf2.assets.heading_icons import HEADING_ICON_FILES, HEADINGS_DIR
    except ImportError as e:
        print(f"ERROR: Could not import heading_icons module: {e}")
        return 1

    missing_files = []

    for key, filename in HEADING_ICON_FILES.items():
        file_path = HEADINGS_DIR / filename
        if not file_path.exists():
            missing_files.append((key, filename, str(file_path)))
            print(f"MISSING: {key} -> {filename} (expected: {file_path})")

    if missing_files:
        print(f"\nFound {len(missing_files)} missing SVG files")
        return 1
    else:
        print(f"✅ All {len(HEADING_ICON_FILES)} heading SVG files exist")
        return 0


if __name__ == "__main__":
    sys.exit(main())
