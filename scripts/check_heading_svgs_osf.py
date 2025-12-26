#!/usr/bin/env python3
"""
Check that all heading SVG files referenced in OSF code exist.
Scans TypeScript files for 'headings/*.svg' references and verifies files exist.
Exit non-zero on missing files.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OSF_DIR = REPO_ROOT / "osf"
HEADINGS_DIR = OSF_DIR / "apps" / "osf-ui" / "public" / "headings"

# Find all TypeScript files in osf
ts_files = []
for pattern in ["**/*.ts", "**/*.html"]:
    ts_files.extend(OSF_DIR.rglob(pattern))

# Extract all heading icon references
heading_refs = set()
# Pattern 1: 'headings/xxx.svg' or "headings/xxx.svg"
pattern1 = r"['\"]headings/([^'\"]+\.svg)['\"]"
# Pattern 2: '/headings/xxx.svg' (from testing-fixtures)
pattern2 = r"['\"]/headings/([^'\"]+\.svg)['\"]"

for ts_file in ts_files:
    try:
        with open(ts_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches1 = re.findall(pattern1, content)
            matches2 = re.findall(pattern2, content)
            heading_refs.update(matches1)
            heading_refs.update(matches2)
    except Exception as e:
        print(f"Warning: Could not read {ts_file}: {e}", file=sys.stderr)

if not heading_refs:
    print("No heading icon references found in OSF code.")
    sys.exit(0)

# Check if all referenced files exist
missing = []
for ref in sorted(heading_refs):
    svg_path = HEADINGS_DIR / ref
    if not svg_path.exists():
        missing.append(f"headings/{ref}")

if missing:
    print("Missing heading SVG files referenced in OSF code:")
    for m in missing:
        print(f"  - {m}")
    print(f"\nExpected location: {HEADINGS_DIR}")
    sys.exit(1)

print(f"✅ All {len(heading_refs)} heading SVG files referenced in OSF code exist.")
sys.exit(0)

