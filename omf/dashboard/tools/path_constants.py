"""
Zentrale Pfad-Konstanten für das OMF-Projekt

State-of-the-Art Ansatz: Robuste Pfad-Definition ohne fehleranfällige parent.parent... Ketten
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

# Wichtige Verzeichnisse
DATA_DIR = PROJECT_ROOT / "data"
OMF_DATA_DIR = DATA_DIR / "omf-data"
SESSIONS_DIR = OMF_DATA_DIR / "sessions"
LOGS_DIR = DATA_DIR / "logs"
CONFIG_DIR = PROJECT_ROOT / "omf" / "config"
REGISTRY_DIR = PROJECT_ROOT / "registry"
TEMPLATES_DIR = REGISTRY_DIR / "model" / "v1" / "templates"
MAPPING_FILE = REGISTRY_DIR / "model" / "v1" / "mapping.yml"


# Validierung
def validate_paths():
    """Validiert, dass alle wichtigen Pfade existieren"""
    required_dirs = [DATA_DIR, OMF_DATA_DIR, CONFIG_DIR, REGISTRY_DIR]
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
        "config_dir": str(CONFIG_DIR),
        "registry_dir": str(REGISTRY_DIR),
        "templates_dir": str(TEMPLATES_DIR),
        "mapping_file": str(MAPPING_FILE),
    }


if __name__ == "__main__":
    # Test der Pfad-Konstanten
    print("🔍 OMF Pfad-Konstanten:")
    for key, value in get_path_info().items():
        print(f"  {key}: {value}")

    try:
        validate_paths()
        print("✅ Alle Pfade validiert")
    except FileNotFoundError as e:
        print(f"❌ Pfad-Validierung fehlgeschlagen: {e}")
