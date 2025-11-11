#!/usr/bin/env python3
"""
Check that all files referenced in omf2/assets/asset_manager.ASSET_MAPPINGS exist.
Exit non-zero on missing files.
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSET_MANAGER_PATH = REPO_ROOT / "omf2" / "assets" / "asset_manager.py"
SVG_DIR = REPO_ROOT / "omf2" / "assets" / "svg"

# Parse ASSET_MAPPINGS from asset_manager.py without importing it
# This avoids dependency issues with streamlit and other imports
try:
    with open(ASSET_MANAGER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract ASSET_MAPPINGS dictionary
    match = re.search(r'ASSET_MAPPINGS[^=]*=\s*{(.*?)\n}', content, re.DOTALL)
    if not match:
        print("Could not find ASSET_MAPPINGS in asset_manager.py")
        sys.exit(1)
    
    dict_content = match.group(1)
    
    # Parse the mapping entries to extract heading icons
    # Format: "KEY": ("subdir", "filename.svg"),
    pattern = r'"([^"]+)":\s*\("([^"]+)",\s*"([^"]+)"\)'
    matches = re.findall(pattern, dict_content)
    
    ASSET_MAPPINGS = {key: (subdir, filename) for key, subdir, filename in matches}
    
    if not ASSET_MAPPINGS:
        print("Could not parse ASSET_MAPPINGS entries")
        sys.exit(1)

except Exception as e:
    print(f"Could not parse asset_manager.py: {e}")
    sys.exit(1)

missing = []
# Filter for heading icons only (subdir="headings")
for key, (subdir, filename) in ASSET_MAPPINGS.items():
    if subdir == "headings" and filename:
        svg_path = SVG_DIR / subdir / filename
        if not svg_path.exists():
            missing.append(str(svg_path))

if missing:
    print("Missing heading SVG files:")
    for m in missing:
        print(" -", m)
    sys.exit(2)

print("All heading SVGs present.")
sys.exit(0)
