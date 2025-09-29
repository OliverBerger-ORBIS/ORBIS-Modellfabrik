"""
Zentrale Pfad-Konstanten für Session Manager
Isolierte Version ohne OMF-Dependencies
"""

import os
from pathlib import Path


# Projekt-Root robust ermitteln
def get_project_root() -> Path:
    """
    Ermittelt das Projekt-Root-Verzeichnis robust.
    Funktioniert unabhängig von der Tiefe der aufrufenden Datei.
    """
    # Starte von der aktuellen Datei
    current_file = Path(__file__).resolve()

    # Gehe nach oben bis zum Projekt-Root (wo pyproject.toml liegt)
    for parent in current_file.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    # Fallback: Aktuelles Arbeitsverzeichnis
    return Path.cwd()


# Projekt-Root-Konstante
PROJECT_ROOT = get_project_root()

# Session Manager spezifische Verzeichnisse
DATA_DIR = PROJECT_ROOT / "data"
OMF_DATA_DIR = DATA_DIR / "omf-data"
SESSIONS_DIR = OMF_DATA_DIR / "sessions"
LOGS_DIR = DATA_DIR / "logs"

# Session Manager spezifische Pfade
SESSION_MANAGER_LOGS_DIR = LOGS_DIR / "session_manager"


# Validierung
def validate_paths():
    """Validiert, dass alle wichtigen Pfade existieren"""
    required_dirs = [DATA_DIR, OMF_DATA_DIR, SESSIONS_DIR]
    missing_dirs = [d for d in required_dirs if not d.exists()]

    if missing_dirs:
        raise FileNotFoundError(f"Fehlende Verzeichnisse: {missing_dirs}")

    return True


# Debug-Information
def get_path_info():
    """Gibt Debug-Informationen über die Pfad-Konfiguration zurück"""
    return {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "sessions_dir": str(SESSIONS_DIR),
        "logs_dir": str(LOGS_DIR),
        "session_manager_logs_dir": str(SESSION_MANAGER_LOGS_DIR),
    }


if __name__ == "__main__":
    # Test der Pfad-Konstanten
    print("🔍 Session Manager Pfad-Konstanten:")
    for key, value in get_path_info().items():
        print(f"  {key}: {value}")

    try:
        validate_paths()
        print("✅ Alle Pfade validiert")
    except FileNotFoundError as e:
        print(f"❌ Pfad-Validierung fehlgeschlagen: {e}")
