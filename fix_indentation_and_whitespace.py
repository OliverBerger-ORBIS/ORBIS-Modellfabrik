#!/usr/bin/env python3
"""
Fix common indentation/whitespace issues that cause IndentationError after cross-platform checkouts.

What it does per .py file:
- Normalize line endings to LF
- Remove UTF-8 BOMs
- Replace tabs with 4 spaces
- Replace non-breaking spaces (U+00A0) with normal spaces
- Remove zero-width chars (U+200B–U+200D, U+FEFF BOM if present inline)
- Trim trailing whitespace
- Ensure file ends with a single newline
- Try to preserve visual indentation but unify to spaces
- AST-validate result; on failure, writes a .bak and keeps both versions for manual inspection

Usage:
    python fix_indentation_and_whitespace.py [path]

If [path] is omitted, it runs on the current working directory recursively.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ZERO_WIDTH = "".join(chr(c) for c in [0x200B, 0x200C, 0x200D, 0xFEFF])
ZW_RE = re.compile(f"[{re.escape(ZERO_WIDTH)}]")


def normalize_text(s: str) -> str:
    # Normalize CRLF/CR to LF
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # Strip BOM at start
    if s.startswith("\ufeff"):
        s = s.lstrip("\ufeff")
    # Replace non-breaking space with normal space
    s = s.replace("\u00A0", " ")
    # Remove zero-width chars
    s = ZW_RE.sub("", s)
    # Replace tabs with 4 spaces
    s = s.expandtabs(4)
    # Trim trailing whitespace per line
    s = "\n".join(line.rstrip() for line in s.split("\n"))
    # Ensure single trailing newline
    if not s.endswith("\n"):
        s += "\n"
    return s


def process_file(p: Path) -> dict:
    original = p.read_text(encoding="utf-8", errors="replace")
    normalized = normalize_text(original)

    changed = normalized != original
    result = {
        "path": str(p),
        "changed": changed,
        "ast_ok_before": None,
        "ast_ok_after": None,
        "error_after": None,
    }

    # Try parse before/after for visibility
    try:
        ast.parse(original)
        result["ast_ok_before"] = True
    except Exception:
        result["ast_ok_before"] = False

    try:
        ast.parse(normalized)
        result["ast_ok_after"] = True
    except Exception as e:
        result["ast_ok_after"] = False
        result["error_after"] = f"{type(e).__name__}: {e}"

    if changed:
        # Backup before overwriting
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            bak.write_text(original, encoding="utf-8")
        # If parsing after failed, still write normalized as .normalized for inspection
        if not result["ast_ok_after"]:
            norm_path = p.with_suffix(p.suffix + ".normalized")
            norm_path.write_text(normalized, encoding="utf-8")
        else:
            # overwrite only if AST is OK
            p.write_text(normalized, encoding="utf-8")

    return result


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    if root.is_file() and root.suffix == ".py":
        files = [root]
    else:
        files = [p for p in root.rglob("*.py") if p.is_file()]

    results = []
    for p in files:
        try:
            results.append(process_file(p))
        except Exception as e:
            results.append({"path": str(p), "error": f"{type(e).__name__}: {e}"})
    # Print a compact report
    changed = sum(1 for r in results if r.get("changed"))
    failed_after = [r for r in results if r.get("ast_ok_after") is False]
    print(f"Processed {len(results)} .py files; changed {changed}.")
    if failed_after:
        print("\nFiles that still fail AST parse after normalization:")
        for r in failed_after:
            print(f" - {r['path']}: {r.get('error_after')} (kept .bak and .normalized)")
    else:
        print("All normalized files parse OK.")


if __name__ == "__main__":
    main()
