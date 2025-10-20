#!/usr/bin/env python3
"""
Syntax-Validator für Helper-Apps
Wird automatisch vor Commits ausgeführt
"""

import ast
import sys
from pathlib import Path


def validate_helper_app_syntax(file_path: Path) -> bool:
    """
    Validiert die Syntax einer Helper-App

    Args:
        file_path: Pfad zur Helper-App

    Returns:
        True wenn Syntax gültig, False wenn Fehler gefunden
    """
    if not file_path.exists():
        print(f"❌ Datei nicht gefunden: {file_path}")
        return False

    try:
        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()

        # Parse Python-Syntax
        ast.parse(source_code, filename=str(file_path))
        print(f"✅ Syntax gültig: {file_path}")
        assert True

    except SyntaxError as e:
        print(f"❌ Syntax-Fehler in {file_path}:")
        print(f"   Zeile {e.lineno}: {e.text}")
        print(f"   Fehler: {e.msg}")
        return False

    except IndentationError as e:
        print(f"❌ Indentations-Fehler in {file_path}:")
        print(f"   Zeile {e.lineno}: {e.text}")
        print(f"   Fehler: {e.msg}")
        return False

    except Exception as e:
        print(f"❌ Unerwarteter Fehler in {file_path}: {e}")
        return False


def main():
    """Hauptfunktion für Command-Line-Usage"""
    if len(sys.argv) != 2:
        print("Usage: python validate_helper_app_syntax.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    success = validate_helper_app_syntax(file_path)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
