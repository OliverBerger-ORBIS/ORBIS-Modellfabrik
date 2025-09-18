#!/usr/bin/env python3
"""
Code Formatierung und Qualitätsprüfung für ORBIS Modellfabrik
Automatische Formatierung und Syntax-Prüfung
"""

import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Führt einen Befehl aus und gibt Status zurück"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} erfolgreich")
            return True
        else:
            print(f"❌ {description} fehlgeschlagen:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Fehler bei {description}: {e}")
        return False

def check_syntax(file_path):
    """Prüft Python-Syntax einer Datei"""
    print(f"🔍 Prüfe Syntax: {file_path}")
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        compile(content, file_path, "exec")
        print(f"✅ Syntax OK: {file_path}")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax-Fehler in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler beim Prüfen von {file_path}: {e}")
        return False

def main():
    """Hauptfunktion für Code-Formatierung"""
    print("🚀 ORBIS Modellfabrik - Code Formatierung")
    print("=" * 50)

    # Python-Dateien finden
    python_files = list(Path("omf").rglob("*.py"))
    python_files.extend(Path("tests").rglob("*.py"))

    print(f"📁 Gefundene Python-Dateien: {len(python_files)}")

    # 1. Black Formatierung
    success = run_command("python -m black omf/ tests/", "Black Formatierung")

    # 2. isort Import-Sortierung
    if success:
        success = run_command("python -m isort omf/ tests/", "Import-Sortierung")

    # 3. Syntax-Prüfung
    if success:
        print("\n🔍 Syntax-Prüfung...")
        all_syntax_ok = True
        for file_path in python_files:
            if not check_syntax(file_path):
                all_syntax_ok = False

        if all_syntax_ok:
            print("✅ Alle Python-Dateien haben korrekte Syntax")
        else:
            print("❌ Syntax-Fehler gefunden!")
            return False

    # 4. Flake8 Linting
    if success:
        success = run_command(
            "python -m flake8 omf/ tests/ --max-line-length=88 --ignore=E203,W503",
            "Code-Linting",
        )

    if success:
        print("\n🎉 Code-Formatierung erfolgreich abgeschlossen!")
        return True
    else:
        print("\n❌ Code-Formatierung fehlgeschlagen!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
