#!/usr/bin/env python3
"""
End-to-End Session Starter für W1B1R1

Startet eine Session für einen vollständigen End-to-End Test mit:
- W1 (WEISS Workpiece 1)
- B1 (BLAU Workpiece 1)
- R1 (ROT Workpiece 1)
"""

import os
import subprocess
from datetime import datetime


def start_end2end_session():
    """Startet eine End-to-End Session für W1B1R1"""

    # Session-Name definieren
    session_name = "end2end_W1B1R1"

    print("🚀 Starte End-to-End Session für W1B1R1")
    print("=" * 50)
    print(f"📋 Session-Name: {session_name}")
    print(f"⏰ Start-Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🏷️ Workpiecee: W1 (WEISS), B1 (BLAU), R1 (ROT)")
    print("=" * 50)

    # APS Session Logger starten
    logger_command = [
        "python",
        "omf/mqtt/loggers/aps_session_logger.py",
        "--session-label",
        session_name,
        "--auto-start",
    ]

    print("📡 Starte APS Session Logger...")
    print(f"🔧 Kommando: {' '.join(logger_command)}")
    print()
    print("💡 Tipp: Drücke 'q' + Enter zum Beenden der Session")
    print("=" * 50)

    try:
        # Session Logger starten
        subprocess.run(logger_command, check=True)

    except KeyboardInterrupt:
        print("\n⚠️ Session durch Benutzer beendet")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten der Session: {e}")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

    return True


def main():
    """Hauptfunktion"""
    print("🎯 End-to-End Session Starter für W1B1R1")
    print("=" * 50)

    # Prüfen ob APS Session Logger existiert
    logger_path = "omf/mqtt/loggers/aps_session_logger.py"
    if not os.path.exists(logger_path):
        print(f"❌ APS Session Logger nicht gefunden: {logger_path}")
        print("💡 Stelle sicher, dass das Projekt korrekt installiert ist")
        return False

    # Session starten
    success = start_end2end_session()

    if success:
        print("✅ Session erfolgreich beendet")
    else:
        print("❌ Session fehlgeschlagen")

    return success


if __name__ == "__main__":
    main()
