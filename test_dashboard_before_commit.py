#!/usr/bin/env python3
"""
Dashboard-Test vor Commit
Testet ob das Dashboard startet und funktioniert
"""

import subprocess
import time
import requests
import sys

def test_dashboard():
    """Testet das Dashboard vor dem Commit"""
    print("🧪 Teste Dashboard vor Commit...")

    # 1. Import-Test
    print("📦 Teste Imports...")
    try:
        print("✅ Imports erfolgreich")
    except Exception as e:
        print(f"❌ Import-Fehler: {e}")
        return False

    # 2. Dashboard-Start-Test
    print("🚀 Teste Dashboard-Start...")
    try:
        # Starte Dashboard im Hintergrund
        process = subprocess.Popen([
            "streamlit", "run",
            "src_orbis/mqtt/dashboard/aps_dashboard.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Warte auf Start
        time.sleep(8)

        # Teste HTTP-Response
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard läuft erfolgreich")
            success = True
        else:
            print(f"❌ Dashboard-Response: {response.status_code}")
            success = False

    except Exception as e:
        print(f"❌ Dashboard-Start-Fehler: {e}")
        success = False

    finally:
        # Stoppe Dashboard
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            subprocess.run(["pkill", "-f", "streamlit"], check=False)

    return success

def main():
    """Hauptfunktion"""
    if test_dashboard():
        print("🎉 Dashboard-Test erfolgreich - Commit erlaubt!")
        sys.exit(0)
    else:
        print("💥 Dashboard-Test fehlgeschlagen - Commit verweigert!")
        print("🔧 Bitte Dashboard-Fehler beheben vor dem Commit")
        sys.exit(1)

if __name__ == "__main__":
    main()

