#!/usr/bin/env python3
"""
Notfall-Dashboard-Reparatur
Repariert kaputte Dashboard-Datei mit Backup
"""

import os
import shutil
import subprocess
import sys


def emergency_fix():
    """Notfall-Reparatur des Dashboards"""
    print("🚨 NOTFALL-REPARATUR: Dashboard ist kaputt!")

    dashboard_file = "src_orbis/mqtt/dashboard/aps_dashboard.py"
    backup_file = "src_orbis/mqtt/dashboard/aps_dashboard_backup.py"

    # 1. Backup erstellen falls nicht vorhanden
    if not os.path.exists(backup_file):
        print("📦 Erstelle Backup...")
        try:
            # Suche nach funktionierender Version in Git
            result = subprocess.run(
                ["git", "show", "787f463:src_orbis/mqtt/dashboard/aps_dashboard.py"],
                capture_output=True,
                text=True,
                check=True,
            )

            with open(backup_file, "w") as f:
                f.write(result.stdout)
            print("✅ Backup erstellt")
        except:
            print("❌ Backup-Erstellung fehlgeschlagen")
            return False

    # 2. Dashboard mit Backup ersetzen
    print("🔄 Ersetze Dashboard mit Backup...")
    try:
        shutil.copy2(backup_file, dashboard_file)
        print("✅ Dashboard ersetzt")
    except Exception as e:
        print(f"❌ Ersetzung fehlgeschlagen: {e}")
        return False

    # 3. Teste ob es funktioniert
    print("🧪 Teste repariertes Dashboard...")
    try:
        subprocess.run(
            [sys.executable, "-m", "py_compile", dashboard_file],
            check=True,
            capture_output=True,
        )
        print("✅ Dashboard funktioniert wieder!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Dashboard immer noch kaputt")
        return False


def main():
    """Hauptfunktion"""
    if emergency_fix():
        print("🎉 NOTFALL-REPARATUR ERFOLGREICH!")
        print("💡 Dashboard ist wieder funktionsfähig")
        sys.exit(0)
    else:
        print("💥 NOTFALL-REPARATUR FEHLGESCHLAGEN!")
        print("🚨 Manuelle Reparatur erforderlich")
        sys.exit(1)


if __name__ == "__main__":
    main()
