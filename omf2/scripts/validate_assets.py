#!/usr/bin/env python3
"""
Asset Validation Script
Prüft, ob alle Mappings in ASSET_MAPPINGS auf existierende Dateien zeigen.
Sollte als Pre-Commit Hook und in CI verwendet werden.
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from omf2.assets.asset_manager import ASSET_DEFAULTS, ASSET_MAPPINGS

    # Get assets directory
    assets_dir = Path(__file__).parent.parent / "assets"
    svg_dir = assets_dir / "svg"

    def validate_asset_mappings():
        """Prüft, ob alle Mappings auf existierende Dateien zeigen"""
        missing = []
        invalid_svgs = []

        for key, (subdir, filename) in ASSET_MAPPINGS.items():
            # Skip EMPTY_MODULE (None, None)
            if subdir is None or filename is None:
                continue

            path = svg_dir / subdir / filename

            if not path.exists():
                missing.append((key, path))
                continue

            # Optional: Prüfe ob es eine valide SVG ist (hat <svg> Tag)
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                    if "<svg" not in content.lower():
                        invalid_svgs.append((key, path, "No <svg> tag found"))
            except Exception as e:
                invalid_svgs.append((key, path, f"Error reading file: {e}"))

        # Check default fallback exists
        fallback_rel = ASSET_DEFAULTS.get("fallback", "")
        if fallback_rel and "/" in fallback_rel:
            fallback_subdir, fallback_filename = fallback_rel.split("/", 1)
            fallback_path = svg_dir / fallback_subdir / fallback_filename
            if not fallback_path.exists():
                missing.append(("DEFAULT_FALLBACK", fallback_path))

        # Report results
        if missing or invalid_svgs:
            print("❌ Asset validation failed!\n")

            if missing:
                print(f"Missing assets ({len(missing)}):")
                for key, path in missing:
                    print(f"  - {key}: {path}")

            if invalid_svgs:
                print(f"\nInvalid SVG files ({len(invalid_svgs)}):")
                for key, path, reason in invalid_svgs:
                    print(f"  - {key}: {path} ({reason})")

            print(f"\n⚠️  Total issues: {len(missing) + len(invalid_svgs)}")
            return False

        print(f"✅ All {len(ASSET_MAPPINGS)} asset mappings validated successfully")
        return True

    if __name__ == "__main__":
        success = validate_asset_mappings()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Failed to import asset_manager: {e}")
    print("Make sure you're running from the project root and dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error during asset validation: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
