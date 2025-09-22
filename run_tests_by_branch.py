#!/usr/bin/env python3
"""
Branch-spezifische Test-Ausführung
Führt Tests basierend auf dem aktuellen Git-Branch aus
"""

import subprocess
import sys


def get_current_branch():
    """Aktuellen Git-Branch ermitteln"""
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Fehler beim Ermitteln des Git-Branches")
        return None


def run_tests(test_path):
    """Tests ausführen"""
    print(f"🧪 Führe Tests aus: {test_path}")
    try:
        subprocess.run(["python", "-m", "pytest", test_path], check=True)
        print("✅ Tests erfolgreich ausgeführt")
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests fehlgeschlagen")
        return False


def main():
    """Hauptfunktion"""
    print("🔍 Branch-spezifische Test-Ausführung")
    print("=" * 50)

    # Aktuellen Branch ermitteln
    branch = get_current_branch()
    if not branch:
        sys.exit(1)

    print(f"📍 Aktueller Branch: {branch}")

    # Test-Pfad basierend auf Branch bestimmen
    if branch.startswith("helper/"):
        test_path = "tests/test_helper_apps/"
        print("🎯 Helper-Branch erkannt → Nur Helper-App-Tests")
    else:
        test_path = "tests/"
        print("🎯 Main-Branch erkannt → Alle Tests")

    # Tests ausführen
    success = run_tests(test_path)

    if success:
        print("🎉 Alle Tests erfolgreich!")
        sys.exit(0)
    else:
        print("💥 Tests fehlgeschlagen!")
        sys.exit(1)


if __name__ == "__main__":
    main()
