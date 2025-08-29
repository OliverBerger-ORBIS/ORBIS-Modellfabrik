#!/usr/bin/env python3
"""
Test für das OMF Dashboard vor Commit
"""

import os
import sys


def test_omf_dashboard():
    """Testet das OMF Dashboard"""

    print("🧪 Teste OMF Dashboard...")

    # Test 1: Import test
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), "src_orbis"))
        from omf.dashboard.omf_dashboard import main

        print("✅ Import erfolgreich")
    except ImportError as e:
        print(f"❌ Import fehlgeschlagen: {e}")
        return False

    # Test 2: Function exists
    try:
        if callable(main):
            print("✅ main() Funktion existiert")
        else:
            print("❌ main() ist keine Funktion")
            return False
    except Exception as e:
        print(f"❌ Funktion-Test fehlgeschlagen: {e}")
        return False

    # Test 3: File structure
    dashboard_file = "src_orbis/omf/dashboard/omf_dashboard.py"
    if os.path.exists(dashboard_file):
        print(f"✅ Dashboard-Datei existiert: {dashboard_file}")
    else:
        print(f"❌ Dashboard-Datei fehlt: {dashboard_file}")
        return False

    print("🎉 Alle Tests erfolgreich!")
    return True


if __name__ == "__main__":
    success = test_omf_dashboard()
    sys.exit(0 if success else 1)
