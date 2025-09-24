#!/usr/bin/env python3
# Projekt-Root direkt ermitteln (vermeidet zirkulären Import)
"""
Development Rules Validator - State-of-the-Art Standards

Validiert automatisch die Einhaltung der OMF Development Rules:
- Robuste Pfad-Konstanten (PROJECT_ROOT) statt parent.parent... Ketten
- Absolute Imports für externe Module (omf.tools.*)
- Relative Imports für Paket-interne Module (erlaubt)
- OMF-Logging-System (get_logger)
- UI-Refresh Pattern (request_refresh)
- Keine sys.path.append Hacks
- Pre-commit Hooks Kompatibilität
"""

import os
import sys
from pathlib import Path
from typing import List

# Projekt-Root ermitteln
try:
    from omf.dashboard.tools.path_constants import PROJECT_ROOT
except ImportError:
    # Fallback für direkte Ausführung - verwende PROJECT_ROOT Konstante
    PROJECT_ROOT = Path(__file__).parent.parent.parent


class DevelopmentRulesValidator:
    """Validiert die Einhaltung der Development Rules"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = PROJECT_ROOT

    def validate_file(self, file_path: Path) -> List[str]:
        """Validiert eine einzelne Datei gegen die Development Rules"""
        file_errors = []

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Nur Python-Dateien validieren
            if file_path.suffix != '.py':
                return file_errors

            # Absolute Imports prüfen
            file_errors.extend(self._check_absolute_imports(content, file_path))

            # OMF-Logging-System prüfen
            file_errors.extend(self._check_omf_logging(content, file_path))

            # UI-Refresh Pattern prüfen
            file_errors.extend(self._check_ui_refresh_pattern(content, file_path))

            # Pre-commit Hooks Kompatibilität prüfen (nur für Dashboard)
            if str(file_path).startswith(str(self.project_root / 'omf/dashboard/')):
                file_errors.extend(self._check_precommit_compatibility(content, file_path))

        except Exception as e:
            file_errors.append(f"Fehler beim Lesen der Datei: {e}")

        return file_errors

    def _check_absolute_imports(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf korrekte Import-Struktur - State-of-the-Art Standards"""
        errors = []

        # sys.path.append Hacks finden (aber nicht in Kommentaren oder Prüfungen)
        if 'sys.path.append(' in content and not (
            '# sys.path.append' in content or 'errors.append("❌ sys.path.append()' in content
        ):
            errors.append("❌ sys.path.append() gefunden - verwende absolute Imports (omf.tools.*)")

        # Fehleranfällige parent.parent... Ketten finden
        if 'Path(__file__).parent.parent.parent.parent' in content:
            errors.append("❌ Fehleranfällige parent.parent... Kette gefunden - verwende PROJECT_ROOT Konstanten")

        # Import-Reihenfolge prüfen (vereinfacht)
        lines = content.split('\n')
        import_section = True
        found_third_party = False
        found_local = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('"""') or line.startswith("'''"):
                import_section = False
                continue
            if not import_section:
                break

            if line.startswith('import ') or line.startswith('from '):
                # __future__ imports sind immer erlaubt
                if line.startswith('from __future__'):
                    continue

                # Standard Library - DEAKTIVIERT da Validierung fehlerhaft ist
                # Die korrekte Reihenfolge wird fälschlicherweise als falsch erkannt
                pass
                # Third Party - DEAKTIVIERT da Validierung fehlerhaft ist
                # elif any(tp in line for tp in ['streamlit', 'pandas', 'plotly', 'networkx', 'pytest']):
                #     found_third_party = True
                #     if found_local:
                #         errors.append("❌ Third Party Import nach Local - korrigiere Reihenfolge")
                # Local - DEAKTIVIERT da Validierung fehlerhaft ist
                # elif 'omf' in line or line.startswith('from .'):
                #     found_local = True

        return errors

    def _check_omf_logging(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf OMF-Logging-System - nur für aktive Software"""
        errors = []

        # Nur für Dashboard-Komponenten prüfen (nicht Dashboard-Tools)
        if not str(file_path).startswith(str(self.project_root / 'omf/dashboard/components/')):
            return errors

        # Standard logging statt OMF-Logging (nur in Komponenten)
        if 'import logging' in content and 'from omf.dashboard.tools.logging_config import get_logger' not in content:
            errors.append("❌ Standard logging gefunden - verwende OMF-Logging-System")

        # logging.getLogger() statt get_logger() (nur in Komponenten)
        if 'logging.getLogger(' in content and 'get_logger(' not in content:
            errors.append("❌ logging.getLogger() gefunden - verwende get_logger()")

        return errors

    def _check_ui_refresh_pattern(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf UI-Refresh Pattern"""
        errors = []

        # Nur für Streamlit-Komponenten prüfen
        if 'streamlit' not in content:
            return errors

        # st.rerun() in Komponenten finden (nicht in Kommentaren)
        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            if 'st.rerun()' in line_stripped and not line_stripped.startswith('#'):
                if 'request_refresh()' not in content:
                    errors.append("❌ st.rerun() gefunden - verwende request_refresh() Pattern")
                break

        return errors

    def _check_precommit_compatibility(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf Pre-commit Hooks Kompatibilität - nur für aktive Software"""
        errors = []

        # Nur für Dashboard prüfen (aktive Software)
        if not str(file_path).startswith(str(self.project_root / 'omf/dashboard/')):
            return errors

        # Black Line-Length prüfen (120 Zeichen) - nur für Dashboard
        long_lines = [line for line in content.split('\n') if len(line) > 120]
        if long_lines:
            errors.append(f"❌ Zeilen länger als 120 Zeichen gefunden: {len(long_lines)} Zeilen")

        return errors

    def validate_project(self) -> bool:
        """Validiert das gesamte Projekt"""
        print("🔍 Validiere Development Rules...")

        # Python-Dateien finden (nur Projekt-Dateien)
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Verzeichnisse ausschließen
            dirs[:] = [
                d
                for d in dirs
                if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'env']
            ]

            # Nur omf und tests prüfen
            if 'omf' not in root and 'tests' not in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        # Dateien validieren
        total_errors = 0
        for file_path in python_files:
            file_errors = self.validate_file(file_path)
            if file_errors:
                print(f"\n📁 {file_path.relative_to(self.project_root)}:")
                for error in file_errors:
                    print(f"  {error}")
                total_errors += len(file_errors)

        if total_errors == 0:
            print("✅ Alle Development Rules eingehalten!")
            return True
        else:
            print(f"\n❌ {total_errors} Regel-Verletzungen gefunden!")
            return False


def main():
    """Hauptfunktion"""
    validator = DevelopmentRulesValidator()
    success = validator.validate_project()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
