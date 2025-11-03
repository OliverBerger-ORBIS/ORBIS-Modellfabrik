#!/usr/bin/env python3
"""
Migration Script: heading_icons.get_svg_inline() → asset_manager.get_asset_inline()

Replaces all imports and calls to heading_icons.get_svg_inline() with asset_manager.get_asset_inline()
"""

import re
from pathlib import Path
from typing import List

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Files to migrate (UI files only, exclude tests and docs for now)
UI_DIR = PROJECT_ROOT / "omf2" / "ui"


def migrate_file(file_path: Path) -> bool:
    """Migrate a single file. Returns True if changes were made."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Pattern 1: Import statement
        # from omf2.assets.heading_icons import get_svg_inline
        # → from omf2.assets.asset_manager import get_asset_manager
        content = re.sub(
            r"from omf2\.assets\.heading_icons import get_svg_inline",
            "from omf2.assets.asset_manager import get_asset_manager",
            content,
        )

        # Pattern 2: Import with other imports
        # from omf2.assets.heading_icons import get_svg_inline, ...
        # → from omf2.assets.asset_manager import get_asset_manager
        # (Note: This might need manual review if other imports are present)
        content = re.sub(
            r"from omf2\.assets\.heading_icons import get_svg_inline(?:\s*,\s*.*)?",
            "from omf2.assets.asset_manager import get_asset_manager",
            content,
        )

        # Pattern 3: Function calls
        # get_svg_inline(key, size_px=..., color=..., locale=...)
        # → get_asset_manager().get_asset_inline(key, size_px=..., color=...)
        # Note: locale parameter is removed (not used in new API)

        # Simple call: get_svg_inline(key)
        content = re.sub(
            r"get_svg_inline\(([^,)]+)\)",
            r"get_asset_manager().get_asset_inline(\1)",
            content,
        )

        # With parameters: get_svg_inline(key, size_px=..., color=..., locale=...)
        # Remove locale parameter if present
        content = re.sub(
            r"get_svg_inline\(([^)]+)\)",
            lambda m: _replace_svg_inline_call(m.group(1)),
            content,
        )

        # Only write if content changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"❌ Error migrating {file_path}: {e}")
        return False


def _replace_svg_inline_call(params_str: str) -> str:
    """Replace get_svg_inline() call parameters, removing locale."""
    # Remove locale parameter if present
    params_str = re.sub(r",\s*locale\s*=\s*[^,)]+", "", params_str)
    params_str = re.sub(r"locale\s*=\s*[^,)]+\s*,?\s*", "", params_str)

    return f"get_asset_manager().get_asset_inline({params_str})"


def find_ui_files() -> List[Path]:
    """Find all Python files in UI directory that use heading_icons."""
    files_to_migrate = []
    for py_file in UI_DIR.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "heading_icons" in content or "get_svg_inline" in content:
                files_to_migrate.append(py_file)
        except Exception:
            pass
    return files_to_migrate


def main():
    """Main migration function."""
    print("🔍 Searching for files to migrate...")
    files = find_ui_files()
    print(f"📁 Found {len(files)} files to migrate")

    migrated = 0
    for file_path in sorted(files):
        print(f"  - {file_path.relative_to(PROJECT_ROOT)}")
        if migrate_file(file_path):
            migrated += 1
            print("    ✅ Migrated")
        else:
            print("    ⏭️  No changes needed")

    print(f"\n✅ Migration complete: {migrated}/{len(files)} files migrated")
    print("⚠️  Please review changes and test before committing")


if __name__ == "__main__":
    main()
